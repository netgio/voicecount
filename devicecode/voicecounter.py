from SpeakPython.SpeakPythonRecognizer import SpeakPythonRecognizer
import websocket


import sys
import logging

logging.basicConfig(filename='voicecount.log',level=logging.DEBUG)

stop = False
ws = None
send = False

def on_message(ws, message):
    logging.debug('received websocket message:' + message)
    print message

def on_error(ws, error):
    global send
    send = False
    logging.error('received websocket error:' + str(error))
    print error

def on_close(ws):
    global send
    global stop
    print "### WS closed ###"
    logging.error('closing websocket')
    send = False
    stop = True
	

def count(out_str):
        global hitcount
	global send
	global stop
	logging.info('Detected : %s' % out_str)
	if not out_str == None:
                if out_str == 'quit':
			stop = True
			logging.info('quitting via voice')
		if send:
			logging.info('sending word to websocket:' + out_str)
			ws.send('{"word":"%s","count":1}' % out_str)
	else:
		logging.info('word not recognised:' + out_str)

def on_open(ws):
	global stop
	global send
	send = True
	try:
		logging.info('websocket opened')
		ws.send('socket started')
		send = True
		while not stop:
			logging.info('listening')
			ws.send('device is listening')
			recog.recognize()
	except KeyboardInterrupt:
		stop = True
		logging.info('Interrupted via keyboard.')
	finally:
		logging.info('closing web socket')
		##ws.send('websocket closing')
		ws.close()
		print 'Finally!'


if __name__ == '__main__':
	#main
	logging.info('### Starting Main ###')

	recog = SpeakPythonRecognizer(count, 'iotcounter')
	recog.setDebug(5)
	logging.info('### Recognizer created ###')

	##websocket.enableTrace(True)
	ws = websocket.WebSocketApp('ws://voicecount.azurewebsites.net',
                         	 on_message = on_message,
                               	 on_error = on_error,
                               	 on_close = on_close)
	logging.info('### Socket Client Created ###')
    	ws.on_open = on_open
	while not stop:
		ws.run_forever(ping_interval=30, ping_timeout=10)
	

