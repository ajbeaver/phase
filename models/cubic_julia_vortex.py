# models/cubic_julia_vortex.py

import math


NAME = "Cubic Julia Vortex"

POWER = 3
MAX_ITER = 120

ESCAPE_RADIUS = 8.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS


def parameters(t):
    """
    Original wider orbit.

    This is where the flipping, folding, and vortex behavior
    was actually coming from.
    """
    cr = (
        -0.188
        + 0.072 * math.cos(t * 0.19)
        + 0.031 * math.sin(t * 0.47)
    )

    ci = (
        0.646
        + 0.068 * math.sin(t * 0.17)
        - 0.028 * math.cos(t * 0.39)
    )

    return cr, ci


def viewport(t, width, height):
    """
    Keep the camera mostly fixed and wide enough to contain
    the more violent parameter excursions.

    The equation supplies the movement.
    """

    zoom = (
        1.28
        + 0.06 * math.sin(t * 0.07)
    )

    center_x = 0.0
    center_y = 0.0

    view_width = (
        3.15 / zoom
    )

    aspect = (
        height / width
    )

    view_height = (
        view_width
        * aspect
        * 2.0
    )

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
