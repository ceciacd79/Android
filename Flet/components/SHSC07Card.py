import flet as ft
from .GenCard import GenCard

class SHSC07Card(GenCard):
    """Card per SHSC-07 Zigbee sensor"""
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.RADIO_BUTTON_CHECKED_OUTLINED, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", **kwargs):
        fields = {
            'battery': 'battery',
            'action': 'action'
        }
        super().__init__(topic, device_name, status, icon, data, fields, battery=True, floor=floor, name=name, pos=pos, **kwargs)