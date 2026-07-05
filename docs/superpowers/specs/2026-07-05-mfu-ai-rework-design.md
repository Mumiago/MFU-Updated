# MFU Randomized AI Rework — Design Spec

Date: 2026-07-05
Status: Approved design, pending spec review

## 1. Goal

Teach the MFU AI to build better, more varied division templates and tank designs, and to
allocate major-power production sensibly — with the choices **randomized at the start of every
new game** so each playthrough differs.

Concretely:
- **Infantry-type divisions:** ~30 combat width, 7–11 org line battalions (infantry / motorized /
  mechanized), the rest artillery / anti-tank / anti-air / (occasionally) tanks.
- **Tank divisions:** ~30 combat width, 7–11 motorized/mechanized org battalions, the rest tanks —
  with variety including **tank destroyers** and **assault guns / SP-artillery**.
- **AI-designed tanks:** the AI designs its own tanks from modules, with varied loadouts.
- **Majors' production:** roughly **40% air / 30% tanks / 30% infantry** of military factories.
- **Per-game variety:** every AI country rolls a random "doctrine profile" at game start; the same
  country plays differently across games.

## 2. Decisions (locked)

| Question | Decision |
|---|---|
| Which AI | **All AI countries** (templates + designs). Production 40/30/30 layer targets **majors**. |
| Variety mechanism | **Randomize at game start** via `on_startup` → `random_list` → country flags. |
| Production integration | **Overhaul** the equipment production-mix in `production_ai_strategies.txt` for majors. Preserve construction/convoy steering. |
| Variety depth | **Medium**: ~4 infantry doctrines, ~4 tank doctrines, ~4 tank-design styles. |

## 3. How the game systems work (grounding)

- **`common/ai_templates/`** — role-based target templates. **Width is implicit**: it is the sum of
  each battalion's combat width in `target_template.regiments`. The mod's existing templates run
  ~15 line battalions (e.g. `medium_armor 7 + motorized 4 + mechanized 3 + armored_car 1`), which is
  the ~30-width calibration we target. Only `generic.txt` is active; the 20 `templates_<TAG>.txt`
  files are fully commented out. There is **no active country gating** — all AI share `generic.txt`.
- **`common/ai_equipment/`** — the AI designs equipment from `type` (chassis archetype) + `modules`
  + `allowed_modules`, grouped by `roles`. Tank family roles include `land_medium_tank`,
  `land_medium_tank_destroyer`, `land_medium_tank_artillery` (assault guns), `land_*_tank_anti_air`.
- **`common/ai_strategy/`** — production steering. No single "40% factories on air" knob; approximated
  with `air_factory_balance`, `equipment_production_factor`, `equipment_production_min_factories`,
  `role_ratio`, `unit_ratio`, `equipment_variant_production_factor`.
- **Randomization idiom** — `on_startup` → `every_country { random_list { … set_country_flag } }`,
  gated by a game rule; other systems read the flags via `enable = { has_country_flag = … }`.

## 4. Valid battalion tokens (from the mod's active `generic.txt`)

- **Org line battalions:** `infantry`, `motorized`, `mechanized`, `armored_car`, `volkssturm_infantry`,
  `garrison`, `marine`, `mountaineers`, `paratrooper`, `cavalry`.
- **Tanks (line):** `light_armor`, `medium_armor`, `heavy_armor`, `super_heavy_armor`, `modern_armor`.
- **Tank variants (line):** `medium_tank_destroyer_brigade`, `light_tank_destroyer`,
  `heavy_tank_destroyer_brigade`, `modern_tank_destroyer_brigade`, `light_sp_artillery_brigade`,
  `light_sp_anti_air_brigade`.
- **Support-fire line battalions:** `artillery_brigade`, `artillery_brigade_mot`, `anti_tank`,
  `anti_air`, `pack_artillery_brigade`, `rocket_artillery`.
- **Support companies (mod-specific):** `mobile_engineer`, `engineer`, `construction_engineer`,
  `recon`, `recon_ac`, `signal_company`, `maintenance_company`, `logistics_company`, `field_hospital`,
  `military_police`, `artillery` (support), `field_gun_support`, `artillery_heavy_support`.

> Implementation note: exact per-battalion combat widths and the precise AT/AA line tokens
> (`anti_tank` vs `anti_tank_brigade`, `anti_air` vs `anti_air_brigade`) will be confirmed against
> `common/units/*.txt` before authoring counts, so every template hits ~30 width with valid tokens
> and no `error.log` warnings. Support cap is 6 (mod division rework), so support blocks stay ≤ 6.

## 5. Architecture — five components (build order A→E)

### A. Foundation: game-start randomizer + toggle
- **New game rule** `MFU_ai_variety` in `common/game_rules/` — options `ON` (default) / `OFF`. Loc added.
- **New** `common/on_actions/MFU_ai_variety_on_actions.txt` appends to `on_startup`:
  ```
  every_country = {
      limit = { has_game_rule = { rule = MFU_ai_variety option = ON } }
      random_list = { … set_country_flag = MFU_inf_<X> … }      # infantry doctrine
      random_list = { … set_country_flag = MFU_tank_<Y> … }     # tank doctrine
      random_list = { … set_country_flag = MFU_tankdesign_<Z> … } # tank-design style
  }
  ```
  (Uses `on_startup` in an additive mod file so vanilla `on_startup` effects are preserved.)
- **Flags (Medium depth):**
  - Infantry: `MFU_inf_arty`, `MFU_inf_at`, `MFU_inf_aa`, `MFU_inf_combined`
  - Tank: `MFU_tank_pure`, `MFU_tank_td`, `MFU_tank_ag`, `MFU_tank_combined`
  - Tank design: `MFU_tankdesign_mass`, `MFU_tankdesign_balanced`, `MFU_tankdesign_quality`, `MFU_tankdesign_fast`
- Runs once at game start; flags persist for the game. Existing saves unaffected (acceptable).

### B. Infantry templates (`ai_templates/generic.txt`, `infantry` role)
Four flag-gated target-template variants, each ~30 width, 7–11 infantry org battalions + rest:
- `MFU_inf_arty` → infantry + heavy artillery_brigade (e.g. `infantry 10 + artillery_brigade 5`)
- `MFU_inf_at` → infantry + anti-tank line + some arty
- `MFU_inf_aa` → infantry + anti-air line + some arty
- `MFU_inf_combined` → infantry + a few `medium_armor` + arty (tank-supported)
- **Default fallback** variant enabled when no `MFU_inf_*` flag is set (game-rule-OFF safety), so the
  AI always has a valid infantry template.
Each variant uses `enable = { has_country_flag = MFU_inf_<X> }`. Support block ≤ 6, mod tokens.

### C. Tank templates (`ai_templates/generic.txt`, `armor` role)
Four flag-gated variants, ~30 width, 7–11 mot/mech org + rest armor:
- `MFU_tank_pure` → mostly `medium_armor` + mot/mech
- `MFU_tank_td` → `medium_armor` + `medium_tank_destroyer_brigade` + mot/mech
- `MFU_tank_ag` → `medium_armor` + `light_sp_artillery_brigade` (assault guns) + mot/mech
- `MFU_tank_combined` → mixed tanks + TD + mot/mech
- **Default fallback** as in B. (The existing `motorized` role is kept/aligned as a secondary mobile line.)

### D. Tank designs (`ai_equipment/`)
- Ensure the AI fields the full tank family (main tank, **tank destroyer**, **assault gun**) so the
  Section-C templates have equipment to fill.
- Vary module loadouts by the **tank-design style** flag, applied in `generic_tank.txt` (covers all
  minors + majors without a specific file) and the per-major tank files, unified onto the style system:
  - `MFU_tankdesign_mass` — cheap gun / thin armor / cheap engine
  - `MFU_tankdesign_balanced` — middle-of-the-road
  - `MFU_tankdesign_quality` — big gun / thick (sloped) armor
  - `MFU_tankdesign_fast` — speed engine / lighter armor
- Uses mod chassis archetypes (`medium_tank_chassis_1940/1942/1943`, `heavy_tank_chassis_1942/1944`)
  and mod slots (incl. `armor_sloping_slot`). `enable`/`priority` gate on `has_country_flag` + `has_tech`.

### E. Production overhaul — majors (`ai_strategy/production_ai_strategies.txt`)
- Replace the per-major **equipment production-mix** blocks with a majors layer targeting
  ~40% air / 30% tank / 30% inf mil factories:
  - `air_factory_balance` (push air share) + `equipment_production_factor` (fighter/CAS high, armor
    moderate, infantry moderate) + `equipment_production_min_factories` floors to hold the split +
    `role_ratio` (armor vs infantry divisions) to shape need.
- **Preserve** construction/convoy steering (autobahn, `GER_wants_civ/mils`, convoy building) — only
  the equipment mix changes.
- Applies to a defined majors set (GER, SOV, USA, ENG, JAP, ITA, FRA + mod-added majors / `is_major`).
- Exact split is need-driven and clamped by available factories, so 40/30/30 is a tuned approximation.

## 6. Files touched

- **New:** `common/game_rules/MFU_ai_variety.txt`, `common/on_actions/MFU_ai_variety_on_actions.txt`,
  loc file for the game rule + any new flag tooltips.
- **Modified:** `common/ai_templates/generic.txt` (B, C); `common/ai_equipment/generic_tank.txt` +
  per-major `*_tank.txt` (D); `common/ai_strategy/production_ai_strategies.txt` (E).
- **Untouched:** the dead `templates_<TAG>.txt` files (remain unused); construction-steering blocks.

## 7. Risks & mitigations

- **Invalid tokens / wrong width** → confirm sub-unit tokens and combat widths from `common/units/`
  before authoring counts; keep support ≤ 6.
- **Overhauling majors' production may unbalance tuned nations** (accepted) → preserve construction
  steering; keep the mix layer isolated and revertible.
- **"No template" when variety is OFF** → default-fallback template variants with no flag requirement.
- **Randomization only fires on new games** → documented; acceptable.
- **Player countries** → template/equipment/strategy systems are AI-only, so rolling flags for all
  countries is harmless to players.

## 8. Verification (no automated HOI4 tests)

- Load mod; check `error.log` for invalid sub-unit/module tokens and script errors (clean = pass).
- In-game debug: `imgui show ai_templates` and `imgui show ai_division_production` on several AI
  nations; confirm ~30-width templates matching the rolled profile.
- Play two fresh games; confirm the same nation rolls different profiles (variety works).
- Spot-check a major's factory allocation trends toward ~40/30/30 after a few years.
- Toggle the game rule OFF; confirm AI still gets valid default templates.

## 9. Out of scope

- Reviving/authoring the dead per-country `templates_<TAG>.txt` files.
- Naval/air template & design rework (this is land templates, tank designs, and the air/tank/inf
  production split only).
- Cleaning the duplicate `ITA_state_development_africa_tt2` loc key (unrelated).
- Difficulty-based scaling.
