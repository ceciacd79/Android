# -*- coding: utf-8 -*-
"""
Calendar Page - Pagina del calendario dell'applicazione
"""

import flet as ft
import inspect as ins
import logging

from common.config import RESPONSIVE_COLS
from common.helpers import get_theme_color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

log = logging.getLogger(__name__)

def get_content(app: 'App', title: str = "Calendario") -> ft.Column:
    """ Restituisce il contenuto della pagina"""
    from components.TitleCard import TitleCard
    
    fix_cards = []

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

    def on_page_event(message):
        # Filtra eventi solo per la pagina attiva
        if app.current_page_index != 4:
            return
        if isinstance(message, dict):
            if message.get("type") == "calendario_updated":
                # Aggiorna la pagina solo se l'evento è pertinente
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

    #   -----   👀  SUBSCRIPTION A EVENTI GLOBALI               👀  -----     #
    subscribe_events()

 #   -----   👀  STRUTTURA UNIFORMATA            👀  -----   #  
    #   ✍🏻      TITLE BAR
    title_bar = TitleCard(
        title=title,
        icon=ft.Icons.PENDING_ACTIONS,
        info_items=[
            "Calendario famiglia"
        ],
        refresh_callback=lambda e: on_page_event({"type": "calendario_updated"}),
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

    # --- CALENDAR CARDS SOPRA LA TABELLA ---
    from components.CalendarCard import CalendarCard
    # --- CALENDAR TIMELINE SETTIMANALE ---
    from datetime import datetime, timedelta
    
    state = {"week_offset": 0}
    calendar_container = ft.Container(
        border=ft.Border.all(1, "outlineVariant"), 
        border_radius=10, 
        bgcolor="surface", 
        padding=0,
        margin=10
    )

    def trigger_scroll(area):
        # Non c'è più la griglia scorrevole, niente scorrimento
        pass

    def render_calendar():
        ora = datetime.now()
        oggi = ora.date()
        
        # Determina inizio settimana (Lun = 0) + offset
        inizio_settimana = (oggi - timedelta(days=oggi.weekday())) + timedelta(weeks=state["week_offset"])
        giorni_da_mostrare = 7
        giorni_settimana_it = ["LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"]
        mesi_it = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
        
        # Controllo navigazione
        def nav_prev(e):
            if state["week_offset"] > 0:
                state["week_offset"] -= 1
                render_calendar()
                calendar_container.update()

        def nav_next(e):
            if state["week_offset"] < 12:
                state["week_offset"] += 1
                render_calendar()
                calendar_container.update()
                
        def nav_oggi(e):
            state["week_offset"] = 0
            render_calendar()
            calendar_container.update()

        # Dati intestazione (Mese, Anno, Settimana)
        target_month_name = mesi_it[inizio_settimana.month - 1]
        target_year = inizio_settimana.year
        week_num = inizio_settimana.isocalendar()[1]

        # Pre-calcolo eventi per giorno
        import datetime as dt_mod
        
        def parse_date(d):
            if isinstance(d, datetime):
                return d.date()
            if isinstance(d, dt_mod.date):
                return d
            if isinstance(d, str):
                try:
                    if "T" in d:
                        return datetime.fromisoformat(d.replace("Z", "+00:00")).date()
                    return datetime.strptime(d, "%Y-%m-%d").date()
                except Exception:
                    pass
            return None

        eventi_per_giorno = []
        has_allday_in_week = False
        
        for i in range(giorni_da_mostrare):
            g_date = inizio_settimana + timedelta(days=i)
            evs = []
            if app.calendario and isinstance(app.calendario, list):
                for evento in app.calendario:
                    inizio = evento.get("inizio")
                    fine = evento.get("fine")
                    if inizio:
                        start_date = parse_date(inizio)
                        end_date = parse_date(fine) if fine else start_date
                        
                        if start_date:
                            if end_date is None:
                                end_date = start_date
                            elif not isinstance(fine, datetime) and end_date > start_date:
                                end_date = end_date - timedelta(days=1)
                                
                            if start_date <= g_date <= end_date:
                                evs.append(evento)
                                
                                is_all = (not isinstance(inizio, datetime)) or (end_date and start_date and end_date > start_date)
                                if is_all:
                                    has_allday_in_week = True
                                        
            eventi_per_giorno.append(evs)
            
        nav_row = ft.Row([
            ft.Container(
                content=ft.IconButton(icon=ft.Icons.TODAY, on_click=nav_oggi, tooltip="Torna a oggi", icon_size=24),
                padding=ft.Padding(right=15)
            ),
            ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=nav_prev, disabled=(state["week_offset"] <= 0)),
            ft.Container(
                content=ft.Text(f"Settimana {week_num}", size=11, color="white"), 
                bgcolor="onSurfaceVariant", 
                padding=ft.Padding.symmetric(horizontal=8, vertical=2), 
                border_radius=12
            ),
            ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=nav_next, disabled=(state["week_offset"] >= 12)),
            ft.Text(f"{target_month_name} {target_year}", size=20, weight="bold"),
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)

        # Funzioni utli per posizionamento eventi
        def get_start_time(ev):
            start = ev.get("inizio")
            return (start.hour, start.minute) if isinstance(start, datetime) else (0, 0)
                 
        def overlaps(ev1, ev2):
            start1 = get_start_time(ev1)
            end1 = (ev1.get("fine").hour, ev1.get("fine").minute) if isinstance(ev1.get("fine"), datetime) else start1
            start2 = get_start_time(ev2)
            end2 = (ev2.get("fine").hour, ev2.get("fine").minute) if isinstance(ev2.get("fine"), datetime) else start2
            return start1 < end2 and start2 < end1 if start1 != end1 and start2 != end2 else start1 == start2

        # --- VISTA MOBILE (Tutto in 1 Colonna) ---
        mobile_giorni_cols = []
        for i in range(giorni_da_mostrare):
            g_date = inizio_settimana + timedelta(days=i)
            is_oggi = (g_date == oggi)
            has_events = len(eventi_per_giorno[i]) > 0
            
            day_content = ft.Row([
                ft.Text(giorni_settimana_it[g_date.weekday()], size=12, weight="bold", color="blue" if is_oggi else "onSurfaceVariant"),
                ft.Container(
                    content=ft.Text(str(g_date.day), color="white" if is_oggi else "onSurface", weight="bold", size=16),
                    bgcolor="blue" if is_oggi else None,
                    shape=ft.BoxShape.CIRCLE,
                    width=30, height=30,
                    alignment=ft.Alignment.CENTER
                )
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)

            if has_events:
                day_content.controls.append(ft.Container(width=6, height=6, border_radius=3, bgcolor="red"))
            
            day_col = ft.Column(spacing=5, expand=1)

            day_col.controls.append(ft.Container(
                content=day_content,
                alignment=ft.Alignment.CENTER, 
                padding=5,
                border=ft.Border.only(bottom=ft.BorderSide(1, "outlineVariant"))
            ))

            allday_giorno = []
            for ev in eventi_per_giorno[i]:
                in_dt = ev.get("inizio")
                out_dt = ev.get("fine")
                start_dt = parse_date(in_dt)
                end_dt = parse_date(out_dt) if out_dt else start_dt
                if not isinstance(out_dt, datetime) and end_dt and start_dt and end_dt > start_dt:
                    end_dt = end_dt - timedelta(days=1)
                
                if (not isinstance(in_dt, datetime)) or (end_dt and start_dt and end_dt > start_dt):
                    allday_giorno.append(ev)

            for ev in allday_giorno:
                info_list = [x for x in [ev.get("posizione"), ev.get("creatore"), ev.get("descrizione")] if x]
                chip = CalendarCard(
                    calendar_name=ev.get("titolo", "Evento"), info_items=info_list,
                    inizio=ev.get("inizio"), fine=ev.get("fine"), creatore=ev.get("creatore"),
                    posizione=ev.get("posizione"), descrizione=ev.get("descrizione"),
                    is_all_day=True, scaduto=ev.get("scaduto", False), ev_data=ev
                )
                day_col.controls.append(ft.Container(content=chip, tooltip=ev.get("descrizione"), padding=ft.Padding.symmetric(horizontal=1)))

            eventi_orari_giorno = [ev for ev in eventi_per_giorno[i] if ev not in allday_giorno]
            eventi_orari_giorno.sort(key=get_start_time)
            
            current_row_group = []
            groups = []
            for ev in eventi_orari_giorno:
                if not current_row_group: current_row_group.append(ev)
                else:
                    if any(overlaps(ev, e) for e in current_row_group): current_row_group.append(ev)
                    else:
                        groups.append(current_row_group)
                        current_row_group = [ev]
            if current_row_group: groups.append(current_row_group)
                
            for group in groups:
                row_ctrls = []
                for ev in group:
                    in_dt = ev.get("inizio")
                    out_dt = ev.get("fine")
                    str_orario = ""
                    if isinstance(in_dt, datetime):
                        str_orario = f"{in_dt.strftime('%H:%M')}"
                        if out_dt and isinstance(out_dt, datetime): str_orario += f" - {out_dt.strftime('%H:%M')}"
                    info_list = [x for x in [str_orario, ev.get('posizione'), ev.get('creatore')] if x]
                    tooltip_text = f"{ev.get('titolo', 'Evento')}\n{str_orario}\n{ev.get('descrizione', '')}".strip()
                    card_content = CalendarCard(
                        calendar_name=ev.get("titolo", "Evento"), info_items=info_list,
                        inizio=ev.get("inizio"), fine=ev.get("fine"), creatore=ev.get("creatore"),
                        posizione=ev.get("posizione"), descrizione=ev.get("descrizione"),
                        is_all_day=False, scaduto=ev.get("scaduto", False), ev_data=ev
                    )
                    row_ctrls.append(ft.Container(content=card_content, tooltip=tooltip_text, expand=1, padding=ft.Padding.symmetric(horizontal=1)))
                day_col.controls.append(ft.Row(row_ctrls, spacing=2))
                
            mobile_giorni_cols.append(ft.Container(
                content=day_col, 
                padding=ft.Padding.all(5),
                border=ft.Border.all(1, "outlineVariant"),
                border_radius=5
            ))

        mobile_view = ft.Container(
            content=ft.Column(mobile_giorni_cols, spacing=10),
            col={"xs": 12, "md": 0}
        )

        # --- VISTA DESKTOP (7 Colonne affiancate con header top per multi-day) ---
        desktop_header_cols = []
        for i in range(giorni_da_mostrare):
            g_date = inizio_settimana + timedelta(days=i)
            is_oggi = (g_date == oggi)
            has_events = len(eventi_per_giorno[i]) > 0
            
            day_content = ft.Row([
                ft.Text(giorni_settimana_it[g_date.weekday()], size=12, weight="bold", color="blue" if is_oggi else "onSurfaceVariant"),
                ft.Container(
                    content=ft.Text(str(g_date.day), color="white" if is_oggi else "onSurface", weight="bold", size=16),
                    bgcolor="blue" if is_oggi else None,
                    shape=ft.BoxShape.CIRCLE, width=30, height=30, alignment=ft.Alignment.CENTER
                )
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)

            if has_events: day_content.controls.append(ft.Container(width=6, height=6, border_radius=3, bgcolor="red"))
            desktop_header_cols.append(ft.Container(content=day_content, expand=1, border=ft.Border.only(left=ft.BorderSide(1, "outlineVariant")) if i > 0 else None, alignment=ft.Alignment.CENTER, padding=5))

        allday_events_unique = []
        for i in range(giorni_da_mostrare):
            for ev in eventi_per_giorno[i]:
                in_dt = ev.get("inizio")
                out_dt = ev.get("fine")
                start_dt = parse_date(in_dt)
                end_dt = parse_date(out_dt) if out_dt else start_dt
                if not isinstance(out_dt, datetime) and end_dt and start_dt and end_dt > start_dt:
                    end_dt = end_dt - timedelta(days=1)
                is_all = (not isinstance(in_dt, datetime)) or (end_dt and start_dt and end_dt > start_dt)
                if is_all and ev not in [a["ev"] for a in allday_events_unique]:
                    clip_start = max(0, (start_dt - inizio_settimana).days)
                    clip_end = min(giorni_da_mostrare - 1, (end_dt - inizio_settimana).days)
                    allday_events_unique.append({"ev": ev, "start": clip_start, "end": clip_end})
                    
        allday_tracks = []
        for aev in allday_events_unique:
            placed = False
            for track in allday_tracks:
                if all(aev["start"] > t["end"] or aev["end"] < t["start"] for t in track):
                    track.append(aev)
                    placed = True
                    break
            if not placed: allday_tracks.append([aev])
                
        allday_stack_col = ft.Column(spacing=2)
        for track in allday_tracks:
            track.sort(key=lambda x: x["start"])
            row_ctrls = []
            curr_idx = 0
            for item in track:
                if item["start"] > curr_idx: row_ctrls.append(ft.Container(expand=item["start"] - curr_idx))
                ev = item["ev"]
                info_list = [x for x in [ev.get("posizione"), ev.get("creatore"), ev.get("descrizione")] if x]
                chip = CalendarCard(
                    calendar_name=ev.get("titolo", "Evento"), info_items=info_list,
                    inizio=ev.get("inizio"), fine=ev.get("fine"), creatore=ev.get("creatore"),
                    posizione=ev.get("posizione"), descrizione=ev.get("descrizione"),
                    is_all_day=True, scaduto=ev.get("scaduto", False), ev_data=ev
                )
                row_ctrls.append(ft.Container(content=chip, tooltip=ev.get("descrizione"), expand=item["end"] - item["start"] + 1, padding=ft.Padding.symmetric(horizontal=1)))
                curr_idx = item["end"] + 1
            if curr_idx < giorni_da_mostrare: row_ctrls.append(ft.Container(expand=giorni_da_mostrare - curr_idx))
            allday_stack_col.controls.append(ft.Row(row_ctrls, spacing=0))

        desktop_giorni_cols = []
        for i in range(giorni_da_mostrare):
            day_col = ft.Column(spacing=5, expand=1)
            eventi_orari_giorno = []
            for ev in eventi_per_giorno[i]:
                in_dt = ev.get("inizio")
                out_dt = ev.get("fine")
                start_date = parse_date(in_dt)
                end_date = parse_date(out_dt) if out_dt else start_date
                if not isinstance(out_dt, datetime) and end_date and start_date and end_date > start_date:
                    end_date = end_date - timedelta(days=1)
                is_all_day = (not isinstance(in_dt, datetime)) or (end_date and start_date and end_date > start_date)
                if not is_all_day: eventi_orari_giorno.append(ev)
                    
            eventi_orari_giorno.sort(key=get_start_time)
            
            current_row_group = []
            groups = []
            for ev in eventi_orari_giorno:
                if not current_row_group: current_row_group.append(ev)
                else:
                    if any(overlaps(ev, e) for e in current_row_group): current_row_group.append(ev)
                    else:
                        groups.append(current_row_group)
                        current_row_group = [ev]
            if current_row_group: groups.append(current_row_group)
                
            for group in groups:
                row_ctrls = []
                for ev in group:
                    in_dt = ev.get("inizio")
                    out_dt = ev.get("fine")
                    str_orario = ""
                    if isinstance(in_dt, datetime):
                        str_orario = f"{in_dt.strftime('%H:%M')}"
                        if out_dt and isinstance(out_dt, datetime): str_orario += f" - {out_dt.strftime('%H:%M')}"
                    info_list = [x for x in [str_orario, ev.get('posizione'), ev.get('creatore')] if x]
                    tooltip_text = f"{ev.get('titolo', 'Evento')}\n{str_orario}\n{ev.get('descrizione', '')}".strip()
                    card_content = CalendarCard(
                        calendar_name=ev.get("titolo", "Evento"), info_items=info_list,
                        inizio=ev.get("inizio"), fine=ev.get("fine"), creatore=ev.get("creatore"),
                        posizione=ev.get("posizione"), descrizione=ev.get("descrizione"),
                        is_all_day=False, scaduto=ev.get("scaduto", False), ev_data=ev
                    )
                    row_ctrls.append(ft.Container(content=card_content, tooltip=tooltip_text, expand=1, padding=ft.Padding.symmetric(horizontal=1)))
                day_col.controls.append(ft.Row(row_ctrls, spacing=2))
                
            desktop_giorni_cols.append(ft.Container(content=day_col, expand=1, padding=ft.Padding.all(2), border=ft.Border.only(left=ft.BorderSide(1, "outlineVariant")) if i > 0 else None))

        desktop_calendar_cols = [ft.Row(desktop_header_cols, spacing=0), ft.Divider(height=1, color="outlineVariant")]
        if has_allday_in_week:
            desktop_calendar_cols.append(ft.Container(content=allday_stack_col, padding=ft.Padding(bottom=5, top=5)))
            desktop_calendar_cols.append(ft.Divider(height=1, color="outlineVariant"))
        desktop_calendar_cols.append(ft.Row(desktop_giorni_cols, spacing=0, vertical_alignment=ft.CrossAxisAlignment.START))

        desktop_view = ft.Container(
            content=ft.Column(desktop_calendar_cols, spacing=0),
            col={"xs": 0, "md": 12}
        )

        responsive_body = ft.ResponsiveRow(
            [mobile_view, desktop_view], 
            columns=12,
            spacing=0,
            run_spacing=0
        )
        
        scrollable_col = ft.Column([responsive_body])
        
        calendar_cols = [
            ft.Container(nav_row, padding=ft.Padding(left=10, top=5, bottom=0)),
            ft.Divider(height=1, color="outlineVariant"),
            ft.Container(content=scrollable_col)
        ]
        
        calendar_container.content = ft.Column(calendar_cols, spacing=0)

        return None

    # Genera la configurazione iniziale per la UI
    render_calendar()

    cards_row = calendar_container

    # Variabili vuote inutilizzate per non disturbare il layout
    table_container = ft.Container(visible=False)

    col = ft.Column([
        title_bar,
        loading_indicator,
        cards_row,
        table_container,
        ft.ResponsiveRow([
            *(ft.Container(card, col=RESPONSIVE_COLS) for card in fix_cards)
        ], spacing=5)
    ],
    scroll=ft.ScrollMode.AUTO,
    spacing=5,                                                                  #   👀  Spazio tra i gruppi di livelli                  
    margin=ft.Margin(left=0, right=5, top=0, bottom=5),                         #   👀  Margini intera finestra
    expand=True,
    alignment=ft.MainAxisAlignment.START)

    if app.page:
        app.page.update()
    return col