import flet as ft
from typing import Optional, Callable, List, Tuple, Dict

class SwitchCard(ft.Card):
    """Card con icona, titolo, sottotitolo e Switch."""
    def __init__(
        self,
        title: str,
        value: bool = False,
        icon: Optional[str] = ft.Icons.TOGGLE_ON,
        subtitle: Optional[str] = None,
        label: str = "Abilita",
        label_on: str = "OFF",
        label_off: str = "ON",
        on_change: Optional[Callable] = None,
        col: Optional[Dict] = None,
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

        self.label_on = label_on
        self.label_off = label_off

        def _on_switch_change(e):
            # Cambia la label in base allo stato
            self.switch.label = self.label_on if e.control.value else self.label_off
            self.update()
            if on_change:
                on_change(e)

        self.switch = ft.Switch(
            label=label_on if value else label_off,
            value=value,
            on_change=_on_switch_change,
            ref=ft.Ref[ft.Switch]()
        )

        header = ft.ListTile(
            leading=ft.Icon(icon, size=32, color=secondary_color) if icon else None,
            title=ft.Text(title, theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            subtitle=ft.Text(subtitle, theme_style=ft.TextThemeStyle.BODY_SMALL) if subtitle else None,
            dense=True,
        )

        self.content = ft.Container(
            bgcolor="secondarycontainer",
            border_radius=10,
            content=ft.Column(
                controls=[
                    header,
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    self.switch,
                ],
                spacing=10,
            ),
            padding=15,
        )
        if col:
            self.col = col
