# Japan Overreach Compliance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Japan's occupation compliance collapse as its Asian conquest counter grows. The collapse is harshest in inland China.

**Architecture:** One scripted effect recomputes three Japan variables from the conquest counter `JAP_resistance_target_modifier` (K). It copies the inland or middle value into a per-state variable on 30 Chinese states and makes sure one state dynamic modifier is attached there. The 10 existing trigger sites call that effect instead of hand-adding compliance deltas.

**Tech Stack:** HOI4 1.19.5 Clausewitz script (on_actions, scripted effects/triggers, dynamic modifiers, localisation). Python 3 static checker in the `tools/<feature>/check.py` style of `tools/afrika_korps/check.py`.

**Spec:** `docs/superpowers/specs/2026-11-14-japan-overreach-compliance-design.md`

## Global Constraints

- Country-wide: `JAP_compliance_gain_modifier` = min(0, −0.20·K)
- Inland: `JAP_inland_overreach_compliance` = min(0, −0.25·K)
- Middle: `JAP_middle_overreach_compliance` = min(0, −0.125·K)
- Inland state ids (21): 283 287 601 603 604 605 616 617 618 619 747 748 750 751 752 753 754 755 756 759 760
- Middle state ids (9): 325 599 600 602 620 622 744 820 821
- Modifier `JAP_overstretched_occupation` is added with NO `scope`. Its only modifier line is `compliance_gain = JAP_overreach_compliance_gain` (a state variable). Its enable is `ROOT = { controller = { OR = { tag = JAP is_in_faction_with = JAP is_subject_of = JAP } } }`. Icon `GFX_modifiers_generic_resistance`.
- Recompute effect name: `JAP_update_overreach_compliance`, run in JAP scope.
- Do not touch any `JAP_resistance_target_modifier` or `MAN_resistance_target_modifier` line. Do not change resistance target anywhere.
- Script files: UTF-8 without BOM, CRLF. This matches the existing `MFU_*` files, `00_on_actions.txt` and `08_hopping_on_actions.txt` (both CRLF). The loc file needs a UTF-8 BOM, then `l_english:`.
- Loc: `JAP_overstretched_occupation: "Overstretched Occupation"`. `JAP_overstretched_occupation_desc` is flavour only, with no numbers.
- Minimal or no code comments (user preference).
- Do not commit. The user commits.

## Review Focus

1. **Counter below 0** (rollback overshoot bug): all three derived values must stay 0, never positive. Pinned by `test_effect_math` (clamp max 0).
2. **Inland state held by Manchukuo or RCC:** the penalty must apply. **Held by a non-Japanese-faction occupier** (SOV, PRC): it must not. Pinned by `test_modifier_definition` (enable shape).
3. **Effect runs many times** (every counter change): the modifier must never stack or re-add. Pinned by `test_attach_is_guarded`.
4. **Existing save, counter changes mid-game:** states get the modifier and their value without a new game. Pinned by `test_effect_copies_state_values` (the effect attaches as well as on_startup).
5. **Counter 0 at game start:** zero penalty, so early compliance still builds. Pinned by `test_simulated_outcome` (K = 0 row).

---

### Task 1: Overreach mechanic files + static checker

**Files:**
- Create: `tools/jap_overreach/check.py`
- Create: `common/scripted_triggers/MFU_JAP_overreach_scripted_triggers.txt`
- Create: `common/scripted_effects/MFU_JAP_overreach_scripted_effects.txt`
- Create: `common/dynamic_modifiers/MFU_JAP_overreach_dynamic_modifiers.txt`
- Create: `common/on_actions/MFU_JAP_overreach_on_actions.txt`
- Create: `localisation/english/MFU_JAP_overreach_l_english.yml`

**Interfaces:**
- Produces:
  - scripted triggers `JAP_is_inland_china_state` and `JAP_is_middle_china_state` (state scope, an `OR` of `state = <id>`)
  - scripted effect `JAP_update_overreach_compliance` (JAP scope)
  - state variable `JAP_overreach_compliance_gain`
  - Japan variables `JAP_inland_overreach_compliance` and `JAP_middle_overreach_compliance`
  - dynamic modifier `JAP_overstretched_occupation`
  - checker CLI `python -I tools/jap_overreach/check.py` (prints PASS/FAIL per test, exits non-zero on any FAIL)

- [ ] **Step 1: Write the checker with these tests** (reuse the `read`/`strip`/`match_brace`/`children` helper style from `tools/afrika_korps/check.py`)

```python
INLAND = {283,287,601,603,604,605,616,617,618,619,747,748,750,751,752,753,754,755,756,759,760}
MIDDLE = {325,599,600,602,620,622,744,820,821}

def test_state_lists():            # scripted triggers list exactly these ids, disjoint
    assert ids_in("JAP_is_inland_china_state") == INLAND
    assert ids_in("JAP_is_middle_china_state") == MIDDLE

def test_lists_match_history_tiers():  # from history/states/*: CHI_tougher_resistance3/4 -> INLAND, CHI_tougher_resistance2 -> MIDDLE
    assert history_tier_ids({3, 4}) == INLAND and history_tier_ids({2}) == MIDDLE

def test_effect_math():            # in JAP_update_overreach_compliance
    assert derived("JAP_compliance_gain_modifier")    == ("JAP_resistance_target_modifier", -0.20, "max0")
    assert derived("JAP_inland_overreach_compliance") == ("JAP_resistance_target_modifier", -0.25, "max0")
    assert derived("JAP_middle_overreach_compliance") == ("JAP_resistance_target_modifier", -0.125, "max0")
    # each = set_variable from K, then multiply_variable by k, then clamp_variable {var=... max=0}, in that order

def test_effect_copies_state_values():
    # an every_state limited by JAP_is_inland_china_state sets JAP_overreach_compliance_gain = JAP.JAP_inland_overreach_compliance
    # an every_state limited by JAP_is_middle_china_state sets it = JAP.JAP_middle_overreach_compliance
    # both blocks add_dynamic_modifier = { modifier = JAP_overstretched_occupation } with no scope key

def test_attach_is_guarded():      # every add_dynamic_modifier of JAP_overstretched_occupation sits under a NOT has_dynamic_modifier check for the same modifier
    ...

def test_modifier_definition():
    m = modifier("JAP_overstretched_occupation")
    assert m.lines == {"compliance_gain": "JAP_overreach_compliance_gain"}
    assert m.icon == "GFX_modifiers_generic_resistance"
    assert m.enable_normalized == "ROOT={controller={OR={tag=JAP is_in_faction_with=JAP is_subject_of=JAP}}}"

def test_on_startup():             # on_actions.on_startup.effect contains JAP = { JAP_update_overreach_compliance = yes }
    ...

def test_loc():                    # BOM ef bb bf, first line l_english:, both keys present, _desc has no digits
    ...

def test_braces_and_encoding_new_files():  # each new script file: balanced braces, CRLF only, no BOM
    ...

def test_simulated_outcome():      # multipliers parsed from the effect file, not hard-coded
    # engine: C += 0.08*M - 0.001*C + G, clamp 0..100, 365 daily steps from C0 = 60
    # G = 0.03 (Japan's bonuses) + cw*K + extra*K ; inland M=0.65 extra=-0.25 ; middle M=0.8 extra=-0.125 ; coast M=0.9 ; SE Asia M=1.0 (extra 0)
    assert 10 <= sim(K=0.38, inland) <= 20 and abs(sim(0.38, inland) - 14.4) < 0.5
    assert abs(sim(0.38, middle) - 32.6) < 0.5 and abs(sim(0.38, coast) - 49.6) < 0.5 and abs(sim(0.38, seasia) - 52.0) < 0.5
    assert sim(0.61, inland) == 0 and abs(sim(0.61, middle) - 9.8) < 0.5
    assert sim(0.0, inland) > 60   # no penalty at K=0: inland with M=0.65, G=0.03 rises from 60
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `python -I tools/jap_overreach/check.py`
Expected: FAIL on every test except `test_lists_match_history_tiers` (it reads only history and the constants), non-zero exit.

- [ ] **Step 3: Create the five mechanic files** to satisfy the Global Constraints and the Interfaces names.
  - The effect does the 3 set/multiply/clamp triples first, then the two guarded `every_state` blocks.
  - The on_actions file is `on_actions = { on_startup = { effect = { JAP = { JAP_update_overreach_compliance = yes } } } }`.
  - The dynamic modifier file also carries `enable` and `icon`, with no `remove_trigger`.

- [ ] **Step 4: Run the checker and confirm all Task 1 tests pass**

Run: `python -I tools/jap_overreach/check.py`
Expected: every listed test PASS, exit 0.

---

### Task 2: Rewire the 10 trigger sites

**Files:**
- Modify: `common/on_actions/00_on_actions.txt`. Compliance `add_to_variable` blocks at 4001-4004 (RAJ cap), 4056-4059 (INS cap), 4114-4117 (AST cap), 4946-4949 (RAJ uncap), 4988-4991 (INS uncap), 5034-5037 (AST uncap), 6337-6340 (Manila taken), 6402-6405 (Manila lost).
- Modify: `common/on_actions/08_hopping_on_actions.txt`. Compliance blocks at 151-154 (island lost) and 209-212 (island taken).
- Test: `tools/jap_overreach/check.py`

**Interfaces:**
- Consumes: `JAP_update_overreach_compliance` from Task 1.

- [ ] **Step 1: Add the site tests to the checker**

```python
def test_no_hand_written_compliance_deltas():   # nowhere under common/
    assert count(r"add_to_variable\s*=\s*\{\s*var\s*=\s*JAP_compliance_gain_modifier") == 0

def test_recompute_called_at_every_site():
    # for every `add_to_variable = { var = JAP_resistance_target_modifier ... }`, the innermost enclosing block
    # contains `JAP_update_overreach_compliance = yes` AFTER it
    assert sites("common/on_actions/00_on_actions.txt") == 8
    assert sites("common/on_actions/08_hopping_on_actions.txt") == 2
    assert all_sites_call_recompute()

def test_counter_lines_untouched():
    assert count(r"var\s*=\s*JAP_resistance_target_modifier", add_only=True) == 10
    assert count(r"var\s*=\s*MAN_resistance_target_modifier", add_only=True) == 20

def test_edited_files_intact():                 # balanced braces, every line still CRLF
    ...
```

- [ ] **Step 2: Run it and confirm the new tests fail**

Run: `python -I tools/jap_overreach/check.py`
Expected: `test_no_hand_written_compliance_deltas` and `test_recompute_called_at_every_site` FAIL; the rest PASS.

- [ ] **Step 3: At each of the 10 sites, replace the 4-line `add_to_variable = { var = JAP_compliance_gain_modifier value = … }` block with one line `JAP_update_overreach_compliance = yes` at the same indentation.** It stays inside the same `JAP = { }` block, after the counter change. Keep CRLF.

- [ ] **Step 4: Run the checker and confirm everything passes**

Run: `python -I tools/jap_overreach/check.py`
Expected: all tests PASS, exit 0.

- [ ] **Step 5: Confirm the diff is surgical**

Run: `git diff --numstat -- common/on_actions/00_on_actions.txt common/on_actions/08_hopping_on_actions.txt`
Expected: `8	32	common/on_actions/00_on_actions.txt` and `2	8	common/on_actions/08_hopping_on_actions.txt`. A whole-file count means line endings were rewritten; redo the edit.

---

### Task 3: In-game check (user runs; executor prepares the checklist)

**Files:** none

- [ ] **Step 1: Launch with `--debug`, load the current save, and play one day.** Run `grep -n -i "overreach\|overstretched" "C:/Users/adamg/Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log"`. Expected: no lines.
- [ ] **Step 2: Trigger a counter change**, e.g. take a USA_controls island or use the console to capitulate RAJ while at war with Japan. Then hover an occupied inland Chinese state (e.g. Sichuan 605) → Compliance. Expected: "Daily Compliance Gain" lines for Japan's −0.20·K and Overstretched Occupation −0.25·K (at K = 0.38 that's −0.076 and −0.095). A coastal state (e.g. Shandong 597) shows only the −0.20·K line.
