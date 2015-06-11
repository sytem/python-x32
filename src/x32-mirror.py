"""
Proxy for 2 Behringer X32 mirror each other
Modified from https://github.com/tjoracoder/python-x32 by Teppo Rekola, sytem@iki.fi
test version 0.4, 10.6.2015 


This software is licensed under the Modified BSD License:

Copyright (c) 2013, Sigve Tjora
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
	* Redistributions of source code must retain the above copyright
	  notice, this list of conditions and the following disclaimer.
	* Redistributions in binary form must reproduce the above copyright
	  notice, this list of conditions and the following disclaimer in the
	  documentation and/or other materials provided with the distribution.
	* Neither the name of the <organization> nor the
	  names of its contributors may be used to endorse or promote products
	  derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import OSC
import time
import threading
import re
from x32parameters import get_settings # sync:n vaatima lista


def request_x32_to_send_change_notifications(clientA, clientB):
	"""request_x32_to_send_change_notifications sends /xremote repeatedly to
	mixing desk to make sure changes are transmitted to our server.
	"""
	print "xremote thread  start"
	while True:
		clientA.send(OSC.OSCMessage("/xremote"))
		clientB.send(OSC.OSCMessage("/xremote"))
		###print "sent /xremote"
		time.sleep(7)

def mixer_thread(server):
	print "server thread start"
	server.serve_forever()


def print_all_x32_change_messages(x32A_address, x32B_address, server_udp_port):
	
	# A:n muutokset B:lle ja toiseen suuntaan 				   
	def msgFilter_handlerA(addr, tags, data, client_address):
		txt = 'OSCMessage("%s", %s)' % (addr, data)
		print "input from A:" + txt
		clientB.send(OSC.OSCMessage(addr,data))
		
	def msgFilter_handlerB(addr, tags, data, client_address):
		txt = 'OSCMessage("%s", %s)' % (addr, data)
		print "input from B:" + txt
		clientA.send(OSC.OSCMessage(addr,data))
		
								   

	serverA = OSC.OSCServer(("", server_udp_port))
	serverA.addMsgHandler("default", msgFilter_handlerA)
	clientA = OSC.OSCClient(server=serverA) #This makes sure that client and server uses same socket. This has to be this way, as the X32 sends notifications back to same port as the /xremote message came from  
	clientA.connect((x32A_address, 10023))
	
	print "client A olemassa"
	print serverA
	print clientA
	
	serverB = OSC.OSCServer(("", server_udp_port+1)) # +1 jotta ei olla samassa portissa
	serverB.addMsgHandler("default", msgFilter_handlerB)
	clientB = OSC.OSCClient(server=serverB) #This makes sure that client and server uses same socket. This has to be this way, as the X32 sends notifications back to same port as the /xremote message came from  
	clientB.connect((x32B_address, 10023))

	print "client B olemassa"
	print serverB
	print clientB
	
		  
	thread_xremote = threading.Thread(target=request_x32_to_send_change_notifications, kwargs = {"clientA": clientA , "clientB": clientB})
	thread_xremote.daemon=True # to get ctrl+c work
	thread_xremote.start()
	
	thread_A = threading.Thread(target=mixer_thread, kwargs = {"server": serverA })
	thread_A.daemon=True
	thread_A.start()

	thread_B = threading.Thread(target=mixer_thread, kwargs = {"server": serverB })
	thread_B.daemon=True
	thread_B.start()  
	
	while True:
		print "\n input \"A\" to do full sync from "  + x32A_address + " to " + x32B_address + " and \"B\" to another way \n"
		print " ctrl+c to stop\n"
		choice = raw_input("> ")

		if choice == 'A' :
			print "running sync A to B"
			
			# ajetaan sync
			for setting in settings:
				print setting
				clientA.send(OSC.OSCMessage(setting))
		
		elif choice == 'B' : 
			print "running sync B to A"
			
			# ajetaan sync
			for setting in settings:
				print setting
				clientB.send(OSC.OSCMessage(setting))

	
	
if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description="Link 2 X32 together")
	parser.add_argument('--addressA', required = True,						
						help='name/ip-address of Behringer X32 mixing desk')
	parser.add_argument('--addressB', required = True,						
						help='name/ip-address of second Behringer X32 mixing desk')
	parser.add_argument('--port', default = 10300,						
						help='UDP-port to open on this machine, also next port')

	args = parser.parse_args()
	
	
	# generoidaan lista sync:ssa tarvittavista parametreista
	settings = get_settings()
    
	print_all_x32_change_messages(x32A_address = args.addressA, x32B_address = args.addressB, server_udp_port = args.port)
	