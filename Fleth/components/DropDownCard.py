import flet as ft
from typing import Optional, Callable, List, Tuple, Dict

class DropDownCard(ft.Card):
    """Card con icona, titolo e un Dropdown."""
    def __init__(
        self,
        title: str,
        options: List[Tuple[str, str]],
        value: Optional[str] = None,
        icon: Optional[str] = ft.Icons.PALETTE,
        subtitle: Optional[str] = None,
        on_change: Optional[Callable] = None,
        col: Optional[Dict] = None,
        label: Optional[str] = None,
        ref: Optional[ft.Ref] = None,
    ):
        super().__init__()

        # Colore dal tema
        primary_color = None
        try:
            if hasattr(ft, 'Page') and hasattr(ft.Page, 'theme') and hasattr(ft.Page.theme, 'color_scheme'):
                primary_color = ft.Page.theme.color_scheme.primary
        except Exception:
            primary_color = ft.Colors.PRIMARY

        secondary_color = None
        try:
            if hasattr(ft, 'Page') and hasattr(ft.Page, 'theme') and hasattr(ft.Page.theme, 'color_scheme'):
                secondary_color = ft.Page.theme.color_scheme.secondary
        except Exception:
            secondary_color = ft.Colors.SECONDARY

        self.elevation = 2
        self.margin = 5
        self.bgcolor = "secondarycontainer"
        self.border_radius = 10
        self.border = ft.Border.all(1, ft.Colors.OUTLINE)

        # Dropdown opzioni
        self.dropdown = ft.Dropdown(
            label=label or title,
            value=value,
            options=[ft.dropdown.Option(v, lbl) for v, lbl in options],
            on_text_change=on_change,
            ref=ref
        )

        header = ft.ListTile(
            leading=ft.Icon(icon, size=32, color=primary_color) if icon else None,
            title=ft.Text(title, theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            subtitle=ft.Text(subtitle, theme_style=ft.TextThemeStyle.BODY_SMALL) if subtitle else None,
            dense=True
        )

        self.content = ft.Container(
            bgcolor="secondarycontainer",
            border_radius=10,
            content=ft.Column(
                controls=[
                    header,
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    self.dropdown
                ],
                spacing=10
            ),
            padding=12
        )

        # Per uso dentro ResponsiveRow
        if col:
            self.col = col
