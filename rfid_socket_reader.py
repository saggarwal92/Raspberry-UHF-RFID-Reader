import datetime, logging, sys
from device_config import *
import socket
from socket import error as SocketError
import errno
import threading, time
from helper import *
from Queue import Queue

from lru import lru_cache_function
from lru import LRUCacheDict


inMemoryCache = LRUCacheDict(max_size = 160, expiration = READ_TIME_INTERVAL, thread_clear = True)


class SocketRFIDReader(threading.Thread):
    m_addr = None
    m_queue = None

    m_socket = None

    m_buffer = ''
    m_last_ping_time = None

    m_mem_cache = None


    def __init__(self,host,port,queue,baudrate=57600):
        threading.Thread.__init__(self)

        self.m_addr = (host,port)
        print 'Creating Socket Listener for Address: ',self.m_addr

        self.m_buffer = ''
        self.m_queue = queue
        self.m_last_ping_time = time.time()


    """Creates New Socket For Connection"""
    def create_new_socket(self):
        self.m_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                self.m_socket.connect(self.m_addr)
                print 'Socket Created For Address: ',self.m_addr
                break  #Connected To Socket
            except Exception as ex:
                print 'Exception: ',ex
                time.sleep(RECONNECT_SOCKET_TIMESTAMP)    #Sleep For Some Time




    def run(self):
        """ CREATE NEW SOCKET """
        print "Running Thread -> RFIDSocketReader"
        self.create_new_socket()

        while True:
            self.update()



    """ Update Data from Socket """
    def update(self):
        try:
            data = self.m_socket.recv(64)
            if len(data) == 0:
                if time.time() - self.m_last_ping_time > PING_TO_READER_TIMESTAMP:
                    self.m_last_ping_time = time.time()
                    self.m_socket.send('h')
                return

            self.m_buffer += bytes_to_hex(data)
            self.process_buffer()

        except socket.error as se:
            print 'SocketError: ',se
            try:
                self.m_socket.close()
            except Exception as ie:
                print 'Socket Exception While Closing: ',ie
            finally:
                self.create_new_socket()
        except Exception as ex:
            print 'Exception in RFIDSocketReader:update: ',ex




    """ PROCESS BUFFER TO FIND CARDS """
    def process_buffer(self):
        #FINDING CARD ID IN CODE
        while len(self.m_buffer) >= LENGTH_OF_CARD_RAW_DATA:
            start_index = self.m_buffer.find(CARD_DATA_PREFIX)
            if start_index >= 0:
                self.m_buffer = self.m_buffer[start_index:]

                if len(self.m_buffer) >= LENGTH_OF_CARD_RAW_DATA:
                    self.m_buffer = self.m_buffer[CARD_DATA_PREFIX_LENGTH:]

                    next_index = self.m_buffer.find(CARD_DATA_PREFIX)
                    if next_index < 0 or next_index >= CARD_VARIABLE_DATA_LENGTH:
                        card_data = CARD_DATA_PREFIX + self.m_buffer[:CARD_VARIABLE_DATA_LENGTH]
                        self.process_card(card_data)
                    else:
                        self.m_buffer = self.m_buffer[next_index:]
                        print 'Bad Data'
            else:
                print 'Data Incomplete'




    """ PROCESS THIS CARD """
    def process_card(self, card_data):
        """ SEND CARD BYTES """
        if card_data not in inMemoryCache:
            print '<<GOT THIS CARD>>',card_data
            inMemoryCache[card_data] = True
            self.m_queue.put((card_data, int(time.time())) ,True)
