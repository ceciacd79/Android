# -*- coding: utf-8 -*-
#!/usr/bin/python

__author__ = "Cechich Diego"
__copyright__ = "Copyright 2025"
__version__ = "0.1.0"
__license__ = "GPL"

#   -----   👀  MODULE          👀  -----   #
import json
import inspect as ins
import logging
import os

from cryptography.fernet import Fernet
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

log = logging.getLogger(__name__)

#   -----   👀  DEFINE          👀  -----   #

#   -----   👀  WORK CLASS      👀  -----   #
class file:
    def RD_json(path, filename):
        file = os.path.join(path, filename)
        data = None
        try:
            with open(file, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")
        finally:
            return data
        
    def save_Ui(dat_path, filename, theme, font_family, font_size):
        path = Path(dat_path) / filename
        data = {
            "theme": theme,
            "font_family": font_family,
            "font_size": font_size
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_Ui(dat_path, filename):
        path = Path(dat_path) / filename
        if not path.exists():
            return {"theme": "Light", "font_family": "Arial", "font_size": 10}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "theme": data.get("theme", "Light"),
            "font_family": data.get("font_family", "Arial"),
            "font_size": data.get("font_size", 10)
        }

    def save_ftp(dat_path, data, filename="init.json"):
        file_path = os.path.join(dat_path, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as msg:
            log.error(f"🆘 Impossibile salvare {file_path}: {msg}")
            return False

    def load_ftp(dat_path, filename="init.json"):
        file_path = os.path.join(dat_path, filename)
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as msg:
            log.error(f"🆘 Impossibile leggere {file_path}: {msg}")
            return {}

    def load_ftp_con(dat_path, filename="init.json"):
        file_path = os.path.join(dat_path, filename)
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f).get("conn", {})
        except Exception as msg:
            log.error(f"🆘 Impossibile leggere {file_path}: {msg}")
            return {}
        
    def save_ssh(dat_path, data, filename="init.json", key=None):
        file_path = os.path.join(dat_path, filename)
        try:
        #    data.get("password", None)
        #    data["password"] = key.encrypt(data["password"].encode())
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as msg:
            log.error(f"🆘 Impossibile salvare {file_path}: {msg}")
            return False

    def load_ssh(dat_path, filename="init.json"):       
        file_path = os.path.join(dat_path, filename)
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as msg:
            log.error(f"🆘 Impossibile leggere {file_path}: {msg}")
            return {}

    def read_topics_json(dat_path, filename="topic.json"):
        file_path = os.path.join(dat_path, filename)
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as msg:
            log.error(f"Impossibile leggere {file_path}: {msg}")
            return {}

    def read_topics(dat_path, filename="topic.json"):
        file_path = os.path.join(dat_path, filename)
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            result = []
            for device, values in data.items():
                for v in values:
                    result.append(f"HomeZig/{device}/{v}")
            return result
        except Exception as msg:
            log.error(f"Impossibile leggere {file_path}: {msg}")
            return {}

    def save_camera_configs(dat_path, data, filename="init.json"):
        file_path = os.path.join(dat_path, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as msg:
            log.error(f"🆘 Impossibile salvare {file_path}: {msg}")
            return False

    def load_camera_configs(dat_path, filename="init.json"):
        file_path = os.path.join(dat_path, filename)
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as msg:
            log.error(f"🆘 Impossibile leggere {file_path}: {msg}")
            return []

    def get_key(dat_path, key, filename="secret.key"):
        file_path = os.path.join(dat_path, filename)
        if not os.path.exists(file_path):
            key = Fernet.generate_key()
            with open(file_path, "wb") as key_file:
                key_file.write(key)
        try:
            with open(file_path, "rb") as key_file:
                key = key_file.read()
            return Fernet(key) 
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")
            return None
    
    def crypt(key, n_pass):
        try:
            return 
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")
            return None
        
    def decrypt(key, r_pass):
        try:
            return key.decrypt(r_pass).decode()
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")
            return None

    def RD_Init(self, path):
        data = None
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")
        finally:
            return data

    def RD_User(self, path):
        data = None
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")
        finally:
            return data

    def RD_CMD(self, path):
        data = None
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")
        finally:
            return data

    def SW_User(self, user_list, path):
        try:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(user_list, file, indent=4, ensure_ascii=False)
            log.info(f"ℹ USER_LIST save in to {path}.")
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")

    def SW_CMD(self, user_list, path):
        try:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(user_list, file, indent=4, ensure_ascii=False)
            log.info(f"ℹ CMD_LIST save in to {path}.")
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")

    def save_user(user_id, first_name, data_path, file_ut):
        path = Path(data_path) / file_ut
        # Carica utenti esistenti
        try:
            with open(path, "r", encoding="utf-8") as f:
                users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            users = {}

        # Salva/aggiorna utente
        users[str(user_id)] = first_name

        # Scrivi su file
        with open(path, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

    def save_group(group_id, title, data_path, file_ut="groups.json"):
        """Salva gruppo in groups.json"""
        try:
            file_path = data_path / file_ut
            groups = {}
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        groups = json.load(f)
                except Exception:
                    groups = {}
            
            groups[str(group_id)] = {
                "title": title,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(groups, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # log o raise a seconda della gestione errori esistente nella classe
            raise Exception(f"Errore save_group: {e}")

    def get_users(data_path, filename="user.json"):
        file_path = os.path.join(data_path, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}.")
            return []

#   -----   👀  MAIN APP        👀  -----   #
if __name__ == '__main__':
    pass