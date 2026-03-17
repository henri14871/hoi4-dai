# DAI - Smarter AI: Design Document v1.1

> **DAI** = Dynamic AI (internal name). **"Smarter AI"** is the Steam Workshop tagline.
> Author: Henri | March 2026 | Confidential — Internal Design Reference

---

## 1. Vision and Brand Identity

### Mission Statement

DAI — Dynamic AI — is a modular, fully dynamic AI overhaul for Hearts of Iron IV, published on the Steam Workshop as **DAI - Smarter AI**. Its goal is to make the AI a genuinely competent opponent that evaluates game state in real time, adapts to any mod environment, and provides players with a challenging, believable experience — whether playing vanilla, Kaiserreich, The New Order, or any community overhaul.

Every AI decision is driven by evaluated game state. Nothing is hardcoded. No country tags, no static date triggers, no scripted nation-specific behaviour. The AI reads the board and reacts, just like a human player would.

### Brand Structure

DAI ships as a **single mod** on the Steam Workshop. All functionality is included out of the box, with individual modules toggled on or off via game rules before each campaign. This means one subscription, one Workshop page, one place for ratings and feedback, and zero dependency headaches.

The four modules within the single mod are:

- **Research module** — dynamic technology prioritisation and research slot management
- **Army module** — adaptive division templates, intelligent production, and factory allocation
- **Warfare module** — front strategy, offensive planning, naval operations, and air wing management
- **Grand Strategy module** — diplomacy, faction logic, trade, economic laws, and mobilisation

The core framework (GPS engine, shared variables, game rules) is always active when DAI is enabled. Players can then enable any combination of the four modules via game rules.

### Design Principles

- **Fully dynamic** — all decisions derive from evaluated game state via triggers and factors, never from hardcoded country tags or static conditions.
- **Universally compatible** — works with any total conversion or overhaul mod without patches, because the system never references vanilla-specific content.
- **Modular** — every module can be toggled on or off via game rules. Players choose exactly what they want before each campaign.
- **Configurable** — extensive game rules let players tune AI intelligence, aggressiveness, and behaviour before each campaign.
- **Transparent** — clear documentation and in-game tooltips explain what the AI is doing and why, so players understand the system and modders can extend it.

---

## 2. AI Intelligence System

### Overview

The intelligence system determines how effectively the AI plays. It uses a two-layer approach: **global presets** set the baseline intelligence level for all nations, while a **dynamic country power scalar** adjusts individual nation competence based on their in-game standing. The preset acts as a multiplier on top of the power-based scaling, giving players full control.

### Global Presets

Players select a global preset via game rules before starting a campaign. Each preset defines a base multiplier that affects how aggressively the AI optimises its decisions across all modules.

| Preset | Multiplier | Description |
|--------|-----------|-------------|
| Casual | 0.6x | AI makes reasonable but suboptimal decisions. Good for narrative or roleplay campaigns. |
| Balanced | 1.0x | Default. AI plays competently across all areas. Suitable for most players. |
| Historical | 1.2x | AI follows historically plausible behaviour for the active mod. Biases are defined by the compatibility profile. |
| Realistic | 1.3x | AI plays with near-optimal efficiency. Major powers are formidable, minor nations are scrappy. |
| Competitive | 1.6x | AI plays to win. Aggressive optimisation across all modules. For experienced players. |
| Custom | User-set | Unlocks additional game rules for per-module tuning of every parameter. |

#### The Historical Preset

The Historical preset is the only preset that reads from the compatibility profile. It applies **soft biases** that nudge nations toward historically plausible behaviour without forcing outcomes. What "historical" means is entirely defined by the active profile:

- **Vanilla profile:** Germany biases toward armour research and Mobile Warfare doctrine. UK biases toward naval and air. USSR biases toward mass industry early, then military pivot. USA biases toward late mobilisation but massive production once at war. Japan biases toward naval and carrier aviation.
- **Kaiserreich profile:** historical means the Kaiserreich timeline — Germany maintains its empire, the Commune of France biases toward revolution and militarisation, the Entente biases toward reconquest.
- **TNO profile:** historical means Cold War dynamics — superpowers bias toward proxy conflicts, nuclear deterrence shapes diplomatic aggression thresholds.
- **Any overhaul mod:** the profile defines what "historical" means for that mod's setting and timeline.

These biases are implemented as additional ai_strategy factor modifiers gated behind the Historical preset game rule. They do not override the dynamic system — they layer on top of it. If conditions diverge from the historical path (e.g., Germany loses early, or the player creates an ahistorical situation), the dynamic system takes over and the historical biases fade in influence because the game state no longer supports them.

If no profile is loaded or the active profile has no historical section, the Historical preset falls back to Realistic behaviour — the biases simply don't apply and the AI plays dynamically at the 1.2x multiplier.

### The Multiplier Affects

- **Research efficiency** — how quickly the AI identifies and pivots to optimal tech paths
- **Template quality** — how close to meta-optimal the AI's division designs are
- **Production responsiveness** — how fast the AI rebalances factories when needs change
- **Strategic decision-making** — how well the AI reads the front and times offensives
- **Naval and air competence** — how effectively the AI composes and deploys fleets and air wings
- **Diplomatic acumen** — how shrewdly the AI handles alliances, guarantees, and peace deals

### Dynamic Country Power Scalar

Within any preset, individual nations receive a competence scalar based on their **Global Power Score (GPS)** — a composite metric calculated by the Core framework. This ensures that major powers play with higher effective intelligence than minor nations, creating a natural difficulty gradient that mirrors real geopolitics.

#### Global Power Score Formula

The GPS is a normalised score from 0 to 100, recalculated periodically (default: every 30 days). It evaluates:

- **Industrial base** (35%) — civilian and military factory count, dockyard count, resource access
- **Military strength** (30%) — fielded divisions, equipment stockpile, manpower reserves, army experience
- **Technology level** (20%) — number of researched techs relative to year, ahead-of-time penalties absorbed
- **Strategic position** (15%) — faction membership, border threat level, alliance strength, war participation

All inputs are read dynamically via scripted triggers. No country tags or year checks are used.

#### Power-to-Competence Mapping

The GPS maps to a competence scalar between 0.7 and 1.4, then multiplied by the global preset to produce the **effective intelligence** for that nation.

| GPS Range | Competence Scalar | Typical Nations (vanilla example) |
|-----------|------------------|----------------------------------|
| 80–100 | 1.3–1.4 | USA, Germany, USSR, UK, Japan |
| 60–79 | 1.1–1.2 | Italy, France, China |
| 40–59 | 1.0 | Spain, Turkey, Brazil, Poland |
| 20–39 | 0.85–0.95 | Romania, Hungary, Siam |
| 0–19 | 0.7–0.8 | Luxembourg, Bhutan, Liberia |

**Example:** On Competitive (1.6x), Germany at GPS 85 gets competence 1.35, producing effective intelligence of 1.6 × 1.35 = **2.16x**. Luxembourg on the same preset at GPS 8 gets 1.6 × 0.72 = **1.15x**. This creates a believable spread where great powers are terrifyingly efficient while minor nations still play reasonably.

The GPS is recalculated throughout the game. A nation that industrialises rapidly will see its competence rise dynamically. A nation that loses territory and factories will see it fall. The AI naturally adapts to alternate history scenarios without scripting.

#### Effective Intelligence Application

The effective intelligence value is passed to each module as a variable. Modules use it to scale the precision of their factor weights. At higher intelligence, the AI makes tighter, more optimal decisions. At lower intelligence, the AI still makes reasonable decisions but with more variance — it might over-invest in one tech path, field slightly suboptimal templates, or commit to an offensive prematurely. This variance is the mechanism, not randomness.

### Political Status Modifiers

A nation's ideology and political status affects how it behaves — not just how smart it is, but what it prioritises. A fascist dictatorship should be more aggressive and militaristic than a stable democracy. DAI evaluates the ruling ideology using `has_government` triggers (which work in vanilla and all overhaul mods that use the base ideology system) and applies behavioural modifiers on top of the intelligence system.

#### Ideology Behaviour Profiles

| Ideology | Aggression Modifier | Strategy Bias | Economic Bias | Diplomatic Bias |
|----------|-------------------|---------------|---------------|-----------------|
| Fascism | +30% aggression | Offensive-first. Commits to attacks at lower force ratios. Prioritises breakthrough divisions and CAS. | Early mobilisation. Rushes military factories and military economy laws. | Interventionist. Eager to form factions, justify wars, and expand. Reluctant to make peace without significant gains. |
| Communism | +15% aggression | Defensive preparation, then offensive. Builds large armies with emphasis on quantity over quality. Strong garrison priority. | Heavy industry focus. Prioritises civilian factories early for industrial snowball, then pivots hard to military. | Bloc-oriented. Eager to spread ideology and support aligned nations via lend-lease and volunteers. Cautious about direct war unless confident. |
| Democracy | -15% aggression | Defensive posture until provoked. High offensive threshold — only attacks with strong force ratios. Prioritises air and naval superiority. | Late mobilisation. Maintains civilian economy longer. Invests in electronics and industry tech. | Alliance-focused. Guarantees threatened nations, builds coalitions. Reluctant to declare war but commits fully once at war. |
| Neutrality / Non-aligned | 0% (baseline) | Balanced, reactive. Adapts strategy to threats rather than pursuing an agenda. | Moderate mobilisation timing based purely on threat level. | Isolationist by default. Joins factions only when directly threatened. Avoids guarantees unless bordered by aggressor. |

#### How It Works Technically

The core evaluation event checks the country's ruling ideology and stores a set of political modifier variables:

- `dai_political_aggression` — a modifier from -0.3 to +0.3 applied to all aggression-related ai_strategy factors (war declarations, offensive thresholds, invasion willingness)
- `dai_political_mil_priority` — scales military factory construction and mobilisation urgency. Fascist nations build military earlier; democracies delay.
- `dai_political_diplo_stance` — scales diplomatic AI weights (faction creation, guarantee willingness, lend-lease generosity). Democracies are alliance-builders; fascists are expansionists.
- `dai_political_doctrine_bias` — nudges doctrine research choice based on ideology. Not a hard lock — just a weighted preference that the AI can override based on circumstances.

#### Ideology Shifts

Because these modifiers are recalculated during the monthly GPS sweep, they automatically adapt to ideology changes mid-game. A nation that flips from democracy to fascism via civil war or focus tree will see its AI behaviour shift accordingly — more aggressive, earlier mobilisation, more willing to declare wars.

#### Overhaul Mod Compatibility

Vanilla HOI4 uses four base ideologies: fascism, communism, democratic, neutrality. Most overhaul mods keep these as the base categories even when adding sub-ideologies. The `has_government` trigger works with whatever ideologies the mod defines. For mods that add entirely custom ideologies (e.g., TNO's multiple authoritarian sub-types), the profile system maps custom ideologies to DAI's abstract political categories (aggressive, moderate, defensive, neutral) so the behaviour profiles still apply.

### Strategic Posture System

The strategic posture system coordinates behaviour across all four modules simultaneously via a single variable (`dai_strategic_posture`). Rather than each module independently evaluating game state, the posture provides a unified strategic stance that drives production, research, warfare, and diplomacy in the same direction.

#### Posture Levels

| Posture | Value | Trigger Conditions | Effect Across Modules |
|---------|-------|-------------------|----------------------|
| **Buildup** | 0 | At peace (default) | Civilian factory priority 2.5x, industry research 1.5x, low military ratio |
| **Defensive** | 1 | At war with weak military or low equipment | Garrison ratio 2x, front allocation +40, armour ratio 0.5x, tank production suppressed |
| **Balanced** | 2 | At war (default wartime) | Standard wartime factors apply normally |
| **Offensive** | 3 | At war with high readiness (>65) and equipment (>0.6) | Armour ratio 2x, tank production 2x, front allocation +20, armour/air research 1.3x |
| **Total War** | 4 | At war with very high threat (>70) and aggressive ideology | Military factory 3x, military-to-civilian ratio +60, armour/air research 1.3x |
| **Survival** | 5 | Surrender progress >30% OR equipment ratio <0.2 at war | Infantry production 4x, tank production 0.1x, infantry research 2x, all luxury suppressed |

Postures are determined by a priority cascade — the highest-matching condition wins. The posture is recalculated monthly alongside the GPS evaluation. Because it's a single variable consumed by factor modifiers across all modules, there is no risk of modules pulling in conflicting directions.

#### Relationship to Needs Failsafe

The needs failsafe system (`dai_needs_override_active`) operates independently of posture and can activate at any posture level. When active, it overrides production priorities and halts offensives regardless of the current posture. The failsafe handles acute crises; posture handles strategic direction.

---

## 3. Game Rules and Customisation

### Game Rules (Pre-Game)

DAI adds the following options to the HOI4 game rules screen. These are split into three groups: the compatibility profile selector, module toggles that control which parts of DAI are active, and behaviour settings that tune how the AI plays.

#### Compatibility Profile

| Rule | Options | Default | Effect |
|------|---------|---------|--------|
| Compatibility Profile | Auto-Detect / Vanilla / Kaiserreich / TNO / BlackICE / ... | Auto-Detect | Selects which mod's content IDs are used for AI strategies. Auto-Detect checks at startup which mod is loaded. Manual options override detection. |

When set to Auto-Detect, DAI checks for mod-specific content at startup using detection hints defined in each profile YAML. The first matching profile wins; if none match, vanilla is the fallback. Players can manually override if auto-detection fails.

#### Module Toggles

| Rule | Options | Default | Effect |
|------|---------|---------|--------|
| DAI: Research | Enabled / Disabled | Enabled | Toggles the Research module (dynamic tech priorities) |
| DAI: Army | Enabled / Disabled | Enabled | Toggles the Army module (templates + production) |
| DAI: Warfare | Enabled / Disabled | Enabled | Toggles the Warfare module (strategy + naval + air) |
| DAI: Grand Strategy | Enabled / Disabled | Enabled | Toggles the Grand Strategy module (diplomacy + economy) |

When a module is disabled, all of its ai_strategy factors are gated behind a scripted trigger that checks the module's game rule variable. Disabled modules have zero performance cost — their triggers are never evaluated because the gate check fails immediately.

#### Behaviour Settings

| Rule | Options | Default | Effect |
|------|---------|---------|--------|
| AI intelligence preset | Casual / Balanced / Historical / Realistic / Competitive / Custom | Balanced | Sets the global intelligence multiplier. Historical reads biases from the active compatibility profile. |
| AI aggression | Passive / Cautious / Normal / Aggressive / Reckless | Normal | Scales offensive commitment and war declarations |
| AI research focus | Historical / Adaptive / Meta-optimal | Adaptive | Controls research pattern behaviour |
| AI template complexity | Simple / Standard / Advanced | Standard | Limits division design complexity |
| AI naval behaviour | Passive / Defensive / Balanced / Aggressive | Balanced | Controls fleet posture |
| AI diplomatic stance | Isolationist / Cautious / Dynamic / Interventionist | Dynamic | Scales faction and alliance behaviour |
| Dynamic power scaling | On / Off | On | Toggles GPS-based country competence |
| Recalculation frequency | Monthly / Bi-monthly / Quarterly | Monthly | How often GPS and weights recalculate |

### Extended Game Rules (Custom Preset)

When the Custom preset is selected, additional game rules become available, organised by module:

- **Research rules** — tech branch weight bias (industry, infantry, armour, naval, air, electronics, doctrine), ahead-of-time willingness (conservative / moderate / aggressive)
- **Army rules** — maximum division width cap (20w / 30w / 40w / uncapped), support company limit (2 / 3 / 5 / unlimited), equipment stockpile target (low / medium / high), factory rebalance sensitivity (slow / normal / fast)
- **Warfare rules** — offensive threshold (cautious / normal / bold / reckless), garrison priority (minimal / standard / heavy), naval invasion willingness (never / reluctant / normal / eager), air superiority vs. CAS priority (fighter focus / balanced / CAS focus)
- **Grand Strategy rules** — faction creation willingness (reluctant / normal / eager), peace deal behaviour (conservative / balanced / greedy), mobilisation timing (late / adaptive / early), trade aggressiveness (passive / balanced / aggressive)

### Per-Nation Overrides

Advanced users can override the intelligence multiplier for specific nations through dedicated game rules. This allows scenarios like setting the USSR to Competitive while keeping everyone else on Balanced. Per-nation overrides are stored as country variables and take precedence over the GPS scalar.

### Ironman Compatibility

All configuration uses the official game_rules system, making it fully Ironman-compatible. Achievements are disabled when any DAI module is active, as with all mods that modify AI behaviour.

---

## 4. Core Framework Specification

### Purpose

The core framework is the always-active foundation of DAI. It provides the scoring engine, global variables, game rules, and event hooks that all modules depend on. When DAI is enabled but all modules are toggled off, only the core runs — calculating GPS scores with no AI behaviour changes.

### Global Power Score Engine

The GPS engine runs as a country-scoped on_action triggered every N days (configurable, default 30). For each country, it:

- Evaluates industrial, military, technological, and strategic factors using only scripted triggers and variable checks
- Normalises the result to a 0–100 scale using a softmax function to prevent outlier distortion
- Stores the result as a country variable (`dai_gps`) readable by all modules
- Computes the competence scalar and stores it as `dai_competence`
- Multiplies competence by the global preset multiplier and stores as `dai_effective_intelligence`

### Shared Variables

Core defines a standard set of country-scoped variables that modules read, recalculated alongside the GPS:

| Variable | Type | Description |
|----------|------|-------------|
| `dai_gps` | 0–100 | Global Power Score |
| `dai_competence` | 0.7–1.4 | Power-based competence scalar |
| `dai_effective_intelligence` | 0.35–2.8 | Final intelligence (preset × competence) |
| `dai_threat_index` | 0–100 | How threatened this nation is by hostile neighbours |
| `dai_industry_score` | 0–100 | Industrial strength sub-score |
| `dai_military_score` | 0–100 | Military strength sub-score |
| `dai_tech_score` | 0–100 | Technological advancement sub-score |
| `dai_resource_need` | 0–1.0 | How resource-starved the nation is (1.0 = critical shortage) |
| `dai_air_threat` | 0–1.0 | Intensity of enemy air superiority in owned states |
| `dai_naval_threat` | 0–1.0 | Threat from enemy naval forces to convoys and coastline |
| `dai_manpower_ratio` | 0–1.0 | Available manpower relative to fielded army needs |
| `dai_equipment_ratio` | 0–1.0 | Equipment stockpile health relative to fielded divisions |
| `dai_political_aggression` | -0.3–0.3 | Ideology-based aggression modifier |
| `dai_political_mil_priority` | float | Ideology-based military construction urgency |
| `dai_political_diplo_stance` | float | Ideology-based diplomatic behaviour modifier |
| `dai_political_doctrine_bias` | float | Ideology-based doctrine preference |
| `dai_supply_strain` | 0–1.0 | Logistics stress level (division count, overextension) |
| `dai_occupied_territory_size` | 0–100 | Scale of occupied non-core territory |
| `dai_needs_override_active` | 0 or 1 | Critical needs failsafe flag (1 = crisis mode) |
| `dai_needs_priority` | 0–100 | Urgency score from equipment, manpower, supply, and surrender crises |
| `dai_strategic_posture` | 0–5 | Coordinated strategic stance (0=Buildup, 1=Defensive, 2=Balanced, 3=Offensive, 4=Total War, 5=Survival) |
| `dai_enemy_armor_threat` | 0–1.0 | Enemy armoured force pressure (detected via enemy tech level) |

### Scripted Triggers Library

Core provides reusable scripted triggers that modules reference:

- `dai_is_major_power` — true if GPS > 60
- `dai_is_at_war` — true if has_war = yes
- `dai_needs_armour` — true if front terrain and enemy composition favour armoured divisions
- `dai_needs_fighters` — true if air_threat > 0.4 and current fighter stockpile is low
- `dai_industry_growing` — true if factory count increased since last evaluation
- `dai_losing_war` — true if war_score is declining and territory has been lost
- `dai_research_enabled` — true if Research module game rule is enabled
- `dai_army_enabled` — true if Army module game rule is enabled
- `dai_warfare_enabled` — true if Warfare module game rule is enabled
- `dai_gs_enabled` — true if Grand Strategy module game rule is enabled
- `dai_posture_buildup` — true if strategic posture is Buildup (peacetime growth)
- `dai_posture_defensive` — true if strategic posture is Defensive
- `dai_posture_balanced` — true if strategic posture is Balanced (default wartime)
- `dai_posture_offensive` — true if strategic posture is Offensive
- `dai_posture_total_war` — true if strategic posture is Total War
- `dai_posture_survival` — true if strategic posture is Survival (nation collapsing)
- `dai_needs_crisis_active` — true if the critical needs override is engaged
- `dai_war_needs_more_garrison` — true if garrison allocation should increase (occupied territory or high threat)
- `dai_war_garrison_emergency` — true if garrison needs are extreme

All triggers evaluate dynamically. None reference country tags, dates, or hardcoded values.

### Event Hooks

Core registers lightweight on_action hooks that modules subscribe to:

- `dai_monthly_evaluation` — fires after GPS recalculation; modules update their own weights
- `dai_war_declared` — fires on any war declaration; Warfare and Grand Strategy re-evaluate
- `dai_peace_signed` — fires after any peace conference; triggers economic and diplomatic re-evaluation
- `dai_tech_completed` — fires when AI completes research; Army module checks for new equipment

---

## 5. Module Specifications

### DAI: Research

Replaces the AI's default research weighting with a dynamic evaluation system. Built on the Arms Race Mechanics foundation, this module makes the AI research like a competent player — identifying gaps, pivoting to urgent needs, and planning ahead.

#### Technology Prioritisation

- **Branch Competence System** — each tech branch (infantry, armour, air, naval, industry, electronics, doctrine) receives a dynamic weight based on current needs, threat profile, and existing progress
- **Gap analysis** — the AI identifies equipment types falling behind relative to enemies and boosts research in those branches
- **Doctrine alignment** — the AI evaluates which doctrine path it has invested in and prioritises complementary technologies

#### Advanced Behaviour

- **Ahead-of-time evaluation** — at higher intelligence, the AI accepts ahead-of-time penalties for critical technologies (e.g., rushing fighters when air_threat is high)
- **Research slot optimisation** — the AI balances slots between urgent military needs and long-term industrial investment based on threat_index
- **Tech trading awareness** — the AI factors in technology sharing from faction members when evaluating research priorities

#### Intelligence Scaling

- **Low (< 1.0x):** Follows a reasonable but generic research order. May over-invest in one branch or neglect critical technologies.
- **Medium (1.0–1.3x):** Actively identifies gaps and pivots. Balances current needs with forward planning.
- **High (> 1.3x):** Min-maxes research order. Prioritises force-multiplier techs early. Accepts ahead-of-time penalties for critical equipment.

### DAI: Army

Combines division template design and production management into a single cohesive module. The AI designs divisions it can actually build and produces what it actually needs — no more 40-width heavy tank templates from a 20-factory nation sitting on empty stockpiles.

#### Adaptive Templates

- **Equipment-aware design** — the AI only designs templates using equipment it can produce in sufficient quantities
- **Terrain evaluation** — analyses terrain on borders and active fronts. Mountains get infantry templates; plains get wider formations with armour
- **Doctrine-matched composition** — template widths and support companies align with chosen doctrine. Superior Firepower gets artillery-heavy; Mobile Warfare gets motorised/mechanised
- **Progressive upgrading** — starts with simple templates early-game and upgrades as the industrial base grows. No end-game templates in 1936.
- **Role classification** — designates templates as line infantry, garrison, breakthrough, exploitation, or special purpose, and produces the right ratio based on front needs

#### Intelligent Production

- **Equipment deficit tracking** — continuously monitors the gap between fielded divisions' needs and current stockpile plus production rate
- **Dynamic rebalancing** — shifts factory allocation when deficits are detected. Higher intelligence = faster rebalancing.
- **Lend-lease awareness** — factors in incoming lend-lease when calculating deficits, avoiding over-production
- **Stockpile targeting** — maintains target stockpile levels per equipment type. Once targets are met, diversifies or trades surplus.
- **Construction priorities** — civilian vs. military factory construction driven by threat-timeline evaluation. Low threat = civilian first for snowball. High threat = rush military. Emergency overrides: needs crisis suppresses civilian building to 0.1x and boosts military to 4x. Posture-driven: buildup posture boosts civilian 2.5x, total war boosts military 3x.
- **Supply infrastructure construction** — three new construction strategies for infrastructure, supply hubs, and railways. All scale with `dai_supply_strain` (driven by division count and territorial overextension). At war with high strain, supply hub priority reaches 18x base. AI also boosts truck production when logistics are strained (up to 3x combined factors).
- **Internal needs failsafe** — when equipment ratio drops below 0.3, manpower below 0.15, supply strain exceeds 0.7, or surrender progress exceeds 0.2, the system activates `dai_needs_override_active`. This triggers emergency production overrides (infantry equipment 3x, suppress tanks/air to 0.1x–0.3x), halts offensives via the needs crisis defense frontline tier, and forces conscription upgrades (priority 100 at manpower < 0.1). Prevents the AI from ignoring its own critical shortages.

### DAI: Warfare

The flagship module. Combines land strategy, naval operations, and air power into a unified military command system. The AI fights wars like a player — concentrating force, controlling the skies, and projecting naval power where it matters.

#### Frontline Control

A dedicated subsystem (`dai_warfare_frontline.txt`) that governs how the AI executes front operations in real time. This is separate from the strategic-level land decisions and controls moment-to-moment front behaviour.

- **Priority-based front control cascade** — 9 tiers of front behaviour, from emergency halt (priority 10000) to balanced warfare (priority 1000). HOI4 picks the highest-priority plan whose conditions are met:
  - `emergency_stop` (10000) — nation collapsing (surrender > 40%, equipment < 25%), halt all movement
  - `pocket_closure` (9000) — enemy extremely weak (strength ratio < 0.3), rush to close encirclements
  - `opportunity_exploit` (8000) — enemy surrendering (> 30%), finish them off
  - `needs_crisis_defense` (6000) — **critical needs failsafe** — halts offensives when equipment ratio < 35% and needs override is active, allowing manual counterattacks while the AI addresses equipment/manpower crises
  - `crisis_defense` (5000) — losing badly (high defensive priority), hold the line
  - `full_offensive` (4000) — overwhelming advantage (readiness > 80%, equipment > 70%), rush all fronts
  - `offensive_push` (3000) — favourable conditions (readiness > 60%), rush weak sectors
  - `cautious_defense` (2000) — under pressure (moderate defensive priority), execute orders carefully
  - `balanced_warfare` (1000) — standard wartime fallback
- **Front armour steering** — dynamically directs armour toward weak enemies (Schwerpunkt) and pulls it away from fortified lines. Rushes armour toward collapsing enemies for exploitation. Intelligence-scaled concentration bonuses.
- **Force concentration** — masses breakthrough forces on weak sectors when offensive readiness is high. Higher intelligence AI concentrates more aggressively (Schwerpunkt factor). Spreads forces evenly when defending.
- **Front unit requests** — boosts division allocation to active fronts during war, scales with defensive/offensive state and intelligence. Reduces allocation during peacetime.
- **Area priorities** — theatre-level force allocation across 7 geographic zones (Europe, Asia, Pacific, Africa, Middle East, South America, North America). Base priorities scale with war state, threat level, and strategic needs (e.g., Pacific boosts for naval powers, Middle East boosts when resource-starved).
- **Theatre distribution demand** — reinforces theatres with active combat. Scales with defensive pressure and intelligence.

All frontline strategies are profile-independent (front control types and area names are engine-level, universal across all mods). Gated by `DAI_WARFARE_ENABLED`.

#### Land Strategy

- **Role ratios** — determines the ideal mix of unit roles (infantry, armour, mobile, garrison) based on front needs, industrial capacity, threat profile, and strategic posture. Posture-driven: offensive posture boosts armour ratio 2x, defensive posture halves it and doubles garrison ratio.
- **Reserve management** — maintains a strategic reserve of mobile/armoured divisions committed to exploit breakthroughs, not fed into static lines
- **Dynamic garrison scaling** — garrison ratio scales dynamically with occupied territory size (2x at 40+ states, stacking 1.5x at 70+), threat level (1.5x at threat > 60), and national power (1.3x for majors). Two garrison templates: basic (6 cavalry + MP) and improved (8 cavalry + MP + AA, unlocked when occupation > 30). Prevents the common AI issue of light garrisons after rapid territorial gains.
- **Reactive anti-tank deployment** — when enemy armour tech is detected (medium/improved/heavy tanks), the AI activates an AT-focused infantry template variant and dramatically boosts anti-tank gun production (up to 9x combined factors for advanced enemy armour).

#### Naval Operations

- **Fleet composition by role** — builds navies with purpose: convoy escort fleets, surface strike groups, and submarine wolfpacks. Ratio determined by strategic needs.
- **Task force sizing** — sized to match missions. Patrol groups are small and numerous, strike groups concentrated, escort groups match active trade routes.
- **Sea zone prioritisation** — evaluates which zones are critical (own trade routes, enemy staging areas, chokepoints) and deploys accordingly
- **Naval invasion support** — invasions are gated by a composite `dai_war_invasion_readiness` score (0–100) that evaluates naval superiority (+30), air superiority (+20), equipment health (up to +25), intelligence (+15), and national power (+10). Invasions are suppressed when supply strain is high (-30) or equipment is critical (-40). This prevents suicidal invasions while enabling well-prepared amphibious operations.
- **Dockyard allocation** — mirrors production logic: builds what it needs, not what looks impressive

#### Air Power

- **Air zone priority** — evaluates which zones contain active fronts, strategic targets, or naval operations, and deploys wings accordingly
- **Mission balance** — balances air superiority, CAS, and strategic bombing based on situation. Active offensives boost CAS; defence boosts fighters.
- **Wing sizing** — sized to match airfield capacity, avoiding over-stacking. Spreads wings across available airfields in a zone.
- **Ace management** — at higher intelligence, assigns aces to high-priority wings and avoids wasteful deployments

### DAI: Grand Strategy

Combines diplomatic and economic decision-making into a single strategic planning module. The AI manages alliances, wars, peace deals, trade, and mobilisation as an integrated grand strategy — not as disconnected systems.

#### Diplomacy

- **Threat-based alignment** — joins factions based on perceived threats, not ideology alone. A democracy facing aggression seeks alliances urgently.
- **War declaration evaluation** — evaluates whether it can win before declaring war, accounting for alliances, readiness, and available fronts. No suicidal declarations.
- **Guarantee logic** — guarantees nations that serve as buffers against threats; avoids guaranteeing nations it can't defend
- **Peace conference behaviour** — prioritises strategic territories (chokepoints, industry, border security) over maximal land grabs. Higher intelligence = more strategic deals.
- **Lend-lease and volunteers** — sends lend-lease to equipment-starved, strategically important allies; volunteers to wars it wants to influence without joining

#### Economy

- **Trade optimisation** — evaluates resource needs and trades efficiently, preferring allies for political power generation
- **Mobilisation timing** — evaluates threat_index and industrial readiness instead of fixed dates. Imminent war = mobilise early; safe position = grow civilian economy. Posture-driven: buildup posture shifts ratio -20 toward civilian; total war posture shifts +60 toward military.
- **Law change sequencing** — prioritises law changes that unlock the most impactful benefits first. Emergency conscription failsafe forces law upgrades at priority 100 when manpower drops below 10%.
- **Civilian-military balance** — maintains a healthy factory ratio, avoiding the trap of going full military too early
- **Resource stockpiling** — anticipates future needs and adjusts trade deals before shortages hit
- **Supply train scaling** — minimum supply trains scale with supply strain (up to +100 above base during logistics crises) and occupied territory size (+30 for large occupations)

---

## 6. Cross-Mod Compatibility

### What Actually Breaks

Most AI mods are incompatible with overhaul mods. There are three layers of incompatibility:

#### Layer 1: Hardcoded References (Solved by Design)

The simplest failures: mods reference specific country tags (GER, SOV), specific dates (1939.9.1), or specific focus tree checks. DAI eliminates this entirely by design — no country tags, no dates, no focus checks.

#### Layer 2: Technology and Research (Requires Profiles)

The hardest compatibility problem. HOI4's ai_strategy system with `type = research_tech` references **technology categories** defined in `common/technology_tags/`. Vanilla defines categories like `infantry_weapons_tech`, `armor_tech`, `air_tech`, etc. But overhaul mods can replace these entirely:

- **Kaiserreich** has a different tech tree structure with modified categories and different tech IDs
- **The New Order** has a radically different tech system with unique categories
- **Ride for Ruin** (LotR mod) replaces the entire tree with Metallurgy, Carpentry, Agriculture, and Organisation
- **Road to 56** extends the vanilla tree with additional techs and categories

If DAI's research strategy references `infantry_weapons_tech` and the overhaul mod has renamed it to `small_arms_tech`, the strategy silently fails — the AI ignores it because the category doesn't exist. No errors — it just doesn't work.

The same applies to specific tech IDs used in `has_tech` triggers.

#### Layer 3: Templates and Equipment (Requires Profiles)

`ai_templates` reference specific sub-unit types (`infantry`, `motorized`, `medium_armor`) defined in `common/sub_units/` and equipment archetypes defined in `common/units/equipment/`. Overhaul mods can:

- Rename sub-unit types (`medium_armor` → `panzer_medium`)
- Remove sub-unit types entirely (no mechanised in a WW1 mod)
- Add new sub-unit types (cavalry variants, unique unit classes)
- Change equipment archetypes and their stat profiles

### The DAI Approach: Three Rules Plus Profiles

- **Rule 1: No country tags, ever.** All triggers use generic conditions evaluated from game state.
- **Rule 2: No date-based triggers.** Strategic conditions (threat level, readiness) replace calendar checks.
- **Rule 3: No content IDs in core logic.** The core framework and shared triggers never reference specific tech IDs, equipment names, or sub-unit types. Only the generated output files (ai_strategy, ai_templates) contain mod-specific content IDs — and these are generated by the profile system.

---

## 7. Profile System

### Overview

A mod profile is a YAML mapping file that tells the DAI build pipeline what technology categories, sub-unit types, and equipment archetypes exist in a target mod, and how they map to DAI's abstract categories. The build pipeline reads **all** profiles from `profiles/` and generates HOI4 script files containing strategies for **every** profile, each gated behind a profile-specific global flag. At runtime, only the active profile's strategies fire.

This means DAI ships as a **single mod** with all supported profiles built in. Players select their profile via a game rule — either "Auto-Detect" (default) or a manual override. No separate builds, no separate downloads, no manual patching.

Profiles are generated automatically by a single Python script (`profile_generator.py`) that scans a mod's directory structure. Manual overrides are supported for edge cases but should rarely be needed.

### What the Profile Scanner Detects

| Scanned Directory | What It Finds | How DAI Uses It |
|-------------------|--------------|-----------------|
| `common/technology_tags/` | All technology category tokens | Maps to DAI's abstract research branches for ai_strategy blocks |
| `common/technologies/` | Individual tech IDs, categories, tree structure, years | Validates category mapping, identifies early vs late techs |
| `common/sub_units/` | All sub-unit types and their stats | Maps to DAI's abstract template roles for ai_templates |
| `common/units/equipment/` | Equipment archetypes and type/group_by fields | Maps to abstract equipment categories for production strategy |
| `common/ideologies/` | All ideology tokens and sub-ideologies | Feeds into political behaviour system, maps to abstract aggression profiles |
| `common/ideas/` | Economy and mobilisation laws | Grand Strategy module uses for mobilisation timing and law sequencing |

### DAI Abstract Categories

DAI defines a fixed set of abstract categories representing universal strategic concepts. The profile maps mod-specific content to these:

| Abstract Category | Purpose | Vanilla Mapping Example |
|-------------------|---------|------------------------|
| `BRANCH_INFANTRY` | Small arms and infantry equipment tech | `infantry_weapons_tech` |
| `BRANCH_ARMOUR` | Tanks and armoured vehicle tech | `armor_tech` |
| `BRANCH_AIR` | Aircraft tech (fighters, CAS, bombers) | `light_air_tech`, `medium_air_tech`, `heavy_air_tech` |
| `BRANCH_NAVAL` | Ship and submarine tech | `dd_tech`, `cl_tech`, `bb_tech`, `ss_tech` |
| `BRANCH_INDUSTRY` | Factories, construction, resources | `industry_tech`, `synth_resources_tech` |
| `BRANCH_ELECTRONICS` | Radar, encryption, computing | `electronics_tech` |
| `BRANCH_DOCTRINE` | Land/naval/air doctrine | `land_doctrine_tech`, `naval_doctrine_tech`, `air_doctrine_tech` |
| `ROLE_LINE_INFANTRY` | Standard front-holding division | `infantry` sub-unit |
| `ROLE_BREAKTHROUGH` | Armoured/heavy assault division | `medium_armor`, `heavy_armor` sub-units |
| `ROLE_MOBILE` | Fast exploitation division | `motorized`, `mechanized` sub-units |
| `ROLE_GARRISON` | Occupation and suppression | `cavalry` sub-unit |
| `ROLE_SPECIAL` | Marines, mountaineers, paratroopers | `marine`, `mountaineers`, `paratrooper` sub-units |
| `EQUIP_INFANTRY` | Infantry weapons family | `infantry_equipment` archetype |
| `EQUIP_ARMOUR` | Tank equipment family | `medium_tank_equipment` archetype |
| `EQUIP_FIGHTER` | Fighter aircraft family | `fighter_equipment` archetype |
| `EQUIP_CAS` | Close air support family | `CAS_equipment` archetype |
| `EQUIP_CAPITAL_SHIP` | Heavy naval vessels | `battleship`, `heavy_cruiser` archetypes |
| `EQUIP_SCREEN` | Light naval vessels | `destroyer`, `light_cruiser` archetypes |

### Profile Generator Script

Usage:

- `python profile_generator.py --scan /path/to/mod` — scans mod directory, generates draft profile YAML
- `python profile_generator.py --scan /path/to/mod --base vanilla` — scans with vanilla as base layer (for mods that extend the tech tree)
- `python profile_generator.py --validate profile.yaml` — validates against DAI abstractions, reports unmapped content
- `python profile_generator.py --diff old_profile.yaml new_profile.yaml` — shows changes between versions (useful when a mod updates)

#### Auto-Detection Logic

The scanner uses heuristics to auto-map mod content:

- **Technology categories** — matched by keyword analysis. A category containing 'armor', 'tank', or 'panzer' maps to `BRANCH_ARMOUR`. Ambiguous categories flagged for manual review.
- **Sub-units** — matched by stat profile (combat_width, need fields, categories). A sub-unit using tank equipment with high hardness maps to `ROLE_BREAKTHROUGH`.
- **Equipment** — matched by archetype type field. Equipment with `type = armor` maps to `EQUIP_ARMOUR`.
- **Ideologies** — matched by vanilla tokens if present, or keyword analysis of custom ideology names.

#### Manual Overrides

Profiles support a `manual_overrides` section for edge cases. Takes priority over auto-detection. Re-running the scanner preserves manual overrides.

### Historical Biases in Profiles

Each profile can include an optional `historical_biases` section, only read when the Historical preset is selected.

| Bias Type | What It Defines | Example (Vanilla Profile) |
|-----------|----------------|--------------------------|
| `research_bias` | Nudges nations toward certain tech branches based on conditions | Nations with GPS > 70 and high armour industry bias toward `BRANCH_ARMOUR`. Island nations with strong naval base bias toward `BRANCH_NAVAL`. |
| `doctrine_bias` | Soft preference for doctrine paths | Nations with large manpower and low industry bias toward Mass Assault. High industry + mobile terrain bias toward Mobile Warfare. |
| `strategy_bias` | Adjusts offensive/defensive posture | Resource-starved industrial powers bias toward early aggression. Strong defensive geography biases toward fortification. |
| `diplomacy_bias` | Nudges alliance behaviour | Nations sharing borders with common threats bias toward mutual alliance. |
| `economy_bias` | Adjusts mobilisation and construction | Large civilian economies bias toward late mobilisation but rapid pivot when threatened. |

**Key design principle: historical biases describe conditions, not countries.** The vanilla profile doesn't say "Germany should build tanks" — it says "a nation with strong industry, limited resources, and hostile neighbours on flat terrain should bias toward armour research and early offensive strategy." Germany matches those conditions in 1936. But if another nation matches them instead, it gets the same biases. This keeps the system dynamic even in Historical mode.

When conditions diverge mid-game (territory lost, alliances broken), the bias triggers no longer match and the dynamic system takes over seamlessly. Historical mode produces plausible alternate history, not a scripted railroad.

### Built-In Profiles

DAI ships with pre-built, tested profiles:

- **vanilla** — default, always included
- **kaiserreich** — Kaiserreich: Legacy of the Weltkrieg
- **tno** — The New Order: Last Days of Europe
- **blackice** — Black ICE

### Runtime Profile Selection

Players select which profile is active via a **"Compatibility Profile"** game rule added by DAI:

| Option | Behaviour |
|--------|-----------|
| **Auto-Detect** (default) | At startup, DAI checks for mod-specific content using `detection_hints` from each profile. The first matching non-vanilla profile wins. If none match, vanilla is the fallback. |
| **Vanilla** | Force vanilla profile regardless of loaded mods. |
| **Kaiserreich** | Force Kaiserreich profile. Use if auto-detect fails. |
| **TNO** / **BlackICE** / etc. | Force the selected profile. |

Auto-detection works by checking for the existence of mod-specific technologies or units defined in each profile's `detection_hints` section. For example, the Kaiserreich profile might list a tech that only exists in KR's tech tree. If that tech exists in the current game, the KR profile is activated.

If auto-detect picks the wrong profile (rare edge case), the player simply selects the correct one manually before starting the campaign.

### Profile Gating in Generated Code

Every ai_strategy block that references profile-specific content IDs (tech categories, equipment archetypes, sub-unit types) is double-gated:

```
dai_res_vanilla_branch_infantry_infantry_weapons = {
    enable = {
        has_global_flag = DAI_RESEARCH_ENABLED    # module gate
        has_global_flag = DAI_PROFILE_VANILLA     # profile gate
        is_ai = yes
    }
    abort = {
        OR = {
            NOT = { has_global_flag = DAI_RESEARCH_ENABLED }
            NOT = { has_global_flag = DAI_PROFILE_VANILLA }
        }
    }
    ...
}
```

Non-active profiles abort on the flag check immediately — near-zero performance cost. The HOI4 engine also silently ignores `ai_strategy` blocks referencing content IDs that don't exist in the loaded mod, providing a second safety layer.

### Build Pipeline Integration

- `python build.py` — builds with ALL profiles from `profiles/` baked into one mod
- `python build.py --validate` — builds and validates generated output
- `python build.py --clean --validate` — cleans generated files first
- `python tools/profile_generator.py --scan /path/to/mod` — auto-generates a draft profile YAML

Output is always a single `dai/` mod directory containing strategies for every profile. One mod, one Workshop subscription, all profiles included.

---

## 8. HOI4 Mod Structure

### Descriptor

Single `descriptor.mod` with no `replace_path`:

```
name = "DAI - Smarter AI"
version = "1.1.0"
tags = { "Gameplay" "Military" "Utilities" }
supported_version = "1.15.*"
picture = "thumbnail.png"
```

No replace_path. No dependencies. One subscription, everything included.

### Directory Layout

Mod folder: `dai/`

| Path | Files | Owner |
|------|-------|-------|
| `common/game_rules/` | `dai_game_rules.txt` | Core — all module toggles, presets, behaviour settings |
| `common/scripted_triggers/` | `dai_core_triggers.txt`, `dai_research_triggers.txt`, `dai_army_triggers.txt`, `dai_warfare_triggers.txt`, `dai_gs_triggers.txt` | Each module owns its trigger file. Core includes GPS tier checks and module-enabled gates. |
| `common/scripted_effects/` | `dai_core_effects.txt`, `dai_research_effects.txt`, `dai_army_effects.txt`, `dai_warfare_effects.txt`, `dai_gs_effects.txt` | Core handles GPS calculation. Module effects handle weight recalculations. |
| `common/on_actions/` | `dai_on_actions.txt` | Core — monthly evaluation hook, war/peace hooks, tech completed hook |
| `common/ai_strategy/` | `dai_research_strategy.txt`, `dai_army_production.txt`, `dai_army_construction.txt`, `dai_warfare_frontline.txt`, `dai_warfare_land.txt`, `dai_warfare_naval.txt`, `dai_warfare_air.txt`, `dai_warfare_invasion.txt`, `dai_gs_diplomacy.txt`, `dai_gs_economy.txt` | Each module owns its strategy files. Every block gated by module-enabled check. |
| `common/ai_templates/` | `dai_army_templates.txt` | Army module — dynamic role-level template targets |
| `common/ai_peace/` | `dai_gs_peace.txt` | Grand Strategy — peace conference weights |
| `common/defines/` | `dai_defines.lua` | Engine-level AI define overrides (garrison fraction, plan execution, convoy escort, air importance, etc.) |
| `events/` | `dai_core_events.txt`, `dai_research_events.txt`, `dai_army_events.txt`, `dai_warfare_events.txt`, `dai_gs_events.txt` | Hidden events (no UI). Namespaces: `dai_core`, `dai_research`, `dai_army`, `dai_warfare`, `dai_gs` |
| `localisation/english/` | `dai_l_english.yml` | All localisation. UTF-8 BOM. |
| `descriptor.mod` | — | Mod metadata |
| `thumbnail.png` | — | Workshop thumbnail (256×256) |

### Module Gating Pattern

Every ai_strategy block is wrapped in a gate trigger. The game rule sets a global flag (e.g., `DAI_RESEARCH_ENABLED`) at game start. Every Research ai_strategy block includes a first factor modifier checking `has_global_flag = DAI_RESEARCH_ENABLED`. If absent, the factor evaluates to 0.01 and the engine skips all subsequent factors. Disabled modules have near-zero performance cost.

### File Ownership Rules

- **No replace_path** — all files additive. Layers on top of vanilla or any overhaul.
- **Unique filenames** — every file prefixed `dai_` to avoid collisions.
- **Unique namespaces** — module-specific event namespaces prevent ID collisions.
- **No vanilla file edits** — never modifies or copies vanilla files.
- **Module isolation** — modules communicate only through shared `dai_` country variables from Core.

### Load Order

Irrelevant. No replace_path + no vanilla edits = works in any load order with any mod.

---

## 9. Performance Optimisation

### Design Philosophy

**Evaluate less, cache more.** Most strategic decisions change on a weekly or monthly timescale. DAI batches expensive evaluations into periodic sweeps and caches results as country variables that modules read cheaply between evaluations.

### Staggered Evaluation

Rather than evaluating all nations on the same day (causing lag spikes), DAI distributes evaluations:

- Each country gets a **recalculation offset** based on a hash of its tag (tag hash mod 30 = day of month)
- On any given day, only 2–3 countries run their full GPS evaluation
- The result is flat, even CPU load across the month
- The offset is deterministic — same country always evaluates on the same day, save/load consistent

### Tiered Evaluation Depth

| Tier | Criteria | Evaluation | Frequency |
|------|----------|-----------|-----------|
| Major | GPS > 60 OR at war OR > 50 factories | Full GPS + all sub-scores + all module weights | Every cycle (default 30 days) |
| Regional | GPS 25–60 OR > 20 factories OR borders a major at war | Full GPS + core sub-scores. Simplified module weights. | Every cycle |
| Minor | GPS < 25 AND not at war AND < 20 factories | Lightweight GPS only. Module weights from preset defaults. | Every other cycle |
| Inactive | No military, no factories, subject with no autonomy | No evaluation. Flat preset multiplier. | Never (re-checked on status change) |

Only 10–15 nations run the expensive full evaluation. 50+ minors use lightweight or skipped evaluations.

### Trigger Complexity Budget

- **Maximum trigger depth: 3 levels.** Deeper logic must be pre-computed and cached as variables.
- **Maximum factors per ai_strategy: 8.** More than 8 causes measurable slowdown across all nations.
- **Prefer variable reads over trigger evaluations.** Reading a cached `dai_` variable is free. Evaluating a trigger is expensive.
- **No `every_country` or `every_state` loops in hot paths.** Pre-compute aggregate data during GPS sweep.

### ai_strategy Factor Optimisation

- **Early-exit ordering** — cheapest, most-likely-to-fail conditions first. Check `dai_is_at_war` before evaluating front ratios.
- **Factor clamping** — use `clamp_min`/`clamp_max` to prevent erratic oscillation.
- **Avoid factor = 0** — use 0.01 instead to prevent re-evaluation loops.
- **Batch related strategies** — fewer blocks with compound logic rather than many blocks with similar triggers.

### Variable Cleanup

- **Fixed variable set** — no dynamic variable creation at runtime.
- **Overwrite, never append** — all variables overwritten each cycle.
- **Compact naming** — short prefixes (`dai_`, `dai_res_`, etc.). ~22 variables × ~80 countries = ~1,760 entries, negligible.

### Performance Testing Protocol

- **Benchmark:** 1936 start, observe to 1945 at speed 5 on mid-range PC. Measure average daily tick with/without DAI.
- **Target overhead:** no more than 10% average daily tick increase. Monthly spikes up to 15%.
- **Late-game stress test:** 1942 bookmark, all majors at war. Must be playable at speed 3.
- **Memory:** save file increase under 50KB.
- **Profiling:** use HOI4 debug console (`tdebug`, `debug_ai`). Any trigger > 0.1ms must be refactored.

### Performance Budget by Module

| Module | Budget | Primary Cost | Optimisation Strategy |
|--------|--------|-------------|----------------------|
| Core | 40% | GPS calculation, variable updates | Staggered evaluation, tiered depth |
| Research | 10% | Tech branch weight factors | Cache branch scores as variables |
| Army | 20% | Template evaluation, production rebalance | Evaluate templates only on `dai_tech_completed`, not every tick |
| Warfare | 20% | Front strength, zone scoring | Pre-compute front ratios monthly, cache as variables |
| Grand Strategy | 10% | Diplomatic evaluation, trade | Evaluate only on war/peace hooks plus monthly sweep |

---

## 10. Build Roadmap

| Phase | Deliverables | Priority | Status |
|-------|-------------|----------|--------|
| Phase 1: Foundation | Core (GPS engine, shared variables, game rules), Research (refactored from Arms Race Mechanics), Python build pipeline | Critical | **Complete** |
| Phase 2: Army | Army module (adaptive templates + intelligent production), Army game rules, integration testing with Research | High | **Complete** |
| Phase 3: Warfare | Warfare module (land + naval + air), combined-arms integration with Army, Warfare game rules | High | **Complete** |
| Phase 4: Grand Strategy | Grand Strategy module (diplomacy + economy), Grand Strategy game rules, per-nation overrides | Medium | **Complete** |
| Phase 5: Polish | Cross-mod testing (Kaiserreich, TNO, BlackICE), performance optimisation, Workshop descriptions, community feedback | High | **Complete** |
| **v1.1: Competitive Advantage** | Supply construction, garrison hardening, needs failsafe, strategic postures, engine defines, reactive AT, invasion readiness, equipment ratio rewrite | High | **Complete** |

### v1.1 Changelog

The v1.1 update addresses known issues shared with competitor AI mods (notably "Better Mechanics: Frontline AI") and adds features that surpass the competition:

- **Equipment ratio accuracy** — replaced binary 0.8/0.4 estimation with multi-signal system (division/factory ratio, surrender progress, industry delta). All downstream systems now receive accurate equipment health signals.
- **Supply infrastructure construction** — AI now builds infrastructure, supply hubs, and railways dynamically based on supply strain. Truck production scales with logistics needs.
- **Dynamic garrison scaling** — garrison ratio, template quality, and triggers all scale with occupied territory size, eliminating light-garrison edge cases after rapid conquests.
- **Internal needs failsafe** — emergency override system prevents the AI from ignoring critical equipment, manpower, supply, or surrender crises. Halts offensives and forces production reprioritisation.
- **Strategic posture system** — 6-level posture (Buildup→Survival) coordinates production, research, warfare, and diplomacy simultaneously. Surpasses competitor "AI Postures" by spanning all modules.
- **Engine define overrides** — new `common/defines/dai_defines.lua` tunes 9 NAI constants (garrison fraction, plan execution, terrain caution, convoy escort, air importance, etc.).
- **Reactive anti-tank production** — detects enemy armour tech level and scales AT gun production and infantry templates accordingly, rather than boosting AT for any war.
- **Naval invasion coordination** — composite readiness score gates invasions on naval/air superiority, equipment health, and intelligence, with supply strain and equipment crisis suppressors.

### Success Metrics

- **Compatibility:** loads without errors alongside top 10 overhaul mods
- **Performance:** adds no more than 10% to average daily tick time
- **AI competence:** on Competitive, AI majors consistently field good divisions, maintain production, and execute coordinated offensives by mid-game
- **Modularity:** any module can be disabled without breaking others

---

## 11. Appendix: Technical Reference

### HOI4 Scripting Constraints

- `ai_strategy` factor weights are multiplicative, not additive. Factor of 0 disables entirely.
- **Country variables** persist across save/load. DAI always reads from ROOT or FROM, never hardcoded tags.
- **on_actions** fire for all countries simultaneously. GPS loop must be lightweight.
- **Game rules** are the primary configuration mechanism. Set pre-game, persist through save/load, no custom GUI needed.
- `division_template` scripting can create/modify but not delete. DAI marks obsolete templates with a prefix.
- **The AI won't use templates it lacks equipment for.** This is a feature — Army module designs aspirational templates the AI adopts as production catches up.
- **`common/defines/` overrides** — `NDefines.NAI.*` values tune engine-level AI behaviour that scripts cannot reach (garrison fraction, plan execution thresholds, convoy escort priority, etc.). These are global and affect all AI nations equally; per-nation tuning remains in ai_strategy scripts. DAI generates `dai_defines.lua` from `config/defines.yaml`.
- **No direct equipment percentage access** — HOI4 provides no trigger for "percentage equipped". DAI uses a multi-signal proxy: division-to-factory ratio, surrender progress, and industry delta. This is less precise than a direct read but dramatically better than a binary estimate.
- **`any_enemy_country` + `has_tech`** — valid but relatively expensive. Used sparingly (monthly evaluation only, not daily) for enemy armour threat detection.

### Variable Naming Conventions

All DAI variables use the `dai_` prefix. Module-specific variables add a second prefix:

- `dai_` — Core framework (GPS, competence, intelligence, political modifiers)
- `dai_res_` — Research module
- `dai_army_` — Army module
- `dai_war_` — Warfare module
- `dai_gs_` — Grand Strategy module

### Source Repository Structure

| Directory | Purpose |
|-----------|---------|
| `config/` | YAML definitions for all module AI strategies and factor weights |
| `config/presets/` | Preset definitions (Casual, Balanced, Historical, Realistic, Competitive) |
| `config/modules/` | Per-module config (research.yaml, army.yaml, warfare.yaml, grand_strategy.yaml) |
| `config/defines.yaml` | Engine-level NAI define overrides (garrison, frontline behaviour, naval, production, air) |
| `profiles/` | Mod compatibility profiles (YAML mapping files) |
| `profiles/vanilla.yaml` | Default profile |
| `profiles/kaiserreich.yaml` | Kaiserreich profile (pre-built, tested) |
| `profiles/tno.yaml` | TNO profile (pre-built, tested) |
| `profiles/blackice.yaml` | BlackICE profile (pre-built, tested) |
| `generator/` | Python package: reads YAML configs + ALL profiles → outputs HOI4 script with per-profile gated strategies |
| `generator/templates/` | Jinja2 templates for generating .txt files. Profile-dependent templates iterate over all profiles. |
| `tools/` | `profile_generator.py` (auto-scans mods), utilities |
| `common/`, `events/`, `localisation/` | Generated HOI4 mod files (output directly into mod root, rebuilt per build). Includes `common/defines/dai_defines.lua` for engine overrides. |
| `tests/` | Validation scripts and integration tests |

### Future Considerations

- **Machine learning integration** — training a model on multiplayer replays to generate optimal factor weights, exported as YAML configs
- **Multiplayer AI** — improving AI for non-player nations in multiplayer without desync
- **Community module API** — documenting the variable/trigger interface for DAI-compatible extensions
- **Victoria 3 / future titles** — the YAML-driven, tag-agnostic architecture could adapt to other Paradox games
