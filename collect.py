import requests
import sqlite3
import json
from time import time,ctime,sleep
from read_data import grab_one_serie, grab_one_serie_for_all_person

url = "http://tesla.iem.pw.edu.pl:9080/v2/monitor/2"
dt = requests.get(url)
dt=dt.json()

conn = sqlite3.connect('proj.db')
cur = conn.cursor()


cur.execute("CREATE TABLE IF NOT EXISTS traces(name varchar(10), L0_val int, L1_val int, L2_val int, R0_val int,R1_val int,R2_val int,time int)")
cur.execute("DROP TABLE IF EXISTS measurements")

sql = ''' INSERT INTO traces(name, L0_val, L1_val, L2_val, R0_val,R1_val,R2_val,time)
              VALUES(?,?,?,?,?,?,?,?) '''



while True:
    dt = requests.get(url)
    dt=dt.json()
    task=(dt["firstname"]+' '+dt["lastname"],dt["trace"]["sensors"][0]["value"],dt["trace"]["sensors"][1]["value"],dt["trace"]["sensors"][2]["value"]
     ,dt["trace"]["sensors"][3]["value"],dt["trace"]["sensors"][4]["value"],dt["trace"]["sensors"][5]["value"],time())
    cur.execute(sql, task)
    conn.commit()
    measurements = grab_one_serie_for_all_person()
    measurements.to_sql('measurements', con=conn, if_exists='append')

    sleep(0.1)
    print(task)

# %%
# import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3

# app = dash.Dash(__name__)

con = sqlite3.connect("proj.db")



df = pd.read_sql_query("SELECT * from traces", con)
df_all_measurement  = pd.read_sql_query("SELECT * from measurements", con)

df_measurement_one_person =  df_all_measurement[df_all_measurement['lastname'] == 'Grzegorczyk']
