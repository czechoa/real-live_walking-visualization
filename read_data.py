import  requests
import time
import pandas as pd
import json

def get_text_measurments_patient( patient_id: int):
    return requests.get('http://tesla.iem.pw.edu.pl:9080/v2/monitor/'+str(patient_id)).json()

def grab_a_serie_of_measurment(id):
    measurments = []
    stud_obj = get_text_measurments_patient(id)
    measurments.append(stud_obj)
    return measurments

def convert_measurments_to_df(measurments:list):
    df_measurements_described = pd.DataFrame([{**measurment,**{'trace_id': measurment['trace']['id']}} for measurment in measurments for sensor in measurment['trace']['sensors']])
    df_measurements_described = df_measurements_described.drop(columns=['trace'])

    df_measurements_sensors = pd.DataFrame([sensor for measurment in measurments for sensor in measurment['trace']['sensors']])
    df_measurements_sensors = df_measurements_sensors.rename(columns={'id':'id_sensor'})
    df_measurements = pd.concat([df_measurements_described,df_measurements_sensors],axis=1)

    df_measurements.insert(0,'time',add_current_time())

    return df_measurements

def add_current_time():
    return time.time()

def grab_one_serie_for_all_person():
    df_measurements = pd.DataFrame()
    for id in range(1,7):
        measurments = grab_a_serie_of_measurment(id)
        if id == 1:
            df_measurements = convert_measurments_to_df(measurments)

        else:
            df_measurements = df_measurements.append(convert_measurments_to_df(measurments), ignore_index=True)
    return df_measurements

def grab_one_serie(id):
    measurments = grab_a_serie_of_measurment(id)
    df_measurements = convert_measurments_to_df(measurments)
    return df_measurements
# %%
# import time
#
# start = time.time()
# df_measurement = grab_one_serie_for_all_person()
# # print(time.time() - start)
#
# df_measurement_1 = grab_one_serie_for_all_person()
# trace_1 = df_measurement['trace_id'].unique()
# trace_2 = df_measurement_1['trace_id'].unique()
# serie_1 = df_measurement.iloc[1,-1]
# serie_2 = df_measurement_1.iloc[1,-1]
