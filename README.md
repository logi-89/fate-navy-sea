# FATE: The Navy Sea

**FATE: The Navy Sea** is a 2D Metroidvania-style action-adventure game developed as the ICS3U1 final culminating project at BHSS. Players navigate a treacherous maritime world, uncovering secrets, battling enemies, and unlocking new abilities to progress through an immersive environment.

---

## Game Overview

**FATE: The Navy Sea** is a **2D side-scrolling action-adventure platformer** with Metroidvania-style progression. Players explore a series of interconnected levels, fight enemies, collect coins and upgrades, and defeat bosses to progress through the story.

### Objective
Navigate through 6 distinct levels — from the Docks to the final Boss Arena — using platforming, combat, and puzzle-solving. Collect paperclips to break doors, spend coins at shops for health and ammo upgrades, and eliminate all enemies to clear each stage. The ultimate goal: conquer the Navy Sea.

### Inspiration
The game was developed as the ICS3U1 final culminating project at BHSS. It draws from classic Metroidvania design — non-linear exploration, ability-gated progression, and boss encounters — with an original nautical theme and custom soundtrack.

### Audio & Visual Design

- **Visuals:** A 2D stylized world utilizing custom tilemaps and sprite animations.
- **Audio:** Original custom-composed soundtrack by **Nathan Chan** and **Nicky Mamoukarys**.

---

## Gameplay Mechanics

- **Core Loop:** Exploration, enemy combat, platforming, and boss fights.
- **Controls:**
  - `W A S D` / `Arrow Keys` – Movement & Jumping
  - `Space` / `W` / `Up` – Jump / Double Jump
  - `E / Q` – Elevator up / down
  - `F` – Break doors (requires paperclips) / Interact with lore
  - `1` / `Mouse Click` – Attack with equipped weapon
  - `H` – Heal (consumes flasks)
  - `Esc` – Quit
  - `P` – Quit (dev mode only)
- **Weapons:**
  - **Spear** – Melee, infinite ammo (Level 1)
  - **Water Gun** – Ranged, 25 ammo (Level 2), 150 ammo (Level 6)
  - **Water Balloon** – Heavy ranged, 5 ammo (Level 2), 150 ammo (Level 6)
- **Shops:** Spend coins on ammo, health upgrades, speed boots, and revive tokens.
- **Ability Gates:** Classic Metroidvania progression requiring specific upgrades.

---

## Levels

| # | Name | Description |
|---|------|-------------|
| 1 | The Docks | Introductory area with spear-only combat and tutorial |
| 2 | The Depths | Unlock water gun and balloon, platforming challenges |
| 3 | The Elevator Shaft | Vertical ascent with elevator mechanics |
| 4 | The Bridge | Mid-game gauntlet |
| 5 | The Tower | Pre-boss gauntlet with the Warden |
| 6 | Boss Arena | Final boss encounter (Fi Fy Fuh & Thule) |

---

## Technical Specifications

Built using **Python 3** and **Pygame**:

- **State Management:** Start Screen, Active Gameplay, Pause Menu, Death Screen, and Game Over.
- **Game Systems:** Game loops, Delta Time clock, physics-based collision detection.
- **Enemy AI:** Dynamic behaviors including tracking, ranged attacks, and boss phases.
- **Custom Audio Engine:** Pygame mixer for simultaneous background tracks and SFX.
- **Intro Animation:** MP4 video played on launch via pre-extracted frames.

---

## How to Run

### Prerequisites

Python 3.x and pip installed.

### Installation

1. Clone the repo:
```bash
git clone https://github.com/logi-89/fate-navy-sea.git
```

2. Navigate into the directory:
```bash
cd fate-navy-sea
```

3. Install dependencies:
```bash
pip install pygame
```

4. Run the game:
```bash
python main.py
```

---

> **Course:** Grade 11 Introduction to Computer Science (ICS3U1)
> **Project Due Date:** June 14, 2026, 11:59 P.M.
