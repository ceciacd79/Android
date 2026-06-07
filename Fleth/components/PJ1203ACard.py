import flet as ft
from .GenCard import GenCard

class PJ1203ACard(GenCard):
    """Card per dispositivo PJ-1203A con contenuto dinamico"""
    def __init__(self, topic: str, device_name: str, status: str, icon: str = ft.Icons.ELECTRICAL_SERVICES, data: dict = {}, floor: str = "N/A", name: str = "", pos: str = "", **kwargs):
        fields = {
            'energy_a': 'KW Consumati',
            'energy_flow_a': 'Stato',
            'power_a': 'W Attuali',
        }
        fieldsB = {
            'energy_produced_b': 'KW Autoprodotti',
            'energy_flow_b': 'Stato',
            'power_b': 'W Attuali',
        }
        super().__init__(topic, device_name, status, icon, data, fields, fieldsB=fieldsB, switch=True, floor=floor, name=name, pos=pos, **kwargs)