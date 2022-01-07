import requests
import sqlite3
import json
from time import time,ctime,sleep

url = "http://tesla.iem.pw.edu.pl:9080/v2/monitor/2"
dt = requests.get(url)
dt=dt.json()

conn = sqlite3.connect('proj.db')
cur = conn.cursor()

# cur.execute("CREATE TABLE  traces(name varchar(10), L0_val int, L1_val int, L2_val int, R0_val int,R1_val int,R2_val int,time int)")

sql = ''' INSERT INTO traces(name, L0_val, L1_val, L2_val, R0_val,R1_val,R2_val,time)
              VALUES(?,?,?,?,?,?,?,?) '''

while True:
    dt = requests.get(url)
    dt=dt.json()
    task=(dt["firstname"]+' '+dt["lastname"],dt["trace"]["sensors"][0]["value"],dt["trace"]["sensors"][1]["value"],dt["trace"]["sensors"][2]["value"]
     ,dt["trace"]["sensors"][3]["value"],dt["trace"]["sensors"][4]["value"],dt["trace"]["sensors"][5]["value"],time())
    cur.execute(sql, task)
    conn.commit()
    sleep(0.5)
    print(task)
