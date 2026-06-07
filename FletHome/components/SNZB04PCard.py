import flet as ft
import logging
from .GenCard import GenCard

log = logging.getLogger(__name__)

class SNZB04PCard(GenCard):
    """Card per SNZB-04P Zigbee sensor"""
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.SENSOR_WINDOW_OUTLINED, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", **kwargs):
        try:
            if name is not None and "porta" in name.lower():
                icon = ft.Icons.SENSOR_DOOR_OUTLINED
        except Exception as e:
            log.error(f"Errore nella creazione della card SNZB-04P: {e}")
            
        fields = {
            'battery': 'battery',
            'contact': 'Stato',
            'tamper': 'Manomissione'
        }
        super().__init__(topic, device_name, status, icon, data, fields, battery=True, switch=False, floor=floor, name=name, pos=pos, **kwargs)