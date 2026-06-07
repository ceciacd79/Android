import flet as ft
from .GenCard import GenCard

class LED2004G8Card(GenCard):
    """Card per LED2004G8 Zigbee lampada"""
    def __init__(self, topic: str, device_name: str, status: str = None, icon: str = ft.Icons.LIGHTBULB, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", page=None, **kwargs):
        fields = {
            'state': 'state',
            'brightness': 'brightness',
            'color_temp': 'color_temp'
        }
        super().__init__(topic, device_name, status, icon, data, fields, battery=False, floor=floor, name=name, pos=pos, page=page, **kwargs)