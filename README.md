# Flappy Bird AI

NEAT neuroevolution AI that teaches birds to play Flappy Bird. No image assets — all shapes drawn with `pygame.draw`.

## Requirements

- Python 3.x
- `pygame-ce` (community edition, prebuilt wheels for Python 3.14)
- `neat-python`

## Run

```
pip install pygame-ce neat-python
python main.py
```

The window stays open across generations so you can watch the birds learn in real time.

## Project Files

- `main.py` — Game loop, NEAT integration, rendering, particles, transitions
- `config-feedforward.txt` — NEAT hyperparameters (5 inputs, 1 output, pop 50)
- `feature.md` — PyInstaller build guide

## How It Works

- 50 birds per generation, each controlled by a neural network
- **Inputs (5):** bird Y, velocity, distance to pipe, distance to gap top/bottom
- **Output (1):** jump when activation > 0.5
- **Fitness:** +0.1 per frame alive, +5 per pipe passed
- **Collision:** Pixel-accurate `pygame.mask.Mask.overlap()` detection
