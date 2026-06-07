import flet as ft
from typing import Optional, Callable, List, Tuple, Dict

class InsCard(ft.Card):
    """Card con icona, titolo e due TextField (IP/Porta)."""
    def __init__(
        self,
        data: str,
        title: str = "Broker MQTT",
        subtitle: Optional[str] = None,
        icon: Optional[str] = ft.Icons.CLOUD_QUEUE,
        data_lab: str = "IP Broker MQTT",
        col: Optional[Dict] = None,
    ):
        super().__init__()
        self.elevation = 2
        self.margin = 5
        self.bgcolor = "secondarycontainer"
        self.border_radius = 10
        self.border = ft.Border.all(1, ft.Colors.OUTLINE)

        # TextField per IP e Porta
        self.ip_field = ft.TextField(
            label=data_lab,
            value=data,
            ref=ft.Ref[ft.TextField]()
        )

        header = ft.ListTile(
            leading=ft.Icon(icon, size=32) if icon else None,
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
                    self.ip_field,
                ],
                spacing=10,
            ),
            padding=15,
        )

        if col:
            self.col = col
