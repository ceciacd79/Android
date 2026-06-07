import flet as ft

class CustomControl(ft.Container):
    """
    Un UserControl che si adatta automaticamente al tema della pagina 
    utilizzando i token di colore semantici di Flet (Material 3).
    NON sono necessarie modifiche a questa classe per cambiare tema/colore.
    """
    def __init__(self, text: str, icon: str = None):
        super().__init__()
        self.text_content = text
        self.icon_name = icon
        
        # Il Container esterno usa token di superficie e bordo
        self.padding = 16
        # Colore superficie per lo sfondo della card
        self.bgcolor = "secondarycontainer"
        self.border_radius = 10
        # Colore outline per il bordo
        self.border = ft.Border.all(2, ft.Colors.OUTLINE) 
        self.width = 300
        self.alignment = ft.Alignment.CENTER_LEFT
        
    def build(self):
        # Il contenuto interno usa token per l'icona e il testo
        if self.icon_name:
            content = ft.Row([
                # Icona usa il Colore Primario (PRIMARY) del tema
                ft.Icon(
                    self.icon_name, 
                    size=24, 
                    color=ft.Colors.PRIMARY 
                ),
                # Testo usa il Colore On Surface Variant
                ft.Text(
                    self.text_content, 
                    size=16,
                    color=ft.Colors.ON_SURFACE_VARIANT 
                )
            ], spacing=12, alignment=ft.MainAxisAlignment.START)
        else:
            # Versione solo testo (usa anche un token on-surface)
            content = ft.Text(
                self.text_content, 
                size=16,
                color=ft.Colors.ON_SURFACE
            )
        return content
