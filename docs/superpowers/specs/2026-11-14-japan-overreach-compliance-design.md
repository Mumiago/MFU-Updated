# Japan overreach compliance — design

## Intent
Japan builds compliance early, before its Asian conquests pile up. In the user's test game inland China reached about 60%. Once Japan has conquered "too much" of Asia, that compliance must collapse. Inland China must fall hardest: from about 60% to 10–20% within one year at today's conquest level (+38% on the existing counter). Penalties grow harsher beyond that.

## Goals
- Use the existing conquest counter `JAP_resistance_target_modifier` to scale a compliance penalty. The counter is bumped by RAJ/AST/INS capitulations, Manila and the 9 USA_controls states, maximum 0.61.
- Inland China harshest, middle China in between, coast and SE Asia milder but still worsening.
- Anchor: at counter 0.38, inland compliance goes from 60% to about 14% in one year (target band 10–20%).
- No extra penalty while the counter is 0, so early-game compliance still builds.

## Non-goals
- Conquering China does not feed the counter. China already has its own per-state resistance tiers. (My call: you picked option A, which is anchored to the existing counter.)
- The three known bugs stay as they are: Manchukuo never gets the country-wide compliance part; rollbacks can push the counter below 0; un-capitulation rollbacks have no winner check. The new derived values are clamped at ≤ 0, so a negative counter can't turn them into a bonus.
  - As a consequence of the first bug, Manchukuo- and RCC-held states get only the state part (inland −0.25·K, middle −0.125·K), not the country-wide −0.20·K.
- The resistance-target side is unchanged.

## Constraints (engine, decoded from hoi4.exe 1.19.5)
- Daily compliance change: dC = 0.08·M − 0.001·C + G.
  - M = 1 + Σ compliance_growth, not clamped.
  - G = flat sum of compliance_gain from the controller country, the state and the relation block.
- Steady state is C* = 1000·(0.08·M + G). After n days, C = C* + (C0 − C*)·0.999^n, so about 31% of the gap closes in a year.
- A state-scope compliance_gain counts no matter which country controls the state. Compliance only ticks where the controller is not a core owner.

## Approaches
1. **Country-wide only, about 4.5× the current steps.** Simplest, but every region collapses almost equally (inland 15 / middle 19 / coast 21 / SE Asia 24 after a year at +38), and everything reaches 0 at the max. Rejected: inland isn't distinctly harsher.
2. **Doubled country-wide penalty plus an inland-only state modifier. PICKED by the user.** Inland is clearly the harshest, coast and SE Asia stay playable, and each part has one tuning number.
3. Adding compliance_gain to the existing CHI_tougher_resistance* tier modifiers. Dropped: they are attached without Japan scope, so they can't read Japan's counter without per-state copies kept in sync across 131 focus swaps.

## Design
Let K = `JAP_resistance_target_modifier` (Japan's conquest counter).

- **Country-wide:** `JAP_compliance_gain_modifier` = min(0, −0.20·K). Today this is −0.1·K.
- **Inland states (full extra):** Japan variable `JAP_inland_overreach_compliance` = min(0, −0.25·K).
  - The 21 states in tiers 3–4: 603 Guizhou, 605 Sichuan, 747, 748, 750, 751, 752, 753, 283 Gansu, 287, 601 Xikang, 604 Qinghai, 616, 617 Xinjiang, 618, 619, 754, 755, 756, 759, 760.
- **Middle states (half extra):** Japan variable `JAP_middle_overreach_compliance` = min(0, −0.125·K).
  - The 9 tier-2 states: 325 Yunnan, 599 Guangxi, 600 Jiangxi, 602 Hunan, 620, 622, 744 Xi'an, 820, 821.
- **One state dynamic modifier**, `JAP_overstretched_occupation`, on all 30 states, with no `scope`.
  - Its compliance_gain reads the state's own variable `JAP_overreach_compliance_gain`. The recompute effect copies Japan's inland or middle value into it. This is the pattern `MFU_terrain_construction` already uses.
  - Its `enable` requires the state's controller to be JAP, in Japan's faction, or a Japanese puppet, so Manchukuo- and RCC-held states count too. (RCC is a puppet from game start but is never added to the faction.)
  - It is not `scope = JAP`: per the vanilla docs that would apply it only while JAP itself is the controller.
- **One recompute effect** (scripted effect) sets the three derived Japan variables from K and copies the state values. The 10 trigger sites call it after changing K, in place of their hand-written compliance `add_to_variable` lines: 8 in `00_on_actions.txt`, 2 in `08_hopping_on_actions.txt`. Tuning means editing one place.
- The same effect attaches the state modifier where it is missing. It also runs on_startup (new games) and monthly through `on_monthly_JAP`, so a running save picks the feature up within a month without waiting for K to change.
- Localisation: a name and a flavour-only description for the modifier (plain style, numbers come from the modifier lines).

### Expected result (one year from 60%; Japan holds its ~+0.03 compliance bonuses)
| Counter | Inland | Middle | Coast | SE Asia |
|---|---|---|---|---|
| 0.38 (today) | 14% | 33% | 50% | 52% |
| 0.61 (max) | 0 | 10% | 36% | 38% |

Coast and SE Asia keep falling after the first year (steady state at 0.38: about 26% / 34%).

## Settled during planning
- In a state-held dynamic modifier's `enable`, ROOT is the state (vanilla aat_dynamic_modifiers.txt comments say so). The check is `ROOT = { controller = { OR = { tag = JAP is_in_faction_with = JAP is_subject_of = JAP } } }`.
- Math: `set_variable` from K, `multiply_variable`, then `clamp_variable = { var = … max = 0 }`. State copies use `JAP.<var>`, as vanilla does with `RAJ.RAJ_agrarian_society_value`.
- All resistance-target and `MAN_resistance_target_modifier` lines stay untouched.

## Verification
- Static: brace balance; every trigger site calls the recompute effect; no hand-written compliance deltas remain; the loc file has a UTF-8 BOM.
- In game (a new game is not required): a console change of K does not run the effect. Trigger a counter event instead (a capitulation, Manila, or a USA_controls island), or run the effect from the console with `effect JAP JAP_update_overreach_compliance` (vanilla `documentation/console_commands_documentation.md`, section "## effect"). Then hover an occupied inland Chinese state's compliance. "Daily Compliance Gain" should show Japan's −0.20·K line plus the inland −0.25·K line.
