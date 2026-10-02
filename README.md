# phase

> **The renderer samples the dynamics. It does not choreograph them.**

A fast terminal fractal engine for watching complex dynamical systems evolve in real time.

`phase` started as a cubic Julia experiment and turned into a modular escape-time engine with multiprocessing, truecolor ANSI output, time-based evolution, and a growing collection of deliberately raw fractal systems.

The point is not to force every equation into being pretty.

The point is to give the math enough room, enough speed, and enough resolution to show what it actually does.

---

## Preview

Recommended media path:

```text
docs/phase-demo.gif
```

Once the file is there, GitHub will render it directly in the README with:

```md
![phase demo](docs/phase-demo.gif)
```

---

## What it does

- renders fractals directly in your terminal
- uses truecolor ANSI output
- runs the math across multiple worker processes
- evolves models in real time instead of tying animation speed to FPS
- keeps the rendering engine separate from the equations
- lets you select models with a flag
- includes a palette picker for quickly changing the visual field
- keeps the camera intentionally restrained so the dynamics stay responsible for the motion

The engine is optimized for **escape-time dynamical systems**.

---

## Quick start

Clone the repo and run:

```bash
python3 engine.py --model cubic_julia --hud
```

Try another model:

```bash
python3 engine.py --model tricorn_julia --hud
```

Slow the mathematical evolution without capping the renderer:

```bash
python3 engine.py --model cubic_julia_vortex --speed 0.25 --hud
```

The renderer remains uncapped. `--speed` only changes how quickly the model moves through mathematical time.

---

## Models

| Model | Equation / behavior |
| --- | --- |
| Cubic Julia | `z → z³ + c(t)` |
| Cubic Julia Vortex | same family, wider parameter orbit |
| Tricorn Julia | `z → conj(z)² + c(t)` |
| Burning Ship Julia | absolute-value folding |
| Celtic Julia | real-axis folding |
| Quartic Julia | `z → z⁴ + c(t)` |
| Phoenix Julia | recurrence with memory |
| Cubic Linear Julia | `z → z³ + a(t)z + c` |
| Rational Pole Julia | `z → z² + c(t) + λ/z` |
| Mandelbrot | canonical parameter plane |

Some are dense. Some are sparse. Some build slowly and suddenly fold into themselves. Some look almost broken until they hit a rich region.

That is intentional.

---

## The engine

The engine handles:

```text
time
terminal dimensions
multiprocessing
sampling
escape-time styling
ANSI output
HUD
```

The model handles:

```text
equation
parameter evolution
viewport
escape behavior
```

A model does not need to know anything about terminal output, workers, ANSI colors, or rendering infrastructure.

The hot path stays intentionally small so the engine can remain fast in CPython.

---

## Controls

Common flags:

```bash
--model MODEL
--speed FLOAT
--workers N
--chunks-per-worker N
--style-buckets N
--hud
```

Examples:

```bash
python3 engine.py --model phoenix --speed 0.2
python3 engine.py --model quartic_julia --hud
python3 engine.py --model tricorn_julia --workers 8 --hud
```

---

## Palette picker

The renderer uses 24-bit terminal color.

Run:

```bash
python3 palette_picker.py
```

Use the arrow keys to move, Enter to select, and choose a color family / shade.

The picker rewrites the engine's color-range variables so the selected palette becomes ordinary source configuration.

The palette changes presentation, not the underlying model.

---

## Make your own model

Models are small Python modules with a deliberately narrow interface.

See:

```text
models/MODELS_README.md
```

for the model contract, examples, performance notes, dynamical-vs-parameter-plane behavior, and guidance for designing parameter paths that preserve the equation's behavior.

---

## Requirements

Python 3.10+ is recommended.

The renderer itself uses only the Python standard library.

For the optional palette picker:

```bash
python3 -m pip install simple-term-menu
```

or:

```bash
pip install -r requirements.txt
```

---

## Notes on performance

The engine uses persistent worker processes and splits the terminal into render bands.

On dense Julia-family models, a single frame may require hundreds of thousands to millions of recurrence steps. Across a live session, the engine can easily evaluate tens of millions of complex iterations per second depending on the model, terminal size, and hardware.

No FPS cap is applied.

Fast machines simply sample the same mathematical trajectory more densely.

---

## License

MIT License.

See `LICENSE` for the full text.
