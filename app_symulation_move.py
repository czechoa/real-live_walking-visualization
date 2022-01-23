import dash
from dash import dcc, html, Output, Input, dash_table

from PIL import Image

from prepared_measurements import get_prepared_measurements

from create_fig import create_fig_foot,create_fig_quartiles,plot_single_figure_six_traces_separately_for_all_foots

# global valous (to do move to json, for share data )
person_measurements = get_prepared_measurements()

anomaly = person_measurements[person_measurements['anomaly'] == 1]
min_time = min(person_measurements['time'])
max_time = max(person_measurements['time'])
step = 0.001
delta = 0.01
slider_left = min_time
slider_middle = (max_time - min_time) / 2
slider_right = max_time
n_intervals = 0

img = Image.open('stopki.png')

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Foot visualization', style={'textAlign': 'center'}),

    html.Div(children='Andrzej Czechowki, Karol Kociołek', style={'textAlign': 'center'}),

    html.H1(children='Person'),

    dcc.Dropdown(
        id='dropdown',
        # options=[{'label': i, 'value': i} for i in df['category'].unique()],
        options=[{'label': "Grzegorczyk", 'value': "Grzegorczyk"}],

        value='Grzegorczyk'
    ),
    dcc.Graph(
        id='scanner_history_foot',
        figure=plot_single_figure_six_traces_separately_for_all_foots(person_measurements, slider_middle, delta),

    ),
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
                {"name": i, "id": i} for i in person_measurements.columns
            ],
            page_current=0,
            page_size=6,
            page_action='custom',
            page_count=int(len(anomaly) / 6),
            style_table={'width': '90vh', 'height': '50vh'}
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
    Input('datatable-paging-page-count', "page_size"))
def update_table(page_current, page_size):
    return anomaly.iloc[
           page_current * page_size:(page_current + 1) * page_size
           ].to_dict('records')


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
    [Input("range-slider", "value")])
def update_middle_slider(slider_range):
    low, current, high = slider_range

    global slider_left, slider_middle, slider_right

    slider_left, slider_middle, slider_right = slider_range

    mask = person_measurements[(person_measurements['time'] > low) & (person_measurements['time'] < high)]

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
        Input('interval-component', 'n_intervals')
    ])
def update_foot_image(hoverData, current_intervals):
    global slider_middle
    global n_intervals
    if current_intervals != n_intervals:
        slider_middle += 0.1
        n_intervals = current_intervals
        if slider_middle > slider_right:
            slider_middle -= 0.1
    else:
        # try:
        if hoverData is not None:
            slider_middle = hoverData['points'][0]['x']
        # except:
        #     pass

    # maybe should be here delta time
    time = slider_middle

    fig_foot = create_fig_foot(person_measurements[person_measurements['time'] == time].iloc[:, -1].values)

    return fig_foot, [slider_left, time, slider_right]


if __name__ == '__main__':
    app.run_server(debug=True)
