import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import sqlite3

app = dash.Dash(__name__)

con = sqlite3.connect("proj.db")



df = pd.read_sql_query("SELECT * from traces", con)




df1=df.drop('name',axis=1)
df1=df1.drop('time',axis=1)


a=[df['L0_val'].mean(),df['L1_val'].mean(),df['L2_val'].mean(),df['R0_val'].mean(),df['R1_val'].mean(),df['R2_val'].mean()]
amin, amax = min(a), max(a)
for i, val in enumerate(a):
    a[i] = val/1023 *100


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
])



if __name__ == '__main__':
    app.run_server(debug=True)
