# -*- coding: utf-8 -*-
"""
MQTT Page - Pagina gestione MQTT (con query DB)
"""

import flet as ft
import logging
from common.config import FLOOR_OPTIONS, RESPONSIVE_COLS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

log = logging.getLogger(__name__)

def get_content(app: 'App', title: str = "MQTT") -> ft.Column:
    """Restituisce il contenuto della pagina MQTT usando query DB"""
    from components.TitleCard import TitleCard
    from components.MqttCard import MqttCard

    level_groups = []

    #   -----   👀  HANDLER
    def mqtt_message_handler(topic, data):
        log.debug(f"Ricevuto messaggio su {topic}: {data}")
        try:
            if "bridge" in topic and "devices" in topic and isinstance(data, list):
                devices = data
                log.debug(f"Ricevuti {len(devices)} devices da bridge/devices")
                for dev in devices:
                    if not isinstance(dev, dict):
                        continue
                    # Estrai i campi richiesti
                    device_row = {
                        "friendly_name": dev.get("friendly_name"),
                        "ieee_address": dev.get("ieee_address"),
                        "type": dev.get("type"),
                        "description": dev.get("definition", {}).get("description") if dev.get("definition") else None,
                        "model": dev.get("definition", {}).get("model") if dev.get("definition") else None,
                        "vendor": dev.get("definition", {}).get("vendor") if dev.get("definition") else None,
                        "manufacturer": dev.get("manufacturer"),
                        "model_id": dev.get("model_id"),
                        "power_source": dev.get("power_source"),
                    }
        except Exception as msg:
            log.error(f"Errore elaborazione messaggio MQTT: {msg}")

    if hasattr(app, "mqtt") and hasattr(app.mqtt, "add_mqtt_message_handler"):
        app.mqtt.add_mqtt_message_handler(mqtt_message_handler)

    #   -----   👀  FUNZIONI INTERNE                👀  -----   #
    def on_filter_btn1(e):
        log.debug("Filtro 1 premuto")
        # Usa la funzione centralizzata in MqttCust
        if hasattr(app, "mqtt") and hasattr(app.mqtt, "publish_message"):
            topic = "HomeZig/bridge/request/permit_join"
            payload = "{\"value\": true, \"time\": 120}"
            app.mqtt.publish_message(topic, payload)
        else:
            log.warning("publish_message non disponibile su app.mqtt")

    def on_filter_btn2(e):
        log.debug("Filtro 2 premuto")
        # Azione 2 qui
        if hasattr(app, "mqtt") and hasattr(app.mqtt, "publish_message"):
            topic = "HomeZig/bridge/request/devices"
            payload = "{}"
            app.mqtt.publish_message(topic, payload)
        else:
            log.warning("publish_message non disponibile su app.mqtt")

    def on_filter_btn3(e):
        log.debug("Filtro 3 premuto")
        # Azione 3 qui

    def save_Card(id_key, room, pos, floor_name, floor_index):
        try:
            app.dbm.UP_DEVICE_INFO(id_key, posizione=room, nome=pos, piano=floor_name, level=floor_index)
        except Exception as ex:
            log.error(f"Errore salvataggio dati device nel DB: {ex}")
    
    #   -----   👀  STRUTTURA UNIFORMATA            👀  -----   #  
    title_bar = TitleCard(
        title=title,
        icon=ft.Icons.SETTINGS_INPUT_ANTENNA,
        info_items=[
            "Gestione dispositivi MQTT tramite query al database"
        ],
        refresh_callback=None
    )

    #   ✍🏻      LOADING INDICATOR
    loading_indicator = ft.Container(
        content=ft.Row([
            ft.ProgressRing(width=20, height=20),
            ft.Text("Caricamento dati MQTT...", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
        ], spacing=10),
        padding=10,
        visible=True
    )
    app.page.update()

    filters_card = ft.Card(
        content=ft.Container(
            bgcolor="secondarycontainer",
            border_radius=10,
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.FILTER_LIST, size=14, color='on_primary_container'),
                    title=ft.Text("Filtri MQTT", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    subtitle=ft.Text("Azioni rapide MQTT", theme_style=ft.TextThemeStyle.BODY_SMALL),
                    dense=True,
                ),
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                ft.Row([
                    ft.ElevatedButton("Permit Join", icon=ft.Icons.FILTER_1, on_click=on_filter_btn1),
                    ft.ElevatedButton("Azione 2", icon=ft.Icons.FILTER_2, on_click=on_filter_btn2),
                    ft.ElevatedButton("Azione 3", icon=ft.Icons.FILTER_3, on_click=on_filter_btn3),
                ], spacing=10),
            ], spacing=5),
            padding=15
        ),
        elevation=2,
        margin=10
    )

    # Caricamento iniziale: mostra loading, carica dati e aggiorna UI
    loading_indicator.visible = True
    app.page.update()
    try:
        if hasattr(app, "mqtt") and hasattr(app.mqtt, "mqtt_client") and app.mqtt.mqtt_client:
            client = app.mqtt.mqtt_client
            if client.is_connected():
                client.publish("HomeZig/bridge/request/health_check", payload="{}", qos=0, retain=False)
    except Exception as ex:
        log.error(f"Errore publish health_check: {ex}")    
 
    # Utilizziamo i dati dal DB invece che da s_devices importato
    loc_mapp = app.mapp

    if len(loc_mapp) == 0:
        log.warning("Mappa dispositivi vuota dopo caricamento.")
        app.show_error_snackbar("Attenzione: Nessun dispositivo trovato. Verifica la connessione al database.")

    for level, devices in loc_mapp.items():
        cards = []
        for dev in devices:
            # dev è il dizionario estratto dal DB
            id_key = dev.get("ID_KEY")
            model = dev.get("MODEL") or "Unknown Model"
            
            card = MqttCard(
                id_key=id_key,
                model=model,
                vendor=dev.get("VENDOR") or "",
                name=dev.get("FRIENDLY_NAME") or "",
                piano=dev.get("FLOOR") or "",
                room=dev.get("POSITION") or "", # Mappa POSITION su room
                descrizione=dev.get("DESCRIPTION") or "",
                ieeeaddr=dev.get("IEEE_ADDRESS") or "",
                on_save=save_Card,
                require_login=app.require_login,
            )
            if hasattr(card, 'tf_pos'): # Esempio di patch se volessimo settarlo
                 card.tf_pos.value = dev.get("NAME") or ""
            cards.append(ft.Container(card, col=RESPONSIVE_COLS))
        
        floor_name = next((name for name, val in FLOOR_OPTIONS if val == level), "Non assegnato")
        group_title = ft.Text(
            f"Piano {floor_name}", 
            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
            margin=ft.Margin(5, 0, 0, 0),
        )
        group_row = ft.ResponsiveRow(cards, spacing=5)
        level_groups.append(
            ft.Container(
                content=ft.Column([
                    group_title,
                    group_row
                ], spacing=5),
                padding=5,
                margin=ft.Margin(5, 0, 0, 0),
                border_radius=10
            )
        )
    
    # 👀    Nascondi loading indicator dopo il caricamento
    loading_indicator.visible = False

    log.debug(f"✅ Caricamento completato della MQTT Page.")

    col = ft.Column([
            title_bar,
            loading_indicator,
            filters_card,
            *level_groups
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=5,                                                                  #   👀  Spazio tra i gruppi di livelli                  
        margin=ft.Margin(left=0, right=5, top=0, bottom=5),                         #   👀  Margini intera finestra
        expand=True,
        alignment=ft.MainAxisAlignment.START)

    app.page.update()
    return col