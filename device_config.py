import json
from Queue import Queue


SCHOOL_ID = 1
CONTROLLER_ID = 12
UPLOAD_URL = "http://gammalabs.in/test"


PING_TO_READER_TIMESTAMP = 30   #Every 30 seconds
RECONNECT_SOCKET_TIMESTAMP = 30 #Every 30 seconds
LENGTH_OF_CARD_RAW_DATA = 36    #Length of card data read

CARD_DATA_PREFIX = "1100EE00"

SERVER_SYNC_TIME = 5

READ_TIME_INTERVAL = 15



""" LOAD DATA FROM JSON FILE """
fdata = open('config.json','r').read()
config_data = json.loads(fdata)


SCHOOL_ID = config_data['school_id']
CONTROLLER_ID = config_data['controller_id']
UPLOAD_URL = config_data['upload_url']

PING_TO_READER_TIMESTAMP = config_data['reader_ping_timestamp']
RECONNECT_SOCKET_TIMESTAMP = config_data['reconnect_socket_timestamp']
LENGTH_OF_CARD_RAW_DATA = config_data['length_of_card_raw_data']

CARD_DATA_PREFIX = config_data['card_data_prefix']

SERVER_SYNC_TIME = config_data['server_sync_time']
READ_TIME_INTERVAL = config_data['read_time_interval']


# SET OF READERS INSTALLED
READERS = config_data['readers']

""" LOAD DATA FROM JSON FILE """

print 'I am loaded once'

CARD_DATA_PREFIX_LENGTH = len(CARD_DATA_PREFIX)
CARD_VARIABLE_DATA_LENGTH = LENGTH_OF_CARD_RAW_DATA - CARD_DATA_PREFIX_LENGTH



""" VARIABLES USED """
REDIS_POOL = None
REDIS_DB = None

database_conn = None
server_syncer = None
server_syncer_timer = None

cards_queue = Queue()
