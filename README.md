# Flappy Bird AI

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Pygame](https://img.shields.io/badge/pygame--ce-rendering-green)
![NEAT](https://img.shields.io/badge/NEAT-neuroevolution-orange)
![License](https://img.shields.io/badge/License-GPL--3.0-lightgrey)

NEAT neuroevolution AI that teaches birds to play Flappy Bird. No image assets — all shapes drawn with `pygame.draw`.

Watch 50 birds per generation learn to flap through pipes in real time — the window stays open across generations so you can watch evolution happen.

## Features

- **NEAT neuroevolution** — population of 50 neural networks evolved with `neat-python`
- **5-input / 1-output network** — bird Y, velocity, distance to pipe, distance to gap top/bottom → jump when activation > 0.5
- **Fitness shaping** — +0.1 per frame alive, +5 per pipe passed
- **Pixel-accurate collision** — `pygame.mask.Mask.overlap()` detection
- **Pure-code rendering** — gradient sky, clouds, pipes, birds, particles; no image assets
- **Live HUD** — generation counter, alive count, best score, per-generation history
- **PyInstaller build guide** — see `feature.md` for packaging to a standalone executable

## Requirements

- Python 3.x
- `pygame-ce` (community edition, prebuilt wheels for Python 3.14)
- `neat-python`

## Install

```bash
pip install pygame-ce neat-python
```

## Run

```bash
python main.py
```

The window stays open across generations so you can watch the birds learn in real time.

### Examples

- **Watch evolution:** run `python main.py` and observe generation 1 flailing vs. later generations timing jumps through the 150px gap.
- **Tune evolution:** edit `config-feedforward.txt` (pop 50, fitness threshold 1000) — e.g. raise `pop_size` for more diversity or adjust `fitness_threshold` to stop earlier.
- **Build an executable:** follow `feature.md` for the PyInstaller build guide.

## Project Files

```text
Flappy-Bird-AI/
├── main.py                  # Game loop, NEAT integration, rendering, particles, transitions
├── config-feedforward.txt   # NEAT hyperparameters (5 inputs, 1 output, pop 50)
├── feature.md               # PyInstaller build guide
└── README.md                # This file
```

- `main.py` — game loop, NEAT integration, rendering, particles, transitions
- `config-feedforward.txt` — NEAT hyperparameters (5 inputs, 1 output, pop 50)
- `feature.md` — PyInstaller build guide

## How It Works

- 50 birds per generation, each controlled by a neural network
- **Inputs (5):** bird Y, velocity, distance to pipe, distance to gap top/bottom
- **Output (1):** jump when activation > 0.5
- **Fitness:** +0.1 per frame alive, +5 per pipe passed
- **Collision:** pixel-accurate `pygame.mask.Mask.overlap()` detection

Physics constants live at the top of `main.py` (`GRAVITY = 0.5`, `JUMP_STRENGTH = -8`, `SCROLL_SPEED = 4`, `GAP_SIZE = 150`).

## Screenshots

> _Add a screenshot or GIF of a generation in flight here (e.g. `docs/demo.gif`)._

## License

GPL-3.0 — see [LICENSE](LICENSE).
