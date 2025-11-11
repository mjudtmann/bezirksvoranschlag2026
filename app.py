# Import data from shared.py
from shared import app_dir, df

from shiny import reactive
from shiny.express import input, render, ui
#from faicons import icon_svg

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

import re
#import contextily as cx

ui.page_opts(title="Bezirke Dashboard", fillable=True)


with ui.sidebar(title="Einstellungen"):
    ui.input_select(  
        "data_select",  
        "Datensatz auswählen:",  
        { k:v for (k,v) in zip(df.columns[20:], df.columns[20:])},  
    )
    
    ui.input_radio_buttons(  
        "radio_farben",  
        "Farbschema",  
        {"Greens": "Grün", "Reds": "Rot", "Cool": "Cool-Warm", "RdYlGn": "Rot-Gelb-Grün", "Magma": "Magma"},  
    )
    
    ui.input_switch("switch", "Farben umkehren", False)
    
    ui.input_radio_buttons(  
        "radio_relation",  
        "Relation",  
        {"Absolut": "Absolut", "Bevölkerung": "Bevölkerung", "Fläche (ha)": "Fläche", "Bezirksbudget (€)": "Bezirksbudget"},  
    )


with ui.layout_columns():

    with ui.card(full_screen=True):
        ui.card_header("Bezirkskarte")

        @render.plot
        def bezirke_karte():
            # initialize the figure
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            
            # define colors
            if input.switch():
                match input.radio_farben():
                    case "Reds":
                        cmap = cm.Reds_r
                    case "Cool":
                        cmap = cm.coolwarm_r
                    case "RdYlGn":
                        cmap = cm.RdYlGn_r
                    case "Magma":
                        cmap = cm.magma_r
                    case _:
                        cmap = cm.Greens_r
            else:
                match input.radio_farben():
                    case "Reds":
                        cmap = cm.Reds
                    case "Cool":
                        cmap = cm.coolwarm
                    case "RdYlGn":
                        cmap = cm.RdYlGn
                    case "Magma":
                        cmap = cm.magma
                    case _:
                        cmap = cm.Greens
            
            min_rate = min(processed_df()[input.data_select()]) 
            max_rate = max(processed_df()[input.data_select()])
            norm = mcolors.Normalize(vmin=min_rate, vmax=max_rate)
            
            # create the plot
            processed_df().plot(column=input.data_select(), cmap=cmap, norm=norm,
                  edgecolor='black', linewidth=0.2, ax=ax)
            ax.axis('off')
            #cx.add_basemap(ax)
             
            # display the plot
            plt.tight_layout()
            return fig
        
    with ui.card(full_screen=True):
        ui.card_header("Tabelle")

        @render.data_frame
        def summary_statistics():
            cols = [
                "Bezirk",
                "Name",
                input.data_select(),
            ]
            return render.DataTable(formated_df()[cols].sort_values(by='Bezirk'), filters=False, height='fit-content')


ui.include_css(app_dir / "styles.css")


@reactive.calc
def processed_df():
    output_df = df.copy()
    if input.radio_relation() != "Absolut":
        output_df[input.data_select()] = df[input.data_select()] / df[input.radio_relation()]
        
    return output_df

@reactive.calc
def formated_df():
    output_df = df.copy()
    if input.radio_relation() != "Absolut":
        output_df[input.data_select()] = df[input.data_select()] / df[input.radio_relation()]
        if input.radio_relation() == "Bezirksbudget (€)" and (re.match(".*(€)", input.data_select()) is not None):
            output_df[input.data_select()] = (output_df[input.data_select()]).map('{:,.2%}'.format)
        else:
            if (re.match(".*(€)", input.data_select()) is not None):
                output_df[input.data_select()] = (output_df[input.data_select()]).map('{:.2f} €'.format)
            else: 
                output_df[input.data_select()] = (output_df[input.data_select()]).map('{:.5f}'.format)
            if input.radio_relation() == "Bezirksbudget (€)":
                output_df[input.data_select()] = (output_df[input.data_select()]).map(lambda x: x + ' / €')
            if input.radio_relation() == "Bevölkerung":
                output_df[input.data_select()] = (output_df[input.data_select()]).map(lambda x: x + ' / Person')
            if input.radio_relation() == "Fläche (ha)":
                output_df[input.data_select()] = (output_df[input.data_select()]).map(lambda x: x + ' / ha')
    else:
        if (re.match(".*(€)", input.data_select()) is not None):
            output_df[input.data_select()] = (output_df[input.data_select()]).map('{:} €'.format) 
    
    return output_df
