# -*- coding: utf-8 -*-
"""
Chart Page - Pagina grafici con lettura dati SQL
"""

import flet as ft
import logging
import threading
import json
import os
from common.config import RESPONSIVE_COLS
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

log = logging.getLogger(__name__)

def get_content(app: 'App', title: str = "Chart") -> ft.Column:
    """Restituisce il contenuto della pagina Chart"""
    from components.TitleCard import TitleCard
    
    try:
        # --- STRUTTURA UNIFORMATA ---
        dbm = app.dbm
        tables = dbm.GET_TABLE()
        db_name = dbm.conn_params.get("database", "N/A")
        db_host = dbm.conn_params.get("host", "N/A")

        # 1. TitleBar
        title_bar = TitleCard(
            title=title,
            icon=ft.Icons.SHOW_CHART,
            info_items=[
                f"Database: {db_name}",
                f"Host: {db_host}",
                f"{len(tables)} tabelle"
            ],
            refresh_callback=lambda e: refresh_charts(e),        
            refresh_tooltip=f"Aggiorna dati {title}"
        )

        # 2. Loading indicator
        loading_indicator = ft.Container(
            content=ft.Row([
                ft.ProgressRing(width=20, height=20),
                ft.Text("Caricamento tabelle in corso...", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
            ], spacing=10),
            padding=10, visible=True
        )
        app.page.update()

        # 3. Filter card (DatePicker)
        today = datetime.now().strftime("%Y-%m-%d")
        start_date_value = today
        end_date_value = today
        start_btn_ref = ft.Ref[ft.OutlinedButton]()
        end_btn_ref = ft.Ref[ft.OutlinedButton]()

        def on_start_change(e):
            nonlocal start_date_value
            if e.control.value:
                new_start = e.control.value.strftime("%Y-%m-%d")
                if new_start > end_date_value:
                    log.warning(f"Data inizio {new_start} non può essere dopo data fine {end_date_value}")
                    app.show_error_snackbar("Data inizio non può essere dopo data fine!")
                    start_picker.open = False
                    app.page.update()
                    return
                start_date_value = new_start
                start_btn_ref.current.text = f"Data Inizio: {start_date_value}"
            start_picker.open = False
            refresh_charts(e)

        def on_end_change(e):
            nonlocal end_date_value
            if e.control.value:
                new_end = e.control.value.strftime("%Y-%m-%d")
                if new_end < start_date_value:
                    log.warning(f"Data fine {new_end} non può essere prima di data inizio {start_date_value}")
                    app.show_error_snackbar("Data fine non può essere prima di data inizio!")
                    end_picker.open = False
                    app.page.update()
                    return
                end_date_value = new_end
                end_btn_ref.current.text = f"Data Fine: {end_date_value}"
            end_picker.open = False
            refresh_charts(e)

        start_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
            on_change=on_start_change,
        )
        end_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
            on_change=on_end_change,
        )
        app.page.overlay.append(start_picker)
        app.page.overlay.append(end_picker)

        def open_start_picker(e):
            start_picker.open = True
            app.page.update()

        def open_end_picker(e):
            end_picker.open = True
            app.page.update()

        filters_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.FILTER_LIST, size=32, color=ft.Colors.BLUE_600),
                        title=ft.Text("Filtri Grafici", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                        subtitle=ft.Text("Seleziona intervallo date e valore", theme_style=ft.TextThemeStyle.BODY_SMALL),
                        dense=True,
                    ),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.ResponsiveRow([
                        ft.Container(
                            content=ft.OutlinedButton(
                                ref=start_btn_ref,
                                content=ft.Text(f"Data Inizio: {today}"),
                                icon=ft.Icons.CALENDAR_TODAY,
                                on_click=open_start_picker,
                            ),
                            col=RESPONSIVE_COLS
                        ),
                        ft.Container(
                            content=ft.OutlinedButton(
                                ref=end_btn_ref,
                                content=ft.Text(f"Data Fine: {today}"),
                                icon=ft.Icons.CALENDAR_TODAY,
                                on_click=open_end_picker,
                            ),
                            col=RESPONSIVE_COLS
                        ),
                    ], spacing=10),
                ], spacing=5, run_spacing=5),
                padding=15
            ),
            elevation=2,
            margin=10
        )

        # Crea Column vuota che verrà popolata progressivamente
        tables_grid = ft.Column([], spacing=10)

        # Funzione di refresh
        def refresh_charts(e):
            tables_grid.controls.clear()
            loading_indicator.visible = True
            app.page.update()
            loading_thread = threading.Thread(target=load_tables_progressively, daemon=True, name="DBTableLoader")
            loading_thread.start()

        # Layout principale
        main_column = ft.Column([
            title_bar,
            loading_indicator,
            filters_card,
            tables_grid
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=5,                                                                  #   👀  Spazio tra i gruppi di livelli                  
        margin=ft.Margin(left=0, right=5, top=0, bottom=5),                         #   👀  Margini intera finestra
        expand=True,
        alignment=ft.MainAxisAlignment.START)

        # Carica le tabelle progressivamente in un thread separato
        def load_tables_progressively():
            try:
                app.is_loading = True
                loading_indicator.visible = True
                app.page.update()
                responsive_cols = RESPONSIVE_COLS
                
                for table_name in tables:
                    try:
                        comm_tab = dbm.GET_TABLE_COMMENT(table_name)
                        if comm_tab and len(comm_tab) > 0:
                            raw_comment = str(comm_tab[0])
                            comment_parts = [p.strip() for p in raw_comment.split(",") if p.strip()]
                        else:
                            raw_comment = ""
                            comment_parts = []

                        first_part = comment_parts[0] if comment_parts else ""
                        comment = " - ".join(comment_parts) if comment_parts else ""
                        
                        # Carica configs.json per ottenere sensor_types
                        configs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'configs.json')
                        sensor_types = {}
                        try:
                            with open(configs_path, 'r', encoding='utf-8') as f:
                                configs = json.load(f)
                                sensor_types = configs.get('sensor_types', {})
                        except Exception as ex:
                            log.warning(f"Impossibile caricare configs.json: {ex}")
                        
                        # Determina graph_type e info dal config
                        graph_type = 0
                        sensor_info = sensor_types.get(first_part, {})
                        
                        if sensor_info:
                            vendor = sensor_info.get('vendor', '?')
                            icon = sensor_info.get('icon', '❓')
                            report_fields = sensor_info.get('report_fields', [])
                            
                            log.debug(f"{icon} {vendor}")
                            
                            # Determina graph_type in base ai report_fields
                            if 'TEMPERATURE' in report_fields and 'HUMIDITY' in report_fields:
                                graph_type = 1
                            elif 'TEMPERATURE' in report_fields and 'SOIL_MOISTURE' in report_fields:
                                graph_type = 2
                        else:
                            log.debug(f"❓ No comment on table {table_name}")

                        match graph_type:
                            case 1:
                                try:
                                    start_val = start_date_value
                                    end_val = end_date_value
                                    DATA = dbm.GET_CHART_1(table_name, start_val, end_val)
                                except Exception as ex:
                                    log.warning(f"Errore lettura dati chart {table_name}: {ex}")
                                    DATA = None
                            case 2:
                                try:
                                    start_val = start_date_value
                                    end_val = end_date_value
                                    DATA = dbm.GET_CHART_2(table_name, start_val, end_val)
                                except Exception as ex:
                                    log.warning(f"Errore lettura dati chart {table_name}: {ex}")
                                    DATA = None
                            case _:
                                continue

                        # Estrai dati da DATA per i grafici
                        chart1_data = []
                        chart2_data = []
                        t_values = []
                        h_values = []
                        time_labels = []  # Per tracciare gli orari
                        
                        if DATA:
                            data_with_time = []
                            for row in DATA:
                                try:
                                    date_u = row[0]  # Data (datetime.date o stringa)
                                    time_str = row[1]  # Stringa "HH:MM" o "HH:MM:SS"
                                    t_value = float(row[2])
                                    h_value = float(row[3])
                                    
                                    # Converti stringa "HH:MM" o "HH:MM:SS" in secondi
                                    time_parts = time_str.split(':')
                                    hours = int(time_parts[0])
                                    minutes = int(time_parts[1])
                                    seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                                    total_seconds = hours * 3600 + minutes * 60 + seconds
                                    
                                    data_with_time.append((date_u, total_seconds, t_value, h_value))
                                except (ValueError, TypeError, AttributeError, IndexError) as e:
                                    log.warning(f"Errore parsing dato: {e}")
                                    continue
                        
                            # Riempi i gap di 5 minuti (300 secondi) con il valore precedente
                            if data_with_time:
                                idx = 0
                                prev_t_val = 0
                                prev_h_val = 0
                                prev_date = None
                                
                                for i, (date_u, data_time, t_val, h_val) in enumerate(data_with_time):
                                    # Se non è il primo elemento, controlla il gap
                                    if i > 0:
                                        prev_time = data_with_time[i-1][1]
                                        
                                        # Controlla gap solo se stesso giorno
                                        if date_u == prev_date:
                                            gap = data_time - prev_time
                                            
                                            # Se gap > 5 minuti (300 secondi), aggiungi punti con valore precedente
                                            if gap > 300:
                                                num_missing = int((gap - 300) / 300)
                                                for j in range(1, num_missing + 1):
                                                    missing_time = prev_time + (j * 300)
                                                    hours = missing_time // 3600
                                                    minutes = (missing_time % 3600) // 60
                                                    time_labels.append(f"{hours:02d}:{minutes:02d}")
                                                    chart1_data.append(ft.LineChartDataPoint(x=idx, y=prev_t_val))
                                                    chart2_data.append(ft.LineChartDataPoint(x=idx, y=prev_h_val))
                                                    idx += 1
                                    
                                    # Aggiungi il dato reale
                                    chart1_data.append(ft.LineChartDataPoint(x=idx, y=t_val))
                                    chart2_data.append(ft.LineChartDataPoint(x=idx, y=h_val))
                                    t_values.append(t_val)
                                    h_values.append(h_val)
                                    prev_t_val = t_val
                                    prev_h_val = h_val
                                    prev_date = date_u
                                    hours = data_time // 3600
                                    minutes = (data_time % 3600) // 60
                                    time_labels.append(f"{hours:02d}:{minutes:02d}")
                                    idx += 1
                        
                        # Se nessun dato, usa valori vuoti
                        if not chart1_data:
                            chart1_data = [ft.LineChartDataPoint(x=i, y=0) for i in range(24)]
                        if not chart2_data:
                            chart2_data = [ft.LineChartDataPoint(x=i, y=0) for i in range(24)]
                        
                        # Calcola statistiche
                        t_min = min(t_values) if t_values else 0
                        t_max = max(t_values) if t_values else 0
                        t_avg = sum(t_values) / len(t_values) if t_values else 0
                        h_min = min(h_values) if h_values else 0
                        h_max = max(h_values) if h_values else 0
                        h_avg = sum(h_values) / len(h_values) if h_values else 0
                        
                        # Calcola range dinamico per chart1 (Temperatura)
                        if t_min > 0:
                            chart1_min_y = 0
                            chart1_max_y = t_max + 2
                        else:
                            chart1_min_y = t_min - 2
                            chart1_max_y = t_max + 2
                        
                        # Arrotonda al multiplo di 5 più vicino
                        chart1_min_y = int(chart1_min_y / 5) * 5
                        chart1_max_y = int((chart1_max_y + 4) / 5) * 5  # Arrotonda verso l'alto
                        
                        # Calcola range dinamico per chart2 (Umidità) - sempre tra 0-100
                        chart2_min_y = max(0, h_min - 5)
                        chart2_max_y = min(100, h_max + 5)
                        
                        # Arrotonda al multiplo di 5 più vicino (mantenendo 0-100)
                        chart2_min_y = max(0, int(chart2_min_y / 5) * 5)
                        chart2_max_y = min(100, int((chart2_max_y + 4) / 5) * 5)
                        
                        # Grafico 1 - LineChart (Temperatura)
                        chart1 = ft.LineChart(
                            data_series=[
                                ft.LineChartData(
                                    data_points=chart1_data,
                                    stroke_width=3,
                                    color=ft.Colors.RED,
                                    curved=True,
                                    stroke_cap_round=True,
                                )
                            ],
                            bottom_axis=ft.ChartAxis(
                                title=ft.Text("Ora", size=11, color=ft.Colors.BLACK),
                                labels=[
                                    ft.ChartAxisLabel(
                                        value=i,
                                        label=ft.Text(time_labels[i] if i < len(time_labels) else f"{i}", size=9, color=ft.Colors.BLACK)
                                    )
                                    for i in range(len(time_labels) if time_labels else len(chart1_data))
                                ],
                            ),
                            left_axis=ft.ChartAxis(
                                title=ft.Text("Temperatura (°C)", size=11, color=ft.Colors.BLACK),
                                labels=[
                                    ft.ChartAxisLabel(value=i, label=ft.Text(f"{i}°C", size=10, color=ft.Colors.BLACK))
                                    for i in range(int(chart1_min_y), int(chart1_max_y) + 1, 5)
                                ],
                            ),
                            horizontal_grid_lines=ft.ChartGridLines(
                                color=ft.Colors.GREY_300,
                                width=1,
                                interval=5,
                            ),
                            vertical_grid_lines=ft.ChartGridLines(
                                color=ft.Colors.GREY_300,
                                width=1,
                                interval=5,
                            ),
                            border=ft.Border(
                                top=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                                right=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                                bottom=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                                left=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                            ),
                            interactive=True,
                            animate=500,
                            expand=True,
                            min_y=chart1_min_y,
                            max_y=chart1_max_y,
                        )
                        
                        # Grafico 2 - LineChart (Umidità)
                        chart2 = ft.LineChart(
                            data_series=[
                                ft.LineChartData(
                                    data_points=chart2_data,
                                    stroke_width=3,
                                    color=ft.Colors.BLUE,
                                    curved=True,
                                    stroke_cap_round=True,
                                )
                            ],
                            bottom_axis=ft.ChartAxis(
                                title=ft.Text("Ora", size=11, color=ft.Colors.BLACK),
                                labels=[
                                    ft.ChartAxisLabel(
                                        value=i,
                                        label=ft.Text(time_labels[i] if i < len(time_labels) else f"{i}", size=9, color=ft.Colors.BLACK)
                                    )
                                    for i in range(len(time_labels) if time_labels else len(chart2_data))
                                ],
                            ),
                            left_axis=ft.ChartAxis(
                                title=ft.Text("Umidità (%)", size=11, color=ft.Colors.BLACK),
                                labels=[
                                    ft.ChartAxisLabel(value=i, label=ft.Text(f"{i}%", size=10, color=ft.Colors.BLACK))
                                    for i in range(int(chart2_min_y), int(chart2_max_y) + 1, 5)
                                ],
                            ),
                            horizontal_grid_lines=ft.ChartGridLines(
                                color=ft.Colors.GREY_300,
                                width=1,
                                interval=5,
                            ),
                            vertical_grid_lines=ft.ChartGridLines(
                                color=ft.Colors.GREY_300,
                                width=1,
                                interval=5,
                            ),
                            border=ft.Border(
                                top=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                                right=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                                bottom=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                                left=ft.BorderSide(width=1, color=ft.Colors.GREY_400),
                            ),
                            interactive=True,
                            animate=500,
                            expand=True,
                            min_y=chart2_min_y,
                            max_y=chart2_max_y,
                        )
                        
                        card = ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.ListTile(
                                        title=ft.Text(
                                            table_name if comment == "" else f"{comment}",
                                            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        dense=True,
                                        content_padding=ft.Padding(0, 0, 0, 0),
                                    ),
                                    ft.Divider(height=1, thickness=1),
                                    # Container Grafico Temperatura
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Text(
                                                f"🌡️ Temperatura: Min {t_min:.1f}°C | Max {t_max:.1f}°C | Media {t_avg:.1f}°C",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.RED_700
                                            ),
                                            ft.Container(
                                                content=chart1,
                                                height=250,
                                            ),
                                        ], spacing=5),
                                        padding=10,
                                        bgcolor="secondarycontainer",
                                        border_radius=8,
                                    ),
                                    ft.Divider(height=1),
                                    # Container Grafico Umidità
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Text(
                                                f"💧 Umidità: Min {h_min:.0f}% | Max {h_max:.0f}% | Media {h_avg:.0f}%",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.BLUE_700
                                            ),
                                            ft.Container(
                                                content=chart2,
                                                height=250,
                                            ),
                                        ], spacing=5),
                                        padding=10,
                                        bgcolor="secondarycontainer",
                                        border_radius=8,
                                    ),
                                ], spacing=8),
                                padding=10
                            ),
                            elevation=2,
                            margin=10
                        )

                        tables_grid.controls.append(card)
                        app.page.update()
                        
                    except Exception as e:
                        app.show_error_snackbar(f"Errore caricamento tabella {table_name}: {e}")
                        continue
                
                loading_indicator.visible = False
                app.page.update()
                log.debug(f"✅ Caricamento completato: {len(tables)} tabelle")
                
            except Exception as e:
                log.error(f"Errore caricamento progressivo tabelle: {e}")
            finally:
                app.is_loading = False
                loading_indicator.visible = False
                app.page.update()
                
        # Avvia thread per caricamento progressivo
        loading_thread = threading.Thread(target=load_tables_progressively, daemon=True, name="DBTableLoader")
        loading_thread.start()

        return main_column
        
    except Exception as e:
        log.error(f"Errore caricamento database: {e}", exc_info=True)
        return ft.Column([
            TitleCard(
                title=title,
                icon=ft.Icons.SHOW_CHART,
                icon_color=ft.Colors.INDIGO_600
            ),
            ft.Divider(),
            ft.Container(
                content=ft.Text(f"❌ Errore: {str(e)}", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.RED),
                bgcolor="secondarycontainer",
                padding=20,
                border_radius=10
            )
        ], spacing=15, expand=True, alignment=ft.MainAxisAlignment.START)
    
def show_chart(app: 'App', table_name: str):
    """Mostra il grafico per la tabella selezionata"""
    try:
        log.debug(f"📊 Visualizzazione grafico per tabella: {table_name}")
        
        snack = ft.SnackBar(
            content=ft.Text(f"📊 Grafico {table_name} - In costruzione"),
            bgcolor="secondary",
            duration=2000
        )
        app.page.overlay.append(snack)
        snack.open = True
        app.page.update()
        
    except Exception as e:
        log.error(f"Errore visualizzazione grafico {table_name}: {e}")