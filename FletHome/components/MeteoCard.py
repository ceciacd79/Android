import flet as ft
from typing import Optional, Callable, List, Tuple, Dict

class MeteoCard(ft.Card):
    """Card dettagliata per previsioni giornaliere"""
    def __init__(self, day_data: dict, weekday_it: str, formatted_date: str):
        super().__init__()
        
        day_info = day_data.get("day", {})
        astro = day_data.get("astro", {})
        condition = day_info.get("condition", {}).get("text", "N/A")
        
        # Dati meteo
        max_temp = day_info.get("maxtemp_c", "N/A")
        min_temp = day_info.get("mintemp_c", "N/A")
        avg_temp = day_info.get("avgtemp_c", "N/A")
        rain_chance = day_info.get("daily_chance_of_rain", 0)
        rain_mm = day_info.get("totalprecip_mm", 0)
        max_wind = day_info.get("maxwind_kph", "N/A")
        avg_humidity = day_info.get("avghumidity", "N/A")
        uv_index = day_info.get("uv", "N/A")
        sunrise = astro.get("sunrise", "N/A")
        sunset = astro.get("sunset", "N/A")
        
        # Determina icona meteo
        icon = self._get_weather_icon(condition)
        
        # Costruisci contenuto card
        self.content = ft.Container(
            bgcolor="secondarycontainer",
            border_radius=10,
            content=ft.Column([
                # Header: Data + Condizione
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(weekday_it, theme_style=ft.TextThemeStyle.TITLE_LARGE, weight=ft.FontWeight.BOLD),
                            ft.Text(formatted_date, theme_style=ft.TextThemeStyle.BODY_MEDIUM, color=ft.Colors.GREY_700)
                        ], spacing=2),
                        ft.Icon(icon, size=50, color=ft.Colors.AMBER_700)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding(bottom=10)
                ),
                
                # Condizione meteo
                ft.Text(condition, theme_style=ft.TextThemeStyle.TITLE_MEDIUM, text_align=ft.TextAlign.CENTER),
                
                ft.Divider(height=1, color=ft.Colors.GREY_400),
                
                # Temperature (layout a 3 colonne)
                ft.ResponsiveRow([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🔥 Max", theme_style=ft.TextThemeStyle.BODY_SMALL, color=ft.Colors.GREY_700),
                            ft.Text(f"{max_temp}°C", theme_style=ft.TextThemeStyle.TITLE_LARGE, color=ft.Colors.RED_600, weight=ft.FontWeight.BOLD)
                        ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        col={"xs": 4}
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📊 Media", theme_style=ft.TextThemeStyle.BODY_SMALL, color=ft.Colors.GREY_700),
                            ft.Text(f"{avg_temp}°C", theme_style=ft.TextThemeStyle.TITLE_LARGE, weight=ft.FontWeight.BOLD)
                        ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        col={"xs": 4}
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("❄️ Min", theme_style=ft.TextThemeStyle.BODY_SMALL, color=ft.Colors.GREY_700),
                            ft.Text(f"{min_temp}°C", theme_style=ft.TextThemeStyle.TITLE_LARGE, color=ft.Colors.BLUE_600, weight=ft.FontWeight.BOLD)
                        ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        col={"xs": 4}
                    )
                ]),
                
                ft.Divider(height=1, color=ft.Colors.GREY_400),
                
                # Dettagli aggiuntivi (griglia 2x3)
                ft.ResponsiveRow([
                    # Pioggia
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.WATER_DROP, size=20, color=ft.Colors.BLUE_600),
                            ft.Column([
                                ft.Text("Pioggia", theme_style=ft.TextThemeStyle.BODY_SMALL),
                                ft.Text(f"{rain_chance}% ({rain_mm}mm)", theme_style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD)
                            ], spacing=2)
                        ], spacing=8),
                        col={"xs": 6}
                    ),
                    # Vento
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.AIR, size=20, color=ft.Colors.TEAL_600),
                            ft.Column([
                                ft.Text("Vento", theme_style=ft.TextThemeStyle.BODY_SMALL),
                                ft.Text(f"{max_wind} km/h", theme_style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD)
                            ], spacing=2)
                        ], spacing=8),
                        col={"xs": 6}
                    ),
                    # Umidità
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.OPACITY, size=20, color=ft.Colors.CYAN_600),
                            ft.Column([
                                ft.Text("Umidità", theme_style=ft.TextThemeStyle.BODY_SMALL),
                                ft.Text(f"{avg_humidity}%", theme_style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD)
                            ], spacing=2)
                        ], spacing=8),
                        col={"xs": 6}
                    ),
                    # UV Index
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.WB_SUNNY, size=20, color=ft.Colors.ORANGE_600),
                            ft.Column([
                                ft.Text("UV Index", theme_style=ft.TextThemeStyle.BODY_SMALL),
                                ft.Text(str(uv_index), theme_style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD)
                            ], spacing=2)
                        ], spacing=8),
                        col={"xs": 6}
                    )
                ], spacing=10),
                
                ft.Divider(height=1, color=ft.Colors.GREY_400),
                
                # Alba e Tramonto
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.WB_TWILIGHT, size=20, color=ft.Colors.ORANGE_400),
                        ft.Text(f"Alba: {sunrise}", theme_style=ft.TextThemeStyle.BODY_SMALL)
                    ], spacing=6),
                    ft.Row([
                        ft.Icon(ft.Icons.NIGHTS_STAY, size=20, color=ft.Colors.INDIGO_400),
                        ft.Text(f"Tramonto: {sunset}", theme_style=ft.TextThemeStyle.BODY_SMALL)
                    ], spacing=6)
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
                
            ], spacing=12),
            padding=20
        )
        
        # Stile card
        self.elevation = 3
        self.margin = 5
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=6,
            color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
            offset=ft.Offset(0, 3)
        )
    
    def _get_weather_icon(self, condition: str):
        """Restituisce l'icona appropriata per la condizione meteo
        ☀️ SOLE/SERENO:
        - Sunny (Soleggiato)
        
        ☁️ NUVOLOSO:
        - Partly cloudy (Parzialmente nuvoloso)
        - Cloudy (Nuvoloso)
        - Overcast (Coperto)
        - Mist (Foschia)
        - Fog (Nebbia)
        - Freezing fog (Nebbia ghiacciata)
        
        🌧️ PIOGGIA:
        - Patchy rain possible (Possibile pioggia a tratti)
        - Patchy light drizzle (Pioggerella leggera a tratti)
        - Light drizzle (Pioggerella leggera)
        - Freezing drizzle (Pioggerella gelata)
        - Heavy freezing drizzle (Pioggerella gelata intensa)
        - Patchy light rain (Pioggia leggera a tratti)
        - Light rain (Pioggia leggera)
        - Moderate rain at times (Pioggia moderata a tratti)
        - Moderate rain (Pioggia moderata)
        - Heavy rain at times (Pioggia forte a tratti)
        - Heavy rain (Pioggia forte)
        - Light freezing rain (Pioggerella gelata leggera)
        - Moderate or heavy freezing rain (Pioggerella gelata moderata/forte)
        - Light rain shower (Rovescio leggero)
        - Moderate or heavy rain shower (Rovescio moderato/forte)
        - Torrential rain shower (Rovescio torrenziale)
        
        ❄️ NEVE:
        - Patchy snow possible (Possibile neve a tratti)
        - Patchy light snow (Neve leggera a tratti)
        - Light snow (Neve leggera)
        - Patchy moderate snow (Neve moderata a tratti)
        - Moderate snow (Neve moderata)
        - Patchy heavy snow (Neve forte a tratti)
        - Heavy snow (Neve forte)
        - Blowing snow (Neve ventosa)
        - Blizzard (Bufera di neve)
        - Light snow showers (Rovesci di neve leggeri)
        - Moderate or heavy snow showers (Rovescio di neve moderati/forti)
        
        🌨️ MISTO (PIOGGIA/NEVE):
        - Patchy sleet possible (Possibile nevischio a tratti)
        - Light sleet (Nevischio leggero)
        - Moderate or heavy sleet (Nevischio moderato/forte)
        - Light sleet showers (Rovesci leggeri di nevischio)
        - Moderate or heavy sleet showers (Rovesci di nevischio moderati/forti)
        - Ice pellets (Grandine/ghiaccio)
        - Light showers of ice pellets (Rovesci leggeri di grandine)
        - Moderate or heavy showers of ice pellets (Rovesci moderati/forti di grandine)
        
        ⛈️ TEMPORALE:
        - Thundery outbreaks possible (Possibili temporali)
        - Patchy light rain with thunder (Pioggia leggera a tratti con tuoni)
        - Moderate or heavy rain with thunder (Pioggia moderata/forte con tuoni)
        - Patchy light snow with thunder (Neve leggera a tratti con tuoni)
        - Moderate or heavy snow with thunder (Neve moderata/forte con tuoni)
        
        🧊 GELO:
        - Patchy freezing drizzle possible (Possibile pioggerella gelata a tratti)
        """
        
        condition_lower = condition.lower()
        
        # ☀️ Sole/Sereno
        if "sunny" in condition_lower or "clear" in condition_lower:
            return ft.Icons.WB_SUNNY
        
        # ☁️ Nuvoloso
        elif any(word in condition_lower for word in ["cloudy", "overcast", "mist"]):
            return ft.Icons.CLOUD
        
        # ☁️ Nuvoloso/Nebbia
        elif any(word in condition_lower for word in [ "fog"]):
            return ft.Icons.FOGGY

        # 🌧️ Pioggia (incluso drizzle = piogggerella)
        elif any(word in condition_lower for word in ["rain", "drizzle", "shower"]) and "snow" not in condition_lower:
            return ft.Icons.UMBRELLA
        
        # ❄️ Neve
        elif "snow" in condition_lower or "blizzard" in condition_lower:
            return ft.Icons.AC_UNIT
        
        # 🌨️ Nevischio/Grandine (sleet = nevischio, pellets = grandine)
        elif "sleet" in condition_lower or "ice pellets" in condition_lower:
            return ft.Icons.SEVERE_COLD
        
        # ⛈️ Temporale/Tuoni
        elif "thunder" in condition_lower or "storm" in condition_lower:
            return ft.Icons.THUNDERSTORM
        
        # 🌫️ Default (condizioni non specificate)
        else:
            return ft.Icons.WB_CLOUDY
