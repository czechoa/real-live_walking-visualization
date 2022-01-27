import dash
from dash import dcc, html, Output, Input, dash_table
from flask import Flask
from time import sleep
from PIL import Image

from live_read_data import DeviceThread
from prepared_measurements import get_prepared_measurements

from create_fig import create_fig_foot, create_fig_quartiles, plot_single_figure_six_traces_separately




server = Flask(__name__)
app = dash.Dash(__name__,server=server,
    url_base_pathname='/dash/')

@server.route("/dash")
def my_dash_app():

    return app.index()

# if __name__ == '__main__':
#     app.run_server(debug=True)

print('before thread \n')
thread = DeviceThread()
thread.start()
sleep(10)
# sleep(10)
# global valous (to do move to json, for share data )
print('data')
measurements_all = get_prepared_measurements()
current_person = 1
person_measurements = measurements_all

anomaly = person_measurements[person_measurements['name_val'] == current_person]
anomaly = anomaly[anomaly['anomaly'] == 1]


min_time = min(person_measurements['time'])
max_time = max(person_measurements['time'])
step = 1
# speed = 1
interval = 1 * 1000 # 1 s

slider_left = min_time
slider_middle = (max_time - min_time) / 2
slider_right = max_time
old_hoverData = 0

n_intervals = 0

img = Image.open('stopki.png')


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
        figure=plot_single_figure_six_traces_separately(person_measurements, slider_middle),

    ),
    html.H1(children='Visualization:'),
    html.Div([
        dcc.Graph(
            id='graph_foot',
            figure=create_fig_foot(person_measurements.iloc[-6:, -1],'blue'),
            style={'width': '90vh', 'height': '70vh'}
        ),
        'mean value',
        dcc.Graph(
            id='graph_foot_mean',
            figure=create_fig_foot(person_measurements.iloc[-6:, -1],'blue'),
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
            options=[{'label': str(i/10), 'value': str(i/10)} for i in range(21)],

            value='1.0'
        ),

        html.P("Time:"),
        dcc.RangeSlider(
            id='range-slider',
            min=min_time, max=max_time, step=step,
            marks={min_time: str(min_time), max_time: str(max_time)},
            value=[slider_left, slider_middle, slider_right],
            allowCross=False,
            tooltip={"placement": "bottom", "always_visible": True},

            pushable= step
        ),
        "Anomaly table",
        dash_table.DataTable(
            id='datatable-paging-page-count',
            columns=[
                {"name": i, "id": i} for i in anomaly.columns[[1,10,11]]
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
        interval= interval,  # in milliseconds
        n_intervals=0,
        disabled=True
    ),
])


@app.callback([
    Output('datatable-paging-page-count', 'data'),
    Output('quartiles', 'figure'),
    ],

    [Input('datatable-paging-page-count', "page_current"),
    Input('datatable-paging-page-count', "page_size"),
    Input('dropdown', 'value') ]

)
def update_table(page_current, page_size,value):
    global current_person
    global person_measurements
    print('\n',value)
    current_person = value
    person_measurements = measurements_all[measurements_all['name_val'] == value]

    anomaly = person_measurements[person_measurements['anomaly'] == 1]
    print('anomaly',anomaly)
    return anomaly.iloc[
           page_current * page_size:(page_current + 1) * page_size,
           ].to_dict('records') ,create_fig_quartiles(person_measurements)

@app.callback(

    Output('interval-component', 'disabled'),
    Output('interval-component', 'interval'),

    Input('start-stop', 'value'),
    Input('speed','value')

)
def update_output(start_stop,speed):
    speed = float(speed)
    if start_stop == 'start':
        return False, interval / speed
    else:
        return True, interval / speed

@app.callback(
    [
    Output("scanner_history_foot", "figure"),
    Output('graph_foot_mean', 'figure'),
    ],
    [
        Input("range-slider", "value"),
        Input('dropdown', 'value')
     ])
def update_fig_foot(slider_range, name_value):
    low, current, high = slider_range

    mask = person_measurements[(person_measurements['time'] > low) & (person_measurements['time'] < high)]

    fig = plot_single_figure_six_traces_separately(mask, current)

    fig_foot_mean = create_fig_foot(mask['value'].mean(),'blue')

    qualities = create_fig_quartiles(mask),

    return fig,fig_foot_mean

@app.callback(
    [
        Output('graph_foot', 'figure'),
        Output('range-slider', 'value'),
        Output('range-slider', 'max'),
    ],
    [

        Input('scanner_history_foot', 'hoverData'),
        Input('interval-component', 'n_intervals'),
        Input('dropdown', 'value'),
        Input("range-slider", "value"),

    ])
def update_foot_image(hoverData, current_intervals,name_val, ranger_slider):
    global slider_middle
    global slider_right
    global slider_left

    global n_intervals
    global  old_hoverData
    global measurements_all
    global person_measurements
    global max_time

    if current_intervals != n_intervals:
        measurements_all = get_prepared_measurements()
        person_measurements = measurements_all[measurements_all['name_val'] == current_person]
        max_time = max(person_measurements['time'])

        if slider_middle < max_time:
            slider_middle += step

        n_intervals = current_intervals

        if slider_middle == slider_right -1 and slider_right <= max_time:
            slider_right += step

    else:

        if hoverData is not None and old_hoverData != hoverData['points'][0]['x']:

            slider_middle = hoverData['points'][0]['x']
            old_hoverData = hoverData['points'][0]['x']

        elif slider_middle != ranger_slider[1]:
            slider_middle = ranger_slider[1]

        if slider_left != ranger_slider[0]:
            slider_left = ranger_slider[0]

        if slider_right != ranger_slider[2]:
            slider_right = ranger_slider[2]



    time = slider_middle

    is_an=any(person_measurements[person_measurements['time'] == time]['anomaly'].values ==1 )
    if is_an:
        fig_foot = create_fig_foot(person_measurements[person_measurements['time'] == time]['value'].values,'red')
    else:
        fig_foot = create_fig_foot(person_measurements[person_measurements['time'] == time]['value'].values, 'blue')



    return fig_foot, [slider_left, time, slider_right], max_time



