# Afrika Korps Mechanic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the cosmetic `GER_africa_korps` operation with an instant decision that spawns 3 medium (or 4 light) panzer divisions in the first Axis-held North African city and grants a self-balancing, decaying "Afrikakorps" spirit.

**Architecture:** A Python generator (`tools/afrika_korps/generate.py`) emits the repetitive game data (15 stepped spirits, 10 hidden desert techs, level-switch effects, template+spawn effects, localisation); a Python static checker (`tools/afrika_korps/check.py`) is the test suite. Hand-written scripted effects hold the logic (compute / sync / grant / weekly / freeze / monthly decay). The decision and the `GER_ussr_war_goal` decision call into them; one new on_actions file drives the weekly and monthly pulses.

**Tech Stack:** HOI4 1.19.x script (Clausewitz), Python 3 (stdlib only, run with `python -I`), repo tools pattern from `tools/terrain_build_speed/generate.py` and `tools/terrain_copies/sync.py`.

**Spec:** `docs/superpowers/specs/2026-11-12-afrika-korps-mechanic-design.md` (read it first; this plan only records implementation decisions). Reference screenshot: `docs/superpowers/specs/assets/afrika-korps-reference-template.png`.

## Global Constraints

- Mod root: `c:\Users\adamg\Documents\Paradox Interactive\Hearts of Iron IV\mod\MFU-Updated`. The working tree has many unrelated uncommitted changes (including `common/decisions/GER.txt`): edit surgically, never revert or reformat other lines, and **do not commit** (the user has not asked; if asked later, stage explicit paths only).
- Game install for reference docs: `C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV` (`documentation\*.md`).
- Spirit ids: `MFU_ak_spirit_0` .. `MFU_ak_spirit_14`; Soviet penalty of level N = `-0.0N` on both `attack_bonus_against` and `defense_bonus_against` with `tag = SOV` (level 0 has no targeted modifier). Display name "Afrikakorps".
- Desert techs: `MFU_ak_desert_1` .. `MFU_ak_desert_10`; level K = `desert = { attack = 0.0K }` and `deep_desert = { attack = 0.0K }` (K=10 is `0.10`). Both blocks identical so `python tools/terrain_copies/sync.py --check` stays clean. Each line battalion type must be covered by exactly one of the chosen unit categories (no stacking).
- Variables on GER: `MFU_ak_sov` (0..14), `MFU_ak_desert` (0..10), `MFU_ak_applied_sov`; GER flags `MFU_ak_active`, `MFU_ak_frozen`; recipient country flag `MFU_ak_recipient`; recipients also hold copies of `MFU_ak_sov` / `MFU_ak_desert` (used by tooltips).
- Africa level W (0..8) = the `GER_aatlantic_wall_W` idea held by ENG (start 4). Pre-Barbarossa `MFU_ak_sov = 14 - W` (W=0 -> 14, W=4 -> 10, W=8 -> 6). If ENG does not exist or holds none of the nine ideas, leave `MFU_ak_sov` unchanged.
- Barbarossa marker: `has_completed_focus = GER_ussr_war_goal` (GER scope). Decay: 1 point per month for both numbers once `MFU_ak_frozen` is set AND `date > 1942.1.2` (first tick 1.2.1942); spirit removed when both are 0.
- Decision `GER_africa_korps`: stays in the `operations` category, instant (`complete_effect`, no `days_remove`, no `remove_effect`), `fire_only_once = yes`, `cost = 25`, `ai_will_do = { factor = 10 }`, `allowed = { tag = GER }`. `available`: `has_war_with = ENG`, `country_exists = EFR`, `NOT = { has_completed_focus = GER_ussr_war_goal }`, `MFU_ak_any_city = yes`. `visible`: `has_war_with = ENG`, `ITA = { has_war_with = ENG }`, `NOT = { has_completed_focus = GER_ussr_war_goal }`.
- Recipients (snapshot at grant): `every_country` with `OR = { is_in_faction_with = GER tag = GER tag = EFR tag = SPR }`.
- City priority and spawn provinces: Tunis state 458 / province 11969 (only if `is_demilitarized_zone = no`), Tripoli 448 / 1149, Benghazi 450 / 11954, Tobruk 451 / 13741. A city is usable if its state is controlled by GER, an ally of GER (`is_controlled_by_ROOT_or_ally`, which covers an allied Vichy) or ITA; a Vichy-held city on its own does not count (changed after review).
- Division grid is 5 columns x 4 rows. Layout: tank columns x=0..2 rows y=0..2 (9 battalions); motorized columns x=3..4 rows y=0..2 (6); with Germany's `width_tech` also motorized `{x=3 y=3}` and `{x=4 y=3}` (total 17 = 30.35 width; without the tech 15 = 30.00). Medium template uses `medium_armor`, light uses `light_armor`; both use `motorized`. Support (x=0, y=0..7): artillery, recon_ac, mobile_engineer, anti_tank, maintenance_company, logistics_company_mot, anti_air_heavy_support, signal_company (drop and report any id invalid as divisional support). `division_names_group = GER_Arm_01`, `priority = 2`. Template names: "Afrikakorps Panzer-Division" (medium), "Afrikakorps leichte Panzer-Division" (light).
- Spawn: `create_unit` with `owner = GER`, `prioritize_location = <province>`, `start_experience_factor = 0.5`, `start_equipment_factor = 1`, `count = 3` (medium) / `count = 4` (light), inside the city's state scope. Medium chosen when `OR = { has_tech = ger_1939_medium_tank_chassis has_tech = ger_1940_medium_tank_chassis }`, else light. Variants via `force_equipment_variants` (owner "GER"): medium with `ger_1940_medium_tank_chassis` -> `medium_tank_chassis_1940` "Panzer III Ausf.H"; medium otherwise -> `medium_tank_chassis_1946` "Panzer IV"; light with `ger_1940_light_tank_chassis` -> `light_tank_chassis_1940` "Panzer 38(t)"; light otherwise -> `light_tank_chassis_1936` "Panzer II Ausf.a".
- Localisation: new uniquely named file `localisation/english/MFU_afrika_korps_l_english.yml` (UTF-8 with BOM, first line `l_english:`). Never edit `GER_afrikakorps_tt` (shared with the Italian focus).
- Not changed: `ITA_afrikakorps` focus, `fall_blau_get_summer_offensive`, `get_barb_offensive`, Tunisia demilitarisation logic, `ENG_africa_hopping_level_up/down`.

## Review Focus

Failure modes the spec implies; each gets a pinned test in the owning task.

1. ENG absent, or holds none of the nine wall ideas, at weekly time: `MFU_ak_sov` must stay unchanged and nothing may error (Task 2).
2. Africa level jumps by more than one step inside a week: the sync must clear all 15 levels before adding the exact one so two penalty spirits never stack (Task 1 + Task 2).
3. `MFU_ak_sov` reaches 0 while desert is still > 0: the `_0` shell spirit must stay; removal only when BOTH are 0 (Task 2).
4. Barbarossa declared while the decision was never pressed: freeze must only set the frozen flag, and the weekly pulse must stop; no spirit appears (Task 2).
5. Held city lost or Tunisia demilitarised: decision unavailable if no usable city remains; Tunis skipped when demilitarised (Task 3).

## File Structure

Create:
- `tools/afrika_korps/generate.py` - emits the five generated files below; constants at the top are the single source of values.
- `tools/afrika_korps/check.py` - static test suite (`python -I tools/afrika_korps/check.py` prints `PASS/FAIL <name>`, exits non-zero on any fail).
- Generated: `common/ideas/MFU_afrika_korps_ideas.txt`, `common/technologies/MFU_afrika_korps_hidden.txt`, `common/scripted_effects/MFU_afrika_korps_level_effects.txt`, `common/scripted_effects/MFU_afrika_korps_spawn_effects.txt`, `localisation/english/MFU_afrika_korps_l_english.yml`.
- Hand-written: `common/scripted_effects/MFU_afrika_korps_scripted_effects.txt`, `common/scripted_triggers/MFU_afrika_korps_scripted_triggers.txt`, `common/on_actions/MFU_afrika_korps_on_actions.txt`.

Modify:
- `common/decisions/GER.txt` - the `GER_africa_korps` entry in the `operations` block (~4705-4779) and the `complete_effect` of `GER_ussr_war_goal` (~587).
- `common/ideas/germany.txt` - remove `GER_afrika_campaign` and `GER_afrika_campaign2` (~1006-1098); keep everything else including the hidden `GER_africa_mastery_gain_bonus_spirit`.
- `localisation/english/focus_l_english.yml` (868-869, decision text), `localisation/english/ideas_l_english.yml` (93-94, old idea keys), `localisation/english/tooltips_l_english.yml` (183 and 2514 only).

---

### Task 1: Checker, generator and generated data

**Files:**
- Create: `tools/afrika_korps/check.py`, `tools/afrika_korps/generate.py` and the five generated files listed above.

**Interfaces:**
- Produces effects (country scope, no parameters): `MFU_ak_set_sov_idea = yes` (reads `MFU_ak_sov`, removes all 15 spirits then adds `MFU_ak_spirit_<MFU_ak_sov>`), `MFU_ak_set_desert_tech = yes` (reads `MFU_ak_desert`, sets all 10 techs to 0 then `MFU_ak_desert_<n>` to 1 when n > 0, `popup = no`), `MFU_ak_clear_spirit = yes` (removes all 15 spirits and zeroes all 10 techs), `MFU_ak_create_template = yes` and `MFU_ak_spawn_divisions = yes` (GER scope; spawn picks the first usable city in priority order and calls the matching branch).
- Consumes triggers from Task 3's trigger file: `MFU_ak_city_tunis`, `MFU_ak_city_tripoli`, `MFU_ak_city_benghazi`, `MFU_ak_city_tobruk`, `MFU_ak_has_medium_tech`, `MFU_ak_has_medium_1940`, `MFU_ak_has_light_1940`, `MFU_ak_has_width_tech` (names fixed here; Task 3 defines them). The generator may emit them inline only if it cannot be avoided; prefer using the named triggers.
- Loc keys produced: `MFU_ak_spirit_<N>` and `MFU_ak_spirit_<N>_desc` for N=0..14, `MFU_ak_desert_<K>` for K=1..10, `MFU_ak_desert_tt` (`"Attack in desert and deep desert: +[?MFU_ak_desert|Y0]%"`-style, using the variable-in-tooltip form at `localisation/english/ideas_l_english.yml:10`), `MFU_ak_decay_tt`, `MFU_ak_effect_tt` (decision effect summary), `MFU_ak_spawn_tt`.

- [ ] **Step 1: Write `tools/afrika_korps/check.py` with these test functions, each reading the files from disk and asserting the Global Constraints values** (use `re` plus a small brace-matching helper; no third-party imports):
  - `test_spirit_ideas`: ids 0..14 exist in `MFU_afrika_korps_ideas.txt` inside `country = {`; level N>0 has exactly one `targeted_modifier` with `tag = SOV` and `attack_bonus_against = -0.0N` / `defense_bonus_against = -0.0N` (N=14 -> `-0.14`); level 0 has none; every level has `removal_cost = -1`, `allowed = { always = no }`, `custom_modifier_tooltip = MFU_ak_desert_tt`, and no other stat modifier.
  - `test_desert_techs`: ids 1..10 exist; each has `desert` and `deep_desert` blocks with the same `attack` value under every category in generate.py's `DESERT_CATEGORIES`; `research_cost = -1`, `allow = { always = no }`.
  - `test_level_effects`: `MFU_ak_set_sov_idea` has 15 `check_variable` branches referencing the matching ids and removes all 15 ids before any `add_ideas`; `MFU_ak_set_desert_tech` references all 10 techs; `MFU_ak_clear_spirit` removes all 15 and zeroes all 10.
  - `test_spawn_effects`: exactly 4 `division_template =` blocks (2 types x width/no-width) with the layout from Global Constraints (count regiments: 15 or 17; support 8); every `create_unit` has `start_equipment_factor = 1`, `owner = GER`, a `prioritize_location` from {11969, 1149, 11954, 13741}, `count = 3` for medium or `count = 4` for light; 16 `create_unit` blocks (4 cities x 4 variants); the four variant names/chassis ids from Global Constraints appear.
  - `test_loc`: file starts with BOM + `l_english:`; every idea id, `_desc`, tech id and tooltip key referenced by any generated file or by `common/decisions/GER.txt`'s `MFU_ak_*` tooltips exists.
  - `test_braces`: every generated and hand-written MFU_ak file has balanced braces.
  - `test_sync_clean`: `python -I tools/terrain_copies/sync.py --check` exits 0 and reports no missing twins for the new tech file.
- [ ] **Step 2: Run `python -I tools/afrika_korps/check.py`; expected: every test FAIL (files missing).**
- [ ] **Step 3: Implement `tools/afrika_korps/generate.py`** (constants first: `SOV_LEVELS = range(0, 15)`, `DESERT_LEVELS = range(1, 11)`, `CITIES = [("tunis", 458, 11969), ("tripoli", 448, 1149), ("benghazi", 450, 11954), ("tobruk", 451, 13741)]`, `DESERT_CATEGORIES`, `TEMPLATE_LAYOUT`, `VARIANTS`). Write each file as UTF-8 (loc with BOM), tabs for indentation, header comment `# Generated by tools/afrika_korps/generate.py - edit the tables there and re-run.`. Pick `DESERT_CATEGORIES` by reading the `categories = { ... }` of the line-battalion definitions in `common/units/*.txt` (infantry, motorized, mechanized, light/medium/heavy armor, artillery brigades, armored car, etc.) so each is covered exactly once; record the chosen list and the reasoning in a comment above the constant. Idea fields: `name`/loc id per level, `picture = GFX_idea_GER_afrika_campaign`, `allowed = { always = no }`, `removal_cost = -1`, `modifier = { custom_modifier_tooltip = MFU_ak_desert_tt custom_modifier_tooltip = MFU_ak_decay_tt }`, targeted modifier per Global Constraints. Take the structure of a stepped targeted idea from `GER_barb_offensive_buff_9` (`common/ideas/germany.txt` ~2230-2269).
- [ ] **Step 4: Run `python -I tools/afrika_korps/generate.py` then `python -I tools/afrika_korps/check.py`; expected: all Task 1 tests PASS (none of them needs Task 3's triggers or the decision; the generated spawn effect only references trigger names, which resolve once Task 3 lands).**

---

### Task 2: Runtime scripted effects and pulses

**Files:**
- Create: `common/scripted_effects/MFU_afrika_korps_scripted_effects.txt`, `common/on_actions/MFU_afrika_korps_on_actions.txt`
- Modify: `common/decisions/GER.txt` (`GER_ussr_war_goal` `complete_effect`, add one line as the FIRST statement inside the leading `hidden_effect` of `complete_effect`, so it stays out of the tooltip: `MFU_ak_freeze = yes`)
- Test: extend `tools/afrika_korps/check.py`

**Interfaces:**
- Consumes: Task 1's `MFU_ak_set_sov_idea`, `MFU_ak_set_desert_tech`, `MFU_ak_clear_spirit`.
- Produces (all GER scope, no parameters): `MFU_ak_compute_sov = yes`; `MFU_ak_sync = yes` (copies `MFU_ak_sov`/`MFU_ak_desert` from GER to every country flagged `MFU_ak_recipient`, runs the two set effects on each, stores `MFU_ak_applied_sov`); `MFU_ak_grant = yes` (flag recipients, set `MFU_ak_desert = 10`, `MFU_ak_active`, compute, sync); `MFU_ak_weekly = yes`; `MFU_ak_freeze = yes`; `MFU_ak_monthly = yes`; `MFU_ak_end = yes`.

- [ ] **Step 1: Add failing checker tests:**
  - `test_compute_sov_guarded`: `MFU_ak_compute_sov` contains the nine-branch mapping `GER_aatlantic_wall_0 -> 14` ... `GER_aatlantic_wall_8 -> 6` read through `ENG = { has_idea = ... }` and has no `else` branch that assigns a value (so it leaves the variable unchanged when ENG is absent).
  - `test_weekly_stops_after_barbarossa`: `MFU_ak_weekly` is guarded by `NOT = { has_completed_focus = GER_ussr_war_goal }` and `NOT = { has_country_flag = MFU_ak_frozen }`, and calls `MFU_ak_sync` only when `MFU_ak_active` is set and `MFU_ak_sov` differs from `MFU_ak_applied_sov`.
  - `test_freeze_without_spirit`: `MFU_ak_freeze` calls `MFU_ak_compute_sov`, sets `MFU_ak_frozen`, and calls `MFU_ak_sync` only inside an `MFU_ak_active` guard.
  - `test_monthly_end_condition`: `MFU_ak_monthly` requires `MFU_ak_active`, `MFU_ak_frozen` and `date > 1942.1.2`, decrements each variable only while > 0, and calls `MFU_ak_end` only when BOTH are 0 (an `AND`).
  - `test_barbarossa_hook_first`: in `common/decisions/GER.txt`, the `GER_ussr_war_goal` `complete_effect` has `MFU_ak_freeze = yes` before `complete_national_focus`/`get_barb_offensive`.
  - `test_on_actions`: the on_actions file defines `on_weekly_GER` calling `MFU_ak_weekly = yes` and `on_monthly_GER` calling `MFU_ak_monthly = yes`.
- [ ] **Step 2: Run the checker; expected: the six new tests FAIL.**
- [ ] **Step 3: Implement the effects.** `MFU_ak_end` calls `MFU_ak_clear_spirit` on every recipient, clears `MFU_ak_recipient`, and clears GER's `MFU_ak_active`/`MFU_ak_frozen` and variables. Variable copy to recipients uses the scoped-variable form (`value = GER.MFU_ak_sov` style); confirm the exact `set_variable` syntax against a precedent in `common/scripted_effects/` or `documentation/effects_documentation.md` before writing it.
- [ ] **Step 4: Implement the on_actions file** with exactly the two blocks (`on_actions = { on_weekly_GER = { effect = { MFU_ak_weekly = yes } } on_monthly_GER = { effect = { MFU_ak_monthly = yes } } }`) — repeated on_action keys across files merge (`common/on_actions/00_MAN_on_actions.txt` does this).
- [ ] **Step 5: Add `MFU_ak_freeze = yes` as the first line of the `GER_ussr_war_goal` `complete_effect` (GER.txt ~587), touching nothing else.**
- [ ] **Step 6: Run the checker; expected: all Task 1 and Task 2 tests PASS.**

---

### Task 3: Decision, triggers and spawn wiring

**Files:**
- Create: `common/scripted_triggers/MFU_afrika_korps_scripted_triggers.txt`
- Modify: `common/decisions/GER.txt` (replace the `GER_africa_korps` entry in the `operations` block, ~4706-4779), `localisation/english/focus_l_english.yml` (868-869), `localisation/english/MFU_afrika_korps_l_english.yml` via generate.py (add any decision-specific keys there, not by hand)
- Test: extend `tools/afrika_korps/check.py`

**Interfaces:**
- Produces triggers (country scope, GER): `MFU_ak_city_tunis`, `MFU_ak_city_tripoli`, `MFU_ak_city_benghazi`, `MFU_ak_city_tobruk` (each: the city's state is controlled by GER, an ally of GER, ITA or EFR; Tunis additionally `is_demilitarized_zone = no`), `MFU_ak_any_city` (OR of the four), `MFU_ak_has_medium_tech` (`OR = { has_tech = ger_1939_medium_tank_chassis has_tech = ger_1940_medium_tank_chassis }`), `MFU_ak_has_medium_1940` (`has_tech = ger_1940_medium_tank_chassis`), `MFU_ak_has_light_1940` (`has_tech = ger_1940_light_tank_chassis`), `MFU_ak_has_width_tech` (`has_tech = width_tech`).
- Consumes: Task 1 `MFU_ak_spawn_divisions`, Task 2 `MFU_ak_grant`.

- [ ] **Step 1: Add failing checker tests:**
  - `test_decision_shape`: the `GER_africa_korps` entry has `complete_effect`, `fire_only_once = yes`, `cost = 25`, `ai_will_do = { factor = 10 }`, and NO `days_remove` / `remove_effect`; `available` and `visible` match the Global Constraints (including both `NOT = { has_completed_focus = GER_ussr_war_goal }`).
  - `test_decision_effect`: `complete_effect` calls `MFU_ak_grant = yes` and `MFU_ak_spawn_divisions = yes` and shows `custom_effect_tooltip = MFU_ak_effect_tt`; it does NOT reference `GER_afrika_campaign`, `GER_afrikakorps_tt` or `germany.233`.
  - `test_triggers`: the trigger file defines all nine trigger names; the Tunis trigger contains `is_demilitarized_zone = no` and state 458; the other three reference states 448, 450, 451 and none of them contains `is_demilitarized_zone`.
- [ ] **Step 2: Run the checker; expected: the three new tests FAIL.**
- [ ] **Step 3: Implement the trigger file** (state-scope controller test written once per city; use `is_controlled_by_ROOT_or_ally = yes` as in `common/ideas/germany.txt` 1024-1026, plus `is_controlled_by = ITA` and `is_controlled_by = EFR`).
- [ ] **Step 4: Replace the `GER_africa_korps` entry in GER.txt in place (same position, same indentation style, keep the surrounding `GER_operation_oak` entry untouched).** `complete_effect` order: recipients snapshot is done inside `MFU_ak_grant`, so call `MFU_ak_grant = yes` first, then `MFU_ak_spawn_divisions = yes`, then `custom_effect_tooltip = MFU_ak_effect_tt`.
- [ ] **Step 5: Rewrite the decision text in `focus_l_english.yml:868-869`** (title "Afrikakorps"; description: instant deployment of panzer divisions to the African front plus the temporary spirit; keep the existing `GER_africa_korps` / `GER_africa_korps_desc` keys). Add the matching `MFU_ak_effect_tt` / `MFU_ak_spawn_tt` text through generate.py (`§Y`/`§G`/`§R` colour codes as in `tooltips_l_english.yml:2514`) and regenerate.
- [ ] **Step 6: Run `python -I tools/afrika_korps/generate.py` and the checker; expected: all PASS.**

---

### Task 4: Remove the old spirit

**Files:**
- Modify: `common/ideas/germany.txt` (delete `GER_afrika_campaign` and `GER_afrika_campaign2`, the block between the "Blitz Strategic bonus / Drang nach Osten" comments and `GER_atlantic_wall_00`, ~1006-1098), `localisation/english/ideas_l_english.yml` (93-94), `localisation/english/tooltips_l_english.yml` (lines 183 and 2514 only: `GER_afrika_spirit_dissappears_tt`, `GER_africa_mastery_gain_bonus_tt`)
- Test: extend `tools/afrika_korps/check.py`

- [ ] **Step 1: Add failing test `test_old_spirit_gone`:** no occurrence of `GER_afrika_campaign`, `GER_afrika_spirit_dissappears_tt` or `GER_africa_mastery_gain_bonus_tt` in `common/` or `localisation/`; `GER_afrikakorps_tt` still present in `tooltips_l_english.yml` and still referenced by `common/national_focus/italy.txt`; `GER_atlantic_wall_00` still defined in `common/ideas/germany.txt`; `GER_africa_mastery_gain_bonus_spirit` (hidden idea) still defined.
- [ ] **Step 2: Run the checker; expected: `test_old_spirit_gone` FAILS.**
- [ ] **Step 3: Delete the two ideas and the three loc entries** (leave `GFX_idea_GER_afrika_campaign`, still used by the ENG ideas and the new spirits). Before editing, `git diff --stat -- common/ideas/germany.txt localisation/english/ideas_l_english.yml localisation/english/tooltips_l_english.yml` to know which of these already carry the user's uncommitted edits, and afterwards confirm the diff only adds the intended deletions.
- [ ] **Step 4: Run the checker; expected: all PASS.**

---

### Task 5: Whole-change verification and hand-off checklist

**Files:**
- Create: `docs/superpowers/plans/2026-11-12-afrika-korps-ingame-checklist.md`

- [ ] **Step 1: Run `python -I tools/afrika_korps/generate.py` twice and confirm the second run changes nothing (hash the five generated files with `sha256sum` before and after), then `python -I tools/afrika_korps/check.py` (all PASS) and `python -I tools/terrain_copies/sync.py --check` (clean).**
- [ ] **Step 2: Confirm scope:** `git status --short` lists only the files named in this plan (plus the user's pre-existing modifications); `git diff -- common/decisions/GER.txt` shows only the replaced `GER_africa_korps` entry and the one added line in `GER_ussr_war_goal`.
- [ ] **Step 3: Write the in-game checklist file** (the implementer cannot run the game). Items: launch and read `C:\Users\adamg\Documents\Paradox Interactive\Hearts of Iron IV\logs\error.log` for `MFU_ak`, `africa_korps`, `afrika` (expected: none); then in a game as Germany use the console (`tag GER`, `effect <script>`; `var MFU_ak_sov`) to confirm: (a) decision visible only at war with ENG and available only with a usable city; (b) pressing it spawns 3 medium or 4 light divisions in the highest-priority held city, fully equipped, and Germany's tank stockpile is unchanged (compare before/after); (c) a Tunisia that is still demilitarised falls through to Tripoli; (d) the spirit shows desert +10% and the Soviet penalty `14 - W`, and the penalty changes within a week when the Africa level changes (e.g. `effect ENG_africa_hopping_level_down = yes`); (e) after Barbarossa is declared (press the real decision after 1941-06-22, or for a quick test `effect complete_national_focus = GER_ussr_war_goal` then `effect MFU_ak_freeze = yes`) the decision disappears, tracking stops, and the monthly decay drops both numbers by 1 and removes the spirit at 0; (f) desert terrain attack appears in the division designer/combat for the new divisions; (g) the width-tech branch (needs sub-doctrine `large_front_operations` active) produces 17 battalions at 30.35 width.
- [ ] **Step 4: Report to the user: what was built, what could only be statically verified, and the checklist path.**
