import sys,os,time
from termios import *

cmd_open="zb\x01"
cmd_close="zb\x02"
cmd_set_channel="zb\x04"
cmd_ed="zb\x05"
cmd_cca="zb\x06"
cmd_set_state="zb\x07"
data_xmit_block="zb\x09"
resp_recv_block="zb\x0b"

IDLE_MODE = 0
RX_MODE = 2
TX_MODE = 3

class DQ:
	def __init__(self, port):
		try:
			print "Openning " + port
			self.file = os.open(port, os.O_RDWR|os.O_NOCTTY)
		except IOError:
			print "IOError in open"
			sys.exit(2)

		try:
			self.oldattrs = tcgetattr(self.file)
			attrs = [IGNPAR, self.oldattrs[1], 0, self.oldattrs[3], B115200, B115200, self.oldattrs[6]]
			attrs[2] = B115200 | CS8 | CLOCAL | CREAD
			attrs[6][VTIME] = 0
			attrs[6][VMIN] = 1
			tcflush(self.file, TCIFLUSH)
			tcsetattr(self.file, TCSANOW, attrs)
		except IOError:
			print "IOError in termios"
			sys.exit(2)
	def parse_status(self):
		if self.status == 0:
			self.strstatus = "SUCCESS"
		elif self.status == 1:
			self.strstatus = "RX_ON"
		elif self.status == 2:
			self.strstatus = "TX_ON"
		elif self.status == 3:
			self.strstatus = "TRX_OFF"
		elif self.status == 4:
			self.strstatus = "IDLE"
		elif self.status == 5:
			self.strstatus = "BUSY"
		elif self.status == 6:
			self.strstatus = "BUSY_RX"
		elif self.status == 7:
			self.strstatus = "BUSY_TX"
		elif self.status == 8:
			self.strstatus = "ERR"


	def write(self, string):
		print "Writing "+string
		os.write(self.file, string)

	def read(self, num):
		v =  os.read(self.file, num)
		if (num == 1) :
			print "Reading %s %02x" %(v, ord(v))
		else :
			print "Got %s" %v
		return v

	def response(self):
		state = 1
		while 1:
			val = self.read(1)
			print val
			if state == 1:
				if val == 'z':
					state = 2
				elif val == '\000':
					state = 1
				else:
					print "Bad character: %s %02x" % (val, ord(val))
			elif state == 2:
				if val == 'b':
					state = 3
				elif val == '\000':
					state = 1
				else:
					print "Bad character: %s %02x" % (val, ord(val))
			elif state == 3:
				id = ord(val)
				if id == 0x85:
					self.status = ord(self.read(1))
					self.data = self.read(1)
				elif id == 0x8b:
					self.status = 0
					self.lqi = ord(self.read(1))
					len = ord(self.read(1))
					self.data = self.read(len)
				else:
					self.status = ord(self.read(1))
					self.data = None
				self.parse_status()
				print self.strstatus
				return id

	def send_cmd(self, cmd):
		self.write(cmd)
		while 1:
			v = self.response()
			if (v != ord(cmd[2]) | 0x80) :
				print "Returned invalid id value %x" % (v)
			else:
				break
		return self.status

	def open(self):
		return self.send_cmd(cmd_open)

	def close(self):
		return self.send_cmd(cmd_close)

	def ed(self):
		return self.send_cmd(cmd_ed)

	def cca(self):
		return self.send_cmd(cmd_cca)

	def set_channel(self, channel):
		return self.send_cmd(cmd_set_channel + chr(channel))

	def set_state(self, mode):
		return self.send_cmd(cmd_set_state+chr(mode))

	def send_block(self, data):
		return self.send_cmd(data_xmit_block+chr(len(data))+data)

