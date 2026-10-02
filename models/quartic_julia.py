# models/quartic_julia.py

import math


NAME = "Quartic Julia"

POWER = 4
MAX_ITER = 110

ESCAPE_RADIUS = 8.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS


def parameters(t):
    cr = (
        -0.22
        + 0.075 * math.cos(t * 0.16)
        + 0.025 * math.sin(t * 0.47)
    )

    ci = (
        0.48
        + 0.070 * math.sin(t * 0.13)
        - 0.022 * math.cos(t * 0.39)
    )

    return cr, ci


def viewport(t, width, height):
    zoom = (
        1.10
        + 0.05 * math.sin(t * 0.07)
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
        x2 = x * x
        y2 = y * y

        # z^4
        real = (
            x2 * x2
            - 6.0 * x2 * y2
            + y2 * y2
        )

        imag = (
            4.0
            * x
            * y
            * (x2 - y2)
        )

        x = real + cr
        y = imag + ci

        magnitude_squared = (
            x * x
            + y * y
        )

        if magnitude_squared > escape_squared:
            return i, magnitude_squared

    return max_iter, 0.0
