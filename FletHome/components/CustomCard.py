import flet as ft

class CustomCard(ft.Card):
    """Card personalizzata con contenuto dinamico"""
    def __init__(self, text: str, icon: str = ft.Icons.INFO_OUTLINE):
        super().__init__()
        
        # Contenuto della card
        self.content = ft.Container(
            content=ft.Column([
                # Header con icona e titolo
                ft.ListTile(
                    leading=ft.Icon(icon, size=40),
                    title=ft.Text(text, theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    subtitle=ft.Text("Card personalizzata", theme_style=ft.TextThemeStyle.BODY_SMALL),
                ),
                ft.Divider(height=1),
                # Azioni
                ft.Row([
                    ft.TextButton("Dettagli", icon=ft.Icons.OPEN_IN_NEW),
                    ft.TextButton("Chiudi", icon=ft.Icons.CLOSE)
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=8),
            padding=15,
        )

        # Stile della card
        self.elevation = 2
        self.margin = 5
        self.bgcolor = "secondarycontainer"
        self.border_radius = 10
        self.border = ft.Border.all(1, ft.Colors.OUTLINE)
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=4,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 2)
        )
