# -*- coding: utf-8 -*-
#!/usr/bin/python

__author__ = "Cechich Diego"
__copyright__ = "Copyright 2025"
__version__ = "0.0.2"
__license__ = "GPL"

#   -----   👀  MODULE          👀  -----   #
import inspect as ins
import logging
import mysql.connector as mariadb
import requests
import json

import requests
import threading
import os
from icalendar import Calendar
from datetime import datetime, timezone

from datetime import date, datetime, timedelta, time as dtime
from pathlib import Path
from sqlalchemy import (
    create_engine, inspect, MetaData, Table, Column, ForeignKey, UniqueConstraint,
    Integer, BigInteger, String, Date, Time, Text, Boolean, Double,
    select, delete, text
)
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

# include_object è la funzione che Alembic chiama per decidere se includere o escludere un oggetto (tabella, colonna, ecc.) durante l'autogenerazione delle migrazioni. Restituisce True per includere, False per escludere.
# $env:PYTHONPATH="..;."
# alembic revision --autogenerate -m "Allineamento finale LOGS"
# alembic upgrade head
# python -c "from sqlalchemy import create_engine, text; engine = create_engine('mysql+pymysql://root:AntoFedeGio79!@192.168.178.150/Home'); conn = engine.connect(); conn.execute(text('TRUNCATE TABLE alembic_version')); conn.commit(); conn.close(); print('Svuotato con successo!')"

# docker exec -it cont_mqtt alembic revision --autogenerate -m "Reset iniziale database"

#   -----   👀  DEFINE          👀  -----   #

#   -----   👀  GLOBAL VARIABLE 👀  -----   #
log_path = ""
#   -----   👀  WORK CLASS      👀  -----   #
log = logging.getLogger(__name__)
Base = declarative_base()       # 🚀 QUESTA È LA "BASE" (Serve ad Alembic per leggere le tabelle)

#   -----   👀  DEFINIZIONE TABELLE  ALEMBIC     👀  -----   #
class TabellaLog(Base):
    __tablename__ = 'LOGS'                                                      # 🚀 Nome della tabella
    __table_args__ = {                                                          # 🚀 ECCO COME INSERIRE IL COMMENTO DELLA TABELLA
        'mysql_comment': 'Log entries from home automation system',
        'mariadb_comment': 'Log entries from home automation system'
    }
    ID_KEY = Column(Integer, primary_key=True, autoincrement=True)
    DAY_U = Column(Date, nullable=False)
    TIME_U = Column(Time, nullable=False)
    TYPE = Column(String(20))
    ROOM = Column(String(50))
    FLOOR = Column(String(20))
    MSG = Column(String(80)) 
    
class TabellaDevice(Base):
    __tablename__ = 'DEVICE'                                                    # 🚀 Nome della tabella
    __table_args__ = {                                                          # 🚀 ECCO COME INSERIRE IL COMMENTO DELLA TABELLA
        'mysql_comment': 'Device from MQTT',
        'mariadb_comment': 'Device from MQTT'
    }
    ID_KEY = Column(Integer, primary_key=True, autoincrement=True)
    FRIENDLY_NAME = Column(String(80))
    IEEE_ADDRESS = Column(String(32), unique=True)
    TYPE = Column(String(20))
    DESCRIPTION = Column(String(100))
    MODEL = Column(String(50))
    VENDOR = Column(String(50))
    MANUFACTURER = Column(String(50))
    MODEL_ID = Column(String(50))
    POWER_SOURCE = Column(String(50))

class TabellaDeviceInfo(Base):
    __tablename__ = 'DEVICE_INFO'                                               # 🚀 Nome della tabella
    __table_args__ = {                                                          # 🚀 ECCO COME INSERIRE IL COMMENTO DELLA TABELLA
        'mysql_comment': 'Info aggiuntive device (posizione, nome, piano, stanza)',
        'mariadb_comment': 'Info aggiuntive device (posizione, nome, piano, stanza)'
    }
    ID_KEY = Column(                                                            # 🚀 ID_KEY è la Chiave Primaria E fa riferimento a DEVICE.ID_KEY con ON DELETE CASCADE
        Integer, 
        ForeignKey('DEVICE.ID_KEY', ondelete='CASCADE'), 
        primary_key=True
    )
    POSITION = Column(String(100))
    NAME = Column(String(100))
    FLOOR = Column(String(20))
    ROOM = Column(String(50))
    LEVEL = Column(Integer)

class TabellaSchedule(Base):
    __tablename__ = 'SCHEDUL'                                                   # 🚀 Nome della tabella
    __table_args__ = {                                                          # 🚀 ECCO COME INSERIRE IL COMMENTO DELLA TABELLA
        'mysql_comment': 'Schedulazioni MQTT',
        'mariadb_comment': 'Schedulazioni MQTT'
    }
    ID_KEY = Column(Integer, primary_key=True, autoincrement=True)
    NAME = Column(String(50))
    TIME = Column(String(20))
    ACTION = Column(String(100))
    ENABLED = Column(Boolean, default=True)

class TabellaGruppi(Base):
    __tablename__ = 'GRUPPI'                                                    # 🚀 Nome della tabella
    __table_args__ = {                                                          # 🚀 ECCO COME INSERIRE IL COMMENTO DELLA TABELLA
        'mysql_comment': 'Gruppi di dispositivi dal bridge',
        'mariadb_comment': 'Gruppi di dispositivi dal bridge'
    }
    ID_KEY = Column(Integer, primary_key=True, autoincrement=True)
    NAME = Column(Text)
    GROUP_ID = Column(Integer, unique=True)

class TabellaScene(Base):
    __tablename__ = 'SCENE'                                                     # 🚀 Nome della tabella
    __table_args__ = {                                                          # 🚀 ECCO COME INSERIRE IL COMMENTO DELLA TABELLA
        'mysql_comment': 'Scene dei gruppi dal bridge',
        'mariadb_comment': 'Scene dei gruppi dal bridge'
    }
    ID_KEY = Column(Integer, primary_key=True, autoincrement=True)
    GROUP_ID = Column(Integer)
    SCENE_ID = Column(Integer)
    NAME = Column(String(32))
    __table_args__ = (
        UniqueConstraint('GROUP_ID', 'SCENE_ID', name='uix_group_scene'),
        {'mysql_comment': 'Scene dei gruppi dal bridge', 'mariadb_comment': 'Scene dei gruppi dal bridge'}
    )

class TabellaRoom(Base):
    __tablename__ = 'ROOM'                                                      # 🚀 Nome della tabella
    __table_args__ = {                                                          # 🚀 ECCO COME INSERIRE IL COMMENTO DELLA TABELLA
        'mysql_comment': 'Nome Room',
        'mariadb_comment': 'Nome Room'
    }
    ID_KEY = Column(Integer, primary_key=True, autoincrement=True)
    TITLE = Column(String(30), unique=True, nullable=False)

class TabellaFloor(Base):
    __tablename__ = 'FLOOR'                                                     # 🚀 Nome della tabella
    __table_args__ = {                                                          # 🚀 ECCO COME INSERIRE IL COMMENTO DELLA TABELLA
        'mysql_comment': 'Nome Piani',
        'mariadb_comment': 'Nome Piani'
    }
    ID_KEY = Column(Integer, primary_key=True, autoincrement=True)
    TITLE = Column(String(30), unique=True, nullable=False)

class TabellaUserChatID(Base):
    __tablename__ = 'USER_CHATID'                                               # 🚀 Nome della tabella
    __table_args__ = {                                                          # 🚀 ECCO COME INSERIRE IL COMMENTO DELLA TABELLA
        'mysql_comment': 'Chat ID degli utenti Telegram',
        'mariadb_comment': 'Chat ID degli utenti Telegram'
    }
    ID_KEY = Column(Integer, primary_key=True, autoincrement=True)
    USERNAME = Column(String(80))
    USER_ID = Column(BigInteger)
    CHAT_ID = Column(BigInteger, unique=True)

class TabellaActions(Base):
    __tablename__ = 'ACTIONS'                                                   # 🚀 Nome della tabella
    __table_args__ = {                                                          # 🚀 ECCO COME INSERIRE IL COMMENTO DELLA TABELLA
        'mysql_comment': 'Azioni eseguibili (MQTT, HTTP, ecc.)',
        'mariadb_comment': 'Azioni eseguibili (MQTT, HTTP, ecc.)'
    }
    ID = Column(Integer, primary_key=True, autoincrement=True)
    NAME = Column(String(32))
    TOPIC = Column(String(64))
    BYPASS = Column(String(20))
    AUTO = Column(String(20))
    ACTION = Column(String(20))
    TAMPER = Column(String(20))
    WATER_LEAK = Column(String(20))
    CONTACT = Column(String(20))
    OCCUPANCY = Column(String(20))
    BATTERY = Column(String(20))
    BATTERY_LOW = Column(String(20))
    STATE = Column(String(20))
    LIM_MIN = Column(Integer)
    LIM_MAX = Column(Integer)
    POWER_A = Column(Integer)
    HUMIDITY = Column(Integer)
    TEMPERATURE = Column(Integer)
    COLOR_TEMP = Column(Integer)
    BRIGHTNESS = Column(Integer)
    STEP = Column(Integer)
    STEPS = Column(Integer)
    TRANSITION = Column(Integer)
    MSG = Column(String(255))
    ROOM = Column(String(20))
    FLOOR = Column(String(20))

class TabellaKeyActions(Base):
    __tablename__ = 'KEY_ACTIONS'                                               # 🚀 Nome della tabella
    __table_args__ = {                                                          # 🚀 ECCO COME INSERIRE IL COMMENTO DELLA TABELLA
        'mysql_comment': 'Azioni chiave (es. BYPASS, AUTO, ecc.)',
        'mariadb_comment': 'Azioni chiave (es. BYPASS, AUTO, ecc.)'
    }
    ID = Column(Integer, primary_key=True, autoincrement=True)
    NAME = Column(String(255), nullable=False, server_default='')
    __table_args__ = (
        UniqueConstraint('NAME', name='unique_name'),
    )


class Home():
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

        # 🚀 INIZIALIZZIAMO LA SESSIONE DI SQLALCHEMY
        try:
            url_sql = f"mysql+pymysql://{user}:{password}@{host}:{int(port)}/{database}"
            self.engine = create_engine(url_sql, pool_recycle=3600)
            self.SessionMaker = sessionmaker(bind=self.engine)
            log.info("🚀 SQLAlchemy Engine inizializzato correttamente in home.py!")
        except Exception as e:
            log.error(f"❌ Impossibile inizializzare SQLAlchemy: {e}")

#   -----   👀  FUNCTIONALY     👀  -----   #
    def GET_TABLE_COLUMNS(self, table_name: str):
        """Restituisce le colonne di una tabella. Thread-safe."""
        try:
            if not table_name or not isinstance(table_name, str):
                log.error("GET_TABLE_COLUMNS: table_name non valido.")
                return []

            inspector = inspect(self.engine)                                                                    # Creiamo l'oggetto Inspector agganciato al nostro motore di connessione engine
            if table_name.upper() not in [t.upper() for t in inspector.get_table_names()]:                      # Verifichiamo prima se la tabella esiste sul database. inspector.get_table_names() restituisce la lista di tutte le tabelle esistenti
                log.debug(f"GET_TABLE_COLUMNS: la tabella `{table_name}` non esiste sul database.")
                return []

            columns_info = inspector.get_columns(table_name)                                                    # Recuperiamo l'elenco delle colonne. Restituisce una lista di dizionari, ognuno contenente informazioni dettagliate sulla colonna
            
            # 4. Formattiamo l'output per emulare parzialmente la struttura di prima se necessario,
            # oppure restituiamo i dati puliti. 
            # NOTA: Ognuno degli elementi in columns_info è un dizionario fatto così:
            # {'name': 'ID_KEY', 'type': INTEGER(), 'nullable': False, 'default': None, 'autoincrement': True}
            
            return columns_info

        except SQLAlchemyError as e:
            log.error(f"❌ Errore SQLAlchemy in GET_TABLE_COLUMNS: {e}")
            return []
        except Exception as e:
            log.error(f"🆘 Errore generico Python in GET_TABLE_COLUMNS: {e}")
            return []

    def GET_TABLE_ROW_COUNT(self, table_name: str):
        """Restituisce il numero di righe di una tabella."""
        session = self.SessionMaker()
        try:
            if not table_name or not isinstance(table_name, str):
                log.error("GET_TABLE_ROW_COUNT: table_name non valido.")
                return 0

            # Componiamo la QUERY testuale in modo sicuro
            # Usiamo i backtick ` per proteggere il nome della tabella da caratteri speciali o riservati
            QUERY = text(f"SELECT COUNT(*) FROM `{table_name}`")
            
            # Eseguiamo la QUERY e usiamo .scalar() per estrarre direttamente il primo valore numerico
            result = session.execute(QUERY)
            count = result.scalar()
            
            return count if count is not None else 0

        except SQLAlchemyError as e:
            log.error(f"❌ Errore SQLAlchemy in GET_TABLE_ROW_COUNT per {table_name}: {e}")
            return 0
        except Exception as e:
            log.error(f"🆘 Errore generico Python in GET_TABLE_ROW_COUNT: {e}")
            return 0
        finally:
            session.close()

    def GET_TABLE_COMMENT(self, table_name: str):
        """Restituisce il commento di una tabella."""
        try:
            if not table_name or not isinstance(table_name, str):
                log.error("GET_TABLE_COMMENT: table_name non valido.")
                return ""

            inspector = inspect(self.engine)                                            # Creiamo l'oggetto Inspector agganciato al nostro motore engine
            comment_dict = inspector.get_table_comment(table_name)                      # ecuperiamo il commento della tabella. Restituisce un dizionario fatto così: {'text': 'Il tuo commento qui'}
            comment_text = comment_dict.get('text', '')                                 # Estraiamo il testo dal dizionario. Se non c'è, restituiamo una stringa vuota
            
            return comment_text if comment_text else ""
        except SQLAlchemyError as e:
            log.error(f"❌ Errore SQLAlchemy in GET_TABLE_COMMENT per {table_name}: {e}")
            return ""
        except Exception as e:
            log.error(f"🆘 Errore generico Python in GET_TABLE_COMMENT: {e}")
            return ""

    def GET_TABLE(self):
        """Restituisce la lista di tutte le tabelle nel database."""
        try:
            inspector = inspect(self.engine)
            table_names = inspector.get_table_names()
            return table_names
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return []

    def GET_TABLE_DATA(self, table_name: str, limit: int = 100, offset: int = 0):
        """Restituisce i dati di una tabella con paginazione."""
        try:
            # 🛡️ SICUREZZA ANTI SQL-INJECTION: 
            clean_table_name = "".join(c for c in table_name if c.isalnum() or c in ("_", "-"))                 # Rimuoviamo eventuali apici singoli, doppi o caratteri strani dal nome della tabella

            with self.engine.connect() as conn:
                QUERY = text(f"SELECT * FROM `{clean_table_name}` LIMIT :limit OFFSET :offset")
                result = conn.execute(QUERY, {"limit": limit, "offset": offset})
                
                # Recuperiamo le righe convertendole in dizionari o tuple (fetchall restituisce oggetti Row)
                # Trasformarli in tuple mantiene la compatibilità al 100% con il tuo vecchio codice Flet
                data = [tuple(row) for row in result]
                return data
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return []

#   -----   👀  PROJECT         👀  -----   #
    def MK_TAB_ZIG(self, table, data, model, label=None):
        """Create Dinamic table."""
        try:
            if not isinstance(table, str) or not table.strip():
                log.error("MK_TAB_ZIG: table name non valido.")
                return False
            if not isinstance(data, dict) or not data:
                log.error("MK_TAB_ZIG: data non valido o vuoto.")
                return False
            if not isinstance(model, str) or not model.strip():
                log.error("MK_TAB_ZIG: model non valido.")
                return False

            table_name = table.upper()

            type_map = {
                bool: Boolean,
                int: Integer,
                float: Double,
                str: Text
            }

            metadata = MetaData()                                                       # Creiamo l'oggetto MetaData e iniziamo a definire le colonne
            columns = [                                                                 # Colonne base fisse (ID, Data, Ora)
                Column("ID_KEY", Integer, primary_key=True, autoincrement=True),
                Column("DAY_U", Date, nullable=False),
                Column("TIME_U", Time, nullable=False)
            ]

            for x, val in data.items():                                                 # Ciclo sui dati per aggiungere le colonne dinamiche
                if not isinstance(x, str):
                    continue
                col_name = x.upper()
                col_type = type_map.get(type(val), None)
                
                if col_type:
                    if col_type == Boolean:
                        columns.append(Column(col_name, col_type, server_default="0"))  # FALSE
                    elif col_type in [Integer, Double]:
                        columns.append(Column(col_name, col_type, server_default="0"))
                    else:
                        columns.append(Column(col_name, col_type)) # TEXT
                else:
                    log.debug(f"MK_TAB_ZIG: tipo non gestito per campo {col_name}: {type(val)}")

            if len(columns) == 3:                                                       # Significa che ci sono solo ID_KEY, DAY_U e TIME_U
                log.error("MK_TAB_ZIG: nessuna colonna valida trovata in data.")
                return False

            nuova_tabella = Table(table_name, metadata, *columns, extend_existing=True)
            metadata.create_all(self.engine, tables=[nuova_tabella])
            comment = f"{model}, {table}, {label}" if label else f"{model}, {table}"

            with self.engine.begin() as connection:
                # text() di SQLAlchemy protegge da SQL Injection e formatta correttamente la stringa
                query_comment = text(f"ALTER TABLE `{table_name}` COMMENT = :comment_val")
                connection.execute(query_comment, {"comment_val": comment})

            log.debug(f"🛠️ Tabella dinamica {table_name} verificata/creata con successo.")
            return True
        except SQLAlchemyError as e:
            log.error(f"❌ Errore SQLAlchemy in MK_TAB_ZIG: {e}")
            return False
        except Exception as e:
            log.error(f"🆘 Errore generico Python in MK_TAB_ZIG: {e}")
            return False

    def UP_TAB_ZIG(self, topic, data):
        """Aggiorna la tabella con nuove colonne a runtime se non esistono. 
        Thread-safe e compatibile SQLAlchemy 2.0.
        """
        session = self.SessionMaker()
        try:
            table_name = topic.upper()
            query_desc = text(f"DESCRIBE {table_name}")
            myresult = session.execute(query_desc).fetchall()
            col_n = [col[0].upper() for col in myresult]
            for d in data:
                col_name = d.upper()
                if col_name not in col_n:
                    query_alter = f"ALTER TABLE {table_name} "
                    type_d = type(data[d])
                    if type_d is bool:
                        query_alter += f"ADD {col_name} BOOL DEFAULT FALSE"
                    elif type_d is int:
                        query_alter += f"ADD {col_name} INT DEFAULT 0"
                    elif type_d is float:
                        query_alter += f"ADD {col_name} DOUBLE DEFAULT 0"
                    elif type_d is str:
                        query_alter += f"ADD {col_name} TEXT"
                    else:
                        log.debug(f"Tipo non supportato per colonna {col_name}: {type_d}")
                    log.debug(f"SQL ADD New col {col_name}, tipo rilevato: {type_d.__name__}")
                    session.execute(text(query_alter))
            session.commit()
        except SQLAlchemyError as msg:
            session.rollback()
            log.error(f"❌ SQL ORM {ins.currentframe().f_code.co_name}: {msg}")
        except Exception as msg:
            if session:
                session.rollback()
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
        finally:
            session.close()

    def ENSURE_DEVICE_INFO(self, ieee_address):
        """Assicura che esista una riga in DEVICE_INFO per il device con questo IEEE_ADDRESS. Thread-safe. Usa 'with' per connessione/cursore."""
        session = self.SessionMaker()
        try:
            # 1. Cerchiamo l'ID_KEY del dispositivo partendo dall'IEEE_ADDRESS
            query_device = select(TabellaDevice.ID_KEY).where(TabellaDevice.IEEE_ADDRESS == ieee_address)
            id_key = session.execute(query_device).scalar_one_or_none()
            
            # Se il dispositivo non esiste ancora nella tabella DEVICE, usciamo
            if id_key is None:
                return False
                
            # 2. Verifichiamo se esiste già la riga corrispondente in DEVICE_INFO
            query_info = select(TabellaDeviceInfo).where(TabellaDeviceInfo.ID_KEY == id_key)
            info_esistente = session.execute(query_info).scalar_one_or_none()
            
            # 3. Se non esiste, creiamo la riga vuota di "ancoraggio"
            if info_esistente is None:
                nuova_info = TabellaDeviceInfo(ID_KEY=id_key)
                session.add(nuova_info)
                session.commit()
                log.debug(f"ℹ️ Creata riga di default in DEVICE_INFO per ID_KEY: {id_key}")
                
            return True
            
        except Exception as e:
            session.rollback()
            log.error(f"❌ Errore in ENSURE_DEVICE_INFO (SQLAlchemy): {e}")
            return False
        finally:
            session.close()

    def UP_TAB_LOG(self, time, log_t, room="", floor="", msg=""):
        """Scrive i log nel DB usando la nuova classe TabellaLog"""
        session = self.SessionMaker()
        try:
            dt = datetime.fromtimestamp(time)
            day = dt.strftime("%Y-%m-%d")
            time = dt.strftime("%H:%M:%S")
            # Usiamo la classe definita in cima al file per creare la riga
            QUERY = TabellaLog(
                DAY_U=day,                                  # Inserisce la data (es. 2026-06-01)
                TIME_U=time,                                # Inserisce l'ora (es. 17:45:00)
                TYPE=str(log_t),
                ROOM=str(room) if room else None,
                FLOOR=str(floor) if floor else None,
                MSG=str(msg) if msg else None
            )
            session.add(QUERY)
            session.commit()
        except Exception as e:
            session.rollback()
            log.error(f"❌ Errore scrittura LOG (SQLAlchemy): {e}")
        finally:
            session.close()

    def GET_TAB_LOG(self):
        """Restituisce i log di un giorno specifico. Thread-safe."""
        session = self.SessionMaker()
        try:
            QUERY = select(TabellaLog).order_by(TabellaLog.DAY_U.desc(), TabellaLog.TIME_U.desc()).limit(100)
            RES = session.execute(QUERY)
            LIST = RES.scalars().all()
            return LIST
        except Exception as e:
            log.error(f"❌ Errore lettura LOG (SQLAlchemy): {e}")
            return []
        finally:
            session.close()

    def MK_TAB_GROUP(self, data):
        """Sincronizza gruppi e scene ricevuti da MQTT con il database. Thread-safe."""
        session = self.SessionMaker()
        try:
            # Estrazione e validazione preliminare dei gruppi dall'input JSON
            gruppi = None
            if isinstance(data, dict) and 'state' in data and isinstance(data['state'], list):
                gruppi = data['state']
            elif isinstance(data, list):
                gruppi = data

            # 1. Recuperiamo tutti i GROUP_ID attualmente presenti sul DB
            query_db_groups = select(TabellaGruppi.GROUP_ID)
            db_group_ids = set(session.execute(query_db_groups).scalars().all())
            new_group_ids = set()

            if gruppi:
                for group in gruppi:
                    group_id = group.get("id")
                    name = group.get("friendly_name") or group.get("name")
                    
                    if group_id is not None and name:
                        new_group_ids.add(group_id)
                        
                        # 🚀 UPSERT Gruppo (Equivale a INSERT ... ON DUPLICATE KEY UPDATE)
                        stmt_gruppo = mysql_insert(TabellaGruppi).values(NAME=str(name), GROUP_ID=group_id)
                        stmt_gruppo = stmt_gruppo.on_duplicate_key_update(
                            NAME=stmt_gruppo.inserted.NAME,
                            GROUP_ID=stmt_gruppo.inserted.GROUP_ID
                        )
                        session.execute(stmt_gruppo)
                        
                    # Gestione e Sincronizzazione delle Scene collegate al Gruppo
                    scenes = group.get("scenes")
                    if scenes and isinstance(scenes, list):
                        new_scene_ids = set()
                        for scene in scenes:
                            scene_id = scene.get("id")
                            scene_name = scene.get("name")
                            
                            if scene_id is not None and scene_name:
                                new_scene_ids.add(scene_id)
                                
                                # 🚀 UPSERT Scena (Sfrutta il vincolo UNIQUE su GROUP_ID e SCENE_ID)
                                stmt_scena = mysql_insert(TabellaScene).values(
                                    GROUP_ID=group_id, 
                                    SCENE_ID=scene_id, 
                                    NAME=str(scene_name)
                                )
                                stmt_scena = stmt_scena.on_duplicate_key_update(
                                    NAME=stmt_scena.inserted.NAME
                                )
                                session.execute(stmt_scena)
                        
                        # Rilevamento e rimozione delle scene eliminate per questo specifico gruppo
                        query_db_scenes = select(TabellaScene.SCENE_ID).where(TabellaScene.GROUP_ID == group_id)
                        db_scene_ids = set(session.execute(query_db_scenes).scalars().all())
                        to_remove_scenes = db_scene_ids - new_scene_ids
                        
                        if to_remove_scenes:
                            stmt_del_scenes = delete(TabellaScene).where(
                                TabellaScene.GROUP_ID == group_id,
                                TabellaScene.SCENE_ID.in_(to_remove_scenes)
                            )
                            session.execute(stmt_del_scenes)

            # 2. Pulizia Globale: Rimuoviamo i gruppi interi (e le loro scene) non più presenti su MQTT
            if gruppi and new_group_ids:
                to_remove_groups = db_group_ids - new_group_ids
                if to_remove_groups:
                    # Cancella tutte le scene associate ai gruppi rimossi
                    session.execute(delete(TabellaScene).where(TabellaScene.GROUP_ID.in_(to_remove_groups)))
                    # Cancella i gruppi rimossi
                    session.execute(delete(TabellaGruppi).where(TabellaGruppi.GROUP_ID.in_(to_remove_groups)))

            # Applichiamo tutte le modifiche (Insert, Update, Delete) in un'unica transazione sicura
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            log.error(f"❌ Errore sincronizzazione gruppi/scene (SQLAlchemy): {e}")
            return False
        finally:
            session.close()

    def UP_TAB_PIANO(self, title):
        """Aggiorna o inserisce un piano nella tabella PIANO. Esegue la QUERY in un thread separato."""
        def worker(piano_list):
            session = self.SessionMaker()
            try:
                for piano in piano_list:
                    QUERY = mysql_insert(TabellaFloor).values(TITLE=str(piano).strip())
                    QUERY = QUERY.on_duplicate_key_update(
                        TITLE=QUERY.inserted.TITLE
                    )
                    session.execute(QUERY)
                session.commit()
                log.debug(f"🏢 Piani sincronizzati con successo in background: {piano_list}")
            except Exception as e:
                session.rollback()
                log.error(f"❌ Errore scrittura PIANO (SQLAlchemy Threaded): {e}")
            finally:
                session.close()

        # Se title è una stringa singola, lo converto in lista
        if isinstance(title, str):
            piano_list = [title]
        else:
            piano_list = list(title)

        t = threading.Thread(target=worker, args=(piano_list,))
        t.start()

    def GET_PIANI(self):
        """Restituisce la lista dei piani ordinati per TITLE."""
        session = self.SessionMaker()
        try:
            QUERY = select(TabellaFloor).order_by(TabellaFloor.TITLE.desc())
            RES = session.execute(QUERY)
            LIST = RES.scalars().all()
            return LIST
        except Exception as e:
            log.error(f"❌ Errore lettura PIANO (SQLAlchemy): {e}")
            return []
        finally:
            session.close()

    def UP_TAB_ROOM(self, title):
        """Aggiorna o inserisce una room nella tabella ROOM. Thread-safe."""
        def worker(room_list):
            session = self.SessionMaker()                                               # 🚀 APRIAMO LA SESSIONE UNA VOLTA SOLA PER TUTTA LA LISTA (Molto più veloce!)
            try:
                for room in room_list:
                    if not room or not str(room).strip():
                        continue
                    QUERY = mysql_insert(TabellaRoom).values(TITLE=str(room).strip())
                    QUERY = QUERY.on_duplicate_key_update(
                        TITLE=QUERY.inserted.TITLE
                    )
                    session.execute(QUERY)
                session.commit()
                log.debug(f"🏠 Stanze sincronizzate con successo in background: {room_list}")
            except Exception as e:
                session.rollback()
                log.error(f"❌ Errore scrittura ROOM (SQLAlchemy Threaded): {e}")
            finally:
                session.close()

        if isinstance(title, str):
            room_list = [title]
        else:
            room_list = list(title)
        t = threading.Thread(target=worker, args=(room_list,), daemon=True)
        t.start()

    def GET_ROOM(self):
        """Restituisce la lista delle room ordinate per TITLE."""
        session = self.SessionMaker()
        try:
            QUERY = select(TabellaRoom).order_by(TabellaRoom.TITLE.desc())
            RES = session.execute(QUERY)
            LIST = RES.scalars().all()
            return LIST
        except Exception as e:
            log.error(f"❌ Errore lettura ROOM (SQLAlchemy): {e}")
            return []
        finally:
            session.close()

    def UP_TAB_ACTION(self, name, data):
        """Aggiorna o inserisce un'azione nella tabella ACTION. Thread-safe."""
        session = self.SessionMaker()
        try:
            insert_vals = {
                "NAME": name,
                "TOPIC": data.get("TOPIC"),
                "BYPASS": data.get("BYPASS"),
                "AUTO": data.get("AUTO"),
                "ACTION": data.get("ACTION"),
                "TAMPER": data.get("TAMPER"),
                "WATER_LEAK": data.get("WATER_LEAK"),
                "CONTACT": data.get("CONTACT"),
                "OCCUPANCY": data.get("OCCUPANCY"),
                "BATTERY": data.get("BATTERY"),
                "BATTERY_LOW": data.get("BATTERY_LOW"),
                "STATE": data.get("STATE"),
                "LIM_MIN": data.get("LIM_MIN"),
                "LIM_MAX": data.get("LIM_MAX"),
                "POWER_A": data.get("POWER_A"),
                "HUMIDITY": data.get("HUMIDITY"),
                "TEMPERATURE": data.get("TEMPERATURE"),
                "COLOR_TEMP": data.get("COLOR_TEMP"),
                "BRIGHTNESS": data.get("BRIGHTNESS"),
                "STEP": data.get("STEP"),
                "STEPS": data.get("STEPS"),
                "TRANSITION": data.get("TRANSITION"),
                "MSG": data.get("MSG"),
                "ROOM": data.get("ROOM"),
                "FLOOR": data.get("FLOOR")
            }
            QUERY = mysql_insert(TabellaActions).values(**insert_vals)

            update_dict = {
                c.name: QUERY.inserted[c.name] 
                for c in TabellaActions.__table__.columns 
                if c.name != 'NAME'
            }
            on_duplicate_stmt = QUERY.on_duplicate_key_update(**update_dict)
            session.execute(on_duplicate_stmt)
            session.commit()
        except SQLAlchemyError as msg:
            session.rollback()
            log.error(f"❌ SQL ORM {ins.currentframe().f_code.co_name}: {msg}")
        except Exception as msg:
            if session:
                session.rollback()
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
        finally:
            session.close()

    def GET_TAB_ACTION(self):
        """Recupera tutte le azioni dalla tabella ACTIONS come lista di dict."""
        session = self.SessionMaker()
        actions = []
        try:
            QUERY = select(TabellaActions).order_by(TabellaActions.NAME.asc())
            db_rows = session.execute(QUERY).scalars().all()
            
            for row_obj in db_rows:
                action = {
                    "ID_KEY": getattr(row_obj, "ID_KEY", getattr(row_obj, "ID", None)),
                    "NAME": row_obj.NAME,
                    "TOPIC": row_obj.TOPIC,
                    "BYPASS": row_obj.BYPASS,
                    "AUTO": row_obj.AUTO,
                    "ACTION": row_obj.ACTION,
                    "TAMPER": row_obj.TAMPER,
                    "WATER_LEAK": row_obj.WATER_LEAK,
                    "CONTACT": row_obj.CONTACT,
                    "OCCUPANCY": row_obj.OCCUPANCY,
                    "BATTERY": row_obj.BATTERY,
                    "BATTERY_LOW": row_obj.BATTERY_LOW,
                    "STATE": row_obj.STATE,
                    "LIM_MIN": row_obj.LIM_MIN,
                    "LIM_MAX": row_obj.LIM_MAX,
                    "POWER_A": row_obj.POWER_A,
                    "HUMIDITY": row_obj.HUMIDITY,
                    "TEMPERATURE": row_obj.TEMPERATURE,
                    "COLOR_TEMP": row_obj.COLOR_TEMP,
                    "BRIGHTNESS": row_obj.BRIGHTNESS,
                    "STEP": row_obj.STEP,
                    "STEPS": row_obj.STEPS,
                    "TRANSITION": row_obj.TRANSITION,
                    "MSG": row_obj.MSG,
                    "ROOM": row_obj.ROOM,
                    "FLOOR": row_obj.FLOOR
                }
                actions.append(action)
                
        except SQLAlchemyError as msg:
            log.error(f"❌ SQL ORM {ins.currentframe().f_code.co_name}: {msg}")
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
        finally:
            session.close()
        return actions

    def CK_KEY_ACTION(self, COL_NAME):
        """Crea la tabella KEY_ACTIONS."""
        session = self.SessionMaker()
        try:
            if COL_NAME:
                db_records = session.query(TabellaKeyActions.NAME).all()
                db_names = {row.NAME for row in db_records}
                current_names = set(COL_NAME)

                to_delete = db_names - current_names
                if to_delete:
                    session.query(TabellaKeyActions).filter(
                        TabellaKeyActions.NAME.in_(to_delete)
                    ).delete(synchronize_session=False)

                to_insert = current_names - db_names
                if to_insert:
                    nuovi_record = [TabellaKeyActions(NAME=x) for x in to_insert]
                    session.bulk_save_objects(nuovi_record)
            else:
                session.query(TabellaKeyActions).delete(synchronize_session=False)
            session.commit()
        except Exception as msg:
            session.rollback()
            log.error(f"🆘 Errore in {ins.currentframe().f_code.co_name}: {msg}")
        finally:
            session.close()

    def GET_KEY_ACTION(self):
        """Restituisce tutte le chiavi di azione dalla tabella KEY_ACTIONS come lista. Thread-safe."""
        session = self.SessionMaker()
        try:
            QUERY = select(TabellaKeyActions.NAME).order_by(TabellaKeyActions.NAME.asc())
            RES = session.execute(QUERY)
            LIST = RES.scalars().all()
            return LIST
        except Exception as e:
            log.error(f"❌ Errore lettura KEY_ACTIONS (SQLAlchemy): {e}")
            return []
        finally:
            session.close()

    










    def MK_TAB_SCHEDULE(self):
        """Crea la tabella SCHEDULE se non esiste. Thread-safe."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            QUERY = (
                "CREATE TABLE IF NOT EXISTS SCHEDULE ("
                "ID INT PRIMARY KEY AUTO_INCREMENT, "
                "NAME VARCHAR(32) NOT NULL UNIQUE, "
                "DATA JSON NOT NULL)"
            )
            cur = conn.cursor()
            cur.execute(QUERY)
            cur.close()
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
        finally:
            if conn:
                conn.close()

    def UP_TAB_DEVICE(self, device_row: dict):
        """Aggiorna la tabella DEVICE: inserisce o aggiorna il device usando le colonne reali della tabella. Thread-safe. Usa 'with' per connessione/cursore."""
        try:
            with mariadb.connect(**self.conn_params) as conn:
                with conn.cursor() as cur:
                    cur.execute("DESCRIBE DEVICE")
                    columns = [col[0] for col in cur.fetchall()]
                    fields = [col for col in columns if col != "ID_KEY"]
                    values = [device_row.get(f.lower()) for f in fields]
                    update_clause = ', '.join([f"{f}=VALUES({f})" for f in fields if f.lower() != "ieee_address"])
                    QUERY = f"INSERT INTO DEVICE ({', '.join(fields)}) "
                    QUERY += f"VALUES ({', '.join(['%s']*len(values))}) "
                    QUERY += f"ON DUPLICATE KEY UPDATE {update_clause}"
                    cur.execute(QUERY, values)
                    conn.commit()
                    log.debug(f"DEVICE aggiornato: {device_row.get('friendly_name')} ({device_row.get('ieee_address')})")
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")      

    def GET_SCENE_GROUP_JOIN(self):
        """Restituisce l'unione (JOIN) tra SCENE e GRUPPI."""
        conn = None
        data = []
        columns = []
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            QUERY = (
                "SELECT SCENE.GROUP_ID, GRUPPI.NAME as GROUP_NAME, SCENE.SCENE_ID, SCENE.NAME as SCENE_NAME "
                "FROM SCENE "
                "LEFT JOIN GRUPPI ON SCENE.GROUP_ID = GRUPPI.GROUP_ID "
                "ORDER BY SCENE.GROUP_ID, SCENE.SCENE_ID"
            )
            cur.execute(QUERY)
            data = cur.fetchall()
            cur.close()
        except Exception as ex:
            log.error(f"Errore GET_SCENE_GROUP_JOIN: {ex}")
        finally:
            if conn:
                conn.close()
        return data

    # def GET_DEVICE_TYPES(self):
    #     """Restituisce l'insieme dei tipi unici di device (colonna TYPE) dalla tabella DEVICE. Thread-safe."""
    #     types = set()
    #     conn = None
    #     try:
    #         conn = mariadb.connect(**self.conn_params)
    #         cur = conn.cursor()
    #         cur.execute("SELECT DISTINCT TYPE FROM DEVICE WHERE TYPE IS NOT NULL AND TYPE != ''")
    #         for row in cur.fetchall():
    #             if row[0]:
    #                 types.add(row[0])
    #     except Exception as ex:
    #         log.error(f"Errore GET_DEVICE_TYPES: {ex}")
    #     finally:
    #         if conn:
    #             conn.close()
    #     return types

    def GET_DEVICE_AND_INFO_COLUMNS(self):
        """Restituisce l'unione delle colonne di DEVICE e DEVICE_INFO tramite SQL."""
        columns = []
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            # Ottieni tutte le colonne da information_schema.COLUMNS in una sola QUERY
            cur.execute(
                """
                SELECT TABLE_NAME, COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = 'Home'
                AND TABLE_NAME IN ('DEVICE', 'DEVICE_INFO')
                ORDER BY FIELD(TABLE_NAME, 'DEVICE', 'DEVICE_INFO')
                """
            )
            columns = cur.fetchall()
        except Exception as ex:
            log.error(f"Errore GET_DEVICE_AND_INFO_COLUMNS: {ex}")
            columns = []
        finally:
            if conn:
                conn.close()
        return columns

    def GET_DEVICE_AND_INFO_COL(self):
        """Restituisce l'unione delle colonne di DEVICE e DEVICE_INFO tramite SQL."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            # Ottieni tutte le colonne da information_schema.COLUMNS in una sola QUERY
            cur.execute(
                """
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = 'Home'
                AND TABLE_NAME IN ('DEVICE', 'DEVICE_INFO')
                ORDER BY FIELD(TABLE_NAME, 'DEVICE', 'DEVICE_INFO')
                """
            )
            columns = cur.fetchall()
            columns_dict = {col[0]: None for col in columns}
        except Exception as ex:
            log.error(f"Errore GET_DEVICE_AND_INFO_COL: {ex}")
        finally:
            if conn:
                conn.close()
        return columns_dict

    def GET_DEVICE_AND_INFO_DATA(self, alias=False):
        """Restituisce tuple: (columns, data) con dati uniti di DEVICE e DEVICE_INFO (LEFT JOIN). Se alias=True, usa alias per colonne duplicate. Thread-safe."""
        data = []
        columns = []
        conn = None
        try:
            raw_columns = self.GET_DEVICE_AND_INFO_COLUMNS()
            if not raw_columns:
                return columns, data
            col_count = {}
            select_cols = []
            columns = []
            for tbl, col in raw_columns:
                key = col.lower()
                if alias:
                    # Se la colonna è già presente, aggiungi alias
                    if key in col_count:
                        col_count[key] += 1
                        alias_name = f"{tbl}_{col}".upper()
                        select_cols.append(f"{tbl}.{col} AS {alias_name}")
                        columns.append(alias_name)
                    else:
                        col_count[key] = 1
                        select_cols.append(f"{tbl}.{col} AS {col}")
                        columns.append(col)
                else:
                    select_cols.append(f"{tbl}.{col}")
                    columns.append(col)
            QUERY = f"SELECT {', '.join(select_cols)} FROM DEVICE LEFT JOIN DEVICE_INFO ON DEVICE.ID_KEY = DEVICE_INFO.ID_KEY"
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            cur.execute(QUERY)
            data = cur.fetchall()
            cur.close()
        except Exception as ex:
            log.error(f"Errore GET_DEVICE_AND_INFO_DATA: {ex}")
        finally:
            if conn:
                conn.close()
        return columns, data

    def UPDATE_DEVICE_INFO_BY_FRIENDLY_NAME(self, friendly_name, posizione, nome, piano, level):
        """Aggiorna la tabella DEVICE_INFO dato il FRIENDLY_NAME del device. Thread-safe."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            # Trova l'ID_KEY del device tramite FRIENDLY_NAME
            cur.execute("SELECT ID_KEY FROM DEVICE WHERE FRIENDLY_NAME = %s", (friendly_name,))
            res = cur.fetchone()
            if not res:
                return False
            id_key = res[0]
            # Aggiorna la tabella DEVICE_INFO
            cur.execute("UPDATE DEVICE_INFO SET POSITION = %s, NAME = %s, FLOOR = %s, LEVEL = %s WHERE ID_KEY = %s", (posizione, nome, piano, level, id_key))
            conn.commit()
            cur.close()
            return True
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
        except Exception as ex:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {ex}")
        finally:
            if conn:
                conn.close()
        return False

    def INS_TAB_DATA(self, topic, data):
        """Insert data in a table. Thread-safe. Usa 'with' per connessione/cursore."""
        try:
            now = datetime.now()
            self.UP_TAB_ZIG(topic, data)
            fields = []
            values = [now.date(), now.strftime("%H:%M:%S")]
            for x in data:
                col_name = x.upper()
                val = data[x]
                if isinstance(val, (int, float, str, bool)):
                    fields.append(col_name)
                    values.append(val)
                else:
                    log.debug(f"INS_TAB_DATA: campo {col_name} tipo non supportato ({type(val)})")
            if not fields:
                log.warning(f"INS_TAB_DATA: nessun campo valido da inserire per la tabella {topic.upper()}. Query non eseguita.")
                return
            QUERY = f"INSERT INTO `{topic.upper()}` (DAY_U, TIME_U, {', '.join(fields)}) VALUES ({', '.join(['%s'] * len(values))})"
            with mariadb.connect(**self.conn_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(QUERY, values)
                    conn.commit()
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg} - topic {topic}")
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg} - topic {topic}")

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

    def GET_DEVICE_INFO(self, table_name: str):
        """Restituisce il numero di righe di una tabella e gli insiemi di vendor e model unici se la tabella è DEVICE."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            result = cur.fetchone()
            count = result[0] if result else 0

            unique_vendors = set()
            unique_models = set()

            cur.execute(f"SELECT VENDOR, MODEL FROM `{table_name}`")
            for row in cur.fetchall():
                vendor, model = row
                if vendor:
                    unique_vendors.add(vendor)
                if model:
                    unique_models.add(model)
            cur.close()
            return count, unique_vendors, unique_models
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
            return 0, set(), set()
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return 0, set(), set()
        finally:
            if conn:
                conn.close()

    def GET_DEVICES_INFO_BY_LEVEL(self):
        """Restituisce un dizionario raggruppato per LEVEL: {level: [devices]}."""
        session = self.SessionMaker()
        results = {}
        try:
            # 1. Query principale con LEFT JOIN tra DEVICE e DEVICE_INFO
            # Selezioniamo esplicitamente le due tabelle. SQLAlchemy farà la join basandosi sulla FK.
            query_base = (
                select(TabellaDevice, TabellaDeviceInfo)
                .outerjoin(TabellaDeviceInfo, TabellaDevice.ID_KEY == TabellaDeviceInfo.ID_KEY)
                .order_by(TabellaDeviceInfo.LEVEL, TabellaDevice.FRIENDLY_NAME)
            )
            
            db_rows = session.execute(query_base).all()

            for dev_obj, info_obj in db_rows:
                # Componiamo il dizionario del device emulando il vecchio comportamento
                device = {
                    "ID_KEY": dev_obj.ID_KEY,
                    "FRIENDLY_NAME": dev_obj.FRIENDLY_NAME,
                    "IEEE_ADDRESS": dev_obj.IEEE_ADDRESS,
                    "TYPE": dev_obj.TYPE,
                    "DESCRIPTION": dev_obj.DESCRIPTION if dev_obj.DESCRIPTION else "",
                    "MODEL": dev_obj.MODEL if dev_obj.MODEL else "",
                    "VENDOR": dev_obj.VENDOR if dev_obj.VENDOR else "",
                    "MANUFACTURER": dev_obj.MANUFACTURER if dev_obj.MANUFACTURER else "",
                    "MODEL_ID": dev_obj.MODEL_ID if dev_obj.MODEL_ID else "",
                    "POWER_SOURCE": dev_obj.POWER_SOURCE if dev_obj.POWER_SOURCE else "",
                    # Dati provenienti da DEVICE_INFO (gestendo il caso in cui la riga info non esista)
                    "POSITION": info_obj.POSITION if info_obj and info_obj.POSITION else "",
                    "NAME": info_obj.NAME if info_obj and info_obj.NAME else "",
                    "FLOOR": info_obj.FLOOR if info_obj and info_obj.FLOOR else "",
                    "LEVEL": info_obj.LEVEL if info_obj and info_obj.LEVEL is not None else None,
                    "data": {} # Contenitore per gli ultimi dati runtime
                }

                friendly_name = device.get('FRIENDLY_NAME')
                
                # 2. 👁️ Tenta di recuperare gli ultimi dati dalla tabella specifica del device
                if friendly_name and friendly_name != 'Coordinator':
                    try:
                        try:
                            table_name = friendly_name.split('/')[1].upper()
                        except IndexError:
                            table_name = friendly_name.upper()

                        # Query testuale per estrarre l'ultimo record della tabella dinamica
                        q_data = text(f"SELECT * FROM `{table_name}` ORDER BY ID_KEY DESC LIMIT 1")
                        res_data = session.execute(q_data).mappings().first()
                        
                        if res_data:
                            # Convertiamo i dati in un dizionario standard modificabile
                            dict_data = dict(res_data)
                            
                            # Convertiamo eventuali oggetti Date/Time in stringhe per l'interfaccia grafica
                            for k, v in dict_data.items():
                                # 🌟 CONTROLLO CORRETTO E COMPLETO: 
                                type_str = type(v).__name__

                                # 1. Gestione dei Timestamps (datetime)
                                if type_str == 'datetime':
                                    dict_data[k] = v.strftime("%Y-%m-%d %H:%M:%S")
                                    
                                # 2. Gestione delle Date (date)
                                elif type_str == 'date':
                                    dict_data[k] = v.strftime("%Y-%m-%d")
                                    
                                # 3. Gestione del Tempo puro (time)
                                elif type_str == 'time':
                                    dict_data[k] = v.strftime("%H:%M:%S")
                                    
                                # 4. 🌟 Gestione dell'intervallo MariaDB (timedelta) - QUELLO CHE TI BLOCCAVA!
                                elif type_str == 'timedelta':
                                    # v.total_seconds() nel tuo caso restituisce 75600.0
                                    tot_seconds = int(v.total_seconds())
                                    hours = tot_seconds // 3600
                                    minutes = (tot_seconds % 3600) // 60
                                    seconds = tot_seconds % 60
                                    dict_data[k] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                            device['data'] = dict_data

                    except Exception:
                        log.error(f"❌ Impossibile recuperare dati per il dispositivo '{friendly_name}'. Tabella inesistente o errore nella QUERY.")

                # 3. Raggruppamento finale nel dizionario dei risultati per LEVEL
                level = device.get('LEVEL')                   
                if level not in results:
                    results[level] = []
                results[level].append(device)

            return results

        except SQLAlchemyError as e:
            log.error(f"❌ Errore SQLAlchemy in GET_DEVICES_INFO_BY_LEVEL: {e}")
            return {}
        except Exception as e:
            log.error(f"🆘 Errore generico Python in GET_DEVICES_INFO_BY_LEVEL: {e}")
            return {}
        finally:
            session.close()







    def GET_TABLE_CONS(self, table_name: str, day, interval_min: int = 15):
        """Restituisce la media di POWER_A ogni 'interval_min' minuti per la data richiesta."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            # Raggruppa per blocchi di interval_min minuti, calcola la media di POWER_A
            QUERY = (
    #            f"SELECT "
    #            f"DATE_FORMAT( "
    #            f"SEC_TO_TIME( "
    #            f"FLOOR(TIME_TO_SEC(TIME_U) / ({interval_min} * 60)) * ({interval_min} * 60)), '%H:%i:00') AS time_group, "
    #            f"AVG(POWER_A) AS avg_power "
    #            f"FROM `{table_name}` "
    #            f"WHERE DAY_U = '{day}' "
   #             f"GROUP BY time_group "
   #             f"ORDER BY time_group"

                f"SELECT DATE_FORMAT( DATE_SUB( CONCAT(DAY_U, ' ', TIME_U), INTERVAL (MINUTE(TIME_U) % {interval_min}) MINUTE ), '%H:%i:00' ) as time_group, "
                f"AVG(POWER_A) as avg_power "
                f"FROM `{table_name}` "
                f"WHERE DAY_U = '{day}'"

# f"AND ENERGY_FLOW_A = 'producing' AND ENERGY_FLOW_B = 'producing' "

                f"GROUP BY time_group "
                f"ORDER BY time_group"
            )
            cur.execute(QUERY)
            data = cur.fetchall()
            cur.close()
            return data if data else []
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
            return []
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return []
        finally:
            if conn:
                conn.close()

    def GET_CHART_PROD(self, table_name, start, end):
        """Restituisce dati aggregati per grafico (media consumi ogni 5 minuti). Thread-safe."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            QUERY = (
                f"SELECT DAY_U AS Data,"
                f"SEC_TO_TIME(TIME_TO_SEC(TIME_U) - (TIME_TO_SEC(TIME_U) % 300)) AS Media_T,"
                f"TRUNCATE(AVG(POWER_AB), 1) AS Media_Power_AB "
                f"FROM {table_name} "
                f"WHERE DAY_U BETWEEN '{start}' AND '{end}' "
                f"GROUP BY DAY_U, Media_T "
                f"ORDER BY DAY_U ASC, Media_T ASC;"
            )
            cur = conn.cursor()
            cur.execute(QUERY)
            DATA = cur.fetchall()
            cur.close()
            return DATA if DATA else []
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
            return []
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return []
        finally:
            if conn:
                conn.close()
    
    def GET_CHART_1(self, table_name, start, end):
        """Restituisce dati aggregati per grafico (media temperatura e umidità ogni 5 minuti). Thread-safe."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            # Utilizziamo una serie numerica (seq_0_to_287) per generare tutti gli slot da 5 min (24h * 12 = 288 slot)
            QUERY = (
                f"WITH RECURSIVE seq_0_to_287 AS ( "
                f"  SELECT 0 AS num "
                f"  UNION ALL "
                f"  SELECT num + 1 FROM seq_0_to_287 WHERE num < 287 "
                f"), "
                f"  time_slots AS ( "
                f"  SELECT "
                f"    DATE_ADD('{start}', INTERVAL num * 5 MINUTE) AS slot_time "
                f"  FROM seq_0_to_287 "
                f"  WHERE DATE_ADD('{start}', INTERVAL num * 5 MINUTE) <= NOW() "
                f") "
                f"SELECT "
                f"  '{start}' AS DAY_U, "
                f"  DATE_FORMAT(ts.slot_time, '%H:%i:00') AS 5min, "
                f"  TRUNCATE(AVG(t.TEMPERATURE), 1) AS Avg_T, "
                f"  TRUNCATE(AVG(t.HUMIDITY), 1) AS Avg_H "
                f"FROM time_slots ts "
                f"LEFT JOIN `{table_name}` t "
                f"  ON t.DAY_U = '{start}' "
                f"  AND t.TIME_U >= DATE_FORMAT(ts.slot_time, '%H:%i:00') "
                f"  AND t.TIME_U < DATE_FORMAT(DATE_ADD(ts.slot_time, INTERVAL 5 MINUTE), '%H:%i:00') "
                f"GROUP BY ts.slot_time "
                f"ORDER BY ts.slot_time"
            )
            cur = conn.cursor()
            cur.execute(QUERY)
            DATA = cur.fetchall()
            cur.close()
            
            # Post-processing in Python per riempire i buchi (interpolazione lineare)
            filled_data = []
            
            # Funzione di supporto per trovare il prossimo valore non nullo
            def get_next_valid(data, start_idx, col_idx):
                for i in range(start_idx, len(data)):
                    if data[i][col_idx] is not None:
                        return float(data[i][col_idx]), i
                return None, None

            first_t, _ = get_next_valid(DATA, 0, 2)
            first_h, _ = get_next_valid(DATA, 0, 3)

            for i in range(len(DATA)):
                row = DATA[i]
                
                # Temperatura
                t_val = float(row[2]) if row[2] is not None else None

                # Umidità / Soil (colonna 3)
                h_val = float(row[3]) if row[3] is not None else None
                
                # Arrotonda per sicurezza e pulizia se presenti
                if t_val is not None: t_val = round(t_val, 2)
                if h_val is not None: h_val = round(h_val, 2)
                
                filled_data.append((row[0], row[1], t_val, h_val))
            
            return filled_data
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
            return []
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return []
        finally:
            if conn:
                conn.close()
            
    def GET_CHART_2(self, table_name, start, end):
        """Restituisce dati aggregati per grafico (media temperatura e soil_moisture ogni 5 minuti). Thread-safe."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            QUERY = (
                f"WITH RECURSIVE seq_0_to_287 AS ( "
                f"  SELECT 0 AS num "
                f"  UNION ALL "
                f"  SELECT num + 1 FROM seq_0_to_287 WHERE num < 287 "
                f"), "
                f"  time_slots AS ( "
                f"  SELECT "
                f"    DATE_ADD('{start}', INTERVAL num * 5 MINUTE) AS slot_time "
                f"  FROM seq_0_to_287 "
                f"  WHERE DATE_ADD('{start}', INTERVAL num * 5 MINUTE) <= NOW() "
                f") "
                f"SELECT "
                f"  '{start}' AS DAY_U, "
                f"  DATE_FORMAT(ts.slot_time, '%H:%i:00') AS 5min, "
                f"  TRUNCATE(AVG(t.TEMPERATURE), 1) AS Avg_T, "
                f"  TRUNCATE(AVG(t.SOIL_MOISTURE), 1) AS Avg_H "
                f"FROM time_slots ts "
                f"LEFT JOIN `{table_name}` t "
                f"  ON t.DAY_U = '{start}' "
                f"  AND t.TIME_U >= DATE_FORMAT(ts.slot_time, '%H:%i:00') "
                f"  AND t.TIME_U < DATE_FORMAT(DATE_ADD(ts.slot_time, INTERVAL 5 MINUTE), '%H:%i:00') "
                f"GROUP BY ts.slot_time "
                f"ORDER BY ts.slot_time"
            )
            cur = conn.cursor()
            cur.execute(QUERY)
            DATA = cur.fetchall()
            cur.close()
            
            # Interpolazione lineare
            filled_data = []
            
            # Funzione di supporto per trovare il prossimo valore non nullo
            def get_next_valid(data, start_idx, col_idx):
                for i in range(start_idx, len(data)):
                    if data[i][col_idx] is not None:
                        return float(data[i][col_idx]), i
                return None, None

            first_t, _ = get_next_valid(DATA, 0, 2)
            first_s, _ = get_next_valid(DATA, 0, 3)

            for i in range(len(DATA)):
                row = DATA[i]
                
                # Temperatura
                t_val = float(row[2]) if row[2] is not None else None

                # Soil (colonna 3)
                s_val = float(row[3]) if row[3] is not None else None
                
                # Arrotonda per sicurezza e pulizia se presenti
                if t_val is not None: t_val = round(t_val, 2)
                if s_val is not None: s_val = round(s_val, 2)
                
                filled_data.append((row[0], row[1], t_val, s_val))
            
            return filled_data
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
            return []
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return []
        finally:
            if conn:
                conn.close()

    def UP_TAB_CHATID(self, username, user_id, chat_id):
        """Aggiorna o inserisce un utente nella tabella USER. Thread-safe."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            QUERY = (
                "INSERT INTO USER_CHATID (USERNAME, USER_ID, CHAT_ID) "
                "VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE USERNAME=VALUES(USERNAME)"
            )
            cur.execute(QUERY, (username, user_id, chat_id))
            conn.commit()
            cur.close()
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
        finally:
            if conn:
                conn.close()





   
    def UP_TAB_SCHEDULE(self, id, name, data):
        """Aggiorna o inserisce una schedulazione nella tabella SCHEDULE. Thread-safe."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            if id is None:
                cur.execute("INSERT INTO SCHEDULE (NAME, DATA) VALUES (%s, %s)", (name, json.dumps(data)))
            else:
                cur.execute("UPDATE SCHEDULE SET DATA = %s WHERE ID = %s", (json.dumps(data), id))  
            conn.commit()
            cur.close()
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
        finally:
            if conn:
                conn.close()

    def GET_TAB_SCHEDULE(self):
        """Recupera tutte le schedulazioni dalla tabella SCHEDULE come lista di dict. Thread-safe."""
        conn = None
        schedules = []
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            QUERY = "SELECT ID, NAME, DATA FROM SCHEDULE"
            cur.execute(QUERY)
            for id, name, data in cur.fetchall():
                schedules.append({"id": id, "name": name, "data": json.loads(data)})
            cur.close()
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
        finally:
            if conn:
                conn.close()
        return schedules

    def DEL_TAB_SCHEDULE(self, id):
        """Elimina una schedulazione dalla tabella SCHEDULE. Thread-safe."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            cur.execute("DELETE FROM SCHEDULE WHERE ID = %s", (id,))
            conn.commit()
            cur.close()
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
        finally:
            if conn:
                conn.close()

    def GET_DEVICE_AND_INFO_BY_IEEE(self, ieee_address):
        """Restituisce i dati uniti di DEVICE e DEVICE_INFO per uno specifico ieee_address."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            with conn.cursor() as cur:
                QUERY = (
                    "SELECT DEVICE.*, DEVICE_INFO.POSITION, DEVICE_INFO.NAME, DEVICE_INFO.FLOOR, DEVICE_INFO.LEVEL "
                    "FROM DEVICE "
                    "LEFT JOIN DEVICE_INFO ON DEVICE.ID_KEY = DEVICE_INFO.ID_KEY "
                    "WHERE DEVICE.IEEE_ADDRESS = %s"
                )
                cur.execute(QUERY, (ieee_address,))
                result = cur.fetchone()
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, result)) if result else None
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
            return None
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return None
        finally:
            if conn:
                conn.close()

    def GET_KEY_DEVICE(self, ieee_address):
        """Restituisce l'ID_KEY di un dispositivo dato il suo ieee_address."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            cur.execute("SELECT ID_KEY FROM DEVICE WHERE IEEE_ADDRESS = %s", (ieee_address,))
            result = cur.fetchone()
            cur.close()
            return result[0] if result else None
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
            return None
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return None
        finally:
            if conn:
                conn.close()

    def UP_DEVICE_INFO(self, id_key, posizione=None, nome=None, piano=None, level=None):
        """Aggiorna le informazioni del dispositivo nella tabella DEVICE_INFO dato l'ID_KEY."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor()
            fields = []
            values = []
            if posizione is not None:
                fields.append("POSITION = %s")
                values.append(posizione)
            if nome is not None:
                fields.append("NAME = %s")
                values.append(nome)
            if piano is not None:
                fields.append("FLOOR = %s")
                values.append(piano)
            if level is not None:
                fields.append("LEVEL = %s")
                values.append(level)
            if not fields:
                return False  # Nessun campo da aggiornare
            values.append(id_key)
            QUERY = f"UPDATE DEVICE_INFO SET {', '.join(fields)} WHERE ID_KEY = %s"
            cur.execute(QUERY, values)
            conn.commit()
            cur.close()
            return True
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
            return False
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return False
        finally:
            if conn:
                conn.close()


    def GET_ENEL(self, table_name, data):
        """Restituisce i dati di consumo Enel se disponibili."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor(dictionary=True)                      #   👀  Per avere i risultati come dizionario
            QUERY = "SELECT ROUND(COALESCE(MAX(ENERGY_A) - MIN(ENERGY_A), 0), 2) AS 'prelievo', " 
            QUERY += "ROUND(COALESCE(MAX(ENERGY_PRODUCED_A) - MIN(ENERGY_PRODUCED_A), 0), 2) AS 'immissione', " 
            QUERY += "ROUND(COALESCE(MAX(ENERGY_PRODUCED_B) - MIN(ENERGY_PRODUCED_B), 0), 2) AS 'produzione', " 
            QUERY += "ROUND(COALESCE((MAX(ENERGY_A) - MIN(ENERGY_A)) + ((MAX(ENERGY_PRODUCED_B) - MIN(ENERGY_PRODUCED_B)) - (MAX(ENERGY_PRODUCED_A) - MIN(ENERGY_PRODUCED_A))), 0), 2) AS 'consumo' " 
            QUERY += f"FROM `{table_name}` "
            QUERY += f"WHERE DATE(timestamp_a) = '{data}';"

            cur.execute(QUERY)
            DATA = cur.fetchall()
            cur.close()
            return DATA if DATA else []
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
            return []
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return []
        finally:
            if conn:
                conn.close()

    def GET_ENEL_HISTORY(self, table_name):
        """Restituisce lo storico dei consumi degli ultimi 30 giorni."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            cur = conn.cursor(dictionary=True)
            # Query che raggruppa per giorno gli ultimi 30 giorni
            QUERY = "SELECT DATE(timestamp_a) as giorno, "
            QUERY += "ROUND(COALESCE(MAX(ENERGY_A) - MIN(ENERGY_A), 0), 2) AS prelievo, "
            QUERY += "ROUND(COALESCE(MAX(ENERGY_PRODUCED_B) - MIN(ENERGY_PRODUCED_B), 0), 2) AS produzione, "
            QUERY += "ROUND(COALESCE(MAX(ENERGY_PRODUCED_A) - MIN(ENERGY_PRODUCED_A), 0), 2) AS 'immissione' "
            QUERY += f"FROM `{table_name}` "
            QUERY += "WHERE timestamp_a >= DATE_SUB(NOW(), INTERVAL 30 DAY) "
            QUERY += "GROUP BY DATE(timestamp_a) "
            QUERY += "ORDER BY giorno ASC;"
            cur.execute(QUERY)
            DATA = cur.fetchall()
            cur.close()
            return DATA if DATA else []
        except Exception as e:
            log.error(f"Errore storico: {e}")
            return []
        finally:
            if conn: conn.close()

    def GET_MB(self):
        """Restituisce la dimensione del database in MB."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_schema AS Database,
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    GROUP BY table_schema;
                """, (self.conn_params.get('database'),))
                result = cur.fetchall()
                return result if result else []
        except mariadb.Error as msg:
            log.error(f"SQL {ins.currentframe().f_code.co_name}: {msg}")
            return []
        except Exception as msg:
            log.error(f"🆘 Python {ins.currentframe().f_code.co_name}: {msg}")
            return []
        finally:
            if conn:
                conn.close()

    def DELL_ROW_NULL(self, table_name, column_name):
        """Elimina tutte le righe dalla tabella specificata dove la colonna indicata è NULL."""
        conn = None
        try:
            conn = mariadb.connect(**self.conn_params)
            with conn.cursor() as cur:
                QUERY = f"DELETE FROM `{table_name}` WHERE `{column_name}` IS NULL"
                cur.execute(QUERY)
                conn.commit()
                log.info(f"Righe eliminate da {table_name} dove {column_name} è NULL.")
        except Exception as e:
            log.error(f"Errore eliminazione righe NULL: {e}")
        finally:
            if conn:
                conn.close()





class CALENDAR():
    """Classe per la gestione del calendario e delle festività italiane."""
    def __init__(self, ICAL_URL = None, periodo = 90):
        self.ICAL_URL = ICAL_URL
        self.periodo = periodo
    
    def leggi_calendario(self):
        """Scarica, analizza e restituisce gli eventi del calendario, espandendo anche le ricorrenze (RRULE)."""
        from dateutil.rrule import rrulestr
        eventi = []
        try:
            risposta = requests.get(self.ICAL_URL)
            risposta.raise_for_status() # Verifica che il download sia andato a buon fine
            gcal = Calendar.from_ical(risposta.content)
            
            # Cerca di estrarre il nome del calendario, così se non c'è l'organizzatore usiamo questo
            cal_name = str(gcal.get('X-WR-CALNAME', 'Sconosciuto'))
            
            anno_corrente = datetime.now().year
            import zoneinfo
            tz_rome = zoneinfo.ZoneInfo("Europe/Rome")
            for componente in gcal.walk():
                if componente.name == "VEVENT":
                    sommario = str(componente.get('summary'))
                    inizio = componente.get('dtstart').dt
                    fine_raw = componente.get('dtend')
                    fine = fine_raw.dt if fine_raw else None
                    rrule = componente.get('RRULE')
                    location_raw = componente.get('location')
                    posizione = str(location_raw) if location_raw else ""
                    desc_raw = componente.get('description')
                    descrizione = str(desc_raw) if desc_raw else ""
                    
                    # --- INIZIO PROVA DA ELIMINARE ---
            #        try:
            #            raw_ical = componente.to_ical().decode('utf-8', errors='ignore')
            #            if "antonella" in raw_ical.lower() or "federico" in raw_ical.lower():
            #                log.info(f"💡 TROVATO IN EVENTO: '{sommario}'")
            #                for k, v in componente.items():
            #                    if "antonella" in str(v).lower() or "federico" in str(v).lower():
            #                        log.info(f"   -> TROVATO NEL CAMPO: {k} = {v}")
            #                        if hasattr(v, 'params'):
            #                            log.info(f"      -> PARAMS: {v.params}")
            #    except Exception as e:
            #            pass
                    # --- FINE PROVA DA ELIMINARE ---

                    creator_raw = componente.get('creator')
                    organizer_raw = componente.get('organizer')
                    
                    creatore = ""
                    # 1. Prova a estrarre l'autore dal campo CREATOR (molto usato nei calendari condivisi Google per indicare chi ha creato l'evento)
                    if creator_raw:
                        creatore = str(creator_raw).replace('mailto:', '').replace('MAILTO:', '')
                        
                    # 2. Se non c'è CREATOR, prova dal campo ORGANIZER
                    if not creatore and organizer_raw:
                        if hasattr(organizer_raw, 'params') and 'CN' in organizer_raw.params:
                            creatore = str(organizer_raw.params['CN'])
                        else:
                            creatore = str(organizer_raw).replace('mailto:', '').replace('MAILTO:', '')
                    
                    # 3. Fallback finale se vuoto o se è l'indirizzo irriconoscibile del gruppo Google
                    if not creatore or "group.calendar.google.com" in creatore:
                        creatore = cal_name
                        
                    # Formatta: se è un'email, prendi solo il nome (es: mario.rossi@gmail.com -> mario.rossi)
                    if "@" in creatore and not "group.calendar" in creatore:
                        creatore = creatore.split("@")[0]
                    # Gestione fusi orari/formato data
                    def to_rome(dt):
                        if isinstance(dt, datetime):
                            if dt.tzinfo is None:
                                # Assume UTC se naive (o cambia qui se vuoi altro default)
                                dt = dt.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                            return dt.astimezone(tz_rome)
                        return dt
                    def format_data(dt):
                        if isinstance(dt, datetime):
                            return to_rome(dt).strftime('%d/%m/%Y %H:%M')
                        else:
                            return dt.strftime('%d/%m/%Y (Tutto il giorno)')

                    if rrule:
                        # Espandi le ricorrenze future (prossimi 30 giorni)
                        rrule_parts = []
                        for k, v in rrule.items():
                            rrule_parts.append(f"{k}={','.join(map(str, v))}")
                        rrule_str = ';'.join(rrule_parts)
                        try:
                            rule = rrulestr(rrule_str, dtstart=inizio)
                            # Gestione naive/aware
                            if isinstance(inizio, datetime) and inizio.tzinfo is not None:
                                now = datetime.now(inizio.tzinfo)
                                limit = now + timedelta(days=self.periodo)
                            else:
                                now = datetime.now()
                                limit = now + timedelta(days=self.periodo)
                            
                            start_eval = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
                            
                            for ev_date in rule.between(start_eval, limit, inc=True):
                                ev_date_rome = to_rome(ev_date)
                                if (isinstance(ev_date_rome, datetime) and ev_date_rome.year == anno_corrente) or \
                                   (not isinstance(ev_date_rome, datetime) and hasattr(ev_date_rome, "year") and ev_date_rome.year == anno_corrente):
                                    # Calcola la vera fine_rome per l'evento ricorrente
                                    fine_rome = None
                                    if fine:
                                        if isinstance(fine, datetime):
                                            # La vera fine è l'inizio corrente + la durata originale
                                            durata = fine - inizio
                                            vera_fine = ev_date_rome + durata
                                            if vera_fine.tzinfo is None:
                                                vera_fine = vera_fine.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                            fine_rome = vera_fine.astimezone(tz_rome)
                                        else:
                                            # Se `fine` non è datetime (es. date), si applica la logica per tutto il giorno
                                            durata = fine - inizio.date() if isinstance(inizio, datetime) else fine - inizio
                                            fine_rome = ev_date_rome.date() + durata if isinstance(ev_date_rome, datetime) else ev_date_rome + durata
                                    eventi.append({
                                        "titolo": sommario,
                                        "inizio": ev_date_rome,
                                        "fine": fine_rome,
                                        "data_formattata_inizio": format_data(ev_date_rome),
                                        "data_formattata_fine": format_data(fine_rome) if fine_rome else "",
                                        "descrizione": descrizione,
                                        "creatore": creatore,
                                        "posizione": posizione,
                                        "scaduto": (fine_rome < datetime.now(tz_rome).date() if not isinstance(fine_rome, datetime) else fine_rome < datetime.now(tz_rome)) if fine_rome else (ev_date_rome < datetime.now(tz_rome).date() if not isinstance(ev_date_rome, datetime) else ev_date_rome < datetime.now(tz_rome))
                                    })
                        except Exception as e:
                            log.error(f"Errore espansione RRULE: {e}")
                    else:
                        # Evento singolo
                        # Se è un evento tipo "Tutto il giorno", dtstart.dt sarà di tipo date, non datetime.
                        # Tuttavia convertiamolo in datetime_rome solo in caso lo sia
                        if isinstance(inizio, datetime):
                            inizio_rome = to_rome(inizio)
                        else:
                            inizio_rome = inizio
                            
                        fine_rome = None
                        if fine:
                            if isinstance(fine, datetime):
                                if fine.tzinfo is None:
                                    fine = fine.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                fine_rome = to_rome(fine)
                            else:
                                fine_rome = fine
                                
                        if (isinstance(inizio_rome, datetime) and inizio_rome.year == anno_corrente) or \
                           (not isinstance(inizio_rome, datetime) and hasattr(inizio_rome, "year") and inizio_rome.year == anno_corrente):
                            eventi.append({
                                "titolo": sommario,
                                "inizio": inizio_rome,
                                "fine": fine_rome,
                                "data_formattata_inizio": format_data(inizio_rome),
                                "data_formattata_fine": format_data(fine_rome) if fine_rome else "",
                                "creatore": creatore,
                                "descrizione": descrizione,
                                "posizione": posizione,
                                "scaduto": (fine_rome < datetime.now(tz_rome).date() if not isinstance(fine_rome, datetime) else fine_rome < datetime.now(tz_rome)) if fine_rome else (inizio_rome < datetime.now(tz_rome).date() if not isinstance(inizio_rome, datetime) else inizio_rome < datetime.now(tz_rome))
                            })

            # Ordina gli eventi in base alla data di inizio (convertendo le Date in Datetime temporaneamente per l'ordine)
            def get_sort_key(x):
                dt = x["inizio"]
                if isinstance(dt, datetime):
                    return dt.replace(tzinfo=None)
                return datetime.combine(dt, datetime.min.time())

            eventi_filtrati = []
            # Gestione naive/aware anche per il filtro finale
            if eventi:
                first = eventi[0]["inizio"]
                if isinstance(first, datetime) and first.tzinfo is not None:
                    now_naive = datetime.now(first.tzinfo)
                    limit_naive = now_naive + timedelta(days=self.periodo)
                else:
                    now_naive = datetime.now()
                    limit_naive = now_naive + timedelta(days=self.periodo)
            else:
                now_naive = datetime.now()
                limit_naive = now_naive + timedelta(days=self.periodo)
            
            inizio_settimana = now_naive - timedelta(days=now_naive.weekday())
            inizio_settimana_date = inizio_settimana.date()

            for ev in eventi:
                inizio_naive = get_sort_key(ev)
                if inizio_settimana_date <= inizio_naive.date() <= limit_naive.date():
                    eventi_filtrati.append(ev)

            eventi_filtrati.sort(key=get_sort_key)

        #    for idx, ev in enumerate(eventi_filtrati):
        #        log.info(f"Evento {idx + 1}: {ev['titolo']} - Creatore: {ev['creatore']} - Inizio: {ev.get('data_formattata_inizio','')} - Fine: {ev.get('data_formattata_fine','')}")

            return eventi_filtrati

        except Exception as e:
            log.error(f"Errore durante la lettura del calendario: {e}")
            return []

#   -----   👀  MAIN APP                    👀  -----   #
if __name__ == '__main__':
    pass