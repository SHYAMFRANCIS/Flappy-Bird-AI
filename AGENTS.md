# AGENTS.md

NEAT neuroevolution AI for Flappy Bird. No tests, no lint, no CI.

## Run

```
pip install pygame-ce neat-python
python main.py
```

## Files

- `main.py` (~300 lines) — Game loop, Bird/Pipe classes, NEAT integration (`eval_genomes`), rendering, particles, transition overlay.
- `config-feedforward.txt` — NEAT hyperparameters: 5 inputs / 1 output / population 50.
- `feature.md` — PyInstaller build guide (`pyinstaller --onefile --windowed --name FlappyBird main.py`).

## Architecture

- **Inputs (5):** bird Y, velocity, distance to pipe, distance to gap top, distance to gap bottom.
- **Output (1):** jump when activation > 0.5.
- **Fitness:** +0.1 per frame survived, +5 per pipe passed.
- **Collision:** `pygame.mask.Mask.overlap()` for pixel-accurate circle↔rect detection.
- **UI:** Gradient sky, clouds, pipe caps, detailed bird sprite (eye/beak/wing), particle burst on death, generation transition overlay.
- The game draws shapes exclusively — no image assets required.
- License: GPL-3.0.
