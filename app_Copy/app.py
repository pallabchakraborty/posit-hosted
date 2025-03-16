from shiny import App, ui, render, Inputs, Outputs, Session
import folium
import branca
import pandas as pd
import geopandas as gpd
import json
from pathlib import Path

# Define the directory
this_dir = Path(__file__).parent

# maleria_data = pd.read_csv("C:/Users/Asus/Desktop/PyDash/app/Excel/RDT_DATA.csv", usecols= [3, 5, 8, 9, 16])
maleria_data = pd.read_csv(this_dir / "Excel/RDT_DATA.csv", usecols= [3, 5, 8, 9, 16])
maleria_data = pd.DataFrame(maleria_data)

# Load climate data
# climate_data = pd.read_excel("C:/Users/Asus/Desktop/PyDash/app/Excel/12month.xlsx")
climate_data = pd.read_excel(this_dir / "Excel/12month.xlsx")

# Load shapefile and convert to GeoJSON
def load_shapefile(filepath):
    gdf = gpd.read_file(filepath)
    return json.loads(gdf.to_json())

# shapefile_geojson = load_shapefile(r"C:/Users/Asus/Desktop/PyDash/app/Lama_With_Union_V2/Lama_With_Union_V2.shp")
shapefile_geojson = load_shapefile(this_dir / r"Lama_With_Union_V2/Lama_With_Union_V2.shp")


# Extract unique union names
uni_names = [feature['properties']['UNI_NAME'] for feature in shapefile_geojson['features']]

# shapefile = gpd.read_file("C:/Users/Asus/Desktop/PyDash/app/Lama_With_Union_V2/Lama_With_Union_V2.shp")
# gdf = shapefile['UNI_NAME']

# Create color map
color_map = branca.colormap.LinearColormap(colors=["#005F73", "#0A9396", "#94D2BD"], vmin=1, vmax=10)
color_map = color_map.to_step(n=len(shapefile_geojson))

# Style function for GeoJSON
def style_function(feature):
    uni_name = feature["properties"]["UNI_NAME"]
    color = color_map(uni_names.index(uni_name))

    return {
        "fillColor": color,
        "color": "gray",
        "weight": 1,
        "fillOpacity": 0.3,
    }

tooltip = folium.GeoJsonTooltip(
    fields = ["UNI_NAME"]
)

# Create Folium map
def create_map():
    m = folium.Map(location=[21.775295, 92.199113], zoom_start=11)
    folium.TileLayer('Stamen Terrain', name='Stamen Terrain', attr='Map data &copy; <a href="https://developer.here.com">HERE</a>').add_to(m)
    folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(m)

    geojson_layer = folium.GeoJson(shapefile_geojson, style_function=style_function, tooltip = tooltip)
    geojson_layer.add_to(m)

    folium.LayerControl().add_to(m)
    return f'<div style="width:100%; height:580px; margin: 0px; padding: 0px;">{m._repr_html_()}</div>'

# def create_map():
#     m = folium.Map(location=[21.775295, 92.199113], zoom_start=11)
#     cpleth = folium.Choropleth(shapefile_geojson, data=gdf, key_on="features.properties.UNI_NAME", columns=["properties" "UNI_NAME"], fill_Color = "RdYlGn")
#     cpleth.geojson.add_child(tooltip)
#     cpleth.add_to(m)
#     folium.LayerControl().add_to(m)
#     return m

# Define the UI
app_ui = ui.page_navbar(
    ui.nav_spacer(),
        ui.nav_panel(
            "Maleria Report",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_select('union', 'Union', choices=["Aziznagar", "Faitong"])
                ),
                # ui.layout_columns(
                #     ui.value_box("Total cases", ui.output_ui("")),
                #     ui.value_box("Total cases by Disease Type", ui.output_ui("")),
                #     ui.value_box("Total cases by Gender", ui.output_ui("")),
                #     ui.value_box("Most affected age Group", ui.output_ui(""))
                # ),
                ui.h2("Maleria Report"),
                ui.output_data_frame("maleria_data")
            )
        ),

        ui.nav_panel(
                    "Map Viewer",
                    ui.layout_sidebar(
                        ui.sidebar(
                            ui.input_select('union', 'Union', choices=["Aziznagar", "Faitong"]),
                            ui.input_selectize('village', 'Village', choices=list(uni_names), multiple=True),
                            # ui.row(
                            #     ui.input_action_button("select_all_u_m", "Select All"),
                            #     ui.input_action_button("deselect_all_v_m", "Deselect All")
                        ),

                        ui.card(
                            ui.output_ui("map")
                        )
                    ),
                ),
                
        ui.nav_panel(
            "Climate Report",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_selectize('climate_data', "Choose Village:", choices=list(climate_data['Name']), multiple=True),
                    # ui.row(
                    #     ui.input_action_button("select_all_u_c", "Select All"),
                    #     ui.input_action_button("deselect_all_v_c", "Deselect All"),
                     
                ),
            
                ui.h2("Climate data report"),
                ui.output_data_frame("summery_data")
            )
        ),
        title= "Maleria Data Viewer"
)



# Define the server logic
def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.ui
    def map():
        selected_union = input.union()
        selected_villages = input.village()
        return ui.HTML(create_map())

    @render.data_frame
    def summery_data():
        return climate_data

    # @render.data_frame
    # def maleria_data():
    #     return maleria_data

# Create and run the Shiny app
app = App(app_ui, server)
app.run()