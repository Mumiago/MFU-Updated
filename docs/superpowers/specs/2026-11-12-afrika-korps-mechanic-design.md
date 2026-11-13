# Afrika Korps decision overhaul - design

Status: draft for approval. Date: 2026-11-12. Mod: MFU-Updated (HOI4 1.19.x).
Reference screenshot of the intended division: `assets/afrika-korps-reference-template.png`.

## Intent

The German operation `GER_africa_korps` (`common/decisions/GER.txt`, `operations` block, ~line 4706) is today a
cosmetic decision: it adds the `GER_afrika_campaign` spirit (+120% army HP, -20% heat attrition, +20% air defence,
+10% armour reliability) and spawns nothing. The tooltip claims a Panzer III/IV gift and Tunis infantry, but those
come from the *Italian* focus `ITA_afrikakorps` (`common/national_focus/italy.txt`, 1942+), which this design does not touch.

Turn it into a real mechanic: Germany presses it after France falls and Axis holds a Tunisian/Libyan foothold; it
spawns fully equipped panzer divisions there and gives the Axis a temporary spirit that helps in the desert but taxes
the Axis against the Soviet Union, cancelling out the existing "North African Campaign" Barbarossa bonus swing.

## Goals

1. Decision is available only after the fall of France and only while the Axis controls one of Tunis, Tripoli,
   Benghazi, Tobruk.
2. On completion it spawns **3 fully equipped 30-width medium-tank divisions** (or **4 light-tank divisions** if
   Germany has neither the 1939 nor the 1940 medium tank tech), in the highest-priority held city (Tunis > Tripoli >
   Benghazi > Tobruk).
3. A replacement spirit, "Afrikakorps", grants **+10% attack in desert and deep_desert** and **-N% attack and
   defence vs the Soviet Union**, where N cancels the Africa swing (below), then, once Barbarossa has begun and it is past 1.1.1942,
   both decay 1 point per month (first tick 1.2.1942) until 0, at which point the spirit is removed.

## Non-goals

- No change to the Italian focus `ITA_afrikakorps`, to `fall_blau_get_summer_offensive`, or to the Tunisia
  demilitarised-zone logic.
- No desert bonus on `desert_hills` (it is a copy of `hills` in this mod).
- No stockpile gift of tanks.
- Countries that join the Germany faction after the grant do not receive the spirit (same one-shot snapshot as today).

## Anti-goals (would make it a failure even if it "works")

- The spirit must carry none of the old modifiers (HP, heat attrition, air defence, reliability bonus).
- Spawning must not consume Germany's tank stockpile (user requirement: "fully equipped divisions spawned, not tank
  stockpiles").
- No raw localisation keys in tooltips; no launch crash (see repo memory on loc shadowing and moved-province crashes - new
  loc goes in a NEW uniquely named file).
- The old spirit's removal at Barbarossa/Aswan must NOT survive on the new spirit.

## Decided behaviour (the user's rules)

### Availability
- Existing gates kept: `has_war_with = ENG`, `country_exists = EFR` (the repo's working proxy for "France has fallen";
  the global flag `fall_of_france` is only set on one path - FRA in ENG's faction, victor in GER's faction, no
  `FRA_refus_absurde` - so it is not used).
- Replace "ITA fully controls Tripoli (448)" with: at least one of the four cities below is held by the Axis.
- Axis = controller is GER, a GER ally/faction member (an allied Vichy included; the mod already uses
  `is_controlled_by_ROOT_or_ally`) or ITA. A city held only by a non-allied Vichy (EFR) does NOT count: it is neutral French
  territory (Free France's `FRA_refus_absurde` clears Tunisia's demilitarized flag, so a Vichy-held Tunis could otherwise
  outrank Tripoli and the spawn would fail). Changed after review to honour the user's rule "French occupation -> Tripoli".

| Priority | City | State | Province for spawning |
|---|---|---|---|
| 1 | Tunis | 458 Tunisia | 11969 |
| 2 | Tripoli | 448 Tripoli | 1149 |
| 3 | Benghazi | 450 Benghasi | 11954 |
| 4 | Tobruk | 451 (file `451-Derna`, loc "Tobruk") | 13741 (new Tobruk port province; vanilla 1130 is now plain desert) |

- **Tunis counts only if it is not demilitarised** (`is_demilitarized_zone = no`). User rule: Tunisia is demilitarised only
  while under French occupation, in which case the divisions spawn in Tripoli. Fact check: the flag is set in
  `history/states/458-Tunisia.txt`, re-asserted by decision `PAR_keep_it_demili_tunisia`
  (`common/decisions/instant_effects.txt` ~2856) while France has not capitulated, and cleared only by `ITA_claim_tunisia`
  (`common/decisions/ITA.txt` ~2284) or a French focus (`common/national_focus/france.txt` ~2564-2582). Fall of France does
  not clear it, so a Vichy- or Italian-held Tunisia can still be demilitarised after the fall. The design gates on the
  flag itself (so such a Tunisia falls through to Tripoli) and does not change the flag logic. Flagged to the user.
- The rule applies to the availability gate too: a city "counts" if Axis-controlled (and, for Tunis, not demilitarised).
- **Instant, not a mission/operation (user):** a normal one-shot decision with `complete_effect` (no `days_remove`, no
  `remove_effect`), `fire_only_once = yes`, cost kept at 25. It stays in the `operations` category (a plain, always-allowed category; no better home was found).
- **Lockout (user):** once Barbarossa is declared (`GER = { has_completed_focus = GER_ussr_war_goal }`, set by the decision
  `GER_ussr_war_goal`) the decision is invisible and unavailable (`NOT = { has_completed_focus = GER_ussr_war_goal }` in
  `visible` and `available`), so it can never be pressed after Barbarossa. This removes any "granted after launch" case.

### Spawn
- Runs in `complete_effect`, instantly on pressing, together with the spirit grant.
- Divisions: 3 medium (Germany has `ger_1939_medium_tank_chassis` OR `ger_1940_medium_tank_chassis`), otherwise 4 light.
- Fully equipped: `create_unit` with `start_equipment_factor = 1`. Repo precedent that creates full tank divisions this way
  without stockpile preparation: `GER_arrdenes_counter_offensive_decision` (`common/decisions/GER.txt` 37-251).

### Template (grid in this mod is 5 columns x 4 rows; `MAX_DIVISION_BRIGADE_HEIGHT = 4`)
- Columns hold one battalion group each: tank columns x=0..2, motorized columns x=3..4.
- Medium version uses `medium_armor` + `motorized`; light version uses `light_armor` + `motorized`. Same layout.
- Without Germany's Mass Assault width tech (`has_tech = width_tech`): 9 tanks (3 x 3) + 6 motorized (2 x 3) = 15
  battalions x 2 = **30.00**, as in the reference screenshot.
- With `width_tech`: tank battalions are 1.95 wide, motorized 1.6 wide. The user's rule is "just above 30, closer is
  better". Computed options: 9+6 = 27.15 (too narrow); the user's suggestion 10+8 = 32.30 (too wide); **9 tanks + 8
  motorized (both motorized columns 4 deep) = 30.35**, the closest above 30 on this grid. 8+9 would be exactly 30.00
  but float-risky. Use 9+8.
- The tech exists only if Germany activated the free Mass Assault sub-doctrine `large_front_operations`; a later doctrine
  switch resets it and the template width changes without being rebuilt (accepted).
- Support companies: the reference screenshot shows 8 support slots and `MAX_DIVISION_SUPPORT_HEIGHT = 8` in the current
  `00_defines.lua` (an older repo note saying the cap is 6 is stale). Use the support set of the existing German
  "Panzer-Division" template (`history/units/GER_1936.txt` 68-77: artillery, recon_ac, mobile_engineer, anti_tank,
  maintenance_company, logistics_company_mot, anti_air_heavy_support, signal_company; x = 0, y = 0..7), dropping and
  reporting any id that is not a valid divisional support unit in the current tree. The screenshot's icons could not be
  read exactly; this is my call.
- Names (my call): "Afrikakorps Panzer-Division" / "Afrikakorps leichte Panzer-Division"; `division_names_group = GER_Arm_01`;
  `start_experience_factor = 0.5` (precedent).
- Equipment variants (`force_equipment_variants`, owner "GER"): medium -> if `ger_1940_medium_tank_chassis`:
  `medium_tank_chassis_1940` "Panzer III Ausf.H", else `medium_tank_chassis_1946` "Panzer IV" (1939 tech); light -> if
  `ger_1940_light_tank_chassis`: `light_tank_chassis_1940` "Panzer 38(t)", else `light_tank_chassis_1936`
  "Panzer II Ausf.a". These variant names exist only after the tech is researched (or, for the start-of-game ones, with the
  No Step Back DLC) - verify.

### Spirit values and timeline
- Recipients (decided by the user, including Finland, Italy and Vichy): same set as today - every country in GER's faction,
  plus EFR, GER, SPR - snapshot at grant. All recipients get the Soviet penalty. Note (consequence, accepted): the
  Barbarossa buff goes only to GER, BUL, ROM, HUN, SLO, SPR, so FIN/ITA/EFR take the Soviet penalty without a swing to cancel.
- Africa level W (0..8) = the `GER_aatlantic_wall_W` idea held by ENG (starts at 4; 0 = Axis holds all 8 checkpoints,
  +4% swing; 8 = Axis lost all, -4% swing). Africa swing = 4 - W points.
- **Before Barbarossa:** Soviet penalty N = 14 - W points, applied to both `attack_bonus_against` and
  `defense_bonus_against` vs SOV: W=0 -> -14%, W=4 -> -10%, W=8 -> -6%. Net with the Africa swing is constant (-10%). The
  repo's Barbarossa buff sums 13 - W with the German Atlantic Wall index, so one wall step = exactly 1 point.
  Desert bonus stays at +10% (desert and deep_desert attack). The Soviet penalty is NOT flat: it follows the Africa
  level the whole time until Barbarossa is declared.
- **Keeping N current (user requirements):** (a) the value N = 14 - W is maintained by a cheap **weekly** pulse on GER
  even while the decision has never been pressed, so the number a player would get is already current (and can be shown
  in the decision's tooltip); once the spirit exists the same pulse swaps it to the new level only when the level
  changed; (b) N is recomputed once more immediately on pressing, so a player pressing the day before Barbarossa never
  gets a stale value; (c) N is recomputed once more when Barbarossa is declared, immediately before it freezes. Daily
  polling is explicitly not wanted (performance).
- **From Barbarossa on:** Barbarossa = the decision `GER_ussr_war_goal` (earliest 1941-06-22; marker
  `GER = { has_completed_focus = GER_ussr_war_goal }`). The Africa swing stops tracking (N is frozen at launch).
  Both numbers then stay fixed until 1.1.1942 (user request, 2026-11-13) and drop 1 point per month after that (first tick
  1.2.1942; guard `date > 1942.1.2`) until 0. Spirit removed when both are 0. Until Barbarossa the desert bonus is
  flat and the Soviet penalty follows Africa (weekly); if Barbarossa never happens the spirit stays (accepted).
- The Africa swing is only guaranteed to net out for the Barbarossa buff. The 1942 summer-offensive decisions re-read W live;
  from 1.2.1942 N decays 1 point a month (about 4-5 points by the summer offensive), so the "constant net" ends around then (accepted).
- The real Africa swing is baked once into a 150-day timed buff (`GER_barb_offensive_buff_N`) at launch by
  `get_barb_offensive` (`XEN_touch_and_perish_scripted_effects.txt` ~8208-8381) and re-read live by the 1942 summer offensive
  decisions; this design does not change either.

## Implementation shape (my calls - builder may improve)

Facts: a targeted modifier cannot take a variable and no country-level desert-attack key exists, so:
- **Soviet penalty:** 15 stepped national spirits `..._0` to `..._14` (the `_0` shell has no targeted modifier)
  each with `targeted_modifier = { tag = SOV attack_bonus_against = -0.0N defense_bonus_against = -0.0N }`, all with the same
  display name "Afrikakorps". Swap with `swap_ideas` / remove-all-then-add. Precedent: `GER_barb_offensive_buff_1..32` in
  `common/ideas/germany.txt`, `ENG_afrika_campaign..4`.
- **Desert bonus:** 10 hidden technologies `MFU_ak_desert_1..10`, each with `desert = { attack = 0.0N }` and
  `deep_desert = { attack = 0.0N }` terrain adjusters under sub-unit categories (`category_all_infantry`, `category_tanks`
  proven in the mod; confirm armour/motorized/artillery coverage). Toggle with `set_technology`. Run
  `python tools/terrain_copies/sync.py --check` afterwards.
- One visible spirit in the UI: each idea level prints the live desert % via a `custom_modifier_tooltip` using a variable.
- State on GER: variables for the Soviet level and desert level, flag for "decaying".
- Pre-Barbarossa tracking (user's choice for performance): one scripted effect computes W from
  `ENG = { has_idea = GER_aatlantic_wall_W }` and stores N = 14 - W on GER. It is called (1) by a weekly pulse limited to
  GER (`on_weekly_GER` if that on_action exists, else `on_weekly` with `limit = { tag = GER }`), which stops once Barbarossa
  is declared and only swaps ideas when the level actually changed; (2) from the decision's `complete_effect` right before
  the grant; (3) from the `GER_ussr_war_goal` decision's `complete_effect` (`common/decisions/GER.txt` ~558-975), before
  `get_barb_offensive`, followed by the freeze. Rejected alternative: appending a call to the tails of
  `ENG_africa_hopping_level_up` / `_down` (`ENG_scripted_effects.txt`) - zero polling cost but touches two ~2,000-line effects.
- Decay: `on_monthly` pulse on GER once the Barbarossa marker is true and `date > 1942.1.2`.
- Generate the ideas, techs and localisation with a new Python generator under `tools/` (pattern:
  `tools/terrain_build_speed/generate.py`); there is no existing generator for idea families.
- Replace/remove `GER_afrika_campaign` and the dead `GER_afrika_campaign2` (its `on_remove` re-adds the first); update the
  two `add_ideas = GER_afrika_campaign` call sites in the decision; stop firing the no-op event `germany.233`.
- Localisation: a new uniquely named file in `localisation/english/`; do NOT edit `GER_afrikakorps_tt` (shared with the
  Italian focus) - use new keys. The decision title/description reuse focus keys `GER_africa_korps(_desc)`
  (`focus_l_english.yml:868`); write new decision-specific text.

## Left to the builder / verify in game
1. Spawned tanks do not reduce Germany's stockpile (compare before/after).
2. A GER-owned division can be placed in a province controlled by ITA or EFR; behaviour if no valid province exists;
   behaviour of `create_unit` in a demilitarised state (avoided for Tunis by the gate).
3. Desert bonus reaches the new divisions and is not diluted by support battalions.
4. `swap_ideas` when the old idea is absent; initial add path.
5. Variant names exist at the time of the spawn; light/medium chassis equipment under the non-No-Step-Back tech tree.
6. Exact weekly on_action form, and that the weekly pulse costs nothing measurable (it should do a handful of variable
   operations and swap ideas only on a level change).
7. Whether the AI should be steered (currently `ai_will_do factor = 10`; keep).

## Calls I made (user to check)
- Gate on `is_demilitarized_zone = no` for Tunis instead of changing when Tunisia is demilitarised.
- "Axis" for control = GER, GER ally (allied Vichy included), ITA; a non-allied Vichy-held Tunis does not count.
- Keep `country_exists = EFR` as the fall-of-France proxy.
- Visible conditions keep "at war with ENG, ITA at war with ENG"; the control requirement lives in `available`.
- Cost stays 25 (political power) on the new instant decision; experience 0.5; template names; variant choices.
- Desert bonus flat, Soviet penalty follows Africa (weekly + recompute on press + recompute at Barbarossa); decay starts after
  Barbarossa AND after 1.1.1942 (first tick 1.2.1942) for both.
- Weekly pulse, not an event hook on the ENG hopping effects.
- Template with width tech = 9 tanks + 8 motorized (30.35).
- Late joiners to the faction get nothing.
- The decision locks out (invisible, unavailable) once Barbarossa is declared, so there is no "granted after launch" case.
