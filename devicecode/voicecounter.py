from SpeakPython.SpeakPythonRecognizer import SpeakPythonRecognizer;
import websocket;


import sys;

hitcount = 0;
stop = False;
ws = None;
send = False;

def on_message(ws, message):
    print message;

def on_error(ws, error):
    global send;
    send = False;
    print error;

def on_close(ws):
    global send;
    global stop
    print "### WS closed ###";
    send = False;
    stop = True;
	

def count(out_str):
        global hitcount;
	global send;
	print "Detected : %s" % out_str;
	if not out_str == None:
                hitcount += 1;
		if send:
			ws.send('{"word":"%s","count":1}' % out_str);
	else:
		print "Couldn't recognize.";

def on_open(ws):
	global stop;
	global send;
	send = True;
	try:
		print "### WS Open ###";
		send = True;
		while not stop:
			recog.recognize();
	except KeyboardInterrupt:
		print "Interrupted.";
	finally:
		ws.close()
		print "Finally!";


if __name__ == "__main__":
	#main
	print "### Starting Main ###";

	recog = SpeakPythonRecognizer(count, "iotcounter");
	recog.setDebug(5);
	print "### Recognizer created ###";


	##websocket.enableTrace(True);
	ws = websocket.WebSocketApp("ws://localhost:3000",
                         	 on_message = on_message,
                               	 on_error = on_error,
                               	 on_close = on_close);
	print "### Socket Client Created ###";
    	ws.on_open = on_open;
	ws.run_forever();

	

