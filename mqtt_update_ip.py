import socket
import paho.mqtt.client as paho
import signal
import time
import os
import sys
from datetime import datetime as dt

# Set LEDs and sigint handler
# import mraa
# leds = []
# for i in range(2,10):
#   led = mraa.Gpio(i)
#   led.dir(mraa.DIR_OUT)
#   leds.append(led)
#   time.sleep(0.05)
#   led.write(1)
def control_c_handler(signum, frame):
#     for led in leds:
#         led.write(1)
    sys.exit()
    print('saw control-c')
    mqtt_client.disconnect()
    mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
    print "Now I am done."
    sys.exit(0)
signal.signal(signal.SIGINT, control_c_handler)

# Set MQTT stuff
MY_NAME = 'Sam'
broker = 'iot.eclipse.org'
topicname = "cis650prs"
# Public brokers: https://github.com/mqtt/mqtt.github.io/wiki/public_brokers

# Get your IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_addr = str(s.getsockname()[0])
print('IP address: {}'.format(ip_addr))
s.close()

def on_connect(client, userdata, flags, rc):
	print('connected')

# The callback for when a PUBLISH message is received from the server that matches any of your topics.
# However, see note below about message_callback_add.
def on_message(client, userdata, msg):
	print(client)
	print(userdata)
	print(msg.topic)
	print(msg.payload)

# You can also add specific callbacks that match specific topics.
# See message_callback_add at https://pypi.python.org/pypi/paho-mqtt#callbacks.
# When you have add ins, then the on_message handler just deals with topics
# you have *not* written an add in for. You can just use the single on_message
# handler for this problem.

def on_disconnect(client, userdata, rc):
	print("Disconnected in a normal way")
	#graceful so won't send will

def on_log(client, userdata, level, buf):
	pass
	# print("log: {}".format(buf)) # only semi-useful IMHO

# Instantiate the MQTT client
mqtt_client = paho.Client()

# set up handlers
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_log = on_log

mqtt_topic = topicname + '/' + socket.gethostname()  # don't change this or you will screw it up for others

# See https://pypi.python.org/pypi/paho-mqtt#option-functions.
mqtt_client.will_set(mqtt_topic, '______________Will of '+MY_NAME+' _________________\n\n', 0, False)

mqtt_client.connect(broker, '1883')

# You can subscribe to more than one topic: https://pypi.python.org/pypi/paho-mqtt#subscribe-unsubscribe.
# If you do list more than one topic, consdier using message_callback_add for each topic as described above.
# For below, wild-card should do it.
mqtt_client.subscribe(topicname + "/#") #subscribe to all students in class

mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive

while True:
    timestamp = dt.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
    mqtt_message = "[%s] %s " % (timestamp,ip_addr) + '==== '+MY_NAME
    mqtt_client.publish(mqtt_topic, mqtt_message)  # by doing this publish, we should keep client alive
    time.sleep(5)

# I have the loop_stop() in the control_c_handler above. A bit kludgey.
