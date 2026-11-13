# Italy African BoP Losses Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Italy loses a reversible, focus-softened 20% Balance of Power per lost African state; the German factory output the Italian focuses gave moves to Germany's plunder levels and Speer; the Grand Council total-control collapse is removed.

**Architecture:** Per-state flag `ITA_africa_bop_lost` plus rate tiers as ITA country flags; all logic in new MFU_ files driven by `on_state_control_changed`. The old ±5% blocks in 00_on_actions.txt are deleted. Focus hooks call scripted effects. German and collapse changes are plain data edits.

**Tech Stack:** HOI4 1.19 script (Clausewitz), Python 3 static checker (stdlib only, run with `python -I`).

**Spec:** `docs/superpowers/specs/2026-11-13-ita-africa-bop-design.md`

## Global Constraints
- All mod files are CRLF; loc files UTF-8 with BOM; edit as bytes, build `\n` in loc with `chr(92)+'n'`.
- States in the rule: exactly 458, 448, 449, 450, 451.
- Rates: base 0.20, tier_1 0.15, tier_2 0.10, off 0.
- Short tooltips (user dislikes blocks of text). Minimal/no code comments.
- No git commits unless the user asks.

## Review Focus
- Tunisia first taken from France/Vichy by Italy: no BoP change (no lost flag yet).
- State passes between two Axis members (ITA -> GER) while not lost: nothing; while lost: refund once, flag cleared.
- State passes between two Allied members while lost: nothing (no double loss).
- Focus completed while states are lost: refund 0.05 per lost state (Viva: the full remaining rate), later retakes refund the new rate.
- Italy without an active power balance when a state is lost: no flag set, so a later retake refunds nothing.

---

### Task 1: Static checker

**Files:**
- Create: `tools/ita_africa_bop/check.py`

- [ ] **Step 1: Write checks** (each a function `test_*`, runner prints PASS/FAIL per test and exits 1 on any failure):
  - `test_old_blocks_removed`: `common/on_actions/00_on_actions.txt` contains no `id = ITA_power_balance`.
  - `test_state_list`: `ITA_africa_bop_state` in `common/scripted_triggers/MFU_ITA_africa_bop_triggers.txt` lists exactly {458, 448, 449, 450, 451}.
  - `test_effects_defined`: `ITA_africa_bop_apply_loss`, `ITA_africa_bop_apply_refund`, `ITA_africa_bop_step_down`, `ITA_africa_bop_end` defined in `common/scripted_effects/MFU_ITA_africa_bop_effects.txt`; values -0.2/-0.15/-0.1 and 0.2/0.15/0.1 present.
  - `test_on_action`: `common/on_actions/MFU_ITA_africa_bop_on_actions.txt` has `on_state_control_changed`, sets and clears `ITA_africa_bop_lost`, calls apply_loss and apply_refund, checks `has_power_balance`.
  - `test_focus_hooks`: Bend and Castello completion_reward contain `ITA_africa_bop_step_down = yes` and `ITA_africa_bop_tier_1_tt`; Victory contains step_down and `ITA_africa_bop_tier_2_tt`; Viva il Duce contains `ITA_africa_bop_end = yes` and `ITA_africa_bop_off_tt`.
  - `test_flat_bop`: live (uncommented) `ITA_bop_low_increase_effect` count: Bend 0, Castello 1, Victory 1.
  - `test_no_german_output_in_ita`: no `GER_arbeitseinsatz_industrial_capacity_factory` and no `GER_elalamein_tt` in the three Italian focuses.
  - `test_plunder_levels`: `GER_economy_of_plunder_1..6` `industrial_capacity_factory` = 0.06, 0.11, 0.17, 0.23, 0.28, 0.34.
  - `test_speer`: `GERminister_of_armament_and_war_production` `industrial_capacity_factory = 0.30`.
  - `test_no_collapse`: `ITA_grand_council_total_control_range` on_activate has no live `remove_power_balance`, `add_war_support`, `add_stability`.
  - `test_loc`: keys `ITA_africa_bop_tier_1_tt`, `_tier_2_tt`, `_off_tt` exist exactly once in localisation/english, file has BOM and `l_english:` header.
  - `test_braces`: every touched file has balanced braces, never negative.
- [ ] **Step 2: Run** `python -I tools/ita_africa_bop/check.py` — Expected: most FAIL (nothing built yet), `test_braces` PASS.

### Task 2: BoP mechanic

**Files:**
- Create: `common/scripted_triggers/MFU_ITA_africa_bop_triggers.txt`, `common/scripted_effects/MFU_ITA_africa_bop_effects.txt`, `common/on_actions/MFU_ITA_africa_bop_on_actions.txt`
- Modify: `common/on_actions/00_on_actions.txt` (delete the two `if` blocks whose body is `ITA = { add_power_balance_value = { id = ITA_power_balance value = ±0.05 } }`, ~5633-5710)

**Interfaces (Produces):**
- Triggers: `ITA_africa_bop_state` (state scope; state = 458/448/449/450/451), `ITA_africa_bop_axis_country` (country scope; tag ITA, is_subject_of ITA, is_in_faction_with ITA, tag GER, is_in_faction_with GER), `ITA_africa_bop_allied_country` (country scope; tag ENG, is_in_faction_with ENG).
- Effects (ITA country scope): `ITA_africa_bop_apply_loss` / `ITA_africa_bop_apply_refund` (add -/+ current rate: off 0, tier_2 0.10, tier_1 0.15, else 0.20), `ITA_africa_bop_step_down` (if no tier_1: set it, else if no tier_2: set it; when a tier was set, +0.05 per state with `ITA_africa_bop_lost`; all hidden), `ITA_africa_bop_end` (+current rate per lost state, then set `ITA_africa_bop_off`; hidden).
- Flags: country `ITA_africa_bop_tier_1`, `ITA_africa_bop_tier_2`, `ITA_africa_bop_off`; state `ITA_africa_bop_lost`.

- [ ] **Step 1:** Write the triggers and effects.
- [ ] **Step 2:** On action: loss branch = FROM.FROM is a rule state without the lost flag, ROOT allied, FROM axis, `country_exists = ITA`, ITA has_power_balance → set flag on FROM.FROM, ITA apply_loss. Else-if retake branch = FROM.FROM has the lost flag and ROOT axis → clear flag, ITA apply_refund.
- [ ] **Step 3:** Delete the two old blocks (anchor on their bodies; assert the remaining file is brace-balanced).
- [ ] **Step 4:** Run checker — `test_old_blocks_removed`, `test_state_list`, `test_effects_defined`, `test_on_action`, `test_braces` PASS.

### Task 3: Focus hooks and German removal in the Italian focuses

**Files:**
- Modify: `common/national_focus/italy.txt` (Bend 2728-7114, Castello 7116-11485, Victory 11564-16685, Viva il Duce ~16991)
- Create: `localisation/english/MFU_ITA_africa_bop_l_english.yml`

**Interfaces (Consumes):** `ITA_africa_bop_step_down`, `ITA_africa_bop_end` from Task 2.

- [ ] **Step 1:** In Bend, Castello, Victory delete the `GER = { custom_effect_tooltip = GER_elalamein_tt add_to_variable = { GER_arbeitseinsatz_industrial_capacity_factory = 0.05 } }` block and add `custom_effect_tooltip = <tier key>` + `ITA_africa_bop_step_down = yes` in its place. Viva il Duce: add `custom_effect_tooltip = ITA_africa_bop_off_tt` + `ITA_africa_bop_end = yes`.
- [ ] **Step 2:** Loc (exact copy):
  - `ITA_africa_bop_tier_1_tt`: "Losing §YTunisia§!, §YTripoli§!, §YEl Agheila§!, §YBenghasi§! or §YTobruk§! now costs §Y15%§! Balance of Power instead of §Y20%§!.\nStates already lost give back §G5%§! each."
  - `ITA_africa_bop_tier_2_tt`: same with §Y10%§! instead of §Y15%§!.
  - `ITA_africa_bop_off_tt`: "Losing §YTunisia§!, §YTripoli§!, §YEl Agheila§!, §YBenghasi§! or §YTobruk§! no longer costs Balance of Power.\nStates already lost give back their remaining cost."
- [ ] **Step 3:** Run checker — `test_focus_hooks`, `test_flat_bop`, `test_no_german_output_in_ita`, `test_loc` PASS.

### Task 4: German output and Grand Council collapse

**Files:**
- Modify: `common/ideas/germany.txt` (GER_economy_of_plunder_1..6), `common/country_leader/00_traits.txt:2972`, `common/bop/ITA.txt:104-106`

- [ ] **Step 1:** Plunder `industrial_capacity_factory` 0.04/0.08/0.12/0.16/0.2/0.24 → 0.06/0.11/0.17/0.23/0.28/0.34 (efficiency gain untouched). Speer trait 0.20 → 0.30. Delete the three live lines in the total-control on_activate (`remove_power_balance`, `add_war_support = -1`, `add_stability =-1`); keep the range, its modifier and the commented block.
- [ ] **Step 2:** Run checker — all PASS.

### Task 5: Independent review
- [ ] Run a read-only review workflow over the diff (rule semantics vs spec incl. Review Focus cases, engine scopes in on_state_control_changed, tooltip text vs code, regressions in 00_on_actions.txt). Fix confirmed findings, rerun checker.
