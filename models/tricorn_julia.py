# models/tricorn_julia.py

import math


NAME = "Tricorn Julia"

POWER = 2
MAX_ITER = 140

ESCAPE_RADIUS = 8.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS


def parameters(t):
    cr = (
        -0.10
        + 0.18 * math.cos(t * 0.15)
        + 0.05 * math.sin(t * 0.49)
    )

    ci = (
        0.62
        + 0.14 * math.sin(t * 0.12)
        + 0.04 * math.cos(t * 0.43)
    )

    return cr, ci


def viewport(t, width, height):
    # Keep the camera restrained.
    # The conjugate dynamics provide the motion.
    zoom = (
        1.08
        + 0.05 * math.sin(t * 0.08)
    )

    center_x = 0.0
    center_y = 0.0

    view_width = 3.15 / zoom

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
        x2 = x * x
        y2 = y * y

        new_x = (
            x2
            - y2
            + cr
        )

        new_y = (
            -2.0 * x * y
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
