from threading import Thread
from scapy.all import *

from prettytable import PrettyTable
import logging
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)

class SSIDscanner:
	def __init__(self, wlan):
		self.wlan = wlan
		conf.iface = self.wlan.interface
		self.channel_hopping_thread = None
		self.ssid_sniffing_thread = None
		self.ap_list = []
		
	def start(self):
		if not (self.channel_hopping_thread and self.ssid_sniffing_thread):
			self.channel_hopping_thread = channel_hopping_thread(self)
			self.channel_hopping_thread.start()
			self.ssid_sniffing_thread = ssid_sniffing_thread(self)
			self.ssid_sniffing_thread.start()

	def stop(self):
		if self.channel_hopping_thread:
			self.channel_hopping_thread.exit()
			del self.channel_hopping_thread
			self.channel_hopping_thread = None

		if self.ssid_sniffing_thread:
			self.ssid_sniffing_thread.exit()
			del self.ssid_sniffing_thread
			self.ssid_sniffing_thread = None

		self.ap_list = []

	def print_apinfo(self):
		print "[+] Channel : %s" % self.wlan.channel
		
		print "######################## AP info ###########################"
		apinfo_table = PrettyTable(['SSID', 'STA_LIST', 'CHANNEL', 'ENC', 'DATA_COUNT','BSSID']
		for i in xrange(len(ap_list)):
			apinfo_table.add_row([ap[i].ssid, str(len(ap[i].sta_list)), ap[i].channel, ap[i].enc, str(ap[i].data_count), ap[i].bssid)

			for j in xrange(len(ap[i].sta_list)):
				apinfo_table.add_row('sta%d'%j, '-', '-', '-', str(ap[i].sta_list[j].data_count), ap[i].sta_list[j].sta_mac)
		
		self.wlan.channel_hopping()	## Channel hopping one by one in wlan class


class channel_hopping_thread(Thread):
	INTERVAL = 0.5
	
	def __init__(self, SSIDscanner):
		Thread.__init__(self)
		self.SSIDscanner = SSIDscanner
		self.__exit = False

	def run(self):
		while True:
			time.sleep(self.INTERVAL)
			self.SSIDscanner.print_apinfo()

			if self.__exit:
				break
	
	def exit(self):
		self.__exit = True

