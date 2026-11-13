r"""Static test suite for the Afrika Korps mechanic (no game launch needed).

From the mod root:
    python -I tools/afrika_korps/check.py
Prints PASS/FAIL per test and exits non-zero when any test fails.
Expected values here come from docs/superpowers/specs/2026-11-12-afrika-korps-mechanic-design.md and the plan's
Global Constraints, not from generate.py, so the generator is tested rather than trusted.
"""
import os
import re
import subprocess
import sys
import traceback

MOD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

IDEAS = "common/ideas/MFU_afrika_korps_ideas.txt"
TECHS = "common/technologies/MFU_afrika_korps_hidden.txt"
LEVEL_FX = "common/scripted_effects/MFU_afrika_korps_level_effects.txt"
SPAWN_FX = "common/scripted_effects/MFU_afrika_korps_spawn_effects.txt"
LOC = "localisation/english/MFU_afrika_korps_l_english.yml"
GENERATED = [IDEAS, TECHS, LEVEL_FX, SPAWN_FX, LOC]

CITIES = {"tunis": (458, 11969), "tripoli": (448, 1149), "benghazi": (450, 11954), "tobruk": (451, 13741)}
SUPPORT = ["artillery", "recon_ac", "mobile_engineer", "anti_tank", "maintenance_company",
           "logistics_company_mot", "anti_air_heavy_support", "signal_company"]

TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


def read(rel):
    with open(os.path.join(MOD, rel), encoding="utf-8-sig", errors="replace") as f:
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


@test
def test_spirit_ideas():
    text = strip(read(IDEAS))
    country = block(text, "country")
    need(country is not None, "no `country = {` category")
    ideas = dict(children(country))
    for n in range(0, 15):
        b = ideas.get(f"MFU_ak_spirit_{n}")
        need(b is not None, f"MFU_ak_spirit_{n} missing")
        need(re.search(r"allowed\s*=\s*\{\s*always\s*=\s*no\s*\}", b), f"level {n}: allowed = {{ always = no }} missing")
        need(re.search(r"removal_cost\s*=\s*-1\b", b), f"level {n}: removal_cost = -1 missing")
        mod = block(b, "modifier")
        need(mod is not None, f"level {n}: no modifier block")
        for tt in ("MFU_ak_desert_tt", "MFU_ak_decay_tt"):
            need(re.search(r"custom_modifier_tooltip\s*=\s*" + tt + r"\b", mod), f"level {n}: tooltip {tt} missing")
        keys = re.findall(r"([A-Za-z_]+)\s*=", mod)
        need(set(keys) == {"custom_modifier_tooltip"}, f"level {n}: unexpected stat modifier(s) {sorted(set(keys))}")
        tm = block(b, "targeted_modifier")
        if n == 0:
            need(tm is None, "level 0 must have no targeted_modifier")
            continue
        need(tm is not None, f"level {n}: targeted_modifier missing")
        need(re.search(r"\btag\s*=\s*SOV\b", tm), f"level {n}: tag = SOV missing")
        for key in ("attack_bonus_against", "defense_bonus_against"):
            m = re.search(key + r"\s*=\s*(-?[0-9.]+)", tm)
            need(m is not None, f"level {n}: {key} missing")
            need(abs(float(m.group(1)) + n / 100.0) < 1e-9, f"level {n}: {key} = {m.group(1)}, expected {-n / 100.0}")
        need(len(re.findall(r"=", tm)) == 3, f"level {n}: targeted_modifier has extra entries")
    need(set(ideas) == {f"MFU_ak_spirit_{n}" for n in range(15)}, "unexpected extra ideas in the file")


@test
def test_spirit_picture_resolves():
    # The engine builds the sprite name as "GFX_idea_" + picture, so a picture that already starts with GFX_ resolves to
    # GFX_idea_GFX_idea_... and shows the question-mark fallback. The old Afrikakorps icon is GFX_idea_GER_afrika_campaign.
    text = strip(read(IDEAS))
    pics = re.findall(r"\bpicture\s*=\s*(\S+)", text)
    need(len(pics) == 15, f"expected 15 picture lines, found {len(pics)}")
    for pic in pics:
        need(not pic.startswith("GFX_"), f"picture = {pic}: drop the GFX_idea_ prefix, the engine adds it")
        need(pic == "GER_afrika_campaign", f"picture = {pic}: must reuse the old Afrikakorps icon GER_afrika_campaign")
    sprite = "GFX_idea_" + pics[0]
    tex = None
    for fn in os.listdir(os.path.join(MOD, "interface")):
        if fn.endswith(".gfx"):
            m = re.search(r'name\s*=\s*"' + re.escape(sprite) + r'"\s*texturefile\s*=\s*"([^"]+)"', read("interface/" + fn))
            if m:
                tex = m.group(1)
    need(tex is not None, f"sprite {sprite} is not defined in interface/*.gfx")
    need(os.path.isfile(os.path.join(MOD, tex)), f"texture {tex} for {sprite} does not exist")


@test
def test_desert_techs():
    text = strip(read(TECHS))
    techs = dict(children(block(text, "technologies") or ""))
    need(set(techs) == {f"MFU_ak_desert_{k}" for k in range(1, 11)}, f"tech ids wrong: {sorted(techs)}")
    for k in range(1, 11):
        b = techs[f"MFU_ak_desert_{k}"]
        need(re.search(r"research_cost\s*=\s*-1\b", b), f"tech {k}: research_cost = -1 missing")
        need(re.search(r"allow\s*=\s*\{\s*always\s*=\s*no\s*\}", b), f"tech {k}: allow = {{ always = no }} missing")
        cats = [name for name, _ in children(b) if name.startswith("category_")]
        need(cats == ["category_front_line"], f"tech {k}: categories {cats}, expected only category_front_line")
        cat = block(b, "category_front_line")
        terrain = dict(children(cat))
        need(set(terrain) == {"desert", "deep_desert"}, f"tech {k}: terrain blocks {sorted(terrain)}")
        for tname, tbody in terrain.items():
            m = re.fullmatch(r"\s*attack\s*=\s*([0-9.]+)\s*", tbody)
            need(m is not None, f"tech {k}/{tname}: body must be only `attack = ...`")
            need(abs(float(m.group(1)) - k / 100.0) < 1e-9, f"tech {k}/{tname}: attack {m.group(1)}, expected {k / 100.0}")


@test
def test_front_line_covers_line_battalions():
    # basis for the single-category choice: the battalions the decision spawns carry category_front_line
    for fname, unit in (("medium_armor.txt", "medium_armor"), ("light_armor.txt", "light_armor"), ("infantry.txt", "motorized")):
        text = strip(read("common/units/" + fname))
        sub = dict(children(block(text, "sub_units")))
        cats = block(sub[unit], "categories").split()
        need("category_front_line" in cats, f"{unit} is not in category_front_line")
        need(len([c for c in cats if c == "category_front_line"]) == 1, f"{unit} lists category_front_line twice")


@test
def test_level_effects():
    text = strip(read(LEVEL_FX))
    fx = dict(children(text))
    ids = [f"MFU_ak_spirit_{n}" for n in range(15)]
    techs = [f"MFU_ak_desert_{k}" for k in range(1, 11)]
    for name in ("MFU_ak_set_sov_idea", "MFU_ak_set_desert_tech", "MFU_ak_clear_spirit"):
        need(name in fx, f"effect {name} missing")
    body = fx["MFU_ak_set_sov_idea"]
    rem = block(body, "remove_ideas")
    need(rem is not None and rem.split() == ids, "set_sov_idea must remove all 15 spirits in one remove_ideas list")
    need(body.index("remove_ideas") < body.index("add_ideas"), "set_sov_idea must remove before it adds")
    for n in range(15):
        branch = re.search(r"check_variable\s*=\s*\{\s*MFU_ak_sov\s*=\s*%d\s*\}" % n, body)
        need(branch is not None, f"set_sov_idea: no branch for MFU_ak_sov = {n}")
        need(re.search(r"add_ideas\s*=\s*MFU_ak_spirit_%d\b" % n, body), f"set_sov_idea: no add_ideas for level {n}")
    d = fx["MFU_ak_set_desert_tech"]
    for t in techs:
        need(re.search(t + r"\s*=\s*0", d), f"set_desert_tech: {t} never zeroed")
        need(re.search(t + r"\s*=\s*1", d), f"set_desert_tech: {t} never set to 1")
    need(re.search(r"popup\s*=\s*no", d), "set_desert_tech: popup = no missing")
    need(d.index("= 0") < d.index("= 1"), "set_desert_tech must zero before it sets")
    for k in range(1, 11):
        need(re.search(r"check_variable\s*=\s*\{\s*MFU_ak_desert\s*=\s*%d\s*\}" % k, d), f"set_desert_tech: no branch for {k}")
    c = fx["MFU_ak_clear_spirit"]
    rem = block(c, "remove_ideas")
    need(rem is not None and rem.split() == ids, "clear_spirit must remove all 15 spirits")
    for t in techs:
        need(re.search(t + r"\s*=\s*0", c), f"clear_spirit: {t} not zeroed")
    need("= 1" not in c.replace("= 10", ""), "clear_spirit must not switch anything on")


def parse_templates(text):
    out = []
    for body in all_blocks(text, "division_template"):
        regs = [(m.group(1), int(m.group(2)), int(m.group(3)))
                for m in re.finditer(r"(\w+)\s*=\s*\{\s*x\s*=\s*(\d+)\s*y\s*=\s*(\d+)\s*\}", block(body, "regiments"))]
        sup = [(m.group(1), int(m.group(2)), int(m.group(3)))
               for m in re.finditer(r"(\w+)\s*=\s*\{\s*x\s*=\s*(\d+)\s*y\s*=\s*(\d+)\s*\}", block(body, "support"))]
        name = re.search(r'name\s*=\s*"([^"]+)"', body).group(1)
        out.append((name, body, regs, sup))
    return out


@test
def test_spawn_effects():
    text = strip(read(SPAWN_FX))
    tpls = parse_templates(text)
    need(len(tpls) == 4, f"expected 4 division_template blocks, found {len(tpls)}")
    seen = set()
    for name, body, regs, sup in tpls:
        light = "leichte" in name
        need(name in ("Afrikakorps Panzer-Division", "Afrikakorps leichte Panzer-Division"), f"template name {name!r}")
        tank = "light_armor" if light else "medium_armor"
        tanks = [(x, y) for t, x, y in regs if t == tank]
        mots = [(x, y) for t, x, y in regs if t == "motorized"]
        need(len(tanks) + len(mots) == len(regs), f"{name}: only {tank}/motorized allowed")
        need(sorted(tanks) == [(x, y) for x in range(3) for y in range(3)], f"{name}: tank layout wrong {sorted(tanks)}")
        base = [(x, y) for x in (3, 4) for y in range(3)]
        wide = sorted(base + [(3, 3), (4, 3)])
        need(sorted(mots) in (sorted(base), wide), f"{name}: motorized layout wrong {sorted(mots)}")
        seen.add((light, len(mots) == 8))
        need(sorted(sup) == [(s, 0, i) for i, s in sorted(enumerate(SUPPORT), key=lambda p: p[1])] or
             [s for s, _, _ in sorted(sup, key=lambda e: e[2])] == SUPPORT, f"{name}: support set/order wrong")
        need(all(x == 0 for _, x, _ in sup) and sorted(y for _, _, y in sup) == list(range(8)), f"{name}: support grid wrong")
        need(re.search(r"division_names_group\s*=\s*GER_Arm_01\b", body), f"{name}: division_names_group")
        need(re.search(r"priority\s*=\s*2\b", body), f"{name}: priority = 2")
    need(seen == {(False, False), (False, True), (True, False), (True, True)}, f"template variants covered: {sorted(seen)}")
    units = all_blocks(text, "create_unit")
    need(len(units) == 16, f"expected 16 create_unit blocks, found {len(units)}")
    per_city = {k: 0 for k in CITIES}
    variants = set()
    for u in units:
        need(re.search(r"start_equipment_factor\s*=\s*1\b", u), "create_unit: start_equipment_factor = 1 missing")
        need(re.search(r"start_experience_factor\s*=\s*0\.5\b", u), "create_unit: start_experience_factor = 0.5 missing")
        need(re.search(r"owner\s*=\s*GER\b", u), "create_unit: owner = GER missing")
        prov = int(re.search(r"prioritize_location\s*=\s*(\d+)", u).group(1))
        city = [k for k, (_, p) in CITIES.items() if p == prov]
        need(len(city) == 1, f"create_unit: prioritize_location {prov} not a spawn province")
        per_city[city[0]] += 1
        light = "light_tank_chassis" in u
        need(re.search(r"\bcount\s*=\s*%d\b" % (4 if light else 3), u), "create_unit: wrong count")
        need("light_tank_chassis" in u or "medium_tank_chassis" in u, "create_unit: no tank variant")
        need(re.search(r'owner\s*=\s*\\"GER\\"', u), "create_unit: variant owner missing")
        variants.add(re.search(r'version_name\s*=\s*\\"([^"\\]+)\\"', u).group(1))
    need(per_city == {k: 4 for k in CITIES}, f"create_unit per city: {per_city}")
    need(variants == {"Panzer III Ausf.H", "Panzer IV", "Panzer 38(t)", "Panzer II Ausf.a"}, f"variants: {sorted(variants)}")
    for chassis, vname in (("medium_tank_chassis_1940", "Panzer III Ausf.H"), ("medium_tank_chassis_1946", "Panzer IV"),
                           ("light_tank_chassis_1940", "Panzer 38(t)"), ("light_tank_chassis_1936", "Panzer II Ausf.a")):
        need(re.search(chassis + r"\s*=\s*\{\s*owner\s*=\s*\\\"GER\\\"\s*version_name\s*=\s*\\\"" + re.escape(vname), text),
             f"{chassis} -> {vname} pairing missing")
    for city, (state, _) in CITIES.items():
        need(len(re.findall(r"\b%d\s*=\s*\{\s*create_unit" % state, text)) == 4, f"state {state} scope missing 4 times")
    # first usable city wins: the four city triggers appear in priority order
    order = [text.index("MFU_ak_city_" + c) for c in ("tunis", "tripoli", "benghazi", "tobruk")]
    need(order == sorted(order), "city triggers not in priority order")


def unit_defs():
    defs = {}
    import glob
    for p in glob.glob(os.path.join(MOD, "common", "units", "*.txt")):
        with open(p, encoding="utf-8-sig", errors="replace") as f:
            t = strip(f.read())
        sub = block(t, "sub_units")
        if sub:
            defs.update(dict(children(sub)))
    return defs


@test
def test_support_ids_valid():
    defs = unit_defs()
    for sid in SUPPORT:
        need(sid in defs, f"support id {sid} is not defined in common/units")
        b = defs[sid]
        need(re.search(r"group\s*=\s*support\b", b), f"{sid}: group is not support")
        need(not re.search(r"regimental\s*=\s*yes", b), f"{sid}: is regimental, not divisional")


@test
def test_loc():
    raw = open(os.path.join(MOD, LOC), "rb").read()
    need(raw.startswith(b"\xef\xbb\xbf"), "loc file must start with a UTF-8 BOM")
    lines = raw.decode("utf-8-sig").splitlines()
    need(lines[0].strip() == "l_english:", "first line must be l_english:")
    keys = {}
    for ln in lines[1:]:
        m = re.match(r'^ ([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', ln)
        if m:
            keys[m.group(1)] = m.group(2)
    want = {f"MFU_ak_spirit_{n}{s}" for n in range(15) for s in ("", "_desc")}
    want |= {f"MFU_ak_desert_{k}" for k in range(1, 11)}
    want |= {"MFU_ak_desert_tt", "MFU_ak_decay_tt", "MFU_ak_effect_tt", "MFU_ak_spawn_tt"}
    need(not (want - set(keys)), f"missing loc keys: {sorted(want - set(keys))}")
    need("[?MFU_ak_desert|" in keys["MFU_ak_desert_tt"], "MFU_ak_desert_tt must show the live MFU_ak_desert variable")
    for rel in GENERATED[:4] + ["common/decisions/GER.txt"]:
        for m in re.finditer(r"(?:custom_modifier_tooltip|custom_effect_tooltip)\s*=\s*(MFU_ak_\w+)", strip(read(rel))):
            need(m.group(1) in keys, f"{rel}: tooltip key {m.group(1)} has no loc")


@test
def test_braces():
    for rel in GENERATED:
        text = read(rel)
        if rel == LOC:
            continue
        t = re.sub(r'"(?:[^"\\]|\\.)*"', '""', strip(text))
        need(t.count("{") == t.count("}"), f"{rel}: unbalanced braces ({t.count('{')} vs {t.count('}')})")
        depth = 0
        for ch in t:
            depth += (ch == "{") - (ch == "}")
            need(depth >= 0, f"{rel}: closing brace before opening")


@test
def test_sync_clean():
    need(os.path.exists(os.path.join(MOD, TECHS)), "tech file missing")
    r = subprocess.run([sys.executable, "-I", "tools/terrain_copies/sync.py", "--check"], cwd=MOD, capture_output=True, text=True)
    need(r.returncode == 0, "terrain_copies sync --check not clean:\n" + r.stdout)


SCRIPT_FX = "common/scripted_effects/MFU_afrika_korps_scripted_effects.txt"
ON_ACTIONS = "common/on_actions/MFU_afrika_korps_on_actions.txt"
DECISIONS = "common/decisions/GER.txt"


def script_effects():
    return dict(children(strip(read(SCRIPT_FX))))


def flat(s):
    return re.sub(r"\s+", " ", s)


@test
def test_compute_sov_guarded():
    body = script_effects()["MFU_ak_compute_sov"]
    branches = children(body)
    need([k for k, _ in branches] == ["if"] + ["else_if"] * 8, f"expected if + 8 else_if, got {[k for k, _ in branches]}")
    seen = {}
    for _, b in branches:
        m = re.search(r"ENG\s*=\s*\{\s*has_idea\s*=\s*GER_aatlantic_wall_(\d)\s*\}", block(b, "limit"))
        s = re.search(r"set_variable\s*=\s*\{\s*MFU_ak_sov\s*=\s*(\d+)\s*\}", b)
        need(m is not None and s is not None, "each branch must test ENG's wall idea and set MFU_ak_sov")
        seen[int(m.group(1))] = int(s.group(1))
    need(seen == {w: 14 - w for w in range(9)}, f"Africa level -> penalty mapping wrong: {seen}")


@test
def test_sync_effect():
    body = script_effects()["MFU_ak_sync"]
    loop = block(body, "every_country")
    need(loop is not None and "has_country_flag = MFU_ak_recipient" in flat(block(loop, "limit")), "sync must loop over recipients")
    for var in ("MFU_ak_sov", "MFU_ak_desert"):
        need(re.search(r"set_variable\s*=\s*\{\s*var\s*=\s*%s\s*value\s*=\s*GER\.%s\s*\}" % (var, var), loop), f"sync must copy {var} from GER")
    for fx in ("MFU_ak_set_sov_idea = yes", "MFU_ak_set_desert_tech = yes"):
        need(fx in loop, f"sync must call {fx}")
    need(re.search(r"set_variable\s*=\s*\{\s*var\s*=\s*MFU_ak_applied_sov\s*value\s*=\s*MFU_ak_sov\s*\}", body.replace(loop, "")),
         "sync must store MFU_ak_applied_sov on GER")


@test
def test_grant_effect():
    body = script_effects()["MFU_ak_grant"]
    loop = block(body, "every_country")
    lim = flat(block(loop, "limit"))
    for cond in ("is_in_faction_with = GER", "tag = GER", "tag = EFR", "tag = SPR"):
        need(cond in lim, f"recipient limit lacks {cond}")
    need("set_country_flag = MFU_ak_recipient" in loop, "grant must flag recipients")
    rest = body.replace(loop, "")
    need("set_country_flag = MFU_ak_active" in rest, "grant must set MFU_ak_active")
    need(re.search(r"MFU_ak_desert\s*=\s*10\b", rest), "grant must set MFU_ak_desert = 10")
    need(rest.index("MFU_ak_compute_sov = yes") < rest.index("MFU_ak_sync = yes"), "grant: compute before sync")


@test
def test_weekly_stops_after_barbarossa():
    body = script_effects()["MFU_ak_weekly"]
    top = children(body)
    need(len(top) == 1 and top[0][0] == "if", "weekly must be one guarded if")
    lim = flat(block(top[0][1], "limit"))
    need("NOT = { has_completed_focus = GER_ussr_war_goal }" in lim, "weekly lacks the Barbarossa guard")
    need("NOT = { has_country_flag = MFU_ak_frozen }" in lim, "weekly lacks the frozen guard")
    inner = [b for k, b in children(top[0][1]) if k == "if"]
    need(len(inner) == 1, "weekly needs exactly one inner if (the sync guard)")
    ilim = flat(block(inner[0], "limit"))
    need("has_country_flag = MFU_ak_active" in ilim, "sync guard lacks MFU_ak_active")
    need(re.search(r"NOT = \{ check_variable = \{ MFU_ak_sov = MFU_ak_applied_sov \} \}", ilim), "sync guard must compare against applied level")
    need("MFU_ak_sync = yes" in inner[0], "sync missing in guard")
    need("MFU_ak_sync = yes" not in top[0][1].replace(inner[0], ""), "sync may only run inside the guard")
    need(body.count("MFU_ak_compute_sov = yes") == 1, "compute must run once per weekly pulse")


@test
def test_freeze_without_spirit():
    body = script_effects()["MFU_ak_freeze"]
    need("MFU_ak_compute_sov = yes" in body, "freeze must recompute first")
    need("set_country_flag = MFU_ak_frozen" in body, "freeze must set MFU_ak_frozen")
    guarded = [b for k, b in children(body) if k == "if"]
    need(len(guarded) == 1 and "MFU_ak_sync = yes" in guarded[0], "sync must sit in one if")
    need("has_country_flag = MFU_ak_active" in flat(block(guarded[0], "limit")), "freeze sync guard lacks MFU_ak_active")
    need(body.count("MFU_ak_sync = yes") == 1, "freeze must not sync outside the guard")


@test
def test_monthly_end_condition():
    body = script_effects()["MFU_ak_monthly"]
    top = children(body)
    need(len(top) == 1 and top[0][0] == "if", "monthly must be one guarded if")
    lim = flat(block(top[0][1], "limit"))
    need("has_country_flag = MFU_ak_active" in lim and "has_country_flag = MFU_ak_frozen" in lim, "monthly guard wrong")
    need("date > 1942.1.2" in lim, "monthly decay must wait for 1942 (date > 1942.1.2 so the first tick is 1942.2.1)")
    inner = children(top[0][1])
    for var in ("MFU_ak_sov", "MFU_ak_desert"):
        d = [b for k, b in inner if k == "if" and ("add_to_variable = { %s = -1 }" % var) in flat(b)]
        need(len(d) == 1, f"monthly must decrement {var} exactly once")
        need(re.search(r"check_variable\s*=\s*\{\s*%s\s*>\s*0\s*\}" % var, block(d[0], "limit")), f"{var} decrement must be guarded > 0")
    end = [b for k, b in inner if k == "if" and "MFU_ak_end = yes" in b]
    need(len(end) == 1, "monthly must call MFU_ak_end once")
    el = flat(block(end[0], "limit"))
    need("MFU_ak_sov = 0" in el and "MFU_ak_desert = 0" in el and "OR" not in el, "end requires BOTH numbers at 0")
    need(top[0][1].index("MFU_ak_sync = yes") < top[0][1].index("MFU_ak_end = yes"), "sync before end")


@test
def test_end_effect():
    body = script_effects()["MFU_ak_end"]
    loop = block(body, "every_country")
    need("has_country_flag = MFU_ak_recipient" in flat(block(loop, "limit")), "end must loop over recipients")
    need("MFU_ak_clear_spirit = yes" in loop and "clr_country_flag = MFU_ak_recipient" in loop, "end must clear the spirit and recipient flag")
    rest = body.replace(loop, "")
    for fl in ("MFU_ak_active", "MFU_ak_frozen"):
        need("clr_country_flag = " + fl in rest, f"end must clear {fl}")


@test
def test_barbarossa_hook_first():
    t = strip(read(DECISIONS))
    m = re.search(r"\n\s*GER_ussr_war_goal\s*=\s*\{", t)
    need(m is not None, "GER_ussr_war_goal decision not found")
    dec = t[m.end():match_brace(t, m.end() - 1)]
    ce = block(dec, "complete_effect")
    need(ce is not None and ce.lstrip().startswith("hidden_effect"), "complete_effect must start with its hidden_effect block (keeps the freeze out of the tooltip)")
    hidden = block(ce, "hidden_effect")
    need(hidden.lstrip().startswith("MFU_ak_freeze = yes"), "the first statement of the leading hidden_effect must be MFU_ak_freeze = yes")
    need(t.count("MFU_ak_freeze = yes") == 1, "MFU_ak_freeze must be called from exactly one place")


@test
def test_on_actions():
    acts = dict(children(block(strip(read(ON_ACTIONS)), "on_actions")))
    need("MFU_ak_weekly = yes" in acts.get("on_weekly_GER", ""), "on_weekly_GER must call MFU_ak_weekly")
    need("MFU_ak_monthly = yes" in acts.get("on_monthly_GER", ""), "on_monthly_GER must call MFU_ak_monthly")


TRIGGERS = "common/scripted_triggers/MFU_afrika_korps_scripted_triggers.txt"


def decision_entry():
    t = strip(read(DECISIONS))
    m = re.search(r"\n\s*GER_africa_korps\s*=\s*\{", t)
    need(m is not None, "GER_africa_korps decision not found")
    return t[m.end():match_brace(t, m.end() - 1)]


@test
def test_decision_shape():
    d = decision_entry()
    need(block(d, "complete_effect") is not None, "complete_effect missing")
    for bad in ("days_remove", "remove_effect"):
        need(bad not in d, f"{bad} must be gone (instant decision)")
    need(re.search(r"fire_only_once\s*=\s*yes", d), "fire_only_once = yes missing")
    need(re.search(r"\bcost\s*=\s*25\b", d), "cost = 25 missing")
    need(re.search(r"ai_will_do\s*=\s*\{\s*factor\s*=\s*10\s*\}", d), "ai_will_do factor 10 missing")
    need(re.search(r"allowed\s*=\s*\{\s*tag\s*=\s*GER\s*\}", d), "allowed = { tag = GER } missing")
    avail, vis = flat(block(d, "available")), flat(block(d, "visible"))
    for cond in ("has_war_with = ENG", "country_exists = EFR", "NOT = { has_completed_focus = GER_ussr_war_goal }", "MFU_ak_any_city = yes"):
        need(cond in avail, f"available lacks {cond}")
    for cond in ("has_war_with = ENG", "ITA = { has_war_with = ENG }", "NOT = { has_completed_focus = GER_ussr_war_goal }"):
        need(cond in vis, f"visible lacks {cond}")
    need("has_full_control_of_state" not in avail + vis, "old Tripoli control gate must be gone")


@test
def test_decision_effect():
    ce = block(decision_entry(), "complete_effect")
    need(ce.index("MFU_ak_grant = yes") < ce.index("MFU_ak_spawn_divisions = yes"), "grant must come before spawn")
    hidden = block(ce, "hidden_effect")
    need(hidden is not None and "MFU_ak_grant = yes" in hidden and "MFU_ak_spawn_divisions = yes" in hidden, "grant and spawn belong in hidden_effect")
    for tt in ("MFU_ak_effect_tt", "MFU_ak_spawn_tt"):
        need(re.search(r"custom_effect_tooltip\s*=\s*" + tt + r"\b", ce.replace(hidden, "")), f"visible tooltip {tt} missing")
    for bad in ("GER_afrika_campaign", "GER_afrikakorps_tt", "germany.233", "add_ideas"):
        need(bad not in ce, f"complete_effect must not reference {bad}")


@test
def test_triggers():
    trig = dict(children(strip(read(TRIGGERS))))
    names = ["MFU_ak_city_tunis", "MFU_ak_city_tripoli", "MFU_ak_city_benghazi", "MFU_ak_city_tobruk", "MFU_ak_any_city",
             "MFU_ak_has_medium_tech", "MFU_ak_has_medium_1940", "MFU_ak_has_light_1940", "MFU_ak_has_width_tech"]
    need(set(trig) == set(names), f"trigger set wrong: {sorted(trig)}")
    for key, state in (("tunis", 458), ("tripoli", 448), ("benghazi", 450), ("tobruk", 451)):
        b = flat(trig["MFU_ak_city_" + key])
        need(re.match(r"\s*%d = \{" % state, b), f"{key}: must scope into state {state}")
        for ctl in ("is_controlled_by = GER", "is_controlled_by = ITA", "is_controlled_by_ROOT_or_ally = yes"):
            need(ctl in b, f"{key}: lacks {ctl}")
        need("is_controlled_by = EFR" not in b, f"{key}: a Vichy-held city must not count by itself (neutral territory); an allied Vichy is covered by ROOT_or_ally")
        need(("is_demilitarized_zone = no" in b) == (key == "tunis"), f"{key}: demilitarized gate only belongs on Tunis")
    any_city = flat(trig["MFU_ak_any_city"])
    need(all(("MFU_ak_city_%s = yes" % c) in any_city for c in ("tunis", "tripoli", "benghazi", "tobruk")) and "OR" in any_city, "any_city must OR the four")
    need("ger_1939_medium_tank_chassis" in trig["MFU_ak_has_medium_tech"] and "ger_1940_medium_tank_chassis" in trig["MFU_ak_has_medium_tech"], "medium tech OR")
    need(flat(trig["MFU_ak_has_medium_1940"]).strip() == "has_tech = ger_1940_medium_tank_chassis", "medium_1940")
    need(flat(trig["MFU_ak_has_light_1940"]).strip() == "has_tech = ger_1940_light_tank_chassis", "light_1940")
    need(flat(trig["MFU_ak_has_width_tech"]).strip() == "has_tech = width_tech", "width tech")


@test
def test_hand_written_braces():
    for rel in (SCRIPT_FX, ON_ACTIONS, TRIGGERS, DECISIONS):
        t = re.sub(r'"(?:[^"\\]|\\.)*"', '""', strip(read(rel)))
        need(t.count("{") == t.count("}"), f"{rel}: unbalanced braces ({t.count('{')} vs {t.count('}')})")


def loc_value(rel, key):
    for ln in read(rel).splitlines():
        m = re.match(r'^ ' + re.escape(key) + r':\d*\s+"(.*)"\s*$', ln)
        if m:
            return m.group(1)
    raise AssertionError(f"{rel}: key {key} not found")


@test
def test_loc_wording_is_honest():
    # The penalty is 10 + the Africa swing, so the net against Barbarossa is a flat -10%; the text must say that, not
    # "offsets the bonus, currently N%" (the Africa bonus is +0% at the neutral level).
    eff = loc_value(LOC, "MFU_ak_effect_tt")
    need("flat" in eff and "-10%" in eff, "MFU_ak_effect_tt must explain the flat -10% net")
    need("currently" not in eff and "offsets" not in eff, "MFU_ak_effect_tt must not say the penalty 'offsets' or 'currently' equals the bonus")
    for n in range(15):
        d = loc_value(LOC, f"MFU_ak_spirit_{n}_desc")
        need("flat" in d and "offsets" not in d, f"MFU_ak_spirit_{n}_desc wording")
    fd = loc_value("localisation/english/focus_l_english.yml", "GER_africa_korps_desc")
    need("flat" in fd and "offsets" not in fd, "decision description wording")
    # Decay starts in 1942, after Barbarossa freezes the numbers; the text must say so.
    for key in ["MFU_ak_decay_tt", "MFU_ak_effect_tt"] + [f"MFU_ak_spirit_{n}_desc" for n in range(15)]:
        need("1942" in loc_value(LOC, key), f"{key} must say the decay starts in 1942")
    need("1942" in fd, "decision description must say the decay starts in 1942")


@test
def test_old_spirit_gone():
    gone = re.compile(r"(?<![A-Za-z0-9_])(GER_afrika_campaign2?|GER_afrika_spirit_dissappears_tt|GER_africa_mastery_gain_bonus_tt)(?![A-Za-z0-9_])")
    for top in ("common", "localisation"):
        for root, _, files in os.walk(os.path.join(MOD, top)):
            for fn in files:
                if not fn.endswith((".txt", ".yml", ".gui", ".gfx", ".lua")):
                    continue
                path = os.path.join(root, fn)
                with open(path, encoding="utf-8-sig", errors="replace") as f:
                    for n, line in enumerate(f, 1):
                        if re.match(r"\s*picture\s*=\s*GER_afrika_campaign\s*$", line):
                            continue  # the idea icon (sprite GFX_idea_GER_afrika_campaign), not the removed idea
                        m = gone.search(line)
                        need(m is None, f"{os.path.relpath(path, MOD)}:{n}: still references {m.group(1) if m else ''}")
    need("GER_afrikakorps_tt:0" in read("localisation/english/tooltips_l_english.yml"), "GER_afrikakorps_tt loc must stay (Italian focus)")
    need("GER_afrikakorps_tt" in read("common/national_focus/italy.txt"), "the Italian focus must still use GER_afrikakorps_tt")
    ideas = read("common/ideas/germany.txt")
    need(re.search(r"\bGER_atlantic_wall_00\s*=\s*\{", ideas), "GER_atlantic_wall_00 must stay defined")
    need(re.search(r"\bGER_africa_mastery_gain_bonus_spirit\s*=\s*\{", ideas), "hidden GER_africa_mastery_gain_bonus_spirit must stay defined")
    t = re.sub(r'"(?:[^"\\]|\\.)*"', '""', strip(ideas))
    need(t.count("{") == t.count("}"), "common/ideas/germany.txt: unbalanced braces")


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
