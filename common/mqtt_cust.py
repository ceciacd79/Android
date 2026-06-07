# -*- coding: utf-8 -*-
#!/usr/bin/python

__author__ = "Cechich Diego"
__copyright__ = "Copyright 2025"
__version__ = "0.0.2"
__license__ = "GPL"

import inspect as ins
import os
import json
import logging
import time
from typing import Callable
import paho.mqtt.client as mqtt
import threading
import queue

log = logging.getLogger(__name__)

class MqttCust:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, app: object = None) -> 'MqttCust':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                # Inizializza solo la prima volta
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, app: object = None) -> None:
        # Salva sempre l'oggetto app, anche se già inizializzato
        self.app = app
        if getattr(self, '_initialized', False):
            return
        self.mqtt_client = None
        self.mqtt_connected = False
        self.mqtt_last_data = {}
        self._mqtt_message_handlers = []
        self._mqtt_status_handlers = []
        self._error_handlers = []
        self._msg_queue = queue.Queue()
        self._queue_thread = threading.Thread(target=self.__process_queue, name="MQTT_Queue", daemon=True)
        self._queue_thread.start()
        self.devices = {}
        self.groups = {}
        self.mapp = {}
        self.state = False
        self._initialized = True

    def __process_queue(self) -> None:
        while True:
            try:
                while True:
                    try:
                        client, userdata, msg = self._msg_queue.get_nowait()
                        self.__hd_mesg(client, userdata, msg)
                    except queue.Empty:
                        break
                time.sleep(0.01)
            except Exception as ex:
                self._notify_error("Errore nella gestione della coda MQTT", ex)

    def mqtt_cl_ok(
        self,
        on_connect: Callable | None = None,
        on_message: Callable | None = None,
        broker: str | None = None,
        port: int | None = None,
        user: str | None = None,
        pwd: str | None = None
    ) -> tuple[mqtt.Client | None, str | None]:
        broker = broker if broker is not None else os.getenv("MQTT_HOST", "localhost")
        port = int(port) if port is not None else int(os.getenv("MQTT_PORT", "1883"))
        user = user if user is not None else os.getenv("MQTT_USER", None)
        pwd = pwd if pwd is not None else os.getenv("MQTT_PASSWORD", None)

        if self.mqtt_client is None:
            log.info(f"Creo nuovo client MQTT per broker={broker}, port={port}, user={user}")
            self.mqtt_client = mqtt.Client()
            if user and pwd:
                log.debug(f"Set credenziali utente MQTT: {user}")
                self.mqtt_client.username_pw_set(user, pwd)

        client = self.mqtt_client
        client.on_connect = self.mqtt_on_connect
        client.on_message = self.mqtt_on_message
        client.on_disconnect = self.mqtt_on_disconnect
        client.on_subscribe = self.mqtt_on_subscribe
        client.on_unsubscribe = self.mqtt_on_unsubscribe
        client.on_publish = self.mqtt_on_publish
        log.debug("Callback MQTT registrate (connect, message, disconnect, subscribe, unsubscribe, publish)")

        if client.is_connected():
            log.info("Client già connesso")
            try:
                res = client.subscribe("HomeZig/#")
                log.debug(f"[MQTT] Subscribed to HomeZig/#, result={res}")
            except Exception as ex:
                log.error(f"Errore subscribe: {ex}")
            return client, None

        try:
            log.debug(f"Connessione al broker {broker}:{port}...")
            client.connect(broker, port, keepalive=60)
            client.loop_start()
            log.debug("[MQTT] loop_start() avviato")
            return client, None
        except Exception as ex:
            log.error(f"Connessione fallita: {ex}")
            return None, str(ex)

    def reconnect_mqtt(self) -> None:
        try:
            if self.mqtt_client and getattr(self.mqtt_client, 'is_connected', lambda: False)():
                return
            if self.mqtt_client:
                try:
                    self.mqtt_client.reconnect()
                    return
                except Exception:
                    pass
            self.mqtt_cl_ok()
        except Exception as ex:
            self._notify_error("Errore riconnessione MQTT", ex)

    def mqtt_on_connect(self, client: mqtt.Client, userdata: object, flags: dict, rc: int) -> None:
        try:
            log.debug(f"on_connect: rc={rc}, flags={flags}, userdata={userdata}")
            self.mqtt_connected = (rc == 0)
            if rc == 0:
                try:
                    res = client.subscribe("HomeZig/#")
                    log.debug(f"[MQTT] Subscribed to HomeZig/#, result={res}")
                    if res[0] == mqtt.MQTT_ERR_SUCCESS:
                        log.debug("✅ Subscribe riuscito.")          
                        self.publish_message("HomeZig/System/new_con", '{"new_con": true}')
                except Exception as ex:
                    log.error(f"Errore subscribe: {ex}")
            for h in list(self._mqtt_status_handlers):
                try:
                    h(self.mqtt_connected, rc)
                except Exception as ex:
                    log.error(f"Status handler error: {ex}")
        except Exception as ex:
            log.error(f"on_connect error: {ex}")

    def mqtt_on_disconnect(self, client: mqtt.Client, userdata: object, rc: int, properties: object = None) -> None:
        try:
            log.warning(f"[MQTT] Disconnesso dal broker, rc={rc}, userdata={userdata}, properties={properties}")
            # Dump stato client
            try:
                log.debug(f"Stato client: is_connected={getattr(client, 'is_connected', lambda: None)()}, socket={getattr(client, '_sock', None)}")
            except Exception as ex_dump:
                log.warning(f"Errore dump stato client: {ex_dump}")
            self.mqtt_connected = False
            for h in list(self._mqtt_status_handlers):
                try:
                    h(False, rc)
                except Exception as ex:
                    log.error(f"Status handler error: {ex}")
            # Riconnessione automatica avanzata
            max_attempts = 5
            for attempt in range(1, max_attempts+1):
                try:
                    log.info(f"Tentativo di riconnessione {attempt}/{max_attempts}...")
                    client.reconnect()
                    log.debug("Riconnessione riuscita!")
                    break
                except Exception as reconn_ex:
                    log.error(f"Errore riconnessione tentativo {attempt}: {reconn_ex}")
                    import time
                    time.sleep(2)
            else:
                log.error("Tutti i tentativi di riconnessione falliti.")
        except Exception as ex:
            log.error(f"on_disconnect error: {ex}")

    def mqtt_on_message(self, client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage) -> None:
        self._msg_queue.put((client, userdata, msg))

    def __hd_mesg(self, client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage) -> None:
        try:
            payload = msg.payload.decode("utf-8") if msg.payload else ""
            topic = msg.topic if msg.topic else ""
            rest = topic[len("HomeZig/"):]
            if not payload.strip():
                log.warning(f"Payload vuoto su topic '{topic}'")
                return
            try:
                data = json.loads(payload)
            except Exception as ex:
                log.error(f"Payload non valido su topic '{topic}'-'{payload}': {ex}")
                return

            # Aggiungi timestamp ricezione e filtra messaggi troppo frequenti
            if isinstance(data, dict):
                data['time_msg'] = time.time()
                last_data = self.mqtt_last_data.get(msg.topic)
                if last_data and isinstance(last_data, dict) and 'time_msg' in last_data:
                    if data['time_msg'] - last_data['time_msg'] < 0.5:
                        return

            if ( topic.startswith("HomeZig/") and "availability" in topic ):
                rest = rest.replace("availability", "").replace("/", "").strip()
                if rest in self.groups:
                    self.groups[rest] = {'state': data}
                return
            elif ( topic.startswith("HomeZig/") and "set" in topic ):
                return
            elif ( topic.startswith("HomeZig/") and "get" in topic ):
                return
            elif ( "get" in topic ):
                log.warning(f"Messaggio ignorato per topic contenente 'get': {topic}")
                return
            elif ( "set" in topic ):
                log.warning(f"Messaggio ignorato per topic contenente 'set': {topic}")
                return
            elif ( topic.startswith("HomeZig/") and "bridge" in topic ):
                if ("definitions" in topic ):
                    return
                elif ("event" in topic ):
                    return
                elif ("health" in topic ):
                    return
                elif ("state" in topic ):
                    log.debug(f"[MQTT] State mqtt ricevuto.")
                    self.state = data
                elif ("converters" in topic ):
                    return
                elif ("info" in topic ):
                    return
                elif ("devices" in topic ):
                    self.devices = data
                    log.debug(f"[MQTT] Devices mqtt ricevuti.")
                elif ("groups" in topic ):
                    log.debug(f"[MQTT] Groups mqtt ricevuti.")
                    self.groups = data
                elif ("extensions" in topic ):
                    return
                elif ("response" in topic ):
                    return 
                elif ("logging" in topic ):
                    return 
                else:
                    log.warning(f"ℹ️ Msg bridge non gestito ricevuto: topic={topic}.")
            elif ( topic.startswith("HomeZig/") and "availability" in topic ):
                pass
            elif ( topic.startswith("HomeZig/") and "state" == topic ):
                self.state = data
            elif ( topic.startswith("HomeZig/") and "write" in data ):
                return 
            else:
                pass

            self.mqtt_last_data[msg.topic] = data

            for h in list(self._mqtt_message_handlers):
                try:
                    h(msg.topic, data)
                except Exception as ex:
                    log.error(f"Message handler error: {ex}")
        except Exception as ex:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}. Topic '{topic}', Payload: '{payload}', Error: {ex}.")

    def mqtt_on_subscribe(
        self,
        client: mqtt.Client,
        userdata: object,
        mid: int,
        reason_codes: list[int],
        properties: object = None
    ) -> None:
        try:
            log.debug(f"Subscribed: mid={mid}, reasons={reason_codes}, properties={properties}")
        except Exception as ex:
            log.error(f"on_subscribe error: {ex}")

    def mqtt_on_unsubscribe(
        self,
        client: mqtt.Client,
        userdata: object,
        mid: int,
        properties: object = None,
        reason_codes: list[int] | None = None
    ) -> None:
        try:
            log.warning(f"Unsubscribed: mid={mid}, reasons={reason_codes}, properties={properties}")
        except Exception as ex:
            log.error(f"on_unsubscribe error: {ex}")

    def mqtt_on_publish(
        self,
        client: mqtt.Client,
        userdata: object,
        mid: int,
        reason_codes: list[int] | None = None,
        properties: object = None
    ) -> None:
        try:
            log.debug(f"Published: mid={mid}, reason_codes={reason_codes}, properties={properties}")
        except Exception as ex:
            log.error(f"on_publish error: {ex}")

    def mqtt_message_handler(self, handler: Callable[[str, dict], None]) -> None:
        if handler and handler not in self._mqtt_message_handlers:
            self._mqtt_message_handlers.append(handler)

    def remove_mqtt_message_handler(self, handler: Callable[[str, dict], None]) -> None:
        if handler in self._mqtt_message_handlers:
            self._mqtt_message_handlers.remove(handler)

    def mqtt_status_handler(self, handler: Callable[[bool, int | None], None]) -> None:
        if handler and handler not in self._mqtt_status_handlers:
            self._mqtt_status_handlers.append(handler)

    def remove_mqtt_status_handler(self, handler: Callable[[bool, int | None], None]) -> None:
        if handler in self._mqtt_status_handlers:
            self._mqtt_status_handlers.remove(handler)

    def error_handler(self, handler: Callable[[str, Exception], None]) -> None:
        if handler and handler not in self._error_handlers:
            self._error_handlers.append(handler)

    def remove_error_handler(self, handler: Callable[[str, Exception], None]) -> None:
        if handler in self._error_handlers:
            self._error_handlers.remove(handler)

    def _notify_error(self, message: str, ex: Exception = None) -> None:
        # Se c'è un'eccezione formatta il messaggio, altrimenti logga e invia solo il messaggio
        full_msg = f"{message}: {ex}" if ex else message
        log.error(full_msg)
        for h in list(self._error_handlers):
            try:
                h(message, ex)
            except Exception as e:
                log.error(f"Errore nell'esecuzione dell'error handler: {e}")

    def publish_message(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> bool:
        """Publish su un topic MQTT con log e gestione errori."""
        try:
            if self.mqtt_client and getattr(self.mqtt_client, 'is_connected', lambda: False)():
                res = self.mqtt_client.publish(topic, payload=payload, qos=qos, retain=retain)
                log.debug(f"[MQTT] Publish {topic}: {payload}, {res}")
                return True
            else:
                log.warning(f"[MQTT] Client non connesso, publish su {topic} non eseguito.")
                return False
        except Exception as ex:
            log.error(f"[MQTT] Errore publish su {topic}: {ex}")
            return False

    def Decode_Topic(self, topic: str) -> tuple[int, str, str]:
        try:
            parts = topic.split("/")
            # Caso Scene: HomeZig/Scene
            if len(parts) == 2:
                return 0, parts[1], "Scene"
            # Caso HomeZig/type/Nome_XX
            elif len(parts) >= 3:
                name = parts[2]
                type = parts[1]
                idx = int(name.split("_")[-1])
                return idx, name, type
            else:
                return 0, "Unknown", "Unknown"
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")
            return 0, "Unknown", "Unknown"

    def sort_Device(self, data: list[dict]) -> dict[int, list[dict]]:
        """
        Raggruppa una lista di dict per 'level'.
        Ogni chiave è un livello, il valore è una lista di dict ordinata per model_id e friendly_name.
        """
        from collections import defaultdict
        grouped = defaultdict(list)
        for v in data:
            if not isinstance(v, dict):
                continue
            level = v.get('level', 0)
            grouped[level].append(v)
        # Ordina ogni gruppo per model_id e friendly_name
        for level in grouped:
            grouped[level].sort(key=lambda item: (
                item.get('model_id', ''),
                item.get('friendly_name', '')
            ))
        return dict(sorted(grouped.items()))