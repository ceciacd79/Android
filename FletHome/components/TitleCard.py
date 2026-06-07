import flet as ft
from common.config import AppStyle
from typing import Optional, Callable, List, Tuple, Dict

class TitleCard(ft.Card):
    """Card standard per titoli di pagina con icona, titolo, info e pulsante refresh opzionale"""
    def __init__(
        self,
        title: str,
        icon: str = ft.Icons.INFO,
        icon_color: Optional[str] = None,
        info_items: Optional[List[Tuple[str, str]]] = None,  # [(icona, testo), ...]
        refresh_callback: Optional[Callable] = None,
        refresh_tooltip: str = "Ricarica",
    ):
        super().__init__()
        
        self.elevation = 2
        self.margin = AppStyle.MARGIN
        self.bgcolor = "secondarycontainer"
        self.border_radius = AppStyle.CORNER_RADIUS
        self.border = ft.Border.all(1, ft.Colors.OUTLINE)
        
        # Costruisci header row con titolo e bottone refresh opzionale
        header_controls = [
            ft.Text(title, theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, expand=True)
        ]
        
        if refresh_callback:
            header_controls.append(
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip=refresh_tooltip,
                    on_click=refresh_callback,
                    icon_size=AppStyle.ICON_SIZE_B,
                    icon_color='secondary_color'
                )
            )
        
        header_row = ft.Row(
            controls=header_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10
        )
        
        # Contenuto colonna principale
        column_controls = [header_row, ft.Divider(height=1)]
        
        # Aggiungi info row se ci sono info items
        if info_items:
            info_controls = [
                ft.Icon(icon, size=AppStyle.ICON_SIZE_B, color=icon_color or ft.Colors.PRIMARY)
            ]
            
            for item_text in info_items:
                info_controls.append(
                    ft.Text(item_text, theme_style=ft.TextThemeStyle.BODY_MEDIUM)
                )
            
            info_row = ft.Row(info_controls, spacing=10, wrap=True)
            column_controls.append(info_row)
        
        self.content = ft.Container(
            content=ft.Column(column_controls, spacing=10),
            padding=AppStyle.PADDING,
            bgcolor="secondarycontainer",
            border_radius=AppStyle.CORNER_RADIUS,
        )