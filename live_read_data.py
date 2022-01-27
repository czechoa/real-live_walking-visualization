import sqlite3
from threading import Thread
from time import sleep,time

from read_data import grab_one_serie_for_all_person


class DeviceThread(Thread):
    def __init__(self):
        print('start thread')
        self.conn = sqlite3.connect('proj.db', check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute("DROP TABLE IF EXISTS measurements")
        self.running = False
        super().__init__()
        self.setDaemon(True)

    def run(self):
        self.running = True
        while self.running:
            start = time()
            measurements = grab_one_serie_for_all_person()
            measurements.to_sql('measurements', con=self.conn, if_exists='append')
            while time() - start < 1:
                pass
            # print(int(measurements[(measurements['firstname'] == 'Janek') & (measurements['name'] == 'L0') ]['time']))


