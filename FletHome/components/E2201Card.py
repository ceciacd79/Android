import flet as ft
from .GenCard import GenCard

class E2201Card(GenCard):
    """Card per E2201 Zigbee Dimmer Switch"""
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.RADIO_BUTTON_CHECKED, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", **kwargs):
        fields = {
            'battery': 'battery',
            'action': 'action'
        }
        super().__init__(topic, device_name, status, icon, data, fields, battery=True, floor=floor, name=name, pos=pos, **kwargs)   