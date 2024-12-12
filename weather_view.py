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
                
                #IconButton(icon=flet.icons.MAPS_HOME_WORK_OUTLINED, on_click=self.travel_weather_map_clicked),
                #IconButton(icon=flet.icons.CLOUD_DONE_OUTLINED, on_click=self.travel_weather_week_compare_clicked),
                #IconButton(icon=flet.icons.SETTINGS_OUTLINED, on_click=self.travel_weather_cities_clicked),
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
                NavigationBarDestination(icon=icons.MAPS_HOME_WORK_OUTLINED, label="Map"),
                NavigationBarDestination(icon=icons.CLOUD_DONE_OUTLINED,  label="Compare"),
                NavigationBarDestination(icon=icons.SETTINGS_OUTLINED,  label="Cities"),
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

    def navbar_event(self, e):
        if e.control.selected_index == 0:
            self.page.go("/travel_weather")	
        if e.control.selected_index == 1:
            self.page.go("/travel_weather_week_compare")
        if e.control.selected_index == 2:
            self.page.go("/travel_weather_cities")
        if e.control.selected_index == 3:
            self.page.go("/more")

    def refresher(self):
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
        self.selected_view = e.control.data
        self.page.go("/travel_weather")
        
    def travel_weather_week_clicked(self, e):
        self.selected_view = e.control.data
        self.page.go("/travel_weather_week")
        
    def travel_weather_week_compare_clicked(self, e):
        self.selected_view = e.control.data
        self.page.go("/travel_weather_week_compare")
    
    def travel_weather_cities_clicked(self, e):
        self.selected_view = e.control.data
        self.page.go("/travel_weather_cities")
        
    def load_image_from_url(self, url):
        #print(url)
        response = requests.get(url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
        else:
            print(f"Не удалось загрузить изображение: {response.status_code}")
            return None
    

   
   
    """
    Displays a map of Olympic games locations.

    The map is based on OpenStreetMap tiles and includes markers for each Olympic
    games location. Each marker has a tooltip that displays the name of the games
    and the year, and clicking on the marker displays a modal dialog with the
    name, year, and country of the games.

    """
    def travel_weather_map_view(self):

        def change_marker_color(e):
            
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
                self.marker_layer_ref.current.markers[marker_index] = map.Marker(
                                content=IconButton(content=Icon(icons.CLOUD, color=flet.colors.RED_500, size=20 ),
                                                alignment=flet.alignment.center,
                                                data=e.control.data,
                                                on_click=lambda e: show_image_modal(e),
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
            
        def show_image_modal(e):
            """
            Shows a modal dialog with the details of the Olympic games.

            The dialog includes the name, year, and country of the games, as well
            as a link to the official website of the Olympic Games.

            Args:
                e (Event): The event that triggered the modal dialog.
            """
            def close_dlg(e):
                """
                Closes the modal dialog.

                Args:
                    e (Event): The event that triggered the dialog close.
                """
                dlg_modal.open = False
                change_marker_color(e)
                self.page.update()

            # Create the content of the modal dialog
            try:
                weather_day = get_weather_day(e.control.data['name'])
                if weather_day is not None:

                    image = Card(
                        elevation=1,
                        color=colors.BLUE_GREY_100,
                        content=Image(src_base64=self.load_image_from_url(weather_day['icon']), width=200, height=200)  )
                        #content=Image(src=self.image_src, width=200, height=200)  ) 
                        #content=Image(src="images/50n@2x.png", width=200, height=200)  )

                    temperature = Text(f"{weather_day["temperature"]}°C", size=20, weight=FontWeight.BOLD)
                    description = Text(weather_day["description"], no_wrap=False, size=20, weight=FontWeight.BOLD)

                    # Create the modal dialog
                    dlg_modal = AlertDialog(
                        modal=True,
                        title=Text(e.control.data['name']),
                        content=Container(Column([image, temperature,description],alignment=flet.MainAxisAlignment.START,horizontal_alignment=flet.CrossAxisAlignment.CENTER,scroll=flet.ScrollMode.ALWAYS,),),
                        actions=[TextButton("Close", data=e.control.data, on_click=lambda e: close_dlg(e))],
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

        cities = []
        """
        with open('db.json', 'r') as f:
            data = json.load(f)
        """
            
        data = self.db.all()

        weather_travel_map = map.Map(
            expand=True,
            configuration=map.MapConfiguration(
                initial_center=map.MapLatitudeLongitude(48, 20),
                initial_zoom=4.2,
                interaction_configuration=map.MapInteractionConfiguration(
                    flags=map.MapInteractiveFlag.ALL
                ),
                on_init=lambda e: print(f"Initialized Map"),
                #on_tap=handle_tap,
                #on_secondary_tap=handle_tap,
                #on_long_press=handle_tap,
                #on_event=handle_event,
            ),
            layers=[
                map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=lambda e: print("TileLayer Error"),
                ),
                map.RichAttribution(
                    attributions=[
                        map.TextSourceAttribution(
                            text="OpenStreetMap Contributors",
                            on_click=lambda e: e.page.launch_url(
                                "https://openstreetmap.org/copyright"
                            ),
                        ),
                        map.TextSourceAttribution(
                            text="Flet222",
                            on_click=lambda e: e.page.launch_url("https://flet.dev"),
                        ),
                    ]
                ),
                map.SimpleAttribution(
                    text="Flet111",
                    alignment=flet.alignment.top_right,
                    on_click=lambda e: print("Clicked SimpleAttribution"),
                ),
                map.MarkerLayer(
                    ref=self.marker_layer_ref,
                    markers=[
                        map.Marker(
                            content=IconButton(content=Icon(icons.CLOUD, color="#36618e", size=20 ),
                                            alignment=flet.alignment.center,
                                            data=city,
                                            on_click=lambda e: show_image_modal(e),
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
                            
                        ) for city in data
                    ],
                ), 
            ],
        )
        self.appbar.title=Text("MTW")                                                
        return View(
            route="/travel_weather",
            #scroll=flet.ScrollMode.AUTO,
            controls=[
                self.appbar,
                weather_travel_map,
                self.navbar
            ]
        )

    def travel_weather_week_view(self):

        cities = []
        data = self.db.all()
                    
        cities = ['Minsk','Milan', 'Venezia', 'Prague', 'Marianske Lazne']
        cities_weather = []
    
        for city in data:
            weather_data = get_weather_week(city['name'])
            if weather_data:
                cities_weather.append(weather_data)
        
        columns = [DataColumn(Text(city['city'])) for city in cities_weather]
            
        
        rows = []
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
                    horizontal_alignment=flet.CrossAxisAlignment.CENTER
                )],alignment=MainAxisAlignment.CENTER)

                # Оборачиваем содержимое ячейки в Container и задаем высоту
                cell_container = Container(
                    content=cell_content,
                    #height=95,  # Установите необходимую высоту
                    #padding=5,    # Добавляем внутренние отступы
                    alignment='center', # Выравнивание по центру
                )

                #cells.append(DataCell(cell_container))
                cells.append(DataCell(cell_content))
            rows.append(DataRow(cells=cells))
        
        table = DataTable(          
             
            data_row_min_height=100,
            data_row_max_height=100,
            columns=columns, rows=rows)
        
        cv = Column([table],scroll=flet.ScrollMode.ADAPTIVE, expand=1, horizontal_alignment=flet.CrossAxisAlignment.START)
        rv = Row([cv], scroll=flet.ScrollMode.ADAPTIVE, expand=1, vertical_alignment=flet.CrossAxisAlignment.START)

                
        header = Row(
            controls=[ Container(
                    content=Text(city['city'], weight="bold"),
                    alignment=alignment.center,
                    padding=5,
                    border=flet.border.only(bottom=flet.border.BorderSide(1, "black"))
                )
                for city in cities_weather
            ]
        )

        # Создаем тело таблицы
        body = Column()
        num_days = len(cities_weather[0]['forecast'])

        for i in range(num_days):
            row = Row(
                controls=[ ]
            )
            for city in cities_weather:
                forecast_info = city['forecast'][i]
                cell_content = Column(
                    controls=[
                        Text(cities_weather[0]['forecast'][i]['day']),
                        Image(src=forecast_info['icon'], width=50, height=50),
                        Text(forecast_info['temperature'])
                    ],
                    alignment='center',
                    spacing=5
                )
                row.controls.append(
                    Container(
                        content=cell_content,
                        alignment=alignment.center,
                        padding=5,
                        border=flet.border.only(bottom=flet.border.BorderSide(1, "lightgrey"))
                    )
                )
            body.controls.append(row)

        self.appbar.title=Text("Compare week")  
        return View(
            route="/travel_weather_week",
            scroll=flet.ScrollMode.AUTO,
            controls=[
                self.appbar,
                rv,
                #table,
                #header,
                #body,
                self.navbar
            ]
        )


    def travel_weather_cities_view(self):

        cities = []
        City = Query()
        data = self.db.all()
        input_name = flet.TextField(label="Name of City")
        city_name = Text("")
    
        # CREATE DATATABLE HERE
        mytable =  DataTable(
            columns=[
                DataColumn(Text("City")),
                #DataColumn(Text("Latitude")),
                #DataColumn(Text("longitude")),
            ],
            # THIS IS YOU ROW OF YOU TABLE
            rows=[]
        )
        
        def recreate_datatable():
            data = self.db.all()
            mytable.rows.clear()
            for city in data:
                mytable.rows.append(
                    DataRow(
                    cells=[
                        # THIS FOR ID THE YOU TABLE 
                        DataCell(Text(city['name'])),
                        #DataCell(Text(city['lat'])),
                        #DataCell(Text(city['lon'])),
                    ],
                # IF YOU CLIK THIS ROW THEN RUN YOU FUNCTION
                # THIS SCRIPT IS IF CLICK THEN GET THE ID AND NAME OF ROW		
                on_select_changed=lambda e:select_item(e.control.cells[0].content.value)
                    )
                )
            return mytable
        
            
        def select_item(e):
            print("you id is = ",e)
            city_name.value = e
            addButton.visible = False
            deleteButton.visible = True
            self.page.update()

        
        def removeitem(e):
            print("you id is = ",e)
            self.db.remove(City.name == city_name.value)
            recreate_datatable()
            # THEN SHOW SNACK BAR . THIS OPTIONAL
            self.page.snack_bar = flet.SnackBar(
                Text(f"succes delete city  = {city_name.value}",color="white"),
                bgcolor="red",
                )
            self.page.snack_bar.open = True
            addButton.visible = True
            deleteButton.visible = False
            self.page.update()
 
        # ADD DATA TO TABLE
        def addnewdata(e):
            geo_data = get_geo_data(input_name.value)
            if geo_data is not None:
                if not self.db.search(City.name.matches(input_name.value, flags=re.IGNORECASE)):
                    self.db.insert({'name': input_name.value, 'lat': geo_data[0], 'lon': geo_data[1]})
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
    
        addButton =  flet.ElevatedButton("add new",
            bgcolor="blue",
            color="white",
            on_click=addnewdata
            )
    
	    # DELETEBUTTON
        deleteButton =  flet.ElevatedButton("delete this",
            bgcolor="red",
            color="white",
            on_click=removeitem
    
        )
        
        recreate_datatable()
        
        deleteButton.visible = False
        return View(
            route="/travel_weather_cities",
            scroll=flet.ScrollMode.AUTO,
            controls=[
                self.appbar,
                Column([
                    Text("my crud sample",size=30,weight="bold"),
                    input_name,
                    Row([addButton, deleteButton]),
                    mytable,
   
                    ]),
                
                self.navbar
            ]
        )
