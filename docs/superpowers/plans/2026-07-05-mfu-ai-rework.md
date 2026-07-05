# MFU Randomized AI Rework — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give MFU's AI randomized, per-game division templates, tank designs, and major-power production mixes so each playthrough differs, while every choice loads clean and stays valid.

**Architecture:** A game-start randomizer (`on_startup` → `every_country` → `random_list`) stamps one flag from each of three doctrine families (infantry / tank / tank-design) onto every AI country. Flag-gated `enable` blocks in `common/ai_templates/generic.txt` select an infantry and an armor target template; flag-gated `priority` modifiers in the per-major `*_tank.txt` files select a tank-design style and add a tank-destroyer design; and per-major production blocks target ~40% air / 30% tank / 30% infantry factories.

**Tech Stack:** Hearts of Iron IV (NSB-era) mod script — `common/game_rules`, `common/on_actions`, `common/ai_templates`, `common/ai_equipment`, `common/ai_strategy`, `localisation/english`. No automated test framework exists; verification is `error.log` inspection plus in-game `imgui` debug.

## Global Constraints

- **Regimental support only for AT/AA/pack-artillery.** `anti_tank`, `anti_air`, and pack-artillery are placed **only** in a template's `regimental_support = { }` block using the mod tokens `anti_tank_brigade`, `anti_air`, `pack_artillery_brigade` (all `combat_width = 0`, `regimental = yes`, defined in `common/units/fire_support.txt`). Never as line `regiments`, never in divisional `support`.
- **Divisional support cap = 6.** Every `support = { }` block has ≤ 6 companies (mod division rework).
- **Width target ≈ 30.** Every combat template's line `regiments` sum to **15 battalions** (all line battalions are `combat_width = 2`; 15 × 2 = 30). Org line battalions (infantry / motorized / mechanized) stay in the **7–11** band.
- **Valid tokens only.** These tokens do **not** exist and must never be written to a template: `anti_tank`, `anti_air_brigade`, `modern_armor`, `light_tank_destroyer`, `modern_tank_destroyer_brigade`. Valid armor-variant line tokens: `medium_tank_destroyer_brigade`, `heavy_tank_destroyer_brigade`, `light_sp_artillery_brigade`, `light_sp_anti_air_brigade` (all cw 2).
- **Loc files need UTF-8-BOM.** Every `.yml` starts with the BOM, then `l_english:`, then ` KEY:0 "value"` (one leading space, `:0` version tag).
- **Additive mod files.** New `on_actions` use `on_actions = { on_startup = { effect = { … } } }` so vanilla `on_startup` effects are preserved.
- **Comment style:** minimal/terse comments only.
- **Randomization fires on new games only** (documented, accepted). Existing saves are unaffected.

---

## File Structure

| File | Status | Responsibility |
|---|---|---|
| `common/game_rules/MFU_ai_variety.txt` | Create | The `MFU_ai_variety` ON/OFF toggle |
| `common/on_actions/MFU_ai_variety_on_actions.txt` | Create | `on_startup` randomizer rolling the 12 doctrine flags |
| `localisation/english/MFU_ai_variety_l_english.yml` | Create | Loc for the rule + options |
| `common/ai_templates/generic.txt` | Modify | Flag-gated infantry (role `infantry`) + tank (role `armor`) target templates |
| `common/ai_equipment/GER_tank.txt` | Modify | GER style-gated medium designs + TD design |
| `common/ai_equipment/SOV_tank.txt` | Modify | SOV style-gated medium designs + TD design |
| `common/ai_equipment/USA_tank.txt` | Modify | USA style-gated medium designs + TD design |
| `common/ai_equipment/ENG_tank.txt` | Modify | ENG style-gated medium designs + TD design |
| `common/ai_strategy/production_ai_strategies.txt` | Modify | GER/SOV/USA/ENG 40/30/30 equipment mix |
| `common/ai_strategy/JAP.txt` | Modify | JAP 40/30/30 equipment mix |
| `common/ai_strategy/ITA.txt` | Modify | ITA 40/30/30 equipment mix |
| `common/ai_strategy/FRA.txt` | Modify | FRA 40/30/30 equipment mix |

**The 12 flags (one rolled per family per country):**
- Infantry: `MFU_inf_arty`, `MFU_inf_at`, `MFU_inf_aa`, `MFU_inf_combined`
- Tank: `MFU_tank_pure`, `MFU_tank_td`, `MFU_tank_ag`, `MFU_tank_combined`
- Tank design: `MFU_tankdesign_mass`, `MFU_tankdesign_balanced`, `MFU_tankdesign_quality`, `MFU_tankdesign_fast`

---

## Verification model (applies to every task)

There are no unit tests. Each task's "run the test" steps mean:

1. **Launch HOI4 with the mod**, let the launcher compile, reach the main menu / start a fresh game.
2. **Open the log:** `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log`.
3. **Pass = the task's named tokens/blocks produce no new error lines** (no `Unexpected token`, no `Invalid … <token>`, no `unknown sub_unit`, no loc `Missing UTF8 BOM`).
4. Where a step says **imgui check**, in a running game open console (`~`), run the named `imgui show …` command, and read off the stated field.

A fast pre-launch syntax sanity check is included where useful via a brace-balance shell check.

---

### Task A: Foundation — game rule, randomizer, loc

**Files:**
- Create: `common/game_rules/MFU_ai_variety.txt`
- Create: `common/on_actions/MFU_ai_variety_on_actions.txt`
- Create: `localisation/english/MFU_ai_variety_l_english.yml`

**Interfaces:**
- Produces: 12 country flags — `MFU_inf_{arty,at,aa,combined}`, `MFU_tank_{pure,td,ag,combined}`, `MFU_tankdesign_{mass,balanced,quality,fast}` — set on every country at `on_startup` when `has_game_rule = { rule = MFU_ai_variety option = ON }`. Tasks B, C, D read these via `has_country_flag`.

- [ ] **Step 1: Create the game rule**

Create `common/game_rules/MFU_ai_variety.txt`:

```
MFU_ai_variety = {
	name = "RULE_MFU_AI_VARIETY"
	group = "RULE_GROUP_MFU"
	default = {
		name = ON
		text = "RULE_MFU_AI_VARIETY_ON"
		desc = "RULE_MFU_AI_VARIETY_ON_DESC"
	}
	option = {
		name = OFF
		text = "RULE_MFU_AI_VARIETY_OFF"
		desc = "RULE_MFU_AI_VARIETY_OFF_DESC"
	}
}
```

Note: the default option's `name = ON` is the token referenced by `option = ON` in `has_game_rule`.

- [ ] **Step 2: Create the randomizer on_action**

Create `common/on_actions/MFU_ai_variety_on_actions.txt`:

```
on_actions = {
	on_startup = {
		effect = {
			every_country = {
				limit = {
					has_game_rule = { rule = MFU_ai_variety option = ON }
				}
				random_list = {
					25 = { set_country_flag = MFU_inf_arty }
					25 = { set_country_flag = MFU_inf_at }
					25 = { set_country_flag = MFU_inf_aa }
					25 = { set_country_flag = MFU_inf_combined }
				}
				random_list = {
					25 = { set_country_flag = MFU_tank_pure }
					25 = { set_country_flag = MFU_tank_td }
					25 = { set_country_flag = MFU_tank_ag }
					25 = { set_country_flag = MFU_tank_combined }
				}
				random_list = {
					25 = { set_country_flag = MFU_tankdesign_mass }
					25 = { set_country_flag = MFU_tankdesign_balanced }
					25 = { set_country_flag = MFU_tankdesign_quality }
					25 = { set_country_flag = MFU_tankdesign_fast }
				}
			}
		}
	}
}
```

- [ ] **Step 3: Create the loc (with BOM)**

Create `localisation/english/MFU_ai_variety_l_english.yml`. It MUST begin with a UTF-8 BOM. Write these exact lines (content):

```
l_english:
 RULE_MFU_AI_VARIETY:0 "MFU AI Variety"
 RULE_GROUP_MFU:0 "MFU Rules"
 RULE_MFU_AI_VARIETY_ON:0 "On"
 RULE_MFU_AI_VARIETY_ON_DESC:0 "AI countries roll randomized division-template, tank-design, and production doctrines at game start, so each game plays differently."
 RULE_MFU_AI_VARIETY_OFF:0 "Off"
 RULE_MFU_AI_VARIETY_OFF_DESC:0 "AI uses fixed default templates and tank designs."
```

- [ ] **Step 4: Ensure the loc file has a BOM**

The Write tool does not emit a BOM. Prepend it. Run:

```bash
f="localisation/english/MFU_ai_variety_l_english.yml"; head -c3 "$f" | xxd | grep -q "efbb bf" || { printf '\xEF\xBB\xBF' | cat - "$f" > "$f.tmp" && mv "$f.tmp" "$f"; }; head -c6 "$f" | xxd
```

Expected output: first bytes `efbb bf6c 5f65` (BOM + `l_e`).

- [ ] **Step 5: Brace-balance sanity check**

Run:

```bash
for f in common/game_rules/MFU_ai_variety.txt common/on_actions/MFU_ai_variety_on_actions.txt; do o=$(grep -o "{" "$f" | wc -l); c=$(grep -o "}" "$f" | wc -l); echo "$f open=$o close=$c"; done
```

Expected: `open` equals `close` for both files.

- [ ] **Step 6: Load test**

Launch HOI4 with MFU, start a fresh game as any country with the default rule (ON). Open `logs/error.log`.
Expected: no lines mentioning `MFU_ai_variety`, `MFU_inf_`, `MFU_tank_`, `RULE_MFU_AI_VARIETY`, or `Missing UTF8 BOM … MFU_ai_variety`. The rule appears in the new-game rules screen under "MFU Rules".

- [ ] **Step 7: Flag check (imgui / console)**

In a running fresh game, open console and run:

```
tag GER
```

then

```
has_country_flag MFU_inf_arty
```

is not a console command; instead verify via effect log — run `effect log = "GER inf=[?GER.has_country_flag ...]"` is unavailable, so use the observable proxy: open console `add_latest_focus` not needed — simplest check is Task B's imgui. For Task A alone, confirm via: console `reload loc` shows the rule text, and error.log is clean. (Flag effect is verified end-to-end in Task B Step 8.)

- [ ] **Step 8: Commit**

```bash
git add common/game_rules/MFU_ai_variety.txt common/on_actions/MFU_ai_variety_on_actions.txt localisation/english/MFU_ai_variety_l_english.yml
git commit -m "feat(ai): add MFU_ai_variety game rule + game-start doctrine randomizer"
```

---

### Task B: Infantry target templates (role `infantry`)

**Files:**
- Modify: `common/ai_templates/generic.txt` (the `infantry_generic` block, currently lines ~260-305; and disable the competing `motorized_generic` role=infantry line ~11 and `infantry_big_generic` role=infantry line ~307)

**Interfaces:**
- Consumes: `MFU_inf_arty` / `MFU_inf_at` / `MFU_inf_aa` / `MFU_inf_combined` flags from Task A.
- Produces: exactly one active role-level `infantry` entry (`infantry_generic`) holding a default + 4 flag-gated variants.

**Design note (pre-existing smell):** vanilla `_documentation.md` says each country should have **max one** role-level entry per role. The mod currently has three role=infantry entries (`motorized_generic`, `infantry_generic`, `infantry_big_generic`), which is "undefined" per the docs. This task consolidates the infantry doctrines into `infantry_generic` and disables the other two entries' `infantry` targeting to make selection deterministic.

- [ ] **Step 1: Read the current infantry blocks**

Run:

```bash
grep -n "role = infantry\|role =infantry\|_generic = {" common/ai_templates/generic.txt
```

Confirm the three role=infantry blocks (`motorized_generic`, `infantry_generic`, `infantry_big_generic`) and their line numbers before editing.

- [ ] **Step 2: Replace the `infantry_generic` block with the flag-gated set**

Replace the entire existing `infantry_generic = { … }` block with:

```
infantry_generic = {

	role = infantry

	upgrade_prio = {
		factor = 1
	}

	# Default fallback — always evaluated. Used when the game rule is OFF (no MFU_inf_* flag). Lowest prio so any rolled doctrine wins.
	infantry_default = {
		upgrade_prio = { factor = 1 }
		target_template = {
			support = {
				engineer = 1
				recon = 1
				field_hospital = 1
				artillery_heavy_support = 1
				signal_company = 1
			}
			regiments = {
				infantry = 11
				artillery_brigade = 4
			}
		}
	}

	# Artillery doctrine — arty-heavy line.
	infantry_arty = {
		enable = { has_country_flag = MFU_inf_arty }
		upgrade_prio = { factor = 10 }
		target_template = {
			support = {
				engineer = 1
				recon = 1
				field_hospital = 1
				artillery_heavy_support = 1
				signal_company = 1
			}
			regiments = {
				infantry = 9
				artillery_brigade = 6
			}
		}
	}

	# Anti-tank doctrine — AT delivered via regimental support.
	infantry_at = {
		enable = { has_country_flag = MFU_inf_at }
		upgrade_prio = { factor = 10 }
		target_template = {
			support = {
				engineer = 1
				recon = 1
				field_hospital = 1
				artillery_heavy_support = 1
			}
			regimental_support = {
				anti_tank_brigade = 1
			}
			regiments = {
				infantry = 11
				artillery_brigade = 4
			}
		}
	}

	# Anti-air doctrine — AA delivered via regimental support.
	infantry_aa = {
		enable = { has_country_flag = MFU_inf_aa }
		upgrade_prio = { factor = 10 }
		target_template = {
			support = {
				engineer = 1
				recon = 1
				field_hospital = 1
				artillery_heavy_support = 1
			}
			regimental_support = {
				anti_air = 1
			}
			regiments = {
				infantry = 11
				artillery_brigade = 4
			}
		}
	}

	# Combined-arms doctrine — infantry backed by a tank block.
	infantry_combined = {
		enable = { has_country_flag = MFU_inf_combined }
		upgrade_prio = { factor = 10 }
		target_template = {
			support = {
				mobile_engineer = 1
				recon = 1
				maintenance_company = 1
				field_hospital = 1
				artillery_heavy_support = 1
			}
			regimental_support = {
				pack_artillery_brigade = 1
			}
			regiments = {
				infantry = 9
				medium_armor = 3
				artillery_brigade = 3
			}
		}
	}
}
```

Width check: every variant's `regiments` sum to 15 line battalions (arty 9+6; at 11+4; aa 11+4; combined 9+3+3; default 11+4). Support ≤ 6; regimental_support ≤ 1.

- [ ] **Step 3: Disable the competing infantry role-level entries**

In `motorized_generic` (top of file), change its role line so it no longer competes for the `infantry` role. Replace:

```
	role = infantry
```

(inside `motorized_generic`) with a commented-out block plus a neutralizing enable on its single variant. Simplest deterministic fix: comment the whole `motorized_generic` block by wrapping — instead, set its variant `motorized_default` to never target infantry by commenting the block. Replace the entire `motorized_generic = { … }` block with:

```
# motorized_generic disabled: infantry role is now served solely by infantry_generic (see MFU AI rework).
# Original motorized target template preserved here for reference / future re-enable.
#motorized_generic = {
#	role = infantry
#	motorized_default = {
#		target_template = {
#			regiments = { mechanized = 2 motorized = 6 armored_car = 2 artillery_brigade_mot = 5 }
#			support = { mobile_engineer = 1 logistics_company = 1 maintenance_company = 1 field_hospital = 1 artillery = 1 field_gun_support = 1 artillery_heavy_support = 1 recon_ac = 1 }
#		}
#	}
#}
```

- [ ] **Step 4: Disable `infantry_big_generic`**

Replace the entire `infantry_big_generic = { … }` block with:

```
# infantry_big_generic disabled: folded into infantry_generic (infantry_default is the 11-inf + 4-arty template).
```

- [ ] **Step 5: Brace-balance sanity check**

Run:

```bash
o=$(grep -o "{" common/ai_templates/generic.txt | wc -l); c=$(grep -o "}" common/ai_templates/generic.txt | wc -l); echo "open=$o close=$c"
```

Expected: `open` equals `close`.

- [ ] **Step 6: Invalid-token scan**

Run:

```bash
grep -nE "\b(anti_tank|anti_air_brigade|modern_armor|light_tank_destroyer|modern_tank_destroyer_brigade)\b *=" common/ai_templates/generic.txt
```

Expected: **no output** (note: `anti_air` as a `regimental_support` token is valid and will NOT match this pattern; only the bare invalid line tokens would).

- [ ] **Step 7: Load test**

Launch HOI4 + MFU, start a fresh game. Open `logs/error.log`.
Expected: no `Invalid`/`unknown` sub_unit lines referencing infantry template tokens, no `Unexpected token` near `infantry_generic`.

- [ ] **Step 8: imgui verification (end-to-end, also validates Task A flags)**

Start a fresh game (rule ON). Pick an AI major, e.g. console `tag SOV`. Open console and run:

```
imgui show ai_templates
```

In the AI Templates window, find the `infantry` role. Expected: the currently-targeted template matches the rolled flag (e.g. if SOV rolled `MFU_inf_arty`, the targeted infantry template is 9 infantry + 6 artillery_brigade). Switch to a different country that rolled a different flag and confirm a different infantry template is targeted. This confirms both the flags (Task A) and the gating (Task B).

- [ ] **Step 9: Commit**

```bash
git add common/ai_templates/generic.txt
git commit -m "feat(ai): flag-gated infantry target templates (arty/at/aa/combined + default)"
```

---

### Task C: Tank target templates (role `armor`)

**Files:**
- Modify: `common/ai_templates/generic.txt` (the `armor_generic` block, currently lines ~42-182; also removes the duplicate `heavy_armor_default`)

**Interfaces:**
- Consumes: `MFU_tank_pure` / `MFU_tank_td` / `MFU_tank_ag` / `MFU_tank_combined` flags from Task A. The `td` variant references `medium_tank_destroyer_brigade`, whose equipment is designed in Task D.
- Produces: one active role-level `armor` entry holding a default + 4 flag-gated variants.

- [ ] **Step 1: Replace the `armor_generic` block**

Replace the entire existing `armor_generic = { … }` block (which contains the duplicated `heavy_armor_default`) with:

```
armor_generic = {

	role = armor

	upgrade_prio = {
		factor = 2

		modifier = {
			factor = 3
			OR = {
				has_tech = basic_medium_tank
				has_tech = basic_medium_tank_chassis
			}
		}
	}

	# Default fallback — always evaluated, lowest prio.
	armor_default = {
		upgrade_prio = { factor = 1 }
		target_template = {
			support = {
				mobile_engineer = 1
				maintenance_company = 1
				logistics_company = 1
				field_hospital = 1
				recon_ac = 1
			}
			regiments = {
				medium_armor = 7
				motorized = 4
				mechanized = 3
				armored_car = 1
			}
		}
	}

	# Pure armor — mostly tanks + mobile line.
	armor_pure = {
		enable = { has_country_flag = MFU_tank_pure }
		upgrade_prio = { factor = 10 }
		target_template = {
			support = {
				mobile_engineer = 1
				maintenance_company = 1
				logistics_company = 1
				field_hospital = 1
				recon_ac = 1
			}
			regimental_support = {
				anti_air = 1
			}
			regiments = {
				medium_armor = 6
				motorized = 5
				mechanized = 4
			}
		}
	}

	# Tank-destroyer emphasis — medium tanks + TD line.
	armor_td = {
		enable = { has_country_flag = MFU_tank_td }
		upgrade_prio = { factor = 10 }
		target_template = {
			support = {
				mobile_engineer = 1
				maintenance_company = 1
				logistics_company = 1
				field_hospital = 1
				recon_ac = 1
			}
			regimental_support = {
				anti_air = 1
			}
			regiments = {
				medium_armor = 5
				medium_tank_destroyer_brigade = 2
				motorized = 5
				mechanized = 3
			}
		}
	}

	# Assault-gun emphasis — medium tanks + SP-artillery line.
	armor_ag = {
		enable = { has_country_flag = MFU_tank_ag }
		upgrade_prio = { factor = 10 }
		target_template = {
			support = {
				mobile_engineer = 1
				maintenance_company = 1
				logistics_company = 1
				field_hospital = 1
				recon_ac = 1
			}
			regimental_support = {
				anti_air = 1
			}
			regiments = {
				medium_armor = 5
				light_sp_artillery_brigade = 2
				motorized = 5
				mechanized = 3
			}
		}
	}

	# Combined armor — tanks + TD + SP-artillery.
	armor_combined = {
		enable = { has_country_flag = MFU_tank_combined }
		upgrade_prio = { factor = 10 }
		target_template = {
			support = {
				mobile_engineer = 1
				maintenance_company = 1
				logistics_company = 1
				field_hospital = 1
				recon_ac = 1
			}
			regimental_support = {
				anti_air = 1
			}
			regiments = {
				medium_armor = 4
				medium_tank_destroyer_brigade = 1
				light_sp_artillery_brigade = 1
				motorized = 5
				mechanized = 4
			}
		}
	}
}
```

Width check: pure 6+5+4=15; td 5+2+5+3=15; ag 5+2+5+3=15; combined 4+1+1+5+4=15; default 7+4+3+1=15. Mobile org (mot+mech) = 9 / 8 / 8 / 9 — all in 7–11.

- [ ] **Step 2: Brace-balance sanity check**

```bash
o=$(grep -o "{" common/ai_templates/generic.txt | wc -l); c=$(grep -o "}" common/ai_templates/generic.txt | wc -l); echo "open=$o close=$c"
```

Expected: equal.

- [ ] **Step 3: Invalid-token scan**

```bash
grep -nE "\b(anti_tank|anti_air_brigade|modern_armor|light_tank_destroyer|modern_tank_destroyer_brigade)\b *=" common/ai_templates/generic.txt
```

Expected: no output.

- [ ] **Step 4: Load test**

Launch + fresh game. `logs/error.log` shows no invalid sub_unit lines for armor tokens.

- [ ] **Step 5: imgui verification**

Fresh game, pick a tank-building AI major. `imgui show ai_templates` → `armor` role. Confirm the targeted armor template matches the rolled `MFU_tank_*` flag (e.g. `MFU_tank_td` → template contains `medium_tank_destroyer_brigade 2`).

- [ ] **Step 6: Commit**

```bash
git add common/ai_templates/generic.txt
git commit -m "feat(ai): flag-gated armor target templates (pure/td/ag/combined + default)"
```

---

### Task D: Tank designs — style variety + tank-destroyer (per major)

**Scope (locked):** "Style variety + TD designs." For each of the four major tank files, add four style-gated **medium** tank design variants and one **tank-destroyer** design. Heavy tank designs are left as-is. Assault-gun / AA-tank equipment (used by Task C's `ag` templates) falls back to base-game auto-design.

**Files (do GER first as the reference implementation, then apply the same shape to the others):**
- Modify: `common/ai_equipment/GER_tank.txt`
- Modify: `common/ai_equipment/SOV_tank.txt`
- Modify: `common/ai_equipment/USA_tank.txt`
- Modify: `common/ai_equipment/ENG_tank.txt`

**Interfaces:**
- Consumes: `MFU_tankdesign_{mass,balanced,quality,fast}` flags from Task A; `MFU_tank_td`/`MFU_tank_combined` templates (Task C) that need TD equipment.
- Produces: designed medium-tank variants whose module loadout varies by style flag, and a `land_medium_tank_destroyer`-role design so the AI purpose-builds TD equipment.

**Mechanism:** `ai_equipment` blocks have **no `enable`** — only `priority = { factor … modifier … }`. A style variant therefore uses base `factor = 0` and a `modifier` that boosts it to a large factor only when its flag is set, so exactly the rolled style is chosen. `has_country_flag` is a valid country trigger inside `priority.modifier`.

- [ ] **Step 1 (GER): Read the current GER medium tank group**

```bash
grep -n "GER_medium_tanks\|GER_heavy_tanks\|improved_medium_tank\|advanced_medium_tank\|target_variant\|type = medium_tank" common/ai_equipment/GER_tank.txt
```

Note the `GER_medium_tanks = { … }` group boundaries and its existing medium variant(s) before editing.

- [ ] **Step 2 (GER): Replace the medium-tank variants with four style-gated variants**

Inside `GER_medium_tanks = { … }`, keep the group header (`category = land`, `blocked_for = {}`, `available_for = {GER}`, `roles = { land_medium_tank }`, group `priority = { factor = 2000 }`) and replace the existing medium variant blocks with these four. Chassis `medium_tank_chassis_1942` is the mid-war workhorse; modules are drawn from the confirmed slot/module tokens.

```
	# MASS: cheap gun, thin/unsloped armor, cheap engine.
	GER_medium_mass = {
		priority = {
			factor = 0
			modifier = { has_country_flag = MFU_tankdesign_mass  factor = 1000 }
		}
		target_variant = {
			match_value = 2500
			type = medium_tank_chassis_1942
			modules = {
				main_armament_slot = tank_medium_cannon_2
				turret_type_slot = tank_medium_three_man_tank_turret
				suspension_type_slot = tank_torsion_bar_suspension
				armor_type_slot = tank_riveted_armor
				armor_sloping_slot = unsloped_armor
				engine_type_slot = tank_gasoline_engine
				special_type_slot_1 = tank_radio_1
			}
			upgrades = { tank_nsb_engine_upgrade = 4  tank_nsb_armor_upgrade = 3 }
		}
		allowed_modules = {
			tank_medium_cannon_2 tank_medium_three_man_tank_turret tank_torsion_bar_suspension
			tank_riveted_armor tank_gasoline_engine tank_radio_1 unsloped_armor
		}
	}

	# BALANCED: middle-of-the-road.
	GER_medium_balanced = {
		priority = {
			factor = 1
			modifier = { has_country_flag = MFU_tankdesign_balanced  factor = 1000 }
		}
		target_variant = {
			match_value = 2500
			type = medium_tank_chassis_1942
			modules = {
				main_armament_slot = tank_high_velocity_cannon_2
				turret_type_slot = tank_medium_three_man_tank_turret
				suspension_type_slot = tank_torsion_bar_suspension
				armor_type_slot = tank_welded_armor
				armor_sloping_slot = unsloped_armor
				engine_type_slot = tank_gasoline_engine
				special_type_slot_1 = tank_radio_2
				special_type_slot_2 = basket
			}
			upgrades = { tank_nsb_engine_upgrade = 6  tank_nsb_armor_upgrade = 6 }
		}
		allowed_modules = {
			tank_high_velocity_cannon_2 tank_medium_three_man_tank_turret tank_torsion_bar_suspension
			tank_welded_armor tank_gasoline_engine tank_radio_2 unsloped_armor basket
		}
	}

	# QUALITY: big gun, thick sloped armor.
	GER_medium_quality = {
		priority = {
			factor = 0
			modifier = { has_country_flag = MFU_tankdesign_quality  factor = 1000 }
		}
		target_variant = {
			match_value = 2500
			type = medium_tank_chassis_1943
			modules = {
				main_armament_slot = tank_high_velocity_cannon_3
				turret_type_slot = tank_medium_advanced_three_man_tank_turret
				suspension_type_slot = tank_torsion_bar_suspension
				armor_type_slot = tank_welded_armor
				armor_sloping_slot = sloped_armor
				engine_type_slot = tank_gasoline_engine
				special_type_slot_1 = tank_radio_2
				special_type_slot_2 = basket
			}
			upgrades = { tank_nsb_engine_upgrade = 8  tank_nsb_armor_upgrade = 9 }
		}
		allowed_modules = {
			tank_high_velocity_cannon_3 tank_medium_advanced_three_man_tank_turret tank_torsion_bar_suspension
			tank_welded_armor tank_gasoline_engine tank_radio_2 sloped_armor basket
		}
	}

	# FAST: speed engine, lighter armor.
	GER_medium_fast = {
		priority = {
			factor = 0
			modifier = { has_country_flag = MFU_tankdesign_fast  factor = 1000 }
		}
		target_variant = {
			match_value = 2500
			type = medium_tank_chassis_1942
			modules = {
				main_armament_slot = tank_high_velocity_cannon_2
				turret_type_slot = tank_medium_three_man_tank_turret
				suspension_type_slot = tank_christie_suspension
				armor_type_slot = tank_welded_armor
				armor_sloping_slot = unsloped_armor
				engine_type_slot = tank_gasoline_engine
				special_type_slot_1 = tank_radio_2
			}
			upgrades = { tank_nsb_engine_upgrade = 9  tank_nsb_armor_upgrade = 4 }
		}
		allowed_modules = {
			tank_high_velocity_cannon_2 tank_medium_three_man_tank_turret tank_christie_suspension
			tank_welded_armor tank_gasoline_engine tank_radio_2 unsloped_armor
		}
	}
```

Note `GER_medium_balanced` has base `factor = 1` (not 0) so it is the fallback design when the game rule is OFF and no `MFU_tankdesign_*` flag is set.

- [ ] **Step 3 (GER): Add a tank-destroyer design group**

After `GER_medium_tanks = { … }` (a new top-level group), add:

```
GER_medium_tds = {
	category = land

	blocked_for = {}

	available_for = {GER}

	roles = {
		land_medium_tank_destroyer
	}

	priority = {
		factor = 200
	}

	GER_medium_td_default = {
		priority = {
			factor = 100
		}
		target_variant = {
			match_value = 2000
			type = medium_tank_chassis_1942
			modules = {
				main_armament_slot = tank_high_velocity_cannon_3
				turret_type_slot = tank_medium_casemate_turret
				suspension_type_slot = tank_torsion_bar_suspension
				armor_type_slot = tank_welded_armor
				armor_sloping_slot = sloped_armor
				engine_type_slot = tank_gasoline_engine
				special_type_slot_1 = tank_radio_2
			}
			upgrades = { tank_nsb_engine_upgrade = 6  tank_nsb_armor_upgrade = 6 }
		}
		allowed_modules = {
			tank_high_velocity_cannon_3 tank_medium_casemate_turret tank_torsion_bar_suspension
			tank_welded_armor tank_gasoline_engine tank_radio_2 sloped_armor
		}
	}
}
```

- [ ] **Step 4 (GER): Brace-balance + module-token sanity**

```bash
f=common/ai_equipment/GER_tank.txt; o=$(grep -o "{" "$f" | wc -l); c=$(grep -o "}" "$f" | wc -l); echo "$f open=$o close=$c"
```

Expected: equal. (Every module/slot/chassis token used above is confirmed present in the mod's tank files.)

- [ ] **Step 5 (GER): Load test**

Launch + fresh game as GER (or `tag GER`). `logs/error.log` shows no `Invalid module`/`unknown … slot`/`Unexpected token` lines for `GER_tank`. In-game, open the tank designer for GER: the medium and TD variants exist and are valid.

- [ ] **Step 6 (GER): imgui / designer verification**

Fresh game where GER rolled a known design flag. Console `tag GER`, open `imgui show ai_equipment` (or check the AI's designed medium tank in the production tab). Expected: the medium tank the AI fields matches the rolled style (e.g. `MFU_tankdesign_quality` → sloped armor + `tank_high_velocity_cannon_3` on the 1943 chassis). Confirm a TD variant is designed when GER also rolled `MFU_tank_td`/`MFU_tank_combined`.

- [ ] **Step 7 (GER): Commit**

```bash
git add common/ai_equipment/GER_tank.txt
git commit -m "feat(ai): GER style-gated medium tank designs + TD design"
```

- [ ] **Step 8 (SOV): Apply the same shape with SOV-flavored modules**

Repeat Steps 2–3 in `common/ai_equipment/SOV_tank.txt` under `SOV_medium_tanks` / new `SOV_medium_tds`, changing only: group `available_for = {SOV}`, variant name prefixes `SOV_medium_*`, and the nation-flavored modules — use `engine_type_slot = tank_diesel_engine`, `suspension_type_slot = tank_christie_suspension`, and `turret_type_slot = tank_medium_two_man_tank_turret` for mass / `tank_medium_advanced_three_man_tank_turret` for quality. Keep the same four style names, the same `priority`/`modifier` `has_country_flag` gating (balanced base `factor = 1`, others `0`), the same chassis years (`medium_tank_chassis_1942`/`1943`), and the same TD casemate pattern. Every module token used must appear in `allowed_modules`.

Full SOV block to insert (medium group body):

```
	SOV_medium_mass = {
		priority = { factor = 0  modifier = { has_country_flag = MFU_tankdesign_mass  factor = 1000 } }
		target_variant = {
			match_value = 2500  type = medium_tank_chassis_1942
			modules = {
				main_armament_slot = tank_medium_cannon_2
				turret_type_slot = tank_medium_two_man_tank_turret
				suspension_type_slot = tank_christie_suspension
				armor_type_slot = tank_riveted_armor
				armor_sloping_slot = sloped_armor
				engine_type_slot = tank_diesel_engine
				special_type_slot_1 = tank_radio_1
			}
			upgrades = { tank_nsb_engine_upgrade = 4  tank_nsb_armor_upgrade = 4 }
		}
		allowed_modules = { tank_medium_cannon_2 tank_medium_two_man_tank_turret tank_christie_suspension tank_riveted_armor tank_diesel_engine tank_radio_1 sloped_armor }
	}
	SOV_medium_balanced = {
		priority = { factor = 1  modifier = { has_country_flag = MFU_tankdesign_balanced  factor = 1000 } }
		target_variant = {
			match_value = 2500  type = medium_tank_chassis_1942
			modules = {
				main_armament_slot = tank_high_velocity_cannon_2
				turret_type_slot = tank_medium_three_man_tank_turret
				suspension_type_slot = tank_christie_suspension
				armor_type_slot = tank_welded_armor
				armor_sloping_slot = sloped_armor
				engine_type_slot = tank_diesel_engine
				special_type_slot_1 = tank_radio_2
			}
			upgrades = { tank_nsb_engine_upgrade = 6  tank_nsb_armor_upgrade = 6 }
		}
		allowed_modules = { tank_high_velocity_cannon_2 tank_medium_three_man_tank_turret tank_christie_suspension tank_welded_armor tank_diesel_engine tank_radio_2 sloped_armor }
	}
	SOV_medium_quality = {
		priority = { factor = 0  modifier = { has_country_flag = MFU_tankdesign_quality  factor = 1000 } }
		target_variant = {
			match_value = 2500  type = medium_tank_chassis_1943
			modules = {
				main_armament_slot = tank_high_velocity_cannon_3
				turret_type_slot = tank_medium_advanced_three_man_tank_turret
				suspension_type_slot = tank_christie_suspension
				armor_type_slot = tank_cast_armor
				armor_sloping_slot = sloped_armor
				engine_type_slot = tank_diesel_engine
				special_type_slot_1 = tank_radio_2
			}
			upgrades = { tank_nsb_engine_upgrade = 8  tank_nsb_armor_upgrade = 9 }
		}
		allowed_modules = { tank_high_velocity_cannon_3 tank_medium_advanced_three_man_tank_turret tank_christie_suspension tank_cast_armor tank_diesel_engine tank_radio_2 sloped_armor }
	}
	SOV_medium_fast = {
		priority = { factor = 0  modifier = { has_country_flag = MFU_tankdesign_fast  factor = 1000 } }
		target_variant = {
			match_value = 2500  type = medium_tank_chassis_1942
			modules = {
				main_armament_slot = tank_high_velocity_cannon_2
				turret_type_slot = tank_medium_three_man_tank_turret
				suspension_type_slot = tank_christie_suspension
				armor_type_slot = tank_welded_armor
				armor_sloping_slot = unsloped_armor
				engine_type_slot = tank_diesel_engine
				special_type_slot_1 = tank_radio_2
			}
			upgrades = { tank_nsb_engine_upgrade = 9  tank_nsb_armor_upgrade = 4 }
		}
		allowed_modules = { tank_high_velocity_cannon_2 tank_medium_three_man_tank_turret tank_christie_suspension tank_welded_armor tank_diesel_engine tank_radio_2 unsloped_armor }
	}
```

SOV TD group:

```
SOV_medium_tds = {
	category = land
	blocked_for = {}
	available_for = {SOV}
	roles = { land_medium_tank_destroyer }
	priority = { factor = 200 }
	SOV_medium_td_default = {
		priority = { factor = 100 }
		target_variant = {
			match_value = 2000  type = medium_tank_chassis_1942
			modules = {
				main_armament_slot = tank_high_velocity_cannon_3
				turret_type_slot = tank_medium_casemate_turret
				suspension_type_slot = tank_christie_suspension
				armor_type_slot = tank_cast_armor
				armor_sloping_slot = sloped_armor
				engine_type_slot = tank_diesel_engine
				special_type_slot_1 = tank_radio_2
			}
			upgrades = { tank_nsb_engine_upgrade = 6  tank_nsb_armor_upgrade = 6 }
		}
		allowed_modules = { tank_high_velocity_cannon_3 tank_medium_casemate_turret tank_christie_suspension tank_cast_armor tank_diesel_engine tank_radio_2 sloped_armor }
	}
}
```

Then run Steps 4–6 for SOV (brace check on `SOV_tank.txt`, load test as SOV, designer check). Commit:

```bash
git add common/ai_equipment/SOV_tank.txt
git commit -m "feat(ai): SOV style-gated medium tank designs + TD design"
```

- [ ] **Step 9 (USA): Apply the same shape with USA-flavored modules**

In `common/ai_equipment/USA_tank.txt` under `USA_medium_tanks` / new `USA_medium_tds`: `available_for = {USA}`, prefixes `USA_medium_*`. USA flavor: `armor_type_slot = tank_cast_armor`, `special_type_slot_2 = stabilizer` on quality, `turret_type_slot = tank_medium_casemate_turret` allowed on TD. Reuse the GER block verbatim but swap TAG, names, and these flavor modules; keep gasoline engine (`tank_gasoline_engine`), `tank_bogie_suspension` for balanced/fast. Every module in `allowed_modules`. Insert the four style variants (mass factor 0 / balanced factor 1 / quality 0 / fast 0, each with its `has_country_flag` modifier) and the `USA_medium_tds` group (role `land_medium_tank_destroyer`, casemate turret + `tank_high_velocity_cannon_3` + `tank_cast_armor`). Run Steps 4–6 for USA. Commit:

```bash
git add common/ai_equipment/USA_tank.txt
git commit -m "feat(ai): USA style-gated medium tank designs + TD design"
```

- [ ] **Step 10 (ENG): Apply the same shape with ENG-flavored modules**

In `common/ai_equipment/ENG_tank.txt` under `ENG_medium_tanks` / new `ENG_medium_tds`: `available_for = {ENG}`, prefixes `ENG_medium_*`. ENG flavor: `tank_riveted_armor` on mass, `tank_bogie_suspension`, gasoline engine; quality uses `tank_welded_armor` + `sloped_armor` + `tank_high_velocity_cannon_3`. Insert the four style variants (same factor/flag gating) and the `ENG_medium_tds` group (role `land_medium_tank_destroyer`, casemate turret). Run Steps 4–6 for ENG. Commit:

```bash
git add common/ai_equipment/ENG_tank.txt
git commit -m "feat(ai): ENG style-gated medium tank designs + TD design"
```

---

### Task E: Production overhaul — majors 40/30/30

**Scope:** For each major, steer ~**40% of military factories to air** via `air_factory_balance`, then split the remaining land factories ~**30% tank / 30% infantry** via `equipment_production_factor` (`armor` vs `infantry`) with `equipment_production_min_factories` floors. **Preserve** all construction/convoy steering.

**Files:**
- Modify: `common/ai_strategy/production_ai_strategies.txt` (GER/SOV/USA/ENG equipment-mix blocks only)
- Modify: `common/ai_strategy/JAP.txt`
- Modify: `common/ai_strategy/ITA.txt`
- Modify: `common/ai_strategy/FRA.txt`

**Interfaces:**
- Consumes: nothing from earlier tasks (independent). Complements Tasks C/D by making majors actually build tanks + air.
- Produces: adjusted `air_factory_balance` (→ 40) and armor/infantry `equipment_production_factor` weights per major.

**PRESERVE untouched (do NOT edit these blocks):** `GER_wants_civ`, `GER_wants_mils`, `GER_my_boy_speer`, `GER_autobahn`, `GER_industry_we_are_the_baddies`, `GER_wants_synth`, `no_more_supply_hubs`, `AI_build_convoys`, `AI_majors_build_convoys`, and all `*_naval_role_ratios_*` blocks.

- [ ] **Step 1: Locate the equipment-mix blocks**

```bash
grep -nE "air_factory_balance|equipment_production_factor id = (armor|infantry|fighter|cas)|_unit_production" common/ai_strategy/production_ai_strategies.txt
```

Confirm the `GER_unit_production` (~L956), `SOV_unit_production` (~L877), `USA_unit_production` (~L1029), and `ENG_unit_production*` (~L1) blocks and their current `air_factory_balance` values (25–35).

- [ ] **Step 2: GER — set air balance to 40 and rebalance armor/infantry**

In `GER_unit_production`, change the existing air line:

```
	ai_strategy = { type = air_factory_balance value = 35 }
```

to:

```
	ai_strategy = { type = air_factory_balance value = 40 }
```

and ensure the block contains these armor/infantry mix lines (add any that are missing; update values if present):

```
	ai_strategy = { type = equipment_production_factor id = armor value = 40 }
	ai_strategy = { type = equipment_production_factor id = infantry value = 40 }
	ai_strategy = { type = equipment_production_min_factories id = infantry value = 6 }
	ai_strategy = { type = equipment_production_min_factories id = fighter value = 20 }
```

(Equal armor/infantry factors split the ~60% non-air land pool ~30/30; the `fighter` floor holds the air share; existing fighter `equipment_production_factor` lines stay.)

- [ ] **Step 3: SOV — same pattern**

In `SOV_unit_production`, set `air_factory_balance value = 40` (from 35), and ensure:

```
	ai_strategy = { type = equipment_production_factor id = armor value = 40 }
	ai_strategy = { type = equipment_production_factor id = infantry value = 40 }
	ai_strategy = { type = equipment_production_min_factories id = infantry value = 6 }
	ai_strategy = { type = equipment_production_min_factories id = fighter value = 20 }
```

- [ ] **Step 4: USA — same pattern**

In `USA_unit_production`, set `air_factory_balance value = 40`, and ensure the four armor/infantry/floor lines above are present with the same values.

- [ ] **Step 5: ENG — same pattern**

ENG uses multiple time-gated blocks (`ENG_unit_production1/2/3`). Edit the **latest active** one (the one without an early `abort = { date > 1940… }`, i.e. `ENG_unit_production3`) to set `air_factory_balance value = 40` (add the line if absent) and the four armor/infantry/floor lines. Leave the early-war blocks' relative emphasis intact except for adding the air balance if they lack it.

- [ ] **Step 6: Brace-balance + preserve check**

```bash
f=common/ai_strategy/production_ai_strategies.txt; o=$(grep -o "{" "$f" | wc -l); c=$(grep -o "}" "$f" | wc -l); echo "open=$o close=$c"; echo "--- preserved blocks still present ---"; grep -cE "GER_wants_civ|GER_wants_mils|GER_autobahn|no_more_supply_hubs|AI_majors_build_convoys" "$f"
```

Expected: braces equal; preserved-block count = 5.

- [ ] **Step 7: JAP/ITA/FRA — apply in their own tag files**

In each of `common/ai_strategy/JAP.txt`, `ITA.txt`, `FRA.txt`, locate the production block(s) that hold `air_factory_balance` / `equipment_production_factor`:

```bash
grep -nE "air_factory_balance|equipment_production_factor id = (armor|infantry)|_unit_production|is_major" common/ai_strategy/JAP.txt common/ai_strategy/ITA.txt common/ai_strategy/FRA.txt
```

In each nation's main equipment-production block, set `air_factory_balance value = 40` and ensure the four armor/infantry/floor lines (values as in Step 2) are present. Do not touch construction/convoy/naval blocks.

- [ ] **Step 8: Load test**

Launch + fresh game. `logs/error.log` shows no `Unexpected token` / malformed `ai_strategy` lines in any of the four files.

- [ ] **Step 9: imgui verification (trend, not exact)**

Start a game, `tag GER`, run `imgui show ai_division_production` and check the production tab after fast-forwarding a few in-game months (or use `instant_prepare`/time-skip). Expected trend: military factories split roughly 40% aircraft, remainder split between armor and infantry equipment. Exact numbers are need-driven and clamped by available factories, so confirm the **direction** (air share rose toward ~40%, armor is a meaningful share), not precise percentages.

- [ ] **Step 10: Commit**

```bash
git add common/ai_strategy/production_ai_strategies.txt common/ai_strategy/JAP.txt common/ai_strategy/ITA.txt common/ai_strategy/FRA.txt
git commit -m "feat(ai): major-power production mix ~40/30/30 air/tank/inf; preserve construction steering"
```

---

## Final integration verification

- [ ] **V1 — Clean load:** Launch MFU, start a fresh game with `MFU_ai_variety = ON`. `logs/error.log` has no new lines referencing any token/block introduced by Tasks A–E.
- [ ] **V2 — Variety across games:** Start two fresh games. For the same AI major (e.g. SOV), `imgui show ai_templates` shows a **different** targeted infantry and/or armor template between the two games (flags rolled differently).
- [ ] **V3 — Width sanity:** In `imgui show ai_templates`, every targeted MFU template sums to ~30 combat width (15 line battalions).
- [ ] **V4 — Rule OFF safety:** Start a game with `MFU_ai_variety = OFF`. Confirm the AI still targets valid `infantry_default` / `armor_default` templates and fields the `balanced` tank design (no missing-template errors).
- [ ] **V5 — Regimental placement:** Confirm no template puts `anti_tank`/`anti_air`/pack-artillery in line `regiments`; they appear only under `regimental_support`.

---

## Self-review notes (author checklist, done)

- **Spec coverage:** A=spec §5A ✓; B=§5B ✓; C=§5C ✓; D=§5D (scoped to style + TD per locked decision) ✓; E=§5E (extended to JAP/ITA/FRA tag files — spec assumed all in one file) ✓.
- **Spec corrections baked in:** invalid tokens (`anti_tank`/`anti_air_brigade`/`modern_armor`/`light_tank_destroyer`/`modern_tank_destroyer_brigade`) removed; AT/AA/pack-arty forced to `regimental_support` per user instruction; ai_equipment gating is `priority`-modifier-based (no `enable` exists); tank family authored (TD role new); JAP/ITA/FRA production in their own files.
- **Type/token consistency:** flag names identical across A→D; chassis/module/slot tokens all confirmed present in the mod; regimental tokens (`anti_tank_brigade`, `anti_air`, `pack_artillery_brigade`) confirmed in `fire_support.txt`.
- **Open item to confirm in-engine (low risk):** the regimental-support per-division cap — each template uses only 1 regimental company, well under any cap; verify in V1 if any "too many support" warning appears.
