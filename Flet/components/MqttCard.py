import logging
import flet as ft
import os

from typing import Optional, Callable, List, Tuple, Dict
from common.config import FLOOR_OPTIONS

log = logging.getLogger(__name__)

class MqttCard(ft.Card):
    """Card per visualizzare e gestire un singolo device MQTT"""
    def __init__(self, id_key: int, model: str, vendor: str, name: str, piano: str, room: str, 
                 on_save: callable, descrizione: str = "", ieeeaddr: str = "", 
                 require_login: callable = lambda action: action()):
        super().__init__()
        self.id_key = id_key
        self.model = model
        self.vendor = vendor
        self.name = name
        # Seleziona l'immagine in base alla prima parte di self.name
        assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "images"))

        image_filename = f"{self.model}.png"
        image_rel_path = f"images/{image_filename}"
        self.image_path = image_rel_path

        self.piano = piano
        self.room = room
        self.descrizione = descrizione
        self.ieeeaddr = ieeeaddr

        self.on_save_callback = on_save
        self.require_login = require_login
        self.editing = False

        if "/" in self.model:
            self.model = self.model.replace("/", "-")

        # Campo per model
        self.model_field = ft.TextField(
            value=self.model,
            label="Modello Dispositivo",
            dense=True,
            disabled=True,
            border_color=ft.Colors.OUTLINE_VARIANT
        )
        # Campo per Nome
        self.name_field = ft.TextField(
            value=self.name,
            label="Friendly Name",
            dense=True,
            disabled=True,
            hint_text="Nome nel Topic MQTT",
            border_color=ft.Colors.OUTLINE_VARIANT
        )
        # Campo per Stanza
        self.room_field = ft.TextField(
            value=self.room,
            label="Stanza",
            dense=True,
            hint_text="Es: Soggiorno, Camera da letto...",
            border_color=ft.Colors.OUTLINE_VARIANT
        )
        # Campo per Posizione
        self.pos_field = ft.TextField(
            value="",
            label="Posizione",
            dense=True,
            hint_text="Es: Finestra, Porta, Caldaia...",
            border_color=ft.Colors.OUTLINE_VARIANT
        )

        # Dropdown per piano
        def get_floor_index(val):
            for name, idx in FLOOR_OPTIONS:
                if val and val.lower() == name.lower():
                    return idx
            return 0
        initial_index = get_floor_index(piano)
        self.floor_field = ft.Dropdown(
            label="Piano",
            options=[ft.dropdown.Option(str(idx), name) for name, idx in FLOOR_OPTIONS],
            value=str(initial_index),
            dense=True,
            border_color=ft.Colors.OUTLINE_VARIANT
        )

        self.view_header = ft.Row([
            ft.CircleAvatar(
                content=ft.Image(src=self.image_path, width=28, height=28, fit="cover"),
                bgcolor='surfacebright',
                radius=16
            ),
            ft.Column([
                ft.Text(self.name, size=14, weight=ft.FontWeight.BOLD, italic=not self.piano)
            ], spacing=2)
        ], spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # Container per dati MQTT dinamici
        self.mqtt_data_container = ft.Column([], spacing=5)
        self._update_mqtt_display()

        # View normale
        self.view_content = ft.Column([
            self.view_header,
            ft.Divider(height=1),
            self.mqtt_data_container,
            ft.Row([
                ft.Text("Type:", size=11, weight=ft.FontWeight.W_500),
                ft.Text(f"{self.vendor} ({self.model})", size=11),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    tooltip="Modifica",
                    on_click=self.request_edit,
                    icon_size=18
                ),
            ], spacing=5, alignment=ft.MainAxisAlignment.START)
        ], spacing=8)

        # Header edit mode
        self.edit_header = ft.Row([
            ft.Row([
                ft.Text("Modifica Device", weight=ft.FontWeight.BOLD, size=14)
            ], spacing=10),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.Icons.SAVE,
                tooltip="Salva",
                on_click=self.save_changes,
                icon_size=20
            ),
            ft.IconButton(
                icon=ft.Icons.CANCEL,
                tooltip="Annulla",
                on_click=lambda e: self._toggle_edit(),
                icon_size=20
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # View edit
        self.edit_content = ft.Column([
            self.edit_header,
            ft.Divider(height=1),
            self.model_field,
            self.name_field,
            self.room_field,
            self.pos_field,
            self.floor_field,
            ft.Text(f"Info: {self.descrizione}", size=11)
        ], spacing=8, visible=False)

        # Contenuto della card
        self.content = ft.Container(
            bgcolor="secondarycontainer",
            border_radius=10,
            content=ft.Column([
                self.view_content,
                self.edit_content
            ], spacing=0),
            padding=15
        )

        # Stile della card - come CustomCard
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
    
    def _update_mqtt_display(self):
        """Aggiorna il display con i dati MQTT ricevuti"""
        self.mqtt_data_container.controls.clear()
                
    def request_edit(self, e):
        """Richiede login prima di abilitare la modifica."""
        if self.require_login:
            self.require_login(lambda: self._toggle_edit())
        else:
            self._toggle_edit()

    def _toggle_edit(self):
        """Alterna tra modalità view e edit, aggiorna in modo sicuro."""
        self.editing = not self.editing
        self.view_content.visible = not self.editing
        self.edit_content.visible = self.editing
        try:
            self.update()
        except AssertionError:
            # Se la card non è ancora nella pagina, aggiorna la pagina principale se disponibile
            if hasattr(self, 'app') and hasattr(self.app, 'page'):
                self.app.page.update()
    
    def save_changes(self, e):
        """Salva le modifiche della Card: stanza, descrizione, indice piano"""
        try:
            room = self.room_field.value.strip()
            pos = self.pos_field.value.strip()
            floor_index = int(self.floor_field.value)
            if self.on_save_callback:
                try:
                    floor_name = next((name for name, val in FLOOR_OPTIONS if val == floor_index), "Non assegnato")
                    self.on_save_callback(self.id_key, room, pos, floor_name, floor_index)
                except Exception as ex:
                    log.error(f"Errore nella callback on_save_callback: {ex}.")
            self._toggle_edit()
        except Exception as ex:
            log.error(f"Errore salvataggio modifiche MqttCard: {ex}")