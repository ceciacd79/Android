import flet as ft
from .GenCard import GenCard

class SNZB01PCard(GenCard):
    """Card per SNZB-01P Zigbee sensor"""
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.SMART_BUTTON, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", **kwargs):
        fields = {
            'battery': 'battery',
            'action': 'action'
        }
        super().__init__(topic, device_name, status, icon, data, fields, battery=True, floor=floor, name=name, pos=pos, **kwargs)