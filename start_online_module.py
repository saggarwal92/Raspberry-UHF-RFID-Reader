from server_syncer import *
from Queue import Queue

REDIS_POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
REDIS_DB = redis.Redis(connection_pool=REDIS_POOL)

database_conn = DatabaseConnection(REDIS_DB)
database_conn.open_connection()
database_conn.setup_database()

def getQueue():
    return cards_queue

def getDatabase():
    return database_conn


# def sync_on_server():
#     server_syncer.process_upload_on_server()


def start_online_module():

    server_syncer = ServerSyncer()
    server_syncer.daemon = True
    server_syncer.start()

    # #Start Server Sync Timer
    # server_syncer_timer = InfiniteTimer(SERVER_SYNC_TIME,sync_on_server)
    # server_syncer_timer.start()
    #
    # set_scheduler()
