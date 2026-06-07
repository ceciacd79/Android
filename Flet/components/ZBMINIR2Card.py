import flet as ft
from .GenCard import GenCard

class ZBMINIR2Card(GenCard):
    """Card per ZBMINIR2 Zigbee Power switch"""
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.POWER, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", **kwargs):
        fields = {
            'state': 'state'
        }
        super().__init__(topic, device_name, status, icon, data, fields, floor=floor, name=name, pos=pos, **kwargs)        