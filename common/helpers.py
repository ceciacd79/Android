import flet as ft

def get_theme_color(page, color_name: str):
    """
    Restituisce il colore richiesto dal tema della pagina ("primary", "secondary", ecc.),
    con fallback ai colori standard Flet.
    """
    try:
        color_scheme = page.theme.color_scheme
        if color_name == "primary":
            return getattr(color_scheme, "primary", ft.Colors.PRIMARY)
        elif color_name == "secondary":
            return getattr(color_scheme, "secondary", ft.Colors.SECONDARY)
        elif color_name == "tertiary":
            return getattr(color_scheme, "tertiary", ft.Colors.TERTIARY)
        # Puoi aggiungere altri colori se servono
    except Exception:
        if color_name == "primary":
            return ft.Colors.PRIMARY
        elif color_name == "secondary":
            return ft.Colors.SECONDARY
        elif color_name == "tertiary":
            return ft.Colors.TERTIARY
    return None
