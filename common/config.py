# Mappa colori globale
import flet as ft
COLOR_MAP = {
    "RED": ft.Colors.RED, "PINK": ft.Colors.PINK, "PURPLE": ft.Colors.PURPLE,
    "DEEP_PURPLE": ft.Colors.DEEP_PURPLE, "INDIGO": ft.Colors.INDIGO,
    "BLUE": ft.Colors.BLUE, "LIGHT_BLUE": ft.Colors.LIGHT_BLUE,
    "CYAN": ft.Colors.CYAN, "TEAL": ft.Colors.TEAL, "GREEN": ft.Colors.GREEN,
    "LIGHT_GREEN": ft.Colors.LIGHT_GREEN, "LIME": ft.Colors.LIME,
    "YELLOW": ft.Colors.YELLOW, "AMBER": ft.Colors.AMBER,
    "ORANGE": ft.Colors.ORANGE, "DEEP_ORANGE": ft.Colors.DEEP_ORANGE,
    "BROWN": ft.Colors.BROWN, "GREY": ft.Colors.GREY,
    "BLUE_GREY": ft.Colors.BLUE_GREY
}
# Opzioni piano disponibili globalmente
FLOOR_OPTIONS = [
    ("Non assegnato", 0),
    ("Secondo", 1),
    ("Primo", 2),
    ("Terra", 3),
    ("Interrato", 4),
    ("Esterno", 5)
]
RESPONSIVE_COLS = {"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 4, "xxl": 3}
COLOR_OPTIONS = [
    ("RED", "🔴 Rosso"), ("PINK", "💗 Rosa"), ("PURPLE", "💜 Viola"),
    ("DEEP_PURPLE", "🟣 Viola Scuro"), ("INDIGO", "🔵 Indaco"),
    ("BLUE", "🔵 Blu"), ("LIGHT_BLUE", "🩵 Azzurro"),
    ("CYAN", "🩵 Ciano"), ("TEAL", "🩵 Verde Acqua"),
    ("GREEN", "💚 Verde"), ("LIGHT_GREEN", "🟢 Verde Chiaro"),
    ("LIME", "🟢 Lime"), ("YELLOW", "💛 Giallo"),
    ("AMBER", "🟡 Ambra"), ("ORANGE", "🟠 Arancione"),
    ("DEEP_ORANGE", "🟠 Arancione Scuro"), ("BROWN", "🟤 Marrone"),
    ("GREY", "⚫ Grigio"), ("BLUE_GREY", "🔵 Grigio Blu"),
]

class AppStyle:
    # Text Sizes
    TEXT_SIZE_SMALL = 12
    TEXT_SIZE_MEDIUM = 16
    TEXT_SIZE_LARGE = 24
    
    # Text Weights
    TEXT_WEIGHT_NORMAL = ft.FontWeight.NORMAL
    TEXT_WEIGHT_BOLD = ft.FontWeight.BOLD
        
    # Corner Radius
    CORNER_RADIUS = 10
    
    # Padding and Margin
    PADDING = 10
    MARGIN = 10
    
    # Default Card Style
    CARD_ELEVATION = 2
    CARD_PADDING = 15
    
    # Default Icon Size
    ICON_SIZE_S = 16
    ICON_SIZE_B = 24

    # Default Switch Height
    SWITCH_HEIGHT = 30

    @classmethod
    def container_style(cls, bgcolor="surfacevariant"):
        return {
            "border_radius": cls.CORNER_RADIUS,
            "padding": cls.PADDING,
            "bgcolor": bgcolor,
        }