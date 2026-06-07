import flet as ft
import flet_charts as fch
import logging
import threading
import time
from datetime import datetime, date, timedelta
from .BaseCard import BaseCard

from common.config import AppStyle

log = logging.getLogger(__name__)

class GenCard(BaseCard):
    """
    Card generica per sensori.
    Accetta un dizionario 'fields' che mappa le chiavi dei dati alle etichette da visualizzare.
    """
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.DEVICE_HUB, data: dict = {}, fields: dict = {}, fieldsB: dict = {}, floor: str = "", name: str = "", pos: str = "", battery: bool = False, switch: bool = False, page=None):
        """
        :param fields: Dizionario {'chiave_dati': 'Etichetta', ...}
                       Esempio: {'temperature': 'Temperature', 'humidity': 'Humidity'}
        :param battery: Se True, mostra icona batteria nel header
        :param switch: Se True, mostra switch nel header
        """
        super().__init__()
        self.main_page = page
        self.topic = topic
        self.device_name = device_name
        self.fields_map = fields
        self.fields_mapB = fieldsB if fieldsB else {}
        self.floor = floor
        self.name = name
        self.pos = pos

        self.field_controls_A = {}
        self.field_controls_B = {}
        
        self.show_battery = battery
        self.show_switch = switch
        self.battery_icon = None
        self.switch_control = None

        has_brightness = 'brightness' in self.fields_map or 'brightness' in self.fields_mapB

        # Helper interno
        def create_controls(f_map, t_dict):
            lst = []
            for key, label in f_map.items():
                key = key.upper()
                if self.show_battery and key == 'BATTERY':
                    continue
                
                # Special handling for "state" if brightness is present
                if key == 'STATE' and has_brightness:
                    val = data.get(key, 'OFF')
                    is_on_state = str(val).lower() in ['on', 'true', '1']
                    icon_n = ft.Icons.LIGHTBULB if is_on_state else ft.Icons.LIGHTBULB_OUTLINE
                    icon_c = ft.Colors.YELLOW if is_on_state else ft.Colors.GREY
                    icn = ft.Icon(icon_n, size=AppStyle.ICON_SIZE_B, color=icon_c)
                    t_dict[key] = icn
                    
                    def on_switch_change(e):
                        """Gestisce il cambio stato dello switch associato a STATE"""
                        new_state = e.control.value
                        msg = '{"state":"ON"}' if new_state else '{"state":"OFF"}'
                        try:
                            if hasattr(self, 'page') and hasattr(self.main_page, 'app') and hasattr(self.main_page.app, 'mqtt'):
                                top = f"HomeZig/{self.topic}/set"
                                self.main_page.app.mqtt.publish_message(top, msg)
                            else:
                                log.warning("MQTT publish non disponibile: manca self.main_page.app.mqtt")
                        except Exception as ex:
                            log.error(f"MQTT publish fallito: {ex}")

                    switch_trailing = ft.Switch(value=is_on_state, on_change=on_switch_change, height=AppStyle.SWITCH_HEIGHT)
                    t_dict[key + '_switch_trailing'] = switch_trailing                                                                  # ℹ️ Salva il riferimento per update_data
                elif key == 'STATE' and ( self.device_name=='E22x4' or self.device_name=='ZBMINIR2' ):
                    val = data.get(key, 'OFF')
                    is_on_state = str(val).lower() in ['on', 'true', '1']
                    icon_n = ft.Icons.POWER if is_on_state else ft.Icons.POWER_OFF
                    icon_c = ft.Colors.YELLOW if is_on_state else ft.Colors.GREY
                    icn = ft.Icon(icon_n, size=AppStyle.ICON_SIZE_B, color=icon_c)
                    t_dict[key] = icn

                    # Switch per controllo stato
                    def on_switch_change(e):
                        """Gestisce il cambio stato dello switch associato a STATE"""
                        new_state = e.control.value
                        msg = '{"state":"ON"}' if new_state else '{"state":"OFF"}'
                        try:
                            if hasattr(self, 'page') and hasattr(self.main_page, 'app') and hasattr(self.main_page.app, 'mqtt'):
                                top = f"HomeZig/{self.topic}/set"
                                self.main_page.app.mqtt.publish_message(top, msg)
                            else:
                                log.warning("MQTT publish non disponibile: manca self.main_page.app.mqtt")
                        except Exception as ex:
                            log.error(f"MQTT publish fallito: {ex}")

                    switch_trailing = ft.Switch(value=is_on_state, on_change=on_switch_change, height=AppStyle.SWITCH_HEIGHT)
                    t_dict[key + '_switch_trailing'] = switch_trailing                                                                  # ℹ️ Salva il riferimento per update_data
                elif key == 'STATE' and (self.device_name=='14594'):
                    pass
                elif key == 'BRIGHTNESS':
                    val = data.get(key, 0)
                    try:
                        val = float(val)
                    except:
                        val = 0
                    
                    def on_change_brightness(e):
                        new_val = int(e.control.value)
                        msg = f'{{"brightness": {new_val}}}'
                        try:
                            if hasattr(self, 'page') and hasattr(self.main_page, 'app') and hasattr(self.main_page.app, 'mqtt'):
                                top = f"HomeZig/{self.topic}/set"
                                self.main_page.app.mqtt.publish_message(top, msg)
                            else:
                                log.warning("MQTT publish non disponibile: manca self.main_page.app.mqtt")
                        except Exception as ex:
                            log.error(f"MQTT publish fallito: {ex}")

                    slider = ft.Slider(
                        min=0, max=254, divisions=50, 
                        size_change_interval=50, 
                        value=val, label="{value}",
                        margin=ft.Margin(0, 0, 0, 0 ),
                        expand=True,
                        on_change_end=on_change_brightness
                    )
                    t_dict[key] = slider

                    row = ft.Row([
                        ft.Icon(ft.Icons.BRIGHTNESS_6, size=AppStyle.ICON_SIZE_S),
                        ft.Container(content=slider, expand=True),
                    ], spacing=5, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    lst.append(row)
                elif key == 'COLOR_TEMP':
                    val = data.get(key, 0)
                    try:
                        val = float(val)
                    except:
                        val = 250
                    
                    if val < 250: val = 250
                    if val > 454: val = 454

                    def on_change_color_temp(e):
                        new_val = int(e.control.value)
                        msg = f'{{"color_temp": {new_val}}}'
                        try:
                            if hasattr(self, 'page') and hasattr(self.main_page, 'app') and hasattr(self.main_page.app, 'mqtt'):
                                top = f"HomeZig/{self.topic}/set"
                                self.main_page.app.mqtt.publish_message(top, msg)
                            else:
                                log.warning("MQTT publish non disponibile: manca self.main_page.app.mqtt")
                        except Exception as ex:
                            log.error(f"MQTT publish fallito: {ex}")

                    slider = ft.Slider(
                        min=250, max=454, divisions=50,
                        size_change_interval=50, 
                        value=val, label="{value}",
                        margin=ft.Margin(0, 0, 0, 0 ),
                        expand=True,
                        on_change_end=on_change_color_temp
                    )
                    t_dict[key] = slider

                    row = ft.Row([
                        ft.Icon(ft.Icons.COLOR_LENS, size=16),
                        ft.Container(content=slider, expand=True),
                    ], spacing=5, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    lst.append(row)
                elif key == 'HUMIDITY' or key == 'SOIL_MOISTURE':
                    val = data.get(key, 'N/A')
                    txt_control = ft.Text(f"{val}", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
                    t_dict[key] = txt_control
                    row = ft.Row([
                        ft.Icon(ft.Icons.WATER_DROP_OUTLINED, 
                                size=AppStyle.ICON_SIZE_B, 
                                color=ft.Colors.BLUE_300),
                        txt_control
                    ], spacing=5, 
                    alignment=ft.MainAxisAlignment.START, 
                    vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    lst.append(row)
                elif key == 'TEMPERATURE':
                    val = data.get(key, 'N/A')
                    txt_control = ft.Text(f"{val}", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
                    t_dict[key] = txt_control
                    
                    row = ft.Row([
                        ft.Icon(ft.Icons.DEVICE_THERMOSTAT, 
                                size=AppStyle.ICON_SIZE_B, 
                                color=ft.Colors.RED_300),
                        txt_control
                    ], spacing=5, 
                    alignment=ft.MainAxisAlignment.START, 
                    vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    lst.append(row)
                elif key == 'ILLUMINANCE':
                    val = data.get(key, 'N/A')
                    txt = ft.Text(f"{val}", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
                    t_dict[key] = txt
                    
                    row = ft.Row([
                        ft.Icon(ft.Icons.LIGHT_MODE_OUTLINED, size=16, color=ft.Colors.YELLOW_300),
                        txt
                    ], spacing=5, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    lst.append(row)
                elif key == 'OCCUPANCY':
                    val = data.get(key, 'False')
                    is_on_state = str(val).lower() in ['on', 'true', '1']
                    icon_n = ft.Icons.SENSOR_OCCUPIED if is_on_state else ft.Icons.SENSOR_OCCUPIED_OUTLINED
                    icon_c = ft.Colors.RED if is_on_state else ft.Colors.GREY
                    txt = ft.Text(f"{is_on_state}", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
                    t_dict[key] = txt
                    
                    row = ft.Row([
                        txt
                    ], spacing=5, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    lst.append(row)
                elif key == 'CONTACT' and self.device_name == 'SNZB-04P':
                    val = data.get(key, 'False')
                    is_on_state = str(val).lower() in ['on', 'true', '1']
                    icon_n = ft.Icons.SENSOR_WINDOW if is_on_state else ft.Icons.SENSOR_WINDOW_OUTLINED
                    icon_c = ft.Colors.RED if is_on_state else ft.Colors.GREY
                    txt = ft.Text(f"{is_on_state}", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
                    
                    t_dict[key] = txt
                    row = ft.Row([
                        txt
                    ], spacing=5, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    lst.append(row)
                elif key == 'WATER_LEAK':
                    val = data.get(key, 'OFF')
                    is_on_state = str(val).lower() in ['on', 'true', '1']
                    icon_n = ft.Icons.WATER_DAMAGE_OUTLINED if is_on_state else ft.Icons.WATER_DROP_OUTLINED
                    icon_c = ft.Colors.RED if is_on_state else ft.Colors.GREY
                    txt = ft.Text(f"{is_on_state}", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
                    
                    t_dict[key] = txt
                    row = ft.Row([
                        txt
                    ], spacing=5, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    lst.append(row)
                elif key == 'POSITION':
                    val = data.get(key, 0)
                    try:
                        val = float(val)
                    except:
                        val = 0
                    
                    if val < 0: val = 0
                    if val > 100: val = 100

                    def on_change_position(e):
                        new_val = int(e.control.value)
                        msg = f'{{"state": "OPEN", "position": {new_val}}}'
                        try:
                            if hasattr(self, 'page') and hasattr(self.main_page, 'app') and hasattr(self.main_page.app, 'mqtt'):
                                top = f"HomeZig/{self.topic}/set"
                                self.main_page.app.mqtt.publish_message(top, msg)
                            else:
                                log.warning("MQTT publish non disponibile: manca self.main_page.app.mqtt")
                        except Exception as ex:
                            log.error(f"MQTT publish fallito: {ex}")

                    slider = ft.Slider(
                        min=0, 
                        max=100, 
                        divisions=20,                           # 👀    step di 5
                        size_change_interval=50, 
                        value=val, label="{value}",
                        on_change_end=on_change_position
                    )
                    t_dict[key] = slider

                    slider_c = ft.Icons.WINDOW
                    slider_o = ft.Icons.WINDOW_OUTLINED
                    if self.name and "porta" in self.name.lower():
                        slider_c = ft.Icons.DOOR_FRONT_DOOR
                        slider_o = ft.Icons.DOOR_FRONT_DOOR_OUTLINED

                    row = ft.Row([
                        ft.Icon(slider_c, size=AppStyle.ICON_SIZE_B, color="secondary"),
                        ft.Container(content=slider, expand=True),
                        ft.Icon(slider_o, size=AppStyle.ICON_SIZE_B),
                    ], spacing=5, 
                    alignment=ft.MainAxisAlignment.START, 
                    vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    lst.append(row)
                else:
                    val = data.get(key, 'N/A')
                    txt = ft.Text(f"{label}: {val}", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
                    t_dict[key] = txt
                    lst.append(txt)
            return lst

        grid_controls_A = create_controls(self.fields_map, self.field_controls_A)
        self.container_A = ft.ResponsiveRow(grid_controls_A, spacing=5)
        
        grid_controls_B = create_controls(self.fields_mapB, self.field_controls_B)        
        self.container_B = ft.ResponsiveRow(grid_controls_B, spacing=5)

        # Fallback in caso di perdita di precisione per TIME_MSG FLOAT sul Database (1777490000)
        day_u = data.get('DAY_U')
        time_u = data.get('TIME_U')
        if day_u and time_u:
            t_msg = f"{day_u} {time_u}"
        else:
            t_msg = data.get('TIME_MSG', 'N/A')
            try:
                t_msg = datetime.fromtimestamp(float(t_msg)).strftime('%Y/%m/%d %H:%M:%S')
            except (ValueError, TypeError):
                pass
        self.time = ft.Text(f"{t_msg}")

        # Configurazione Header (ListTile trailing)
        trailing_controls = []
        
        #   👀  Icona del titolo (colore coerente con stato reale, se disponibile)
        title_icon_color = None
        # Prova a usare lo stato reale se presente tra i dati
        state_val = data.get('STATE', None)
        if has_brightness:
            is_on_state = str(state_val).lower() in ['on', 'true', '1'] if state_val is not None else False
            title_icon_color = ft.Colors.YELLOW if is_on_state else ft.Colors.GREY
        elif self.device_name in ['E22x4', 'ZBMINIR2']:
            is_on_state = str(state_val).lower() in ['on', 'true', '1'] if state_val is not None else False
            title_icon_color = ft.Colors.YELLOW if is_on_state else ft.Colors.GREY
        elif self.device_name == '14594':
            title_icon_color = None  # nessun colore specifico
        else:
            title_icon_color = None

        self.title_icon = ft.Icon(
            icon,
            size=AppStyle.ICON_SIZE_B,
            color=title_icon_color,
            tooltip=f"Device: {self.device_name}\nTopic: {self.topic}"
        )

        sw_tr = self.field_controls_A.get('STATE_switch_trailing')                              # ℹ️ Aggiungi lo switch_trailing se presente nei field params
        if sw_tr:
            trailing_controls.append(sw_tr)

        #   👀  Button Grafico
        chart_triggers = ['humidity', 'temperature', 'energy_a', 'soil_moisture']
        has_chart = any(k in self.fields_map for k in chart_triggers)
        if has_chart:
            trailing_controls.append(
                ft.IconButton(
                    icon=ft.Icons.SHOW_CHART, icon_color="secondary",
                    icon_size=AppStyle.ICON_SIZE_B, 
                    tooltip="Grafico",
                    on_click=lambda _: self.show_chart_dialog()
                )
            )
        #   👀  Icon Battery
        if self.show_battery:
            # Logica base per icona batteria
            bat_val = data.get('BATTERY', None)
            icon_bat = ft.Icons.BATTERY_STD
            try:
                # Esempio semplice di logica icona
                if bat_val is None:
                    icon_bat = ft.Icons.BATTERY_UNKNOWN
                elif int(str(bat_val).replace('%', '')) < 20:
                     icon_bat = ft.Icons.BATTERY_ALERT
                else: 
                     icon_bat = ft.Icons.BATTERY_FULL
            except:
                pass
            self.battery_icon = ft.Icon(icon_bat, size=AppStyle.ICON_SIZE_B, color=ft.Colors.GREY)
            trailing_controls.append(self.battery_icon)
        #   👀  Switch Toggle
        if self.show_switch:
            self.switch_control = ft.Switch(value=False, height=AppStyle.SWITCH_HEIGHT, on_change=self._on_switch_card_change)
            trailing_controls.append(self.switch_control)
        #   👀  Header Trailing
        header_trailing = None
        if trailing_controls:
            header_trailing = ft.Row(
                trailing_controls, 
                spacing=5, 
                tight=True, 
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        #   👀  Wrapper containers for animation
        self.c_A = ft.Container(
            content=self.container_A,
            offset=ft.Offset(0, 0),
            animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.c_B = ft.Container(
            content=self.container_B,
            offset=ft.Offset(-1.1, 0),
            animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT_CUBIC),
            opacity=0,
        )

        self.stack_content = ft.Stack([self.c_A, self.c_B])

        #   👀  Icon e Label Time
        footer = [
            ft.Row([
                ft.Icon(ft.Icons.ACCESS_TIME, 
                        size=AppStyle.ICON_SIZE_S, 
                        color="secondary"),
                self.time,
            ], spacing=5)
        ]
        
        # Contenuto della card
        self.content = ft.Container(
            bgcolor="secondarycontainer",
            border_radius=AppStyle.CORNER_RADIUS,
            content=ft.Column([
                # Header con icona e titolo (Custom Row al posto di ListTile per forzare l'allineamento Top-Right)
                ft.Row(
                    [
                        ft.Container(self.title_icon,
                                     padding=ft.Padding(top=5)),
                        ft.Column([
                            ft.Text(self.pos, theme_style=ft.TextThemeStyle.BODY_SMALL, color="surfacecontainercontrast"),
                            ft.Text(self.name, theme_style=ft.TextThemeStyle.BODY_MEDIUM),
                        ], spacing=0, expand=True),
                        header_trailing if header_trailing else ft.Container()
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                self.stack_content,
                ft.Row(footer, alignment=ft.MainAxisAlignment.END),
            ], spacing=0),
            padding=5,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )
        self.configure_animated_content(self.content)

        # Stile della card (preso dai file esistenti)
        self.elevation = 2
        self.margin = 5
        self.bgcolor = "surfacecontainerhighest"
        self.border_radius = 10
        self.border = ft.Border.all(1, ft.Colors.OUTLINE)
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=4,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 2)
        )

    def _on_switch_card_change(self, e):
        """Gestisce il cambio stato dello switch per togglare la vista"""
        is_on = self.switch_control.value
        if self.fields_mapB:
             if is_on:
                 # False -> True: A va a destra, B entra da sinistra
                 self.c_A.offset = ft.Offset(1.1, 0)
                 self.c_A.opacity = 0
                 
                 self.c_B.offset = ft.Offset(0, 0)
                 self.c_B.opacity = 1
             else:
                 # True -> False: A torna da destra, B esce a sinistra
                 self.c_A.offset = ft.Offset(0, 0)
                 self.c_A.opacity = 1
                 
                 self.c_B.offset = ft.Offset(-1.1, 0)
                 self.c_B.opacity = 0
             
             self.c_A.update()
             self.c_B.update()

    def update_data(self, data: dict):
        """Aggiorna i dati della card e ridisegna"""
        if not data:
            return
        
        def update_controls(f_map, c_dict):
            for key in f_map:
                val = data.get(key.upper(), None)
                if val is None:
                    continue
                label = f_map[key]
                control = c_dict.get(key.upper(), None)
                # Aggiorna icona stato e switch associato
                if key.upper() == 'STATE' and control is not None:
                    is_on = str(val).lower() in ['on', 'true', '1']
                    if ( self.device_name=='E22x4' or self.device_name=='ZBMINIR2' ):
                        control.name = ft.Icons.POWER if is_on else ft.Icons.POWER_OFF
                        control.color = ft.Colors.YELLOW if is_on else ft.Colors.GREY
                        if hasattr(control, "value"):
                            control.value = "Open" if is_on else "Close"
                    elif self.device_name=='SNZB-04P':
                        if "porta" in self.name.lower():
                            control.name = ft.Icons.SENSOR_DOOR if is_on else ft.Icons.SENSOR_DOOR_OUTLINED
                        else:
                            control.name = ft.Icons.SENSOR_WINDOW if is_on else ft.Icons.SENSOR_WINDOW_OUTLINED
                        control.color = ft.Colors.YELLOW if is_on else ft.Colors.GREY
                        if hasattr(control, "value"):
                            control.value = "Open" if is_on else "Close"
                    elif self.device_name.startswith('ZG-222Z'):
                        control.name = ft.Icons.WATER_DROP_OUTLINED if is_on else ft.Icons.WATER_DROP
                        control.color = ft.Colors.YELLOW if is_on else ft.Colors.GREY
                        if hasattr(control, "value"):
                            control.value = "Open" if is_on else "Close"
                    else:
                        if control and isinstance(control, ft.Icon):
                            control.name = ft.Icons.LIGHTBULB if is_on else ft.Icons.LIGHTBULB_OUTLINED
                            control.color = ft.Colors.YELLOW if is_on else ft.Colors.GREY
                        sw_tr = c_dict.get(key.upper() + '_switch_trailing') or c_dict.get(key.lower() + '_switch_trailing')
                        if sw_tr:
                            sw_tr.value = is_on                                                                                 # ⬅️ Questo muoverà fisicamente lo switch su True (ON) o False (OFF)
                    
                    if hasattr(self, 'title_icon'):
                        self.title_icon.name = control.name
                        self.title_icon.color = control.color

                    # Aggiorna lo switch_trailing associato
                    sw_tr = c_dict.get(key + '_switch_trailing')
                    if sw_tr and hasattr(sw_tr, "value"):
                        sw_tr.value = is_on
                elif key.upper() == 'CONTACT' and self.device_name == 'SNZB-04P':
                    is_on = str(val).lower() in ['on', 'true', '1']
                    if "porta" in self.name.lower():
                        control.name = ft.Icons.SENSOR_DOOR if is_on else ft.Icons.SENSOR_DOOR_OUTLINED
                    else:
                        control.name = ft.Icons.SENSOR_WINDOW if is_on else ft.Icons.SENSOR_WINDOW_OUTLINED
                    control.color = ft.Colors.YELLOW if is_on else ft.Colors.GREY
                    if hasattr(control, "value"):
                        control.value = "Open" if is_on else "Close"

                    if hasattr(self, 'title_icon'):
                        self.title_icon.name = control.name
                        self.title_icon.color = control.color
                elif control is not None:
                    if key.upper() == 'BRIGHTNESS':
                        try:
                            if hasattr(control, "value"):
                                control.value = float(val)
                        except Exception as e:
                            log.warning(f"[GenCard] Errore assegnando BRIGHTNESS: {e}")
                    elif key.upper() == 'COLOR_TEMP':
                        try:
                            v = float(val)
                            if v < 250: v = 250
                            if v > 454: v = 454
                            if hasattr(control, "value"):
                                control.value = v
                        except Exception as e:
                            log.warning(f"[GenCard] Errore assegnando COLOR_TEMP: {e}")
                    elif key.upper() == 'POSITION':
                        try:
                            v = float(val)
                            if v < 0: v = 0
                            if v > 100: v = 100
                            if hasattr(control, "value"):
                                control.value = v
                        except Exception as e:
                            log.warning(f"[GenCard] Errore assegnando POSITION: {e}")
                    # Handle Text
                    elif key.upper() in ['HUMIDITY', 'TEMPERATURE', 'ILLUMINANCE', 'OCCUPANCY']:
                        if hasattr(control, "value"):
                            control.value = f"{val}"
                        else:
                            log.warning(f"[GenCard] Il controllo per '{key}' non ha attributo 'value' (type: {type(control)}): {control}")
                    else:
                        if hasattr(control, "value"):
                            control.value = f"{label}: {val}"
                        else:
                            log.warning(f"[GenCard] Il controllo per '{key}' non ha attributo 'value' (type: {type(control)}): {control}")

        # Aggiorna i campi dinamici A
        update_controls(self.fields_map, self.field_controls_A)

        # Aggiorna i campi dinamici B
        update_controls(self.fields_mapB, self.field_controls_B)

        # Aggiorna batteria
        if self.show_battery and self.battery_icon:
            bat_val = data.get('BATTERY', None)
            try:
                if bat_val is None:
                    self.battery_icon.name = ft.Icons.BATTERY_UNKNOWN
                    self.battery_icon.color = ft.Colors.RED
                else:
                    percent = int(str(bat_val).replace('%', ''))
                    if percent < 5:
                        self.battery_icon.name = ft.Icons.BATTERY_0_BAR
                        self.battery_icon.color = ft.Colors.RED
                    elif percent < 15:
                        self.battery_icon.name = ft.Icons.BATTERY_1_BAR
                        self.battery_icon.color = ft.Colors.RED
                    elif percent < 30:
                        self.battery_icon.name = ft.Icons.BATTERY_2_BAR
                        self.battery_icon.color = ft.Colors.ORANGE
                    elif percent < 50:
                        self.battery_icon.name = ft.Icons.BATTERY_3_BAR
                        self.battery_icon.color = ft.Colors.ORANGE
                    elif percent < 70:
                        self.battery_icon.name = ft.Icons.BATTERY_4_BAR
                        self.battery_icon.color = ft.Colors.YELLOW
                    elif percent < 90:
                        self.battery_icon.name = ft.Icons.BATTERY_5_BAR
                        self.battery_icon.color = ft.Colors.GREEN
                    else:
                        self.battery_icon.name = ft.Icons.BATTERY_6_BAR
                        self.battery_icon.color = ft.Colors.GREEN
            except Exception as e:
                log.error(f"Error updating battery icon: {e}")

        t_msg = data.get('TIME_MSG', 'N/A')
        try:
            t_msg = datetime.fromtimestamp(float(t_msg)).strftime('%Y/%m/%d %H:%M:%S')
        except (ValueError, TypeError):
            log.warning(f"Invalid TIME_MSG value: {t_msg}")
        
        self.time.value = f"{t_msg}"

        if self.main_page:
            self.trigger_update_animation()

    def show_chart_dialog(self, target_date=None):
        """Mostra un grafico per il topic corrente"""
        if not self.main_page or not hasattr(self.main_page, 'app'):
            log.warning("App context not available")
            return
            
        app = self.main_page.app
        dbm = app.dbm
        
        # Tentativo di trovare la tabella corretta
        parts = self.topic.split('/')
        table_name = parts[1] if len(parts) > 1 else self.topic
        
        def _create_line_chart(points, color, left_title, top_title, b_labels, min_y, max_y, min_x=None, max_x=None, grid_x=1, grid_y=1):
            return fch.LineChart(
                animation=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
                border=ft.Border(
                    bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.5, ft.Colors.PRIMARY))
                ),
                data_series=[
                    fch.LineChartData(
                        points=points,
                        stroke_width=2,
                        rounded_stroke_cap=True,
                        color=color,
                        curved=True,
                    )
                ],
                left_axis=fch.ChartAxis(
                    title=ft.Text(left_title, size=15),
                    label_size=40,
                ),
                right_axis=fch.ChartAxis(show_labels=False),
                top_axis=fch.ChartAxis(
                    title=ft.Text(top_title, size=15), 
                    show_labels=False, label_spacing=5, label_size=15, show_max=True, show_min=True,
                ),
                bottom_axis=fch.ChartAxis(
                    labels=b_labels,
                    label_size=40
                ),
                horizontal_grid_lines=fch.ChartGridLines(
                    interval=grid_y, color=ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY), width=1
                ),
                vertical_grid_lines=fch.ChartGridLines(
                    interval=grid_x, color=ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY), width=1
                ),
                min_x=min_x,
                max_x=max_x,
                min_y=min_y,
                max_y=max_y,
                expand=True,
                height=300
            )

        try:
            # 2. Determina Tipo Grafico
            graph_type = 0
            
            if 'temperature' in self.fields_map and 'humidity' in self.fields_map:
                graph_type = 1
            elif 'temperature' in self.fields_map and 'soil_moisture' in self.fields_map:
                graph_type = 2
            elif 'power_a' in self.fields_map:
                graph_type = 3

            if graph_type == 0:
                if hasattr(app, 'show_info_snackbar'):
                     app.show_info_snackbar("Nessun grafico configurato per questa tabella")
                return

            # 3. Recupera Dati (Default: Oggi)
            chart1 = None
            chart2 = None
            today_date = target_date if target_date else date.today()
            if isinstance(today_date, datetime):
                today_date = today_date.date()
            today = today_date.strftime("%Y-%m-%d")
            
            if graph_type == 3:
                # Logica specifica per BarChart (confronto Oggi vs Ieri)
                try:
                    yesterday_date = today_date - timedelta(days=1)
                    today_str = today_date.isoformat()
                    yesterday_str = yesterday_date.isoformat()
                    
                    # Default n_val a 50 se non specificato
                    n_val = 50
                    
                    cons_today = dbm.GET_TABLE_CONS(table_name, today_str, n_val)
                    cons_yesterday = dbm.GET_TABLE_CONS(table_name, yesterday_str, n_val)
                    prod = dbm.GET_CHART_PROD(table_name, today_str, today_str)

                    data_today = {str(row[0])[:5]: float(row[1]) if row[1] is not None else 0 for row in (cons_today or [])}
                    data_yesterday = {str(row[0])[:5]: float(row[1]) if row[1] is not None else 0 for row in (cons_yesterday or [])}
                    
                    all_labels = sorted(set(data_today.keys()) | set(data_yesterday.keys()))
                    
                    bar_groups = []
                    for i, label in enumerate(all_labels):
                        val_today = data_today.get(label, 0)
                        val_yesterday = data_yesterday.get(label, 0)
                        bar_groups.append(
                            fch.BarChartGroup(
                                x=i,
                                rods=[
                                    fch.BarChartRod(to_y=val_today, width=14, color=ft.Colors.BLUE_400, border_radius=0, tooltip=f"Oggi ({label}): {val_today}"),
                                    fch.BarChartRod(to_y=val_yesterday, width=14, color=ft.Colors.ORANGE_400, border_radius=0, tooltip=f"Ieri ({label}): {val_yesterday}"),
                                ]
                            )
                        )
                    
                    all_vals = [rod.to_y for group in bar_groups for rod in group.rods]
                    max_val = max(all_vals + [1])
                    max_y = ((int(max_val) + 99) // 100) * 100
                    if max_y == 0: max_y = 100
                    step_y = max(1, 100)

                    # Calcoliamo i punti all'ora per posizionare le griglie verticali
                    h_counts1 = {}
                    for l in all_labels:
                        if l:
                            h = l.split(':')[0]
                            h_counts1[h] = h_counts1.get(h, 0) + 1
                    v_step_1 = max(list(h_counts1.values()) or [6])

                    chart2_data = []
                    p_values = []
                    time_labels = []
                    
                    for i, row in enumerate(prod or []):
                        media_t = row[1]  # Media_T
                        media_power = float(row[2]) if row[2] is not None else 0
                        chart2_data.append(fch.LineChartDataPoint(x=i, y=media_power))

                        time_str = str(media_t)[:5]
                        time_parts = time_str.split(':')
                        hours = int(time_parts[0])
                        minutes = int(time_parts[1])
                        idx = len(chart2_data)
                        p_values.append(media_power)
   
                        step = max(1, len(prod) // 6) 
                    #    if idx % step == 0: 
                        time_labels.append(f"{hours:02d}:{minutes:02d}")
                    #    else:
                    #        time_labels.append("")

                    p_min, p_max = min(p_values), max(p_values)
                    chart2_min_y = (int(p_min) // 100) * 100
                    chart2_max_y = ((int(p_max) // 100) + 1) * 100
                    
                    chart1 = fch.BarChart(
                        animation=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
                        groups=bar_groups,
                        border=ft.Border(
                            bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.5, ft.Colors.PRIMARY))
                        ),
                        left_axis=fch.ChartAxis(
                            title=ft.Text("W", size=15),
                    #        labels=[fch.ChartAxisLabel(value=y, label=ft.Text(str(y))) for y in range(0, int(max_y)+1, step_y)],
                            label_size=40,
                        ),
                        right_axis=fch.ChartAxis(show_labels=False),
                        bottom_axis=fch.ChartAxis(
                            labels=[fch.ChartAxisLabel(value=i, 
                                                       label=ft.Container(
                                                           content=ft.Text(l), 
                                                           padding=ft.Padding(top=10)
                                                       )
                                                    ) for i, l in enumerate(all_labels) if l and l.endswith(':00')
                                        ],
                            label_size=40
                        ),         
                        horizontal_grid_lines=fch.ChartGridLines(
                            interval=step_y, color=ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY), width=1
                        ),
                        vertical_grid_lines=fch.ChartGridLines(
                            interval=v_step_1, color=ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY), width=1
                        ),
                        min_y=0,
                        max_y=max_y,
                        expand=True,
                        height=300
                    )

                    # Calcoliamo i punti all'ora
                    h_counts2 = {}
                    for l in time_labels:
                        if l:
                            h = l.split(':')[0]
                            h_counts2[h] = h_counts2.get(h, 0) + 1
                    v_step_2 = max(list(h_counts2.values()) or [6])

                    b_labels2 = [
                        fch.ChartAxisLabel(
                            value=i, 
                            label=ft.Container(
                                content=ft.Text(l), 
                                padding=ft.Padding(top=10)
                            )
                        ) for i, l in enumerate(time_labels) if l and l.endswith(':00')
                    ]

                    chart2 = _create_line_chart(
                        points=chart2_data, color=ft.Colors.GREEN, 
                        left_title="Power", top_title="Orario", 
                        b_labels=b_labels2, min_y=chart2_min_y, max_y=chart2_max_y, 
                        grid_x=v_step_2, grid_y=step_y
                    )
                except Exception as ex:
                    log.error(f"Errore creazione BarChart: {ex}")
                    if hasattr(app, 'show_info_snackbar'):
                        app.show_info_snackbar(f"Errore dati power: {ex}")
                    return

            else:
                # Logica standard per LineChart (Tipo 1 e 2)
                start_val = today
                next_date = today_date + timedelta(days=1)
                end_val = next_date.strftime("%Y-%m-%d")
                DATA = None
                
                if hasattr(dbm, 'GET_CHART_1') and graph_type == 1:
                    DATA = dbm.GET_CHART_1(table_name, start_val, end_val)
                elif hasattr(dbm, 'GET_CHART_2') and graph_type == 2:
                    DATA = dbm.GET_CHART_2(table_name, start_val, end_val)
                
                if not DATA:
                    if hasattr(app, 'show_info_snackbar'):
                        app.show_info_snackbar(f"Nessun dato trovato per {today}")
                    return

                # 4. Elabora Dati LineChart
                chart1_data = []
                chart2_data = []
                t_values = []
                h_values = []
                time_labels = []
                
                for row in DATA:
                    try:
                        time_str = str(row[1])
                        
                        time_parts = time_str.split(':')
                        hours = int(time_parts[0])
                        minutes = int(time_parts[1])
                        seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                        
                        decimal_time = hours + (minutes / 60.0) + (seconds / 3600.0)
                        
                        if row[2] is not None:
                            t_value = float(row[2])
                            chart1_data.append(fch.LineChartDataPoint(x=decimal_time, y=t_value))
                            t_values.append(t_value)
                            
                        if len(row) > 3 and row[3] is not None:
                            h_value = float(row[3])
                            chart2_data.append(fch.LineChartDataPoint(x=decimal_time, y=h_value))
                            h_values.append(h_value)

                    except Exception as e:
                        continue

                if not chart1_data:
                    if hasattr(app, 'show_info_snackbar'):
                        app.show_info_snackbar("Dati non validi per il grafico")
                    return

                # 5. Crea Charts (LineChart)
                t_min, t_max = min(t_values), max(t_values)
                h_min, h_max = min(h_values), max(h_values)
                                
                chart1_min_y = (int(t_min) // 10) * 10
                chart1_max_y = ((int(t_max) // 10) + 1) * 10

                x_labels = []
                for h in range(25):
                    x_labels.append(
                        fch.ChartAxisLabel(
                            value=h, 
                            label=ft.Container(
                                content=ft.Text(f"{h:02d}:00"), 
                                padding=ft.Padding(top=10)
                            )
                        )
                    )

                chart1 = _create_line_chart(
                    points=chart1_data, color=ft.Colors.RED,
                    left_title="°C", top_title="Orario",
                    b_labels=x_labels, 
                    min_y=chart1_min_y, max_y=chart1_max_y,
                    min_x=0, max_x=24.5, grid_x=1, grid_y=1
                )
                
                chart2 = _create_line_chart(
                    points=chart2_data, color=ft.Colors.BLUE,
                    left_title="Umidità %" if graph_type==1 else "Soil %", top_title="Orario",
                    b_labels=x_labels,
                    min_y=0, max_y=100,
                    min_x=0, max_x=24.5, grid_x=1, grid_y=5
                )

            # 6. Mostra Dialog
            def close_dlg(e):
                dialog.open = False
                self.main_page.update()

            # Calcola larghezza dialog in base alla finestra
            page_width = app.page.window.width if app.page.window.width else app.page.width
            page_height = app.page.window.height if app.page.window.height else app.page.height

            dialog_width = min(page_width * 0.95, 1400) if page_width else 1300
            dialog_height = min(page_height * 0.95, 800) if page_height else 700

            # --- GESTIONE TRUCCO ANIMAZIONE ---

            # Salviamo i dati originali di chart1
            real_chart1_data = None
            if hasattr(chart1, 'groups'):  # BarChart
                real_chart1_data = chart1.groups
                chart1.groups = [
                    fch.BarChartGroup(
                        x=g.x, 
                        rods=[fch.BarChartRod(to_y=0, width=r.width, color=r.color, border_radius=r.border_radius) for r in g.rods]
                    ) for g in real_chart1_data
                ]
            elif hasattr(chart1, 'data_series'):  # LineChart
                real_chart1_data = chart1.data_series
                chart1.data_series = [
                    fch.LineChartData(
                        points=[fch.LineChartDataPoint(x=p.x, y=chart1.min_y if chart1.min_y is not None else 0) for p in ds.points],
                        stroke_width=ds.stroke_width,
                        rounded_stroke_cap=ds.rounded_stroke_cap,
                        color=ds.color,
                        curved=ds.curved
                    ) for ds in real_chart1_data
                ]

            # Salviamo i dati originali di chart2
            real_chart2_data = None
            if chart2:
                if hasattr(chart2, 'data_series'):  # LineChart
                    real_chart2_data = chart2.data_series
                    chart2.data_series = [
                        fch.LineChartData(
                            points=[fch.LineChartDataPoint(x=p.x, y=chart2.min_y if chart2.min_y is not None else 0) for p in ds.points],
                            stroke_width=ds.stroke_width,
                            rounded_stroke_cap=ds.rounded_stroke_cap,
                            color=ds.color,
                            curved=ds.curved
                        ) for ds in real_chart2_data
                    ]

            controls_list = []
            if graph_type == 3:
                controls_list.append(
                    ft.Row(
                        [
                            ft.Container(width=15, height=15, bgcolor=ft.Colors.BLUE_400),
                            ft.Text("Oggi"),
                            ft.Container(width=15, height=15, bgcolor=ft.Colors.ORANGE_400),
                            ft.Text("Ieri"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                )
            
            controls_list.append(ft.Container(chart1, height=300))
            
            if chart2:
                controls_list.append(ft.Divider())
                controls_list.append(ft.Container(chart2, height=300))

            data_container = ft.Column(
                controls_list,
                scroll=ft.ScrollMode.ALWAYS,
                expand=True
            )

            # DatePicker per cambiare giorno
            def on_date_change(e):
                new_date = e.control.value
                if new_date:
                    dialog.open = False
                    try:
                        self.main_page.overlay.remove(date_picker)
                    except ValueError:
                        pass
                    self.main_page.update()
                    self.show_chart_dialog(target_date=new_date)

            date_picker = ft.DatePicker(
                value=today_date,
                first_date=datetime(2020, 1, 1),
                last_date=datetime(2035, 12, 31),
                on_change=on_date_change
            )
            self.main_page.overlay.append(date_picker)

            def open_picker(e):
                date_picker.open = True
                self.main_page.update()

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Text(f"{self.name or self.topic}", expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CALENDAR_MONTH,
                        tooltip="Seleziona data",
                        on_click=open_picker
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        tooltip="Chiudi",
                        on_click=close_dlg
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                content=ft.Container(
                    content=data_container,
                    width=dialog_width,
                    height=dialog_height
                ),
            )
            
            self.main_page.overlay.append(dialog)
            dialog.open = True
            self.main_page.update()

            def animate_charts():
                try:
                    time.sleep(0.3)
                    if not self.main_page or not getattr(self.main_page, "app", None):
                        return
                    # --- APPLICA DATI ORIGINALI PER FAR SCATTARE ANIMAZIONE ---
                    if real_chart1_data is not None:
                        if hasattr(chart1, 'groups'):
                            chart1.groups = real_chart1_data
                        elif hasattr(chart1, 'data_series'):
                            chart1.data_series = real_chart1_data
                        chart1.update()

                    if chart2 and real_chart2_data is not None:
                        if hasattr(chart2, 'data_series'):
                            chart2.data_series = real_chart2_data
                        chart2.update()
                except Exception as e:
                    log.warning(f"Animazione interrotta o pagina non più valida: {e}")

            threading.Thread(target=animate_charts, daemon=True).start()

        except Exception as e:
            log.error(f"Errore mosta grafico {table_name}: {e}", exc_info=True)
            if hasattr(app, 'show_error_snackbar'):
                 app.show_error_snackbar(f"Errore grafico: {str(e)}")