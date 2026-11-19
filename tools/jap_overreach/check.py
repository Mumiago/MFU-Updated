r"""Static test suite for the Japan overreach compliance mechanic (no game launch needed).

From the mod root:
    python -I tools/jap_overreach/check.py
Prints PASS/FAIL per test and exits non-zero when any test fails.
Expected values here come from docs/superpowers/specs/2026-11-14-japan-overreach-compliance-design.md and the plan's
Global Constraints, not from the mechanic files, so the files are tested rather than trusted.
"""
import glob
import os
import re
import sys
import traceback

MOD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

TRIGGERS = "common/scripted_triggers/MFU_JAP_overreach_scripted_triggers.txt"
EFFECTS = "common/scripted_effects/MFU_JAP_overreach_scripted_effects.txt"
MODIFIERS = "common/dynamic_modifiers/MFU_JAP_overreach_dynamic_modifiers.txt"
ON_ACTIONS = "common/on_actions/MFU_JAP_overreach_on_actions.txt"
LOC = "localisation/english/MFU_JAP_overreach_l_english.yml"
SCRIPT_FILES = [TRIGGERS, EFFECTS, MODIFIERS, ON_ACTIONS]

EFFECT = "JAP_update_overreach_compliance"
MODIFIER = "JAP_overstretched_occupation"
STATE_VAR = "JAP_overreach_compliance_gain"
COUNTER = "JAP_resistance_target_modifier"

INLAND = {283, 287, 601, 603, 604, 605, 616, 617, 618, 619, 747, 748, 750, 751, 752, 753, 754, 755, 756, 759, 760}
MIDDLE = {325, 599, 600, 602, 620, 622, 744, 820, 821}

TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


def read(rel):
    with open(os.path.join(MOD, rel), encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def read_bytes(rel):
    with open(os.path.join(MOD, rel), "rb") as f:
        return f.read()


def strip(text):
    return re.sub(r"#[^\n]*", "", text)


def match_brace(t, i):
    depth = 0
    for j in range(i, len(t)):
        if t[j] == "{":
            depth += 1
        elif t[j] == "}":
            depth -= 1
            if depth == 0:
                return j
    raise ValueError("unbalanced braces")


def children(body):
    """Top-level `key = { ... }` pairs of a block body, as (key, inner)."""
    out, i = [], 0
    pat = re.compile(r"([A-Za-z0-9_.:@\-]+)\s*=\s*\{")
    while True:
        m = pat.search(body, i)
        if not m:
            return out
        j = match_brace(body, m.end() - 1)
        out.append((m.group(1), body[m.end():j]))
        i = j + 1


def block(text, name):
    """Inner text of the first `name = { ... }` anywhere in text, or None."""
    m = re.search(r"(?<![\w.])" + re.escape(name) + r"\s*=\s*\{", text)
    if not m:
        return None
    return text[m.end():match_brace(text, m.end() - 1)]


def all_blocks(text, name):
    out, pos = [], 0
    pat = re.compile(r"(?<![\w.])" + re.escape(name) + r"\s*=\s*\{")
    while True:
        m = pat.search(text, pos)
        if not m:
            return out
        j = match_brace(text, m.end() - 1)
        out.append(text[m.end():j])
        pos = j + 1


def need(cond, msg):
    if not cond:
        raise AssertionError(msg)


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"\s*([={}])\s*", r"\1", s)).strip()


def effect_body():
    body = block(strip(read(EFFECTS)), EFFECT)
    need(body is not None, f"{EFFECT} not defined in {EFFECTS}")
    return body


def ids_in(trigger):
    body = block(strip(read(TRIGGERS)), trigger)
    need(body is not None, f"{trigger} not defined in {TRIGGERS}")
    need(re.fullmatch(r"\s*OR\s*=\s*\{(?:\s*state\s*=\s*\d+)*\s*\}\s*", body),
         f"{trigger}: body must be exactly one top-level OR = {{ }} holding only `state = N` entries")
    listed = [int(n) for n in re.findall(r"\bstate\s*=\s*(\d+)\b", body)]
    need(len(listed) == len(set(listed)), f"{trigger}: duplicate state ids")
    return set(listed)


def history_tier_ids(tiers):
    """State ids whose history adds CHI_tougher_resistance<tier>; no digit is tier 1, history uses only 0-4."""
    found = set()
    for path in glob.glob(os.path.join(MOD, "history", "states", "*.txt")):
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            text = strip(f.read())
        sid = re.search(r"\bid\s*=\s*(\d+)", text)
        if not sid:
            continue
        for d in re.findall(r"modifier\s*=\s*CHI_tougher_resistance(\d*)\b", text):
            if (int(d) if d else 1) in tiers:
                found.add(int(sid.group(1)))
    return found


def derived(var):
    """(source variable, multiplier, clamp) of `var` from the effect's top-level ops, requiring set -> multiply -> clamp in that order."""
    ops = []
    for kind, args in children(effect_body()):
        if kind == "clamp_variable":
            c = re.fullmatch(r"\s*var\s*=\s*(\w+)\s+max\s*=\s*(-?[0-9.]+)\s*", args)
            if c and c.group(1) == var:
                ops.append((kind, c.group(2)))
        elif kind in ("set_variable", "multiply_variable"):
            c = re.fullmatch(r"\s*(\w+)\s*=\s*(\S+)\s*", args)
            if c and c.group(1) == var:
                ops.append((kind, c.group(2)))
    need([k for k, _ in ops] == ["set_variable", "multiply_variable", "clamp_variable"],
         f"{var}: expected set_variable, multiply_variable, clamp_variable in that order, found {[k for k, _ in ops]}")
    need(float(ops[2][1]) == 0, f"{var}: clamp max must be 0, found {ops[2][1]}")
    return (ops[0][1], float(ops[1][1]), "max0")


def modifier_def(name):
    """(body without enable, plain `key = value` lines, normalized enable) of a dynamic modifier."""
    body = block(strip(read(MODIFIERS)), name)
    need(body is not None, f"{name} not defined in {MODIFIERS}")
    m = re.search(r"(?<![\w.])enable\s*=\s*\{", body)
    need(m is not None, f"{name}: no enable block")
    end = match_brace(body, m.end() - 1)
    rest = body[:m.start()] + body[end + 1:]
    pairs = dict(re.findall(r"^\s*([A-Za-z_]+)\s*=\s*([^\s{}]+)\s*$", rest, re.M))
    return rest, pairs, norm(body[m.end():end])


def sim(k_counter, tier, days=365, c0=60.0):
    """Daily compliance engine: C += 0.08*M - 0.001*C + G, clamped 0..100, G = Japan bonus + counter penalties."""
    mult, uses_extra = {"inland": (0.65, "inland"), "middle": (0.8, "middle"), "coast": (0.9, None), "seasia": (1.0, None)}[tier]
    cw = derived("JAP_compliance_gain_modifier")[1]
    extra = derived(f"JAP_{uses_extra}_overreach_compliance")[1] if uses_extra else 0.0
    g = 0.03 + min(0.0, cw * k_counter) + min(0.0, extra * k_counter)
    c = c0
    for _ in range(days):
        c = min(100.0, max(0.0, c + 0.08 * mult - 0.001 * c + g))
    return c


@test
def test_state_lists():
    inland, middle = ids_in("JAP_is_inland_china_state"), ids_in("JAP_is_middle_china_state")
    need(inland == INLAND, f"inland list differs: missing {sorted(INLAND - inland)}, extra {sorted(inland - INLAND)}")
    need(middle == MIDDLE, f"middle list differs: missing {sorted(MIDDLE - middle)}, extra {sorted(middle - MIDDLE)}")
    need(not inland & middle, f"lists overlap: {sorted(inland & middle)}")


@test
def test_lists_match_history_tiers():
    inland, middle = history_tier_ids({3, 4}), history_tier_ids({2})
    need(inland == INLAND, f"history tier 3/4 states differ: missing {sorted(INLAND - inland)}, extra {sorted(inland - INLAND)}")
    need(middle == MIDDLE, f"history tier 2 states differ: missing {sorted(MIDDLE - middle)}, extra {sorted(middle - MIDDLE)}")


@test
def test_effect_math():
    need(derived("JAP_compliance_gain_modifier") == (COUNTER, -0.20, "max0"), "country-wide value is not min(0, -0.20*K)")
    need(derived("JAP_inland_overreach_compliance") == (COUNTER, -0.25, "max0"), "inland value is not min(0, -0.25*K)")
    need(derived("JAP_middle_overreach_compliance") == (COUNTER, -0.125, "max0"), "middle value is not min(0, -0.125*K)")
    body = effect_body()
    last_clamp = max(m.start() for m in re.finditer(r"\bclamp_variable\b", body))
    first_state = re.search(r"\bevery_state\b", body)
    need(first_state is not None and last_clamp < first_state.start(), "the three set/multiply/clamp triples must come before the every_state blocks")


@test
def test_effect_copies_state_values():
    states = [(c, b) for c, b in children(effect_body()) if c == "every_state"]
    need(len(states) == 2, f"expected 2 every_state blocks, found {len(states)}")
    seen = {}
    for _, b in states:
        limit = norm(block(b, "limit") or "")
        for trig, var in (("JAP_is_inland_china_state", "JAP_inland_overreach_compliance"),
                          ("JAP_is_middle_china_state", "JAP_middle_overreach_compliance")):
            if limit == f"{trig}=yes":
                seen[trig] = b
                top = [norm(inner) for key, inner in children(b) if key == "set_variable"]
                need(f"{STATE_VAR}=JAP.{var}" in top,
                     f"{trig}: {STATE_VAR} = JAP.{var} must be set unconditionally, directly in the every_state body (not inside an if)")
                adds = re.findall(r"add_dynamic_modifier\s*=\s*\{([^{}]*)\}", b)
                need(len(adds) == 1, f"{trig}: expected one add_dynamic_modifier, found {len(adds)}")
                need(norm(adds[0]) == f"modifier={MODIFIER}", f"{trig}: add_dynamic_modifier must be {{ modifier = {MODIFIER} }} with no scope key, found {{ {norm(adds[0])} }}")
    need(set(seen) == {"JAP_is_inland_china_state", "JAP_is_middle_china_state"}, f"every_state limits found: {sorted(seen)}")


@test
def test_man_mirror():
    tops = children(effect_body())
    man = [i for i, (key, _) in enumerate(tops) if key == "MAN"]
    need(len(man) == 1, f"expected one top-level MAN = {{ }} block in {EFFECT}, found {len(man)}")
    need(norm(tops[man[0]][1]) == "set_variable={JAP_compliance_gain_modifier=JAP.JAP_compliance_gain_modifier}",
         f"MAN block must be exactly set_variable = {{ JAP_compliance_gain_modifier = JAP.JAP_compliance_gain_modifier }}, found {norm(tops[man[0]][1])}")
    clamp = [i for i, (key, inner) in enumerate(tops)
             if key == "clamp_variable" and re.search(r"\bvar\s*=\s*JAP_compliance_gain_modifier\b", inner)]
    need(len(clamp) == 1 and man[0] > clamp[0], "the MAN copy must come after Japan's country-wide value is clamped")
    reader = block(strip(read("common/dynamic_modifiers/jap_danymic_modifier.txt")), "JAP_china_war_bonus") or ""
    need(re.search(r"\bcompliance_gain\s*=\s*JAP_compliance_gain_modifier\b", reader), "JAP_china_war_bonus must read compliance_gain = JAP_compliance_gain_modifier")
    holder = [norm(b) for b in all_blocks(strip(read("history/countries/MAN - Manchukou.txt")), "add_dynamic_modifier")]
    need("modifier=JAP_china_war_bonus" in holder, "MAN history must add JAP_china_war_bonus")


@test
def test_attach_is_guarded():
    body = effect_body()
    adds = [m.start() for m in re.finditer(r"add_dynamic_modifier\s*=\s*\{\s*modifier\s*=\s*" + MODIFIER + r"\b", body)]
    need(adds, f"no add_dynamic_modifier of {MODIFIER}")
    guard = f"NOT={{has_dynamic_modifier={{modifier={MODIFIER}}}}}"
    for pos in adds:
        ok = False
        for m in re.finditer(r"(?<![\w.])if\s*=\s*\{", body):
            end = match_brace(body, m.end() - 1)
            lim = re.match(r"\s*limit\s*=\s*\{", body[m.end():end])
            if not (lim and m.end() <= pos <= end):
                continue
            lim_end = m.end() + match_brace(body[m.end():end], lim.end() - 1)
            if pos > lim_end and norm(body[m.end() + lim.end():lim_end]).replace(" ", "") == guard:
                ok = True
        need(ok, f"add_dynamic_modifier at offset {pos} is not directly under `if = {{ limit = {{ NOT = {{ has_dynamic_modifier = {{ modifier = {MODIFIER} }} }} }} }}`")


@test
def test_modifier_definition():
    body, pairs, enable = modifier_def(MODIFIER)
    lines = {k: v for k, v in pairs.items() if k != "icon"}
    need(lines == {"compliance_gain": STATE_VAR}, f"modifier lines must be exactly compliance_gain = {STATE_VAR}, found {lines}")
    need(pairs.get("icon") == "GFX_modifiers_generic_resistance", f"icon is {pairs.get('icon')}")
    need(enable == "ROOT={controller={OR={tag=JAP is_in_faction_with=JAP is_subject_of=JAP}}}", f"enable is {enable}")
    need("remove_trigger" not in body, "no remove_trigger allowed")


def hook_effect(name):
    hook = block(block(strip(read(ON_ACTIONS)), "on_actions") or "", name)
    need(hook is not None, f"on_actions.{name} missing")
    eff = block(hook, "effect")
    need(eff is not None, f"{name}.effect missing")
    return norm(eff)


@test
def test_on_startup():
    need(hook_effect("on_startup") == f"JAP={{{EFFECT}=yes}}", f"on_startup.effect must be exactly JAP = {{ {EFFECT} = yes }}")


@test
def test_on_monthly():
    need(hook_effect("on_monthly_JAP") == f"JAP={{{EFFECT}=yes}}", f"on_monthly_JAP.effect must be exactly JAP = {{ {EFFECT} = yes }}")


@test
def test_loc():
    raw = read_bytes(LOC)
    need(raw.startswith(b"\xef\xbb\xbf"), "loc file must start with a UTF-8 BOM")
    lines = raw[3:].decode("utf-8").splitlines()
    need(lines and lines[0].strip() == "l_english:", f"first line must be l_english:, found {lines[:1]}")
    entries = {m.group(1): m.group(2) for m in (re.match(r'\s*([A-Za-z0-9_.]+):\d*\s*"(.*)"\s*$', ln) for ln in lines[1:]) if m}
    need(MODIFIER in entries, f"{MODIFIER} key missing")
    need(MODIFIER + "_desc" in entries, f"{MODIFIER}_desc key missing")
    need(entries[MODIFIER] == "Overstretched Occupation", f"name is {entries[MODIFIER]!r}")
    need(not re.search(r"\d", entries[MODIFIER + "_desc"]), "description must be flavour only, no digits")


@test
def test_braces_and_encoding_new_files():
    for rel in SCRIPT_FILES:
        raw = read_bytes(rel)
        need(not raw.startswith(b"\xef\xbb\xbf"), f"{rel}: script files must have no BOM")
        raw.decode("utf-8")
        need(raw.count(b"\r\n") == raw.count(b"\n") == raw.count(b"\r") and raw.count(b"\n") > 0, f"{rel}: must be CRLF only")
        t = strip(raw.decode("utf-8"))
        need(t.count("{") == t.count("}"), f"{rel}: unbalanced braces")


@test
def test_simulated_outcome():
    inland = sim(0.38, "inland")
    need(10 <= inland <= 20 and abs(inland - 14.4) < 0.5, f"K=0.38 inland ends at {inland:.1f}, expected ~14.4")
    for tier, want in (("middle", 32.6), ("coast", 49.6), ("seasia", 52.0)):
        got = sim(0.38, tier)
        need(abs(got - want) < 0.5, f"K=0.38 {tier} ends at {got:.1f}, expected ~{want}")
    need(sim(0.61, "inland") == 0, f"K=0.61 inland ends at {sim(0.61, 'inland'):.1f}, expected 0")
    need(abs(sim(0.61, "middle") - 9.8) < 0.5, f"K=0.61 middle ends at {sim(0.61, 'middle'):.1f}, expected ~9.8")
    need(sim(0.0, "inland") > 60, f"K=0 inland ends at {sim(0.0, 'inland'):.1f}, expected above 60")


def common_texts():
    for path in sorted(glob.glob(os.path.join(MOD, "common", "**", "*.txt"), recursive=True)):
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            yield strip(f.read())


def count(pattern, add_only=False):
    """Occurrences of pattern across common/; add_only anchors it to `add_to_variable = {`."""
    rx = re.compile((r"add_to_variable\s*=\s*\{\s*" if add_only else "") + pattern + r"\b")
    return sum(len(rx.findall(t)) for t in common_texts())


def site_calls(rel):
    """For each JAP_resistance_target_modifier add_to_variable in rel: (header of enclosing block, call follows it)."""
    t = strip(read(rel))
    out = []
    for m in re.finditer(r"add_to_variable\s*=\s*\{\s*var\s*=\s*" + COUNTER + r"\b", t):
        depth, i = 0, m.start() - 1
        while i >= 0:
            if t[i] == "}":
                depth += 1
            elif t[i] == "{":
                if depth == 0:
                    break
                depth -= 1
            i -= 1
        need(i >= 0, f"{rel}: counter change at offset {m.start()} is not inside a block")
        header = re.search(r"([A-Za-z0-9_.:@\-]+)\s*=\s*$", t[:i]).group(1)
        after = match_brace(t, m.start() + m.group(0).index("{")) + 1
        out.append((header, re.search(r"(?<![\w.])" + EFFECT + r"\s*=\s*yes\b", t[after:match_brace(t, i)]) is not None))
    return out


def variable_writes():
    """(file, op, variable) for every variable op under common/, events/ and history/, in long (var = NAME) and short (NAME = ...) form."""
    out = []
    op = re.compile(r"(?<![\w.])((?:set|add_to|subtract_from|multiply|divide|clamp|round|modulo)_variable)\s*=\s*\{")
    for top in ("common", "events", "history"):
        for path in sorted(glob.glob(os.path.join(MOD, top, "**", "*.txt"), recursive=True)):
            with open(path, encoding="utf-8-sig", errors="replace") as f:
                t = strip(f.read())
            rel = os.path.relpath(path, MOD).replace(os.sep, "/")
            for m in op.finditer(t):
                body = t[m.end():match_brace(t, m.end() - 1)]
                name = re.search(r"\bvar\s*=\s*([^\s{}]+)", body) or re.match(r"\s*([^\s={}]+)\s*=", body)
                if name:
                    out.append((rel, m.group(1), re.split(r"[.:]", name.group(1))[-1]))
    return out


@test
def test_variable_ownership():
    writes = variable_writes()

    def by(var):
        return [(rel, op) for rel, op, v in writes if v == var]

    triple = [(EFFECTS, "set_variable"), (EFFECTS, "multiply_variable"), (EFFECTS, "clamp_variable")]
    need(by("JAP_compliance_gain_modifier") == triple + [(EFFECTS, "set_variable")],
         f"JAP_compliance_gain_modifier: only the set/multiply/clamp and the MAN copy in {EFFECTS} may write it, found {by('JAP_compliance_gain_modifier')}")
    for var in ("JAP_inland_overreach_compliance", "JAP_middle_overreach_compliance"):
        need(by(var) == triple, f"{var}: only the set/multiply/clamp in {EFFECTS} may write it, found {by(var)}")
    need(by(STATE_VAR) == [(EFFECTS, "set_variable")] * 2, f"{STATE_VAR}: only the 2 state copies in {EFFECTS} may write it, found {by(STATE_VAR)}")
    want = ([("common/on_actions/00_on_actions.txt", "add_to_variable")] * 8
            + [("common/on_actions/08_hopping_on_actions.txt", "add_to_variable")] * 2
            + [("history/countries/JAP - Japan.txt", "set_variable")])
    need(sorted(by(COUNTER)) == sorted(want), f"{COUNTER}: writers must be the 10 known add_to_variable sites plus the history init, found {sorted(by(COUNTER))}")


@test
def test_recompute_called_at_every_site():
    for rel, want in (("common/on_actions/00_on_actions.txt", 8), ("common/on_actions/08_hopping_on_actions.txt", 2)):
        sites = site_calls(rel)
        need(len(sites) == want, f"{rel}: expected {want} counter changes, found {len(sites)}")
        bad = [i + 1 for i, (header, called) in enumerate(sites) if header != "JAP" or not called]
        need(not bad, f"{rel}: counter change(s) #{bad} are not in a `JAP = {{ }}` block with `{EFFECT} = yes` after them")


@test
def test_counter_lines_untouched():
    man = count(r"var\s*=\s*MAN_resistance_target_modifier", add_only=True)
    need(man == 20, f"MAN_resistance_target_modifier changes: expected 20, found {man}")


@test
def test_edited_files_intact():
    for rel in ("common/on_actions/00_on_actions.txt", "common/on_actions/08_hopping_on_actions.txt"):
        raw = read_bytes(rel)
        need(not raw.startswith(b"\xef\xbb\xbf"), f"{rel}: must have no BOM")
        raw.decode("utf-8")
        need(raw.count(b"\r\n") == raw.count(b"\n") == raw.count(b"\r") and raw.count(b"\n") > 0, f"{rel}: every line must be CRLF")
        t = strip(raw.decode("utf-8"))
        need(t.count("{") == t.count("}"), f"{rel}: unbalanced braces")


def main():
    failed = 0
    for fn in TESTS:
        try:
            fn()
            print("PASS", fn.__name__)
        except Exception as e:  # noqa: BLE001
            failed += 1
            msg = str(e) or e.__class__.__name__
            if not isinstance(e, (AssertionError, FileNotFoundError)):
                msg += "\n" + traceback.format_exc(limit=3)
            print("FAIL", fn.__name__, "-", msg)
    print(f"{len(TESTS) - failed}/{len(TESTS)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
