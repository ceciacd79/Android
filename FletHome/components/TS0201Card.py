import flet as ft
from .GenCard import GenCard

class TS0201Card(GenCard):
    """Card per TS0201 Zigbee Temperature and Humidity sensor"""
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.SENSORS, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", **kwargs):
        fields = {
            'battery': 'battery',
            'temperature': 'temperature',
            'humidity': 'humidity'
        }
        super().__init__(topic, device_name, status, icon, data, fields, battery=True, switch=False, floor=floor, name=name, pos=pos, **kwargs)