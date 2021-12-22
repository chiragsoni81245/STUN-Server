from socket import *
import os
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from time import sleep

class STUNServer:

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket_obj = socket(family=AF_INET, type=SOCK_DGRAM)
		self.socket_obj.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self._conn_handler_thread_pool = ThreadPoolExecutor(10)
		self.connections = []
		self.received_data = {}

	def bind(self):
		'''
			This function is to bind port with our socket and then
			start listening on that port
		'''
		try:
			print("Binding to port {} ...".format(self.port))
			self.socket_obj.bind(( self.host, self.port ))

		except socket.error as msg:
			print("Socket Binding error {}".format(str(msg)))
			print("Retrying...")
			self.bind()

	def start(self):
		'''
			This function is for Establishing Connections before that socket must be listening
		'''
		self.bind()
		try:
			thread = self._conn_handler_thread_pool.submit(self.receiver)
			while True:
				keys = self.received_data.keys()
				has_to_be_deleted_keys = []
				for address in keys:
					if len(self.received_data[address][0])>6:
						has_to_be_deleted_keys.append(address)
					if self.received_data[address][1]:
						if self.received_data[address][0].decode('utf-8')=="whoami":
							response = "{}:{}\0".format(address[0], address[1])
							for i in response:
								self.socket_obj.sendto(i.encode('utf-8'), address)
							has_to_be_deleted_keys.append(address)
						else:
							has_to_be_deleted_keys.append(address)

				for key in has_to_be_deleted_keys:
					del self.received_data[key]
				sleep(0.01)

		except Exception as error:
			print("Error in starting:")
			print(error)

	def receiver(self):
		while True:
			temp, address = self.socket_obj.recvfrom(1)
			while temp!=b'\x00':
				if address in self.received_data:
					if not self.received_data[address][1]:
						self.received_data[address][0] += temp
				else:
					self.received_data[address] = [temp, False]
				temp, address = self.socket_obj.recvfrom(1)
			self.received_data[address][1] = True

if __name__=="__main__":
	s1 = STUNServer("0.0.0.0", 3478)
	s1.start()
	

