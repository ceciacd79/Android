# -*- coding: utf-8 -*-
#!/usr/bin/python
#   .\.venv\Scripts\Activate.ps1
# my_flet_app/
# │
# ├── main.py                # Entry point dell'app Flet
# │
# ├── pages/                 # (Opzionale) Moduli per le varie pagine/view
# │   ├── home_page.py
# │   └── settings_page.py
# │
# ├── components/            # (Opzionale) Componenti UI riutilizzabili
# │   ├── nav_bar.py
# │   └── mqtt_card.py
# │
# ├── services/              # (Opzionale) Logica di business, API, MQTT, ecc.
# │   └── mqtt_service.py
# │
# ├── assets/                # (Opzionale) File statici: immagini, icone, ecc.
# │   └── logo.png
# │
# └── utils/                 # (Opzionale) Funzioni di utilità
#     └── helpers.py

#   -----   👀  FONT SIZE       👀  -----   #
# Display
# Headline
# Title
# Label
# body
#   -----   👀  COLORI FLET     👀  -----   #
#   Colore	                    Descrizione	                Uso
#   ft.Colors.PRIMARY	        Colore primario del tema	Pulsanti principali, elementi di enfasi
#   ft.Colors.SECONDARY	        Colore secondario	        Pulsanti secondari, chip
#   ft.Colors.SURFACE	        Sfondo superficie	        Card, dialog, menu
#   ft.Colors.SURFACE_VARIANT	Variante superficie	        Container, card secondarie ✅
#   ft.Colors.BACKGROUND	    Sfondo pagina	            Sfondo principale
#   ft.Colors.ERROR	            Colore errore	            Messaggi di errore
#   ft.Colors.ON_PRIMARY	    Testo su primario	        Testo su pulsanti primari
#   ft.Colors.ON_SURFACE	    Testo su superficie	        Testo standard ✅
#   ft.Colors.ON_BACKGROUND	    Testo su sfondo	            Testo su pagina
#   ft.Colors.OUTLINE	        Bordi/divisori	            Bordi, divider ✅
#   ft.Colors.OUTLINE_VARIANT	Bordi secondari	            Bordi meno evidenti

#   1. Colori di Superficie (Surface)
#   Questi sono quelli che cercavi specificamente, usati per sfondi, card e livelli:
#   surface: Il colore di sfondo principale.
#   surface_dim: Una versione più scura (per il tema chiaro) o più profonda della superficie.
#   surface_bright: Una versione più luminosa della superficie (quello che citavi).
#   surface_container_lowest: Il livello di elevazione più basso (sfondo più scuro).
#   surface_container_low: Elevazione bassa.
#   surface_container: Il contenitore standard (es. per le Card).
#   surface_container_high: Elevazione alta.
#   surface_container_highest: Il livello di elevazione massimo.
#   surface_variant: Una variante cromatica per differenziare sezioni.
#   on_surface: Il colore del testo/icone sopra la superficie.
#   on_surface_variant: Testo/icone con enfasi minore.
#   inverse_surface: Colore invertito (es. per Snackbars).
#   on_inverse_surface: Testo sopra la superficie invertita.

#   2. Colori Accento (Core Palette)
#   Ogni gruppo ha 4 varianti (Colore, On-Colore, Container, On-Container):
#   Primary Group: primary, on_primary, primary_container, on_primary_container.
#   Secondary Group: secondary, on_secondary, secondary_container, on_secondary_container.
#   Tertiary Group: tertiary, on_tertiary, tertiary_container, on_tertiary_container.
#   Error Group: error, on_error, error_container, on_error_container.

#   3. Altri colori di utilità
#   outline: Per bordi e divisori (contrasto medio).
#   outline_variant: Per bordi con contrasto molto basso.
#   shadow: Il colore delle ombre.
#   scrim: Il colore che oscura il contenuto dietro un Drawer o un Modal.
#   inverse_primary: Usato raramente, per elementi che devono richiamare il Primary su superfici invertite.

__author__ = "Cechich Diego"
__copyright__ = "Copyright 2026"
__version__ = "0.2.0"
__license__ = "GPL"
__annotations__ = "HomeZig Flet Application"

#   -----   👀  MODULE          👀  -----   #
import flet as ft
import queue
import inspect as ins
import json
import logging
import os
import schedule
import sys
import threading
import time
import copy
import math

from collections import deque
from datetime import datetime
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# -----     👀  Load environment variables from .env file
from dotenv import dotenv_values
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(base_path)
env_path = os.path.join(base_path, '.env')
env = dict(os.environ)
if os.path.exists(env_path):
    env = dotenv_values(env_path)
    debug = env.get("DEBUG", "False") == "True"

from common.config import COLOR_MAP
from common.home import Home as sqlm
from common.home import CALENDAR as cal
from common.info import Info as inf
from common.info import Meteo as pv
from common.info import UTILITY as utils
from common.file_op import file as file
from common.mqtt_cust import MqttCust
from functools import wraps

from components.MeteoCard import MeteoCard

# 👀    Import pagine modulari
from pages import home_page
from pages import actions_page
from pages import meteo_page 
from pages import mqtt_page
from pages import schedule_page
from pages import settings_page
from pages import log_page
from pages import calend_page
from pages import chart_page
from pages import database_page

nav_items = [
    {"icon": ft.Icons.HOME_OUTLINED, "selected_icon": ft.Icons.HOME, "label": "Home", "function": home_page.get_content},
    {"icon": ft.Icons.CALENDAR_MONTH, "selected_icon": ft.Icons.CALENDAR_MONTH, "label": "Calendario", "function": calend_page.get_content},
    {"icon": ft.Icons.WEB_OUTLINED, "selected_icon": ft.Icons.WEB, "label": "Azioni", "function": actions_page.get_content},
    {"icon": ft.Icons.WB_SUNNY_OUTLINED, "selected_icon": ft.Icons.WB_SUNNY, "label": "Meteo", "function": meteo_page.get_content},
    {"icon": ft.Icons.DNS_OUTLINED, "selected_icon": ft.Icons.DNS, "label": "Mqtt", "function": mqtt_page.get_content},
    {"icon": ft.Icons.PENDING_ACTIONS_OUTLINED, "selected_icon": ft.Icons.PENDING_ACTIONS, "label": "Schedule", "function": schedule_page.get_content},
    {"icon": ft.Icons.SETTINGS_OUTLINED, "selected_icon": ft.Icons.SETTINGS, "label": "Settings", "function": settings_page.get_content},
    {"icon": ft.Icons.INFO_OUTLINE, "selected_icon": ft.Icons.INFO, "label": "Info", "function": log_page.get_content},
]

#   -----   👀  DEFINE          👀  -----   #
debug = False

#   -----   👀  GLOBAL VARIABLE 👀  -----   #
msg_queue = queue.Queue()

GLOBAL_CACHED_MAPP = None                   # Cache per i dati dei dispositivi (mappatura)
GLOBAL_CACHED_SCENE = None                  # Cache per i dati delle scene (scene_group_join)
GLOBAL_CACHED_SCHEDULE = None               # Cache per i dati della schedule (tab_schedule)
GLOBAL_CACHED_ACTIONS = None                # Cache per i dati delle azioni (tab_action)
GLOBAL_CACHED_TABLE = None                  # Cache per i dati delle tabelle (tab_table)
GLOBAL_CACHED_CALENDAR = None               # Cache per i dati calendario
GLOBAL_CACHED_GROUPS = None                 # Cache per i dati dei gruppi (bridge/groups)
GLOBAL_CACHED_ENEL = None                   # Cache per i dati Enel
GLOBAL_CACHED_LOG = None                    # Cache per i dati dei log

def up_cache(dbm_instance):
    """Aggiorna le cache globali con i dati più recenti dal database. Deve essere chiamata ogni volta che si sospetta che i dati siano cambiati (es. dopo modifiche, azioni, ecc.)"""
    global GLOBAL_CACHED_MAPP
    global GLOBAL_CACHED_SCENE
    global GLOBAL_CACHED_SCHEDULE
    global GLOBAL_CACHED_ACTIONS
    global GLOBAL_CACHED_TABLE
    global GLOBAL_CACHED_GROUPS
    global GLOBAL_CACHED_ENEL
    global GLOBAL_CACHED_LOG

    log.debug("🔄 Cache Globale aggiornate dal DB")
    try:
        if dbm_instance is not None:
            loc_mapp = dbm_instance.GET_DEVICES_INFO_BY_LEVEL()
            if loc_mapp:
                GLOBAL_CACHED_MAPP = loc_mapp
            loc_scene = dbm_instance.GET_SCENE_GROUP_JOIN()
            if loc_scene:
                GLOBAL_CACHED_SCENE = loc_scene
            loc_schedule = dbm_instance.GET_TAB_SCHEDULE()
            if loc_schedule:
                GLOBAL_CACHED_SCHEDULE = loc_schedule
            loc_actions = dbm_instance.GET_TAB_ACTION()
            if loc_actions:
                GLOBAL_CACHED_ACTIONS = loc_actions
            loc_table = dbm_instance.GET_TABLE()
            if loc_table:
                GLOBAL_CACHED_TABLE = loc_table
            loc_groups = dbm_instance.GET_SCENE_GROUP_JOIN()
            if loc_groups:
                GLOBAL_CACHED_GROUPS = loc_groups
            loc_enel = dbm_instance.GET_ENEL("CONS_01", datetime.now().date().strftime("%Y-%m-%d"))
            if loc_enel:
                GLOBAL_CACHED_ENEL = loc_enel
            loc_log = dbm_instance.GET_TAB_LOG()
            if loc_log:
                GLOBAL_CACHED_LOG = loc_log
    except Exception as e:
        log.error(f"Errore aggiornamento cache globale: {e}")

def up_cache_log(dbm_instance):
    """Aggiorna la cache dei log globali con i dati più recenti dal database. Deve essere chiamata ogni volta che si sospetta che i dati dei log siano cambiati (es. dopo modifiche, azioni, ecc.)"""
    global GLOBAL_CACHED_LOG
    log.debug("🔄 Cache Log Globale aggiornata dal DB")
    try:
        if dbm_instance is not None:
            loc_log = dbm_instance.GET_TAB_LOG()
            if loc_log:
                GLOBAL_CACHED_LOG = loc_log
    except Exception as e:
        log.error(f"Errore aggiornamento cache log globale: {e}")

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

#   -----   👀  WORK CLASS      👀  -----   #
active_sessions = 0  # Numero di sessioni/pagine Flet attive

class AppManager:
    def __init__(self, page, sql=None, meteo=None, calen=None, sett=None):   
        self.page = page
        self.dbm = sql
        self.meteo = meteo
        self.cal = calen
        self.settings = sett

        self.mapp = {}
        self.scene = {}
        self.current_page_index = 0
        self.pages_cache = {}
        self.content_container = None
        self.require_login = False
        self.running_threads = {}
        self.allarme = True                                                                     # ℹ️ Mqtt variabile sistema Allarme: True = Attivo, False = Disattivato
        self.modo = True                                                                        # ℹ️ Mqtt variabile sistema Modalità luci living: True = Automatico, False = Manuale
        self.up_sched = False                                                                   # ℹ️ Mqtt variabile sistema Aggiornamento schedule: True = In corso, False = Non in corso
        self.up_actions = False                                                                 # ℹ️ Mqtt variabile sistema Aggiornamento azioni: True = In corso, False = Non in corso

        self.Set_settings()

        self.mqtt = MqttCust()
        self.mqtt_handlers = []

        self.page.app = self

        self.key_sql = self.settings.get("key_sql", ["temperature", "humidity", "illuminance", "occupancy", "soil_moisture"])
        self.key_act = self.settings.get("key_act", ["auto", "action", "contact", "occupancy", "battery", "battery_low", "state", "tamper", "water_leak"])
        self.key_rooms = self.settings.get("key_rooms", ["living", "kitchen", "bedroom", "bathroom", "garage"])
        self.key_floor = self.settings.get("key_floor", ["ground", "first", "second"])

        self.mqtt_connected = False                                                             # Stato connessione MQTT all'avvio
        client = getattr(self.mqtt, "mqtt_client", None)
        if client and hasattr(client, "is_connected"):
            self.mqtt_connected = client.is_connected()
            self.mqtt.publish_message("HomeZig/System/key_sql", json.dumps(self.key_sql))
            self.mqtt.publish_message("HomeZig/System/key_act", json.dumps(self.key_act))
            self.mqtt.publish_message("HomeZig/System/key_rooms", json.dumps(self.key_rooms))
            self.mqtt.publish_message("HomeZig/System/key_floor", json.dumps(self.key_floor))

        self._inactivity_timer = None
        self.reset_inactivity_timer()

        self.page.on_resize = self.on_resize

        self.up_calendar()

        def handler_state(topic, data):
            """Decodicfica i messagg MQTT di stato"""
            try:
                if "state" in topic and isinstance(data, dict):
                    try:
                        if hasattr(self.mqtt, "publish_message"):
                            self.mqtt.publish_message("HomeZig/bridge/groups", "{}")
                            log.debug("✅ MQTT attivo.")           
                            self.mqtt.publish_message("HomeZig/System/key_sql", json.dumps(self.key_sql))
                            self.mqtt.publish_message("HomeZig/System/key_act", json.dumps(self.key_act))
                            self.mqtt.publish_message("HomeZig/System/key_rooms", json.dumps(self.key_rooms))
                            self.mqtt.publish_message("HomeZig/System/key_floor", json.dumps(self.key_floor))
                    except Exception as ex_pub:
                        log.error(f"Errore publish stato connesso: {ex_pub}")
            except Exception as msg:
                log.error(f"Errore elaborazione messaggio MQTT: {msg}")

        def handler_msg(topic, data):
            """Prende in carico i messaggi MQTT"""

            def has_null_act_key(data, act_key):
                return any(data[k] is None for k in act_key if k in data)
            
            try:
                global msg_queue, active_sessions
                if "HomeZig/" in topic and ("bridge" not in topic) and ("System" not in topic) and isinstance(data, dict):
                    if active_sessions > 0:
                        if not has_null_act_key(data, self.key_act):
                            msg_queue.put((topic, data))
                        else:
                            log.debug(f"Messaggio scartato: una key è nulla, {data}")
                    else:
                        log.debug("Messaggio scartato: nessuna sessione attiva")
            except Exception as msg:
                log.error(f"Errore elaborazione messaggio MQTT: {msg}")

        def handler_devices(topic, data):
            """Decodifica i messaggi MQTT relativi ai dispositivi"""
            try:
                if "bridge" in topic and "devices" in topic and isinstance(data, list):
                    devices = data
                    log.debug(f"Ricevuti {len(devices)} devices da bridge/devices")
            except Exception as msg:
                log.error(f"Errore elaborazione messaggio MQTT: {msg}")

        def handler_groups(topic, data):
            """Decodifica i messaggi MQTT relativi ai gruppi"""
            try:
                if "bridge" in topic and "groups" in topic and isinstance(data, list):
                    log.debug(f"ℹ️ Recived '{topic}'.")
            except Exception as msg:
                log.error(f"Errore elaborazione messaggio MQTT: {msg}")

        def handler_error(error_message):
            """Gestisce gli errori MQTT"""
            try:
                log.error(f"Errore MQTT: {error_message}")
                self.show_error_snackbar(f"❌ Errore MQTT: {error_message}")
            except Exception as e:
                log.error(f"Errore nell'esecuzione dell'error handler: {e}")

        def handler_system(topic, data):
            """Gestisce i messaggi MQTT relativi al sistema"""
            try:
                if "HomeZig/System/Allarme" in topic and isinstance(data, dict):
                    state = data.get("state")
                    if state == "ON":
                        self.allarme = True
                    elif state == "OFF":
                        self.allarme = False
                elif "HomeZig/System/Modo" in topic and isinstance(data, dict):
                    state = data.get("state")
                    if state == "ON":
                        self.modo = True
                    elif state == "OFF":
                        self.modo = False
                elif "HomeZig/System/up_sched" in topic and isinstance(data, dict):
                    self.up_sched = False
                elif "HomeZig/System/up_actions" in topic and isinstance(data, dict):
                    self.up_actions = False
                elif "HomeZig/System/new_con" in topic and isinstance(data, dict):
                    if client and hasattr(client, "is_connected"):
                        self.mqtt_connected = client.is_connected()
                        self.mqtt.publish_message("HomeZig/System/key_sql", json.dumps(self.key_sql))
                        self.mqtt.publish_message("HomeZig/System/key_act", json.dumps(self.key_act))
                        self.mqtt.publish_message("HomeZig/System/key_rooms", json.dumps(self.key_rooms))
                        self.mqtt.publish_message("HomeZig/System/key_floor", json.dumps(self.key_floor))
                elif "HomeZig/System/log_up" in topic and isinstance(data, dict):
                    self.ref_logs_cache()
            except Exception as msg:
                log.error(f"Errore elaborazione messaggio MQTT: {msg}")

        # -----     👀      Add Handlers
        self.mqtt.mqtt_message_handler(handler_state)
        self.mqtt.mqtt_message_handler(handler_msg)
        self.mqtt.mqtt_message_handler(handler_groups)
        self.mqtt.mqtt_message_handler(handler_devices)
        self.mqtt.mqtt_message_handler(handler_system)
        self.mqtt.error_handler(handler_error)
        
        # Aggiungi alla lista di tracciamento per la pulizia al disconnect
        if hasattr(self, 'mqtt_handlers'):
            self.mqtt_handlers.extend([handler_state, handler_msg, handler_groups, handler_devices, handler_system, handler_error])              

        if inf.is_docker():
            log.info("🐳 Running inside DOCKER (Production Mode)")
            self.mqtt.mqtt_cl_ok(broker= env.get("MQTT_HOST"), port=int(env.get("MQTT_PORT", 1883)), user=env.get("MQTT_USER"), pwd=env.get("MQTT_PASSWORD"))
        else:
            log.info("💻 Running on LOCAL HOST (Test Mode)")
            self.mqtt.mqtt_cl_ok(broker=env.get("IP_TEST"), port=int(env.get("MQTT_PORT", 1883)), user=env.get("MQTT_USER"), pwd=env.get("MQTT_PASSWORD"))

        global GLOBAL_CACHED_MAPP
        if GLOBAL_CACHED_MAPP is None:
            up_cache(self.dbm)
        self.mapp = copy.deepcopy(GLOBAL_CACHED_MAPP) if GLOBAL_CACHED_MAPP else {}
        self.scene = copy.deepcopy(GLOBAL_CACHED_SCENE) if GLOBAL_CACHED_SCENE else {}
        self.schedule = copy.deepcopy(GLOBAL_CACHED_SCHEDULE) if GLOBAL_CACHED_SCHEDULE else []
        self.action = copy.deepcopy(GLOBAL_CACHED_ACTIONS) if GLOBAL_CACHED_ACTIONS else []
        self.table = copy.deepcopy(GLOBAL_CACHED_TABLE) if GLOBAL_CACHED_TABLE else []
        self.calendario = copy.deepcopy(GLOBAL_CACHED_CALENDAR) if GLOBAL_CACHED_CALENDAR else []
        self.logs = copy.deepcopy(GLOBAL_CACHED_LOG) if GLOBAL_CACHED_LOG else []

    def refresh_schedule_cache(self):
        """Forza l'aggiornamento della cache globale e ri-allinea i dati dell'app."""
        try:
            up_cache(self.dbm)
            self.schedule = copy.deepcopy(GLOBAL_CACHED_SCHEDULE) if GLOBAL_CACHED_SCHEDULE else []
            self.action = copy.deepcopy(GLOBAL_CACHED_ACTIONS) if GLOBAL_CACHED_ACTIONS else []
            self.page.pubsub.send_all({"type": "schedule_updated"})
            payload = '{"state": "ON"}' if self.up_sched else '{"state": "OFF"}'
            self.mqtt.publish_message("HomeZig/System/up_sched", payload)
        except Exception as e:
            log.error(f"Errore aggiornamento cache schedule: {e}")

    def ref_logs_cache(self):
        """Forza l'aggiornamento della cache globale dei log e ri-allinea i dati dell'app."""
        try:
            session_id = getattr(getattr(self.page, "session", None), "id", "N/A")
            up_cache_log(self.dbm)
            self.logs = copy.deepcopy(GLOBAL_CACHED_LOG) if GLOBAL_CACHED_LOG else []

            def has_alive_ui_session():
                """Verifica che la sessione pagina sia ancora attiva e abbia un loop valido."""
                try:
                    if not self.page:
                        return False
                    session = getattr(self.page, "session", None)
                    if not session:
                        return False
                    connection = getattr(session, "connection", None)
                    if not connection:
                        return False
                    loop = getattr(connection, "loop", None)
                    return loop is not None
                except Exception:
                    return False

            def run_on_ui_thread(callback):
                """Esegue callback sul thread UI quando possibile."""
                try:
                    if threading.current_thread() is threading.main_thread():
                        callback()
                        return True
                    if not has_alive_ui_session():
                        return False

                    session = getattr(self.page, "session", None)
                    connection = getattr(session, "connection", None) if session else None
                    loop = getattr(connection, "loop", None) if connection else None

                    if self.page and hasattr(self.page, "call_from_thread"):
                        self.page.call_from_thread(callback)
                        return True
                    if self.page and hasattr(self.page, "invoke_later"):
                        self.page.invoke_later(callback)
                        return True
                    if loop and hasattr(loop, "call_soon_threadsafe"):
                        loop.call_soon_threadsafe(callback)
                        return True
                except Exception as ex:
                    log.warning(f"Dispatch su thread UI fallito: {ex}")
                return False

            try:
                current_module = None
                if hasattr(self, "PAGE_MODULES"):
                    current_module = self.PAGE_MODULES.get(self.current_page_index)
                is_log_page = bool(current_module and getattr(current_module, "__name__", "").endswith("log_page"))
                direct_refresh = getattr(self, "log_page_refresh", None)
                if is_log_page and callable(direct_refresh):
                    if run_on_ui_thread(direct_refresh):
                        log.debug(f"📋 [session:{session_id}] LogPage aggiornata con refresh diretto")
                    else:
                        log.warning(f"[session:{session_id}] Refresh diretto LogPage non eseguito: dispatcher UI non disponibile")
            except Exception as ex:
                log.warning(f"[session:{session_id}] Refresh diretto LogPage fallito: {ex}")

            if self.page and hasattr(self.page, "pubsub") and has_alive_ui_session():
                def notify_logs_updated():
                    self.page.pubsub.send_all({"type": "logs_updated"})

                if run_on_ui_thread(notify_logs_updated):
                    log.debug(f"📋 [session:{session_id}] Cache log aggiornata e notificata a tutte le pagine")
                else:
                    log.warning(f"[session:{session_id}] Notifica logs_updated non inviata: impossibile dispatch su loop UI")
            else:
                log.debug(f"[session:{session_id}] Skip notifica logs_updated: sessione UI non attiva")
        except Exception as e:
            log.error(f"Errore aggiornamento cache log: {e}")

    def refresh_meteo(self):
        try:
            if self.meteo and hasattr(self.meteo, 'Get_WeatherF_api'):
                self.meteo.Get_WeatherF_api()
                if self.page and hasattr(self.page, "pubsub"):
                    try:
                        log.debug("🌤️ Meteo Cache aggiornata")
                        self.page.pubsub.send_all({"type": "meteo_updated"})                        #   👀  Notifica a tutte le pagine
                    except Exception as e:
                        log.warning(f"Notifica pubsub refresh_meteo fallita: {e}")
        except Exception as e:
            log.error(f"Errore aggiornamento meteo: {e}")

    def up_calendar(self):
        global GLOBAL_CACHED_CALENDAR
        try:
            if self.cal and hasattr(self.cal, 'leggi_calendario'):
                GLOBAL_CACHED_CALENDAR = self.cal.leggi_calendario()
                log.debug("📅 Cache calendario aggiornata")
        except Exception as e:
            log.error(f"Errore aggiornamento cache calendario: {e}")

    # --- HANDLER EVENTI PAGINA GLOBALI --- 
    def reset_inactivity_timer(self):
        """Resettare o avviare il timer di inattività. Se il timer esiste già, viene cancellato e ricreato."""
        try:
            if hasattr(self, '_inactivity_timer') and self._inactivity_timer:
                self._inactivity_timer.cancel()
            self._inactivity_timer = threading.Timer(300, self.return_to_home)
            self._inactivity_timer.name = "Timer_home"
            self._inactivity_timer.daemon = True
            self._inactivity_timer.start()
        except Exception as e:
            log.error(f"Errore nel reset del timer di inattività: {e}")

    def return_to_home(self):
        try:
            if self.current_page_index != 0:
                self.current_page_index = 0
                self.is_logged_in = False
                if hasattr(self, "nav_rail"):
                    # Trova indice visuale della Home (ID=0)
                    if 0 in self.visible_pages_map:
                        self.nav_rail.selected_index = self.visible_pages_map.index(0)
                        self.content_container.content = self.get_page_content(0)
                        
                        # Aggiorna anche nav_rail ed eventuale drawer per riflettere il cambio
                        self.nav_rail.update()
                        if hasattr(self.page, "drawer") and self.page.drawer:
                            self.page.drawer.selected_index = self.nav_rail.selected_index
                            self.page.drawer.update()
                            
                        self.page.update()
                        self.show_info_snackbar("🔒 Logout per inattività. Ritorno alla Home.")
                        log.info("🔙 Timeout inattività: ritorno alla pagina Home e logout")
                    else:
                        log.warning("Impossibile tornare alla Home: pagina non visibile")
            else:
                # Se sono già in Home, chiudi il contenitore dei grafici
                if self.page.overlay:
                    for control in list(self.page.overlay):
                        if hasattr(control, "open"):
                            control.open = False
                    self.page.update()
                    self.page.overlay.clear()
                    log.debug("📉 Chiusura contenitore grafici in Home per inattività")
        except Exception as e:
            log.error(f"Errore ritorno Home per inattività: {e}")

    def on_session_open(self):
        global active_sessions
        active_sessions += 1
        log.info(f"Sessione Flet aperta. Sessioni attive: {active_sessions}")

    def on_session_close(self):
        global active_sessions
        if active_sessions > 0:
            active_sessions -= 1
        log.info(f"Sessione Flet chiusa. Sessioni attive: {active_sessions}")

    def on_resize(self, e):
        page_w = self.page.window.width if getattr(self.page, "window", None) and self.page.window.width else self.page.width
        log.debug(f"Evento on_resize: larghezza={page_w}")
        
        if hasattr(self, "nav_rail") and self.nav_rail:
            if page_w and page_w < 600:
                if self.nav_rail.visible is not False:
                    self.nav_rail.visible = False
                    self.nav_rail.update()
                if hasattr(self, "appbar") and self.appbar.visible is not True:
                    self.appbar.visible = True
                    self.appbar.update()
            else:
                if self.nav_rail.visible is not True:
                    self.nav_rail.visible = True
                    self.nav_rail.update()
                if hasattr(self, "appbar") and self.appbar.visible is not False:
                    self.appbar.visible = False
                    self.appbar.update()

    def on_scroll(self, e):
    #    self.reset_inactivity_timer()
        log.debug(f"Evento on_scroll: {e}")

    def on_change(self, e):
        log.info(f"Evento on_change: {e}")

    def get_secondary_color(self):
        try:
            return self.page.theme.color_scheme.secondary
        except Exception:
            return ft.Colors.SECONDARY

    def get_snackbar_duration(self):
        """Restituisce la durata standard per i snackbar in millisecondi. Puoi personalizzare questo valore o renderlo dinamico in base al tipo di messaggio."""
        return 5000  # ms
    
    def get_page_content(self, index):
        """Questa funzione permette alla home_page di ricaricarsi da sola"""
        from pages import home_page
        return home_page.get_content(self, "Dashboard")
    
    def change_theme(self, e):
        """Cambia il tema dell'applicazione in runtime"""
        try:
            theme_value = e.control.value
            log.debug(f"🎨 Cambio tema: {theme_value}")       
            theme_map = {
                "SYSTEM": ft.ThemeMode.SYSTEM,
                "LIGHT": ft.ThemeMode.LIGHT,
                "DARK": ft.ThemeMode.DARK
            }
            
            new_theme = theme_map.get(theme_value, ft.ThemeMode.SYSTEM)
            self.page.theme_mode = new_theme
            self.page.update()
            
            theme_names = {"SYSTEM": "Sistema", "LIGHT": "Chiaro", "DARK": "Scuro"}
            self.show_info_snackbar(f"✅ Tema cambiato: {theme_names.get(theme_value, theme_value)}")
            log.debug(f"✅ Tema applicato: {theme_value}")
        except Exception as e:
            log.error(f"❌ Errore cambio tema: {e}", exc_info=True)

    def change_colors(self, colors_dict):
        """Cambia i colori principale e secondario dell'app in runtime, ricevendo un dict con i valori."""
        try:
            primary_color_name = colors_dict.get("primary_color", "BLUE")
            secondary_color_name = colors_dict.get("secondary_color", "AMBER")

            log.debug(f"🎨 Cambio colori: primario={primary_color_name}, secondario={secondary_color_name}")

            primary_color = COLOR_MAP.get(primary_color_name, ft.Colors.BLUE)
            secondary_color = COLOR_MAP.get(secondary_color_name, ft.Colors.AMBER)

            self.page.theme = ft.Theme(
                use_material3=True,
                color_scheme_seed=primary_color
            )
            self.page.dark_theme = ft.Theme(
                use_material3=True,
                color_scheme_seed=primary_color
            )

            self.page.update()

            color_names_it = {
                "RED": "Rosso", "PINK": "Rosa", "PURPLE": "Viola", "DEEP_PURPLE": "Viola Scuro",
                "INDIGO": "Indaco", "BLUE": "Blu", "LIGHT_BLUE": "Azzurro", "CYAN": "Ciano",
                "TEAL": "Verde Acqua", "GREEN": "Verde", "LIGHT_GREEN": "Verde Chiaro", "LIME": "Lime",
                "YELLOW": "Giallo", "AMBER": "Ambra", "ORANGE": "Arancione", "DEEP_ORANGE": "Arancione Scuro",
                "BROWN": "Marrone", "GREY": "Grigio", "BLUE_GREY": "Grigio Blu"
            }

            self.show_info_snackbar(
                f"✅ Colori aggiornati! "
                f"Primario: {color_names_it.get(primary_color_name, primary_color_name)} "
                f"Secondario: {color_names_it.get(secondary_color_name, secondary_color_name)}"
            )

            log.debug(f"✅ Colori applicati: primario={primary_color_name}, secondario={secondary_color_name}")
        except Exception as e:
            log.error(f"❌ Errore cambio colore: {e}", exc_info=True)

    def toggle_debug(self, e):
        """Aggiorna la variabile globale debug quando lo switch cambia"""
        try:
            global debug
            debug = e.control.value
            con_hd = None
            for handler in logging.getLogger().handlers:
                if isinstance(handler, logging.StreamHandler) and not isinstance(handler, TimedRotatingFileHandler):
                    con_hd = handler
                    break
            if con_hd:
                if debug:
                    con_hd.setLevel(logging.DEBUG)
                    log.debug("🐛 Debug mode ATTIVATO")
                else:
                    con_hd.setLevel(logging.INFO)
                    log.debug("🐛 Debug mode DISATTIVATO")
            
            status = "attivato ✅" if debug else "disattivato ❌"
            self.show_info_snackbar(f"🐛 Debug mode {status}")
        except Exception as ex:
            log.error(f"❌ Errore toggle debug: {ex}", exc_info=True)
            
    def Set_settings(self):
        """Applica le impostazioni già caricate in self.settings"""
        try:
            settings = self.settings
            # Applica tema
            if "theme" in settings:
                theme_map = {
                    "SYSTEM": ft.ThemeMode.SYSTEM,
                    "LIGHT": ft.ThemeMode.LIGHT,
                    "DARK": ft.ThemeMode.DARK
                }
                theme_mode = theme_map.get(settings["theme"], ft.ThemeMode.SYSTEM)
                self.page.theme_mode = theme_mode
                log.debug(f"🎨 Tema caricato: {settings['theme']}")
            # Applica configurazione pagine
            if "pages_config" in settings:
                self.pages_config = settings["pages_config"]
                self.PAGE_NAMES = {}
                self.PAGE_MODULES = {}
                for page_conf in self.pages_config:
                    p_id = page_conf["id"]
                    p_name = page_conf["name"]
                    p_module_name = page_conf.get("module")
                    self.PAGE_NAMES[p_id] = p_name
                    if p_module_name:
                        module_obj = globals().get(p_module_name)
                        if module_obj:
                            self.PAGE_MODULES[p_id] = module_obj
                        else:
                            log.error(f"❌ Modulo '{p_module_name}' non trovato nei globals per pagina {p_name}")
                    else:
                        log.warning(f"⚠️ Nessun modulo specificato per pagina {p_name}")
                log.debug(f"📄 Configurazione pagine caricata ({len(self.pages_config)} pagine)")
            else:
                self.pages_config = [] # Fallback
            # Applica colori principale e secondario
            if "primary_color" in settings or "secondary_color" in settings:
                primary_color = COLOR_MAP.get(settings.get("primary_color", "BLUE"), ft.Colors.BLUE)
                secondary_color = COLOR_MAP.get(settings.get("secondary_color", "AMBER"), ft.Colors.AMBER)
                self.page.theme = ft.Theme(
                    use_material3=True,
                    color_scheme_seed=primary_color
                )
                self.page.dark_theme = ft.Theme(
                    use_material3=True,
                    color_scheme_seed=primary_color
                )
                log.debug(f"🎨 Colori caricati: primario={settings.get('primary_color')}, secondario={settings.get('secondary_color')}")
            # Applica debug mode (se necessario salvare globalmente)
            if "debug" in settings:
                global debug
                debug = settings["debug"]
                log.info(f"🐛 Debug mode: {debug}")
            if "mqtt_ip" in settings:
                log.debug(f"📡 MQTT IP: {settings['mqtt_ip']}")
            if "mqtt_port" in settings:
                log.debug(f"📡 MQTT Port: {settings['mqtt_port']}")
            log.debug("✅ Impostazioni applicate con successo")
        except Exception as e:
            log.warning(f"⚠️ Errore applicazione impostazioni: {e}")

    def save_settings(self, settings: dict):
        """Salva impostazioni in file JSON. Ora riceve un dict con i valori da salvare."""
        try:
            # Aggiungi timestamp di aggiornamento
            settings["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            settings_file = dat_path / "settings.json"
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            self.show_info_snackbar("✅ Impostazioni salvate con successo")
            self.mqtt.publish_message("HomeZig/System/key_sql", json.dumps(settings.get("key_sql", self.key_sql)))
            self.mqtt.publish_message("HomeZig/System/key_act", json.dumps(settings.get("key_act", self.key_act)))
            self.mqtt.publish_message("HomeZig/System/key_rooms", json.dumps(settings.get("key_rooms", self.key_rooms)))
            self.mqtt.publish_message("HomeZig/System/key_floor", json.dumps(settings.get("key_floor", self.key_floor)))
        except Exception as ex:
            log.error(f"❌ Errore salvataggio impostazioni: {ex}", exc_info=True)
            self.show_error_snackbar(f"❌ Errore salvataggio impostazioni: {str(ex)}")
    
    def show_info_snackbar(self, message):
        """Aggiungi al log recente"""
        timestamp = time.time()
        time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
        threading.Thread(
            target=dbm.UP_TAB_LOG, 
            kwargs={"time": timestamp, "log_t": "INFO", "room": "", "floor": "", "msg": message}, 
            daemon=True
        ).start()                                                                                               # ℹ️ Lancia UP_TAB_LOG in un thread separato per non bloccare la UI
        try:
            if hasattr(self.page, "pubsub"):
                self.page.pubsub.send_all({"type": "logs_updated"})
        except Exception as e:
            log.warning(f"Errore notifica aggiornamento log: {e}")
        snack = ft.SnackBar(
            content=ft.Text(message, expand=True, color='primary_contrast'),
            bgcolor=self.get_secondary_color(),
            duration=self.get_snackbar_duration()
        )
        self.page.overlay.append(snack)
        snack.open = True
    #    self.ref_logs_cache()
        self.page.update()
    
    def show_warn_snackbar(self, floor, room, message):
        """Aggiungi al log recente"""
        timestamp = time.time()
        time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
        threading.Thread(
            target=dbm.UP_TAB_LOG, 
            kwargs={"time": timestamp, "log_t": "WARN", "room": room, "floor": floor, "msg": message}, 
            daemon=True
        ).start()                                                                                               # ℹ️ Lancia UP_TAB_LOG in un thread separato per non bloccare la UI
        try:
            if hasattr(self.page, "pubsub"):
                self.page.pubsub.send_all({"type": "logs_updated"})
        except Exception as e:
            log.warning(f"Errore notifica aggiornamento log: {e}")        
        snack = ft.SnackBar(
            content=ft.Text(message, expand=True, color='primary_contrast'),
            bgcolor=ft.Colors.ORANGE_700,
            duration=self.get_snackbar_duration()
        )
        self.page.overlay.append(snack)
        snack.open = True
    #    self.ref_logs_cache()
        self.page.update()

    def show_error_snackbar(self, message):
        """Aggiungi al log recente"""
        timestamp = time.time()
        time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
        threading.Thread(
            target=dbm.UP_TAB_LOG, 
            kwargs={"time": timestamp, "log_t": "ERROR", "room": "", "floor": "", "msg": message}, 
            daemon=True
        ).start()                                                                                                   # ℹ️ Lancia UP_TAB_LOG in un thread separato per non bloccare la UI
        try:
            if hasattr(self.page, "pubsub"):
                self.page.pubsub.send_all({"type": "logs_updated"})
        except Exception as e:
            log.warning(f"Errore notifica aggiornamento log: {e}")
        snack = ft.SnackBar(
            content=ft.Text(message, expand=True, color='primary_contrast'),
            bgcolor='error',
            duration=self.get_snackbar_duration()
        )
        self.page.overlay.append(snack)
        snack.open = True
    #    self.ref_logs_cache()
        self.page.update()
    
    def get_weather_icon(self, condition: str):
        """Restituisce l'icona appropriata per la condizione meteo"""
        try:
            condition_lower = condition.lower()
            if "sole" in condition_lower or "sereno" in condition_lower or "clear" in condition_lower or "sunny" in condition_lower:
                return ft.Icons.WB_SUNNY
            elif "nuvo" in condition_lower or "cloud" in condition_lower or "overcast" in condition_lower:
                return ft.Icons.CLOUD
            elif "pioggia" in condition_lower or "rain" in condition_lower:
                return ft.Icons.UMBRELLA
            elif "neve" in condition_lower or "snow" in condition_lower:
                return ft.Icons.AC_UNIT
            elif "tempesta" in condition_lower or "thunder" in condition_lower or "storm" in condition_lower:
                return ft.Icons.THUNDERSTORM
            else:
                return ft.Icons.WB_CLOUDY
        except Exception as e:
            log.error(f"Errore determinazione icona meteo: {e}")
            return ft.Icons.WB_CLOUDY
    
    def create_forecast_cards(self, forecast_days:list):
        """Crea una lista di MeteoCard per i prossimi giorni, formattando le date e traducendo i giorni della settimana in italiano."""
        cards = []
        weekdays_it = {
            "Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì",
            "Thursday": "Giovedì", "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"
        }
        
        for day_data in forecast_days[:6]:
            try:
                date_str = day_data.get("date", "")
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                weekday_en = date_obj.strftime("%A")
                weekday_it = weekdays_it.get(weekday_en, weekday_en)
                formatted_date = date_obj.strftime("%d/%m/%Y")
                
                card = MeteoCard(day_data, weekday_it, formatted_date)
                cards.append(card)  
            except Exception as e:
                log.error(f"Errore creazione card forecast: {e}")
                continue
        return cards

    def _normalize_mapp_payload(self, payload):
        """Rende coerenti le chiavi runtime MQTT con lo snapshot iniziale del DB."""
        if not isinstance(payload, dict):
            return {}

        normalized = dict(payload)

        for key, value in payload.items():
            if isinstance(key, str):
                # Manteniamo entrambe le varianti per compatibilita' con UI e DB.
                normalized[key.lower()] = value
                normalized[key.upper()] = value

        time_msg = normalized.get("time_msg", normalized.get("TIME_MSG"))
        if time_msg is not None:
            normalized["TIME_MSG"] = time_msg

        timestamp_a = normalized.get("timestamp_a", normalized.get("TIMESTAMP_A"))
        if timestamp_a is not None:
            normalized["TIMESTAMP_A"] = timestamp_a

        timestamp_b = normalized.get("timestamp_b", normalized.get("TIMESTAMP_B"))
        if timestamp_b is not None:
            normalized["TIMESTAMP_B"] = timestamp_b

        day_u = normalized.get("day_u", normalized.get("DAY_U"))
        time_u = normalized.get("time_u", normalized.get("TIME_U"))

        if (day_u is None or time_u is None) and time_msg is not None:
            try:
                dt_msg = datetime.fromtimestamp(float(time_msg))
                day_u = day_u or dt_msg.strftime("%Y-%m-%d")
                time_u = time_u or dt_msg.strftime("%H:%M:%S")
            except (TypeError, ValueError, OverflowError):
                pass

        normalized["day_u"] = day_u
        normalized["time_u"] = time_u
        if day_u is not None:
            normalized["DAY_U"] = day_u
        if time_u is not None:
            normalized["TIME_U"] = time_u

        return normalized

    def ck_cmd(self):
        """Controlla se ci sono nuovi messaggi MQTT da elaborare e aggiorna i dati dei dispositivi di conseguenza."""
        try:
            global msg_queue
            if not msg_queue.empty():     
                topic, data = msg_queue.get()
                idx, name, type = self.mqtt.Decode_Topic(topic)

                log.debug(f"📡 MQTT '{topic}', '{data.get('time_msg')}'")

                f_name = f"{type}/{name}"
                device_found = False
                for devices in self.mapp.values():
                    for dev in devices:
                        if dev.get('FRIENDLY_NAME') == f_name:
                            if 'data' not in dev:
                                dev['data'] = {}
                            if isinstance(data, dict):
                                normalized_data = self._normalize_mapp_payload(data)
                                prev_data = dict(dev['data'])
                                dev['data'].update(normalized_data)
                                device_found = dev['data'] != prev_data
                            break
                    if device_found:
                        break

                if device_found:
                    self.page.pubsub.send_all({"type": "mapp_updated", "topic": topic, "data": self.mapp})
        except Exception as msg:
            if "destroyed session" in str(msg):
                log.info("Sessione flet chiusa, interrompo il task MQTT per questa sessione.")
                import schedule
                return schedule.CancelJob
            log.error(f"Errore elaborazione messaggio MQTT: {msg}")
            
def main(page: ft.Page):
    """Funzione principale per inizializzare l'applicazione Flet"""
    def load_settings():
        """Carica impostazioni dal file JSON"""
        try:
            default_pages = [
                {"id": 0, "name": "Home", "module": "home_page", "icon": "HOME", "selected_icon": "HOME_FILLED", "visible": True},
                {"id": 1, "name": "Meteo", "module": "meteo_page", "icon": "WB_SUNNY_OUTLINED", "selected_icon": "WB_SUNNY", "visible": True},
                {"id": 2, "name": "Mqtt", "module": "mqtt_page", "icon": "SETTINGS_OUTLINED", "selected_icon": "SETTINGS", "visible": True},
                {"id": 3, "name": "Chart", "module": "chart_page", "icon": "SHOW_CHART", "selected_icon": "SHOW_CHART", "visible": True},
                {"id": 4, "name": "DataBase", "module": "database_page", "icon": "DATA_OBJECT_SHARP", "selected_icon": "DATA_OBJECT_SHARP", "visible": True},
                {"id": 5, "name": "Settings", "module": "settings_page", "icon": "SETTINGS_OUTLINED", "selected_icon": "SETTINGS", "visible": True},
            ]
            default_settings = {
                "theme": "SYSTEM",
                "primary_color": "BLUE",
                "secondary_color": "AMBER",
                "debug": debug,
                "mqtt_ip": "192.168.178.2",
                "mqtt_port": 1883,
                "pages_config": default_pages
            }

            settings_file = dat_path / "settings.json"
            if settings_file.exists():
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                
                # Merge con default per chiavi mancanti
                updated = False
                for k, v in default_settings.items():
                    if k not in settings:
                        settings[k] = v
                        updated = True
                
                # Se abbiamo aggiunto chiavi, possiamo anche salvare il file aggiornato
                # ma per ora ci limitiamo a usarle in memoria
                log.debug(f"⚙️ Impostazioni caricate: {settings}")
                return settings
            else:
                log.debug("⚙️ Uso impostazioni di default")
                return default_settings
        except Exception as e:
            log.error(f"❌ Errore caricamento impostazioni: {e}", exc_info=True)
            return {}

    def show_drawer(e):
        """Mostra il drawer se definito, altrimenti mostra un messaggio di avviso"""
        try:
            drawer = page.drawer
            if hasattr(page, "open"):
                page.open(drawer)
            else:
                page.run_task(page.show_drawer)
        except Exception as ex:
            log.error(f"Errore apertura drawer: {ex}")
            app.show_warn_snackbar("⚠️ Drawer non disponibile in questa sessione")

    # --- LOGIN ICON BUTTON ---
    def on_login_click(e):
        """Mostra il dialog di login"""
        try:
            from pages import schedule_page
            def on_success():
                log.debug("Login effettuato!")
            schedule_page.show_login_dialog(page, on_success=on_success)
        except Exception as ex:
            log.error(f"Errore apertura login dialog: {ex}")

    try:    
        # Log informazioni client
        log.info(f"🌐 Nuova connessione client:")
        log.info(f"  └─ Platform: {page.platform}")
        log.info(f"  └─ User Agent: {page.client_user_agent if hasattr(page, 'client_user_agent') else 'N/A'}")
        log.info(f"  └─ Session ID: {page.session.id if hasattr(page.session, 'id') else page.session}")
        client_ip = page.client_ip if page.client_ip else "IP non rilevato"
        log.info(f"  └─ IP Client: {client_ip}")       
        # Parsing avanzato del User Agent
        if hasattr(page, 'client_user_agent') and page.client_user_agent:
            user_agent = page.client_user_agent
            
            # Rileva browser
            if "Chrome" in user_agent and "Edg" not in user_agent:
                browser = "Chrome"
            elif "Edg" in user_agent:
                browser = "Edge"
            elif "Firefox" in user_agent:
                browser = "Firefox"
            elif "Safari" in user_agent and "Chrome" not in user_agent:
                browser = "Safari"
            elif "Opera" in user_agent or "OPR" in user_agent:
                browser = "Opera"
            else:
                browser = "Unknown"
            
            # Rileva OS
            if "Windows" in user_agent:
                os_name = "Windows"
                if "Windows NT 10.0" in user_agent:
                    os_name = "Windows 10/11"
                elif "Windows NT 6.3" in user_agent:
                    os_name = "Windows 8.1"
                elif "Windows NT 6.2" in user_agent:
                    os_name = "Windows 8"
            elif "Macintosh" in user_agent or "Mac OS X" in user_agent:
                os_name = "macOS"
            elif "Linux" in user_agent and "Android" not in user_agent:
                os_name = "Linux"
            elif "Android" in user_agent:
                os_name = "Android"
            elif "iPhone" in user_agent or "iPad" in user_agent:
                os_name = "iOS"
            else:
                os_name = "Unknown"
            
            log.info(f"  └─ Browser: {browser}")
            log.info(f"  └─ OS: {os_name}")
            log.info(f"  └─ Full UA: {user_agent}")

        settings = load_settings()

        app = AppManager(page, sql=dbm, meteo=mt, calen=i_cal, sett=settings)                       # 1. Inizializza il manager
        content_area = ft.Container(expand=True)                                                    # 2. Crea il contenitore principale
        app.content_container = content_area                                                        # 3. COLLEGA IL CONTENITORE AL MANAGER 👈 FONDAMENTALE
        app.on_session_open()

        page.title = "Home Automation Dashboard"
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.padding = 0

        app.ck_cmd_job = schedule.every(0.05).seconds.do(lambda: app.ck_cmd())

        def on_disconnect(e):
            if hasattr(app, "ck_cmd_job"):
                try:
                    schedule.cancel_job(app.ck_cmd_job)
                except Exception as e:
                    log.error(f"Errore cancellazione job MQTT: {e}")
            app.on_session_close()
        page.on_disconnect = on_disconnect

        if not hasattr(main, "_scheduler_started"):                                                 #   👀  Start schedule
            schedule.every(5).minutes.do(lambda: up_cache(dbm))
            schedule.every(10).minutes.do(lambda: utils.log_all_threads_stacks())
            
            def up_meteo():
                mt.Get_WeatherF_api()
                try:
                    if page and hasattr(page, "pubsub"):
                        page.pubsub.send_all({"type": "meteo_updated"})
                except Exception as e:
                    if "destroyed session" not in str(e):
                        log.error(f"Errore notifica meteo_updated: {e}")

            def up_enel():
                global GLOBAL_CACHED_ENEL
                loc_enel = app.dbm.GET_ENEL("CONS_01", datetime.now().date().strftime("%Y-%m-%d"))
                loc_enel = loc_enel[0] if loc_enel else {}
                if loc_enel:
                    GLOBAL_CACHED_ENEL = loc_enel
                try:
                    if page and hasattr(page, "pubsub"):
                        page.pubsub.send_all({"type": "enel_updated", "data": loc_enel})
                except Exception as e:
                    if "destroyed session" not in str(e):
                        log.error(f"Errore notifica enel_updated: {e}")

            schedule.every(5).minutes.do(up_enel)
            schedule.every(20).minutes.do(up_meteo)
            schedule.every(1).hours.do(lambda: app.up_calendar())

            # Nota: update_meteo_scheduled è locale alla sessione, non va schedulato globalmente qui duplicato
            def run_scheduler():
                try:
                    while True:
                        schedule.run_pending()
                        time.sleep(0.05)
                except Exception as e:
                    log.error(f"Errore nel thread scheduler: {e}", exc_info=True)
            
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True, name="Scheduler Main")
            scheduler_thread.start()
            main._scheduler_started = True

        if not getattr(mt, "last_data", None):                                                  #   ℹ️ Load meteo on first start without waiting for 20 mins
            threading.Thread(target=app.refresh_meteo, daemon=True, name="InitMeteoThread").start()

        # --- BUILDING NAV ITEMS FROM app.pages_config ---
        dynamic_nav_items = []
        visible_pages_map = []
        if hasattr(app, "pages_config"):
            for p_conf in app.pages_config:
                if p_conf.get("visible", True):
                    mod_obj = app.PAGE_MODULES.get(p_conf.get("id"))
                    if mod_obj and hasattr(mod_obj, "get_content"):
                        icon_name = p_conf.get("icon", "SETTINGS")
                        sel_icon_name = p_conf.get("selected_icon", icon_name)
                        
                        dynamic_nav_items.append({
                            "id": p_conf.get("id"),
                            "icon": getattr(ft.Icons, icon_name, ft.Icons.SETTINGS),
                            "selected_icon": getattr(ft.Icons, sel_icon_name, getattr(ft.Icons, icon_name, ft.Icons.SETTINGS)),
                            "label": p_conf.get("name", "Unknown"),
                            "function": mod_obj.get_content
                        })
                        visible_pages_map.append(p_conf.get("id"))
        
        if not dynamic_nav_items:
            dynamic_nav_items = [{"id": i, **n} for i, n in enumerate(nav_items)]
            visible_pages_map = [n["id"] for n in dynamic_nav_items]

        app.visible_pages_map = visible_pages_map

        def get_login_icon():
            """Restituisce l'icona corretta per il login/logout in base allo stato di login attuale"""
            try:
                return ft.Icons.VERIFIED_USER if getattr(app, "is_logged_in", False) else ft.Icons.PERSON
            except Exception as e:
                log.error(f"Errore ottenimento icona login: {e}")
                return ft.Icons.PERSON

        def build_nav_rail_destinations():
            """Costruisce dinamicamente le destinazioni per la nav_rail in base alla configurazione e allo stato di login"""
            try:
                nav_items = [
                    ft.NavigationRailDestination(
                        icon=item["icon"],
                        label=item["label"],
                        selected_icon=item.get("selected_icon", item["icon"])
                    )
                    for item in dynamic_nav_items
                ]
                nav_items.append(
                    ft.NavigationRailDestination(
                        icon=get_login_icon(),
                        label="Login",
                        selected_icon=ft.Icons.VERIFIED_USER if getattr(app, "is_logged_in", False) else ft.Icons.PERSON_OUTLINED
                    )
                )
                return nav_items
            except Exception as e:
                log.error(f"Errore costruzione nav_rail destinations: {e}")
                return []

        def update_nav_rail():
            """Aggiorna le destinazioni della nav_rail, utile dopo login/logout per aggiornare l'icona"""
            try:
                nav_rail.destinations = build_nav_rail_destinations()
                nav_rail.update()
            except Exception as e:
                log.error(f"Errore aggiornamento nav_rail: {e}")

        def nav_rail_on_change(e):
            """Gestisce il cambio di selezione nella nav_rail, intercettando il click su Login"""
            try:
                idx = e.control.selected_index
                if idx == len(nav_rail.destinations) - 1:
                    on_login_click(e)
                    # Resta sulla pagina corrente
                    e.control.selected_index = app.current_page_index if hasattr(app, "current_page_index") else 0
                    e.control.update()
                    update_nav_rail()
                else:
                    change_view(idx)
            except Exception as e:
                log.error(f"Errore gestione cambio nav_rail: {e}")

        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=50,
            min_extended_width=100,
            group_alignment=-0.9,
            selected_label_text_style=ft.TextStyle(color=ft.Colors.SECONDARY),
            unselected_label_text_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
            indicator_color=ft.Colors.SECONDARY_CONTAINER,
            destinations=build_nav_rail_destinations(),
            on_change=nav_rail_on_change,
        )
        app.nav_rail = nav_rail

        if not hasattr(app, "update_login_badge"):                                              #   ℹ️ Aggiorna la nav_rail quando cambia lo stato di login
            def update_login_badge():
                update_nav_rail()
            app.update_login_badge = update_login_badge

        # --- NAVIGATION DRAWER E APPBAR PER SCHERMI STRETTI ---
        page.drawer = ft.NavigationDrawer(
            on_change=lambda e: change_view(e.control.selected_index),
            controls=[
                ft.Container(height=12),
                *[
                    ft.NavigationDrawerDestination(
                        icon=item["icon"], 
                        label=item["label"],
                        selected_icon=item.get("selected_icon", item["icon"])
                    ) for item in dynamic_nav_items
                ]
            ]
        )

        appbar = ft.AppBar(
            leading=ft.IconButton(ft.Icons.MENU, on_click=show_drawer),
            title=ft.Text("Dashboard"),
            center_title=True,
            bgcolor="surfaceVariant",
            actions=[
                ft.IconButton(ft.Icons.PERSON, tooltip="Login", on_click=on_login_click)
            ],
            visible=False
        )
        page.appbar = appbar
        app.appbar = appbar

        content_area = ft.Container(expand=True, alignment=ft.Alignment.TOP_LEFT)
        app.content_container = content_area 

        main_layout = ft.Row(                                                                   #   ℹ️ Layout orizzontale: Rail a sinistra, Contenuto a destra
            [
                nav_rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        )

        gesture_wrapper = ft.GestureDetector(
        #    on_scroll=lambda e: app.reset_inactivity_timer(),
            on_tap_down=lambda e: app.reset_inactivity_timer(),
            content=main_layout,
            expand=True,
        )

        def change_view(index):
            """Funzione per cambiare la vista in base all'indice selezionato"""
            nav_rail.selected_index = index
            try:
                if page.drawer:
                    page.drawer.selected_index = index
                    try:
                        page.drawer.open = False
                    except Exception as e:
                        log.error(f"Errore chiusura drawer: {e}")

                app.current_page_index = dynamic_nav_items[index]["id"]
                selected_func = dynamic_nav_items[index]["function"]
                
                nuova_pagina = selected_func(app=app)
                content_area.content = nuova_pagina                                             #   ℹ️ Aggiunge il layout all'area e aggiorna
                
                nav_rail.update()
                if page.drawer:
                    page.drawer.update()
                
                page.update()
            except Exception as e:
                log.error(f"Errore cambio vista: {e}", exc_info=True)
                app.show_error_snackbar(f"❌ Errore cambio vista: {str(e)}")

        page.add(gesture_wrapper)                                                               #   ℹ️ Aggiungi l'UNICO main_content esistente, avvolto dal GestureDetector
        page.on_keyboard_event = lambda e: app.reset_inactivity_timer()                         #   ℹ️ Evento globale per i tasti della tastiera

        app.on_resize(None)                                                                     #   ℹ️ Eseguiamo on_resize manualmente all'avvio per impostare lo stato iniziale corretto
        
        change_view(0)                                                                          #   ℹ️ Mostra la prima pagina (Home) all'avvio 
        page.update()

        log.info("🚴 App started successfully.")
    except Exception as e:
        log.error(f"🆘 Errore in main: {e}", exc_info=True)

#   -----   👀  MAIN APP        👀  -----   #
if __name__ == "__main__":
    cur_path = Path(os.path.join(os.path.dirname(__file__)))
    Inf = inf(cur_path, debug=debug)
    log_path = Inf.check_folder(cur_path / "LOG")
    dat_path = Inf.check_folder(cur_path / "Data")
    temp_path = Inf.check_folder(cur_path / "Temp")
    font_path = Inf.check_folder(cur_path / "Fonts")
    img_path = Inf.check_folder(cur_path / "assets")

    # ℹ️ create formatter
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d: [%(levelname)-5s], %(module)-9s, %(funcName)-15s, %(lineno)4d: %(message)s', datefmt='%H:%M:%S')
    
    # ℹ️ create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    file_hd = TimedRotatingFileHandler(r'' + str(log_path) + '/LOG.log', when='midnight', backupCount=7, encoding = "UTF-8")
    file_hd.setLevel(logging.INFO)
    file_hd.setFormatter(formatter)
    root_logger.addHandler(file_hd)

    con_hd = logging.StreamHandler()
    if debug:
        con_hd.setLevel(logging.DEBUG)
    else:
        con_hd.setLevel(logging.INFO)
    con_hd.setFormatter(formatter)
    root_logger.addHandler(con_hd)

    log = logging.getLogger(__name__)
    logging.getLogger("schedule").setLevel(logging.WARNING)                     # 👈 Ignora log schedule
    logging.getLogger("httpx").setLevel(logging.WARNING)                        # 👈 Ignora log httpx
    logging.getLogger("uvicorn").setLevel(logging.WARNING)                      # 👈 Ignora log uvicorn
    logging.getLogger("watchfiles").setLevel(logging.WARNING)                   # 👈 Ignora log watchfiles
    logging.getLogger("flet").setLevel(logging.WARNING)                         # 👈 Ignora log flet
    logging.getLogger("flet_fastapi").setLevel(logging.WARNING)                 # 👈 Ignora log flet_fastapi
    logging.getLogger("flet_core").setLevel(logging.WARNING)                    # 👈 Ignora log flet_core
    logging.getLogger("flet_app").setLevel(logging.WARNING)                     # 👈 Ignora log flet app
    logging.getLogger("flet_app_manager").setLevel(logging.WARNING)             # 👈 Ignora log flet app manager
    logging.getLogger("flet_static_files").setLevel(logging.ERROR)              # 👈 Ignora log flet static files
    logging.getLogger("flet_runtime").setLevel(logging.WARNING)                 # 👈 Ignora log flet runtime
    logging.getLogger("alembic").setLevel(logging.WARNING)                      # 👈 Ignora log alembic
    logging.getLogger("alembic.runtime.migration").setLevel(logging.WARNING)    # 👈 Ignora log alembic runtime migration
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)            # 👈 Ignora log sqlalchemy engine

    log.info("🏎" * 40)
    log.info(f"Start Application '{__annotations__}'.")
    log.info("Author: " + __author__ + " - Version: " + __version__)
    log.info(f"Flet v: {ft.__version__}")
    IP = Inf.get_lan_ip()
    Inf.PC_Info()

    # -----     👀      RUN in DOCKER
    if inf.is_docker():
        log.info("🐳 Running inside DOCKER (Production Mode)")
        dbm = sqlm(t_time=2, debug=debug, user=env.get("DB_USER"), password=env.get("DB_PASSWORD"), host=env.get("DB_HOST"), database=env.get("DB_NAME"), port=int(env.get("DB_PORT")))
    else:
        log.info("💻 Running on LOCAL HOST (Test Mode)")
        dbm = sqlm(t_time=2, debug=debug, user=env.get("DB_USER"), password=env.get("DB_PASSWORD"), host=env.get("IP_TEST"), database=env.get("DB_NAME"), port=int(env.get("DB_PORT")))
    
    gps_lat = env.get("GPS_LAT")
    gps_lon = env.get("GPS_LON")
    gps_val = {'lat': gps_lat, 'lon': gps_lon}   
   
    i_cal = cal(env.get("I_CAL"))
    mt = pv(gps_val=gps_val, accu_key=env.get("KEY_OPEN"), debug=debug)

    log.info(f"🌐 Avvio app HTTP su http://{IP}:8550")
    #ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550, assets_dir="assets")
    ft.app(target=main)