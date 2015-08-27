# -*- coding: utf-8 -*-

import threading
import socket
import logging
import time

from error import Error


class Sink(threading.Thread):
    DEFAULT_RECV_BUFFER_SIZE = 5000000

    def __init__(self, host, sleep_delay=0.1, log=None, on_receive=None, buffer_size=DEFAULT_RECV_BUFFER_SIZE):
        threading.Thread.__init__(self)

        self.log = log or logging.getLogger(__name__)
        self.host = host
        self.sleep_delay = sleep_delay
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active = True
        self.last_received = None
        self.last_com = None
        self.recv_buf_size = buffer_size
        self.on_receive = on_receive
        self.temp = ""

    def connect(self, port):
        try:
            self.sock.connect((self.host, port))
            self.start()
        except socket.error as e:
            raise Error("Can't connect to AceStream socket (%s)" % e[1], Error.CANT_CONNECT)

    def end(self):
        self.active = False

    def send(self, command):
        self.log.debug(">> %s" % command)

        try:
            self.sock.send("%s\r\n" % command)
        except socket.error as e:
            raise Error("Can't send data to AceStream socket (%s)" % e[1], Error.CANT_SEND_DATA)

    def run(self):
        self.log.info("Sink thread going to running state")

        while self.active:
            try:
                self.last_received = self.sock.recv(self.recv_buf_size)
            except socket.error:
                self.last_received = ""

            ind = self.last_received.find("\r\n")
            cnt = self.last_received.count("\r\n")

            if ind != -1 and cnt == 1:
                self.last_received = self.temp + self.last_received[:ind]
                self.temp = ""
                self._exec_com()
            elif cnt > 1:
                fcom = self.last_received
                ind = 1
                while ind != -1:
                    ind = fcom.find("\r\n")
                    self.last_received = fcom[:ind]
                    self._exec_com()
                    fcom = fcom[(ind+2):]
            elif ind == -1:
                self.temp = self.temp + self.last_received
                self.last_received = None

            time.sleep(self.sleep_delay)

        self.log.info("Sink thread stopped")

    def _exec_com(self):
        self.log.debug("<< %s" % self.last_received)

        pos = self.last_received.find(" ")
        if pos >= 0:
            command = self.last_received[:pos]
            params = self.last_received[pos+1:]
        else:
            command = self.last_received
            params = []

        self.on_receive(command, params)
