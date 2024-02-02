NDefines.NGame.LAG_DAYS_FOR_LOWER_SPEED = 250
NDefines.NGame.LAG_DAYS_FOR_PAUSE = 200
NDefines.NGame.COMBAT_LOG_MAX_MONTHS = 36
NDefines.NCountry.EVENT_PROCESS_OFFSET = 25 -- Performance enhancer. --TW/WTT
NDefines.NGame.GAME_SPEED_SECONDS = { 600.0, 0.35 , 0.32, 0.29, 0.12 }
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