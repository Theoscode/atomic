# -*- coding: utf-8 -*-
"""
Spyder Editor


This Script is designed to build a dashboard to display isa-analysis stuff. 


This is a temporary script file.
"""



from dash import Dash , dcc, Input , Output
import dash_bootstrap_components as dbc

title = 'theo dash'

inputs = 'wazzzzup'


app = Dash(__name__ , external_stylesheets = [dbc.themes.BOOTSTRAP])

my_text = dcc.Markdown(children = title)


my_input = dbc.Input(value= inputs)


my_graph = dcc.Graph(figure=fig)


app.layout = dbc.Container([my_text , my_input , my_graph])


## function must follow app callback otherwsie syntax error
@app.callback(
    Output(my_text, component_property='children'),
    Input(my_input , component_property='value')
)



# def update_title(user_input):
#     return user_input * 5

app.run_server(port = 8051)


    
#%%

def run_dash( fig : go.Figure, title  : str = "ISA Analysis"):
    
    app = Dash(__name__ , external_stylesheets = [dbc.themes.BOOTSTRAP])
    
    my_text = dcc.Markdown(children = title)
        
    my_graph = dcc.Graph(figure=fig)
    
    app.layout = dbc.Container([my_text , my_graph])

    app.run_server(port = 8051)



# def update_title(user_input):
#     return user_input

# if __name__ == '__main__':
    
#     run_dash("theos dashboard", "input toolbar")
    
    


    
    
