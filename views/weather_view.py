import json
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
)
import flet
from tinydb import TinyDB, Query

from weather import get_weather_day

class WeatherTravel():

    def __init__(self, page):
        self.db = TinyDB('db.json')
        self.page = page    
        self.page.theme_mode = ThemeMode.LIGHT
        self.selected_view = '0'
        
        self.appbar = AppBar(
            #leading=Icon(flet.icons.HOME),
            leading=IconButton(
                icon=flet.icons.HOME,
                data='0',
                on_click=self.select_view
            ),
            leading_width=40,
            title=Text("Weather Travel Map", size=20, weight=FontWeight.BOLD),
            center_title=False,
            bgcolor=colors.SURFACE_VARIANT,
            actions=[
                IconButton(icon=flet.icons.WB_SUNNY_OUTLINED, on_click=self.theme_changed),
                PopupMenuButton(
                    icon=flet.icons.MENU,
                    items=[
                        PopupMenuItem(text="  Daily Weather", data='1', on_click=self.weather_travel_map_clicked), 
                        PopupMenuItem(text="  Weekly Weather", data='2', on_click=self.select_view),
                        #PopupMenuItem(text="  Destinations", data='2', on_click=self.select_destinations),
                        PopupMenuItem(text="  About", data='4', on_click=self.show_about_modal),
                    ]
                )
            ],
        )


        self.image_src = ""
        self.image_title = ""
        self.image_url = ""
        self.image_code = ""
        self.image_country = ""
        self.image_games = ""
        self.ctrl = [self.appbar, Container(content='', alignment=flet.alignment.top_center, padding=10)]


        self.main_view = View(
            route="/daily_weather",
            scroll=flet.ScrollMode.AUTO,
            controls=self.ctrl
            #js=[Javascript(analytics_script)]
			)
        
        # Insert Google Analytics script
        analytics_script = """
            <!-- Google tag (gtag.js) -->
            <script async src="https://www.googletagmanager.com/gtag/js?id=G-ED2BNEW5E2"></script>
            <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'G-ED2BNEW5E2');
            </script>
        """


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
        self.page.go("/weather_travel")
        
    def select_view(self, e):
        self.selected_view = e.control.data
        self.refresher()
        self.page.go("/weather_travel")
   



    def on_marker_click(self, e):
        """Handles the marker click event in the weather_travel map view.

        When a marker is clicked, this function is called. It determines the
        selected view and sets the corresponding attributes of the class. The
        page is then navigated to the details page.

        Args:
            e (Event): The event object.
        """
        self.image_src = e.control.data["src"]
        self.image_games = e.control.data["games"]    
        self.image_title = e.control.data["title"]
        self.image_url = e.control.data["url"]
        self.image_code = e.control.data["code"]  
        self.page.go("/details_olympic_map")


    def on_country_click(self, e):
        """Handles the country click event in the countries map view.

        When a country is clicked, this function is called. It determines the
        selected view and sets the corresponding attributes of the class. The
        page is then navigated to the details page.

        Args:
            e (Event): The event object.
        """
        self.image_src = e.control.data["src"]
        self.image_country = e.control.data["country"]
        self.image_title = e.control.data["title"]
        self.image_url = e.control.data["url"]
        self.image_code = e.control.data["code"]  
        self.page.go("/details_country_map")

  
    def weather_travel_map_clicked(self, e):
        self.selected_view = e.control.data
        self.page.go("/daily_weather")
        

    def check_item_clicked(self, e):
        e.control.checked = not e.control.checked
        self.page.update()

 

    def show_about_modal(self, e):
        """Show the 'About' modal dialog."""
        def close_dlg(e):
            """Close the modal dialog."""
            dlg_modal.open = False
            self.page.update()

        # Create the image widget for the modal dialog
        image = flet.Image(src='icons/logo1.png', width=200, height=200) 
        
        # Create the modal dialog with the image
        dlg_modal = flet.AlertDialog(
            modal=True,
            title=flet.Text("About"),
            content=flet.Column([
                image,
                flet.ListTile(
                    title=flet.Text("My coins collection"),
                    subtitle=flet.Text(
                        spans=[
                            flet.TextSpan(
                                "e-mail: mycoins92@gmail.com", 
                                flet.TextStyle(decoration=flet.TextDecoration.UNDERLINE),
                                url="mailto: mycoins92@gmail.com", 
                            )
                        ],
                        size=10,
                    )
                )
            ], 
            alignment=flet.MainAxisAlignment.CENTER,
            horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            height=300,
            ),
            actions=[
                flet.TextButton("Close", on_click=lambda e: close_dlg(e))
            ],
            actions_alignment=flet.MainAxisAlignment.END,
        )            
        # Show the modal dialog
        self.page.dialog = dlg_modal
        dlg_modal.open = True
        self.page.update() 

    def view(self):
        return 	self.main_view


     
   
    """
    Displays a map of Olympic games locations.

    The map is based on OpenStreetMap tiles and includes markers for each Olympic
    games location. Each marker has a tooltip that displays the name of the games
    and the year, and clicking on the marker displays a modal dialog with the
    name, year, and country of the games.

    """
    def weather_travel_map_view(self):

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
                self.page.update()

            # Create the content of the modal dialog
            image = Card(
                elevation=1,
                color=colors.BLUE_GREY_100,
                content=Image(src=e.control.data["icon"], width=200, height=200)  )
            temperature = Text(f"{e.control.data["temperature"]}°C", size=20, weight=FontWeight.BOLD)
            description = Text(e.control.data["description"], no_wrap=False, size=20, weight=FontWeight.BOLD)

            # Create the modal dialog
            dlg_modal = AlertDialog(
                modal=True,
                #title=Text("Olympic Games Details"),
                content=Container(Column([image,temperature,description],alignment=flet.MainAxisAlignment.START,horizontal_alignment=flet.CrossAxisAlignment.CENTER,scroll=flet.ScrollMode.ALWAYS,),),
                actions=[TextButton("Close", on_click=lambda e: close_dlg(e))],
                actions_alignment=MainAxisAlignment.END,
            )            
            # Show the modal dialog
            self.page.dialog = dlg_modal
            dlg_modal.open = True
            self.page.update()

        cities = []
        with open('db.json', 'r') as f:
            data = json.load(f)
            
            
        for city in data:
            weather_day = get_weather_day(city['name'])
            if weather_day is not None:
                combined_data = {**weather_day, **{'lat': city['lat'], 'lon': city['lon']}}
                cities.append(combined_data)
            

        marker_layer_ref = flet.Ref[map.MarkerLayer]()
        circle_layer_ref = flet.Ref[map.CircleLayer]()


        weather_travel_map = map.Map(
            expand=True,
            configuration=map.MapConfiguration(
                initial_center=map.MapLatitudeLongitude(48, 2),
                initial_zoom=3,
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
                    #url_template="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                    on_image_error=lambda e: print("TileLayer Error"),
                ),
                map.MarkerLayer(
                    ref=marker_layer_ref,
                    markers=[
                        
                        map.Marker(
                            content=IconButton(content=Icon(icons.LOCATION_ON, 
                                                    color=colors.BLUE_GREY_500, size=25
                                                    ),
                                            alignment=flet.alignment.center,
                                            data=img,
                                            on_click=lambda e: show_image_modal(e),
                                            #on_click=self.on_marker_click,
                                            tooltip=flet.Tooltip(
                                                message=f"{img["city"]}, {img["temperature"]}°C",
                                                padding=20,
                                                border_radius=10,
                                                bgcolor=colors.WHITE,
                                                shadow=flet.BoxShadow(spread_radius=5, blur_radius=5, color=colors.BLACK),
                                                text_style=flet.TextStyle(size=20, color=colors.BLACK)
                                            )),
                            coordinates=map.MapLatitudeLongitude(img["lat"], img["lon"]),
                        ) for img in cities
                    ],
                ), 
            ],
        )
                                                            
        return View(
            route="/weather_travel_map",
            #scroll=flet.ScrollMode.AUTO,
            controls=[
                self.appbar,
                weather_travel_map,
            ]
        )

        
    """
    flet.Tooltip(
                                        message=img["title"],
                                        content= IconButton(content=Icon(icons.LOCATION_ON, 
                                                    color="red" if img["code"].endswith("s") else "blue",
                                                    #tooltip=img["title"]
                                                ),
                                            alignment=flet.alignment.center,
                                            icon_size=25,
                                            data=img,
                                            #on_click=lambda e: show_image_modal(e)
                                            on_click=self.on_marker_click,
                                        ),
                
                                        padding=20,
                                        border_radius=10,
                                        bgcolor=colors.WHITE,
                                        text_style=flet.TextStyle(size=20, color=colors.BLACK),
                                    ),
    """



    """    
    IconButton(content=Icon(icons.LOCATION_ON, 
                                        color="red" if img["code"].endswith("s") else "blue",
                                        #tooltip=img["title"]
                                    ),
                        alignment=flet.alignment.center,
                        icon_size=25,
                        data=img,
                        #on_click=lambda e: show_image_modal(e)
                        on_click=self.on_marker_click,
                        ),
    """    