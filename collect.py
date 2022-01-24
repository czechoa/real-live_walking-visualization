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

start = time()
delta = 0
while delta < 10* 60: # 10 minunts
    dt = requests.get(url)
    dt=dt.json()
    # task=(dt["firstname"]+' '+dt["lastname"],dt["trace"]["sensors"][0]["value"],dt["trace"]["sensors"][1]["value"],dt["trace"]["sensors"][2]["value"]
    #  ,dt["trace"]["sensors"][3]["value"],dt["trace"]["sensors"][4]["value"],dt["trace"]["sensors"][5]["value"],time())
    # cur.execute(sql, task)
    # conn.commit()


    # measurements = grab_one_serie_for_all_person() # time of that is 0.7 secunds, it too long

    # start = time()
    # measurements = grab_one_serie(1) # one person
    # measurements.to_sql('measurements', con=conn, if_exists='append')
    # measurements = grab_one_serie(2)  # one person
    # measurements.to_sql('measurements', con=conn, if_exists='append')
    # measurements = grab_one_serie(3)  # one person
    # measurements.to_sql('measurements', con=conn, if_exists='append')
    # measurements = grab_one_serie(4)  # one person
    # measurements.to_sql('measurements', con=conn, if_exists='append')
    # measurements = grab_one_serie(5)  # one person
    # measurements.to_sql('measurements', con=conn, if_exists='append')
    # measurements = grab_one_serie(6)  # one person
    # measurements.to_sql('measurements', con=conn, if_exists='append')

    measurements = grab_one_serie_for_all_person()
    measurements.to_sql('measurements', con=conn, if_exists='append')

    stop = time()
    delta = stop - start

    print(delta)    # this procedure take   -0.17148542404174805 for me it to long

    sleep(0.2)

