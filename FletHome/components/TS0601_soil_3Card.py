import flet as ft
from .GenCard import GenCard

class TS0601_soil_3Card(GenCard):
    """Card per TS0601_soil_3 Zigbee Sensor (Temperatura, Umidità, Batteria)"""
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.SENSORS, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", **kwargs):
        fields = {
            'battery': 'battery',
            'temperature': 'temperature',
            'soil_moisture': 'soil_moisture'
        }
        super().__init__(topic, device_name, status, icon, data, fields, battery=True, switch=False, floor=floor, name=name, pos=pos, **kwargs)