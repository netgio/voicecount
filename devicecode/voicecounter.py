from SpeakPython.SpeakPythonRecognizer import SpeakPythonRecognizer
import websocket


import sys
import logging

logging.basicConfig(filename='voicecount.log',level=logging.DEBUG)

stop = False
ws = None
send = False
exitcode = 0

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
    logging.info('closing websocket')
    send = False
    stop = True
	

def count(out_str):
        global hitcount
	global send
	global stop
	global exitcode
	logging.info('Detected : %s' % out_str)
	if not out_str == None:
                if out_str == 'quit':
			stop = True
			exitcode = 0;
			logging.info('quitting via voice - Exit Code 0')
		elif out_str == 'restart':
			stop = True
			exitcode = 1;
			logging.info('quitting with Exit Code 1')

		if send:
			logging.info('sending word to websocket:' + out_str)
			ws.send('{"word":"%s","count":1}' % out_str)
	else:
		logging.info('word not recognised:' + out_str)

def on_open(ws):
	global stop
	global send
	global exitcode
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
	except : # unexpected exception
		stop = True
		exitcode = 1
	finally:
		logging.info('closing web socket')
		ws.send('Disconnecting Websocket')
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
	logging.info('existing with code ' + str(exitcode))
	exit(exitcode) # this should run for ever

