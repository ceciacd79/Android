# -*- coding: utf-8 -*-
"""
Database Page - Pagina gestione database
"""

import flet as ft
import logging
import threading
from common.config import RESPONSIVE_COLS, AppStyle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

log = logging.getLogger(__name__)

def get_content(app: 'App', title: str = "DataBase") -> ft.Column:  
    """Restituisce il contenuto della pagina Database"""
    from components.TitleCard import TitleCard

    #   -----   👀  FUNZIONI INTERNE                👀  -----   #
    def reload_page(e=None):
        """Ricarica la pagina corrente e rimuove la subscription specifica della pagina."""
        log.debug(f"Ricaricamento pagina {app.current_page_index} richiesto dall'utente.")
        try:
            # Rimuovi l'handler della pagina se presente
            if hasattr(app, '_database_page_listener'):
                if hasattr(app.page.pubsub, "remove_listener"):
                    app.page.pubsub.remove_listener(app._database_page_listener)
                elif hasattr(app.page.pubsub, "unsubscribe"):
                    app.page.pubsub.unsubscribe()
                del app._database_page_listener
            # Reset cache
            if app.current_page_index in app.pages_cache:
                del app.pages_cache[app.current_page_index]
            # Ricarica contenuto
            app.content_container.content = app.get_page_content(app.current_page_index)
            app.content_container.update()
        except Exception as ex:
            log.error(f"Errore durante il reload della pagina: {ex}")

    def on_page_event(message):
        # Filtra eventi solo per la pagina attiva
        if app.current_page_index != app.PAGE_DATABASE:
            return
        if isinstance(message, dict) and message.get("type") == "database_updated":
            if app.current_page_index in app.pages_cache:
                del app.pages_cache[app.current_page_index]
            app.content_container.content = app.get_page_content(app.current_page_index)
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

    #   -----   👀  SUBSCRIPTION SOLO QUANDO LA PAGINA È ATTIVA 👀  -----     #
    # Registra l'handler solo quando la pagina è attiva
        subscribe_events()

    #   -----   👀  STRUTTURA UNIFORMATA            👀  -----   #  
    #   ✍🏻      TITLE BAR
    title_bar = TitleCard(
        title=title,
        icon=ft.Icons.STORAGE,
        info_items=[
            "Gestione database e tabelle"
        ],
            refresh_callback=lambda e: on_page_event({"type": "database_updated"}),
        refresh_tooltip=f"Aggiorna dati {title}"
    )

    #   ✍🏻      LOADING INDICATOR
    loading_indicator = ft.Container(
        content=ft.Row([
            ft.ProgressRing(width=20, height=20),
            ft.Text("Caricamento tabelle in corso...", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
        ], spacing=10),
        padding=10, visible=True
    )
    app.page.update()

    #   ✍🏻      FILTER CARD (esempio generico)
    filters_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.FILTER_LIST, size=14, color='on_primary_container'),
                    title=ft.Text("Filtri Database", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    subtitle=ft.Text("Filtri rapidi per la pagina database", theme_style=ft.TextThemeStyle.BODY_SMALL),
                    dense=True,
                ),
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                ft.Row([
                    # Esempio: aggiungi qui eventuali filtri per database
                ], spacing=10),
            ], spacing=5),
            padding=15
        ),
        elevation=2,
        margin=10,
        visible=False
    )

    #   -----   👀  CONTENUTO ORIGINALE DELLA PAGINA     👀  -----   #
    try:
        if not hasattr(app, 'dbm') or app.dbm is None:
            return ft.Column([
                title_bar,
                loading_indicator,
                filters_card,
                ft.Container(
                    content=ft.Text("⚠️ Database non configurato", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    bgcolor="secondarycontainer",
                    padding=AppStyle.PADDING,
                    border_radius=AppStyle.CORNER_RADIUS
                )
            ], 
            scroll=ft.ScrollMode.AUTO,
            spacing=5,                                                                  #   👀  Spazio tra i gruppi di livelli                  
            margin=ft.Margin(left=0, right=5, top=0, bottom=5),                         #   👀  Margini intera finestra
            expand=True,
            alignment=ft.MainAxisAlignment.START)
        
        dbm = app.dbm
        tables = dbm.GET_TABLE()
        
        if not tables:
            return ft.Column([
                title_bar,
                loading_indicator,
                filters_card,
                ft.Container(
                    content=ft.Text("⚠️ Nessuna tabella trovata", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    bgcolor="secondarycontainer",
                    padding=AppStyle.PADDING,
                    border_radius=AppStyle.CORNER_RADIUS
                )
            ], 
            scroll=ft.ScrollMode.AUTO,
            spacing=5,                                                                  #   👀  Spazio tra i gruppi di livelli                  
            margin=ft.Margin(left=0, right=5, top=0, bottom=5),                         #   👀  Margini intera finestra
            expand=True,
            alignment=ft.MainAxisAlignment.START)
        
        db_name = dbm.conn_params.get("database", "N/A")
        db_host = dbm.conn_params.get("host", "N/A")
    
        # Crea ResponsiveRow vuota che verrà popolata progressivamente
        tables_grid = ft.ResponsiveRow([], spacing=10, run_spacing=10)
        
        # Lista per tracciare i pulsanti
        all_buttons = []
        
        # Layout principale
        main_column = ft.Column([
            title_bar,
            loading_indicator,
            filters_card,
            # Grid responsive con le card delle tabelle (inizialmente vuota)
            ft.Container(
                content=tables_grid,
                padding=0,
                margin=ft.Margin.only(left=10, right=10)
            )
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
                        row_count = dbm.GET_TABLE_ROW_COUNT(table_name)
                        columns = dbm.GET_TABLE_COLUMNS(table_name)
                        comm_tab = dbm.GET_TABLE_COMMENT(table_name)
                        if comm_tab and len(comm_tab) > 0:
                            raw_comment = str(comm_tab[0])
                            comment_parts = [p.strip() for p in raw_comment.split(",") if p.strip()]
                        else:
                            raw_comment = ""
                            comment_parts = []

                        first_part = comment_parts[0] if comment_parts else ""
                        comment = " - ".join(comment_parts) if comment_parts else ""
                        
                        btn_visualizza = ft.TextButton(
                            "Visualizza",
                            icon=ft.Icons.VISIBILITY,
                            on_click=lambda e, tn=table_name: show_table_data(app, tn),
                            disabled=True
                        )
                        btn_struttura = ft.TextButton(
                            "Struttura",
                            icon=ft.Icons.SCHEMA,
                            on_click=lambda e, tn=table_name: show_table_structure(app, tn),
                            disabled=True
                        )
                        
                        all_buttons.extend([btn_visualizza, btn_struttura])
                        
                        card = ft.Card(
                            content=ft.Container(
                                bgcolor="secondarycontainer",
                                border_radius=AppStyle.CORNER_RADIUS,
                                content=ft.Column([
                                    ft.ListTile(
                                        leading=ft.Icon(ft.Icons.TABLE_CHART, size=14, color='on_primary_container'),
                                        dense=True,
                                        content_padding=ft.Padding.all(0),
                                        title=ft.Text(table_name if comment == "" else f"{comment}", 
                                                      theme_style=ft.TextThemeStyle.BODY_SMALL),
                                        subtitle=ft.Text(f"📊 {row_count} row.", theme_style=ft.TextThemeStyle.BODY_MEDIUM),
                                    ),
                                    ft.Row([
                                        btn_visualizza,
                                        btn_struttura,
                                    ], alignment=ft.MainAxisAlignment.END)
                                ], spacing=5),
                                padding=AppStyle.PADDING
                            ),
                            elevation=2,
                            margin=0
                        )
                        
                        card_container = ft.Container(
                            content=card,
                            col=responsive_cols
                        )
                        
                        tables_grid.controls.append(card_container)
                        app.page.update()
                        
                    except Exception as e:
                        log.error(f"Errore lettura tabella {table_name}: {e}")
                        continue
                
                loading_indicator.visible = False
                app.page.update()
                
                for btn in all_buttons:
                    btn.disabled = False
                
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
            ft.Text("🗄️ DataBase", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
            ft.Divider(),
            ft.Container(
                content=ft.Text(f"❌ Errore: {str(e)}", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.RED),
                bgcolor="secondarycontainer",
                padding=20,
                border_radius=10
            )
        ], spacing=15, expand=True, alignment=ft.MainAxisAlignment.START)

def show_table_data(app: 'App', table_name: str):
    """Mostra i dati della tabella in un dialog con navigazione a pagine"""
    try:
        dbm = app.dbm
        
        # Variabili per la paginazione
        current_page = [0]  # Usa lista per mutabilità in closure
        
        # Ottieni il numero totale di righe
        total_rows = dbm.GET_TABLE_ROW_COUNT(table_name)
        
        # Dropdown per selezionare il numero di righe
        limit_dropdown = ft.Dropdown(
            label="Righe per pagina",
            value="25",
            options=[
                ft.dropdown.Option("25", "25 righe"),
                ft.dropdown.Option("50", "50 righe"),
                ft.dropdown.Option("100", "100 righe"),
            ],
            width=150
        )
        
        # Container per il DataTable
        data_container = ft.Column([], scroll=ft.ScrollMode.ALWAYS, expand=True, horizontal_alignment=ft.CrossAxisAlignment.START)
        
        # Pulsanti di navigazione
        btn_first = ft.IconButton(
            icon=ft.Icons.FIRST_PAGE,
            tooltip="Prima pagina",
            disabled=True
        )
        
        btn_prev = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Pagina precedente",
            disabled=True
        )
        
        btn_next = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD,
            tooltip="Pagina successiva",
            disabled=False
        )
        
        btn_last = ft.IconButton(
            icon=ft.Icons.LAST_PAGE,
            tooltip="Ultima pagina",
            disabled=False
        )
        
        # Text per mostrare info pagina
        page_info_text = ft.Text("", theme_style=ft.TextThemeStyle.BODY_SMALL)
        
        # Funzione per caricare i dati
        def load_data():
            try:
                # Disabilita tutti i pulsanti durante il caricamento
                btn_first.disabled = True
                btn_prev.disabled = True
                btn_next.disabled = True
                btn_last.disabled = True
                limit_dropdown.disabled = True
                app.page.update()
                
                limit = int(limit_dropdown.value)
                offset = current_page[0] * limit
                
                # Usa il nuovo metodo con offset
                columns_info = dbm.GET_TABLE_COLUMNS(table_name)
                
                # Verifica che ci siano colonne
                if not columns_info:
                    app.show_error_snackbar("⚠️ Tabella senza colonne")
                    try:
                        # Rimuovi l'handler della pagina se presente
                        if hasattr(app, '_database_page_listener'):
                            if hasattr(app.page.pubsub, "remove_listener"):
                                app.page.pubsub.remove_listener(app._database_page_listener)
                            elif hasattr(app.page.pubsub, "unsubscribe"):
                                app.page.pubsub.unsubscribe(app._database_page_listener)
                            del app._database_page_listener
                        # Reset cache
                        if app.current_page_index in app.pages_cache:
                            del app.pages_cache[app.current_page_index]
                        # Ricarica contenuto
                        app.content_container.content = app.get_page_content(app.current_page_index)
                        app.content_container.update()
                    except Exception as ex:
                        log.error(f"Errore durante il reload della pagina: {ex}")
                    data_container.controls.clear()
                    data_container.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.INFO_OUTLINE, size=24, color=ft.Colors.GREY_400),
                                ft.Text("Nessun dato presente nella tabella", 
                                       theme_style=ft.TextThemeStyle.BODY_LARGE,
                                       color=ft.Colors.GREY_600)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                            padding=40,
                            alignment=ft.Alignment.CENTER
                        )
                    )
                    page_info_text.value = f"Tabella vuota • 0 righe"
                    btn_first.disabled = True
                    btn_prev.disabled = True
                    btn_next.disabled = True
                    btn_last.disabled = True
                    app.page.update()
                    return
                
                # Crea DataTable
                data_table = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD)) for col in column_names],
                    rows=[
                        ft.DataRow(
                            cells=[ft.DataCell(ft.Text(str(cell))) for cell in row]
                        )
                        for row in data
                    ],
                    border=ft.Border.all(1, ft.Colors.GREY_400),
                    border_radius=10,
                    vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
                    horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
                )
                
                # Calcola dimensioni
                page_width = app.page.window.width if app.page.window.width else app.page.width
                dialog_width = min(page_width * 0.9, 1400) if page_width else 1200
                
                # Aggiorna il container con i dati
                data_container.controls.clear()
                data_container.controls.append(
                    ft.Container(
                        content=data_table,
                        width=max(len(column_names) * 150, dialog_width),
                    )
                )
                
                # Aggiorna info pagina
                start_row = offset + 1
                end_row = min(offset + limit, total_rows)
                total_pages = max((total_rows + limit - 1) // limit, 1)  # Almeno 1 pagina
                current_page_num = current_page[0] + 1
                max_page = total_pages - 1
                
                page_info_text.value = f"Pagina {current_page_num} di {total_pages} • Righe {start_row}-{end_row} di {total_rows}"
                
                # Aggiorna stato pulsanti ALLA FINE
                btn_first.disabled = current_page[0] == 0
                btn_prev.disabled = current_page[0] == 0
                btn_next.disabled = current_page[0] >= max_page or total_rows == 0
                btn_last.disabled = current_page[0] >= max_page or total_rows == 0
                limit_dropdown.disabled = False
                
                app.page.update()
                
            except Exception as e:
                log.error(f"Errore caricamento dati: {e}", exc_info=True)
                # Riabilita i pulsanti anche in caso di errore
                btn_first.disabled = False
                btn_prev.disabled = False
                btn_next.disabled = False
                btn_last.disabled = False
                limit_dropdown.disabled = False
                app.show_error_snackbar(f"Errore: {str(e)}")
        
        # Callback per il dropdown
        def on_limit_change(e):
            current_page[0] = 0  # Reset alla prima pagina
            load_data()
        
        # Callback per navigazione
        def on_first_click(e):
            current_page[0] = 0
            load_data()
        
        def on_prev_click(e):
            if current_page[0] > 0:
                current_page[0] -= 1
                load_data()
        
        def on_next_click(e):
            limit = int(limit_dropdown.value)
            max_page = (total_rows + limit - 1) // limit - 1
            if current_page[0] < max_page:
                current_page[0] += 1
                load_data()
        
        def on_last_click(e):
            limit = int(limit_dropdown.value)
            max_page = (total_rows + limit - 1) // limit - 1
            current_page[0] = max_page
            load_data()
        
        limit_dropdown.on_change = on_limit_change
        btn_first.on_click = on_first_click
        btn_prev.on_click = on_prev_click
        btn_next.on_click = on_next_click
        btn_last.on_click = on_last_click
        
        # Calcola dimensioni basate sulla pagina
        page_width = app.page.window.width if app.page.window.width else app.page.width
        page_height = app.page.window.height if app.page.window.height else app.page.height
        
        dialog_width = min(page_width * 0.9, 1400) if page_width else 1200
        dialog_height = min(page_height * 0.8, 800) if page_height else 600
        
        # Crea dialog con scroll bidimensionale e controlli di navigazione
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Text(f"📊 Dati: {table_name}", expand=True, theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    tooltip="Chiudi",
                    on_click=lambda e: close_dialog(app, dialog)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(
                content=ft.Column([
                    # DataTable con scroll
                    data_container,
                    ft.Divider(height=1),
                    # Barra inferiore con tutti i controlli
                    ft.Row([
                        # Gruppo pulsanti navigazione a sinistra
                        ft.Row([
                            btn_first,
                            btn_prev,
                            btn_next,
                            btn_last,
                        ], spacing=5),
                        # Info pagina al centro (expand)
                        ft.Container(
                            content=page_info_text,
                            expand=True,
                            alignment=ft.Alignment.CENTER
                        ),
                        # Dropdown a destra
                        limit_dropdown,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=10),
                width=dialog_width,
                height=dialog_height
            ),
        )
        
        app.page.overlay.append(dialog)
        dialog.open = True
        app.page.update()
        
        # Carica i dati iniziali (prima pagina, 25 righe)
        load_data()
        
    except Exception as e:
        log.error(f"Errore visualizzazione dati {table_name}: {e}")
        app.show_error_snackbar(f"Errore: {str(e)}")

def show_table_structure(app: 'App', table_name: str):
    """Mostra la struttura della tabella in un dialog"""
    try:
        dbm = app.dbm
        
        # Usa il metodo dedicato
        columns = dbm.GET_TABLE_COLUMNS(table_name)
        
        # Crea DataTable per struttura
        structure_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Campo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Null", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Key", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Default", weight=ft.FontWeight.BOLD)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(col[0]))),
                        ft.DataCell(ft.Text(str(col[1]))),
                        ft.DataCell(ft.Text(str(col[2]))),
                        ft.DataCell(ft.Text(str(col[3]))),
                        ft.DataCell(ft.Text(str(col[4]) if col[4] else "")),
                    ]
                )
                for col in columns
            ],
            border=ft.Border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
        )
        
        # Calcola dimensioni basate sulla pagina
        page_width = app.page.window.width if app.page.window.width else app.page.width
        page_height = app.page.window.height if app.page.window.height else app.page.height
        
        dialog_width = min(page_width * 0.7, 900) if page_width else 700
        dialog_height = min(page_height * 0.7, 600) if page_height else 500
        
        # Crea dialog con scroll bidimensionale
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Text(f"🔢 Struttura: {table_name}", expand=True, theme_style=ft.TextThemeStyle.BODY_MEDIUM),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    tooltip="Chiudi",
                    on_click=lambda e: close_dialog(app, dialog)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=structure_table,
                        width=max(800, dialog_width),  # Larghezza minima per attivare scroll
                    )
                ], scroll=ft.ScrollMode.ALWAYS, horizontal_alignment=ft.CrossAxisAlignment.START),
                width=dialog_width,
                height=dialog_height
            ),
        )
        
        app.page.overlay.append(dialog)
        dialog.open = True
        app.page.update()
        
    except Exception as e:
        log.error(f"Errore visualizzazione struttura {table_name}: {e}")
        app.show_error_snackbar(f"Errore: {str(e)}")

def close_dialog(app: 'App', dialog):
    """Chiude il dialog"""
    dialog.open = False
    app.page.update()

def refresh_database_page(app: 'App'):
    """Ricarica la pagina database"""
    try:
        app.content_container.content = get_content(app)
        app.page.update()
        
        snack = ft.SnackBar(
            content=ft.Text("✅ Database aggiornato!"),
            bgcolor=ft.Colors.GREEN_700,
            duration=2000
        )
        app.page.overlay.append(snack)
        snack.open = True
        app.page.update()
        
    except Exception as e:
        log.error(f"Errore refresh database: {e}")
        app.show_error_snackbar(f"Errore: {str(e)}")