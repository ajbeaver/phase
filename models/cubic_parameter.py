import math


NAME = "Cubic Linear Julia"

POWER = 3
MAX_ITER = 120

ESCAPE_RADIUS = 8.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS


# Fixed constant.
#
# a(t) is what evolves in this model.
C_REAL = -0.18
C_IMAG = 0.64


def parameters(t):
    """
    Evolving complex linear coefficient:

        a = ar + ai*i

    Equation:

        z(n+1) = z(n)^3 + a(t)z(n) + c
    """

    ar = (
        -0.25
        + 0.38 * math.cos(t * 0.13)
        + 0.10 * math.sin(t * 0.41)
    )

    ai = (
        0.34 * math.sin(t * 0.11)
        + 0.12 * math.cos(t * 0.37)
    )

    return ar, ai


def viewport(t, width, height):
    """
    Wide, nearly stationary framing.

    a(t) supplies the deformation.
    """

    zoom = (
        1.06
        + 0.05 * math.sin(t * 0.067)
    )

    center_x = 0.0
    center_y = 0.0

    view_width = (
        3.15 / zoom
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
    ar,
    ai,
):
    """
    Dynamical plane for:

        z(n+1) = z(n)^3 + a(t)z(n) + c

    Pixel coordinate x + yi is z(0).

    Unlike the old parameter-plane version, the entire screen
    now samples the dynamics of one changing equation.
    """

    zr = x
    zi = y

    cr = C_REAL
    ci = C_IMAG

    max_iter = MAX_ITER
    escape_squared = ESCAPE_SQUARED

    for i in range(max_iter):
        zr2 = zr * zr
        zi2 = zi * zi

        # z^3
        cubic_r = (
            zr
            * (zr2 - 3.0 * zi2)
        )

        cubic_i = (
            zi
            * (3.0 * zr2 - zi2)
        )

        # a*z
        linear_r = (
            ar * zr
            - ai * zi
        )

        linear_i = (
            ar * zi
            + ai * zr
        )

        new_zr = (
            cubic_r
            + linear_r
            + cr
        )

        new_zi = (
            cubic_i
            + linear_i
            + ci
        )

        zr = new_zr
        zi = new_zi

        magnitude_squared = (
            zr * zr
            + zi * zi
        )

        if magnitude_squared > escape_squared:
            return i, magnitude_squared

    return max_iter, 0.0
