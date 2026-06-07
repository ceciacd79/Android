# -*- coding: utf-8 -*-
"""
Funzioni comuni per autenticazione e gestione utente
"""
import flet as ft
import logging

def show_login_dialog(page, on_success):
    """ Mostra un dialog di login per autenticare l'utente prima di permettere modifiche sensibili """
    log = logging.getLogger(__name__)
    def check_password(e):
        log.debug(f"Conferma premuta, valore inserito: {password_field.value}")
        try:
            if password_field.value == "admin":  # Sostituisci con la tua logica di verifica
                app = getattr(page, "app", None)
                if app is not None:
                    app.is_logged_in = True
                    if hasattr(app, "update_login_badge"):
                        app.update_login_badge()
                dialog.open = False
                page.update()
                on_success()
            else:
                password_field.error_text = "Password errata"
                page.update()
        except Exception as ex:
            log.error(f"Errore durante la verifica della password: {ex}")
            password_field.error_text = "Si è verificato un errore"
            page.update()

    log.debug("Apro dialog di login...")
    password_field = ft.TextField(password=True, label="Password", autofocus=True, on_submit=check_password)
    app = getattr(page, "app", None)
    if app is not None and hasattr(app, "is_logged_in"):
        if getattr(app, "is_logged_in", False):
            log.debug("Utente già autenticato, non mostro il dialog di login.")
            if hasattr(app, "update_login_badge"):
                app.update_login_badge()
            on_success()
            return
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Autenticazione richiesta"),
        content=password_field,
        actions=[
            ft.TextButton("Annulla", on_click=lambda e: (setattr(dialog, 'open', False), page.update())),
            ft.TextButton("Conferma", on_click=check_password),
        ],
    )
    if dialog not in page.overlay:
        page.overlay.append(dialog)
    dialog.open = True
    page.update()
    log.debug(f"Dialog stato: {dialog.open}, page.overlay: {page.overlay}")
