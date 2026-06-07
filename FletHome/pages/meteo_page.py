# -*- coding: utf-8 -*-
"""
Meteo Page - Pagina previsioni meteo
"""

import flet as ft
import logging
from common.config import RESPONSIVE_COLS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

log = logging.getLogger(__name__)

def get_content(app: 'App', title: str = "Meteo") -> ft.Column:
    """ Restituisce il contenuto della pagina Meteo """
    from components.TitleCard import TitleCard
    from components.MeteoCard import MeteoCard
   
    #   -----   👀  FUNZIONI INTERNE                👀  -----   #
    def on_resume():
        """Aggiorna la UI quando la pagina viene ripresa dalla cache"""
        try:
            # Recupera dati aggiornati
            new_data = getattr(app.meteo, 'last_data', None)
            cur = new_data.get('current', {}) if new_data and isinstance(new_data, dict) else {}
            l_up = cur.get('last_updated', 'N/A')
            # Aggiorna info titlebar
            title_bar.info_items = [f"Ultimo aggiornamento: {l_up}"]
            title_bar.update()
            log.debug("MeteoPage: on_resume executed (timestamp updated)")
            app.page.update()
        except Exception as ex:
            log.error(f"Errore on_resume Meteo: {ex}")

    def on_page_event(message):
        try:
            if app.current_page_index != 1:                                                                             #   ℹ️ Filtra eventi solo per la pagina attiva
                return
            if isinstance(message, dict) and message.get("type") == "meteo_updated":
                new_data = getattr(app.meteo, 'last_data', None)
                cur = new_data.get('current', {}) if new_data and isinstance(new_data, dict) else {}
                l_up = cur.get('last_updated', 'N/A')
                if title_bar.page:                                                                                      #   ℹ️ Controlla che il componente sia ancora agganciato a una pagina valida
                    title_bar.info_items = [f"Ultimo aggiornamento: {l_up}"]
                    title_bar.update()
                    log.debug("MeteoPage: on_page_event eseguito (timestamp aggiornato)")
                    app.page.update()
        except Exception as ex:
            log.error(f"Errore on_page_event Meteo: {ex}")

    def subscribe_events():
        if hasattr(app.page, "pubsub"):
            if hasattr(app.page.pubsub, "subscribe"):
                app.page.pubsub.subscribe(on_page_event)
            elif hasattr(app.page.pubsub, "add_listener"):
                app.page.pubsub.add_listener(on_page_event)

    def unsubscribe_events():
        try:
            if hasattr(app.page, "pubsub"):
                if hasattr(app.page.pubsub, "unsubscribe"):
                    app.page.pubsub.unsubscribe()
                elif hasattr(app.page.pubsub, "remove_listener"):
                    try:
                        app.page.pubsub.remove_listener()
                    except TypeError:
                        log.warning("remove_listener richiede un argomento, ma non è stato fornito. Tentativo di rimozione senza argomento.")
                        app.page.pubsub.remove_listener(on_page_event)
        except Exception as ex:
            log.error(f"Errore unsubscribe_events Meteo: {ex}")

    #   -----   👀  SUBSCRIPTION A EVENTI GLOBALI               👀  -----     #
    subscribe_events()

    # Recupera i dati meteo direttamente da app.meteo
    meteo_data = getattr(app.meteo, "last_data", None)
    current = meteo_data.get('current', {}) if meteo_data else {}
    last_update = current.get('last_updated', 'N/A')

    #   -----   👀  STRUTTURA UNIFORMATA            👀  -----   #  
    #   ✍🏻      TITLE BAR
    title_bar = TitleCard(
        title=title,
        icon=ft.Icons.WB_SUNNY,
        info_items=[
            f"Ultimo aggiornamento: {last_update}"
        ],
        refresh_callback=lambda e: on_page_event({"type": "meteo_updated"}),
        refresh_tooltip=f"Aggiorna dati {title}"
    )

    #   ✍🏻      LOADING INDICATOR
    loading_indicator = ft.Container(
        content=ft.Row([
            ft.ProgressRing(width=20, height=20),
            ft.Text("Caricamento dati meteo...", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
        ], spacing=10),
        padding=10, visible=True
    )
    app.page.update()

    #   -----   👀  CARICAMENTO DATI                👀  -----   #
    content = []
    try:
        if meteo_data:
            location = meteo_data.get("location", {})
            forecast = meteo_data.get("forecast", {}).get("forecastday", [])
            loc_name = location.get("name", "N/A")
            loc_region = location.get("region", "")
            # Aggiorna la titlebar con info dinamiche (titolo, ma info_items resta sempre con ora aggiornata)
            title_bar.title = f"Meteo - {loc_name} {loc_region}"
            content.append(
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=MeteoCard(
                                day_data=forecast[0] if forecast else {},
                                weekday_it="Oggi",
                                formatted_date=last_update.split(' ')[0]
                            ) if forecast else ft.Container(
                                content=ft.Text("⚠️ Dati oggi non disponibili"),
                                bgcolor="secondarycontainer",
                                padding=20,
                                border_radius=10
                            ),
                            col=RESPONSIVE_COLS
                        ),
                        *[
                            ft.Container(
                                content=card,
                                col=RESPONSIVE_COLS
                            )
                            for card in app.create_forecast_cards(forecast[1:])
                        ]
                    ],
                    run_spacing=10,
                    spacing=10
                )
            )
        else:
            content.append(
                ft.Container(
                    content=ft.Text("⚠️ Dati meteo non disponibili", size=16),
                    bgcolor="secondarycontainer",
                    padding=20,
                    border_radius=10
                )
            )
    except Exception as e:
        log.error(f"Errore caricamento meteo: {e}", exc_info=True)
        content = [
            ft.Container(
                content=ft.Text(f"❌ Errore: {str(e)}", size=16, color=ft.Colors.RED),
                bgcolor="secondarycontainer",
                padding=20,
                border_radius=10
            )
        ]

    # 👀    Nascondi loading indicator dopo il caricamento
    loading_indicator.visible = False
    
    log.debug(f"✅ Caricamento completato della Meteo Page.")
    col = ft.Column([
            title_bar,
            loading_indicator,
            *content
        ],
    scroll=ft.ScrollMode.AUTO,
    spacing=5,                                                                  #   👀  Spazio tra i gruppi di livelli                  
    margin=ft.Margin(left=0, right=5, top=0, bottom=5),                         #   👀  Margini intera finestra
    expand=True,
    alignment=ft.MainAxisAlignment.START)

    col.on_resume = on_resume
    app.page.update()
    return col