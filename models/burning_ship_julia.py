# models/burning_ship_julia.py

import math


NAME = "Burning Ship Julia"

POWER = 2
MAX_ITER = 110

ESCAPE_RADIUS = 4.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS


def parameters(t):
    """
    Orbit through a much richer Burning Ship Julia region.

    Wider movement is intentional.
    """
    cr = (
        -0.52
        + 0.20 * math.cos(t * 0.13)
        + 0.07 * math.sin(t * 0.41)
    )

    ci = (
        -0.86
        + 0.13 * math.sin(t * 0.11)
        + 0.045 * math.cos(t * 0.37)
    )

    return cr, ci


def viewport(t, width, height):
    # Fixed-ish camera. Let c(t) do the interesting work.
    zoom = (
        1.02
        + 0.04 * math.sin(t * 0.07)
    )

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


def iterate(x, y, cr, ci):
    max_iter = MAX_ITER
    escape_squared = ESCAPE_SQUARED

    for i in range(max_iter):
        ax = abs(x)
        ay = abs(y)

        new_x = (
            ax * ax
            - ay * ay
            + cr
        )

        new_y = (
            2.0 * ax * ay
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
