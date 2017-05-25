from db_handler import *
import threading
import time
import requests
import json



STATUS_NOT_ON_SERVER = 0
STATUS_UPLOADING_ON_SERVER = 1



class ServerSyncer(threading.Thread):
    db_conn = None
    #Run As Timer
    is_uploading_on_server = False

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        """ RUN SYNCER """
        self.db_conn = DatabaseConnection(None)
        self.process_database()

        while True:
            self.process_upload_on_server()
            time.sleep(SERVER_SYNC_TIME)    #TIME DELAY FOR SYNC WITH SERVER

    def process_database(self):
        c = self.db_conn.get_connection().cursor()
        c.execute("UPDATE checkins SET status = 0 WHERE status = 1")
        self.db_conn.commit_connection()

    def is_connected_to_internet(self):
        #CHECK IF CONNECTED TO INTERNET
        return True

    def process_upload_on_server(self):
        if self.is_connected_to_internet() == True and self.is_uploading_on_server == False:
            self.is_uploading_on_server = True  #UPLOADING ON SERVER

            data = self.get_data_to_upload_on_server()
            if len(data) > 0:
                print 'Processing Upload On Server'
                success = self.upload_data_on_server(data)
                self.post_process_data_on_uploaded_on_server(success)

            self.is_uploading_on_server = False #UPLOADING FINISHED ON SERVER
        else:
            pass


    def get_data_to_upload_on_server(self):
        c = self.db_conn.get_connection().cursor()
        c.execute("UPDATE checkins SET status = 1 WHERE status = 0 LIMIT 100")
        self.db_conn.commit_connection()

        r = c.execute("SELECT card_id, in_out, read_time FROM checkins WHERE status = 1")
        cards = r.fetchall()

        list_cards = []
        for card in cards:
            list_cards.append({'cardid':card[0].encode('utf-8'),'in_out':card[1].encode('utf-8'),'timestamp':card[2]})

        return list_cards



    def upload_data_on_server(self,list_cards):
        if len(list_cards) == 0:
            return 0

        data = {
            'school_id':SCHOOL_ID,
            'controller_id': CONTROLLER_ID,
            'cards':list_cards
        }

        data['cards'] = json.dumps(data['cards'])
        res = requests.post(UPLOAD_URL,data=data)
        try:
            a = json.loads(res.content)
            if a['success'] == 1:
                return 1
        except Exception as ex:
            print 'Exception: ',ex

        return 0



    def post_process_data_on_uploaded_on_server(self,success):
        c = self.db_conn.get_connection().cursor()
        if success == 1:
            print "Successfully Uploaded On Server: DELETING ROWS"
            c.execute("DELETE FROM checkins WHERE status = 1")
        else:
            print "Failed To Upload On Server: RESETTING STATUS"
            c.execute("UPDATE checkins SET status = 0 WHERE status = 1")
            #HIT MISSING DATA URL
        self.db_conn.commit_connection()
