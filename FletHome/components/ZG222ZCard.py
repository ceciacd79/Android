import flet as ft
from .GenCard import GenCard

class ZG222ZCard(GenCard):
    """Card per ZG222Z Zigbee Power switch"""
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.WATER, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", **kwargs):
        fields = {
            'battery': 'battery',
            'water_leak': 'Perdita d\'acqua',
            'tamper': 'manomissione'
        }
        super().__init__(topic, device_name, status, icon, data, fields, battery=True, floor=floor, name=name, pos=pos, **kwargs)