import sqlite3
from threading import Thread
from time import sleep,time

from read_data import grab_one_serie_for_all_person


class DeviceThread(Thread):
    def __init__(self):
        self.conn = sqlite3.connect('proj.db', check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute("DROP TABLE IF EXISTS measurements")
        self.running = False
        super().__init__()
        self.setDaemon(True)

    def run(self):
        self.running = True
        while self.running:
            # start_all = time()
            measurements = grab_one_serie_for_all_person()
            measurements.to_sql('measurements', con=self.conn, if_exists='append')
            # print(measurements)
            start = time()
            while time() - start < 0.2:
                pass
            # print(time() -start_all)


# %%

