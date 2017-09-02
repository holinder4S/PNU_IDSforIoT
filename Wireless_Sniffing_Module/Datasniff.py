import hashlib
import hmac
import logging
import os
import struct
from binascii import a2b_hex, a2b_qp
from threading import Thread

from Crypto.Cipher import ARC4, AES
from pbkdf2 import PBKDF2
from scapy.all import *

logging.getLogger('scapy.runtime').setLevel(logging.ERRPR)

class DataSniffer:
	TUNSETIFF = 0x400454ca
	IFF_TAP = 0x0002
	IFF_NO_PI = 0x1000

	def __init__(self, wlan):
		self.wlan = wlan
		self.data_sniffing_thread = None
		self.sniff_fd = None
		self.deauth_list = []

	def start(self):
		## sniff parameter value check(target info)
		param_status = self.__param_check()
		if param_status != None:
			return param_status

		if not self.data_sniffing_thread:
			## change channel for sniffing AP & station's channel
			print "[+] Channel Setting : %s" % self.channel
			self.wlan.change_channel(self.channel)
		
			## Activate Tap Interface
			tap_status = self.__set_sniffing_interface()
			if tap_status != None:
				return tap_status
			self.data_sniffing_thread = DataSniffingThread(self)
			self.data_sniffing_thread.start()
	
	def stop(self):
		if self.data_sniffing_thread:
			self.data_sniffing_thread.exit()
			del self.data_sniffing_thread
			self.data_sniffing_thread = None

		if self.sniff_fd:
			os.close(self.sniff_fd)
			self.sniff_fd = None
		self.deauth_list = []
	
	def __param_check(self):
		config_fd = open('config.txt', 'r')
		self.ssid = config_fd.readline()[7:]
		self.bssid = config_fd.readline()[8:]
		self.channel = config_fd.readline()[10:]
		self.enc = config_fd.readline()[6:]
		config_fd.close()
	
		self.key = raw_input("[+] Please Enter selected AP's Password : ")
		deauth_tmp = raw_input("[+] Are you send deauth packet?(y/n) ")
		if deauth_tmp = 'y' or deauth_tmp = 'Y':
			self.deauth = True
			self.sta_mac = raw_input("[+] Please Enter deauth packet's target MAC : ")
		else:
			self.deauth = False
			self.sta_mac = ''

		dump_tmp = raw_input("[+] Are you want Packet dump?(y/n) "
		if dump_tmp = 'y' or dump_tmp = 'Y':
			self.dump = True
		else:
			self.dump = False

		
