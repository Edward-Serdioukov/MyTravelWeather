import base64
import json
import re
import flet.map as map
from flet import (
    View,
    Container,
    Text,
    Column,
    Row,
    colors,
    Card,
    Image,
    GridView,
    AppBar,
    Icon,
    IconButton,
    PopupMenuItem,
    PopupMenuButton,
    MainAxisAlignment,
    TextStyle,
    LinearGradient,
    CrossAxisAlignment,
    ThemeMode,
    AlertDialog,
    TextButton,
    FontWeight,
    icons,
    alignment,
    Tabs,
    Tab,
    Markdown,
    MarkdownExtensionSet,
    ListView,
    SubmenuButton,
    MenuItemButton,
    NavigationBar,NavigationBarDestination,
    DataTable, DataColumn, DataRow, DataCell,
)
import flet
import requests
from tinydb import TinyDB, Query

from weather import get_geo_data, get_weather_day, get_weather_week

class TravelWeather():

    def __init__(self, page):
        self.db = TinyDB('db.json')
        self.City = Query()
        self.page = page    
        self.page.theme_mode = ThemeMode.LIGHT
        self.selected_view = '0'
        
        self.appbar = AppBar(
            #leading=Icon(flet.icons.HOME),
            leading_width=40,
            title=Text("MTW"), ##size=20, weight=FontWeight.BOLD),
            center_title=False,
            bgcolor=colors.SURFACE_VARIANT,
            actions=[
                IconButton(icon=flet.icons.WB_SUNNY_OUTLINED, on_click=self.theme_changed)
            ],
        )
        
        self.appbar2 = AppBar(
                title=Text("Compare weather"),
                center_title=False,
                bgcolor=colors.SURFACE_VARIANT,
                actions=[
                    IconButton(icon=flet.icons.WB_SUNNY_OUTLINED, on_click=self.theme_changed),
                ]
 
        )

        self.navbar = NavigationBar(
            destinations=[
                NavigationBarDestination(icon=icons.MAP, label="Map"),
                NavigationBarDestination(icon=icons.COMPARE_OUTLINED, label="Compare"), #CLOUD_DONE_OUTLINED
                NavigationBarDestination(icon=icons.SETTINGS, label="Settings"),
                #NavigationBarDestination(icon=icons.MAPS_HOME_WORK, label="Cities"),
            ],
            on_change=lambda e: self.navbar_event(e),
        )
        self.image_src = ""
        self.image_title = ""
        self.image_url = ""
        self.image_code = ""
        self.image_country = ""
        self.image_games = ""
        self.ctrl = [self.appbar, Container(content='', alignment=flet.alignment.top_center, padding=10)]
        self.marker_layer_ref = flet.Ref[map.MarkerLayer]()
        self.circle_layer_ref = flet.Ref[map.CircleLayer]()
        self.compare_table =DataTable(
                columns=[DataColumn(Text("No data"))],
                rows=[DataRow([DataCell(Text("No selected cities for compare"))])]
            )
        self.markers = [] 
        
        self.compare_table = DataTable(
                data_row_min_height=100,
                data_row_max_height=100,
                columns=[DataColumn(Text("No data"))],
                rows=[DataRow([DataCell(Text("No selected cities for compare"))])]
            )
        
        self.weather_travel_map = map.Map(
            expand=True,
            configuration=map.MapConfiguration(
                initial_center=map.MapLatitudeLongitude(48, 20),
                initial_zoom=3.6,
                interaction_configuration=map.MapInteractionConfiguration(
                    flags=map.MapInteractiveFlag.ALL
                ),
                on_init=lambda e: print(f"Initialized Map"),
            ),
            layers=[
                map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=lambda e: print("TileLayer Error"),
                ),
                map.MarkerLayer(
                    ref=self.marker_layer_ref,
                    markers = self.markers,
                ), 
            ],
        )
        self.progress_ring = flet.ProgressRing(stroke_width = 5)

        self.splash = Container(
            content=self.progress_ring,
            expand=True,
            alignment=alignment.center,
            visible=False
        )
        self.page.overlay.append(self.splash)
        
    def navbar_event(self, e):
        if e.control.selected_index == 0:
            self.page.go("/travel_weather")	
        if e.control.selected_index == 1:
            self.page.go("/travel_weather_week_compare")
        if e.control.selected_index == 2:
            self.page.go("/travel_weather_cities")
        if e.control.selected_index == 3:
            self.page.go("/more")

    def refresh_compare_table(self):
        self.show_progress()
        self.compare_table.columns.clear()
        self.compare_table.rows.clear()
        self.create_compare_table()
        self.hide_progress()
        self.page.update()

        
    def refresh_map_markers(self):
        self.show_progress()
        self.markers.clear()
        self.create_map()
        self.hide_progress()
        self.page.update()

    def show_progress(self):
        self.splash.visible = True
        self.page.update()

    def hide_progress(self):
        self.splash.visible = False
        self.page.update()
        
    def theme_changed(self, e):
        if self.page.theme_mode == ThemeMode.LIGHT:
            self.page.theme_mode = ThemeMode.DARK
        else:
            self.page.theme_mode = ThemeMode.LIGHT

        self.page.update()

    def click_home(self, e):
        self.selected_view = e.control.data
        self.refresher()
        self.page.go("/travel_weather")
        
  
  
    def travel_weather_map_clicked(self, e):
        self.refresh_map_markers()
        
        
    def travel_weather_week_compare_clicked(self, e):
        self.refresh_compare_table()
    
        
    def load_image_from_url(self, url):
        #print(url)
        response = requests.get(url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
        else:
            print(f"Не удалось загрузить изображение: {response.status_code}")
            return None
    
    def change_marker_color(self, e):
            
        marker_index = next(
            (
                i
                for i, marker in enumerate(self.marker_layer_ref.current.markers)
                if marker.coordinates.latitude == e.control.data['lat']
                and marker.coordinates.longitude == e.control.data['lon']
            ),
            None,
        )

        if marker_index is not None:
            # Replace the marker with a new one with a different color
            location_src = "images/location2-red.png" if e.control.data['comp'] else "images/location2.png"
            self.marker_layer_ref.current.markers[marker_index] = map.Marker(
                        content=Container(content=Image(src=location_src, width=345, height=345),
                                        alignment=flet.alignment.center,
                                        data=e.control.data,  width=345, height=345,
                                        on_click=lambda e: self.show_image_modal(e),
                                        #on_click=self.on_marker_click,
                                        tooltip=flet.Tooltip(
                                            message=f"{e.control.data["name"]}",
                                            padding=20,
                                            border_radius=10,
                                            bgcolor=colors.WHITE,
                                            shadow=flet.BoxShadow(spread_radius=5, blur_radius=5, color=colors.BLACK),
                                            text_style=flet.TextStyle(size=20, color=colors.BLACK)
                                        )),
                            
                            coordinates=map.MapLatitudeLongitude(e.control.data['lat'], e.control.data['lon']),
                            
                        )
            
    def show_image_modal(self, e):

        def close_dlg(e):

            dlg_modal.open = False
            #e.control.data['comp'] = check_compare.value
            #self.db.update({'comp': check_compare.value}, self.City.name == e.control.data['name'])
            #self.change_marker_color(e)
            #self.refresh_compare_table()
            self.page.update()

        # Create the content of the modal dialog
        try:
            weather_day = get_weather_day(e.control.data['name'])
            if weather_day is not None:

                image = Card(
                    elevation=1,
                    color=colors.BLUE_GREY_100,
                    content=Image(src_base64=self.load_image_from_url(weather_day['icon']), width=200, height=200)  )

                temperature = Text(f"{weather_day["temperature"]}°C", size=20, weight=FontWeight.BOLD)
                description = Text(weather_day["description"], no_wrap=False, size=20, weight=FontWeight.BOLD)
                #check_compare = flet.Checkbox(label="Set for Compare", value=e.control.data['comp'])

                # Create the modal dialog
                dlg_modal = AlertDialog(
                    modal=True,
                    title=Text(e.control.data['name']),
                    content=Container(Column([image, temperature, description],
                                                alignment=flet.MainAxisAlignment.START,
                                                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
                                                scroll=flet.ScrollMode.ALWAYS,),),
                    actions=[TextButton("Ok", data=e.control.data, on_click=lambda e: close_dlg(e))],
                    actions_alignment=MainAxisAlignment.END,
                )           
                # Show the modal dialog
                self.page.dialog = dlg_modal
                dlg_modal.open = True
                self.page.update()
            else:
                print(f"Не удалось загрузить информацию для: {e.control.data['name']}")
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {e}")


    def create_map(self):
        data = self.db.all()   

        for city in self.db.all():
            marker = map.Marker(
                            content=Container(content=Image(src="images/location2.png",#"images/location2-red.png" if city['comp'] else "images/location2.png",
                                                            width=345, height=345),
                                            alignment=flet.alignment.center,
                                            data=city,  width=345, height=345,
                                            on_click=lambda e: self.show_image_modal(e),
                                            #on_click=self.on_marker_click,
                                            tooltip=flet.Tooltip(
                                                message=f"{city["name"]}",
                                                padding=20,
                                                border_radius=10,
                                                bgcolor=colors.WHITE,
                                                shadow=flet.BoxShadow(spread_radius=5, blur_radius=5, color=colors.BLACK),
                                                text_style=flet.TextStyle(size=20, color=colors.BLACK)
                                            )),
                            
                            coordinates=map.MapLatitudeLongitude(city["lat"], city["lon"]),
                            
                        )
            self.markers.append(marker)
    
    def travel_weather_map_view(self):
        appbar = AppBar(
            #leading=Icon(flet.icons.HOME),
            #leading_width=40,
            title=Text("MTW"), ##size=20, weight=FontWeight.BOLD),
            center_title=False,
            #bgcolor=colors.SURFACE_VARIANT,
            actions=[
                IconButton(icon=flet.icons.REFRESH_OUTLINED, on_click=self.travel_weather_map_clicked),
                #IconButton(icon=flet.icons.WB_SUNNY_OUTLINED, on_click=self.theme_changed)
            ],
        )
        self.create_map()                                            
        return View(
            route="/travel_weather",
            #scroll=flet.ScrollMode.AUTO,
            controls=[
                appbar,
                self.weather_travel_map,
                self.navbar
            ]
        )

    def create_compare_table(self):
        data = self.db.all()
                    
        cities_weather = []
    
        for city in data:
            if city['comp']:
                weather_data = get_weather_week(city['name'])
                if weather_data:
                    cities_weather.append(weather_data)
        if not cities_weather:
            return flet.Text("No data to compare")
        
        columns = [DataColumn(Text(city['city'])) for city in cities_weather]
        rows = []
        
        if cities_weather:
            for i in range(len(cities_weather[0]['forecast'])):
                cells = []
                for city in cities_weather:
                    forecast_info = city['forecast'][i]
                    cell_content = Row([Column(
                        [
                            Text(forecast_info['day'], size=12, text_align=flet.TextAlign.CENTER),
                            Image(src_base64=self.load_image_from_url(forecast_info['icon']), width=40, height=40),
                            Text(f"{forecast_info['temperature']}°C", size=12, text_align=flet.TextAlign.CENTER),
                        ],
                        alignment='center',
                        spacing=1,  # Добавляем отступы между элементами
                        expand=True,
                    )],
                    alignment='center',
                    expand=True,
                    )
                    cells.append(DataCell(cell_content))
                rows.append(DataRow(cells=cells))
            
            self.compare_table.columns = columns
            self.compare_table.rows = rows
        elif not cities_weather:
            self.compare_table.columns = [DataColumn(Text("No data"))],
            self.compare_table.rows = [DataRow([DataCell(Text("No selected cities for compare"))])]

    
    def travel_weather_week_view(self):
  
        appbar = AppBar(
            title=Text("Compare week"), ##size=20, weight=FontWeight.BOLD),
            center_title=False,
            bgcolor=colors.SURFACE_VARIANT,
            actions=[
                #IconButton(icons.CLOUD_DONE_OUTLINED, on_click=lambda _: self.page.go("/travel_weather_compare_settings")),
                IconButton(icon=flet.icons.REFRESH_OUTLINED, on_click=self.travel_weather_week_compare_clicked),
                #IconButton(icon=flet.icons.WB_SUNNY_OUTLINED, on_click=self.theme_changed)
            ],
        )

        self.create_compare_table()
        
        cv = Column([self.compare_table],scroll=flet.ScrollMode.ADAPTIVE, expand=1, horizontal_alignment=flet.CrossAxisAlignment.START)
        rv = Row([cv], scroll=flet.ScrollMode.ADAPTIVE, expand=1, vertical_alignment=flet.CrossAxisAlignment.START)

        self.appbar.title=Text("Compare week")  
        return View(
            route="/travel_weather_week_compare",
            scroll=flet.ScrollMode.AUTO,
            controls=[
                appbar,
                rv,
                self.navbar
            ]
        )


    def show_city_modal(self, e):

        def close_dlg(e):
            dlg_modal.open = False
            e.control.data['comp'] = check_compare.value
            self.db.update({'comp': check_compare.value}, self.City.name == e.control.data['name'])
            self.change_marker_color(e)
            self.refresh_compare_table()
            self.page.update()

        # Create the content of the modal dialog
        try:

                check_compare = flet.Checkbox(label="Set for Compare", value=e.control.data['comp'])

                # Create the modal dialog
                dlg_modal = AlertDialog(
                    modal=True,
                    title=Text(e.control.data['name']),
                    content=Container(Column([check_compare,]),
                                                alignment=flet.MainAxisAlignment.START,
                                                ),
                    actions=[TextButton("Cansel", data=e.control.data, on_click=lambda e: close_dlg(e)),
                            TextButton("Update", data=e.control.data, on_click=lambda e: close_dlg(e)),
                            TextButton("Delete", data=e.control.data, on_click=lambda e: close_dlg(e))],
                    actions_alignment=MainAxisAlignment.END,
                )           
                # Show the modal dialog
                self.page.dialog = dlg_modal
                dlg_modal.open = True
                self.page.update()

        except Exception as e:
            print(f"Ошибка при загрузке: {e}")


    def travel_weather_cities_view(self):

        data = self.db.all()
        input_name = flet.TextField(label="Name of City")
        city_name = Text("")
    
        mytable =  DataTable(
            columns=[
                DataColumn(Text("City")),
                DataColumn(Text("Set for Compare")), 
                DataColumn(Text("Delete")),
            ],
            rows=[]
        )
        

        
        def recreate_datatable():
            data = self.db.all()
            mytable.rows.clear()
            for city in data:
                mytable.rows.append(
                    DataRow(
                    cells=[
                        DataCell(Text(city['name'])),
                        DataCell(flet.Checkbox( value=city['comp'], data=city, on_change=lambda e:select_item(e))), 
                        DataCell(IconButton(icon=flet.icons.DELETE, data=city, on_click=lambda e:removeitem(e))),
                    ],
                # IF YOU CLIK THIS ROW THEN RUN YOU FUNCTION
                # THIS SCRIPT IS IF CLICK THEN GET THE ID AND NAME OF ROW		
                #on_select_changed=lambda e:select_item(e.control.cells[0].content.value)
                    )
                )
            return mytable
        
            
        def select_item(e):
            print("select name is = ",e.control.data['name'])
            city_name.value = e.control.data['name']
            i = 0
            for i in range(len(mytable.rows)):
                if mytable.rows[i].cells[0].content.value == city_name.value:
                    break

            print("index is = ",i)
            self.db.update({'comp': e.control.value}, self.City.name == city_name.value)

            #self.refresh_compare_table(e)
            
            #addButton.visible = False
            #deleteButton.visible = True
            self.page.update()
        
        def removeitem(e):
            print("remove name is = ",e.control.data['name'])
            self.db.remove(self.City.name == e.control.data['name'])
            recreate_datatable()
            # THEN SHOW SNACK BAR . THIS OPTIONAL
            self.page.snack_bar = flet.SnackBar(
                Text(f"succes delete city  = {e.control.data['name']}",color="white"),
                bgcolor="red",
                )
            self.page.snack_bar.open = True
            #addButton.visible = True
            #deleteButton.visible = False
            self.page.update()
 
        # ADD DATA TO TABLE
        def addnewdata(e):
            geo_data = get_geo_data(input_name.value)
            if geo_data is not None:
                if not self.db.search(self.City.name.matches(input_name.value, flags=re.IGNORECASE)):
                    self.db.insert({'name': input_name.value, 'lat': geo_data[0], 'lon': geo_data[1], 'comp': False})
                    recreate_datatable()
            
                    self.page.snack_bar = flet.SnackBar(
                        Text(f"succes add city  = {input_name.value}",color="white"),
                        bgcolor="green",
                    )

                else:
                    self.page.snack_bar = flet.SnackBar(
                        Text(f"city  = {input_name.value} is already in the database",color="white"),
                        bgcolor="red",)
            else:
                self.page.snack_bar = flet.SnackBar(
                    Text(f"city  = {input_name.value} not found",color="white"),
                    bgcolor="red",)
                
            self.page.snack_bar.open = True
            # THEN BLANK AGAIN THE TEXTFIELD
            input_name.value = ""
            self.page.update()
    
            
        def saveall(e):
            print("you id is = ",e)
 
            for i in range(len(mytable.rows)):
                if mytable.rows[i].cells[1].content.value:
                    self.db.update({'comp': True}, self.City.name == mytable.rows[i].cells[0].content.value)
                else:
                    self.db.update({'comp': False}, self.City.name == mytable.rows[i].cells[0].content.value)

            self.page.snack_bar = flet.SnackBar(
                Text(f"succes save items",color="white"),
                bgcolor="green",
                )
            self.page.snack_bar.open = True
            #self.refresh_compare_table(e)
            self.page.update()
            #self.page.go("/travel_weather_week_compare")
            
        addButton =  flet.ElevatedButton("add new",
            bgcolor="blue",
            color="white",
            on_click=addnewdata
            )
    
	    # DELETEBUTTON
        saveButton =  flet.ElevatedButton("Save all",
            bgcolor="blue",
            color="white",
            on_click=saveall
            )
        
        recreate_datatable()
        
        #deleteButton.visible = False
        self.appbar.title = Text("Compare week")
        return View(
            route="/travel_weather_cities",
            scroll=flet.ScrollMode.AUTO,
            controls=[
                self.appbar,
                Column([
                    #Text("add destinations",size=30,weight="bold"),
                    input_name,
                    Row([addButton]),
                    mytable,
                    #Row([saveButton]),  
                    ]),
                
                self.navbar
            ]
        )
    
    def compare_settings_view(self):
        data = self.db.all()
        city_name = Text("")
    
        mytable =  DataTable(
            columns=[
                DataColumn(Text("City")),
                DataColumn(Text("Compare")),
            ],
            rows=[]
        )
        
        def select_item(e, r):
            print("name is = ",e)
            print("check is = ",r)
            city_name.value = e
            i = 0
            for i in range(len(mytable.rows)):
                if mytable.rows[i].cells[0].content.value == e:
                    break

            print("index is = ",i)
            if r == icons.CHECK_BOX_OUTLINED:
                mytable.rows[i].cells[1].content = Icon(name=icons.CHECK_BOX_OUTLINE_BLANK)
                #self.db.update({'comp': False}, self.City.name == city_name.value)
            else:
                mytable.rows[i].cells[1].content = Icon(name=icons.CHECK_BOX_OUTLINED)
                #self.db.update({'comp': True}, self.City.name == city_name.value)

            #self.refresh_compare_table(e)
            
            self.page.update()    
            
        def recreate_datatable():
            data = self.db.all()
            mytable.rows.clear()
            for city in data:
                mytable.rows.append(
                    DataRow(
                    cells=[
                        # THIS FOR ID THE YOU TABLE 
                        DataCell(Text(city['name'])),
                        #DataCell(Image(src="https://img.icons8.com/ios/50/000000/checked-checkbox.png" if city['comp'] else "https://img.icons8.com/ios/50/000000/unchecked-checkbox.png")),
                        DataCell(Icon(name=icons.CHECK_BOX_OUTLINED if city['comp'] else icons.CHECK_BOX_OUTLINE_BLANK)),
                    ],
	
                on_select_changed=lambda e:select_item(e.control.cells[0].content.value, e.control.cells[1].content.name)
                    )
                )
            return mytable
        
        def saveitems(e):
            print("you id is = ",e)

            for i in range(len(mytable.rows)):
                if mytable.rows[i].cells[1].content == icons.CHECK_BOX_OUTLINED:
                    self.db.update({'comp': True}, self.City.name == mytable.rows[i].cells[0].content.value)
                else:
                    self.db.update({'comp': False}, self.City.name == mytable.rows[i].cells[0].content.value)

            self.page.snack_bar = flet.SnackBar(
                Text(f"succes save items",color="white"),
                bgcolor="green",
                )
            self.page.snack_bar.open = True
            self.refresh_compare_table(e)
            #self.page.update()
            self.page.go("/travel_weather_week_compare")
 
        recreate_datatable()
        self.appbar.title = Text("Compare Settings")
        #self.appbar.automatically_imply_leading = False
        return View(
            route="/travel_weather_compare_settings",
            scroll=flet.ScrollMode.AUTO,
            controls=[
                self.appbar,
                Column([
                    #Text("add destinations",size=30,weight="bold"),
                    mytable,
                    flet.ElevatedButton("Save", on_click = saveitems)    
                    ]),
                    ]
            )
