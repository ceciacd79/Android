import flet as ft
from typing import Optional, Callable, List, Tuple, Dict

class RadioCard(ft.Card):
    """Card con icona, titolo e RadioGroup con N Radio."""
    def __init__(
        self,
        title: str,
        options: List[Tuple[str, str]],
        value: Optional[str] = None,
        icon: Optional[str] = ft.Icons.COLOR_LENS,
        subtitle: Optional[str] = None,
        on_change: Optional[Callable] = None,
        col: Optional[Dict] = None
    ):
        super().__init__()
        self.elevation = 2
        self.margin = 5
        self.bgcolor = "secondarycontainer"
        self.border_radius = 10
        self.border = ft.Border.all(1, ft.Colors.OUTLINE)

        radios = [
            ft.Radio(
                value=v,
                label=lbl,
                label_style=ft.TextStyle(size=14),
                fill_color=ft.Colors.PRIMARY
            )
            for v, lbl in options
        ]

        self.radio_group = ft.RadioGroup(
            value=value,
            content=ft.Column(radios, spacing=6),
            on_change=on_change
        )

        header = ft.ListTile(
            leading=ft.Icon(icon, size=32) if icon else None,
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
                    self.radio_group
                ],
                spacing=10
            ),
            padding=15
        )

        # Consente uso dentro ResponsiveRow
        if col:
            self.col = col
