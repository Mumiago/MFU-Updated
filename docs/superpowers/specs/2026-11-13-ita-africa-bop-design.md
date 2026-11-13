# Italy: African state losses and Balance of Power (design, short)

Approved by the user on 2026-11-13 ("go").

## Intent
Losing Italian North Africa should hit Mussolini's position hard (20% per state), but it must be fully reversible: retaking a state gives back what it currently costs, so a loss followed by a retake always nets to zero. The North African focuses soften the penalty step by step, and Viva il Duce ends it. German factory output that the Italian focuses used to grant moves to Germany's own plunder line and to Speer.

## Rules
- States: Tunisia 458, Tripoli 448, El Agheila 449, Benghasi 450, Tobruk 451. Nothing else moves Italy's bar on capture (Egypt 446/447/452/456, Casablanca 461, Sicily 115, Sardinia 114 are dropped from the old ±5% rule).
- Loss: the Allies (ENG or its faction) take one of these states from the Axis (ITA, its subjects or faction, GER or its faction) while Italy has a balance of power and the state is not already marked lost. Italy shifts by minus the current rate toward the Grand Council; the state is marked lost.
- Retake: the Axis takes a state that is marked lost. Italy gets plus the current rate; the mark is cleared. Capturing a state that was never lost (e.g. Tunisia from France) does nothing.
- Rate: 20%. ITA_bend_the_bars or ITA_castello_di_sabbia: 15%. ITA_victory_in_the_desert: 10%. ITA_viva_il_duce: 0%.
- When the rate drops, every state currently marked lost refunds the difference (5% each for Bend/Castello and Victory, the whole remaining rate for Viva il Duce).
- Flat BoP: Castello and Victory keep their existing +10% (ITA_bop_low_increase_effect). Bend the Bars gets no flat bonus (its line stays commented out, by the user's choice).
- Grand Council total control (bar -1 to -0.9): its on_activate collapse is removed (no remove_power_balance, no -100% war support / stability). The range and its modifier stay.

## Germany
- Remove the `GER = { GER_elalamein_tt; +0.05 GER_arbeitseinsatz_industrial_capacity_factory }` block from Bend, Castello and Victory.
- Economy of Plunder levels 1-6 factory output 4/8/12/16/20/24% -> 6/11/17/23/28/34% (the extra 10% spread over the six plunder focuses; Fritz Todt still removes plunder).
- Speer's trait GERminister_of_armament_and_war_production: industrial_capacity_factory 0.20 -> 0.30. After Todt, Germany ends where it is today.

## Approaches considered
- Chosen: per-state flags plus rate tiers as country flags, in new MFU_ files; the old two blocks are removed from 00_on_actions.txt. Simple, exact, no variable-valued BoP effects (add_power_balance_value only documents a fixed value).
- Rejected: variable-valued rate (undocumented support for variables in add_power_balance_value); keeping the old symmetric ±rate on every capture (would reward first conquest of Tunisia, which the user ruled out).

## Builder's calls
- New files: common/on_actions/MFU_ITA_africa_bop_on_actions.txt, common/scripted_effects/MFU_ITA_africa_bop_effects.txt, common/scripted_triggers/MFU_ITA_africa_bop_triggers.txt, loc in localisation/english/MFU_ITA_africa_bop_l_english.yml.
- Short focus tooltips (the user dislikes blocks of text).
- Known edge: if the bar is already at an end, part of a loss can be eaten by the clamp and the retake refunds the full rate.
