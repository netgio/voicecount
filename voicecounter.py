from SpeakPython.SpeakPythonRecognizer import SpeakPythonRecognizer;


import sys;

hitcount = 0;
stop = False;

def quit():
	stop = True;
	off("all");
	sys.exit(0);

def count(out_str):
        global hitcount;
	print out_str;
	if not out_str == None:
                hitcount += 1;
		print hitcount;
	else:
		print "Couldn't recognize.";

recog = SpeakPythonRecognizer(count, "iotcounter");
recog.setDebug(3);

#main
try:
	while not stop:
		recog.recognize();
except KeyboardInterrupt:
	stop = True;
	print "Interrupted.";
finally:
	print "Finally!";
