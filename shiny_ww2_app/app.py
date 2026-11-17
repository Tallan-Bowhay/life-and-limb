import pandas as pd
import geopandas as gpd
import gspread

from shiny import render, reactive
from shiny.express import input, ui
from shiny import ui as core_ui
from shiny.express.ui import tooltip
from shiny.ui import page_navbar

import folium
from faicons import icon_svg
from functools import partial


google_creds = gspread.service_account(
    filename=r"C:\Users\Tallan\PycharmProjects\life-and-limb\gspread_creds\carbon-aquifer-513923-s3-07304a64a6a7.json"
)

political_temperature = 1
prep_point_funds = 24

def read_in_google_sheet(
    sheet_id: str,
    sheet_name: str,
    gc: gspread.Client,
    header_row: bool = True,
) -> pd.DataFrame:
    """
    Read a worksheet from a Google Sheet into a pandas DataFrame.
    Requires Google Sheet credentials and sheet Id
    """
    worksheet = gc.open_by_key(sheet_id).worksheet(sheet_name)

    values = worksheet.get_all_values()

    if not values:
        return pd.DataFrame()

    if header_row:
        return pd.DataFrame(values[1:], columns=values[0])

    return pd.DataFrame(values)

world_info_import_df = read_in_google_sheet(
    "1wKrJtO2lsDoDr7y9-O2-gi5AiIgwR7-s_Gyu49MEhko",
    "World Summary Sheet",
    google_creds
)

world_boarders_gdf = gpd.read_file("shiny_ww2_app/geo_data/app_map.geojson")

world_info_gdf = world_boarders_gdf.merge(world_info_import_df, how="inner", on="Name")

polarity_colors = [
    "#B9DFF0",  # Commonwealth
    "#C00000",  # Tripartite
    "#087653",  # Soviet Bloc
    "#E5E5E5",  # Neutral
    "#E5C9EB",  # New Axis
    "#F5C0A9",  # Antifa Asia
]

polarity_order = [
    "The Commonwealth (Allies)",
    "The Tripartite Signatories (Axis)",  # Adjust to exact column value
    "The Soviet Bloc",
    "Neutral/Unaligned",
    "The New Axis",
    "Antifa Asia",
]

polarity_lookup = dict(zip(polarity_order, polarity_colors))

world_info_gdf["Polarity"] = pd.Categorical(
    world_info_gdf["Polarity"],
    categories=polarity_order,
    ordered=True,
)

world_info_gdf["Leader"] = (
    world_info_gdf["Current Leader Title"].fillna("")
    + " "
    + world_info_gdf["Current Leader"].fillna("")
).str.strip()

# anything missing should instead say [REDACTED]

ui.page_opts(
    title = "Intelligence Overview",
    page_fn = partial(page_navbar, id = "navbar"),
)



# ==========================================
# Page 1
# ==========================================

with ui.nav_panel("Global Operations"):
    with ui.layout_sidebar():
        with ui.sidebar():
            ui.input_selectize(
                id = "map_mode_selectize",
                label = "Map Mode:",
                #choices = world_info_gdf.columns.tolist(),
                choices = ["Polarity","Region","Operational Ease","Has Safehouse"],
                selected = "Polarity"
            ),
            # ui.input_action_button(
            #     id = "test_button",
            #     label = "Test Button",
            # )
        with ui.layout_columns(fill=False):
            with ui.value_box(showcase=icon_svg("house")):
                "Active Safehouses"


                @render.text
                def safe_houses():
                    return f"{(world_info_gdf['Has Safehouse'] == 'TRUE').sum()}"

            with ui.value_box(showcase=icon_svg("fire")):
                "Political Temperature"


                @render.text
                def temperature():
                    levels = {0: "Negligible", 1: "Low", 2: "High", 3: "Very High", 4: "Critical"}
                    return levels.get(political_temperature, "Unknown")

            with ui.value_box(showcase=icon_svg("gift")):
                "Funds"
                f"{prep_point_funds}"
        @render.ui
        def world_map_plot():
            map_mode = input.map_mode_selectize()
            if map_mode == "Polarity":
                map_cmap=polarity_colors
            elif map_mode == "Region":
                map_cmap = []
            elif map_mode == "Operational Ease":
                map_cmap="RdYlGn"
            elif map_mode == "Has Safehouse":
                map_cmap=["red", "blue"]
            else:
                return "Map Error"
            world_map = world_info_gdf.explore(
                column=map_mode,
                categorical=True,
                cmap=map_cmap,
                tooltip=["Name","Region","Operational Ease","Polarity","Has Safehouse","Leader"],
                tiles="Esri.WorldShadedRelief",
                # tiles=None,
                min_zoom=2,
                min_lat=-70, max_lat=80,
                min_lon=-150, max_lon=160,
                max_bounds=True,
                tile_kwds={"no_wrap": True},
            )
            world_map.get_root().height = "100%"  # fill the wrapper instead of the 60% default
            world_map.get_root().header.add_child(folium.Element("""
            <style>
            .maplegend {
                left: 20px !important;
                right: auto !important;
                bottom: 50px !important;   /* sits above the scale bar */
            }
            </style>
            """))

            return ui.div(
                ui.HTML(world_map._repr_html_()),
                style="width: 100%; max-width: 1024px; aspect-ratio: 3 / 2; margin: 0 auto;",
            )


# ==========================================
# Page 2
# ==========================================

with ui.nav_panel("Country Details"):
    with ui.layout_sidebar():
        with ui.sidebar():
            ui.input_selectize(
                id = "country_selectize",
                label = "Country:",
                choices = world_info_gdf["Name"].unique().tolist(),
                selected = "United Kingdom"
            )
            ui.input_action_button(
                id = "init_safehouse_button",
                label = "Establish Safehouse",
            )
            ui.input_action_button(
                id="kill_safehouse_button",
                label="Burn Safehouse",
            )


    # Page 2 content
        with ui.layout_columns(fill=False):
            with ui.value_box(
                    showcase=icon_svg("house")
            ):
                "Active Safehouse"
                @render.ui
                def safe_house():
                    if country_gdf()['Has Safehouse'].iloc[0]:
                        return "Yes"
                    else:
                        return "No"
            with ui.value_box(
                showcase=icon_svg("fire")
            ):
                "Operational Ease"
                f"{prep_point_funds}"
            # with ui.value_box(
            #     showcase=icon_svg("gift")
            # ):
            #     "Funds"
            #     f"{prep_point_funds}"
            with ui.value_box(showcase=icon_svg("gift")):
                "Funds"
                core_ui.output_text("funds_display")  # second child is the value
                core_ui.toolbar(  # third child is body content
                    core_ui.toolbar_input_button(
                        id="funds_down",
                        label="Decrease funds",
                        icon=icon_svg("minus"),
                    ),
                    core_ui.toolbar_input_button(
                        id="funds_up",
                        label="Increase funds",
                        icon=icon_svg("plus"),
                    ),
                    align="left",
                )


        with ui.layout_columns(fill=False):
            with ui.value_box(
                    #showcase=icon_svg("handshake")
                    showcase=icon_svg("globe")
            ):
                "Polarity"
                @render.ui
                def polarity():
                    if country_gdf()['Has Safehouse'].iloc[0]:
                        return "Yes"
                    else:
                        return "No"
            with ui.value_box(
                showcase=icon_svg("user")
            ):
                "Leader"
                f"{prep_point_funds}"
            with ui.value_box(
                showcase=icon_svg("user-secret")
            ):
                "Contacts"
                f"{prep_point_funds}"

        with ui.layout_columns(fill=False):
            @reactive.calc
            def country_gdf():
                return world_info_gdf[world_info_gdf["Name"] == input.country_selectize()]

            @render.ui
            def country_map_plot():
                polarity = country_gdf()["Polarity"].iloc[0]
                color = polarity_lookup.get(polarity, "#999999")
                country_map = country_gdf().explore(
                    tiles="Esri.WorldShadedRelief",
                    min_zoom=2,
                    min_lat=-70, max_lat=80,
                    min_lon=-150, max_lon=160,
                    max_bounds=True,
                    color=color,
                    tooltip=["Name", "Region", "Operational Ease", "Polarity", "Has Safehouse", "Leader"],
                )
                #return ui.HTML(country_map._repr_html_())
                return ui.div(
                    ui.HTML(country_map._repr_html_()),
                    style="width: 100%; max-width: 1024px; aspect-ratio: 3 / 2; margin: 0 auto;",
                )
            @render.data_frame
            def contacts_df():
                return world_info_gdf



with ui.nav_panel("Agent Overviews"):
    with ui.layout_sidebar():
        with ui.sidebar():
            ui.input_selectize(
                id = "agent_selectize",
                label = "Agent:",
                choices = ["Handler"],
                selected = "Handler"
            )
        "temp"