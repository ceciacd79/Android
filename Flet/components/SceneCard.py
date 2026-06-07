import flet as ft

class SceneCard(ft.Card):
    """Card per visualizzare una scena, stile coerente con le altre Card."""
    def __init__(self, scene_name: str, scene_id: int = None, icon: str = ft.Icons.THEATER_COMEDY, info_items=None):
        
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

        if not icon:
            icon = ft.Icons.THEATER_COMEDY

        self.elevation = 2
        self.margin = 5
        self.bgcolor = "secondarycontainer"
        self.border_radius = 10
        self.border = ft.Border.all(1, ft.Colors.OUTLINE)

        # Header row con icona e titolo
        header_controls = [
            ft.Icon(icon, size=24, color=primary_color ),
            ft.Text(scene_name, theme_style=ft.TextThemeStyle.TITLE_MEDIUM, expand=True)
        ]
        header_row = ft.Row(
            controls=header_controls,
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )

        # Contenuto colonna principale
        column_controls = [header_row, ft.Divider(height=1)]

        # Info row opzionale (es: ID scena)
        if scene_id is not None or info_items:
            info_controls = []
            if scene_id is not None:
                info_controls.append(ft.Text(f"ID scena: {scene_id}", theme_style=ft.TextThemeStyle.BODY_SMALL))
            if info_items:
                for item in info_items:
                    info_controls.append(ft.Text(str(item), theme_style=ft.TextThemeStyle.BODY_SMALL))
            
            info_row = ft.Row(info_controls, spacing=10, wrap=True)
            column_controls.append(info_row)

        self.content = ft.Container(
            bgcolor="secondarycontainer",
            border_radius=10,
            content=ft.Column(column_controls, spacing=10),
            padding=12
        )