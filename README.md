# DAI - Smarter AI

**Make the AI play like it actually wants to win.**

DAI is a modular, fully dynamic AI overhaul for Hearts of Iron IV. Every decision the AI makes — what to research, what to produce, when to attack, when to stop — is driven by real-time evaluation of game state. No hardcoded country tags. No scripted date triggers. No nation-specific logic. The AI reads the board and reacts, just like a human player would.

The result: AI that builds supply infrastructure when it conquers territory, garrisons occupied land properly, stops attacking when it runs out of equipment, concentrates armour on weak sectors, and coordinates production, research, and diplomacy into a coherent strategy.

**Version:** 1.0.0 | **HOI4:** 1.17.4.1+ | **DLC Required:** None

---

## What changes in your game

- **AI builds supply infrastructure.** Railways, supply hubs, and infrastructure scale with logistics strain. No more offensives grinding to a halt because the AI forgot about supply.
- **Garrisons scale with occupation.** Germany garrisons France. Japan holds the Pacific. Garrison templates upgrade as territory grows. No more free resistance spirals.
- **AI stops ignoring its own crises.** Equipment critically low? Offensives halt automatically. Production shifts to infantry gear. Conscription laws upgrade. The AI addresses the problem instead of pretending it doesn't exist.
- **Strategic postures coordinate everything.** A single posture variable drives all four modules: Buildup, Defensive, Balanced, Offensive, Total War, and Survival. No more modules pulling in different directions.
- **Wars are harder.** Late-game AI is not early-game AI. Nations that industrialized are dangerous. Nations losing ground fight smarter, not dumber.
- **Anti-tank is reactive.** The AI detects enemy armour tech and boosts AT gun production and deploys AT-focused infantry templates in response.

---

## How it works

### Global Power Score

Every country gets a composite score from 0 to 100, recalculated monthly:

| Component | Weight | What it measures |
|---|---|---|
| Industry | 35% | Civilian + military factories, dockyards |
| Military | 30% | Fielded divisions, manpower, army experience |
| Technology | 20% | Researched techs relative to frontier |
| Strategic | 15% | Threat level, faction membership, war state |

The GPS maps to a competence scalar (0.7-1.4), then multiplied by the global intelligence preset to produce each nation's **effective intelligence**. Major powers play with higher effective intelligence than minors — a natural difficulty gradient.

### 22 Dynamic Variables

DAI tracks these variables per country, recalculated monthly:

| Variable | Range | Purpose |
|---|---|---|
| `dai_gps` | 0-100 | Global Power Score |
| `dai_competence` | 0.7-1.4 | Power-based competence scalar |
| `dai_effective_intelligence` | 0.35-2.8 | Final intelligence (preset x competence) |
| `dai_threat_index` | 0-100 | Threat from hostile neighbours |
| `dai_industry_score` | 0-100 | Industrial strength |
| `dai_military_score` | 0-100 | Military strength |
| `dai_tech_score` | 0-100 | Technology advancement |
| `dai_resource_need` | 0-1.0 | Resource starvation level |
| `dai_air_threat` | 0-1.0 | Enemy air superiority |
| `dai_naval_threat` | 0-1.0 | Enemy naval threat |
| `dai_manpower_ratio` | 0-1.0 | Manpower availability |
| `dai_equipment_ratio` | 0-1.0 | Equipment health (multi-signal estimation) |
| `dai_supply_strain` | 0-1.0 | Logistics stress |
| `dai_occupied_territory_size` | 0-100 | Occupied non-core territory |
| `dai_needs_override_active` | 0/1 | Critical needs failsafe flag |
| `dai_needs_priority` | 0-100 | Crisis urgency score |
| `dai_strategic_posture` | 0-5 | Strategic stance (Buildup to Survival) |
| `dai_enemy_armor_threat` | 0-1.0 | Enemy armoured force pressure |
| `dai_political_aggression` | -0.3-0.3 | Ideology aggression modifier |
| `dai_political_mil_priority` | -0.3-0.3 | Ideology military urgency |
| `dai_political_diplo_stance` | -0.3-0.3 | Ideology diplomatic modifier |
| `dai_political_doctrine_bias` | -0.3-0.3 | Ideology doctrine preference |

Every ai_strategy factor in the mod reads from these variables. The AI adapts because the variables change — not because someone wrote "Germany attacks Poland in 1939."

### Four Modules

Each module can be toggled independently via game rules:

- **Research** — 7 tech branches dynamically weighted. Industrial powers research tanks. Naval powers research ships. Posture-driven: survival mode prioritises infantry tech 2x.
- **Army** — 8 equipment categories, 6 construction types (including infrastructure, supply hubs, railways), adaptive division templates with progressive upgrading, reactive AT deployment, emergency production overrides.
- **Warfare** — 9-tier frontline cascade, armour concentration (Schwerpunkt), force massing, 7 theatre zones, naval invasion readiness scoring, posture-driven front allocation.
- **Grand Strategy** — threat-based diplomacy, posture-driven mobilisation, supply train scaling, conscription failsafe, strategic peace conferences.

### Strategic Posture System

A single variable coordinates all four modules:

| Posture | Triggers | Effect |
|---|---|---|
| **Buildup** (0) | At peace | Civilian factories 2.5x, industry research 1.5x |
| **Defensive** (1) | At war, weak military or low equipment | Garrison ratio 2x, armour ratio 0.5x, front allocation +40 |
| **Balanced** (2) | At war (default) | Standard wartime factors |
| **Offensive** (3) | High readiness + equipment | Armour ratio 2x, tank production 2x, armour research 1.3x |
| **Total War** (4) | High threat + aggressive ideology | Military factory 3x, military ratio +60 |
| **Survival** (5) | Surrender >30% or equipment <0.2 | Infantry production 4x, tanks 0.1x, infantry research 2x |

### Critical Needs Failsafe

When equipment drops below 30%, manpower below 15%, supply strain exceeds 70%, or surrender progress exceeds 20%, the failsafe activates:

- Offensives halt (needs crisis defense tier, priority 6000)
- Infantry equipment production jumps to 3x
- Tank and aircraft production suppressed to 0.1x-0.3x
- Military factory construction boosted to 4x
- Civilian factory construction suppressed to 0.1x
- Conscription law upgrades forced at priority 100

This prevents the AI from ignoring its own critical shortages — one of the most common complaints about HOI4 AI across all mods.

### Engine Define Overrides

DAI tunes 9 engine-level AI constants that scripts can't reach:

| Define | DAI Value | Effect |
|---|---|---|
| `GARRISON_FRACTION` | 0.08 | Stronger default garrisons |
| `FRONT_TERRAIN_ATTACK_FACTOR` | 0.3 | More cautious in bad terrain |
| `PLAN_VALUE_TO_EXECUTE` | 0.35 | Execute plans earlier when ready |
| `PLAN_ATTACK_DEPTH_FACTOR` | 0.8 | Don't overextend |
| `CONVOY_ESCORT_PRIORITY` | 1.5 | Protect convoys better |
| `NAVAL_MISSION_SPREAD_BASE` | 0.6 | Better naval coverage |
| `PRODUCTION_LINE_SWITCH_FACTOR` | 0.7 | Less penalty for switching lines |
| `EQUIPMENT_SURPLUS_FACTOR` | 0.3 | Use equipment, don't hoard it |
| `AIR_SUPERIORITY_IMPORTANCE` | 1.3 | Value air superiority more |

---

## Features

- 22 dynamic country variables driving all AI decisions
- 6-level strategic posture system coordinating all modules
- Critical needs failsafe preventing AI self-destruction
- Supply infrastructure construction (railways, supply hubs, infrastructure)
- Dynamic garrison scaling with occupied territory
- Reactive anti-tank production and template deployment
- 9-tier frontline cascade (emergency halt to pocket closure to full offensive)
- Naval invasion readiness scoring
- Engine define tuning (9 NAI constants)
- 5 intelligence presets (Casual 0.6x to Competitive 1.6x)
- 4 ideology behaviour profiles (fascist, communist, democratic, neutral)
- 4 compatibility profiles (Vanilla, Kaiserreich, TNO, BlackICE)
- Auto-detect mod profile at startup
- 19 game rules for full customisation
- Fully modular — any combination of 4 modules
- No country tags, no dates, no hardcoding
- No replace_path — fully additive
- Bucket-staggered evaluation — flat CPU load, no monthly lag spikes

---

## Game rules

| Rule | Default | Options |
|---|---|---|
| Compatibility Profile | Auto-Detect | Auto-Detect / Vanilla / Kaiserreich / TNO / BlackICE |
| Intelligence Preset | Balanced | Casual / Balanced / Historical / Realistic / Competitive |
| Research Module | Enabled | Enabled / Disabled |
| Army Module | Enabled | Enabled / Disabled |
| Warfare Module | Enabled | Enabled / Disabled |
| Grand Strategy Module | Enabled | Enabled / Disabled |
| AI Aggression | Normal | Passive / Cautious / Normal / Aggressive / Reckless |
| AI Naval Behaviour | Balanced | Passive / Defensive / Balanced / Aggressive |
| AI Diplomatic Stance | Dynamic | Isolationist / Cautious / Dynamic / Interventionist |
| AI Template Complexity | Standard | Simple / Standard / Advanced |
| AI Research Focus | Adaptive | Historical / Adaptive / Meta-optimal |
| Dynamic Power Scaling | On | On / Off |

---

## Mod compatibility

DAI ships with 4 built-in profiles that auto-detect your mod environment. No patches, no sub-mods, no load order issues.

| Profile | Status |
|---|---|
| **Vanilla** | Default, fully tested |
| **Kaiserreich** | Built-in, auto-detected |
| **The New Order** | Built-in, auto-detected |
| **BlackICE** | Built-in, auto-detected |

Each profile maps DAI's abstract categories (BRANCH_INFANTRY, ROLE_BREAKTHROUGH, EQUIP_FIGHTER, etc.) to that mod's specific tech categories, sub-unit types, and equipment archetypes. The build pipeline generates strategies for all profiles; at runtime, only the active profile fires.

---

## Load order

No hard dependencies. No replace_path. Works in any load order with any mod.

---

## For modders

### Build pipeline

DAI uses a Python/Jinja2 build system. YAML configs define AI behaviour; Jinja2 templates generate HOI4 script.

```bash
python build.py                    # Build with all profiles
python build.py --validate         # Build and validate output
python build.py --clean --validate # Clean first, then build and validate
```

### Source structure

| Directory | Purpose |
|---|---|
| `config/` | Core YAML config and engine define overrides |
| `config/modules/` | Per-module AI strategy definitions |
| `config/presets/` | Intelligence preset multipliers |
| `config/defines.yaml` | Engine-level NAI define overrides |
| `profiles/` | Mod compatibility profiles (Vanilla, Kaiserreich, TNO, BlackICE) |
| `generator/` | Python build pipeline (config loader, Jinja2 renderer, validator) |
| `generator/templates/` | Jinja2 templates for all generated files |
| `common/`, `events/`, `localisation/` | Generated HOI4 mod files |

### Adding a new profile

1. Create `profiles/yourmod.yaml` with tech categories, sub-units, equipment, and ideology mappings
2. Add `detection_hints` with a global flag your mod sets at startup
3. Run `python build.py --validate`
4. The new profile is automatically included in the build and selectable via game rules

### Debug

Enable debug mode via game rules. Trigger event `dai_core.100` from the console to get a full GPS readout for the selected country.
