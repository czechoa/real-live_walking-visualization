import sqlite3
import pandas as pd
import numpy as np



def normalised_column_value(df):
    return df['value'] / max(df['value']) * 100


def get_prepared_measurements():
    con = sqlite3.connect("proj.db")

    df_all_measurement = pd.read_sql_query("SELECT * from measurements", con)  # this moment it is one person

    conditions = [
        (df_all_measurement['lastname'] == 'Grzegorczyk'),
        (df_all_measurement['lastname'] == 'Kochalska') ,
        (df_all_measurement['lastname'] == 'Lisowski'),
        (df_all_measurement['lastname'] == 'Nosowska'),
        (df_all_measurement['lastname'] == 'Fokalski'),
        (df_all_measurement['lastname'] == 'Moskalski'),
    ]
    choices = [1, 2, 3,4,5,6]

    df_all_measurement.insert(1, 'name_val', np.select(conditions, choices))

    df_all_measurement['value'] = normalised_column_value(df_all_measurement)


    df_all_measurement['time'] = (df_all_measurement['time'] - min(df_all_measurement['time'])).astype(int)



    person_measurements = df_all_measurement.drop('index', axis=1)


    return person_measurements



