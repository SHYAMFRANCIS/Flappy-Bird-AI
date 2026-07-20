# AGENTS.md

Single-file Python/Pygame Flappy Bird game. No tests, no lint, no CI.

## Run

```
pip install pygame
python main.py
```

## Notes

- All game logic lives in `main.py` (154 lines). Bird/pipe classes, rendering, and game loop are all here.
- The game draws shapes (circles, rects) — the `imgs/` directory referenced in README does not exist.
- Despite the repo name, there is no AI implementation yet; the bird is player-controlled (spacebar/click).
- `QWEN.md` contains stale info (wrong paths, references to missing assets). Treat `main.py` as the source of truth.
- License: GPL-3.0.
