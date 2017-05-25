from start_online_module import *
from rfid_socket_reader import *

socket_readers = []


def before_starting_process():
    #SET TIME OF THE CONTROLLER
    #VALIDATE IDENTITY OF CONTROLLER
    pass

def start_process():
    start_online_module()

    for reader in READERS:
        ethernet_socket = SocketRFIDReader(reader['host'],reader['port'],getQueue())
        ethernet_socket.daemon = True
        ethernet_socket.start()


def after_starting_process():
    sr_queue = getQueue()
    sr_dbcon = getDatabase()

    print 'Database: ',sr_dbcon

    while True:
        while sr_queue.empty():
            time.sleep(3)   #Sleep for 3 seconds

        try:
            item = sr_queue.get(True,2) #Timeout After 2 seconds
            sr_dbcon.insert_card_id( item[0], item[1])
        except Exception as ex:
            print 'QueueException: ',ex


if __name__ == '__main__':
    before_starting_process()
    start_process()
    after_starting_process()
