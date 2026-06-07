import flet as ft
import logging
from .GenCard import GenCard

log = logging.getLogger(__name__)

class _14594Card(GenCard):
    """Card per 14594 Zigbee Wimar"""
    def __init__(self, topic: str, device_name: str, status: str = None, icon: str = ft.Icons.ROLLER_SHADES_OUTLINED, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", page=None):
        try:
            if name is not None and "porta" in name.lower():
                icon = ft.Icons.SENSOR_DOOR_OUTLINED
        except Exception as e:
            log.error(f"Errore nella creazione della card 14594: {e}")

        fields = {
            'state': 'Status',
            'position': 'Pos'
        }
        super().__init__(topic, device_name, status, icon, data, fields, floor=floor, name=name, pos=pos, page=page)