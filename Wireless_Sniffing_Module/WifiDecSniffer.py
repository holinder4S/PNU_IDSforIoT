import fcntl
import time
import os
import re
import socket
import struct
import sys
from subprocess import Popen, PIPE
from prettytable import PrettyTable

import APscan
#import DecSniffer

class WifiSniffer:
	def __init__(self):
		self.wlan = WLAN()
		self.APscanner = APscan.APscanner(self.wlan)
		#self.DecSniffer = DecSniffer.DecSniffer(self.wlan)
		self.is_apscan = False
		self.is_decsniff = False

	def APscan_start(self):
		if self.__thread_check():
			return
		iface_list = self.get_wlan_iface_list()
		iface_table = PrettyTable(['Index','Wlan Interface'])
		for i in xrange(len(iface_list)):
			iface_table.add_row([str(i), iface_list[i]])
		print iface_table

		iface_index = int(raw_input("Please Select interface : "))
		self.wlan.set_interface(iface_list[iface_index])

		print "[+] AP scanning started~!"
		self.is_apscan = True
		self.wlan.monitoring_start()
		self.APscanner.start()

	def APscan_stop(self):
		if self.is_apscan:
			self.is_apscan = False
			self.APscanner.stop()
			print "[+] AP scanning stopped~!"

	def __thread_check(self):
		if self.is_apscan:
			print "[ERROR] APscan_thread is running!"
			return True
		elif self.is_decsniff: 
			print "[ERROR] DecSniff_thread is running!"
			return True
		return False

	def get_wlan_iface_list(self):
		try:
			p = Popen('iwconfig', stdout=PIPE, stderr=PIPE)
		except OSError:
			print "[ERROR] Could not execute 'iwconfig'"
			exit(-1)
		
		response = p.communicate()[0]
		interface_list = []
		try:
			interface_list = map(lambda x: x[:-4].strip(' '), re.findall('([^\s].*IEEE)', response))
		except:
			interface_list = []
		
		return interface_list

class WLAN:
	MAX_CHANNEL = 13
	
	def __init__(self):
		self.interface = ''
		self.mac = ''
		self.channel = 1

	def monitoring_start(self):
		try:
			p = Popen(['iwconfig', self.interface], stdout=PIPE, stderr=PIPE)
		except OSError:
			print "[ERROR] Could not execute 'iwconfig'"
			exit(-1)

		response = p.communicate()[0]
		if response.find('Monitor') == -1:
			try:
				os.system('ifconfig %s down' % self.interface)
				os.system('iwconfig %s mode monitor' % self.interface)
				os.system('ifconfig %s up' % self.interface)
			except:
				print "[ERROR] Could not setting monitor mode"
				exit(-1)

	def set_interface(self, interface):
		self.interface = interface
		self.get_macaddr(self.interface)

	def get_macaddr(self, interface):
		# http://stackoverflow.com/questions/159137/getting-mac-address #
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', interface[:15]))
		self.mac = ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

	def change_channel(self, channel=-1):
		# change channel one by one (max 13)
		if channel == -1:
			self.channel = (self.channel % self.MAX_CHANNEL) + 1
		else:
			self.channel = channel
		os.system('iwconfig %s channel %d' % (self.interface, self.channel))

if __name__ == "__main__":
	wifisniffer = WifiSniffer()
	wifisniffer.APscan_start()
	time.sleep(3)
	wifisniffer.APscan_stop()
