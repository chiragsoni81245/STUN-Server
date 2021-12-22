from socket import *
import os
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

class STUNServer:

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket_obj = socket(family=AF_INET, type=SOCK_DGRAM)
		self.socket_obj.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self._conn_handler_thread_pool = ThreadPoolExecutor(10)
		self.connections = []

	def bind(self):
		'''
			This function is to bind port with our socket and then
			start listening on that port
		'''
		try:
			print("Binding to port {} ...".format(self.port))
			self.socket_obj.bind(( self.host, self.port ))
			
			# One argument is listen function is the no. of unaccepted connection allowed before refusing new connections
			print("Listening...")
			self.socket_obj.listen(5)
		except socket.error as msg:
			print("Socket Binding error {}".format(str(msg)))
			print("Retrying...")
			self.bind()

	def accept_connections(self):
		'''
			This function is for Establishing Connections before that socket must be listening
		'''
		try:
			while True:
				conn, address = self.socket_obj.accept()
				print("Connection has been established! | {}:{}".format(address[0],address[1]))
				thread = self._conn_handler_thread_pool.submit(
					self.conn_handler, 
					conn, address
				)
				self.connections.append(thread)
		except:
			print("Error in accepting connections")

	def conn_handler(self, conn, address):
		response = "{}:{}\0".format(address[0], address[1])
		response = str.encode(response, 'utf-8')
		conn.send(response)
		conn.close()
		print("Clossed connection of {}:{}".format(address[0], address[1]))

if __name__=="__main__":
	s1 = STUNServer("0.0.0.0", 3478)
	s1.bind()
	s1.accept_connections()
	

