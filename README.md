# DAI - Smarter AI

**The AI finally plays the game you're playing.**

DAI is a modular AI overhaul for Hearts of Iron IV that replaces the AI's broken decision-making with 40+ dynamic evaluation variables. No country scripts. No fixed dates. No tag-specific rails. The AI scores its own economy, military, technology, logistics, fuel, air threat, naval threat, invasion risk, casualties, stability, and political posture -- then makes decisions that actually make sense.

The result: fewer obviously suicidal offensives, proper coastal defense, fuel-aware production, real multi-front scaling, and late-game opponents that stay dangerous instead of collapsing into AI nonsense.

**Version:** 1.1.0
**Supported HOI4 Version:** `1.15+`
**DLC Required:** None

---

## What Changes In Game

- The AI builds and repairs its logistics network instead of stalling entire offensives on bad supply.
- Occupied land gets proper garrisons, scaling suppression, and stronger templates as empires expand.
- Equipment, manpower, and supply crises trigger emergency behavior instead of suicidal attacks.
- Frontline behavior is posture-driven, with offensive, defensive, and survival states coordinating all modules.
- Armor is concentrated on favorable sectors instead of being wasted uniformly across fronts.
- The AI reacts to enemy armor, air power, naval power, resistance pressure, and invasion risk.
- Puppets, faction leaders, island nations, landlocked nations, colonial empires, and multi-front powers now evaluate their situations differently instead of sharing one generic behavior model.

---

## Core Model

### Global Power Score

Each country gets a monthly composite score from industry, military, technology, and strategic position. That feeds a competence scalar, which is then combined with the chosen preset to produce each country's effective intelligence.

This creates natural scaling:

- majors make more coherent long-range decisions
- minors still behave sensibly without being scripted like majors
- the AI adapts to game state, not historical tags

### Dynamic Variables

DAI tracks a shared set of country-level variables used across all four modules. These include:

- power and competence: `dai_gps`, `dai_competence`, `dai_effective_intelligence`
- pressure signals: `dai_threat_index`, `dai_supply_strain`, `dai_resource_need`, `dai_manpower_ratio`, `dai_equipment_ratio`
- warfare signals: `dai_air_threat`, `dai_naval_threat`, `dai_enemy_armor_threat`, `dai_war_offensive_readiness`, `dai_war_defensive_priority`
- political and strategic signals: `dai_strategic_posture`, `dai_political_aggression`, `dai_political_mil_priority`, `dai_political_diplo_stance`
- occupation and coordination signals: `dai_occupied_territory_size`, `dai_faction_border_threat`, `dai_has_colonial_territory`, `dai_needs_override_active`

The system also evaluates:

- naval invasion defense and coastal threat response
- graduated air and naval threat scoring (multi-signal, not binary)
- puppet status and faction leader/member distinction
- fuel ratio, stability, war support, casualties, and resistance pressure
- coastal vs. landlocked logic and island nation posture
- multi-front enemy counting and front scaling
- capital threat, civil war, nuclear capability, and front stagnation detection

---

## Modules

DAI is split into four modules, each toggleable through game rules.

### Research

- 7 adaptive research branches
- weights react to war state, industry, threat, posture, and intelligence
- electronics and radar rise under air pressure
- naval research is suppressed for land powers and increased for maritime states

### Army

- adaptive division template progression
- reactive anti-tank and anti-air responses
- equipment production driven by stockpile pressure and battlefield conditions
- construction logic for civilian factories, military factories, dockyards, infrastructure, supply hubs, railways, synthetic refineries, radar stations, and air bases
- emergency air crisis response with fighter and AA production surges

### Warfare

- deep frontline control cascade with emergency halt, cautious defense, offensive push, and full offensive states
- armor steering toward weak or collapsing enemies
- front allocation, reserves, and theater demand scaling
- naval invasion readiness and air/naval production balancing
- coastal defense and naval invasion threat detection
- multi-front scaling based on active enemy count

### Grand Strategy

- threat-based war preparation
- ally-border defense logic
- lend-lease and volunteer behavior
- mobilization, economy law, conscription, PP, and XP spending priorities
- strategic peace conference weighting with annex, puppet, and liberate priorities
- puppet behavior suppression and faction leader/member distinction
- stability-aware and war-support-aware law management
- civil war focus and nuclear capability awareness

---

## Strategic Posture

One shared posture variable coordinates the entire mod:

- `Buildup`
- `Defensive`
- `Balanced`
- `Offensive`
- `Total War`
- `Survival`

This keeps research, construction, production, diplomacy, and frontline behavior aligned instead of letting separate subsystems fight each other.

---

## Crisis Handling

DAI includes a critical-needs failsafe. When equipment, manpower, surrender progress, supply, fuel, or comparable strategic pressure crosses danger thresholds, the AI shifts into damage-control behavior:

- offensive plans are suppressed
- infantry and support production rises
- luxury production is reduced
- military construction and law pressure increase
- defensive allocation and reserve logic take priority

This is one of the main differences from vanilla-style AI behavior, where countries often continue attacking straight through an obvious collapse.

---

## Features

- Dynamic AI with no country tags, no scripted dates, and no replace-path design
- 4 independently toggleable modules
- Global Power Score and competence scaling
- 6-level strategic posture system
- Adaptive research weighting across 7 branches
- Adaptive production across infantry, support, artillery, AT, AA, motorized, armor, fighters, and CAS
- Supply-aware construction for infrastructure, railways, and supply hubs
- Occupation-aware garrison logic and colonial defense support
- Frontline control cascade with readiness gating and emergency shutdowns
- Armor concentration and theater priority control
- Reactive anti-tank, anti-air, and air-defense behavior
- Dynamic naval and invasion planning
- Expanded threat model including coastal, air, naval, fuel, casualty, resistance, and capital pressure
- Better differentiation for puppets, faction leaders, members, island states, colonial powers, and landlocked nations
- Strategic peace conference behavior including annex, puppet, and liberate priorities
- Engine define tuning beyond what script-only AI mods can change
- Bucketed evaluation scheduling to avoid monthly CPU spikes

---

## Game Rules

The current workspace exposes 13 rule groups:

- Compatibility Profile
- Intelligence Preset
- Army Module
- Grand Strategy Module
- Research Module
- Warfare Module
- AI Aggression
- AI Research Focus
- AI Template Complexity
- AI Naval Behaviour
- AI Diplomatic Stance
- Dynamic Power Scaling
- Recalculation Frequency

Presets include `Casual`, `Balanced`, `Historical`, `Realistic`, and `Competitive`.

---

## Compatibility

DAI is fully additive and does not rely on `replace_path`.

Included profiles:

- Vanilla
- BlackICE
- Kaiserreich
- Millennium Dawn
- Road to 56
- The Fire Rises
- The New Order

Auto-detect and manual profile selection are both supported depending on the environment and game-rule choice.

Not intended to be stacked with other full AI overhauls.

---

## For Modders

DAI uses a Python + Jinja build pipeline.

```bash
python build.py
python build.py --validate
python build.py --clean --validate
```

Relevant source layout:

- `config/` for module configs, presets, and define tuning
- `profiles/` for compatibility mappings
- `generator/` and `generator/templates/` for the build pipeline
- `common/`, `events/`, and `localisation/` for generated game content

Debug output is available through the core debug event:

```txt
event dai_core.100
```
