# -*- coding: utf-8 -*-
"""
Settings Page - Pagina impostazioni applicazione
"""

import flet as ft
import logging

from common.config import COLOR_OPTIONS, RESPONSIVE_COLS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

log = logging.getLogger(__name__)

primary_dropdown_ref = ft.Ref[ft.Dropdown]()
secondary_dropdown_ref = ft.Ref[ft.Dropdown]()

def get_content(app: 'App', title: str = "Impostazioni") -> ft.Column:
    """ Restituisce il contenuto della pagina Settings """   
    from components.TitleCard import TitleCard
    from components.RadioCard import RadioCard
    from components.DropDownCard import DropDownCard
    from components.SwitchCard import SwitchCard
    from components.DoubleInCard import DoubleInCard
    from components.InsCard import InsCard

    #   -----   👀  FUNZIONI INTERNE                👀  -----   #
    # Usa le impostazioni già caricate in app.settings
    settings = getattr(app, 'settings', {})

    # CHIP EDITABILI per key_sql e key_act
    key_sql_list = settings.get("key_sql", [])[:]
    key_act_list = settings.get("key_act", [])[:]
    key_room_list = settings.get("key_rooms", [])[:]
    key_floor_list = settings.get("key_floor", [])[:]
    key_sql_chips = ft.Row(wrap=True, spacing=4)
    key_act_chips = ft.Row(wrap=True, spacing=4)
    key_room_chips = ft.Row(wrap=True, spacing=4)
    key_floor_chips = ft.Row(wrap=True, spacing=4)
    key_sql_input = ft.TextField(label="Aggiungi chiave SQL", width=180, expand=True)
    key_act_input = ft.TextField(label="Aggiungi chiave Action", width=180, expand=True)
    key_room_input = ft.TextField(label="Aggiungi stanza", width=180, expand=True)
    key_floor_input = ft.TextField(label="Aggiungi piano", width=180, expand=True)

    def update_key_sql_chips():
        key_sql_chips.controls.clear()
        for k in key_sql_list:
            key_sql_chips.controls.append(
                ft.Chip(label=k, on_delete=lambda e, val=k: remove_key_sql(val))
            )
        # NON chiamare key_sql_chips.update() qui

    def update_key_act_chips():
        key_act_chips.controls.clear()
        for k in key_act_list:
            key_act_chips.controls.append(
                ft.Chip(label=k, on_delete=lambda e, val=k: remove_key_act(val))
            )
        # NON chiamare key_act_chips.update() qui

    def update_key_room_chips():
        key_room_chips.controls.clear()
        for k in key_room_list:
            key_room_chips.controls.append(
                ft.Chip(label=k, on_delete=lambda e, val=k: remove_key_room(val))
            )
        # NON chiamare key_room_chips.update() qui

    def update_key_floor_chips():
        key_floor_chips.controls.clear()
        for k in key_floor_list:
            key_floor_chips.controls.append(
                ft.Chip(label=k, on_delete=lambda e, val=k: remove_key_floor(val))
            )
        # NON chiamare key_floor_chips.update() qui

    def add_key_sql(e):
        val = key_sql_input.value.strip()
        if val and val not in key_sql_list:
            key_sql_list.append(val)
            key_sql_input.value = ""
            update_key_sql_chips()
            key_sql_chips.update()
            key_sql_input.update()

    def add_key_act(e):
        val = key_act_input.value.strip()
        if val and val not in key_act_list:
            key_act_list.append(val)
            key_act_input.value = ""
            update_key_act_chips()
            key_act_chips.update()
            key_act_input.update()

    def add_key_room(e):
        val = key_room_input.value.strip()
        if val and val not in key_room_list:
            key_room_list.append(val)
            key_room_input.value = ""
            update_key_room_chips()
            key_room_chips.update()
            key_room_input.update()

    def add_key_floor(e):
        val = key_floor_input.value.strip()
        if val and val not in key_floor_list:
            key_floor_list.append(val)
            key_floor_input.value = ""
            update_key_floor_chips()
            key_floor_chips.update()
            key_floor_input.update()

    def remove_key_sql(val):
        if val in key_sql_list:
            key_sql_list.remove(val)
            update_key_sql_chips()
            key_sql_chips.update()

    def remove_key_act(val):
        if val in key_act_list:
            key_act_list.remove(val)
            update_key_act_chips()
            key_act_chips.update()
            update_key_act_chips()

    def remove_key_room(val):
        if val in key_room_list:
            key_room_list.remove(val)
            update_key_room_chips()
            key_room_chips.update()

    def remove_key_floor(val):
        if val in key_floor_list:
            key_floor_list.remove(val)
            update_key_floor_chips()
            key_floor_chips.update()

    update_key_sql_chips()
    update_key_act_chips()
    update_key_room_chips()
    update_key_floor_chips()

    def reload_page(e):
        """Ricarica la pagina corrente e rimuove la subscription specifica della pagina."""
        log.debug(f"Ricaricamento pagina {app.current_page_index} richiesto dall'utente.")
        try:
            # Rimuovi l'handler della pagina se presente
            if hasattr(app, '_settings_page_listener'):
                if hasattr(app.page.pubsub, "remove_listener"):
                    app.page.pubsub.remove_listener(app._settings_page_listener)
                elif hasattr(app.page.pubsub, "unsubscribe"):
                    app.page.pubsub.unsubscribe(app._settings_page_listener)
                del app._settings_page_listener
            # Reset cache
            if hasattr(app, 'pages_cache') and app.current_page_index in app.pages_cache:
                del app.pages_cache[app.current_page_index]
            # Ricarica contenuto chiamando direttamente get_content di questa pagina
            app.content_container.content = get_content(app, title)
            app.content_container.update()
        except Exception as ex:
            log.error(f"Errore durante il reload della pagina: {ex}")

    def on_page_event(message):
        # Filtra eventi solo per la pagina attiva Settings (es: indice 6, da adattare se diverso)
        if getattr(app, 'current_page_index', None) != 6:
            return
        if isinstance(message, dict) and message.get("type") == "colors_updated":
            colors_dict = message.get("colors_dict", {})
            app.change_colors(colors_dict)

    def on_change_colors(e):
        colors_dict = {
            "primary_color": primary_dropdown_ref.current.value,
            "secondary_color": secondary_dropdown_ref.current.value
        }

    def on_save_settings(e):
        # Usa le Ref per i dropdown
        primary_color = primary_dropdown_ref.current.value if primary_dropdown_ref.current else None
        secondary_color = secondary_dropdown_ref.current.value if secondary_dropdown_ref.current else None

        parent = e.control
        debug_value = None
        mqtt_ip = None
        mqtt_port = None
        theme_value = None
        # Cerca nella gerarchia dei genitori la colonna principale
        while parent is not None and not (hasattr(parent, 'controls') and isinstance(parent.controls, list)):
            parent = getattr(parent, 'parent', None)
        if parent is not None:
            # Cerca ResponsiveRow
            rows = [ctrl for ctrl in parent.controls if isinstance(ctrl, ft.ResponsiveRow)]
            if len(rows) >= 3:
                # ResponsiveRow 0: tema/colori
                theme_card = rows[0].controls[0]
                if hasattr(theme_card, 'radio_group'):
                    theme_value = theme_card.radio_group.value
                # ResponsiveRow 1: debug
                debug_card = rows[1].controls[0]
                if hasattr(debug_card, 'switch'):
                    debug_value = debug_card.switch.value
                # ResponsiveRow 2: mqtt
                mqtt_card = rows[2].controls[0]
                if hasattr(mqtt_card, 'ip_field'):
                    mqtt_ip = mqtt_card.ip_field.value
                if hasattr(mqtt_card, 'port_field'):
                    mqtt_port = mqtt_card.port_field.value

        # Recupera le chiavi dalle liste chip
        settings = {
            "theme": theme_value,
            "primary_color": primary_color,
            "secondary_color": secondary_color,
            "debug": debug_value,
            "mqtt_ip": mqtt_ip,
            "mqtt_port": int(mqtt_port) if mqtt_port and str(mqtt_port).isdigit() else 1883,
            "pages_config": getattr(app, "pages_config", []),
            "key_sql": key_sql_list,
            "key_act": key_act_list,
            "key_rooms": key_room_list,
            "key_floor": key_floor_list
        }
        app.save_settings(settings)
        if hasattr(app, 'settings'):
            app.settings.update(settings)

    #   -----   👀  SUBSCRIPTION A EVENTI GLOBALI 👀  -----   #
    if hasattr(app.page, "pubsub") and hasattr(app.page.pubsub, "add_listener"):
        app.page.pubsub.add_listener(on_page_event)
        app._settings_page_listener = on_page_event
    elif hasattr(app.page, "pubsub") and hasattr(app.page.pubsub, "subscribe"):
        app.page.pubsub.subscribe(on_page_event)
        app._settings_page_listener = on_page_event

    #   -----   👀  STRUTTURA UNIFORMATA            👀  -----   #  
    #   ✍🏻      TITLE BAR
    title_bar = TitleCard(
        title=title,
        icon=ft.Icons.SETTINGS,
        info_items=[
            "Configura tema, colori e opzioni dell'applicazione"
        ],
        refresh_callback=reload_page,
        refresh_tooltip="Aggiorna dati Impostazioni"
    )

    #   ✍🏻      LOADING INDICATOR
    loading_indicator = ft.Container(
        content=ft.Row([
            ft.ProgressRing(width=20, height=20),
            ft.Text("Caricamento impostazioni...", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
        ], spacing=10),
        padding=10, visible=True
    )
    app.page.update()

    log.debug(f"✅ Caricamento completato della Home Page.")
    loading_indicator.visible = False

    col = ft.Column([
        title_bar,
        loading_indicator,
        ft.Container(
            content=ft.Column([
                ft.ResponsiveRow([
                    # Selettore tema
                    RadioCard(
                        title="Tema Applicazione",
                        subtitle="Sistema, chiaro o scuro",
                        icon=ft.Icons.COLOR_LENS,
                        options=[
                            ("SYSTEM", "🔄 Sistema (Auto)"),
                            ("LIGHT", "☀️ Chiaro"),
                            ("DARK", "🌙 Scuro")
                        ],
                        value=settings.get("theme", "SYSTEM"),
                        on_change=app.change_theme,
                        col=RESPONSIVE_COLS
                    ),

                    # Selettore colore principale
                    DropDownCard(
                        title="Colore Principale",
                        subtitle="Colore base del tema",
                        icon=ft.Icons.FORMAT_COLOR_FILL,
                        options=COLOR_OPTIONS,
                        value=settings.get("primary_color", "BLUE"),
                        on_change=on_change_colors,
                        col=RESPONSIVE_COLS,
                        label="Scegli colore primario",
                        ref=primary_dropdown_ref
                    ),

                    DropDownCard(
                        title="Colore Secondario",
                        subtitle="Colore di accento",
                        icon=ft.Icons.BRUSH,
                        options=COLOR_OPTIONS,
                        value=settings.get("secondary_color", "AMBER"),
                        on_change=on_change_colors,
                        col=RESPONSIVE_COLS,
                        label="Scegli colore secondario",
                        ref=secondary_dropdown_ref
                    ),
                ]),
                
                ft.Divider(),
                # CHIP UI per key_sql e key_act
                ft.Text("Chiavi SQL (usate in Schedule e filtri MQTT):", weight="bold"),
                ft.Row([
                    key_sql_input,
                    ft.IconButton(icon=ft.Icons.ADD, on_click=add_key_sql, tooltip="Aggiungi chiave SQL")
                ], spacing=8),
                key_sql_chips,
                ft.Divider(),
                ft.Text("Chiavi Action (usate in Schedule e filtri MQTT):", weight="bold"),
                ft.Row([
                    key_act_input,
                    ft.IconButton(icon=ft.Icons.ADD, on_click=add_key_act, tooltip="Aggiungi chiave Action")
                ], spacing=8),
                key_act_chips,
                ft.Divider(),
                ft.Text("Piani (usate in Schedule e Action):", weight="bold"),
                ft.Row([
                    key_floor_input,
                    ft.IconButton(icon=ft.Icons.ADD, on_click=add_key_floor, tooltip="Aggiungi piano")
                ], spacing=8),
                key_floor_chips,
                ft.Divider(),
                ft.Text("Stanze (usate in Schedule e Action):", weight="bold"),
                ft.Row([
                    key_room_input,
                    ft.IconButton(icon=ft.Icons.ADD, on_click=add_key_room, tooltip="Aggiungi stanza")
                ], spacing=8),
                key_room_chips,
                ft.Divider(),
                ft.ResponsiveRow([
                    # Switch Debug Mode (SwitchCard)
                    SwitchCard(
                        title="Debug Mode",
                        subtitle="Attiva log dettagliati",
                        icon=ft.Icons.BUG_REPORT,
                        value=settings.get("debug", False),
                        label="Abilita debug",
                        on_change=app.toggle_debug,
                        col=RESPONSIVE_COLS
                    )
                ]),
                ft.Divider(),
                
                ft.ResponsiveRow([                  
                    # Configurazione MQTT
                    DoubleInCard(
                        ip_value=settings.get("mqtt_ip", "192.168.1.100"),
                        port_value=str(settings.get("mqtt_port", 1883)),
                        title="Broker MQTT",
                        subtitle="Configurazione connessione",
                        icon=ft.Icons.HUB,
                        ip_label="IP Broker MQTT",
                        port_label="Porta MQTT",
                        col=RESPONSIVE_COLS
                    ),
                ]),
                ft.Divider(),

                ft.ResponsiveRow([                  
                    # Configurazione Livello Spegnimento
                    InsCard(
                        data=settings.get("Livello spegnimento", "30"),
                        title="Livello Spegnimento",
                        subtitle="Configurazione livello spegnimento",
                        icon=ft.Icons.LIGHT_MODE_ROUNDED,
                        data_lab="Livello spegnimento",
                        col=RESPONSIVE_COLS
                    ),
                ]),
                ft.Divider(),
                
                # Pulsante Salva Impostazioni
                ft.Container(
                    bgcolor="secondarycontainer",
                    content=ft.ElevatedButton(
                        "Salva Tutte le Impostazioni",
                        icon=ft.Icons.SAVE,
                        on_click=on_save_settings,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.PRIMARY,
                            color=ft.Colors.ON_PRIMARY,
                            padding=ft.Padding.symmetric(horizontal=30, vertical=15)
                        )
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=10,
                    border_radius=10,
                ),
            ], spacing=10),
            padding=10,
            border_radius=10
        )
    ], 
    scroll=ft.ScrollMode.AUTO,
    spacing=5,                                                                  #   👀  Spazio tra i gruppi di livelli                  
    margin=ft.Margin(left=0, right=5, top=0, bottom=5),                         #   👀  Margini intera finestra
    expand=True,
    alignment=ft.MainAxisAlignment.START)
    
    app.page.update()
    return col