# models/celtic_julia.py

import math


NAME = "Celtic Julia"

POWER = 2
MAX_ITER = 130

ESCAPE_RADIUS = 8.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS


def parameters(t):
    cr = (
        -0.44
        + 0.12 * math.cos(t * 0.14)
        + 0.035 * math.sin(t * 0.46)
    )

    ci = (
        0.56
        + 0.11 * math.sin(t * 0.12)
        - 0.030 * math.cos(t * 0.41)
    )

    return cr, ci


def viewport(t, width, height):
    zoom = (
        1.05
        + 0.05 * math.sin(t * 0.065)
    )

    center_x = 0.0
    center_y = 0.0

    view_width = 3.1 / zoom

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
            abs(x2 - y2)
            + cr
        )

        new_y = (
            2.0 * x * y
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
