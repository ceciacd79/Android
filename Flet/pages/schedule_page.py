import os
import json as _json
# -*- coding: utf-8 -*-
"""
Schedule Page - Gestione degli scheduler per azioni e scene predefinite. Permette di creare, modificare ed eliminare schedulazioni basate su orari, giorni della settimana e condizioni specifiche. Integra un sistema di dialoghi per la configurazione dettagliata di ogni schedule, con supporto per payload dinamici e interazione con il database per la persistenza dei dati.
"""

import flet as ft
import logging
import inspect as ins

from common.config import RESPONSIVE_COLS
from common.helpers import get_theme_color
from common.ui import show_login_dialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

log = logging.getLogger(__name__)

loc_schedule = []
loc_actions = []
loc_scene = []
loc_table = []
loc_groups = []
no_topic = ['ACTIONS', 'ALLARME', 'DEVICE', 'DEVICE_INFO', 'GRUPPI', 'MODO', 'SCENE', 'SCHEDULE', 'USER_CHATID']

def get_content(app: 'App', title: str = "Home Page") -> ft.Column:
    # Badge login rimosso per compatibilità
    """ Restituisce il contenuto della pagina Home"""
    global loc_schedule
    global loc_actions
    global loc_table
    global loc_scene

    from components.TitleCard import TitleCard

    editing_schedule = {}                                                       #   ℹ️   Mantiene traccia dell'elemento in modifica
    item_to_delete = None

    key_act = app.settings.get("key_act", [])
    key_sql = app.settings.get("key_sql", [])
    key_rooms = app.settings.get("key_rooms", [])
    key_floor = app.settings.get("key_floor", [])
   
    loc_schedule = app.schedule if hasattr(app, "schedule") else []
    loc_actions = app.action if hasattr(app, "action") else []
    loc_scene = app.scene if hasattr(app, "scene") else []
    loc_groups = app.groups if hasattr(app, "groups") else []
    
    _all_tables = app.table if hasattr(app, "table") else []
    # Filtro: esclude i nomi di tabella presenti in no_topic (supporta sia stringhe semplici che tuple)
    loc_table = [t[0] if isinstance(t, tuple) else t for t in _all_tables if (t[0] if isinstance(t, tuple) else t) not in no_topic]

    #   -----   👀  FUNZIONI INTERNE                👀  -----   #
    def reload_page(e=None):
        """Ricarica la pagina Schedule aggiornando i dati e la UI."""
        if hasattr(app, 'pages_cache') and app.current_page_index in app.pages_cache:
            del app.pages_cache[app.current_page_index]
        app.content_container.content = get_content(app, title)
        app.content_container.update()
    
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
        # Filtra eventi solo per la pagina attiva
        if app.current_page_index != 5:
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

    def New_time():
        if not dlg_time.value:
            return
        else:
            update_payload()

    def New_end_time():
        if not dlg_time_end.value:
            return
        else:
            update_payload()

    def New_days(e):
        try:
            selected_days = [day for day, cb in days_checkboxes.items() if cb.value]
            if "All" in selected_days:
                for day, cb in days_checkboxes.items():
                    if day != "All":
                        cb.value = True
                    cb.update()
        except Exception as ex:
            log.error(f"Errore nella gestione della selezione dei giorni: {ex}")
        finally:
            update_payload()

    def New_desc():
        if not dlg_desc.value:
            return
        else:
            update_payload()

    def New_msg():
        if not dlg_message.value:
            return
        else:
            update_payload()

    def New_topic():
        def handler(e):
            if not dlg_topic_dd.value:
                return
            else:
                # Aggiorna le opzioni chiave in base al topic selezionato
                if dlg_topic_dd.value in ["ACTIONS", "SCENE"]:
                    dlg_key_act_dd.options = [ft.dropdown.Option(k) for k in key_act]
                    dlg_key_act_dd.value = None
                    dlg_key_sql_dd.options = []
                    dlg_key_sql_dd.value = None
                elif dlg_topic_dd.value in ["DEVICE", "DEVICE_INFO"]:
                    dlg_key_sql_dd.options = [ft.dropdown.Option(k) for k in key_sql]
                    dlg_key_sql_dd.value = None
                    dlg_key_act_dd.options = []
                    dlg_key_act_dd.value = None
                else:
                    dlg_key_act_dd.options = []
                    dlg_key_act_dd.value = None
                    dlg_key_sql_dd.options = []
                    dlg_key_sql_dd.value = None
                update_payload()
        return handler

    def update_payload(e=None):
        try:
            selected_days = [day for day, cb in days_checkboxes.items() if cb.value and day != "All"]
            dlg_payload.value = "{"
            if dlg_time.value:
                dlg_payload.value += f'"time": "{dlg_time.value}"' 
            if dlg_time_end.value:
                dlg_payload.value += f', "time_end": "{dlg_time_end.value}"'
            if dlg_desc.value:
                dlg_payload.value += f', "description": "{dlg_desc.value}"'
            if dlg_message.value:
                dlg_payload.value += f', "message": "{dlg_message.value}"'
            if selected_days:
                days_str = ", ".join([f'"{d}"' for d in selected_days])
                dlg_payload.value += f', "days": [{days_str}]'

            dlg_payload.value += "}"
            dlg_payload.update()
        except Exception as ex:
            log.error(f"Errore durante l'aggiornamento del payload: {ex}")
    
    #   -----   👀  SUBSCRIPTION A EVENTI GLOBALI               👀  -----     #
    subscribe_events()

    #   -----   👀  DIALOGO DI CREAZIONE/EDITING SCHEDULE       👀  -----     #
    days_checkboxes = {
        "mon": ft.Checkbox(label="Lun", value=False, on_change=New_days, col={"xs": 3, "sm": 2}),
        "tue": ft.Checkbox(label="Mar", value=False, on_change=New_days, col={"xs": 3, "sm": 2}),
        "wed": ft.Checkbox(label="Mer", value=False, on_change=New_days, col={"xs": 3, "sm": 2}),
        "thu": ft.Checkbox(label="Gio", value=False, on_change=New_days, col={"xs": 3, "sm": 2}),
        "fri": ft.Checkbox(label="Ven", value=False, on_change=New_days, col={"xs": 3, "sm": 2}),
        "sat": ft.Checkbox(label="Sab", value=False, on_change=New_days, col={"xs": 3, "sm": 2}),
        "sun": ft.Checkbox(label="Dom", value=False, on_change=New_days, col={"xs": 3, "sm": 2}),
        "All": ft.Checkbox(label="All", value=False, on_change=New_days, col={"xs": 3, "sm": 2})
    }
    dlg_days_row = ft.ResponsiveRow(list(days_checkboxes.values()))

    dlg_time = ft.TextField(
        label="Orario Inizio", 
        hint_text="es. 07:00", 
        col={"xs": 12, "sm": 6},
        on_blur= New_time,
        on_tap_outside=New_time
    )
           
    dlg_time_end = ft.TextField(
        label="Orario Fine", 
        hint_text="es. 17:30", 
        col={"xs": 12, "sm": 6},
        on_blur= New_end_time,
        on_tap_outside=New_end_time
    )
    
    dlg_desc = ft.TextField(
        label="Descrizione", 
        hint_text="Inserisci una descrizione...", 
        multiline=True, 
        min_lines=1, 
        expand=True,
        on_blur= New_desc,
        on_tap_outside=New_desc
        )

    dlg_message = ft.TextField(
        label="Messaggio", 
        hint_text="Messaggio opzionale...", 
        multiline=True, 
        min_lines=1, 
        expand=True,
        on_blur= New_msg,
        on_tap_outside=New_msg
    )
         
    # Dropdown per topic
    dlg_topic_dd = ft.Dropdown(
        label="Topic",
        options=[ft.dropdown.Option(t) for t in loc_table],
        on_text_change=New_topic()
    )
    # Dropdown per chiave (dinamico)
    dlg_key_act_dd = ft.Dropdown(
        label="Azione",
        options=[ft.dropdown.Option(k) for k in key_act]
    )
    # Dropdown per chiave (dinamico)
    dlg_key_sql_dd = ft.Dropdown(
        label="Valore",
        options=[ft.dropdown.Option(k) for k in key_sql]
    )
    # Dropdown per scena
    dlg_scene_dd = ft.Dropdown(
        label="Scena",
        options=[ft.dropdown.Option(s) for s in loc_scene]
    )
    # Campo payload generato
    dlg_payload = ft.TextField(
        label="Payload", 
        read_only=True, 
        disabled=True, 
        expand=True, 
        multiline=True, 
        min_lines=2, 
        max_lines=8, 
        adaptive=True
    )
 
    def save_schedule(e):
        global loc_schedule
        global editing_schedule

        id = None
        days_list = [day for day, cb in days_checkboxes.items() if cb.value]
                        
        # Recupera altri campi non precedentemente gestiti esplicitamente se necessario, al momento rimangono 'duration','message', e aggiungiamo 'check', 'level', 'repeat' come attributi extra
        new_data = {
            'def': dlg_desc.value,
            'time': dlg_time.value,
            'time_end': dlg_time_end.value,
            'description': dlg_desc.value,
            'message': dlg_message.value,
            'payload': dlg_payload.value
        }

        if days_list: new_data['days'] = days_list
        if dlg_message.value: new_data['message'] = dlg_message.value
                
        if editing_schedule and 'id' in editing_schedule:
            id = editing_schedule['id']
            log.debug(f"Salvataggio in corso per schedule esistente con ID {id}")
            name = editing_schedule['name']
        else:
            log.debug("Creazione di una nuova schedule")
            existing_names = [s.get('name') for s in loc_schedule]
            idx = 0
            while True:
                name = f"sch_{idx:03d}"
                if name not in existing_names:
                    break
                idx += 1
            loc_schedule.append({'id': id, 'name': name, 'data': new_data})

        try:
            if hasattr(app, "dbm") and app.dbm is not None:
                app.dbm.UP_TAB_SCHEDULE(id, name, new_data)
                app.show_info_snackbar(f"✅ Schedule {name} salvata con successo.")
                app.refresh_schedule_cache()
        except Exception as e:
            log.error(f"Errore nel salvataggio della schedule a DB: {e}")

        edit_dialog.open = False
        app.page.update()

    def open_edit_dialog(schedule=None):
        global editing_schedule
        editing_schedule = schedule if schedule else {}
        
        if schedule:
            data = schedule.get('data', {})
            dlg_time.value = data.get('time', '')
            dlg_time_end.value = data.get('time_end', '')
            
            saved_days = data.get('days', [])
            if not saved_days or len(saved_days) == 7:
                for cb in days_checkboxes.values():
                    cb.value = True
            else:
                for day, cb in days_checkboxes.items():
                    cb.value = (day in saved_days)

            dlg_desc.value = data.get('description', data.get('def', ''))
            dlg_message.value = data.get('message', '')
            dlg_topic_dd.value = data.get('topic', None)

            # --- Popola la sezione payload dinamico ---
            # Prova a recuperare i valori dal payload (se esiste)
            try:
                payload_val = data.get('payload', None)
                if payload_val:
                    # Se è una stringa tipo dict, prova a caricarla
                    import ast
                    if isinstance(payload_val, str):
                        try:
                            payload_dict = ast.literal_eval(payload_val)
                        except Exception:
                            payload_dict = None
                    elif isinstance(payload_val, dict):
                        payload_dict = payload_val
                    else:
                        payload_dict = None
                    if payload_dict:
                        
                #        dlg_keytype_dd.value = payload_dict.get('keytype', 'key_act')
                #        # Aggiorna le opzioni chiave in base al tipo
                #        if dlg_keytype_dd.value == "key_act":
                #            dlg_key_dd.options = [ft.dropdown.Option(k) for k in key_act]
                #        else:
                #            dlg_key_dd.options = [ft.dropdown.Option(k) for k in key_sql]
                #        dlg_key_dd.value = payload_dict.get('key', None)
                        dlg_scene_dd.value = payload_dict.get('scene', None)
                        # Aggiorna il campo payload generato
                #        update_payload2()
            except Exception as ex:
                log.error(f"Errore nel parsing del payload dinamico: {ex}")
        else:
            dlg_time.value = ""
            dlg_time_end.value = ""
            dlg_desc.value = ""

            for cb in days_checkboxes.values():
                cb.value = False
            dlg_message.value = ""

            # Reset sezione payload dinamico
            dlg_topic_dd.value = None
            dlg_key_act_dd.options = [ft.dropdown.Option(k) for k in key_act]
            dlg_key_act_dd.value = None
            dlg_key_sql_dd.options = [ft.dropdown.Option(k) for k in key_sql]
            dlg_key_sql_dd.value = None
            dlg_scene_dd.value = None
            dlg_payload.value = "{}"
            
        update_payload()
        edit_dialog.open = True
        app.page.update()

    edit_dialog = ft.AlertDialog(
        title=ft.Text("Modifica Schedule"),
        content=ft.Container(
            width=650,
            content=ft.Column([
                ft.Text("Giorni:", weight="bold"), dlg_days_row,
                ft.ResponsiveRow([dlg_time, dlg_time_end]),
                ft.Row([dlg_desc]),
                ft.Row([dlg_message]),                
                ft.Divider(),
                ft.ResponsiveRow([
                    dlg_topic_dd,
                    dlg_key_act_dd,
                    dlg_key_sql_dd,
                    dlg_scene_dd
                ]),
                ft.ResponsiveRow([dlg_payload]),
            ], scroll=ft.ScrollMode.AUTO, tight=True)
        ),
        actions=[
            ft.TextButton("Annulla", on_click=lambda e: setattr(edit_dialog, 'open', False) or app.page.update()),
            ft.TextButton("Salva", on_click=save_schedule),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    confirm_delete_dialog = ft.AlertDialog(
        title=ft.Text("Elimina Schedule"),
        content=ft.Text("Sei sicuro di voler eliminare questa schedule?"),
        actions=[
            ft.TextButton("Annulla", on_click=lambda e: setattr(confirm_delete_dialog, 'open', False) or app.page.update()),
            ft.TextButton("Elimina", on_click=lambda e: delete_confirmed(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def prompt_delete(id):
        global item_to_delete
        item_to_delete = id
        confirm_delete_dialog.open = True
        app.page.update()
        
    def delete_confirmed(e):
        global loc_schedule, item_to_delete
        try:
            if item_to_delete:
                loc_schedule = [s for s in loc_schedule if s['id'] != item_to_delete]
                try:
                    if hasattr(app, "dbm") and app.dbm is not None:
                        app.dbm.DEL_TAB_SCHEDULE(id=item_to_delete)
                        app.show_info_snackbar(f"✅ Schedule {item_to_delete} eliminata con successo.")
                        app.refresh_schedule_cache()
                except Exception as e:
                    log.error(f"Errore nell'eliminazione della schedule a DB: {e}")

                item_to_delete = None
            confirm_delete_dialog.open = False
            app.page.update()
        except Exception as ex:
            log.error(f"Errore durante la conferma di eliminazione: {ex}")
        finally:
            update_table()

    schedule_table = ft.DataTable(
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
            ft.DataColumn(label=ft.Text("Giorni", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Inizio", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Fine", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Descrizione", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Messaggio", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Action/Payload", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Azioni", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
        ],
        rows=[]
    )

    action_table = ft.DataTable(
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
            ft.DataColumn(label=ft.Text("Name", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Topic", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("ByPass", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Auto", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Action", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Tamper", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Water Leak", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Contact", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Occupancy", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Battery", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Battery Low", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("State", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Min Lev", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Max Lev", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Power A", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Humidity", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Temperature", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Color Temp", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Brightness", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Step", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Steps", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Transition", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Message", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
            ft.DataColumn(label=ft.Text("Azioni", theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
        ],
        rows=[]
    )

    def update_table():
        schedule_table.rows.clear()
        for idx, sch in enumerate(loc_schedule):
            id = sch.get('id', idx)
            name = sch.get('name', f"sch_{idx}")
            data = sch.get('data', {})
            time_val = data.get('time', '-')
            time_end_val = data.get('time_end', '-')
                
            days_list = data.get('days', [])
            if not days_list or len(days_list) == 7:
                days_str = "Tutti"
            else:
                days_str = ", ".join(days_list).upper()
                
            desc_val = data.get('description', '-')
            msg_val = data.get('message', '')
            action_val = data.get('action', '')
            payload_val = data.get('payload', '')
            
            if action_val:
                import json
                action_str = json.dumps(action_val) if isinstance(action_val, dict) else str(action_val)
            elif payload_val:
                action_str = str(payload_val)
            else:
                action_str = "-"
            
            row = ft.DataRow(cells=[
                ft.DataCell(ft.Text(id, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0), visible=False),
                ft.DataCell(ft.Text(days_str, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(time_val, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(time_end_val, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(desc_val, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(msg_val, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(action_str, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Row([
                    ft.IconButton(
                        ft.Icons.EDIT,
                        tooltip="Modifica",
                        on_click=lambda e, s=sch: show_login_dialog(app.page, on_success=lambda: open_edit_dialog(s))
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE,
                        tooltip="Elimina",
                        icon_color=ft.Colors.ERROR,
                        on_click=lambda e, n=id: show_login_dialog(app.page, on_success=lambda: prompt_delete(n))
                    )
                ]))
            ])
            schedule_table.rows.append(row)

        action_table.rows.clear()
        for idx, sch in enumerate(loc_actions):
            id = sch.get('ID_KEY', idx)
            name = sch.get('NAME', f"sch_{idx}")
            topic = sch.get('TOPIC', '-')
            bypass  = sch.get('BYPASS', '')
            auto  = sch.get('AUTO', '')
            action  = sch.get('ACTION', '')
            tamper  = sch.get('TAMPER', '')
            water_leak  = sch.get('WATER_LEAK', '')
            contact  = sch.get('CONTACT', '')
            occupancy  = sch.get('OCCUPANCY', '')
            battery  = sch.get('BATTERY', '')
            battery_low  = sch.get('BATTERY_LOW', '')
            state  = sch.get('STATE', '')
            min_lev  = sch.get('LIM_MIN', '')
            max_lev  = sch.get('LIM_MAX', '')
            pow_act  = sch.get('POWER_A', '')
            humydity = sch.get('HUMIDITY', '')
            temp = sch.get('TEMPERATURE', '')
            col_temp = sch.get('COLOR_TEMP', '')
            brightness = sch.get('BRIGHTNESS', '')
            step = sch.get('STEP', '')
            steps = sch.get('STEPS', '')
            transition = sch.get('TRANSITION', '')
            msg_val = sch.get('MSG', '')
            
            row = ft.DataRow(cells=[
                ft.DataCell(ft.Text(id, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0), visible=False),
                ft.DataCell(ft.Text(name, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(topic, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(bypass, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(auto, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(action, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(tamper, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(water_leak, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(contact, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(occupancy, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(battery, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(battery_low, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(state, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(min_lev, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(max_lev, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(pow_act, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(humydity, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(temp, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(col_temp, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(brightness, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(step, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(steps, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(transition, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Text(msg_val, theme_style=ft.TextThemeStyle.BODY_MEDIUM, margin=0)),
                ft.DataCell(ft.Row([
                    ft.IconButton(
                        ft.Icons.EDIT,
                        tooltip="Modifica",
                        on_click=lambda e, s=sch: show_login_dialog(app.page, on_success=lambda: open_edit_dialog(s))
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE,
                        tooltip="Elimina",
                        icon_color=ft.Colors.ERROR,
                        on_click=lambda e, n=id: show_login_dialog(app.page, on_success=lambda: prompt_delete(n))
                    )
                ]))
            ])
            action_table.rows.append(row)
        app.page.update()

    update_table()                                                  #   ℹ️   Inizializza tabella con dati esistenti

    table_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Lista Scheduler", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.ElevatedButton(
                    "Nuovo",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: show_login_dialog(app.page, on_success=lambda: open_edit_dialog())
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(
                content=ft.Row([schedule_table], scroll=ft.ScrollMode.AUTO),
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ),
            ft.Row([
                ft.Text("Lista Action", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.ElevatedButton(
                    "Nuovo",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: show_login_dialog(app.page, on_success=lambda: open_edit_dialog())
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(
                content=ft.Row([action_table], scroll=ft.ScrollMode.AUTO),
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

    app.page.overlay.extend([edit_dialog, confirm_delete_dialog])

    #   -----   👀  STRUTTURA UNIFORMATA            👀  -----   #  
    #   ✍🏻      TITLE BAR
    title_bar = TitleCard(
        title=title,
        icon=ft.Icons.PENDING_ACTIONS,
        info_items=[
            "Crea Azioni rapide e scene predefinite"     
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

def show_payload_dialog(app, loc_table, loc_scene):
    topic_dropdown = ft.Dropdown(
        label="Scegli Topic",
        options=[ft.dropdown.Option(t) for t in loc_table],
        width=300
    )

    key_act_dropdown = ft.Dropdown(label="Azione")
    key_sql_dropdown = ft.Dropdown(label="Valore")

    scene_dropdown = ft.Dropdown(
        label="Scegli scena",
        options=[ft.dropdown.Option(str(s)) for s in loc_scene],
        width=200
    )

    def on_confirm(e):
        dialog.open = False
        dialog.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Crea/Modifica Payload"),
        content=ft.Column([
            topic_dropdown,
            key_act_dropdown,
            key_sql_dropdown,
            scene_dropdown
        ], spacing=10),
        actions=[
            ft.TextButton("Annulla", on_click=lambda e: (setattr(dialog, 'open', False), dialog.update())),
            ft.ElevatedButton("Conferma", on_click=on_confirm)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        open=True
    )
    app.page.dialog = dialog
    app.page.update()