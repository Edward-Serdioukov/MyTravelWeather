import logging
from flet import *
import flet
from flet import Page

from views.weather_view import TravelWeather

#logging.basicConfig(level=logging.DEBUG)

def main(page: Page):

    travel_weather = TravelWeather(page)
    travel_weather_week_view = travel_weather.travel_weather_week_view()
    travel_weather_cities_view = travel_weather.travel_weather_cities_view()
    travel_weather_map_view = travel_weather.travel_weather_map_view()
    travel_weather_compare_settings_view = travel_weather.compare_settings_view()
    
    def route_change(route):
        page.views.clear()
        if page.route == "/travel_weather":
            #travel_weather.refresh_map_markers()
            page.views.append( travel_weather_map_view)
        elif page.route == "/travel_weather_week_compare":
            #travel_weather.refresh_compare_table()
            page.views.append( travel_weather_week_view)
        elif page.route == "/travel_weather_cities":
            travel_weather.appbar.title = Text("Settings")
            page.views.append( travel_weather_cities_view)
        elif page.route == "/travel_weather_compare_settings":
            page.views.append( travel_weather_week_view)
            page.views.append( travel_weather_compare_settings_view)

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go("/travel_weather")
    
flet.app(target=main, assets_dir="assets", view=AppView.WEB_BROWSER, upload_dir="assets/images", port=8000)
#
#flet.app(target=main, assets_dir="assets")
#flet.app(main) ###flet run --web main.py

