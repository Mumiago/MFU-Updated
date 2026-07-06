# MFU AI Assembly Construction — Design Spec

Date: 2026-07-06
Status: Approved design, pending spec review

## 1. Problem

The mod gates tank and aircraft production behind two custom strategic resources, `tank_production`
and `air_production` (`common/resources/00_resources.txt`). Each tank/plane costs **10** of its
resource; the resource is supplied by two buildings, `tank_assembly` (~**90** capacity each) and
`air_assembly` (~**110** capacity each), via the "BI" dynamic-modifier system
(`common/scripted_effects/BI_scripted_effects.txt` → `assembly_production` dynamic modifier in
`common/dynamic_modifiers/1_BI_modifiers.txt`, which sets `country_resource_cost_{tank,air}_production`).

**No `ai_strategy` anywhere tells the AI to build `tank_assembly`/`air_assembly`.** So AI countries
build zero assemblies, have ~zero tank/air production capacity, and therefore cannot produce tanks or
aircraft in quantity — regardless of the 40/30/30 factory-mix strategy added earlier. This is the root
cause of both reported symptoms: "AI underproduces air/tanks" and "AI doesn't follow 40/30/30".

(Related prerequisite, already fixed: `update_resource_assembly` was gated `is_ai = no`, so even an AI
that *had* assemblies got no capacity. That gate was removed so AI now converts assemblies into
capacity via the same `on_daily`/`on_weekly` path as the player.)

## 2. Goal

Teach **all AI countries** to build `tank_assembly` and `air_assembly` buildings in proportion to their
military-industrial size, so they have the capacity to execute tank/air production.

## 3. Decisions (locked)

| Question | Decision |
|---|---|
| Which AI | **All AI countries** (`is_ai = yes`), scaled by size. |
| Sizing | **Scale to military-factory count** via tiered `building_target` bands. |
| Mechanism | **`ai_strategy = { type = building_target id = <assembly> value = N }`** — the idiomatic HOI4 construction lever (same one the mod uses for `industrial_complex`/`arms_factory`). |
| Calibration anchor | A ~150-military-factory major should end up with **~5 tank / ~5 air** assemblies (≈ 1 assembly per ~30 military factories). |

## 4. Design

New file **`common/ai_strategy/MFU_assembly_targets.txt`** — additive, modifies nothing else.

Five tiered strategy blocks, each gated `is_ai = yes` on a military-factory **band** (mutually
exclusive, so exactly one tier is active per country; the target is absolute, not additive):

| Tier | `enable` factory trigger(s) | Covers | `tank_assembly` | `air_assembly` |
|---|---|---|---|---|
| 1 | `num_of_military_factories < 20` | 0–19 | 1 | 1 |
| 2 | `> 19` and `< 51` | 20–50 | 2 | 2 |
| 3 | `> 50` and `< 101` | 51–100 | 3 | 3 |
| 4 | `> 100` and `< 201` | 101–200 | 5 | 5 |
| 5 | `> 200` | 201+ | 8 | 7 |

`num_of_military_factories` is an integer, so `> 19` means ≥ 20 and `< 51` means ≤ 50; the bands are
mutually exclusive with no gaps (0–19, 20–50, 51–100, 101–200, 201+).

Block shape:
```
MFU_assembly_tier_4 = {
    allowed = { always = yes }
    enable = { is_ai = yes  num_of_military_factories > 100  num_of_military_factories < 201 }
    ai_strategy = { type = building_target id = tank_assembly value = 5 }
    ai_strategy = { type = building_target id = air_assembly  value = 5 }
}
```

Rationale for the numbers: anchored to ~5/~5 at 150 factories (≈ 1 per 30 mil factories); the top tier
leans slightly tank-heavy because tanks are the 30% slice of a larger base and each tank assembly (90)
covers fewer units than an air assembly (110). GER/SOV get extra `tank_production_capacity` from national
ideas, so their tank assemblies over-supply the target — harmless.

## 5. Files touched

- **New:** `common/ai_strategy/MFU_assembly_targets.txt`.
- **Untouched:** everything else (buildings, resources, BI system, the earlier 40/30/30 production
  strategies).

## 6. Risks & mitigations

- **AI may deprioritize assemblies** in its construction queue despite the `building_target` (it weighs
  them against factories/infra). Mitigation: ship the clean `building_target` version first; if a test
  game shows the AI ignoring it, escalate with a construction-priority nudge (higher target or a
  `factory_build_score_factor`-style boost). Documented, accepted.
- **Assemblies share building slots** with civ/mil factories, so the AI builds somewhat fewer factories.
  This trade is unavoidable (no capacity = no tanks/air); the tier values are the dial to soften it.
- **Exact targets are calibration estimates** and may need in-game tuning after observing an AI major's
  actual `tank_production`/`air_production` balance. The tier table is the single tuning knob.

## 7. Verification (no automated HOI4 tests)

- Load mod; `error.log` clean (valid `building_target` ids `tank_assembly`/`air_assembly`, no script
  errors).
- In-game: fast-forward a few years, inspect an AI major — confirm it has built ~5 of each assembly at
  ~150 factories and now shows positive `tank_production`/`air_production` capacity and actual tank/air
  equipment in production.
- Confirm a small AI (< 20 factories) builds ~1 of each, not a runaway amount.

## 8. Out of scope

- Division `role_ratio` retuning (secondary suspect for tank underproduction; revisit only if capacity
  fix proves insufficient).
- Per-country assembly targets (generic band scaling is used for all AI).
- Changing assembly building costs, capacities, or the resource costs of tanks/aircraft.
