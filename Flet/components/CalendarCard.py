import flet as ft
import urllib.parse

class CalendarCard(ft.Card):
    def __init__(self,
                 calendar_name: str, 
                 calendar_id: int = None, 
                 info_items=None,
                 inizio=None,
                 fine=None,
                 creatore: str = None,
                 posizione: str = None,
                 descrizione: str = None,
                 is_all_day: bool = False,
                 scaduto: bool = False,
                 ev_data: dict = None):
        super().__init__()
        
        self.elevation = 2
        self.margin = 0
        self.bgcolor = "secondarycontainer"
        self.border_radius = 5
        self.border = ft.Border.all(1, ft.Colors.OUTLINE)
        
        self.disabled = scaduto
        if scaduto:
            self.opacity = 0.5

        async def apri_maps(e):
            if posizione:
                query = urllib.parse.quote(posizione)
                url = f"https://www.google.com/maps/search/?api=1&query={query}"
                await e.page.launch_url(url)

        # Valori informativi
        info_elements = []
        if info_items:
            for item in info_items:
                if item == posizione:
                    continue # Lo gestiamo con un chip separato
                info_elements.append(
                    ft.Text(item, theme_style=ft.TextThemeStyle.BODY_SMALL, color=ft.Colors.ON_SURFACE_VARIANT, max_lines=10)
                )

        if posizione:
             chip_maps = ft.Chip(
                 label=ft.Text(posizione, size=10, max_lines=10),
                 leading=ft.Icon(ft.Icons.LOCATION_ON, size=12),
                 on_click=apri_maps,
                 padding=0,
             )
             info_elements.append(chip_maps)

        info_row = ft.Row(info_elements, wrap=True) if info_elements else ft.Container()

        # Gestione Leading (Icona o Avatar in base al titolo)
        leading_ctrl = ft.Icon(ft.Icons.CALENDAR_MONTH, size=14)
        if ev_data:
            titolo_lower = (ev_data.get("titolo") or "").lower()
            if "federico" in titolo_lower or "fede" in titolo_lower:
                leading_ctrl = ft.CircleAvatar(foreground_image_src="images/fede.png", radius=12)
            elif "gioia" in titolo_lower or "gio" in titolo_lower:
                leading_ctrl = ft.CircleAvatar(foreground_image_src="images/gioia.png", radius=12)

        # Contenuto della card
        self.content = ft.Container(
            content=ft.Column([
                # Header con icona e titolo
                ft.ListTile(
                    title=ft.Text(calendar_name, theme_style=ft.TextThemeStyle.TITLE_SMALL, size=12, max_lines=10),
                    subtitle=ft.Text(descrizione, theme_style=ft.TextThemeStyle.BODY_SMALL, max_lines=20) if descrizione else None,
                    trailing=leading_ctrl,
                    content_padding=0,
                    min_leading_width=10,
                ),
                info_row
            ], spacing=3),
            padding=ft.Padding(left=10, top=5, bottom=10, right=5),
        )