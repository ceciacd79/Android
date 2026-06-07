import flet as ft
import threading
import time

class BaseCard(ft.Card):
    """
    Classe base per Card che implementa un'animazione standard all'aggiornamento.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def configure_animated_content(self, content_container: ft.Container):
        """
        Configura il container del contenuto per supportare le animazioni.
        Deve essere chiamato nel costruttore della classe figlia passando il container principale.
        """
        content_container.scale = 1
        content_container.animate_scale = ft.Animation(300, ft.AnimationCurve.BOUNCE_IN_OUT)
        
        # Imposta sfondo trasparente iniziale e animazione generica (che include bgcolor)
        content_container.border_radius = 10
        content_container.bgcolor = "secondarycontainer"
        content_container.animate = ft.Animation(300, ft.AnimationCurve.LINEAR)
        
        return content_container

    def trigger_update_animation(self):
        """
        Esegue l'animazione visiva (scale + flash colore).
        Da chiamare all'interno di update_data() o quando si vuole notificare un cambiamento.
        """
        try:
            if not self.page: return
        except Exception:
            return

        if isinstance(self.content, ft.Container):
            self.content.scale = 1.02
            self.content.bgcolor = "primarycontainer"
            self.content.border_radius = 10
            try:
                self.update()
            except Exception:
                pass

            def restore():
                time.sleep(0.4)
                try:
                    if not self.page: return
                except Exception:
                    return
                
                if isinstance(self.content, ft.Container):
                    self.content.scale = 1.0
                    self.content.bgcolor = "secondarycontainer"
                    self.content.border_radius = 10
                #    self.bgcolor = ft.Colors.SECONDARY_CONTAINER
                    try:
                        self.content.update()
                        self.update()
                    except Exception:
                        pass
            
            try:
                self.page.run_thread(restore)
            except Exception:
                pass
