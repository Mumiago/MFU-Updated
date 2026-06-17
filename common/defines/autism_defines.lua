NDefines.NGame.LAG_DAYS_FOR_LOWER_SPEED = 250
NDefines.NGame.LAG_DAYS_FOR_PAUSE = 200
NDefines.NGame.COMBAT_LOG_MAX_MONTHS = 24
NDefines.NCountry.EVENT_PROCESS_OFFSET = 20 -- Performance enhancer. --TW/WTT
NDefines.NGame.GAME_SPEED_SECONDS = { 600.0, 0.26, 0.25, 0.19, 0.12}
---Diplomacy
NDefines.NDiplomacy.PEACE_SCORE_PER_PASS = 2.0
NDefines.NDiplomacy.DIPLOMACY_HOURS_BETWEEN_REQUESTS = 12
NDefines.NDiplomacy.GUARANTEE_COST = 12
NDefines.NDiplomacy.PEACE_SCORE_PER_PASS = 2.0
NDefines.NDiplomacy.TRUCE_PERIOD_AFTER_KICKING_FROM_FACTION = 0
NDefines.NDiplomacy.NUM_DAYS_TO_ENABLE_KICKING_NEW_MEMBERS_OF_FACTION = 0
NDefines.NDiplomacy.NUM_DAYS_TO_ENABLE_REINVITE_KICKED_NATIONS = 0

---AI
NDefines.NAI.DIPLOMACY_ACCEPT_ATTACHE_BASE = 100
NDefines.NAI.DIPLOMACY_ACCEPT_ATTACHE_OPINION_TRASHHOLD = 0
NDefines.NAI.DIPLOMACY_ACCEPT_ATTACHE_OPINION_PENALTY = 0
NDefines.NAI.GIVE_STATE_CONTROL_MIN_CONTROLLED = 0
NDefines.NAI.GIVE_STATE_CONTROL_MIN_CONTROL_DIFF = 0
---Graphics
NDefines_Graphics.NMapIcons.STRATEGIC_AIR_PRIORITY_AIR_MISSION = 290


--Graphics
NDefines_Graphics.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF = {300, 500, 1500}
NDefines_Graphics.NGraphics.VICTORY_POINTS_DISTANCE_CUTOFF = {300, 500, 1500}

--NDefines_Graphics.NGraphics.MAP_ICONS_GROUP_MAX_SIZE = 0
NDefines_Graphics.NGraphics.MAP_ICONS_STATE_GROUP_CAM_DISTANCE = 325.0		--group into states
NDefines_Graphics.NGraphics.MAP_ICONS_STRATEGIC_GROUP_CAM_DISTANCE = 400		--group units into air regions
NDefines_Graphics.NGraphics.MAP_ICONS_GROUP_SPLIT_SELECTED_LIMIT = 8
NDefines_Graphics.NGraphics.MAP_ICONS_COARSE_COUNTRY_GROUPING_DISTANCE = 200
NDefines_Graphics.NGraphics.MAP_ICONS_COARSE_COUNTRY_GROUPING_DISTANCE_STRATEGIC = 0
NDefines_Graphics.NGraphics.CAMERA_ZOOM_SPEED_DISTANCE_MULT = 20
NDefines_Graphics.NGraphics.AIRBASE_ICON_DISTANCE_CUTOFF = 900
NDefines_Graphics.NGraphics.NAVALBASE_ICON_DISTANCE_CUTOFF = 900
NDefines_Graphics.NGraphics.RESISTANCE_COLOR_GOOD = {0.0, 0.65, 0, 1}

NDefines.NCountry.INTERPOLATED_FRONT_STEPS_SHORT = 2				-- Performance optimization - The amount of steps for interpolated fronts. Non-AI countries got full interpolated fronts, the rest has optimized version of it.

NDefines_Graphics.NGraphics.CAPITAL_ICON_CUTOFF = 1000	-- At what camera distance capital icons disappears
NDefines_Graphics.NGraphics.NAVAL_MINES_DISTANCE_CUTOFF = 250
NDefines_Graphics.NGraphics.CRYPTOLOGY_MAP_ICON_DISTANCE_CUTOFF = 800
NDefines_Graphics.NGraphics.NAVAL_MINES_CLUMPING = 150 --The higher value, the more likely the 3d naval mines will clamp together
NDefines_Graphics.NGraphics.NAVAL_MINES_CLUMP_NEAR_TERRITORY = 60 -- Higher chance to spawn 3d naval mine near our territory
NDefines_Graphics.NGraphics.MAPICON_GROUP_PASSES = 10 -- how many mapicons get processed per frame for grouping. more = quicker response, fewer = better performance
NDefines_Graphics.NGraphics.WEATHER_DISTANCE_CUTOFF = 1000 -- At what distance weather effects are hidden

--- New defines added for HOI4 version update (vanilla values)
--- NMilitary
NDefines.NMilitary.CAPTAIN_EXPERIENCE_ON_SHIP_MULT = 1.55 -- XP multiplier a ship captain gains while serving aboard a ship
NDefines.NMilitary.MAX_CAPTAIN_EXPERIENCE_ON_SHIP = 8000 -- cap on experience a captain can accumulate from ship service
NDefines.NMilitary.CAPTAIN_EXPERIENCE_ON_SHIP_PER_MEDAL_MULT = 0.1 -- extra captain-XP multiplier per naval medal the captain holds
NDefines.NMilitary.MAX_REGIMENTAL_SUPPORT_WIDTH = 5 -- division designer: columns in the regimental-support slot grid
NDefines.NMilitary.MAX_REGIMENTAL_SUPPORT_HEIGHT = 1 -- division designer: rows in the regimental-support slot grid
NDefines.NMilitary.MAX_HQ_BATTALION_WIDTH = 4 -- Army HQ designer: columns in the HQ line-battalion grid
NDefines.NMilitary.MAX_HQ_BATTALION_HEIGHT = 4 -- Army HQ designer: rows in the HQ line-battalion grid (so up to 1x4 line battalions)
NDefines.NMilitary.MAX_HQ_SUPPORT_WIDTH = 1 -- Army HQ designer: columns in the HQ support-company grid
NDefines.NMilitary.MAX_HQ_SUPPORT_HEIGHT = 5 -- Army HQ designer: rows in the HQ support-company grid (so up to 1x4 support)
NDefines.NMilitary.MAX_HQ_REGIMENTAL_SUPPORT_WIDTH = 0 -- Army HQ designer: regimental-support columns (0 = HQs cannot take regimental support)
NDefines.NMilitary.MAX_HQ_REGIMENTAL_SUPPORT_HEIGHT = 0 -- Army HQ designer: regimental-support rows (0 = disabled for HQs)
NDefines.NMilitary.REGIMENTAL_SUPPORT_REQUIRED_BATTALIONS = { 3 } -- line battalions of a type required before its regimental-support slot unlocks
-- AI_BATTALION_BUILD_ORDER: grid-cell priority order the AI uses when filling division-designer battalion slots
NDefines.NMilitary.AI_BATTALION_BUILD_ORDER = { 	1,  6,  11, 16, 21,
												2,  7,  12, 17, 22,
												3,  8,  13, 18, 23,
												4,  9,  14, 19, 24,
												5,  10, 15, 20, 25 }
NDefines.NMilitary.REGIMENTAL_SUPPORT_SLOT_COST_MULTIPLIER = 1 -- production/equipment cost multiplier applied to units in regimental-support slots
NDefines.NMilitary.UNIT_LEADER_MODIFIER_COOLDOWN_ON_DEPLOY = 3 -- days an Army HQ's leader modifiers are on cooldown after first deploying
NDefines.NMilitary.UNIT_LEADER_MODIFIER_COOLDOWN_ON_DEPLOY_MIN = 7 -- minimum deploy cooldown in days regardless of manpower scaling
NDefines.NMilitary.UNIT_LEADER_MODIFIER_COOLDOWN_ON_REDEPLOY = 15 -- cooldown in days when an already-deployed HQ is moved/redeployed
NDefines.NMilitary.UNIT_LEADER_MODIFIER_COOLDOWN_ON_WITHDRAW = 14 -- cooldown in days applied when an HQ is withdrawn
NDefines.NMilitary.UNIT_LEADER_MODIFIER_COOLDOWN_ON_WITHDRAW_MIN = 14 -- minimum withdraw cooldown in days
NDefines.NMilitary.UNIT_LEADER_MODIFIER_COOLDOWN_REFERENCE_MANPOWER = 9600 -- reference HQ manpower used to scale the cooldown durations above
NDefines.NMilitary.UNIT_LEADER_MODIFIER_COOLDOWN_MANPOWER_EXPONENT = 1.5 -- exponent scaling cooldown length by HQ manpower relative to the reference
NDefines.NMilitary.FIGHTING_STRENGTH_DEATH_THRESHOLD = 0.001 -- fighting-strength fraction below which an HQ/unit is treated as destroyed
NDefines.NMilitary.FIGHTING_STRENGTH_HQ_ALERT_THRESHOLD = 0.2 -- HQ fighting-strength fraction below which the UI shows a low-strength alert
NDefines.NMilitary.COMMANDER_ABILITY_BASE_RANGE = 1 -- base range (provinces) of a commander/HQ ability's area of effect
NDefines.NMilitary.COMMS_MAX_DISTANCE = 4 -- max communication distance (hops from the Army HQ) before units count as out of comms
NDefines.NMilitary.PLANNING_CAP_COMMS_SCALING = { 1.3, 1, 0.6, 0.3, 0} -- max-planning multiplier indexed by comms distance (0..4 hops from HQ)
NDefines.NMilitary.PLANNING_CAP_NO_HQ_SCALING = 0 -- max-planning multiplier for units that have no Army HQ
NDefines.NMilitary.PLANNING_SPEED_COMMS_SCALING = { 1.3, 1, 0.6, 0.3, 0} -- planning-speed multiplier indexed by comms distance
NDefines.NMilitary.PLANNING_SPEED_NO_HQ_SCALING = 0 -- planning-speed multiplier for units with no Army HQ
NDefines.NMilitary.LEADER_MOD_COMMS_SCALING = { 1.3, 1, 0.6, 0.3, 0} -- HQ leader-modifier effectiveness multiplier by comms distance
NDefines.NMilitary.LEADER_MOD_NO_HQ_SCALING = 0 -- HQ leader-modifier effectiveness when no HQ
NDefines.NMilitary.ABILITY_COMMS_SCALING = { 1.3, 1, 0.6, 0.3, 0} -- HQ ability effectiveness multiplier by comms distance
NDefines.NMilitary.ABILITY_NO_HQ_SCALING = 0 -- HQ ability effectiveness when no HQ
NDefines.NMilitary.GENERAL_PROXIMITY_CLOSE = 1 -- proximity tier value: general/HQ is close to its units
NDefines.NMilitary.GENERAL_PROXIMITY_MEDIUM = 2 -- proximity tier value: medium distance
NDefines.NMilitary.GENERAL_PROXIMITY_FAR = 3 -- proximity tier value: far
NDefines.NMilitary.GENERAL_PROXIMITY_DEFAULT = 1 -- default proximity tier used when none is computed
NDefines.NMilitary.GENERAL_RANK_TO_ARMY_HQ_EXP_LEVEL_FACTOR = 1.5 -- converts a general's rank into the deployed Army HQ's starting experience level
NDefines.NMilitary.ARMY_HQ_REQUISITION_MINIMUM_REMAINING_PERCENTAGE = 1 -- min % of equipment kept in the stockpile when an HQ requisitions equipment
NDefines.NMilitary.PREFERRED_PRISON_VP = 5 -- victory-point weight used when choosing which state to hold captured generals in

--- NAI
NDefines.NAI.ARMY_LEADER_ASSIGN_WITHDRAW_DAYS = 7 -- AI: days to wait before withdrawing/reassigning an army leader's HQ
NDefines.NAI.ARMY_LEADER_MIN_DIVISIONS_FOR_HQ = 10 -- AI: minimum divisions in an army before the AI deploys an Army HQ for it
NDefines.NAI.MAX_DEPLOYED_ARMY_HQS = 5 -- AI: maximum number of Army HQs the AI keeps deployed at once
NDefines.NAI.MAX_CAPTURED_GENERALS_TO_STOP_HQ_DEPLOY = 3 -- AI: stops deploying new HQs once this many of its generals are captured

--- NNavy
NDefines.NNavy.NAVAL_COMBAT_MEDAL_CHANCE = 24 -- base chance/weight for a ship captain to be awarded a medal after a naval battle
NDefines.NNavy.NAVAL_COMBAT_MEDAL_MIN_DURATION = 48 -- minimum naval-combat duration (hours) required to be eligible for a medal
NDefines.NNavy.NAVAL_COMBAT_MEDAL_LAST_MEDAL_LIMIT = 30 -- minimum days since the captain's last medal before another can be awarded
NDefines.NNavy.NAVAL_COMBAT_MEDAL_ALLOW_CONVOY = false -- whether combat involving only convoys can award captain medals
