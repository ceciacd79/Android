# -*- coding: utf-8 -*-
import flet as ft
from datetime import datetime

class ConsBarWidget(ft.Container):
    def __init__(self, app, initial_data=None):
        super().__init__()
        self.app = app
        
        # Grafico a Barre
        self.chart = ft.BarChart(
            bar_groups=[],
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE)),
            left_axis=ft.ChartAxis(labels_size=30),
            bottom_axis=ft.ChartAxis(labels_size=40),
            horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE)),
            expand=True,
        )

        # Legenda superiore
        self.legend = ft.Row([
            ft.Row([ft.Container(width=10, height=10, bgcolor=ft.Colors.RED_400, border_radius=2), ft.Text("Rete", size=12)]),
            ft.Row([ft.Container(width=10, height=10, bgcolor=ft.Colors.GREEN_400, border_radius=2), ft.Text("Auto", size=12)]),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        
        self.content = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Storico Consumi 30gg (kWh)", weight="bold", size=14),
                    self.legend, # <--- Legenda aggiunta
                    ft.Container(self.chart, expand=True), 
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=10
            ), 
            margin=5,
            height=250 # Pareggiato al circolare
        )
        
        if initial_data:
            self.update_data(initial_data)

    def update_data(self, data_list):
        if not data_list or not isinstance(data_list, list):
            return
            
        new_groups = []
        new_labels = []
        step = 4 # Mostra data ogni 4 giorni per pulizia

        for i, d in enumerate(data_list):
            # Estrazione dati
            p = float(d.get('prelievo', 0) or 0)
            imm = float(d.get('immissione', 0) or 0)
            prod = float(d.get('produzione', 0) or 0)
            
            # Calcolo Autoconsumo: quello che produci meno quello che vendi
            auto = max(0, prod - imm)
            
            # Formattazione data GG/MM
            raw_date = d.get('giorno', '')
            try:
                if isinstance(raw_date, str):
                    dt_obj = datetime.strptime(raw_date, '%Y-%m-%d')
                else:
                    dt_obj = raw_date
                label_str = dt_obj.strftime('%d/%m')
            except:
                label_str = str(raw_date)

            # Creazione gruppo con DUE barre (Rossa e Verde)
            new_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(from_y=0, to_y=p, width=8, color=ft.Colors.RED_400, border_radius=2),
                        ft.BarChartRod(from_y=0, to_y=auto, width=8, color=ft.Colors.GREEN_400, border_radius=2),
                    ]
                )
            )
            
            if i % step == 0:
                new_labels.append(
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Container(
                            content=ft.Text(label_str, size=10, weight="bold"),
                            margin=ft.Margin.only(top=5)
                        )
                    )
                )

        self.chart.bar_groups = new_groups
        self.chart.bottom_axis.labels = new_labels
        
        if self.page:
            self.page.update()