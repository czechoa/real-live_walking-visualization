import dash
from dash import dcc, html, Output, Input, dash_table
import plotly.graph_objects as go
from flask import Flask


import time

import requests

from PIL import Image

from prepared_measurements import get_prepared_measurements

from create_fig import create_fig_foot,create_fig_quartiles,plot_single_figure_six_traces_separately_for_all_foots

# global valous (to do move to json, for share data )
person_measurements = get_prepared_measurements()


anomaly = person_measurements[person_measurements['name_val'] == 1]
anomaly = anomaly[anomaly['anomaly'] == 1]


min_time = min(person_measurements['time'])
max_time = max(person_measurements['time'])
step = 0.001
delta = 0.01
slider_left = min_time
slider_middle = (max_time - min_time) / 2
slider_right = max_time
n_intervals = 0

url = "http://tesla.iem.pw.edu.pl:9080/v2/monitor/2"
dt = requests.get(url)
dt = dt.json()
marker = [dt["trace"]["sensors"][0]["value"]/1023*100, dt["trace"]["sensors"][1]["value"]/1023*100, dt["trace"]["sensors"][2]["value"]/1023*100, dt["trace"]["sensors"][3]["value"]/1023*100, dt["trace"]["sensors"][4]["value"]/1023*100, dt["trace"]["sensors"][5]["value"]/1023*100]



img = Image.open('stopki.png')

server = Flask(__name__)
app = dash.Dash(__name__,server=server,
    url_base_pathname='/dash/')

@server.route("/dash")
def my_dash_app():
    return app.index()

app.layout = html.Div(children=[
    html.H1(children='Walking visualization', style={'textAlign': 'center'}),

    html.Div(children='Andrzej Czechowki, Karol Kociołek', style={'textAlign': 'center'}),


    html.H1(children='Person'),

    dcc.Dropdown(
        id='dropdown',
        # options=[{'label': i, 'value': i} for i in df['category'].unique()],
        options=[{'label': "Grzegorczyk", 'value': 1},
                 {'label': "Kochalska", 'value': 2},
                 {'label': "Lisowski", 'value': 3},
                 {'label': "Nosowska", 'value': 4},
                 {'label': "Fokalski", 'value': 5},
                 {'label': "Moskalski", 'value': 6}],

        value=1
    ),
    html.H1(children='Patterns:'),
    dcc.Graph(
        id='scanner_history_foot',
        figure=plot_single_figure_six_traces_separately_for_all_foots(person_measurements, slider_middle, delta),

    ),
    html.H1(children='Visualization:'),
    html.Div([
        dcc.Graph(
            id='graph_foot',
            figure=create_fig_foot(person_measurements.iloc[-6:, -1]),
            style={'width': '90vh', 'height': '70vh'}
        ),
        'mean value',
        dcc.Graph(
            id='graph_foot_mean',
            figure=create_fig_foot(person_measurements.iloc[-6:, -1]),
            style={'width': '90vh', 'height': '70vh'}
        ),

    ],
        style={'width': '48%', 'float': 'left', 'display': 'inline-block'}

    ),
    html.Div([
        dcc.RadioItems(
            id='start-stop',
            options=[
                {'label': 'start', 'value': 'start'},
                {'label': 'stop', 'value': 'stop'},
            ],
            value='stop',
            labelStyle={'display': 'inline-block'}
        ),
        'Speed simulations',
        dcc.Dropdown(
            id='speed',
            # options=[{'label': i, 'value': i} for i in df['category'].unique()],
            options=[{'label': str(i / 10), 'value': str(i / 10)} for i in range(11)],

            value='0.0'
        ),

        html.P("Time:"),
        dcc.RangeSlider(
            id='range-slider',
            min=min_time, max=max_time, step=step,
            marks={min_time: str(min_time), max_time: str(max_time)},
            value=[slider_left, slider_middle, slider_right],
            allowCross=False,
            tooltip={"placement": "bottom", "always_visible": True},

            pushable=0.01
        ),
        "Anomaly table",
        dash_table.DataTable(
            id='datatable-paging-page-count',
            columns=[
                {"name": i, "id": i} for i in anomaly.columns
            ],
            page_current=0,
            page_size=6,
            page_action='custom',
            page_count=int(len(anomaly) / 6),
            style_table={'width': '90vh', 'height': '40vh'}
        ),
        dcc.Graph(
            id='quartiles',
            figure=create_fig_quartiles(person_measurements),
            style={'width': '90vh', 'height': '60vh'}
        ),

    ],
        style={'width': '48%', 'float': 'right', 'display': 'inline-block'}
    ),
    #

    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,  # in milliseconds
        n_intervals=0,
        disabled=True
    ),
])


@app.callback(
    Output('datatable-paging-page-count', 'data'),
    Input('datatable-paging-page-count', "page_current"),
    Input('datatable-paging-page-count', "page_size"),
    Input('dropdown', 'value'))
def update_table(page_current, page_size,value):
    anomaly=person_measurements[person_measurements['name_val'] == value]
    anomaly = anomaly[anomaly['anomaly'] == 1]
    return anomaly.iloc[
           page_current * page_size:(page_current + 1) * page_size
           ].to_dict('records')

@app.callback(
    Output('quartiles','figure'),
    Input('dropdown', 'value'))
def update_table(value):
    anomaly=person_measurements[person_measurements['name_val'] == value]
    figure = create_fig_quartiles(anomaly)
    return figure



@app.callback(
    Output('interval-component', 'disabled'),
    Input('start-stop', 'value')
)
def update_output(value):
    if value == 'start':
        return False
    else:
        return True


@app.callback(
    [
    Output("scanner_history_foot", "figure"),
     Output('graph_foot_mean', 'figure'),
     ],
    [Input("range-slider", "value"),
    Input('dropdown', 'value')])
def update_middle_slider(slider_range,value):
    low, current, high = slider_range

    global slider_left, slider_middle, slider_right

    slider_left, slider_middle, slider_right = slider_range
    mask=person_measurements[person_measurements['name_val'] == value]

    mask = mask[(mask['time'] > low) & (mask['time'] < high)]

    fig = plot_single_figure_six_traces_separately_for_all_foots(mask, current, delta)

    fig_foot_mean = create_fig_foot(mask['value'].mean())

    return fig,fig_foot_mean

@app.callback(
    [
        Output('graph_foot', 'figure'),
        Output('range-slider', 'value'),
    ],
    [
        Input('scanner_history_foot', 'hoverData'),
        Input('interval-component', 'n_intervals'),
        Input('dropdown', 'value')
    ])
def update_foot_image(hoverData, current_intervals,value):
    global slider_middle
    global n_intervals
    if current_intervals != n_intervals:
        slider_middle += 0.1
        n_intervals = current_intervals
        if slider_middle > slider_right:
            slider_middle -= 0.1
    else:
        try:
            slider_middle = hoverData['points'][0]['x']
        except:
            pass

    # maybe should be here delta time
    time = slider_middle

    dt = requests.get('http://tesla.iem.pw.edu.pl:9080/v2/monitor/' + str(value)).json()
    marker = [dt["trace"]["sensors"][0]["value"] / 1023 * 100, dt["trace"]["sensors"][1]["value"] / 1023 * 100,
              dt["trace"]["sensors"][2]["value"] / 1023 * 100, dt["trace"]["sensors"][3]["value"] / 1023 * 100,
              dt["trace"]["sensors"][4]["value"] / 1023 * 100, dt["trace"]["sensors"][5]["value"] / 1023 * 100]


    fig_foot = create_fig_foot(marker)

    return fig_foot, [slider_left, time, slider_right]













if __name__ == '__main__':
    app.run_server(debug=True)
