import sqlite3
import pandas as pd



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



