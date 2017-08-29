import fcntl
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
		self.APscanner = APscanner.APscanner(self.wlan)
		#self.DecSniffer = DecSniffer.DecSniffer(self.wlan)
		self.is_apscan = False
		self.is_decsniff = False

	def APscan_start(self):
		if self.__thread_check():
			return
		iface_list = self.get_wlan_iface_list()
		iface_table = PrettyTable(['Index','Wlan Interface'])
		for i in xrange(len(iface_list)):
			iface_table.add_row(str(i), iface_list[i])
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
		interface_list = p[]
		try:
			interface_list = map(lambda x: x[:-4].strip(' '), re.findall('([^\s].*IEEE)', response))
		except:
			interface_list = []
		
		return interface_list
		
