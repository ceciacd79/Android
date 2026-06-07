import flet as ft
from .GenCard import GenCard

class TH02ZCard(GenCard):
    """Card per TH02Z Zigbee Temperature and Humidity sensor"""
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.SENSORS, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", **kwargs):
        fields = {
            'battery': 'Battery',
            'temperature': 'Temperature',
            'humidity': 'Humidity'
        }
        super().__init__(topic, device_name, status, icon, data, fields, battery=True, switch=False, floor=floor, name=name, pos=pos, **kwargs)