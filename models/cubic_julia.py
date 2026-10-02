import math


NAME = "Cubic Julia"

POWER = 3
MAX_ITER = 120

ESCAPE_RADIUS = 8.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS


def parameters(t):
    """
    Evolving Julia constant:

        c = cr + ci*i
    """

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
    """
    Restrained camera.

    Mutation comes from c(t), not from chasing the set around.
    """

    zoom = (
        1.05
        + 0.04 * math.sin(t * 0.07)
    )

    center_x = 0.0
    center_y = 0.0

    view_width = (
        3.05 / zoom
    )

    aspect = height / width

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


def iterate(
    x,
    y,
    cr,
    ci,
):
    """
    Cubic Julia:

        z(n+1) = z(n)^3 + c

    Pixel coordinate x + yi is z(0).
    """

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
