#!/usr/bin/python3
# -*- coding: utf-8 -*-
from time import sleep
import RPi.GPIO as GPIO
import OSC
import threading

bounceTime = 500; # milliseconds
toggleTime = 500; # milliseconds

x32_ip = '10.0.0.5'
x32_port = 10023

# kanavat: gpio in, gpio out, OSC
# 99 on ei kytketty
channels = [[21,17,"/ch/01/mix/on"],
	[22,99,"/ch/02/mix/on"],
	[23,18,"/ch/02/mix/on"],
	[24,99,"/ch/02/mix/on"]]

#samassa järjestyksessä äskeisen kanssa, nää on globaalisti muutettavissa oleva
states = ["OFF","OFF","OFF","OFF"]			
pushed = [0,0,0,0]

#yleismallin funktio, lyhyt painallus toggle, pitkä latch
def buttonFunc(gpioNumber):
	global pushed

	#selvitetään mikä kanava kyseessä
	channel = 0
	for index, item in enumerate(channels):
        	if (item[0] == gpioNumber):
        		channel = index

	# varmistetaan ettei sama nappi oo jo pohjassa, eli debounce pohjaanpainetun napin ylösnostolle
	if pushed[channel]:
		return
 
	print('nappi %s pohjaan'%gpioNumber)

	
	#kutsutaan togglea ekan kerran
	toggleOSC (channel)

	#odotetaan toggletime ja jos nappi ei oo pohjassa, ei tehdä muuta
	sleep( toggleTime / 1000.0 )
	if not GPIO.input(gpioNumber):
		return
	
	#muuten odotetaan että nappi nousee, tallennetaan lippu jotta debounce toimii
	pushed[channel] = 1		
	while GPIO.input(gpioNumber):     
        	print('nappi pohjassa, odotetaan')
        	sleep(0.05)
      
	print('nappi %s ylos'%gpioNumber)

	#kutsutaan toggle toisen kerran, nollataan lippu hetken päästä
	toggleOSC (channel)

	sleep( bounceTime / 1000.0 )
	pushed[channel] = 0


#funktio joka kääntää osc-parametrin arvon	
def toggleOSC (channel):

	# halutaan muuttaa tätä
	global states

	oscmsg = OSC.OSCMessage()
	oscmsg.setAddress( channels[channel][2])

	if (states[channel] == "OFF"):		
		oscmsg.append("ON")
		states[channel] = "ON"
		# päivitettään ledi jos sellainen on
		if (channels[channel][1] != 99):
                   GPIO.output(channels[channel][1], 0)
	else:
		oscmsg.append("OFF")
		states[channel] = "OFF"
		if (channels[channel][1] != 99):
                   GPIO.output(channels[channel][1], 1)

	print oscmsg
	x32.send(oscmsg)

def oscInputHandler(addr, tags, data, client_address):
	# halutaan muuttaa tätä
	global states
	
	txt = 'OSCMessage("%s", %s)' % (addr, data)
	print "input:" + txt

	for index, item in enumerate(channels):
            if ( addr == item[2] ):
        	if (data[0] == 1):
        		# ledit on invert, 99 on kytkemätön ledi, eli ei yritetä käyttää
        		if (item[1] != 99):
					GPIO.output(item[1], 0)
			elif (data[0] == 0):
				if (item[1] != 99):
					GPIO.output(item[1], 1)
			states[index] = data


def request_x32_to_send_change_notifications(client):

	# selvitetään kanavien alkutilat, kunhan kuuntelu on valmis
	print "odotetaan serveriä"
	sleep(5)
	print "kysytään tila:"
	for index, item in enumerate(channels):
		client.send(OSC.OSCMessage(item[2]))
		print "kavana " + index + ": " + item[2]

    """request_x32_to_send_change_notifications sends /xremote repeatedly to
    mixing desk to make sure changes are transmitted to our server.
    """
    while True:
        client.send(OSC.OSCMessage("/xremote"))
        sleep(7)



#alustetaan gpio, 99 on kytkemätön pinni jota ei käytetä
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

for index, item in enumerate(channels):
	if (item[0] != 99):
		GPIO.setup(item[0], GPIO.IN)
		GPIO.add_event_detect(item[0], GPIO.RISING, callback=buttonFunc, bouncetime=bounceTime)
	if (item[1] != 99):
		GPIO.setup(item[1], GPIO.OUT)	


# recieve
server = OSC.OSCServer(("", 10023))
server.addMsgHandler("default", oscInputHandler)
print server

# send
x32 = OSC.OSCClient(server=server)
x32.connect((x32_ip,x32_port))
print x32

thread = threading.Thread(target=request_x32_to_send_change_notifications, kwargs = {"client": x32})
thread.daemon=True # to get ctrl+c work
thread.start()



# start recieving messages from mixer
server.serve_forever()


