# Writing Models

Models are the mathematical layer of the engine.

The engine owns rendering, multiprocessing, terminal dimensions, styling, and output.

A model owns the equation.

The goal of this interface is to keep models easy to write without adding abstraction to the pixel hot path.

---

## Model contract

Every model module must expose:

```python
NAME
POWER
MAX_ITER

parameters(t)
viewport(t, width, height)
iterate(x, y, p0, p1)
```

Example layout:

```text
models/
├── __init__.py
├── cubic_julia.py
├── tricorn_julia.py
└── your_model.py
```

Run a model with:

```bash
python3 engine.py --model your_model
```

The engine imports `models.your_model`.

---

## Required constants

### `NAME`

Human-readable model name.

```python
NAME = "Cubic Julia"
```

This may be shown in the HUD.

### `POWER`

The dominant polynomial exponent used by the escape-time smoothing function.

```python
POWER = 3
```

For:

```text
z² + c  → POWER = 2
z³ + c  → POWER = 3
z⁴ + c  → POWER = 4
```

For more unusual maps, choose the dominant escape-growth order that best approximates the model.

### `MAX_ITER`

Maximum number of recurrence steps per pixel.

```python
MAX_ITER = 120
```

A pixel that has not escaped after `MAX_ITER` iterations is treated as bounded/interior by the current engine.

Higher values reveal slower escape structure but increase CPU cost.

---

## `parameters(t)`

```python
def parameters(t):
    ...
    return p0, p1
```

This function defines the model's evolving state.

`t` is continuous mathematical time.

It is based on real elapsed time and is independent of render FPS.

That means:

```text
20 FPS
60 FPS
200 FPS
```

all move through the same trajectory at the same `--speed`. A faster renderer simply samples the trajectory more densely.

For a Julia set, `p0` and `p1` are usually the real and imaginary parts of `c(t)`:

```python
def parameters(t):
    cr = (
        -0.46
        + 0.045 * math.cos(t * 0.21)
        + 0.018 * math.sin(t * 0.67)
    )

    ci = (
        0.57
        + 0.045 * math.sin(t * 0.17)
        + 0.018 * math.cos(t * 0.59)
    )

    return cr, ci
```

The engine does not interpret these values. It simply passes them into `iterate()`.

They can represent:

- a Julia constant
- a polynomial coefficient
- a memory coefficient
- a deformation term
- any other two scalar parameters your model needs

Keep them numeric and cheap to compute.

---

## `viewport(t, width, height)`

```python
def viewport(t, width, height):
    ...
    return x_min, x_max, y_min, y_max
```

This maps the terminal grid into the complex plane.

A typical implementation:

```python
def viewport(t, width, height):
    zoom = 1.05

    center_x = 0.0
    center_y = 0.0

    view_width = 3.0 / zoom

    aspect = height / width
    view_height = view_width * aspect * 2.0

    return (
        center_x - view_width * 0.5,
        center_x + view_width * 0.5,
        center_y - view_height * 0.5,
        center_y + view_height * 0.5,
    )
```

### Design recommendation

Keep the camera boring unless camera motion is mathematically meaningful to the model.

A useful rule for generative models is:

```text
wild parameter orbit
        +
stable viewport
        =
visible dynamics
```

If the model already mutates strongly, aggressive panning and zooming can make the interesting structure leave the screen.

When a model disappears, first try widening or stabilizing the viewport before reducing the parameter orbit.

The parameter path is often where the interesting folding and topology changes come from.

---

## `iterate(x, y, p0, p1)`

This is the hot path.

It is called once per sampled terminal cell and may run tens or hundreds of iterations before returning.

Signature:

```python
def iterate(x, y, p0, p1):
    ...
    return iterations, magnitude_squared
```

Return:

```text
iterations
    number of iterations completed before escape

magnitude_squared
    |z|² at escape
```

For bounded points:

```python
return MAX_ITER, 0.0
```

The engine uses the returned escape count and magnitude for smooth styling.

---

# Example: cubic Julia

The pixel coordinate is the initial value `z₀`.

Every pixel in a frame shares the same `c(t)`.

Equation:

```text
z(n+1) = z(n)³ + c(t)
```

Implementation:

```python
import math


NAME = "Cubic Julia"

POWER = 3
MAX_ITER = 120

ESCAPE_RADIUS = 8.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS


def parameters(t):
    cr = (
        -0.46
        + 0.045 * math.cos(t * 0.21)
        + 0.018 * math.sin(t * 0.67)
    )

    ci = (
        0.57
        + 0.045 * math.sin(t * 0.17)
        + 0.018 * math.cos(t * 0.59)
    )

    return cr, ci


def viewport(t, width, height):
    view_width = 3.0

    aspect = height / width
    view_height = view_width * aspect * 2.0

    return (
        -view_width * 0.5,
        view_width * 0.5,
        -view_height * 0.5,
        view_height * 0.5,
    )


def iterate(x, y, cr, ci):
    max_iter = MAX_ITER
    escape_squared = ESCAPE_SQUARED

    for i in range(max_iter):
        x2 = x * x
        y2 = y * y

        new_x = (
            x * (x2 - 3.0 * y2)
            + cr
        )

        new_y = (
            y * (3.0 * x2 - y2)
            + ci
        )

        x = new_x
        y = new_y

        magnitude_squared = (
            x * x
            + y * y
        )

        if magnitude_squared > escape_squared:
            return i, magnitude_squared

    return max_iter, 0.0
```

---

# Dynamical planes vs parameter planes

This distinction matters a lot visually.

## Dynamical plane

Julia-style model:

```text
pixel = starting z
shared parameter = c(t)
```

Every terminal cell asks:

> What happens to this starting point under the current equation?

These models tend to produce the folding, flipping, splitting, helix, and topology-changing behavior that works especially well for generative animation.

Example:

```text
z(n+1) = z(n)³ + c(t)
```

## Parameter plane

Mandelbrot-style model:

```text
pixel = parameter c
z₀ = 0
```

Every terminal cell asks:

> What happens to the orbit if the equation uses this parameter?

Example:

```text
z(n+1) = z(n)² + c
z₀ = 0
```

Parameter planes are maps of a family of systems rather than one evolving dynamical plane.

They are often visually more static unless another meaningful coefficient evolves.

Do not fake dynamics by moving the camera aggressively unless that is what you actually want.

---

# Parameter paths

A parameter path is often more important than the equation choice.

This:

```python
cr = base + a * math.cos(t * f1)
ci = base + b * math.sin(t * f2)
```

moves through parameter space smoothly.

Adding a second frequency:

```python
cr = (
    base
    + a * math.cos(t * f1)
    + b * math.sin(t * f2)
)
```

creates a less repetitive orbit.

Different frequencies create long, quasi-periodic paths that may take a long time to repeat.

### Important

If you find a path that produces interesting flips, folds, or vortices, preserve it.

If the fractal leaves the screen, fix the viewport first.

Reducing the parameter amplitude can remove the exact excursions that caused the interesting behavior.

---

# Escape radius

A typical model defines:

```python
ESCAPE_RADIUS = 8.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS
```

Then checks:

```python
magnitude_squared = x * x + y * y

if magnitude_squared > ESCAPE_SQUARED:
    return i, magnitude_squared
```

Using squared magnitude avoids calculating a square root every iteration.

Different equations may need different practical escape radii.

---

# Performance rules

`iterate()` is the most performance-sensitive function in the entire project.

Treat it differently from normal Python application code.

Prefer:

```python
x2 = x * x
y2 = y * y
```

over:

```python
z = complex(x, y)
z = z ** 3
```

when the expanded arithmetic is straightforward.

Prefer local scalar arithmetic over:

- dictionaries
- classes
- object allocation
- callbacks
- dynamic imports
- generic expression evaluators

inside `iterate()`.

The engine resolves the model once per worker.

Do not add model lookup logic inside the pixel loop.

---

## Good hot-loop shape

```python
def iterate(x, y, cr, ci):
    max_iter = MAX_ITER
    escape_squared = ESCAPE_SQUARED

    for i in range(max_iter):
        ...
        if magnitude_squared > escape_squared:
            return i, magnitude_squared

    return max_iter, 0.0
```

Simple is fast.

---

# Models with memory

The model may keep local recurrence state inside `iterate()`.

For example, Phoenix-style systems use the previous orbit position:

```text
z(n+1) = z(n)² + c + p*z(n-1)
```

That does not require any engine changes.

Example:

```python
previous_r = 0.0
previous_i = 0.0

for i in range(MAX_ITER):
    ...
    previous_r = zr
    previous_i = zi
    zr = new_zr
    zi = new_zi
```

The memory belongs to the orbit for that pixel.

---

# Rational maps

Rational maps also fit the current contract:

```text
z(n+1) = z² + c + λ/z
```

Be careful around poles such as `z = 0`.

Use a small epsilon check before dividing:

```python
denominator = x * x + y * y

if denominator < 1.0e-12:
    return i, 1.0e24
```

These models may be slower because division is more expensive than the multiply/add-heavy polynomial models.

---

# Choosing `MAX_ITER`

There is no universal best value.

As a rough starting point:

```text
simple quadratic maps     100–160
cubic / quartic maps      100–140
very expensive rational   80–130
```

Too low:

- fine boundary structure disappears
- points are classified as bounded too early

Too high:

- CPU cost increases
- large bounded regions can dominate render time

Tune it for the model, not for a target FPS.

---

# Writing a new model

A practical workflow:

1. copy a nearby model
2. replace the equation in `iterate()`
3. choose a reasonable fixed viewport
4. find a parameter region that produces structure
5. add a slow parameter orbit
6. only then add very small viewport breathing if desired

Do not begin by animating the camera.

You want to know whether the equation itself is interesting.

---

# Minimal template

```python
import math


NAME = "My Model"

POWER = 2
MAX_ITER = 120

ESCAPE_RADIUS = 8.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS


def parameters(t):
    p0 = 0.0
    p1 = 0.0

    return p0, p1


def viewport(t, width, height):
    center_x = 0.0
    center_y = 0.0

    view_width = 3.0

    aspect = height / width
    view_height = view_width * aspect * 2.0

    return (
        center_x - view_width * 0.5,
        center_x + view_width * 0.5,
        center_y - view_height * 0.5,
        center_y + view_height * 0.5,
    )


def iterate(x, y, p0, p1):
    max_iter = MAX_ITER
    escape_squared = ESCAPE_SQUARED

    for i in range(max_iter):
        # Apply your recurrence here.
        #
        # Update x and y.

        magnitude_squared = (
            x * x
            + y * y
        )

        if magnitude_squared > escape_squared:
            return i, magnitude_squared

    return max_iter, 0.0
```

---

# What currently requires engine work

The current engine assumes an escape-time field.

Models that naturally return:

```text
escaped after N iterations
```

fit directly.

Other fractal families may need a new rendering contract, including:

- Newton/root-basin fractals
- convergence coloring
- orbit traps
- Lyapunov fields
- distance estimators
- density / histogram renderers

Those are good future extensions, but they are meaningfully different from the v1 escape-time model interface.

---

# Principle

The model should describe the system.

The viewport should make the system visible.

The renderer should not manufacture the interesting behavior.

If the math looks raw, let it look raw.
