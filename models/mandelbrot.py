NAME = "Mandelbrot"

POWER = 2
MAX_ITER = 140

ESCAPE_RADIUS = 2.0
ESCAPE_SQUARED = ESCAPE_RADIUS * ESCAPE_RADIUS


def parameters(t):
    # Canonical Mandelbrot has no external evolving parameter.
    return 0.0, 0.0


def viewport(t, width, height):
    """
    Stable view of the actual Mandelbrot parameter plane.

    This model is intentionally not animated through camera tricks.
    """

    center_x = -0.50
    center_y = 0.0

    view_width = 3.20

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
    p0,
    p1,
):
    """
    Classic Mandelbrot:

        z(n+1) = z(n)^2 + c
        z(0) = 0

    Pixel coordinate x + yi is c.
    """

    cr = x
    ci = y

    zr = 0.0
    zi = 0.0

    max_iter = MAX_ITER
    escape_squared = ESCAPE_SQUARED

    for i in range(max_iter):
        zr2 = zr * zr
        zi2 = zi * zi

        new_zr = (
            zr2
            - zi2
            + cr
        )

        new_zi = (
            2.0 * zr * zi
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
