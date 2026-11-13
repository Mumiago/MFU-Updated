# Afrika Korps - in-game checklist

Everything below needs the game; the static suite (`python -I tools/afrika_korps/check.py`, 24 tests) already passes.
Restart the game so the new ideas, technologies, scripted effects and on_actions load. A new game is recommended: in a save where the old Afrikakorps decision was already taken, the old spirit is gone and the
new decision cannot be pressed again. In any other existing save it works (the weekly
pulse starts on its own); a new game is the cleanest.

## 0. Load errors
After launching, search `C:\Users\adamg\Documents\Paradox Interactive\Hearts of Iron IV\logs\error.log` for
`MFU_ak`, `africa_korps`, `afrika`, `MFU_afrika_korps`. Expected: no lines. Any hit is a script error to send back.

## Console cheat sheet
`tag GER` (play Germany), `effect <script>` runs a script on the current country, `var MFU_ak_sov` / `var MFU_ak_desert` show
GER's variables. Useful effects: `effect MFU_ak_compute_sov = yes`, `effect MFU_ak_sync = yes`,
`effect ENG_africa_hopping_level_down = yes` (moves the Africa level one step towards "Axis winning": penalty +1),
`effect ENG_africa_hopping_level_up = yes` (penalty -1).

## 1. Decision gating
- [ ] Decision "Afrikakorps" (operations category) is visible only while Germany and Italy are at war with Britain, and
      not after Barbarossa.
- [ ] It is unavailable until France has fallen (Vichy exists) AND the Axis holds Tripoli, Benghazi, Tobruk, or a
      non-demilitarized Tunis. Check the greyed-out tooltip, then give/lose a city.
- [ ] With Tunisia still demilitarized and held by an Axis member, Tunis does not count by itself.
- [ ] A Vichy-held Tunisia (not allied, flag cleared by Free France's `FRA_refus_absurde`) does not count either: with Italy
      holding Tripoli the divisions appear in Tripoli, and with no other city the decision stays unavailable.

## 2. Pressing it
- [ ] It fires instantly (no 30-day timer) and costs 25 political power; it cannot be pressed twice.
- [ ] 3 divisions (medium) or 4 (light, when Germany has neither `ger_1939_medium_tank_chassis` nor
      `ger_1940_medium_tank_chassis`) appear in the highest-priority held city: Tunis, else Tripoli, else Benghazi, else Tobruk.
- [ ] **Germany's tank stockpile is unchanged** (compare the equipment screen before/after). The divisions are 100% equipped.
- [ ] A German-owned division can appear in a province controlled by Italy or Vichy (if not, note where they landed and tell me).
- [ ] Template looks like the reference screenshot: 3x3 tanks + 2x3 motorized = 30.00 width; with the Mass Assault width tech
      (activate sub-doctrine `large_front_operations`) it is 3x3 tanks + 2x4 motorized = 30.35. Eight support companies.
- [ ] Variant names resolve (Panzer III Ausf.H / Panzer IV / Panzer 38(t) / Panzer II Ausf.a); divisions are not "obsolete" shells.

## 3. The spirit before Barbarossa
- [ ] A national spirit "Afrikakorps" shows for Germany and every faction member, Vichy and Spain (Finland and Italy included).
- [ ] The spirit icon is the old Africa-campaign art, NOT the question mark (`picture = GER_afrika_campaign`, no `GFX_idea_` prefix).
- [ ] It shows "+10%" desert/deep-desert attack and a Soviet attack/defence penalty of `14 - W` points: -10% at the neutral
      Africa level, -14% if the Axis hold every checkpoint, -6% if the Axis lost them all.
- [ ] Run `effect ENG_africa_hopping_level_down = yes`, wait up to a week: the spirit's Soviet penalty goes up by one point
      (the swap is weekly, so a short delay is expected). Check `var MFU_ak_sov`.
- [ ] Press the decision right after changing the level: the penalty is already correct (the press recomputes it).
- [ ] The +10% desert attack shows up for the new divisions (division designer terrain adjuster or an actual desert fight)
      and is not diluted by support companies.

## 4. Barbarossa and decay
- [ ] Declaring Barbarossa (decision available after 1941-06-22, or `effect complete_national_focus = GER_ussr_war_goal`
      then `effect MFU_ak_freeze = yes` for a quick test) freezes the penalty; later Africa changes no longer move it.
- [ ] If the Afrikakorps decision was never pressed, nothing appears at Barbarossa and the decision is gone.
- [ ] After Barbarossa both numbers stay fixed until 1.1.1942; a monthly tick before that changes nothing.
- [ ] From 1.2.1942 both numbers drop by 1 each month. `effect MFU_ak_monthly = yes` only steps them once the date is
      past 1942.1.2 (before that it is a no-op by design; to test early, temporarily lower the date in `MFU_ak_monthly`).
      The spirit disappears when BOTH are 0 (the penalty can reach 0 first; the spirit stays until the desert bonus is also 0).
- [ ] After removal: `var MFU_ak_sov` / `MFU_ak_desert` are cleared and no `MFU_ak_desert_*` technology remains.

## 5. Known limits (accepted in the design)
- Countries that join the Germany faction after the press do not get the spirit.
- Finland, Italy and Vichy take the Soviet penalty without the matching Barbarossa buff (design decision).
- The 1942 summer-offensive decisions still read the live Africa level; by then the penalty has decayed about 4-5 points.
- A later doctrine switch resets `width_tech`; already-created divisions keep their 17-battalion layout.
