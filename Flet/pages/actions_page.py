# -*- coding: utf-8 -*-
"""
Home Page - Pagina principale dell'applicazione
"""

import flet as ft
import inspect as ins
import logging
import threading

from common.config import RESPONSIVE_COLS
from common.helpers import get_theme_color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

log = logging.getLogger(__name__)

def get_content(app: 'App', title: str = "Actions Page") -> ft.Column:
    """ Restituisce il contenuto della pagina"""
    from components.TitleCard import TitleCard
    from components.SceneCard import SceneCard
    
    loc_mapp, fix_dict = {}, {}
    fix_cards = []

    #   -----   👀  FUNZIONI INTERNE                👀  -----   #
    def Decode_Topic(topic):
        try:
            parts = topic.split("/")
            # Caso Scene: HomeZig/Scene
            if len(parts) == 2:
                return 0, parts[1], "Scene"
            # Caso HomeZig/type/Nome_XX
            if len(parts) >= 3:
                name = parts[2]
                type = parts[1]
                idx = int(name.split("_")[-1])
                return idx, name, type
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")
            return 0, "Unknown", "Unknown"


    def reload_page(e):
        """Ricarica la pagina corrente e rimuove la subscription specifica della pagina."""
        log.info(f"Ricaricamento pagina {app.current_page_index} richiesto dall'utente.")
        try:
            # Rimuovi l'handler della pagina se presente
            if hasattr(app, '_actions_page_listener'):
                if hasattr(app.page.pubsub, "remove_listener"):
                    app.page.pubsub.remove_listener(app._actions_page_listener)
                elif hasattr(app.page.pubsub, "unsubscribe"):
                    app.page.pubsub.unsubscribe(app._actions_page_listener)
                del app._actions_page_listener
            # Reset cache della pagina
            if hasattr(app, 'pages_cache') and app.current_page_index in app.pages_cache:
                del app.pages_cache[app.current_page_index]
            # Ricarica contenuto chiamando direttamente get_content di questa pagina
            app.content_container.content = get_content(app, title)
            app.content_container.update()
        except Exception as ex:
            log.error(f"Errore durante il reload della pagina: {ex}")

    def on_page_event(message):
        if app.current_page_index != 2:
            return
        if isinstance(message, dict) and message.get("type") == "schedule_updated":
            if hasattr(app, 'pages_cache') and app.current_page_index in app.pages_cache:
                del app.pages_cache[app.current_page_index]
            app.content_container.content = get_content(app, title)
            app.content_container.update()

    def subscribe_events():
        if hasattr(app.page, "pubsub"):
            if hasattr(app.page.pubsub, "subscribe"):
                app.page.pubsub.subscribe(on_page_event)
            elif hasattr(app.page.pubsub, "add_listener"):
                app.page.pubsub.add_listener(on_page_event)

    def unsubscribe_events():
        if hasattr(app.page, "pubsub"):
            if hasattr(app.page.pubsub, "unsubscribe"):
                app.page.pubsub.unsubscribe(on_page_event)
            elif hasattr(app.page.pubsub, "remove_listener"):
                app.page.pubsub.remove_listener(on_page_event)

    def on_scene_button_click(e):
        if hasattr(app, "mqtt") and hasattr(app.mqtt, "publish_message"):
            group_name = e.control.data.get("group_name")
            scene_id = e.control.data.get("scene_id")
            scene_name = e.control.data.get("scene_name")
            topic = f"HomeZig/{group_name}/set"
            payload = f'{{"scene_recall": {scene_id}}}'
        #    payload = f'{{"status": "CLOSE", "position":40}}'
            app.mqtt.publish_message(topic, payload)
            log.debug(f"Publish scena: {topic} -> {payload}")
            app.show_info_snackbar(f"🚴‍♀️ Scena {group_name} - {scene_name}")

    def load_progressively():
        nonlocal loc_mapp
        try:
            app.is_loading = True
            # 1. Load Scenes
            try:
                data_s = app.scene
                group_dict_local = {}
                for row in data_s:
                    group_id = row[0]
                    group_name = row[1]
                    scene_id = row[2]
                    scene_name = row[3]
                    if group_name not in group_dict_local:
                        group_dict_local[group_name] = {"id": group_id, "scenes": []}
                    group_dict_local[group_name]["scenes"].append({"id": scene_id, "name": scene_name})

                local_scene_cards = []
                for group_name, group in group_dict_local.items():
                    scene_buttons = [
                        ft.TextButton(
                            scene["name"],
                            icon=ft.Icons.GESTURE,
                            icon_color=get_theme_color(app.page, "secondary"),
                            data={"group_name": group_name, "group_id": group.get("id"), "scene_id": scene["id"], "scene_name": scene["name"]},
                            style=ft.ButtonStyle(color=get_theme_color(app.page, "secondary")),
                            on_click=on_scene_button_click
                        ) for scene in group["scenes"]
                    ]
                    icon = scene_buttons[0].icon if scene_buttons and hasattr(scene_buttons[0], "icon") else ft.Icons.THEATER_COMEDY
                    card = SceneCard(
                        scene_name=group_name,
                        scene_id=group.get("id"),
                        icon=icon
                    )
                    card.content.content.controls[2].controls = scene_buttons
                    local_scene_cards.append(card)
                
                if scenes_row_ref.current:
                    scenes_row_ref.current.controls = [ft.Container(c, col=RESPONSIVE_COLS) for c in local_scene_cards]
                    try:
                        if scenes_row_ref.current.page:
                            scenes_row_ref.current.update()
                    except Exception as e:
                        if "must be added" not in str(e):
                            raise

            except Exception as e:
                log.error(f"Errore caricamento scene: {e}")

        except Exception as e:
             log.error(f"Errore generale caricamento progressivo home: {e}")
        finally:
            loading_indicator.visible = False
            app.is_loading = False
            try:
                if app.page:
                    app.page.update()
            except Exception:
                pass

    def on_fix_click(e):
        """Gestisce il click sui pulsanti delle variabili globali (Fix Scenes)"""
        data = e.control.data
        group_name = data.get("group_name", "?")
        group_id = data.get("group_id")
        scene_name = data.get("scene_name", "?")
        scene_id = data.get("scene_id")

        if group_id == 0:
            app.allarme = (scene_id == 0)
            if hasattr(app, "mqtt") and hasattr(app.mqtt, "publish_message"):
                payload = '{"state": "ON"}' if app.allarme else '{"state": "OFF"}'
                app.mqtt.publish_message("HomeZig/System/Allarme", payload)

        elif group_id == 1:
            app.modo = (scene_id == 0)
            if hasattr(app, "mqtt") and hasattr(app.mqtt, "publish_message"):
                payload = '{"state": "ON"}' if app.modo else '{"state": "OFF"}'
                app.mqtt.publish_message("HomeZig/System/Modo", payload)

    #   -----   👀  SUBSCRIPTION A EVENTI GLOBALI               👀  -----     #
    subscribe_events()

    #   -----   👀  STRUTTURA UNIFORMATA            👀  -----   #  
    #   ✍🏻      TITLE BAR
    title_bar = TitleCard(
        title=title,
        icon=ft.Icons.PENDING_ACTIONS,
        info_items=[
            "Azioni rapide e scene predefinite"
        ],
        refresh_callback=reload_page,
        refresh_tooltip=f"Aggiorna dati {title}"
    )

    #   ✍🏻      LOADING INDICATOR
    loading_indicator = ft.Container(
        content=ft.Row([
            ft.ProgressRing(width=20, height=20),
            ft.Text("Caricamento dati in corso...", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
        ], spacing=10),
        padding=10, visible=True
    )
    app.page.update()

    #   ✍🏻      FIX CARDS (Scene)
    fix_dict["Allarme"] = {
        "id": 0,
        "scenes": [
            {"id": 0, "name": "On"},
            {"id": 1, "name": "Off"}
        ]
    }
    fix_dict["Luci Mode Living"] = {
        "id": 1, 
        "scenes": [
            {"id": 0, "name": "Auto"}, 
            {"id": 1, "name": "Manuale"}
        ]
    }
    
    for group_name, group in fix_dict.items():
        scene_buttons = [
            ft.TextButton(
                scene["name"],
                icon=ft.Icons.GESTURE,
                icon_color=get_theme_color(app.page, "secondary"),
                data={"group_name": group_name, "group_id": group.get("id"), "scene_id": scene["id"], "scene_name": scene["name"]},
                style=ft.ButtonStyle(color=get_theme_color(app.page, "secondary")),
                on_click=on_fix_click
            ) for scene in group["scenes"]
        ]
        icon = scene_buttons[0].icon if scene_buttons and hasattr(scene_buttons[0], "icon") else ft.Icons.THEATER_COMEDY
        card = SceneCard(
            scene_name=group_name,
            scene_id=group.get("id"),
            icon=icon
        )
        card.content.content.controls[2].controls = scene_buttons
        # Aggiungi data anche al container della card per coerenza
        card.data = {"group_name": group_name, "group_id": group.get("id")}
        fix_cards.append(card)
    
        #   ✍🏻      DEVICES ROW
    scenes_row_ref = ft.Ref[ft.ResponsiveRow]()
    scenes_row = ft.ResponsiveRow([], spacing=5, ref=scenes_row_ref)

    log.debug(f"✅ Caricamento completato della {title}.")
    loading_indicator.visible = False

    col = ft.Column([
        title_bar,
        loading_indicator,
        ft.ResponsiveRow([
            *(ft.Container(card, col=RESPONSIVE_COLS) for card in fix_cards)
        ], spacing=5),
        scenes_row
    ],
    scroll=ft.ScrollMode.AUTO,
    spacing=5,                                                                  #   👀  Spazio tra i gruppi di livelli                  
    margin=ft.Margin(left=0, right=5, top=0, bottom=5),                         #   👀  Margini intera finestra
    expand=True,
    alignment=ft.MainAxisAlignment.START)

    loading_thread = threading.Thread(target=load_progressively, daemon=True, name="ActionLoader")
    loading_thread.start()

    app.page.update()
    return col