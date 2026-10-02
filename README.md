# phase

A small fractal generator for the terminal.

I made this because I wanted a local way to mess around with Julia sets, vortex-like behavior, and other escape-time systems without needing a browser or a big graphics stack.

The math is definitely above my pay grade in places, and I used AI tools while building it, but the project was mostly an excuse to experiment and learn.

I’m also a freak for CLI tools, so it lives in the terminal.

![phase demo](docs/phase-demo.gif)

## run

```bash
python3 engine.py --model cubic_julia
```

A few other models:

```bash
python3 engine.py --model cubic_julia_vortex
python3 engine.py --model tricorn_julia
python3 engine.py --model phoenix
```

Slow things down:

```bash
python3 engine.py --model cubic_julia_vortex --speed 0.25
```

The renderer is standard-library Python.

The optional palette picker needs:

```bash
python3 -m pip install simple-term-menu
python3 palette_picker.py
```

If you want to make your own model, there’s more documentation in:

[`models/MODELS_README.md`](models/MODELS_README.md)

MIT licensed.
