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

		if ((self.enc.find("WPA2") != -1) or (self.enc.find("WPA") != -1)) and (self.ssid == ''):
			return "[ERROR] WPA/WPA2 encryption need SSID"
		if (self.enc.find("OPEN") == -1) and (self.key == ''):
			return "[ERROR] WEP/WPA/WPA2 encryption need key"
		if (self.enc.find("WEP") != -1):
			if len(self.key) not in [5,13]:
				return "[ERROR] WEP key only has 5 or 13 length key"
		elif (self.bssid.count('-') != 5) and (self.bssid.count(':') != 5):
			return "[ERROR] Invalid BSSID"
		elif (self.sta_mac != '') and ((self.sta_mac.count('-') != 5) or (self.sta_mac.count(':') != 5)):
			return "[ERROR] Invalid STA MAC"

		print "######################"
		print "## AP info to sniff ##"
		print "######################"
		print "[*] AP's SSID : %s" % self.ssid
		print "[*] AP's BSSID : %s" % self.bssid
		print "[*] AP's CHANNEL : %s" % self.channel
		print "[*] AP's ENC : %s" % self.enc
		if self.key != '':
			print "[*] AP's KEY : %s" % self.key
		if self.sta_mac != '':
			print "[*] Target Station's MAC : %s" % self.sta_mac
		if self.deauth:
			if (self.enc.find("OPEN") != -1) or (self.enc.find("WEP") != -1):
				self.deauth = False
			else:
				print "[*] Send Deauthentication Packet~!"
				conf.iface = self.wlan.interface
		if self.dump:
			if not os.path.exists('./dump')
				os.mkdir('./dump')
			dump_path = time.strftime('./dump/%m-%d(%H:%M:%S).pcap', time.localtime())
			print "[*] Packet dump : %s" % dump_path
			self.packet_dump = PcapWriter(dump_path, append=True, sync=True)
	
	def __set_sniffing_interface(self):
		try:
			self.sniff_fd = os.open('/dv/net/tun', os.O_RDWR)
			ifs = ioctl(self.sniff_fd, self.TUNSETIFF, struct.pack('16sH', 'PNUDSniface', self.IFF_TAP | self.IFF_NO_PI))
			ifname = ifs[:16].strip("\x00")
			os.system('ifconfig %s up' % ifname)
			print "[+] '%s' is activated~!" % ifname)
		except IOError:
			return "[ERROR] Interface is busy now~!!!"
		ipv6_disable_path = '/proc/sys/net/ipv6/conf/%s/' % ifname
		if os.path.exists(ipv6_disable_path):
			os.system('echo 1 > %s/disable_ipv6' % ipv6_disable_path)
		returna


class DataSniffingThread(Thread):
	def __init__(self, data_sniffer):
		Thread.__init__(self)
		self.__exit = False
		self.data_sniffer = data_sniffer
		self.packetdecrypter = PacketDecrypter()
		self.session_list = []
		self.ap_mac = self.data_sniffer.bssid

	def run(self):
		sniff(iface=self.data_sniffer.wlan.interface, prn=self.data_sniff, stop_filter=self.data_stop)

	def data_sniff(self, pkt):
		if pkt.haslayer(Dot11QoS):
			if self.data_sniffer.sta_mac in [pkt.addr1, pkt.addr2, pkt.addr3] or self.data_sniffer.sta_mac == '':
				if self.ap_mac = in [pkt.addr1, pkt.addr2, pkt.addr3]:
					sta_mac = pkt.addr2 if pkt.addr1 == self.ap_mac else pkt.addr1
					## WPA/WPA2 Encryption Case
					if pkt.haslayer(EAPOL):
						print "[+] to do implement"
					## OPEN/WEP Case
					else:
						## OPEN
						if self.data_sniffer.enc.find("OPEN") != -1:
							de_pkt = pkt
						else:
							if not pkt.haslayer(Dot11WEP):
								return
							## WEP
							wep_pkt = pkt.getlayer(Dot11WEP)
							if self.data_sniffer.enc.find("WEP") != -1:
								de_pkt = self.packetdecrypter.decryptWEP(wep_pkt, self.data_sniffer.key)
							else:
								print "[+] to do implement"
						## packet send & dump
						if de_pkt.haslayer(SNAP):
							snap_data = de_pkt.getlayer(SNAP)
							send_pkt = self.__make_ether(pkt, snap_data.code) / snap_data.payaload
							self.data_sniffer.send_packet(send_pkt)
							if self.sniffer.dump:
								self.data_sniffer.pktdump.write(send_pkt)

	def data_stop(self, pkt):
		if self.__exit:
			return True

	def exit(self):
		self.__exit = True

	def __make_ether(self, pkt, code):
		to_ds = 1 if pkt.FCfield & 0x1 else 0
		from_ds = 1 if pkt.FCfield & 0x2 else 0
		
		## DA, SA, BSSID
		if (to_ds == 0) and (from_ds == 0):
			return Ether(src=pkt.addr2, dst=pkt.addr1, type=code)
		## BSSID, SA, DA
		elif (to_ds == 1) and (from_ds == 0):
			return Ether(src=pkt.addr2, dst=pkt.addr3, type=code)
		## DA, BSSID, SA
		elif (to_ds == 0) and (from_ds == 1):
			return Ether(src=pkt.addr3, dst=pkt.addr1, type=code)
		## RA, TA, DA, SA
		elif (to_ds == 1) and (from_ds == 1):
			return Ether(src=pkt.addr4, dst=pkt.addr3, type=code)

class PacketDecrypter:
	def decryptWEP(self, wep_pkt, passphrase):
		iv = wep_pkt.iv
		enc_data = wep_pkt.wepdata
		rc4 = ARC4.new(iv + passphrase)
		dec_data = rc4.decrypt(enc_data)
		return LLC(dec_data)
