import asyncio
import flet as ft
import flet_charts as fch
import logging

from common.config import AppStyle
from datetime import datetime, timedelta

log = logging.getLogger(__name__)

loc_enel = {}
NORMAL_RADIUS = 45
HOVER_RADIUS = 55
NORMAL_STYLE = ft.TextStyle(size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
HOVER_STYLE = ft.TextStyle(
    size=14, 
    color=ft.Colors.WHITE, 
    weight=ft.FontWeight.BOLD,
    shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK54)
)
NORMAL_BADGE_SIZE = 30
HOVER_BADGE_SIZE = 40

class ConsWidget(ft.Container):
    def __init__(self, app, title="Consumi", tab=None, **kwargs):
        super().__init__()
        self.app = app
        self.title = title
        self.tab = tab
        self.last_data = {} # Per conservare i dati durante l'hover
        self.hover_idx = -1 # Traccia quale sezione è sotto il mouse

        self.animate_opacity = ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
        self.animate_scale = ft.Animation(500, ft.AnimationCurve.DECELERATE)
        self.opacity = 1.0
        self.scale = 1.0

        self.selected_date = datetime.now()
        
        self.date_label = ft.Text(
            self.selected_date.strftime("%d %b"), 
            size=14, 
            color=ft.Colors.WHITE
        )

        self.datepicker = ft.DatePicker(
            on_change=self.on_date_selected,
            last_date=datetime.now()
        )

        self.chart = fch.PieChart(
            sections=[], 
            sections_space=2, 
            center_space_radius=40, 
            expand=True,
            on_event=self.handle_hover
        )
        
        self.content = ft.Card(
            content=ft.Container(
                bgcolor="secondarycontainer",
                border_radius=AppStyle.CORNER_RADIUS,
                content=ft.Column([
                    ft.Row([
                        ft.Text(self.title, size=16, weight="bold"),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.CHEVRON_LEFT,
                                on_click=self.prev_day,
                                icon_size=AppStyle.ICON_SIZE_B,
                                tooltip="Giorno precedente"
                            ),
                            ft.IconButton(
                                ft.Icons.CALENDAR_MONTH, 
                                on_click=self.choose_date, 
                                icon_size=AppStyle.ICON_SIZE_B,
                                tooltip="Scegli data"
                            ),
                            self.date_label,
                            ft.IconButton(
                                ft.Icons.CHEVRON_RIGHT,
                                on_click=self.next_day,
                                icon_size=AppStyle.ICON_SIZE_B,
                                tooltip="Giorno successivo"
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER, tight=True, spacing=0),
                        ft.IconButton(
                            icon=ft.Icons.SHOW_CHART,
                            icon_size=AppStyle.ICON_SIZE_B, 
                            tooltip="Grafico",
                            on_click=lambda _: getattr(self, 'show_chart_dialog', lambda: None)()
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(self.chart, height=180),
                ]), padding=10
            ), margin=0
        )
    
    def handle_hover(self, e):
        # Se cambiamo sezione col mouse, aggiorniamo il raggio (animazione)
        if self.hover_idx != e.section_index:
            self.hover_idx = e.section_index
            self._render_pie(self.last_data)

    def did_mount(self):
        """Si attiva automaticamente al caricamento del widget"""
        self.load_initial_data()
        self.running = True
        try:
            self.page.pubsub.subscribe(self.on_pubsub_message)
        except Exception as e:
            log.error(f"❌ Errore avvio refresh automatico: {e}")

    def will_unmount(self):
        self.running = False
        try:
            # 1. Cancella i task asincroni attivi del widget
            if hasattr(self, 'update_task') and self.update_task:
                self.update_task.cancel()
                log.debug("Task di refresh automatico cancellato con successo.")
        except Exception as e:
            log.error(f"❌ Errore cancellazione task refresh automatico: {e}")
        try:
            if hasattr(self, 'page') and self.page and hasattr(self.page, "pubsub"):
                if hasattr(self.page.pubsub, "unsubscribe"):
                    self.page.pubsub.unsubscribe()
                    log.debug("Disiscrizione PubSub completata per ConsWidget.")
        except Exception as e:
            log.error(f"❌ Errore cancellazione task refresh automatico: {e}")

    def on_pubsub_message(self, message):
        """Gestisce tutti gli eventi pubsub per la Home"""
        global loc_enel
        try:
            if isinstance(message, dict):
                if message.get("type") == "enel_updated":
                    log.debug("Ricevuto segnale di aggiornamento ENEL, ricarico i consumi.")
                    loc_enel = message.get("data", self.last_data)
                    self.update_data(loc_enel)
        except Exception as e:
            log.error(f"❌ Errore gestione messaggio PubSub ConsWidget: {e}")

    def load_initial_data(self):
        """Recupera i dati per la data corrente all'avvio"""
        global loc_enel
        try:
            self.update_data(loc_enel)
        except Exception as e:
            log.error(f"❌ Errore caricamento iniziale: {e}")

    def update_data(self, data):
        """Punto di ingresso dati. Applica l'animazione incrementale."""
        try:
            if not hasattr(self, "page") or self.page is None:
                return
            session = getattr(self.page, "session", None)
            if session and hasattr(session, "connection") and session.connection is None:
                log.warning("ConsWidget: Impossibile aggiornare, la sessione Flet è stata chiusa.")
                return
            self.last_data = data
            if hasattr(self, "_render_pie"):
                self._render_pie(data)
            self.page.run_task(self.refresh_with_animation, data)
        except Exception as e:
            log.error(f"❌ Errore aggiornamento dati ConsWidget: {e}")

    def _render_pie(self, data):
        """Il motore vero e proprio che disegna il grafico senza animazione logica."""
        self.last_data = data

        try:
            mapping = [
                {"k": "prelievo", "t": "Rete", "c": ft.Colors.RED_400, "i": ft.Icons.ELECTRICAL_SERVICES},
                {"k": "auto", "t": "Auto", "c": ft.Colors.BLUE_400, "i": ft.Icons.BATTERY_SAVER},
                {"k": "immissione", "t": "Imms", "c": ft.Colors.GREEN_400, "i": ft.Icons.UPLOAD_FILE},
            ]

            p = float(data.get('prelievo', 0) or 0)
            i = float(data.get('immissione', 0) or 0)
            prod = float(data.get('produzione', 0) or 0)
            auto = max(0, prod - i)
            
            vals = {"prelievo": p, "auto": auto, "immissione": i}
            total_val = sum(vals.values())

            self.chart.sections = []

            if total_val < 0.1:
                # Disegna un cerchio grigio "vuoto" fisso quando tutti i dati sono nulli
                self.chart.sections = [
                    fch.PieChartSection(
                        1, 
                        title="0.00", 
                        color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), 
                        radius=NORMAL_RADIUS,
                        title_style=NORMAL_STYLE
                    )
                ]
            else:
                for idx, item in enumerate(mapping):
                    val = vals[item["k"]]
                    is_hover = (self.hover_idx == idx)
                    
                    # Usa un valore minimo per mantenere la matematica compatibile con i tooltip
                    draw_val = max(0.001, val)
                    
                    s_size = HOVER_BADGE_SIZE if is_hover else NORMAL_BADGE_SIZE
                    badge_icon = ft.Container(
                        ft.Icon(item["i"], size=s_size*0.6, color=item["c"]),
                        width=s_size,
                        height=s_size,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=s_size / 2,
                        border=ft.Border.all(1, item["c"]),
                    )

                    self.chart.sections.append(
                        fch.PieChartSection(
                            draw_val,
                            title=f"{val:.2f}" if val >= 0.1 else "", # Nasconde il testo allo start dei contatori
                            color=item["c"],
                            radius=HOVER_RADIUS if is_hover else NORMAL_RADIUS,
                            badge=badge_icon if val >= 0.1 else None, # Nasconde badge se parte da 0
                            badge_position=1.4 if is_hover else 1.1, 
                            title_style=HOVER_STYLE if is_hover else NORMAL_STYLE,
                        )
                    )
            
            if self.page:
                try:
                    self.update()
                except Exception as inner_e:
                    if "Control must be added to the page" not in str(inner_e):
                        log.error(f"❌ Errore rendering pie chart ConsWidget update: {inner_e}")
        except Exception as e:
            if "Control must be added to the page" not in str(e):
                log.error(f"❌ Errore rendering pie chart ConsWidget: {e}")

    def choose_date(self, e):
        if self.datepicker not in self.page.overlay:
            self.page.overlay.append(self.datepicker)
        self.page.update()
        self.datepicker.open = True
        self.datepicker.update()

    def prev_day(self, e):
        self.selected_date -= timedelta(days=1)
        self.date_label.value = self.selected_date.strftime("%d %b")
        if getattr(self, "page", None):
            self.page.run_task(self._fetch_and_refresh)

    def next_day(self, e):
        # Blocca se si prova ad andare oltre il giorno attuale (oggi)
        if self.selected_date.date() >= datetime.now().date():
            return
            
        self.selected_date += timedelta(days=1)
        self.date_label.value = self.selected_date.strftime("%d %b")
        if getattr(self, "page", None):
            self.page.run_task(self._fetch_and_refresh)

    async def _fetch_and_refresh(self):
        try:
            date_str = self.selected_date.strftime("%Y-%m-%d")
            res = self.app.dbm.GET_ENEL(self.tab, date_str)
            dati = res[0] if res else {}
            await self.refresh_with_animation(dati)
        except Exception as ex:
            log.error(f"❌ Errore caricamento giorno ConsWidget: {ex}")

    async def on_date_selected(self, e):
        try:
            if e.control.value:
                corrected_date = e.control.value + timedelta(hours=12)
            
                self.selected_date = corrected_date
                self.date_label.value = self.selected_date.strftime("%d %b")
                
                date_str = self.selected_date.strftime("%Y-%m-%d")
                
                log.debug(f"Valore originale: {e.control.value}")
                log.debug(f"Valore corretto: {date_str}")

                res = self.app.dbm.GET_ENEL(self.tab, date_str)
                dati = res[0] if res else {}
                
                await self.refresh_with_animation(dati)
        except Exception as e:
            log.error(f"❌ Errore selezione data: {e}")

    async def refresh_with_animation(self, dati):
        """Esegue l'animazione incrementale da 0 ai valori finali del grafico."""
        # Se è appena stato caricato, attendi un istante affinchè la UI esista prima di animarla
        await asyncio.sleep(0.1)

        p_target = float(dati.get('prelievo', 0) or 0)
        i_target = float(dati.get('immissione', 0) or 0)
        prod_target = float(dati.get('produzione', 0) or 0)
        
        self.last_data = dati
        
        steps = 15
        delay = 0.016  # Circa 60 fps
        
        for step in range(1, steps + 1):
            fraction = step / steps
            # Ease-out cubic: rallenta in modo morbido alla fine
            ease = 1 - pow(1 - fraction, 3)
            
            current_data = {
                'prelievo': p_target * ease,
                'immissione': i_target * ease,
                'produzione': prod_target * ease
            }
            
            self._render_pie(current_data)
            await asyncio.sleep(delay)
            
        # Forza i dati esatti alla fine del ciclo per evitare micro-sbavature
        self._render_pie(dati)