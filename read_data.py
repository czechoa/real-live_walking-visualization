import  requests
import time
import pandas as pd
import json

def get_text_measurments_patient( patient_id: int):
    return requests.get('http://tesla.iem.pw.edu.pl:9080/v2/monitor/'+str(patient_id)).json()

def get_text_measurments_patient_for_all_patient( ):
    return [requests.get('http://tesla.iem.pw.edu.pl:9080/v2/monitor/'+str(patient_id)).json() for patient_id in range(1,7)]


def grab_a_serie_of_measurment(id, measurments = []):
    stud_obj = get_text_measurments_patient(id)
    measurments.append(stud_obj)
    return measurments


def grab_a_serie_of_measurments_for_all_patients(id, measurments = []):
    measurments.append(get_text_measurments_patient(id))
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
    measurments = []

    for id in range(1,7):
        measurments = grab_a_serie_of_measurment(id,measurments)


    df_measurements = convert_measurments_to_df(measurments)

    return df_measurements

def grab_one_serie(id):
    measurments = grab_a_serie_of_measurment(id)
    df_measurements = convert_measurments_to_df(measurments)
    return df_measurements
# %%
import  time
start = time.time()
result = grab_one_serie_for_all_person()
print(time.time() - start)

