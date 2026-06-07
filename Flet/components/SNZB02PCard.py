import flet as ft
from .GenCard import GenCard

class SNZB02PCard(GenCard):
    """Card per SNZB-02P Zigbee Sensor (Temperatura, Umidità, Batteria)"""
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.SENSORS, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", **kwargs):
        fields = {
            'battery': 'battery',
            'temperature': 'temperature',
            'humidity': 'humidity'
        }
        super().__init__(topic, device_name, status, icon, data, fields, battery=True, floor=floor, name=name, pos=pos, **kwargs)