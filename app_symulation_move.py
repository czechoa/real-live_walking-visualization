import dash
from dash import dcc, html, Output, Input, dash_table
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image

from prepared_measurements_and_starts_fig import get_prepared_measurements, \
    plot_single_figure_six_traces_separately_for_all_foots, \
    create_fig_quartiles, create_fig_foot

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
    html.H1(children='Wizualizcja stopek', style={'textAlign': 'center'}),

    html.Div(children='Andrzej Czechowki, Karol Kociołek', style={'textAlign': 'center'}),

    html.H1(children='Patterns:'),
    html.H1(children='Person'),

    dcc.Dropdown(
        id='dropdown',
        # options=[{'label': i, 'value': i} for i in df['category'].unique()],
        options=[{'label': "Grzegorczyk", 'value': "Grzegorczyk"}],

        value='Grzegorczyk'
    ),
    dcc.Graph(
        id='scanner_history_foot',
        figure=plot_single_figure_six_traces_separately_for_all_foots(person_measurements),

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
    Output("scanner_history_foot", "figure"),
    [Input("range-slider", "value")])
def update_bar_chart(slider_range):
    low, current, high = slider_range

    global slider_left, slider_middle, slider_right

    slider_left, slider_middle, slider_right = slider_range

    print("slider in range-slider",slider_middle)
    delta = 0.01

    mask = person_measurements[(person_measurements['time'] > low) & (person_measurements['time'] < high)]

    title = str(person_measurements['firstname'].unique() + ' ' + person_measurements['lastname'].unique())

    fig = make_subplots(rows=2, cols=3, start_cell="bottom-left", shared_xaxes=True, shared_yaxes=True,
                        subplot_titles=person_measurements['name'].unique(), x_title='time', y_title='value')

    for i in range(6):
        point = \
            mask[((mask['time'] > (current - delta)) & (mask['time'] < (current + delta))) & (
                    mask['id_sensor'] == i)].iloc[
                -1]

        fig.add_trace(go.Scatter(x=mask[mask['id_sensor'] == i]['time'], y=mask[mask['id_sensor'] == i]['value'],
                                 showlegend=False, mode='lines'),
                      row=int(i / 3) + 1, col=(i % 3) + 1)

        fig.add_trace(go.Scatter(x=[point['time']], y=[point['value']],
                                 showlegend=False, mode='markers'),
                      row=int(i / 3) + 1, col=(i % 3) + 1)

    fig.update_layout(
        title={
            'text': title[2:-2],
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    return fig


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
    print(current_intervals,n_intervals)
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

    print("slider",slider_middle)
    # maybe should be here delta time
    time = slider_middle
    print('new \n',person_measurements[person_measurements['time'] == time].iloc[:, -1])

    fig_foot = create_fig_foot(person_measurements[person_measurements['time'] == time].iloc[:, -1].values)

    return fig_foot, [slider_left, time, slider_right]


if __name__ == '__main__':
    app.run_server(debug=True)
