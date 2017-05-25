import sqlite3
import datetime
from device_config import *
import redis



CONNECTION_STATE_CLOSED = 0
CONNECTION_STATE_OPENED = 1

TEN_HOURS = 10*24*60*60


class DatabaseConnection:
    conn = None
    connection_state = CONNECTION_STATE_CLOSED

    def __init__(self,redis_obj):
        self.redis_obj = redis_obj

    def open_connection(self):
        self.conn = sqlite3.connect('reader-logs.db')
        self.connection_state = CONNECTION_STATE_OPENED

    def setup_database(self):
        table_command = """
                CREATE TABLE IF NOT EXISTS checkins (
                    card_id varchar(200),
                    in_out varchar(10),
                    read_time timestamp,
                    status int default 0
                );
              """

        self.conn.execute(table_command)
        self.conn.commit()


    def get_connection(self):
        if self.connection_state == CONNECTION_STATE_CLOSED:
            self.open_connection()
        return self.conn

    def commit_connection(self):
        if self.connection_state == CONNECTION_STATE_OPENED:
            self.conn.commit()

    def close_connection(self):
        self.connection_state = CONNECTION_STATE_CLOSED
        self.conn.close()


    def insert_card_id(self, card_id, card_read_time):

        if self.redis_obj.get('SWIPE|'+card_id) is not None:
            print '<<<<<<<<CARD ALREADY EXIST>>>>>>>>>'
            return

        self.redis_obj.set('SWIPE|'+card_id,1,READ_TIME_INTERVAL) #TIME TO LIVE = READ_TIME_INTERVAL
        print '>>>>>>>>NEW CARD FOUND: ',card_id

        in_out = self.redis_obj.get(card_id)

        if in_out is None or in_out is 'out':
            in_out = 'in'
            self.redis_obj.set( card_id, in_out, TEN_HOURS )
        else:
            in_out = 'out'
            self.redis_obj.delete(card_id)

        c = self.get_connection().cursor()
        c.execute("INSERT INTO checkins ('card_id','in_out','read_time') VALUES(?, ?, ?)",( card_id , in_out , card_read_time ))
        self.commit_connection()
