import math


NAME = "Phoenix Julia"

POWER = 2
MAX_ITER = 140

ESCAPE_RADIUS = 4.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS


# Phoenix memory coefficient.
#
# Keeping this fixed gives c(t) room to expose the recurrence itself.
P_REAL = -0.52
P_IMAG = 0.0


def parameters(t):
    """
    Evolving complex Julia constant c(t).

    The Phoenix memory coefficient p stays fixed.
    """

    cr = (
        0.28
        + 0.16 * math.cos(t * 0.14)
        + 0.055 * math.sin(t * 0.43)
    )

    ci = (
        0.03
        + 0.17 * math.sin(t * 0.12)
        + 0.045 * math.cos(t * 0.31)
    )

    return cr, ci


def viewport(t, width, height):
    """
    Mostly fixed frame.

    The recurrence and c(t) generate the motion.
    """

    zoom = (
        1.02
        + 0.04 * math.sin(t * 0.061)
    )

    center_x = 0.0
    center_y = 0.0

    view_width = (
        3.25 / zoom
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
    Phoenix Julia:

        z(n+1) = z(n)^2 + c(t) + p*z(n-1)

    Pixel coordinate x + yi is z(0).

    Every pixel follows the same changing recurrence.
    """

    zr = x
    zi = y

    previous_r = 0.0
    previous_i = 0.0

    pr = P_REAL
    pi = P_IMAG

    max_iter = MAX_ITER
    escape_squared = ESCAPE_SQUARED

    for i in range(max_iter):
        zr2 = zr * zr
        zi2 = zi * zi

        memory_r = (
            pr * previous_r
            - pi * previous_i
        )

        memory_i = (
            pr * previous_i
            + pi * previous_r
        )

        new_zr = (
            zr2
            - zi2
            + cr
            + memory_r
        )

        new_zi = (
            2.0 * zr * zi
            + ci
            + memory_i
        )

        previous_r = zr
        previous_i = zi

        zr = new_zr
        zi = new_zi

        magnitude_squared = (
            zr * zr
            + zi * zi
        )

        if magnitude_squared > escape_squared:
            return i, magnitude_squared

    return max_iter, 0.0
