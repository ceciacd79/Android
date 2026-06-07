import flet as ft
from .GenCard import GenCard

class E22X4Card(GenCard):
    """Card per E22X4 Zigbee TRETAKT smart plug"""
    def __init__(self, topic: str, device_name: str, status: str = None, icon: str = ft.Icons.ELECTRICAL_SERVICES, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", page=None, **kwargs):
        fields = {
            'state': 'state'
        }
        super().__init__(topic, device_name, status, icon, data, fields, floor=floor, name=name, pos=pos, page=page, **kwargs)