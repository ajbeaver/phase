#!/usr/bin/env python3

import math
import re
from pathlib import Path

try:
    from simple_term_menu import TerminalMenu
except ImportError:
    raise SystemExit(
        "simple-term-menu is required.\n\n"
        "Install it with:\n"
        "    python3 -m pip install simple-term-menu"
    )


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent
ENGINE_PATH = ROOT / "engine.py"


# ============================================================
# ANSI
# ============================================================

RESET = "\033[0m"


def fg(rgb):
    r, g, b = rgb

    return (
        f"\033[38;2;"
        f"{r};{g};{b}m"
    )


def bg(rgb):
    r, g, b = rgb

    return (
        f"\033[48;2;"
        f"{r};{g};{b}m"
    )


def swatch(rgb, width=8):
    return (
        bg(rgb)
        + (" " * width)
        + RESET
    )


# ============================================================
# PALETTE LIBRARY
# ============================================================

PALETTES = {
    "Purple": {
        "Amethyst": {
            "inside": (10, 8, 18),
            "red_low": 45,
            "red_high": 165,
            "green_low": 20,
            "green_high": 65,
            "blue_low": 120,
            "blue_high": 255,
        },

        "Violet": {
            "inside": (8, 5, 18),
            "red_low": 70,
            "red_high": 200,
            "green_low": 10,
            "green_high": 60,
            "blue_low": 120,
            "blue_high": 255,
        },

        "Electric Purple": {
            "inside": (5, 3, 15),
            "red_low": 90,
            "red_high": 255,
            "green_low": 0,
            "green_high": 55,
            "blue_low": 150,
            "blue_high": 255,
        },

        "Plum": {
            "inside": (14, 7, 15),
            "red_low": 65,
            "red_high": 180,
            "green_low": 15,
            "green_high": 55,
            "blue_low": 70,
            "blue_high": 190,
        },

        "Deep Space": {
            "inside": (3, 3, 10),
            "red_low": 25,
            "red_high": 120,
            "green_low": 10,
            "green_high": 45,
            "blue_low": 75,
            "blue_high": 220,
        },
    },

    "Blue": {
        "Midnight": {
            "inside": (2, 5, 12),
            "red_low": 5,
            "red_high": 55,
            "green_low": 20,
            "green_high": 90,
            "blue_low": 85,
            "blue_high": 220,
        },

        "Electric Blue": {
            "inside": (2, 5, 12),
            "red_low": 0,
            "red_high": 70,
            "green_low": 40,
            "green_high": 170,
            "blue_low": 140,
            "blue_high": 255,
        },

        "Cobalt": {
            "inside": (3, 4, 14),
            "red_low": 15,
            "red_high": 80,
            "green_low": 25,
            "green_high": 100,
            "blue_low": 110,
            "blue_high": 245,
        },

        "Ice": {
            "inside": (4, 10, 14),
            "red_low": 40,
            "red_high": 150,
            "green_low": 90,
            "green_high": 220,
            "blue_low": 150,
            "blue_high": 255,
        },
    },

    "Cyan": {
        "Deep Cyan": {
            "inside": (2, 10, 12),
            "red_low": 0,
            "red_high": 55,
            "green_low": 70,
            "green_high": 200,
            "blue_low": 95,
            "blue_high": 235,
        },

        "Neon Cyan": {
            "inside": (2, 8, 10),
            "red_low": 0,
            "red_high": 80,
            "green_low": 120,
            "green_high": 255,
            "blue_low": 140,
            "blue_high": 255,
        },

        "Sea Glass": {
            "inside": (5, 12, 12),
            "red_low": 25,
            "red_high": 120,
            "green_low": 95,
            "green_high": 215,
            "blue_low": 105,
            "blue_high": 220,
        },
    },

    "Green": {
        "Emerald": {
            "inside": (3, 10, 6),
            "red_low": 5,
            "red_high": 70,
            "green_low": 80,
            "green_high": 220,
            "blue_low": 30,
            "blue_high": 130,
        },

        "Terminal": {
            "inside": (0, 8, 2),
            "red_low": 0,
            "red_high": 50,
            "green_low": 90,
            "green_high": 255,
            "blue_low": 10,
            "blue_high": 80,
        },

        "Acid": {
            "inside": (5, 10, 0),
            "red_low": 50,
            "red_high": 170,
            "green_low": 130,
            "green_high": 255,
            "blue_low": 0,
            "blue_high": 70,
        },
    },

    "Red": {
        "Crimson": {
            "inside": (14, 3, 4),
            "red_low": 100,
            "red_high": 255,
            "green_low": 5,
            "green_high": 55,
            "blue_low": 15,
            "blue_high": 90,
        },

        "Scarlet": {
            "inside": (14, 4, 2),
            "red_low": 130,
            "red_high": 255,
            "green_low": 15,
            "green_high": 80,
            "blue_low": 5,
            "blue_high": 50,
        },

        "Blood Moon": {
            "inside": (10, 2, 5),
            "red_low": 65,
            "red_high": 210,
            "green_low": 5,
            "green_high": 35,
            "blue_low": 20,
            "blue_high": 100,
        },
    },

    "Orange": {
        "Ember": {
            "inside": (14, 6, 2),
            "red_low": 110,
            "red_high": 255,
            "green_low": 35,
            "green_high": 145,
            "blue_low": 0,
            "blue_high": 55,
        },

        "Copper": {
            "inside": (12, 7, 4),
            "red_low": 90,
            "red_high": 220,
            "green_low": 45,
            "green_high": 130,
            "blue_low": 15,
            "blue_high": 75,
        },

        "Solar": {
            "inside": (12, 8, 0),
            "red_low": 140,
            "red_high": 255,
            "green_low": 70,
            "green_high": 200,
            "blue_low": 0,
            "blue_high": 65,
        },
    },

    "Pink": {
        "Hot Pink": {
            "inside": (14, 4, 12),
            "red_low": 130,
            "red_high": 255,
            "green_low": 10,
            "green_high": 80,
            "blue_low": 80,
            "blue_high": 220,
        },

        "Rose": {
            "inside": (12, 6, 10),
            "red_low": 100,
            "red_high": 240,
            "green_low": 30,
            "green_high": 110,
            "blue_low": 60,
            "blue_high": 170,
        },

        "Magenta": {
            "inside": (10, 3, 12),
            "red_low": 100,
            "red_high": 255,
            "green_low": 0,
            "green_high": 55,
            "blue_low": 100,
            "blue_high": 255,
        },
    },

    "Gold": {
        "Amber": {
            "inside": (12, 8, 2),
            "red_low": 120,
            "red_high": 255,
            "green_low": 65,
            "green_high": 190,
            "blue_low": 0,
            "blue_high": 55,
        },

        "Gold": {
            "inside": (12, 9, 2),
            "red_low": 140,
            "red_high": 255,
            "green_low": 100,
            "green_high": 220,
            "blue_low": 10,
            "blue_high": 80,
        },

        "Pale Gold": {
            "inside": (12, 10, 5),
            "red_low": 130,
            "red_high": 255,
            "green_low": 110,
            "green_high": 235,
            "blue_low": 40,
            "blue_high": 130,
        },
    },

    "Monochrome": {
        "Silver": {
            "inside": (7, 7, 9),
            "red_low": 60,
            "red_high": 220,
            "green_low": 60,
            "green_high": 220,
            "blue_low": 70,
            "blue_high": 240,
        },

        "White": {
            "inside": (4, 4, 4),
            "red_low": 80,
            "red_high": 255,
            "green_low": 80,
            "green_high": 255,
            "blue_low": 80,
            "blue_high": 255,
        },

        "Smoke": {
            "inside": (5, 6, 8),
            "red_low": 35,
            "red_high": 160,
            "green_low": 40,
            "green_high": 170,
            "blue_low": 50,
            "blue_high": 190,
        },
    },
}


# ============================================================
# MENU CONFIG
# ============================================================

def make_menu(
    entries,
    title,
):
    return TerminalMenu(
        entries,
        title=title,
        menu_cursor="> ",
        menu_cursor_style=(),
        menu_highlight_style=(),
        cycle_cursor=True,
        clear_screen=True,
    )


# ============================================================
# PREVIEW
# ============================================================

def interpolate(
    start,
    end,
    amount,
):
    return int(
        start
        + (end - start)
        * amount
    )


def sample_palette(
    palette,
    steps=28,
):
    colors = []

    for index in range(
        steps
    ):
        if steps <= 1:
            n = 0.0
        else:
            n = (
                index
                / (steps - 1)
            )

        wave1 = (
            0.5
            + 0.5
            * math.sin(
                n * 10.0
            )
        )

        wave2 = (
            0.5
            + 0.5
            * math.sin(
                n * 6.0
            )
        )

        r = interpolate(
            palette["red_low"],
            palette["red_high"],
            wave1,
        )

        g = interpolate(
            palette["green_low"],
            palette["green_high"],
            wave2,
        )

        b = interpolate(
            palette["blue_low"],
            palette["blue_high"],
            wave1,
        )

        colors.append(
            (
                r,
                g,
                b,
            )
        )

    return colors


def print_preview(
    family,
    name,
    palette,
):
    print(
        "\033[2J\033[H",
        end="",
    )

    print(
        f"{family} / {name}"
    )

    print()

    colors = sample_palette(
        palette
    )

    print(
        "  ",
        end="",
    )

    for color in colors:
        print(
            bg(color)
            + "  "
            + RESET,
            end="",
        )

    print()
    print()

    inside = (
        palette["inside"]
    )

    print(
        "Interior"
    )

    print(
        f"  {swatch(inside, 10)} "
        f"{inside}"
    )

    print()
    print(
        "RGB ranges"
    )

    print(
        f"  R  "
        f"{palette['red_low']:3}"
        f" → "
        f"{palette['red_high']:3}"
    )

    print(
        f"  G  "
        f"{palette['green_low']:3}"
        f" → "
        f"{palette['green_high']:3}"
    )

    print(
        f"  B  "
        f"{palette['blue_low']:3}"
        f" → "
        f"{palette['blue_high']:3}"
    )

    print()


# ============================================================
# ENGINE REWRITE
# ============================================================

def replace_assignment(
    source,
    variable,
    replacement,
):
    pattern = (
        rf"^{re.escape(variable)}"
        rf"\s*=\s*.*$"
    )

    new_source, count = (
        re.subn(
            pattern,
            f"{variable} = {replacement}",
            source,
            count=1,
            flags=re.MULTILINE,
        )
    )

    if count != 1:
        raise RuntimeError(
            f"Could not uniquely locate "
            f"{variable} in "
            f"{ENGINE_PATH.name}"
        )

    return new_source


def apply_palette(
    palette,
):
    if not ENGINE_PATH.exists():
        raise RuntimeError(
            f"Could not find engine.py at:\n"
            f"{ENGINE_PATH}"
        )

    source = (
        ENGINE_PATH.read_text(
            encoding="utf-8"
        )
    )

    source = replace_assignment(
        source,
        "INSIDE_RGB",
        repr(
            palette["inside"]
        ),
    )

    source = replace_assignment(
        source,
        "RED_LOW",
        str(
            palette["red_low"]
        ),
    )

    source = replace_assignment(
        source,
        "RED_HIGH",
        str(
            palette["red_high"]
        ),
    )

    source = replace_assignment(
        source,
        "GREEN_LOW",
        str(
            palette["green_low"]
        ),
    )

    source = replace_assignment(
        source,
        "GREEN_HIGH",
        str(
            palette["green_high"]
        ),
    )

    source = replace_assignment(
        source,
        "BLUE_LOW",
        str(
            palette["blue_low"]
        ),
    )

    source = replace_assignment(
        source,
        "BLUE_HIGH",
        str(
            palette["blue_high"]
        ),
    )

    ENGINE_PATH.write_text(
        source,
        encoding="utf-8",
    )


# ============================================================
# FAMILY MENU
# ============================================================

def choose_family():
    families = list(
        PALETTES.keys()
    )

    menu = make_menu(
        families,
        (
            "Palette Picker\n\n"
            "↑ ↓  Move\n"
            "Enter Select\n"
            "Esc   Exit\n\n"
            "Choose a color family:"
        ),
    )

    selected = menu.show()

    if selected is None:
        return None

    return families[
        selected
    ]


# ============================================================
# SHADE MENU
# ============================================================

def choose_shade(
    family,
):
    names = list(
        PALETTES[
            family
        ].keys()
    )

    entries = (
        names
        + ["Back"]
    )

    menu = make_menu(
        entries,
        (
            f"{family}\n\n"
            "↑ ↓  Move\n"
            "Enter Select\n"
            "Esc   Back\n\n"
            "Choose a palette:"
        ),
    )

    selected = menu.show()

    if selected is None:
        return None

    if selected == len(
        names
    ):
        return None

    return names[
        selected
    ]


# ============================================================
# CONFIRMATION
# ============================================================

def confirm_palette():
    entries = [
        "Apply palette",
        "Choose another shade",
        "Choose another color family",
        "Cancel",
    ]

    menu = make_menu(
        entries,
        (
            "Use this palette?\n\n"
            "↑ ↓  Move\n"
            "Enter Select"
        ),
    )

    return menu.show()


# ============================================================
# MAIN
# ============================================================

def main():
    while True:
        family = (
            choose_family()
        )

        if family is None:
            return

        while True:
            name = (
                choose_shade(
                    family
                )
            )

            if name is None:
                break

            palette = (
                PALETTES[
                    family
                ][name]
            )

            print_preview(
                family,
                name,
                palette,
            )

            choice = (
                confirm_palette()
            )

            if choice is None:
                return

            if choice == 0:
                try:
                    apply_palette(
                        palette
                    )

                except Exception as exc:
                    print(
                        "\nFailed to update engine.py:\n"
                        f"{exc}\n"
                    )

                    raise SystemExit(
                        1
                    )

                print(
                    "\033[2J\033[H",
                    end="",
                )

                print(
                    f"Applied: "
                    f"{family} / {name}"
                )

                print()
                print(
                    "engine.py updated."
                )

                return

            if choice == 1:
                continue

            if choice == 2:
                break

            if choice == 3:
                return


if __name__ == "__main__":
    main()
