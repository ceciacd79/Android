import flet as ft
from .GenCard import GenCard

class E2134Card(GenCard):
    """Card per E2134 Zigbee Motion Sensor"""
    def __init__(self, topic: str, device_name: str, status: str = None, icon: str = ft.Icons.PERSON_OUTLINED, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", page=None, **kwargs):
        fields = {
            'battery': 'battery',
            'occupancy': 'occupancy',
            'illuminance': 'illuminance'
        }
        super().__init__(topic, device_name, status, icon, data, fields, battery=True, floor=floor, name=name, pos=pos, page=page, **kwargs)