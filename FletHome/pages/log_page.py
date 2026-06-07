# -*- coding: utf-8 -*-
"""
Log Page - Pagina dei log dell'applicazione
"""

import flet as ft
import inspect as ins
import logging
import threading

from common.config import RESPONSIVE_COLS
from common.helpers import get_theme_color
from common.ui import show_login_dialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

log = logging.getLogger(__name__)

loc_log = []

def get_content(app: 'App', title: str = "Lista eventi") -> ft.Column:
    """ Restituisce il contenuto della pagina"""
    from components.TitleCard import TitleCard
    from components.SceneCard import SceneCard
    
    global loc_log
    session_id = getattr(getattr(app.page, "session", None), "id", "N/A")

    loc_log = app.logs if hasattr(app, "logs") else []
    current_page_id = app.current_page_index


    def reload_page(e=None):
        """Ricarica la pagina Log aggiornando i dati e la UI."""
        if hasattr(app, 'pages_cache') and app.current_page_index in app.pages_cache:
            del app.pages_cache[app.current_page_index]
        app.ref_logs_cache()
        app.content_container.content = get_content(app, title)
        app.content_container.update()  

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

    def on_page_event(message):
        if not isinstance(message, dict) or message.get("type") != "logs_updated":
            return
        try:
            log.debug(
                f"[session:{session_id}] Evento logs_updated ricevuto in LogPage (captured={current_page_id}, current={app.current_page_index})"
            )
            update_table()
            log_table.update()
            if app.content_container:
                app.content_container.update()
        except Exception as e:
            log.error(f"[session:{session_id}] Errore aggiornamento UI LogPage su evento logs_updated: {e}")

    def subscribe_events():
        if app.page and hasattr(app.page, "pubsub"):
            log.debug(f"[session:{session_id}] Iscrivendo eventi in LogPage")
            if hasattr(app.page.pubsub, "subscribe"):
                app.page.pubsub.subscribe(on_page_event)
                log.debug(f"[session:{session_id}] Iscrizione a eventi con metodo subscribe")
            elif hasattr(app.page.pubsub, "add_listener"):
                app.page.pubsub.add_listener(on_page_event)
                log.debug(f"[session:{session_id}] Iscrizione a eventi con metodo add_listener")
            app._log_page_listener = on_page_event
            log.debug(f"[session:{session_id}] Listener salvato in app._log_page_listener")

    def unsubscribe_events():
        if app.page and hasattr(app.page, "pubsub"):
            if hasattr(app.page.pubsub, "unsubscribe"):
                app.page.pubsub.unsubscribe(on_page_event)
            elif hasattr(app.page.pubsub, "remove_listener"):
                app.page.pubsub.remove_listener(on_page_event)

    def unsubscribe_previous_listener():
        prev_listener = getattr(app, "_log_page_listener", None)
        if not prev_listener:
            return
        if app.page and hasattr(app.page, "pubsub"):
            try:
                if hasattr(app.page.pubsub, "unsubscribe"):
                    app.page.pubsub.unsubscribe(prev_listener)
                elif hasattr(app.page.pubsub, "remove_listener"):
                    app.page.pubsub.remove_listener(prev_listener)
            except Exception as e:
                log.debug(f"[session:{session_id}] Listener log precedente non rimosso: {e}")

    #   -----   👀  SUBSCRIPTION A EVENTI GLOBALI               👀  -----     #
    unsubscribe_previous_listener()
    subscribe_events()

    log_table = ft.DataTable(
        vertical_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        horizontal_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        heading_row_color=ft.Colors.PRIMARY_CONTAINER,
        data_row_color={ft.ControlState.HOVERED: ft.Colors.BLACK12},
        show_checkbox_column=False,
        column_spacing=20,
        horizontal_margin=12,
        data_row_min_height=40,
        data_row_max_height=48,
        heading_row_height=45,
        columns=[
            ft.DataColumn(label=ft.Text("ID", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0), visible=False),
            ft.DataColumn(label=ft.Text("Giorno", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Ora", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Type", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Room", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Floor", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Message", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
        ],
        rows=[]
    )

    def update_table():
        global loc_log

        log_table.rows.clear()
        try:
            loc_log = app.logs if hasattr(app, "logs") else []
            for logs in loc_log:           
                row = ft.DataRow(cells=[
                    ft.DataCell(ft.Text(logs.ID_KEY, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0), visible=False),   
                    ft.DataCell(ft.Text(logs.DAY_U.strftime("%Y-%m-%d"), theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                    ft.DataCell(ft.Text(logs.TIME_U.strftime("%H:%M:%S"), theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                    ft.DataCell(ft.Text(logs.TYPE, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                    ft.DataCell(ft.Text(logs.ROOM, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                    ft.DataCell(ft.Text(logs.FLOOR, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                    ft.DataCell(ft.Text(logs.MSG, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ])
                log_table.rows.append(row)
        except Exception as e:
            log.error(f"Errore durante l'aggiornamento della tabella dei log: {e}")

    def refresh_log_page_ui():
        update_table()
        log_table.update()
        if app.content_container:
            app.content_container.update()

    app.log_page_refresh = refresh_log_page_ui

    update_table()                                                  #   ℹ️   Inizializza tabella con dati esistenti

    table_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Log", theme_style=ft.TextThemeStyle.TITLE_LARGE)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(
                content=ft.Row([log_table], scroll=ft.ScrollMode.AUTO),
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )
        ]), 
        padding=10,
        border_radius=10,
        bgcolor="surfaceVariant",
        expand=True
    )

    #   -----   👀  STRUTTURA UNIFORMATA            👀  -----   #  
    #   ✍🏻      TITLE BAR
    title_bar = TitleCard(
        title=title,
        icon=ft.Icons.PENDING_ACTIONS,
        info_items=[
            "Log degli eventi dell'applicazione",
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
      
    log.debug(f"✅ Caricamento completato della {title}.")
    loading_indicator.visible = False

    col = ft.Column([
        title_bar,
        loading_indicator,
        table_container
    ],
    scroll=ft.ScrollMode.AUTO,
    spacing=5,                                                                  #   👀  Spazio tra i gruppi di livelli                  
    margin=ft.Margin(left=0, right=5, top=0, bottom=5),                         #   👀  Margini intera finestra
    expand=True,
    alignment=ft.MainAxisAlignment.START)

    app.page.update()
    return col