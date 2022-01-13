import sqlite3
import pandas as pd
from PIL import Image
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px


def normalised_column_value(df):
    return df['value'] / max(df['value']) * 100


def get_prepared_measurements():
    con = sqlite3.connect("proj.db")

    tmp_last_name = "Grzegorczyk"

    df_all_measurement = pd.read_sql_query("SELECT * from measurements", con)  # this moment it is one person

    df_all_measurement['value'] = normalised_column_value(df_all_measurement)

    df_all_measurement['time'] = (df_all_measurement['time'] - min(df_all_measurement['time'])) / (
            max(df_all_measurement['time']) - min(df_all_measurement['time']))

    df_all_measurement = df_all_measurement.drop('index', axis=1)

    person_measurements = df_all_measurement[df_all_measurement['lastname'] == tmp_last_name]
    return person_measurements


def plot_single_figure_six_traces_separately_for_all_foots(df_measurements, current, delta):
    title = str(df_measurements['firstname'].unique() + ' ' + df_measurements['lastname'].unique())

    fig = make_subplots(rows=2, cols=3, start_cell="bottom-left", shared_xaxes=True, shared_yaxes=True,
                        subplot_titles=df_measurements['name'].unique(), x_title='time', y_title='value')

    for i in range(6):
        point = \
            df_measurements[
                ((df_measurements['time'] > (current - delta)) & (df_measurements['time'] < (current + delta))) & (
                        df_measurements['id_sensor'] == i)].iloc[
                -1]
        fig.add_trace(go.Scatter(x=df_measurements[df_measurements['id_sensor'] == i]['time'],
                                 y=df_measurements[df_measurements['id_sensor'] == i]['value'],
                                 showlegend=False, mode='lines'),
                      row=int(i / 3) + 1, col=(i % 3) + 1)

        # fig.add_trace(go.Scatter(x= y=df_measurements[df_measurements['id_sensor'] == i]['value'], showlegend=False),
        #               row=int(i / 3) + 1, col=(i % 3) + 1)

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


def create_fig_quartiles(person_measurements: pd.DataFrame):
    fig_quartiles = px.box(
        {'sensor_' + str(i): person_measurements[person_measurements['name'] == i]['value'].values for i in
         person_measurements['name'].unique()})
    fig_quartiles.update_layout(
        title="Quartiles")

    return fig_quartiles


def create_fig_foot(marker_size):
    img = Image.open('stopki.png')

    fig_foot = go.Figure(data=[go.Scatter(
        x=[3.5, 1, 3, 6.5, 9, 7],
        y=[7, 6, 1.5, 7, 6, 1.5],
        mode='markers',
        marker_size=marker_size
    )],
    )

    fig_foot.add_layout_image(
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
            layer="below")
    )

    fig_foot.update_layout(
        template="plotly_white",
    )
    return fig_foot
