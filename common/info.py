# -*- coding: utf-8 -*-
#!/usr/bin/python

__author__ = "Cechich Diego"
__copyright__ = "Copyright 2025"
__version__ = "0.0.2"
__license__ = "GPL"

#   -----   👀  MODULE          👀  -----   #
import inspect as ins
import logging
import os
import mysql.connector as mariadb
import psutil
import requests
import schedule
import socket
import sqlite3
import sys
import platform
import threading
import ipaddress

from datetime import date, datetime, time as dtime
from pathlib import Path

#   -----   👀  DEFINE          👀  -----   #

#   -----   👀  GLOBAL VARIABLE 👀  -----   #
log_path = ""
#   -----   👀  WORK CLASS      👀  -----   #
log = logging.getLogger(__name__)
class Info():
    def __init__(self, cur_path, debug=False):
        global log_path
        try:
            self.cur_path = cur_path
            self.log_path = cur_path / "LOG"
            self.dat_path = cur_path / "Data" 
            self.img_path = cur_path / "ImgCam"
            log_path = self.log_path
            self.nic = []
            self.user = ""

            if debug:
                schedule.every(5).seconds.do(self.CPU_Usage)
        except Exception as msg:
            log.error("🆘 Python {}:{}." .format(ins.currentframe().f_code.co_name, msg))
        
    def get_ip_address(self):
        """
        Restituisce l'indirizzo IP locale della macchina.
        """
        ip_address = '0.0.0.0'
        if self.check_internet():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    ip_address = s.getsockname()[0]
            except Exception as e:
                log.error(f"Errore ottenendo l'IP locale: {e}")
        return ip_address

    def get_lan_ip(self):
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip = addr.address
                    if ip.startswith("192.168.178."):
                        return ip
        return "127.0.0.1"  # fallback

    def get_external_ip(self):
        """
        Get the external IP address of the machine.
        """
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text
        except Exception as e:
            log.error(f"Error getting external IP: {e}")
            return "Non disponibile"

    @staticmethod
    def is_docker():
        # Docker crea questo file automaticamente all'avvio del container
        return os.path.exists('/.dockerenv')

    def check_internet(self):
        """
        Check if internet connection is available
        """
        timeout = 3
        host = "8.8.8.8"         # google-public-dns-a.google.com
        port = 53
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as msg:
            log.error('Socket {}, {}' .format(ins.currentframe().f_code.co_name, msg))
            return False

    def get_app_base_path(self):
        if getattr(sys, 'frozen', False):
            return Path(os.path.dirname(sys.executable))
        else:
            return Path(os.path.dirname(os.path.abspath(__file__)))

    def check_folder(self, path):
        isExist = os.path.exists(str(path))
        if (not isExist):
            os.makedirs(path)
            log.debug(f"📂 Create folder '{path}'.")
        return path

    def PC_Info(self):
        class Nic():
            def __init__(self, name, up, mtu, speed, ip4 ="", ip6="", mac="", sub="", mask=""):
                self.name = name
                self.up = up
                self.mtu = mtu
                self.speed = speed
                self.ip4 = ip4
                self.ip6 = ip6
                self.mac = mac
                self.sub = sub
                self.mask = mask
        try:
            try:
                self.user = os.getlogin()
            except OSError:
                import getpass
                self.user = getpass.getuser()
            log.info("👔 Current user '{:<10}'." .format(self.user))
            log.info("💻 Logic CPU {:<2}, fisical core {:<2}, usable CPU {:<2}." .format(psutil.cpu_count(), psutil.cpu_count(logical=False), len(psutil.Process().cpu_affinity())))
            val = psutil.cpu_freq()
            log.info("💻 Current freq {:<4}, min {:<4}, max{:<4}." .format(val.current, val.min, val.max))
            val = psutil.virtual_memory()
            log.info("💻 Memory Total {:<5} Gb, Available {:<5} Gb, {:>5} %." .format(round(val.total/1024.0/1024.0/1024.0, 1), round(val.available/1024.0/1024.0/1024.0,1), val.percent))

            val = psutil.disk_partitions()
            for d in range(len(val)):
                try:
                    det = psutil.disk_usage(val[d].device)
                    log.info("💻 Partition {} type {}, total {} Gb, used {} Gb, free {} Gb, {:>5} %."
                        .format(val[d].device, val[d].fstype, round(det.total/1024.0/1024.0/1024.0, 1),
                                round(det.used/1024.0/1024.0/1024.0, 1), round(det.free/1024.0/1024.0/1024.0, 1), det.percent))
                except Exception as e:
                    log.warning(f"Impossibile accedere a {val[d].device}: {e}")

            p_nic = psutil.net_if_stats()
            val = psutil.net_if_addrs()
            for n in val:
                mac =""
                ip =""
                ip6 =""
                netm = ""
                for cn in range(len(val[n])):
                    if val[n][cn].family == socket.INADDR_BROADCAST:
                        mac = val[n][cn][1]
                    if val[n][cn].family == socket.AddressFamily.AF_INET:
                        ip = val[n][cn][1]
                        netm = val[n][cn][2]
                    if val[n][cn].family == socket.AddressFamily.AF_INET6:
                        ip6 = val[n][cn][1]
                nic = Nic(name=n, up=p_nic[n].isup, mtu=p_nic[n].mtu, speed=p_nic[n].speed, ip4=ip, ip6=ip6, mac=mac, sub=netm  )
                self.nic.append(nic)
            #    log.info("{:<38}, MAC {:<17}, IP4 {:<15}, IP6 {:<25} , SubNet {:<15}, isUp {:<4}." .format(nic.name, nic.mac, nic.ip4, nic.ip6, nic.sub, nic.up))
                log.info("{:<38}, MAC {:<17}, IP4 {:<15}, SubNet {:<15}, isUp {:<2}." .format(nic.name, nic.mac, nic.ip4, nic.sub, nic.up))

            val = psutil.sensors_battery()
            if val is None:
                log.info("🔌 Only power supplie.")
            else:
                log.info("🔋 Battery {} %, power plugged {}." .format(val[0], val[2]))
            val = psutil.boot_time()
            log.info("Boot Time {}." .format(datetime.fromtimestamp(val).strftime("%Y-%m-%d %H:%M:%S")))
        #    val = psutil.sensors_temperatures()
        #    val = psutil.sensors_fans()
        except Exception as msg:
            log.error("🆘 Python {}:{}." .format(ins.currentframe().f_code.co_name, msg))

    def CPU_Usage(self):
        try:
            msgl = ""
            percent = psutil.cpu_percent(interval=1, percpu=True)
            ram = psutil.virtual_memory().percent
            if psutil.cpu_count()>1:
                percent_g = psutil.cpu_percent(interval=1)
                log.debug("💻 CPU {:>5} %, Ram {:>5} %. Single CPU % {}." .format(percent_g, ram, percent))
            else:
                log.debug("💻 CPU {:>5} %, Ram {:>5} %." .format(percent_g, ram))
                msgl = f"CPU {percent_g:>5} %, Ram {ram:>5} %."
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")
        finally:
            return msgl   

    def list_network_interfaces(self):
        """
        Restituisce una lista di dizionari con nome, indirizzi IP e stato (UP/DOWN) delle schede di rete.
        """
        interfaces = []
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            for name, addr_list in addrs.items():
                ips = []
                for addr in addr_list:
                    if addr.family == socket.AF_INET:
                        ips.append(addr.address)
                is_up = stats[name].isup if name in stats else False
                interfaces.append({
                    "name": name,
                    "ipv4": ips,
                    "is_up": is_up
                })
        except Exception as e:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {e}.")
        return interfaces

    def monitor_network_interfaces(self, callback):
        """
        Monitora le schede di rete e chiama callback(event_type, device_name) su inserimento/rimozione.
        Su Linux usa pyudev, su Windows usa wmi.
        """
        system = platform.system().lower()
        if system == "linux":
            try:
                import pyudev
            except ImportError:
                log.error("pyudev non installato. Installa con: pip install pyudev")
                return

            def linux_monitor():
                context = pyudev.Context()
                monitor = pyudev.Monitor.from_netlink(context)
                monitor.filter_by(subsystem='net')
                for device in monitor:
                    if device.action == "add":
                        callback("added", device.sys_name)
                    elif device.action == "remove":
                        callback("removed", device.sys_name)

            threading.Thread(target=linux_monitor, daemon=True).start()

        elif system == "windows":
            def windows_monitor():
                import pythoncom
                pythoncom.CoInitialize()
                import wmi
                c = wmi.WMI()
                watcher = c.Win32_NetworkAdapter.watch_for()
                while True:
                    try:
                        event = watcher()
                        if event.NetConnectionStatus == 2:  # Connected
                            callback("added", event.Name)
                        elif event.NetConnectionStatus == 7:  # Disconnected
                            callback("removed", event.Name)
                    except wmi.x_wmi as e:
                        log.error(f"🆘 WMI Error: {e}")
            threading.Thread(target=windows_monitor, daemon=True).start()
        else:
            log.warning("Monitoraggio schede non supportato su questo sistema operativo.")

#   -----   👀  DATABASE       👀  -----   #
class SQliteDB():
    def __init__(self, path , db_name, sens, doors, t_time, debug=False):
        try:       
            self.db = f"{path[2]}/{db_name}"
            self.sens = sens
            self.doors = doors
            self.t_time = t_time
            self.conn = None         

            log.info("SQL3 version: " + str(sqlite3.sqlite_version))
        except Exception as msg:
            log.error("🆘 Python {}:{}." .format(ins.currentframe().f_code.co_name, msg))        

#   -----   👀  DATABASE       👀  -----   #
class MariaDB():
    def __init__(self, t_time=5, debug=False, user=None, password=None, host=None, database=None, port=None):
        self.conn_params = {
            "user": user,
            "password": password,
            "host": host,
            "database": database,
            "port": int(port)
        }
        self.t_time = t_time
        log.debug("📊 MariaDB module initialized.")

    def create_conn(self):
        """ Create a connection with DB. """
        try:
            self.conn = mariadb.connect(**self.conn_params)
        #    log.debug("📊 Connessione DB creata con successo")
            return self.conn
        except mariadb.Error as msg:
            log.error("SQL {}: {}." .format(ins.currentframe().f_code.co_name, msg))
            self.conn = None  # Assicurati che sia None in caso di errore
            return None
        except Exception as msg:
            log.error("🆘 Python {}:{}." .format(ins.currentframe().f_code.co_name, msg))
            self.conn = None
            return None

    def close_conn(self):
        """ Close a connection with DB. """
        try:
            if self.conn:
                self.conn.commit()
                self.conn.close()
        except mariadb.Error as msg:
            log.error("SQL {}: {}." .format(ins.currentframe().f_code.co_name, msg)) 

    def GET_DATAFRAME(self, name, data_query):
        """Restituisce i dati di una tabella per il giorno corrente e le colonne richieste. Thread-safe."""
        data = []
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            cur.execute("SHOW TABLES")
            tables = cur.fetchall()
            if (name,) not in tables:
                log.warning(f"📊 Tabella '{name}' non esistente nel database.")
                return data

            day = str(date.today())
            cols_str = ", ".join(f"{c}" for c in data_query)
            QUERY = f"SELECT {cols_str} FROM `{name}` WHERE DAY_U LIKE '{day}' ORDER BY ID_KEY"
            cur.execute(QUERY)
            data = cur.fetchall()
            cur.close()
        except mariadb.Error as e:
            log.error(f"🆘 Errore MariaDB: {e}")
        finally:
            if conn:
                conn.close()
        return data

    def GET_TABLE(self):
        """Restituisce la lista di tutte le tabelle nel database."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            cur.execute("SHOW TABLES")
            tables = cur.fetchall()
            table_names = [table[0] for table in tables]
            cur.close()
            return table_names
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
            return []
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return []
        finally:
            if conn:
                conn.close()

#   -----   👀  METEO          👀  -----   #

class Meteo():
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, debug=False, gps_val=None, accu_key=None):
        global log_path
        try:
            self.sun_s = None
            self.sun_r = None
            self.is_day = False
            self.lat = gps_val["lat"]
            self.lon = gps_val["lon"]
            self.api_key = accu_key
            self.api_type = 0
            self.last_data = None
            log.debug(f"☀️ Meteo module initialized with lat: {self.lat}, lon: {self.lon}.")
        #    self.Get_sun()
        #    self.Get_Open_Weather()
        #    self.Get_WeatherF_api()
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")

    def Get_sun(self):
        try:
            r = requests.get(f'https://api.sunrisesunset.io/json?lat={self.lat}&lng={self.lon}', timeout=5)
            if r.status_code == requests.codes.ok:
                data = r.json()
                if data.get("status") == "OK":
                    self.sun_r = data["results"]["sunrise"]
                    self.sun_s = data["results"]["sunset"]

                    self.sun_r = self.Conv_time(self.sun_r)
                    self.sun_s = self.Conv_time(self.sun_s)

                    self.is_day = self.CK_Day()
                    log.debug(f"🌅 Dati sole aggiornati: Alba {self.sun_r}, Tramonto {self.sun_s}")
                else:
                    log.error(f"❌ API sole error: {data}")
            else:
                log.error(f"❌ Errore HTTP API sole: {r.status_code}")
        except requests.exceptions.Timeout:
            log.error("⏰ Timeout nella richiesta API sole")
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")   

    def Get_Open_Weather(self):
        try:
            self.api_type = 0
            url = (
                f"https://api.openweathermap.org/data/3.0/onecall?lat={self.lat}&lon={self.lon}&exclude=alerts&appid={self.api_key}&units=metric&lang=it"
            )
          
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self.last_data = data
            self.print_fore(data)

        except requests.exceptions.Timeout:
            log.error("⏰ Timeout nella richiesta API AccuWeather")
            return None
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")   
            return None

    def Get_WeatherF_api(self):
        try:
            self.api_type = 1
            url = ('http://api.weatherapi.com/v1/forecast.json?key=fe722f6f3c844791996202852252610&q=gradisca d\'isonzo,IT&days=6&aqi=no&alerts=no&lang=it')
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self.last_data = data
            self.print_fore(data)
            return data
        except requests.exceptions.Timeout:
            log.error("⏰ Timeout Forecast API meteo")
            return None
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")   
            return None
    
    def Get_WeatherR_api(self):
        try:
            self.api_type = 1
            url = ('http://api.weatherapi.com/v1/current.json?key=fe722f6f3c844791996202852252610&q=gradisca d\'isonzo,IT&days=5&aqi=no&alerts=no&lang=it')
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self.last_data = data
            self.print_curr(data)
            return data
        except requests.exceptions.Timeout:
            log.error("⏰ Timeout Current API meteo")
            return None
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")   
            return None        

    def Conv_time(self, t):
        try:
            t = t.strip()
            fmts = ("%I:%M:%S %p", "%I:%M %p", "%H:%M:%S", "%H:%M")
            for f in fmts:
                try:
                    t = datetime.strptime(t , f).time()
                    return t.strftime("%H:%M")
                    break
                except Exception:
                    continue
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")   
            return "00:00:00"

    def CK_Day(self):
        try:
            if self.sun_r is None or self.sun_s is None:
                log.warning("🌅 Dati alba/tramonto non disponibili. Uso valore predefinito.")
                return True

            now = datetime.now()
            datetime_r = datetime.strptime(self.sun_r, '%H:%M')
            datetime_s = datetime.strptime(self.sun_s, '%H:%M')
            time_act = now.time()

            if (datetime_r.time() < time_act < datetime_s.time()):
                self.is_day = True
            else:
                self.is_day = False

            log.debug(f"ℹ Is day {self.is_day}. Alba: {self.sun_r}, Tramonto: {self.sun_s}")
            return self.is_day

        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return True

    def print_fore(self, data):
        try:
            if (self.api_type == 0):
                city = data.get("city", {})
                sunrise = city.get("sunrise")
                sunset = city.get("sunset")

                self.sun_r = self.Conv_time(sunrise)
                self.sun_s = self.Conv_time(sunset)

                if sunrise and sunset:
                    sunrise_str = datetime.datetime.fromtimestamp(sunrise).strftime("%H:%M:%S")
                    sunset_str = datetime.datetime.fromtimestamp(sunset).strftime("%H:%M:%S")
                for item in data.get("list", [])[:5]:  # Mostra solo le prime 5 previsioni
                    dt_txt = item.get("dt_txt", "")
                    main = item.get("main", {})
                    temp = main.get("temp", "?")
                    weather = item.get("weather", [{}])[0]
                    desc = weather.get("description", "")
                    icon = weather.get("icon", "")
            elif (self.api_type == 1):
                city = data.get("location", {})

                forecastday_list = data.get("forecast", {}).get("forecastday", [])
                if not forecastday_list:
                    log.warning("📊 Nessun dato forecastday disponibile nel JSON meteo.")
                    return

                sunrise = data.get("forecast", {}).get("forecastday", [])[0].get("astro", {}).get("sunrise")
                sunset = data.get("forecast", {}).get("forecastday", [])[0].get("astro", {}).get("sunset")

                self.sun_r = self.Conv_time(sunrise)
                self.sun_s = self.Conv_time(sunset)

                last_up = data.get("current", {}).get("last_updated", "")
                temp_c = data.get("current", {}).get("temp_c", "?")
                condition = data.get("current", {}).get("condition", {}).get("text", "")
                press_mb = data.get("current", {}).get("pressure_mb", "?")
                hum = data.get("current", {}).get("humidity", "?")
                cloud = data.get("current", {}).get("cloud", "?")

                log.debug(f"🌆 Weather for {city.get('name', '')}, {city.get('region', '')}, {city.get('country', '')}. Last update {last_up}.")
                for item in data.get("forecast", {}).get("forecastday", [])[:5]:
                    dt_txt = item.get("date", "")
                    day = item.get("day", {})
                    temp = day.get("avgtemp_c", "?")
                    temp_M = day.get("maxtemp_c", "?")
                    temp_m = day.get("mintemp_c", "?")
                    p_rain = day.get("daily_chance_of_rain", {})
                    desc = day.get("condition", {}).get("text", "")
                    sunr = item.get("astro", {}).get("sunrise")
                    suns = item.get("astro", {}).get("sunset")
                    monr = item.get("astro", {}).get("moonrise")
                    mons = item.get("astro", {}).get("moonset")
                    log.debug(f"📅 {dt_txt}: 🌡 {temp}°C, {desc}, Alba {sunr}, Tramonto {suns}")
        except Exception as e:
            log.error(f"🆘 Errore nel parsing dei dati meteo: {e}", exc_info=True)
    
    def print_curr(self, data):
        try:
            if ( self.api_type == 0):
                pass
            elif ( self.api_type == 1):
                city = data.get("location", {})
                last_up = data.get("current", {}).get("last_updated", "")
                temp_c = data.get("current", {}).get("temp_c", "?")
                condition = data.get("current", {}).get("condition", {}).get("text", "")
                press_mb = data.get("current", {}).get("pressure_mb", "?")
                hum = data.get("current", {}).get("humidity", "?")
                cloud = data.get("current", {}).get("cloud", "?")

                log.debug(f"🌆 Current Weather for {city.get('name', '')}, {city.get('region', '')}. Last update {last_up}.")
                log.debug(f"🌡 Temp:{temp_c}°C, Condition: {condition}, Pressure: {press_mb}mb, Humidity: {hum}%, Cloud: {cloud}%.")
        except Exception as e:
            log.error("Errore nel parsing dei dati meteo:", e)

#class OpenWeatherClient(QObject):
#    meteo_ready = Signal(dict)

#    def __init__(self, api_key=None, lat=None, lon=None, updates_per_hour=6):
#        super().__init__()
#        self.api_key = api_key
#        self.lat = lat
#        self.lon = lon
#        self.updates_per_hour = updates_per_hour
#        self.interval_sec = int(3600 / updates_per_hour)
#        self.last_data = None
#        self._timer = None
#        self._running = False
#        self._callback = None
#        log.info(f"☀️ OpenWeatherClient initialized with lat: {lat}, lon: {lon}.")

#    def update(self):
#        url = (
#            f"https://api.openweathermap.org/data/2.5/forecast?"
#            f"lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=metric&lang=it"
#        )
#        try:
#            resp = requests.get(url, timeout=10)
#            resp.raise_for_status()
#            data = resp.json()
#            self.last_data = data
#            self.print_fore(data)
#            if self._callback:
#                self._callback(data)
#            self.meteo_ready.emit(data)
#        except Exception as msg:
#            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")

#    def get_last(self):
#        return self.last_data

class UTILITY:   
    @staticmethod
    def log_all_threads_stacks():
        """Stampa o logga il Call Stack di TUTTI i thread attivi nel sistema."""
        try:
            import traceback

            # Mappa gli ID ai nomi dei thread (es. Dummy-51)
            thread_names = {t.ident: t.name for t in threading.enumerate()}
            
            if (len(thread_names)>=300):
                log.info(f"--- FOTOGRAFIA DI {len(thread_names)} THREAD ATTIVI ---")
                
                for thread_id, frame in sys._current_frames().items():
                    thread_name = thread_names.get(thread_id, f"Thread-{thread_id}")
                    
                    stack_trace = "".join(traceback.format_stack(frame))
                    log.info(f"\nThread: {thread_name} (ID: {thread_id})\n{stack_trace}")
        except Exception as e:
            log.error(f"🆘 Errore in log_all_threads_stacks: {e}")

    def in_range(start_hhmm, end_hhmm):
        try:
            now = datetime.now().time()
            start = dtime.fromisoformat(start_hhmm)
            end   = dtime.fromisoformat(end_hhmm)
            if start <= end:
                return start <= now <= end
            return now >= start or now <= end
        except Exception as e:
            log.error(f"🆘 Errore in in_range: {e}")
            return False

#   -----   👀  FILE HANDLER    👀  -----   #

class File():
    def __init__(self, path, debug=False):
        try:
            self.path = path

        except Exception as msg:
            log.error("🆘 Python {}:{}." .format(ins.currentframe().f_code.co_name, msg))
 
#   -----   👀  MAIN APP        👀  -----   #
if __name__ == '__main__':
    pass