#!/bin/env python

# Written-by: Tony Cheneau <tony.cheneau@amnesiak.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""Assigns the PANID, short address and long address on an econotag device.
This script requires a specific firmware, implementing the corresponding commands"""

import sys
from termios import *
from test_DQ import *


RETRY = 0
OK = 1

def set_PANID(panid):
	try:
		panid = int(panid,16)
		print 'Result of set_PANID ' + hex(cn.set_panid(chr((panid>>8)& 0xff) + chr(panid & 0xff)))
	except:
		print "wrong PANID value %s, a correct PAN ID would be : \"777\" (hex)" % panid
		sys.exit(-1)
	return OK

def set_short_address(saddr):
	try:
		saddr = int(saddr,16)
		print 'Result of set_shortaddr ' + hex(cn.set_shortaddr(chr((saddr>>8)& 0xff) + chr(saddr & 0xff)))
	except:
		print "wrong short address, a correct short address would be: \"1\" (hex)"
		sys.exit(-1)
	return OK

def set_long_address(laddr):
	laddr = laddr.replace(":","")
	if len(laddr) != 16:
		print "wrong long address %s, should be in the following format ba:be:ba:be:ba:be:ba:be or babebabebabebabe" % laddr
		sys.exit(-1)
	laddr = "".join([ chr(int(a + b,16)) for (a,b) in  zip(laddr[::2], laddr[1::2]) ])
	try:
		result = cn.set_longaddr(laddr)
		print 'Result of set_long_addr ' + hex(result)
		if result != 0:
			print "Long address was not assigned properly"
			return RETRY
	except:
		print "wrong long address"
	return OK

if __name__ == "__main__":
	
	if len(sys.argv) != 5:
		print "usage: %s device PANID shortaddr longaddr" % sys.argv[0]
		sys.exit(-1)
	
	# prepare connection to the serial device
	cn = DQ(sys.argv[1])
	print 'Result of close ' + hex(cn.close())
	print 'Result of open ' + hex(cn.open())

	set_PANID(sys.argv[2])
	set_short_address(sys.argv[3])

	# long address might not get assigned properly on the first time
	while RETRY == set_long_address(sys.argv[4]):
	    pass # do nothing
	

	# properly disconnect from the serial device
	cn.close()
	sys.exit(2)

