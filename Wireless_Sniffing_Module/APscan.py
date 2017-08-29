from threading import Thread
from scapy.all import *

from prettytable import PrettyTable
import logging
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)

class APscanner:
	def __init__(self, wlan):
		self.wlan = wlan
		conf.iface = self.wlan.interface
		self.channel_hopping_thread = None
		self.get_apinfo_thread = None
		self.ap_list = []
		
	def start(self):
		if not (self.channel_hopping_thread and self.get_apinfo_thread):
			self.channel_hopping_thread = channel_hopping_thread(self)
			self.channel_hopping_thread.start()
			self.get_apinfo_thread = get_apinfo_thread(self)
			self.get_apinfo_thread.start()

	def stop(self):
		if self.channel_hopping_thread:
			self.channel_hopping_thread.exit()
			del self.channel_hopping_thread
			self.channel_hopping_thread = None

		if self.get_apinfo_thread:
			self.get_apinfo_thread.exit()
			del self.get_apinfo_thread
			self.get_apinfo_thread = None

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
	
	def __init__(self, APscanner):
		Thread.__init__(self)
		self.APscanner = APscanner
		self.__exit = False

	def run(self):
		while True:
			time.sleep(self.INTERVAL)
			self.APscanner.print_apinfo()

			if self.__exit:
				break
	
	def exit(self):
		self.__exit = True

class get_apinfo_thread(Thread):
	
	def __init__(self, APscanner):
		Thread.__init__(self)
		self.APscanner = APscanner
		self.__exit = False

	def run(self):
		sniff(iface=self.APscanner.wlan.interface, prn=self.apinfo_sniff, stop_filter=self.apinfo_stop)

	def apinfo_sniff(self, pkt):
		if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
			p = pkt[Dot11Elt]
			cap = pkt.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}"
					  "{Dot11ProbeResp:%Dot11ProbeResp.cap%}").split('+')
			crypto = []
			while isinstance(p, Dot11Elt):
				if p.ID == 0:
					ssid = p.info
				elif p.ID == 3:
					try:
						channel = ord(p.info)
					except:
						return
				elif p.ID == 48:
					crypto.append('WPA2')
				elif p.ID == 221 and p.info.startswith('\x00P\xf2\x01\x01\x00'):
					crypto.append('WPA')
				p = p.payload
			if not crypto:
				if 'privacy' in cap:
					crypto.append('WEP')
				else:
					crypto.append('OPEN')
			bssid = pkt.addr3
			crypto.sort()
			crypto = '/'.join(crypto)
			
			if not self.APscanner.is_aplist(ssid, bssid):
				self.APscanner.ap_list.append(AP(ssid, bssid, channel, crypto))

		elif pkt.haslayer(Dot11Qos):
			ap = self.APscanner.is_aplist(pkt.addr1)
			sta_mac = pkt.addr2
			if not ap:
				ap = self.APscanner.is_aplist(pkt.addr2)
				sta_mac = pkt.addr1
				if not ap:
					return
			ap.add_sta(sta_mac)

