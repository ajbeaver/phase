# models/rational_pole_julia.py

import math


NAME = "Rational Pole Julia"

POWER = 2
MAX_ITER = 130

ESCAPE_RADIUS = 12.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS

LAMBDA_REAL = 0.12
LAMBDA_IMAG = 0.05

POLE_EPSILON = 1.0e-12


def parameters(t):
    cr = (
        -0.32
        + 0.085 * math.cos(t * 0.15)
        + 0.025 * math.sin(t * 0.43)
    )

    ci = (
        0.53
        + 0.080 * math.sin(t * 0.13)
        - 0.022 * math.cos(t * 0.37)
    )

    return cr, ci


def viewport(t, width, height):
    zoom = (
        1.02
        + 0.04 * math.sin(t * 0.06)
    )

    center_x = 0.0
    center_y = 0.0

    view_width = 3.4 / zoom

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

    lr = LAMBDA_REAL
    li = LAMBDA_IMAG

    for i in range(max_iter):
        denominator = (
            x * x
            + y * y
        )

        # Approaching the pole at z = 0 means the rational term
        # tends toward infinity.
        if denominator < POLE_EPSILON:
            return i, 1.0e24

        inverse_real = (
            x / denominator
        )

        inverse_imag = (
            -y / denominator
        )

        pole_real = (
            lr * inverse_real
            - li * inverse_imag
        )

        pole_imag = (
            lr * inverse_imag
            + li * inverse_real
        )

        x2 = x * x
        y2 = y * y

        new_x = (
            x2
            - y2
            + cr
            + pole_real
        )

        new_y = (
            2.0 * x * y
            + ci
            + pole_imag
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
