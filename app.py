import dash
from dash import dcc, html, Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import sqlite3

app = dash.Dash(__name__)

con = sqlite3.connect("proj.db")


df = pd.read_sql_query("SELECT * from traces", con)
df_all_measurement  = pd.read_sql_query("SELECT * from measurements", con) # this moment it is one person

def plot_single_figure_six_traces_separately_for_all_foots(df_measurements):
    title  = str(df_measurements['firstname'].unique() + ' ' +  df_measurements['lastname'].unique())
    fig = make_subplots(rows=2, cols=3, start_cell="bottom-left",shared_xaxes = True,shared_yaxes= True, subplot_titles = df_measurements['name'].unique(),x_title= 'time',y_title='value')
    for i in range(6):
        fig.add_trace(go.Scatter(y=df_measurements[df_measurements['id_sensor'] == i]['value'],showlegend=False),
                row= int(i/3)+1, col=  (i % 3)+1)
    fig.update_layout(
    title={
        'text': title[2:-2],
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    # fig.show()
    return fig

time = df['time']

df1=df.drop('name',axis=1)
df1=df1.drop('time',axis=1)


a=[df['L0_val'].mean(),df['L1_val'].mean(),df['L2_val'].mean(),df['R0_val'].mean(),df['R1_val'].mean(),df['R2_val'].mean()]
current_value =  [df['L0_val'].iloc[-1],df['L1_val'].iloc[-1],df['L2_val'].iloc[-1],df['R0_val'].iloc[-1],df['R1_val'].iloc[-1],df['R2_val'].iloc[-1]]

# normalized_df=(df1-df1.min())/(df1.max()-df1.min())


amin, amax = min(a), max(a)
for i, val in enumerate(a):
    a[i] = val/1023 *100

amin, amax = min(current_value), max(current_value)
for i, val in enumerate(current_value):
    current_value[i] = val/1023 *100

img = Image.open('stopki.png')


fig = go.Figure(data=[go.Scatter(
    x=[3.5, 1, 3, 6.5,9,7], y=[7, 6, 1.5, 7, 6, 1.5],
    mode='markers',
    marker_size=a,
    )
])

fig.add_layout_image(
        dict(
            source=img,
            xref="x",
            yref="y",
            x=0,
            y=10,
            sizex=10,
            sizey=10,
            sizing="stretch",
            opacity=0.5,
            layer="below"),

)

fig.update_layout(
    template="plotly_white",
    title="Mean values")


fig2 = px.box(df1)
fig2.update_layout(
    title="Quartiles")



fig3 = go.Figure(data=[go.Table(header=dict(values=['Time', 'Place']),
                 cells=dict(values=[[100, 90, 80, 90], [95, 85, 75, 95]]))
                     ])
fig3.update_layout(
    title="Anomaly")

fig5 = go.Figure(data=[go.Scatter(
    x=[3.5, 1, 3, 6.5,9,7],
    y=[7, 6, 1.5, 7, 6, 1.5],
    mode='markers',
    marker_size=current_value
    )],
)


fig5.add_layout_image(
        dict(
            source=img,
            xref="x",
            yref="y",
            x=0,
            y=10,
            sizex=10,
            sizey=10,
            sizing="stretch",
            opacity=0.5,
            layer="below"),

)

fig5.update_layout(
    template="plotly_white",
    title="current values")


app.layout = html.Div(children=[
    html.H1(children='Wizualizcja stopek',style={'textAlign': 'center'}),

    html.Div(children='Andrzej Czechowki, Karol Kociołek',style={'textAlign': 'center'}),

    html.Div(children='Patient:'),
    dcc.Dropdown(
        id='fig_dropdown',
        options=[{'label': 'Karol', 'value': 'Karol'}],
        value=None
    ),

    dcc.Graph(
        id='graph',
        figure=fig,
        style={'width': '90vh', 'height': '90vh'}
    ),

    dcc.Graph(
        id='graph2',
        figure=fig2,
        style={'width': '180vh', 'height': '90vh'}
    ),

    html.Button('START', id='button1'),
    html.Button('STOP', id='button2'),
    html.Button('NEXT', id='button3'),
    html.Button('PREVIOUS', id='button4'),

    dcc.Graph(
        id='graph3',
        figure=fig,
        style={'width': '90vh', 'height': '90vh'}
    ),

    dcc.Graph(
        id='graph4',
        figure=fig3,
        style={'width': '180vh', 'height': '90vh'}
    ),

    html.H1(children='Patterns:'),
    html.H1(children='co to wgl znaczy wzor chodzenia, nwm jakas prenetacja stopek tu pewnie bedzie'),

    html.Button('START', id='button_start'),
    html.Button('STOP', id='button_stop'),
    # html.Button('NEXT', id='button3'),
    # html.Button('PREVIOUS', id='button4'),

    html.H1(children='Speed'),
    dcc.Slider(
        id='speed-slider',
        min=0,
        max=2,
        step=0.1,
        value=1,
    ),

    dcc.Graph(
        id='graph5',
        figure=fig5,
        style={'width': '90vh', 'height': '90vh'}
    ),

    html.H1(children='Time'),
    dcc.Slider(
        id='time-slider',
        min=0,
        max=10,
        step=1,
        # value=time[-1],
        value=1,


    ),
    html.H1(children='delta-time'),

    dcc.Slider(
        id='delta-time-slider',
        min=0,
        max=5,
        step=0.1,
        # value=time[-1],
        value=1,

        marks={
            0: '0',
            1: '1',

            5: '2',
            10: '10',
        }
    ),
    dcc.Graph(
        id='graph6',
        figure=plot_single_figure_six_traces_separately_for_all_foots(df_all_measurement[df_all_measurement['lastname'] == 'Grzegorczyk']),
        # style={'width': '180vh', 'height': '180vh'}
    ),
    html.Div(id='slider-output-container')
])


# @app.callback(
#     dash.dependencies.Output('graph5', 'figure'),
#     [dash.dependencies.Input('time-slider', 'value')])
# def update_output(value):
#     return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)
