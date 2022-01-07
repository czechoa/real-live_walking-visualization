import  requests
import time
import pandas as pd
import json

def get_text_measurments_patient( patient_id: int):
    return requests.get('http://tesla.iem.pw.edu.pl:9080/v2/monitor/'+str(patient_id)).json()

# patient = get_text_measurments_patient(1)

def grab_a_series_of_measurments():
    measurments = []
    start = time.time()
    t = []
    while True:
        stud_obj = get_text_measurments_patient(1)
        measurments.append(stud_obj)
        time.sleep(0.1)
        current = time.time()
        elapsed_time = current - start
        t.append(elapsed_time)
        if elapsed_time > 5: # 300 = 5 min
            break
    return measurments,t

def grab_a_serie_of_measurment():
    measurments = []
    stud_obj = get_text_measurments_patient(1)
    measurments.append(stud_obj)
    return measurments

def convert_measurments_to_df(measurments:list):
    df_measurements_described = pd.DataFrame([{**measurment,**{'trace_id': measurment['trace']['id']}} for measurment in measurments for sensor in measurment['trace']['sensors']])
    df_measurements_described = df_measurements_described.drop(columns=['trace'])

    df_measurements_sensors = pd.DataFrame([sensor for measurment in measurments for sensor in measurment['trace']['sensors']])
    df_measurements_sensors = df_measurements_sensors.rename(columns={'id':'id_sensor'})
    df_measurements = pd.concat([df_measurements_described,df_measurements_sensors],axis=1)
    return df_measurements

def grab_one_serie():
    measurments = grab_a_serie_of_measurment()
    df_measurements = convert_measurments_to_df(measurments)
    return df_measurements

# df_measurement = grab_one_serie()
