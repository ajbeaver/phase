#!/usr/bin/env python3

import argparse
import importlib
import math
import os
import shutil
import sys
import time
from multiprocessing import get_context


# ============================================================
# VISUAL CONFIG
# ============================================================

# ASCII density ramp.
PALETTE = " .:-=+*#%@"
PALETTE_LAST = len(PALETTE) - 1

# Interior / bounded region.
INSIDE_RGB = (10, 8, 18)

# Escape-field colors.
#
# These are the low and high ends of the animated color ranges.
#
# Current values preserve the purple/blue look we've been using.
RED_LOW = 45
RED_HIGH = 165

GREEN_LOW = 20
GREEN_HIGH = 65

BLUE_LOW = 120
BLUE_HIGH = 255

# Color animation through the escape field.
COLOR_SPATIAL_1 = 10.0
COLOR_SPATIAL_2 = 6.0

COLOR_TIME_1 = 0.55
COLOR_TIME_2 = 0.35

# Lower values = smoother RGB gradients.
# Higher values = more aggressively quantized colors.
COLOR_QUANTIZATION = 16

# Number of precomputed style entries.
STYLE_BUCKETS = 32


# ============================================================
# ENGINE CONFIG
# ============================================================

DEFAULT_CHUNKS_PER_WORKER = 4
DEFAULT_SPEED = 1.0

RESET = "\033[0m"

INSIDE_COLOR = (
    f"\033[38;2;"
    f"{INSIDE_RGB[0]};"
    f"{INSIDE_RGB[1]};"
    f"{INSIDE_RGB[2]}m"
)


# ============================================================
# WORKER STATE
# ============================================================

_MODEL_ITERATE = None
_MODEL_MAX_ITER = None
_MODEL_INV_MAX_ITER = None
_MODEL_INV_LOG_POWER = None

_STYLE_BASIS_CACHE = {}

_STYLE_TABLE_T = None
_STYLE_TABLE_BUCKETS = None
_STYLE_TABLE = None

_X_CACHE_KEY = None
_X_CACHE = None


# ============================================================
# MODEL LOADING
# ============================================================

def import_model(model_name):
    try:
        model = importlib.import_module(
            f"models.{model_name}"
        )

    except ModuleNotFoundError as exc:
        raise SystemExit(
            f"Could not load model "
            f"'models.{model_name}'"
        ) from exc

    required = (
        "NAME",
        "POWER",
        "MAX_ITER",
        "parameters",
        "viewport",
        "iterate",
    )

    missing = [
        name
        for name in required
        if not hasattr(model, name)
    ]

    if missing:
        raise SystemExit(
            f"Model '{model_name}' is missing: "
            + ", ".join(missing)
        )

    if model.POWER <= 1:
        raise SystemExit(
            f"Model '{model_name}' must have POWER > 1"
        )

    if model.MAX_ITER < 1:
        raise SystemExit(
            f"Model '{model_name}' must have MAX_ITER >= 1"
        )

    return model


def init_worker(model_name):
    global _MODEL_ITERATE
    global _MODEL_MAX_ITER
    global _MODEL_INV_MAX_ITER
    global _MODEL_INV_LOG_POWER

    model = import_model(
        model_name
    )

    _MODEL_ITERATE = (
        model.iterate
    )

    _MODEL_MAX_ITER = (
        model.MAX_ITER
    )

    _MODEL_INV_MAX_ITER = (
        1.0 / model.MAX_ITER
    )

    _MODEL_INV_LOG_POWER = (
        1.0
        / math.log(
            model.POWER
        )
    )


# ============================================================
# SMOOTH ESCAPE
# ============================================================

def smooth_iter(
    iterations,
    magnitude_squared,
):
    if iterations == _MODEL_MAX_ITER:
        return float(
            _MODEL_MAX_ITER
        )

    log_magnitude = (
        0.5
        * math.log(
            magnitude_squared
        )
    )

    return (
        iterations
        + 1
        - math.log(
            log_magnitude
        )
        * _MODEL_INV_LOG_POWER
    )


# ============================================================
# STYLE TABLE
# ============================================================

def build_style_basis(
    bucket_count,
):
    cached = (
        _STYLE_BASIS_CACHE.get(
            bucket_count
        )
    )

    if cached is not None:
        return cached

    basis = []

    last_index = (
        bucket_count - 1
    )

    for index in range(
        bucket_count
    ):
        if last_index:
            n = (
                index
                / last_index
            )
        else:
            n = 0.0

        glyph_n = math.sqrt(n)

        glyph_index = int(
            glyph_n
            * PALETTE_LAST
        )

        glyph_index = max(
            0,
            min(
                PALETTE_LAST,
                glyph_index,
            ),
        )

        char = (
            PALETTE[glyph_index]
        )

        angle1 = (
            n
            * COLOR_SPATIAL_1
        )

        angle2 = (
            n
            * COLOR_SPATIAL_2
        )

        basis.append(
            (
                char,
                math.sin(angle1),
                math.cos(angle1),
                math.sin(angle2),
                math.cos(angle2),
            )
        )

    _STYLE_BASIS_CACHE[
        bucket_count
    ] = basis

    return basis


def quantize_color(value):
    q = COLOR_QUANTIZATION

    if q <= 1:
        return max(
            0,
            min(
                255,
                int(value),
            ),
        )

    value = (
        int(value)
        // q
    ) * q

    return max(
        0,
        min(
            255,
            value,
        ),
    )


def build_frame_style_table(
    t,
    bucket_count,
):
    basis = build_style_basis(
        bucket_count
    )

    phase1 = (
        t
        * COLOR_TIME_1
    )

    phase2 = (
        t
        * COLOR_TIME_2
    )

    sin_phase1 = math.sin(
        phase1
    )

    cos_phase1 = math.cos(
        phase1
    )

    sin_phase2 = math.sin(
        phase2
    )

    cos_phase2 = math.cos(
        phase2
    )

    table = []
    color_cache = {}

    red_range = (
        RED_HIGH
        - RED_LOW
    )

    green_range = (
        GREEN_HIGH
        - GREEN_LOW
    )

    blue_range = (
        BLUE_HIGH
        - BLUE_LOW
    )

    for (
        char,
        sin1,
        cos1,
        sin2,
        cos2,
    ) in basis:

        wave1 = (
            0.5
            + 0.5
            * (
                sin1
                * cos_phase1
                + cos1
                * sin_phase1
            )
        )

        wave2 = (
            0.5
            + 0.5
            * (
                sin2
                * cos_phase2
                - cos2
                * sin_phase2
            )
        )

        r = quantize_color(
            RED_LOW
            + red_range
            * wave1
        )

        g = quantize_color(
            GREEN_LOW
            + green_range
            * wave2
        )

        b = quantize_color(
            BLUE_LOW
            + blue_range
            * wave1
        )

        rgb = (
            r,
            g,
            b,
        )

        color = (
            color_cache.get(
                rgb
            )
        )

        if color is None:
            color = (
                f"\033[38;2;"
                f"{r};{g};{b}m"
            )

            color_cache[
                rgb
            ] = color

        table.append(
            (
                char,
                color,
            )
        )

    return table


def get_style_table(
    t,
    bucket_count,
):
    global _STYLE_TABLE_T
    global _STYLE_TABLE_BUCKETS
    global _STYLE_TABLE

    if (
        _STYLE_TABLE is not None
        and _STYLE_TABLE_T == t
        and _STYLE_TABLE_BUCKETS
        == bucket_count
    ):
        return _STYLE_TABLE

    _STYLE_TABLE = (
        build_frame_style_table(
            t,
            bucket_count,
        )
    )

    _STYLE_TABLE_T = t
    _STYLE_TABLE_BUCKETS = (
        bucket_count
    )

    return _STYLE_TABLE


# ============================================================
# X COORDINATE CACHE
# ============================================================

def get_x_coordinates(
    width,
    x_min,
    x_max,
):
    global _X_CACHE_KEY
    global _X_CACHE

    key = (
        width,
        x_min,
        x_max,
    )

    if key == _X_CACHE_KEY:
        return _X_CACHE

    x_step = (
        x_max
        - x_min
    ) / width

    _X_CACHE = [
        x_min
        + col * x_step
        for col in range(
            width
        )
    ]

    _X_CACHE_KEY = key

    return _X_CACHE


# ============================================================
# WORKER RENDER
# ============================================================

def render_band(task):
    (
        start_row,
        end_row,
        width,
        height,
        x_min,
        x_max,
        y_min,
        y_max,
        p0,
        p1,
        t,
        style_buckets,
    ) = task

    style_table = (
        get_style_table(
            t,
            style_buckets,
        )
    )

    xs = get_x_coordinates(
        width,
        x_min,
        x_max,
    )

    y_step = (
        y_max
        - y_min
    ) / height

    local_iterate = (
        _MODEL_ITERATE
    )

    local_smooth = (
        smooth_iter
    )

    local_style_table = (
        style_table
    )

    local_max_iter = (
        _MODEL_MAX_ITER
    )

    local_inv_max_iter = (
        _MODEL_INV_MAX_ITER
    )

    local_inside_color = (
        INSIDE_COLOR
    )

    local_reset = RESET

    style_last = (
        style_buckets - 1
    )

    rendered_rows = []

    for row in range(
        start_row,
        end_row,
    ):
        y = (
            y_max
            - row
            * y_step
        )

        line_parts = []
        last_color = None

        for x in xs:
            (
                iterations,
                magnitude_squared,
            ) = local_iterate(
                x,
                y,
                p0,
                p1,
            )

            if (
                iterations
                == local_max_iter
            ):
                char = " "
                color = (
                    local_inside_color
                )

            else:
                value = (
                    local_smooth(
                        iterations,
                        magnitude_squared,
                    )
                )

                n = (
                    value
                    * local_inv_max_iter
                )

                if n <= 0.0:
                    index = 0

                elif n >= 1.0:
                    index = (
                        style_last
                    )

                else:
                    index = int(
                        n
                        * style_last
                    )

                (
                    char,
                    color,
                ) = (
                    local_style_table[
                        index
                    ]
                )

            if (
                color
                != last_color
            ):
                line_parts.append(
                    color
                )

                last_color = color

            line_parts.append(
                char
            )

        line_parts.append(
            local_reset
        )

        rendered_rows.append(
            "".join(
                line_parts
            )
        )

    return (
        start_row,
        rendered_rows,
    )


# ============================================================
# TASK BUILDING
# ============================================================

def build_tasks(
    workers,
    chunks_per_worker,
    width,
    height,
    x_min,
    x_max,
    y_min,
    y_max,
    p0,
    p1,
    t,
    style_buckets,
):
    chunk_count = max(
        1,
        min(
            height,
            workers
            * chunks_per_worker,
        ),
    )

    tasks = []

    for chunk_index in range(
        chunk_count
    ):
        start_row = (
            chunk_index
            * height
            // chunk_count
        )

        end_row = (
            (
                chunk_index + 1
            )
            * height
            // chunk_count
        )

        if (
            start_row
            == end_row
        ):
            continue

        tasks.append(
            (
                start_row,
                end_row,
                width,
                height,
                x_min,
                x_max,
                y_min,
                y_max,
                p0,
                p1,
                t,
                style_buckets,
            )
        )

    return tasks


# ============================================================
# FRAME RENDER
# ============================================================

def render_frame(
    model,
    t,
    pool,
    workers,
    chunks_per_worker,
    style_buckets,
    hud_enabled,
):
    terminal = (
        shutil.get_terminal_size()
    )

    width = max(
        1,
        terminal.columns,
    )

    # Leave a safety row at the bottom so the terminal does not
    # scroll when the final cell is written.
    #
    # HUD gets one additional dedicated row.
    reserved_rows = (
        2
        if hud_enabled
        else 1
    )

    height = max(
        1,
        terminal.lines
        - reserved_rows,
    )

    p0, p1 = (
        model.parameters(t)
    )

    (
        x_min,
        x_max,
        y_min,
        y_max,
    ) = model.viewport(
        t,
        width,
        height,
    )

    tasks = build_tasks(
        workers,
        chunks_per_worker,
        width,
        height,
        x_min,
        x_max,
        y_min,
        y_max,
        p0,
        p1,
        t,
        style_buckets,
    )

    worker_results = (
        pool.map(
            render_band,
            tasks,
        )
    )

    rows = (
        [None] * height
    )

    for (
        start_row,
        band_rows,
    ) in worker_results:

        for (
            offset,
            row_text,
        ) in enumerate(
            band_rows
        ):
            rows[
                start_row
                + offset
            ] = row_text

    return (
        "\n".join(
            rows
        ),
        width,
        height,
    )


# ============================================================
# CPU DETECTION
# ============================================================

def available_cpu_count():
    process_count = getattr(
        os,
        "process_cpu_count",
        None,
    )

    if process_count is not None:
        count = (
            process_count()
        )
    else:
        count = (
            os.cpu_count()
        )

    if count is None:
        return 1

    return max(
        1,
        count,
    )


def automatic_worker_count():
    cpus = (
        available_cpu_count()
    )

    if cpus <= 2:
        return 1

    workers = int(
        cpus * 0.75
    )

    workers = min(
        workers,
        cpus - 1,
    )

    return max(
        1,
        workers,
    )


# ============================================================
# HUD
# ============================================================

def build_hud(
    model,
    workers,
    speed,
    render_ms,
    output_ms,
    total_ms,
    fps,
):
    return (
        f"{model.NAME}  "
        f"workers={workers}  "
        f"speed={speed:.2f}x  "
        f"render={render_ms:5.1f}ms  "
        f"output={output_ms:4.1f}ms  "
        f"total={total_ms:5.1f}ms  "
        f"fps={fps:5.1f}"
    )


# ============================================================
# ARGUMENTS
# ============================================================

def parse_args():
    parser = (
        argparse.ArgumentParser(
            description=(
                "Terminal fractal engine"
            )
        )
    )

    parser.add_argument(
        "--model",
        default="cubic_julia",
        help=(
            "model module from models/ "
            "(default: cubic_julia)"
        ),
    )

    parser.add_argument(
        "--workers",
        default="auto",
        help=(
            "worker process count "
            "or 'auto'"
        ),
    )

    parser.add_argument(
        "--chunks-per-worker",
        type=int,
        default=(
            DEFAULT_CHUNKS_PER_WORKER
        ),
    )

    parser.add_argument(
        "--style-buckets",
        type=int,
        default=STYLE_BUCKETS,
    )

    parser.add_argument(
        "--speed",
        type=float,
        default=DEFAULT_SPEED,
        help=(
            "mathematical evolution speed "
            "(default: 1.0)"
        ),
    )

    parser.add_argument(
        "--hud",
        action="store_true",
        help=(
            "show renderer status line"
        ),
    )

    return parser.parse_args()


def resolve_worker_count(
    value,
):
    if value == "auto":
        return (
            automatic_worker_count()
        )

    try:
        workers = int(value)

    except ValueError:
        raise SystemExit(
            "--workers must be a positive "
            "integer or 'auto'"
        )

    if workers < 1:
        raise SystemExit(
            "--workers must be at least 1"
        )

    return workers


# ============================================================
# MAIN
# ============================================================

def main():
    args = parse_args()

    if (
        args.chunks_per_worker
        < 1
    ):
        raise SystemExit(
            "--chunks-per-worker must "
            "be at least 1"
        )

    if (
        args.style_buckets
        < 2
    ):
        raise SystemExit(
            "--style-buckets must "
            "be at least 2"
        )

    if args.speed <= 0.0:
        raise SystemExit(
            "--speed must be greater than 0"
        )

    model = import_model(
        args.model
    )

    workers = (
        resolve_worker_count(
            args.workers
        )
    )

    ctx = get_context(
        "spawn"
    )

    pool = ctx.Pool(
        processes=workers,
        initializer=init_worker,
        initargs=(
            args.model,
        ),
    )

    animation_start = (
        time.perf_counter()
    )

    sys.stdout.write(
        "\033[2J"
        "\033[H"
        "\033[?25l"
    )

    sys.stdout.flush()

    try:
        while True:
            frame_start = (
                time.perf_counter()
            )

            elapsed = (
                frame_start
                - animation_start
            )

            t = (
                elapsed
                * args.speed
            )

            render_start = (
                time.perf_counter()
            )

            (
                frame,
                width,
                height,
            ) = render_frame(
                model,
                t,
                pool,
                workers,
                args.chunks_per_worker,
                args.style_buckets,
                args.hud,
            )

            render_end = (
                time.perf_counter()
            )

            render_ms = (
                render_end
                - render_start
            ) * 1000.0

            #
            # Build output before timing terminal I/O.
            #

            if args.hud:
                # Output stats describe the previous terminal write.
                # Current write time is filled in immediately afterward.
                # This avoids adding another terminal write just for HUD.
                placeholder_output_ms = 0.0

                total_before_output = (
                    render_end
                    - frame_start
                ) * 1000.0

                provisional_fps = (
                    1000.0
                    / total_before_output
                    if total_before_output > 0.0
                    else 0.0
                )

                hud = build_hud(
                    model,
                    workers,
                    args.speed,
                    render_ms,
                    placeholder_output_ms,
                    total_before_output,
                    provisional_fps,
                )

                output_text = (
                    "\033[H"
                    + RESET
                    + hud
                    + "\n"
                    + frame
                )

            else:
                output_text = (
                    "\033[H"
                    + frame
                )

            output_start = (
                time.perf_counter()
            )

            sys.stdout.write(
                output_text
            )

            sys.stdout.flush()

            output_end = (
                time.perf_counter()
            )

            output_ms = (
                output_end
                - output_start
            ) * 1000.0

            total_ms = (
                output_end
                - frame_start
            ) * 1000.0

            fps = (
                1000.0 / total_ms
                if total_ms > 0.0
                else 0.0
            )

            #
            # When HUD is enabled, update just the status row with the
            # completed frame's real timing.
            #
            # This tiny second write never touches the artwork.
            #

            if args.hud:
                hud = build_hud(
                    model,
                    workers,
                    args.speed,
                    render_ms,
                    output_ms,
                    total_ms,
                    fps,
                )

                sys.stdout.write(
                    "\033[H"
                    + RESET
                    + hud
                )

                sys.stdout.flush()

    except KeyboardInterrupt:
        pass

    finally:
        pool.terminate()
        pool.join()

        sys.stdout.write(
            RESET
            + "\033[?25h"
            + "\n"
        )

        sys.stdout.flush()


if __name__ == "__main__":
    main()
