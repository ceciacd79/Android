# -*- coding: utf-8 -*-
"""
Home Page - Pagina principale dell'applicazione
"""

import flet as ft
import inspect as ins
import logging
import threading
import time
import websockets

from common.config import FLOOR_OPTIONS, RESPONSIVE_COLS
from common.helpers import get_theme_color
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from functools import wraps

from starlette.websockets import WebSocketDisconnect

if TYPE_CHECKING:
    from main import App

log = logging.getLogger(__name__)

#   -----   👀  DECORATOR       👀  -----   #
def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        if (total_time>= 0.05):
            log.debug(f'Run def in {total_time:.4f} seconds')
        return result
    return timeit_wrapper

@timeit
def get_content(app: 'App', title: str = "Home Page") -> ft.Column:
    """ Restituisce il contenuto della pagina"""
    instance_id = datetime.now().timestamp()
    app.running_threads[app.current_page_index] = instance_id

    # 👀    Import Custom Card
    from components._14594 import _14594Card
    from components.BaseCard import BaseCard
    from components.cons import ConsWidget
    from components.cons_bar import ConsBarWidget
    from components.CustomControl import CustomControl
    from components.CustomCard import CustomCard
    from components.DropDownCard import DropDownCard
    from components.DoubleInCard import DoubleInCard
    from components.E22X4Card import E22X4Card
    from components.E2134Card import E2134Card
    from components.E2201Card import E2201Card
    from components.LED2004G8Card import LED2004G8Card
    from components.LED2005R5_LED2106R3Card import LED2005R5_LED2106R3Card
    from components.LED2107C4Card import LED2107C4Card
    from components.MeteoCard import MeteoCard
    from components.MqttCard import MqttCard
    from components.PJ1203ACard import PJ1203ACard
    from components.RadioCard import RadioCard
    from components.SceneCard import SceneCard
    from components.SHSC07Card import SHSC07Card
    from components.SNZB01PCard import SNZB01PCard
    from components.SNZB02PCard import SNZB02PCard
    from components.SNZB04PCard import SNZB04PCard
    from components.SwitchCard import SwitchCard
    from components.TH02ZCard import TH02ZCard
    from components.TitleCard import TitleCard
    from components.TS0201Card import TS0201Card
    from components.TS0601_soil_3Card import TS0601_soil_3Card
    from components.ZBMINIR2Card import ZBMINIR2Card
    from components.ZG222ZCard import ZG222ZCard
    
    loc_mapp, device_containers = {}, {}
    is_subscribed = False
    warned_models = set()
    fix_cards = []
    list_cons_widgets = []
    devices_col_ref = ft.Ref[ft.Column]()
    log_column_ref = ft.Ref[ft.Column]()

    consumi_widget = ConsWidget(app, title="Consumi")

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

    def create_card_for_device(dev):
        """Crea l'istanza della card appropriata per il dispositivo"""
        try:
            model = dev.get("MODEL", "Unknown Model")
        except Exception as e:
            app.show_error_snackbar(f"Errore DB: {str(e)}")
        match model:
            case "14594":
                return _14594Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "E22x4":
                return E22X4Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "E2134":
                return E2134Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "E2201":
                return E2201Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "LED2004G8":
                return LED2004G8Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "LED2005R5/LED2106R3":
                return LED2005R5_LED2106R3Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "LED2107C4":
                return LED2107C4Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "PJ-1203A":
                return PJ1203ACard(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "SH-SC07":
                return SHSC07Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "SNZB-01P":
                return SNZB01PCard(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "SNZB-02P":
                return SNZB02PCard(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "SNZB-04P":
                return SNZB04PCard(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "TH02Z":
                return TH02ZCard(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "TH09Z":
                return TS0201Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )            
            case "TS0201":
                return TS0201Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "TS0601_soil_3":
                return TS0601_soil_3Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "ZBMINIR2":
                return ZBMINIR2Card(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case "ZG-222Z":
                return ZG222ZCard(dev.get("FRIENDLY_NAME", ""), model,
                    status=dev.get("STATUS", "Unknown"),
                    data=dev.get("data", {}),
                    floor=dev.get("FLOOR", "N/A"),
                    name=dev.get("NAME", ""),
                    pos=dev.get("POSITION", ""),
                    page=app.page
                )
            case _:
                if model not in warned_models:
                    f_name =dev.get("FRIENDLY_NAME", {})
                    if (f_name == "Coordinator") or (f_name == "Router"):
                        return
                    else:
                        log.warning(f"Modello non gestito nella home: {model}.")
                        warned_models.add(model)
                
                return ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"Model: {model}", size=12, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Name: {dev.get('FRIENDLY_NAME', 'Unknown')}", size=12)
                        ], spacing=2),
                        padding=10
                    )
                )

    def on_mapp_updated(message):
        """Questa funzione viene chiamata ogni volta che app.page.pubsub.send_all è invocato"""
        try:
        # Se non siamo sulla pagina Home, evita aggiornamenti inutili
            if app.current_page_index != 0:
                return

            nonlocal loc_mapp
            if isinstance(message, dict) and message.get("type") == "mapp_updated":
                # log.info(f"[HomePage] Ricevuto segnale di aggiornamento mapp.")
                topic = message.get("topic", "")
                loc_mapp = message.get("data", {})  # Aggiorna i dati locali completi
                
                idx, name, type = Decode_Topic(topic)
                target_fname = f"{type}/{name}"

                found_dev = None
                for devices in loc_mapp.values():
                    for d in devices:
                        if str(d.get("FRIENDLY_NAME")).upper() == str(target_fname).upper():
                            found_dev = d
                            break
                    if found_dev: break
                
                if not found_dev:
                    return

                # Aggiornamento puntuale se il container esiste
                if target_fname in device_containers:
                    container = device_containers[target_fname]
                    
                    card = container.content
                    if hasattr(card, "update_data"):
                        try:
                            card.update_data(found_dev.get("data", {}))

                            # --- GESTIONE VISIBILITÀ CONTAINER ---
                            if not container.visible:
                                container.visible = True
                                try:
                                    if container.page:
                                        container.update()
                                except Exception as e:
                                    log.warning(f"[HomePage] Impossibile aggiornare la visibilità del container: {e}")
                            
                            # --- ✅ FORZA UPDATE GRAFICO DELLA CARD PER MOSTRARE I NUOVI TESTI ---
                            try:
                                if card.page:
                                    card.update()
                            except Exception as e:
                                log.warning(f"[HomePage] Impossibile eseguire card.update(): {e}")

                            log.debug(f"[HomePage] Card aggiornata puntualmente: {target_fname}")
                        except Exception as e:
                            if "must be added" not in str(e):
                                raise e
                        return # Stop qui, update fatto

                temp_card = create_card_for_device(found_dev)
                if temp_card:
                    if devices_col_ref.current:
                        devices_col_ref.current.controls = render_devices(loc_mapp)
                        try:
                            if devices_col_ref.current.page:
                                devices_col_ref.current.update()
                                app.page.update()
                        except (WebSocketDisconnect, websockets.exceptions.InvalidState):
                            log.warning("WebSocket chiuso, interrompo l'update.")
                        except Exception as e:
                            if "must be added" not in str(e):
                                raise e
                # Se temp_card è None, è un modello non gestito -> IGNORA re-render.
        except (WebSocketDisconnect, websockets.exceptions.InvalidState):
            log.warning("WebSocket chiuso, interrompo l'update.")
        except Exception as e:
            log.error(f"Errore in on_mapp_updated: {e},  {message.get('topic', '')}")

    def reload_page(e):
        try:
            # 1. Verifica di sicurezza sul container del main.py
            if not app.content_container or not app.content_container.page:
                log.warning("Impossibile ricaricare: Container non collegato alla pagina.")
                return

            # 2. Ottieni il nuovo contenuto (senza update interni)
            new_content = get_content(app, "Dashboard")
            
            # 3. Sostituisci e aggiorna il container 'padre'
            app.content_container.content = new_content
            app.content_container.update()

        except (WebSocketDisconnect, websockets.exceptions.InvalidState):
            log.warning("WebSocket chiuso, interrompo l'update.")
        except Exception as ex:
            log.error(f"Errore durante il reload: {ex}")

    def last_seen_recent(last_seen_epoch):
        """Controlla se last_seen è entro le ultime 48 ore"""
        # 🌟 Recuperiamo TIME_MSG (che è un numero Epoch, es. 1780254000.11)
        now_epoch = time.time()
        day_ago_epoch = now_epoch - (48 * 3600)
        is_recent = False
        if last_seen_epoch:
            try:
                last_seen_epoch = float(last_seen_epoch)                        # Ci assicuriamo che sia trattato come numero (float o int)
                if last_seen_epoch > day_ago_epoch:                             # Filtro per Data: Confronto matematico diretto tra numeri!
                    is_recent = True
            except (ValueError, TypeError):
                log.error(f"Errore conversione TIME_MSG: valore non numerico ({last_seen_epoch}).")
        return is_recent

    def load_progressively():
        time.sleep(0.2)  # Lascia il tempo per montare l'interfaccia
        nonlocal loc_mapp
        try:
            app.is_loading = True
            if app.running_threads.get(app.current_page_index) != instance_id:
                return
            loc_mapp = app.mapp
            # --- LOGICA DINAMICA PER PJ-1203A ---
            
            for level, devices in loc_mapp.items():
                for dev in devices:
                    model = dev.get("MODEL", "Unknown")
                    # 1. Filtro per Modello
                    if model == "PJ-1203A":
                        idx, name, type = Decode_Topic(dev.get("FRIENDLY_NAME", ""))
                        last_seen_epoch = dev.get("data", {}).get("TIME_MSG")
                        is_recent = last_seen_recent(last_seen_epoch)
                        new_cons_widget = ConsWidget(app, title=name, tab=name)

                        list_cons_widgets.append(
                            ft.Container(
                                content=new_cons_widget,
                                col=RESPONSIVE_COLS,
                                margin=ft.Margin.only(left=8, right=8),
                                visible=is_recent 
                            )
                        )
            cards = render_devices(loc_mapp)
        
            if app.running_threads.get(app.current_page_index) == instance_id:
                if devices_col_ref.current:
                    devices_col_ref.current.controls = cards
                    try:
                        if devices_col_ref.current.page:
                            devices_col_ref.current.update()
                    except Exception as e:
                        if "must be added" not in str(e):
                            log.warning(f"Errore UI devices update: {e}")

            if len(loc_mapp) == 0:
                log.warning("Mappa dispositivi vuota dopo caricamento.")
                app.show_error_snackbar("Attenzione: Nessun dispositivo trovato. Verifica la connessione al database.")

        except (WebSocketDisconnect, websockets.exceptions.InvalidState):
            log.warning("WebSocket chiuso, interrompo l'update.")
        except Exception as e:
            log.error(f"Errore caricamento: {e}")
            if app.page:
                app.show_error_snackbar(f"Errore loading: {str(e)}")
        finally:
            app.is_loading = False
            # Verifica finale prima di nascondere il loading
            if app.running_threads.get(app.current_page_index) == instance_id:
                loading_indicator.visible = False
                try:
                    if loading_indicator.page:
                        loading_indicator.update()
                    elif app.page:
                        app.page.update()
                except Exception as e:
                    if "must be added" not in str(e):
                        log.error(f"Errore finale aggiornamento loading indicator: {e}")

    def update_log_container(update_ui=True):
        new_rows = []
        if hasattr(app, 'recent_logs'):
            for log_entry in reversed(list(app.recent_logs)):
                color = ft.Colors.RED if log_entry.get("type") == "ERROR" else ft.Colors.GREEN
                new_rows.append(
                    ft.Row([
                        ft.Text(log_entry.get("time", ""), size=12, color=ft.Colors.GREY),
                        ft.Text(log_entry.get("type", ""), size=10, weight=ft.FontWeight.BOLD, color=color),
                        ft.Text(log_entry.get("msg", ""), size=12, color=ft.Colors.ON_SURFACE, selectable=True, overflow=ft.TextOverflow.ELLIPSIS, expand=True)
                    ], spacing=5, alignment=ft.MainAxisAlignment.START)
                )
        if log_column_ref.current:
            log_column_ref.current.controls = new_rows if new_rows else [ft.Text("Nessun messaggio recente.", size=12, italic=True)]
            if update_ui:
                try:
                    log_column_ref.current.update()
                except Exception:
                    pass # Ignora se non attaccato alla pagina

    def render_devices(mapp_data):
        level_groups = []
        device_containers.clear() # Reset mappa

        now_epoch = time.time()
        one_day_ago_epoch = now_epoch - (24 * 3600)

        if not mapp_data:
            return level_groups
   
        now_epoch = time.time()
        one_day_ago_epoch = now_epoch - (24 * 3600)

        for level, devices in mapp_data.items():
            cards = []
            for dev in devices:
                card = create_card_for_device(dev)
                if not card:
                    continue

                f_name = dev.get("FRIENDLY_NAME")
                model = dev.get("MODEL")

                last_seen_epoch = dev.get("data", {}).get("TIME_MSG")
                is_recent = last_seen_recent(last_seen_epoch)
                    
                container = ft.Container(
                    card, 
                    col=RESPONSIVE_COLS,
                    visible=is_recent   
                )

                if f_name:
                    device_containers[f_name] = container
                
                cards.append(container)
            
            # --- STRUTTURA ESATTA DEL TUO CODICE ---
            floor_name = next((name for name, val in FLOOR_OPTIONS if val == level), "Non assegnato")
            group_title = ft.Text(f"Piano {floor_name}", 
                                  theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                                  margin=ft.Margin(5, 0, 0, 0)
            ) # 👀  Margin modificato per ridurre spazio sopra il titolo
            group_row = ft.ResponsiveRow(cards, spacing=5)
            level_groups.append(
                ft.Container(
                    content=ft.Column([
                        group_title,
                        group_row
                    ], spacing=5),
                    padding=5,
                    margin=ft.Margin(5, 0, 0, 0), # 👀  Margin modificato per ridurre spazio tra i gruppi
                    border_radius=10
                )
            )
        return level_groups

    def on_page_event(message):
        """Gestisce tutti gli eventi pubsub per la Home"""
        # Se non siamo sulla pagina Home, evita aggiornamenti inutili
        if app.current_page_index != 0:
            return
        if isinstance(message, dict):
            # Aggiornamento puntuale Logs
            if message.get("type") == "logs_updated":
                update_log_container()
            # Aggiornamento Mappa Device
            elif message.get("type") == "mapp_updated":
                on_mapp_updated(message)

    def subscribe_events():
        nonlocal is_subscribed
        try:
            # Defensive cleanup: if a stale listener exists, remove it before subscribing again.
            app.page.pubsub.unsubscribe(on_page_event)
        except Exception:
            pass
        app.page.pubsub.subscribe(on_page_event)
        is_subscribed = True

    def unsubscribe_events():
        nonlocal is_subscribed
        if not is_subscribed:
            return
        try:
            app.page.pubsub.unsubscribe(on_page_event)
        finally:
            is_subscribed = False

    subscribe_events()
    
    #   -----   👀  STRUTTURA UNIFORMATA            👀  -----   #  
    #   ✍🏻      TITLE BAR
    title_bar = TitleCard(
        title=title,
        icon=ft.Icons.HOME,
        info_items=[
            f"IP Server: {app.page.url if hasattr(app.page, 'url') else 'N/A'}",
            f"Platform: {app.page.platform}"
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
    
    cons_container = ft.Container(
        content=consumi_widget,
        col=RESPONSIVE_COLS,
        margin=ft.Margin.only(left=10, right=10)
    )

    #   ✍🏻      ️DEVICES COLUMNS
    columns_devices = ft.Column(
        controls=render_devices(loc_mapp),
        spacing=1,
        ref=devices_col_ref
    )

    log.debug(f"✅ Caricamento completato della {title}.")
    col = ft.Column([
        title_bar,
        loading_indicator,
        ft.ResponsiveRow(
            controls=list_cons_widgets,
            alignment=ft.MainAxisAlignment.START,
            spacing=5
        ),
        ft.ResponsiveRow([
            *(ft.Container(card, col=RESPONSIVE_COLS) for card in fix_cards)
        ], spacing=5),
        columns_devices
    ],
    scroll=ft.ScrollMode.AUTO,
    spacing=5,                                                                  #   👀  Spazio tra i gruppi di livelli                  
    margin=ft.Margin(left=0, right=5, top=0, bottom=5),                         #   👀  Margini intera finestra
    expand=True,
    alignment=ft.MainAxisAlignment.START)

    loading_thread = threading.Thread(target=load_progressively, daemon=True, name="HomeLoader")
    loading_thread.start()

    col.on_resume = lambda: (subscribe_events(), update_log_container(update_ui=False))
    col.on_pause = unsubscribe_events

    if app.page:
        app.page.update()
    return col