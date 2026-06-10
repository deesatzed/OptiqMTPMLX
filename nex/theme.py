"""
Shared theming for Rich + Textual (very lightweight).

Usage:
    from nex.theme import NEX_THEME
    # then use colors in your widgets / rich styles
"""

NEX_THEME = {
    "primary": "cyan",
    "accent": "green",
    "warning": "yellow",
    "error": "red",
    "surface": "#1a1a1a",
    "text": "#e0e0e0",
}

def get_color(name: str) -> str:
    return NEX_THEME.get(name, "white")