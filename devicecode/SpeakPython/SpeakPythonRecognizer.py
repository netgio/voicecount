#SpeakPython allows developers to add speech recognition support to their Python applications
#Copyright (C) 2015  Eric Matthews

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by 
#the Free Software Foundation, either version 3 of the License, or 
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of 
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#import pygst;
import gi;
#import gobject;

gi.require_version("Gst", "1.0");
from gi.repository import GObject, Gst;
GObject.threads_init();
Gst.init(None);

#import Gst;
import os.path;
import sys;

from SpeakPython import SpeakPython;

class SpeakPythonRecognizer:

	main_loop = None;

	bus = None;
	pipeline = None;
	asr = None;

	appName = "";
	recogPath = "";

	callback = None;

	DEBUG_VAL = 3;

	#partial result from recog thread
	def asr_partial_result(self, asr, text, uttid):
		struct = Gst.Structure("partial_result");
		struct.set_value("hyp", text);
		struct.set_value("uttid", uttid);
		self.debugMsg("asr partial: " + text, 0);
		asr.post_message(Gst.message_new_application(asr, struct));

	#result from speech recog thread
	def asr_result(self, asr, text, uttid):
		struct = Gst.Structure("result");
		struct.set_value("hyp", text);
		struct.set_value("uttid", uttid);
		self.debugMsg("asr result: " + text, 0);
		asr.post_message(Gst.message_new_application(asr, struct));

	#partial definitive result
	def partial_result(self, hyp):
		self.debugMsg("partial speech result: " + hyp, 2);
		##We will process on partial matches because we are doing
		## keyword matching and we want to process each match - not the whole string at the end. 
		self.matchSpeechToResult(hyp);
		self.quit();


	#final definitive result
	def final_result(self, hyp, confidence):
		#put result into regex-testing module to get result of uttered speech	
		self.debugMsg("final speech result: " + hyp, 2);
		##self.matchSpeechToResult(hyp);
		self.quit();

	def app_msg(self, bus, msg):
##		msgType = msg.structure.get_name();
##		if msgType == 'partial_result':
##			self.partial_result(msg.structure['hyp'], msg.structure['uttid']);
##		elif msgType == 'result':
##			self.result(msg.structure['hyp'], msg.structure['uttid']);
##			self.pipeline.set_state(Gst.State.PAUSED);

                """Receive element messages from the bus."""
                msgtype = msg.get_structure().get_name()
                if msgtype != 'pocketsphinx':
                    return
                if msg.get_structure().get_value('final'):
                    self.final_result(msg.get_structure().get_value('hypothesis'), msg.get_structure().get_value('confidence'))
                    self.pipeline.set_state(Gst.State.PAUSED)
                    #self.button.set_active(False)
                elif msg.get_structure().get_value('hypothesis'):
                    self.partial_result(msg.get_structure().get_value('hypothesis'))

	#create SpeakPython object for conversion of text to results
	def matchSpeechToResult(self, text):
		#create SpeakPython matcher
		sp = SpeakPython(self.recogPath + self.appName + ".db", self.DEBUG_VAL);
		#get the result of the match
		r = sp.matchResult(text);

		#as long as we have a result, pass it back to developer's application using the callback
		if r != None:
			self.callback(r.getResult());
		else:
			self.debugMsg("Tried to match text using SpeakPython.py '" + text + "', but no result.", 2);

	#print a self.debug statement depending on severity	
	def debugMsg(self, msg, severity):
		if (self.DEBUG_VAL <= severity):
			print msg;

	#test for fsg file existence, and let user know how to create it if it doesn't exist
	#returns 0 if fails
	def test_fsg(self, fsgPath):

		#if the fsg doesn't exist, try creating it from jsgf
		if not os.path.isfile(fsgPath):
			self.debugMsg("Could not find the file " + fsgPath + ".fsg. Maybe try running 'python MakeRecog.py <app_name>' to generate necessary language files.\nFor example, for speech commands app, we would run: 'python MakeRecog.py commands'.", 3);
			
			#try to create the fsg file from the jsgf
			self.debugMsg("Attempting to create FSG from JSGF using sphinx tools on the command line...", 3);

			#run grammar conversion using sphinx tools
			jsgfPath = fsgPath[-3] + "jsgf";
			cmd = "sphinx_jsgf2fsg -jsgf " + jsgfPath + " -fsg " + fsgPath;
			iret = os.system(cmd);
		
			#conversion checks	
			if iret != 0:
				self.debugMsg("Creation of fsg by running '" + cmd + "' failed", 3);
				raise Exception("Failed to run " + cmd + " (ensure sphinx tools and sphinxbase is installed): " + iret);
			else:
				self.debugMsg("Successfully created fsg file!", 2);

			#if we reach here and jsgf doesn't exist, let the user know what to do
			if not os.path.isfile(jsgfPath):
				self.debugMsg("jsgf file still does not exist, try running 'python SpeakPythonMakeJSGF.py [app_name] [sps_path(s)]'", 3);
				raise Exception("jsgf file does not exist, even though the creation command succeeeded.");

	def quit(self):
		self.main_loop.quit();

	def recognize(self):
		self.main_loop = GObject.MainLoop();
		self.pipeline.set_state(Gst.State.PLAYING);
		self.main_loop.run();

	def pause(self):
		self.pipeline.set_state(Gst.State.PAUSED);

	def stop(self):
		self.pause();
		self.quit();

	#test for a callback function, and let user know that we need one
	def setCallback(self, newCallback):
		if newCallback == None:
			debugMsg("SpeakPythonRecognition needs a function callback to pass a result to, otherwise we might as well not do speech recognition. This function requires 1 string parameter, which is the result of the recognition.", 2);
			return;

		self.callback = newCallback;

	def setDebug(self, newDebugVal):
		self.DEBUG_VAL = newDebugVal;

	#constructor
	def __init__(self, callback, appName, recogPath='./'):

		#function reference to the callback we will use upon recognition completion
		try:
			self.setCallback(callback);
		except e:
			raise e;

		#init custom app fields
		self.recogPath = recogPath;

		if self.recogPath[len(self.recogPath)-1] != "/":
			self.recogPath += "/"

		self.appName = appName;

		#init speech recog pipeline
		self.pipeline = Gst.parse_launch(' ! '.join(['alsasrc device=hw:1,0',
                                           'queue',
                                           'audioconvert',
                                           'audioresample',
                                           'queue',
                                           #'vader name=vader auto-threshold=true',
                                           'pocketsphinx name=asr',
                                           'fakesink']))

		#get asr out of pipeline to specify functions for sphinx to send data to, as well as add the grammar file to improve recognition
		self.asr = self.pipeline.get_by_name("asr");

		dictFilePath = recogPath + appName + ".dic";

		if not os.path.isfile(dictFilePath):
			print "The dictionary file for your application could not be found, continuing with default pocketsphinx dictionary."
		else:
			self.asr.set_property("dict", dictFilePath);

		#self.asr.connect("partial_result", self.asr_partial_result);
		#self.asr.connect("result", self.asr_result);

##		fsgPath = recogPath + appName + ".fsg";
##
##		#test for .fsg grammar file existence, usually created automatically from MakeRecog.py
##		try:
##			self.test_fsg(fsgPath);
##		except e:
##			raise e;
##
##		#actually set fsg because it exists
##		self.asr.set_property("fsg", fsgPath);

                gramPath = recogPath + appName + ".gram";

                if not os.path.isfile(gramPath):
			print "The dictionary file for your application could not be found, continuing with default pocketsphinx dictionary."
		else:
			self.asr.set_property("kws", gramPath);

		
		#self.asr.set_property("configured", True);

		self.bus = self.pipeline.get_bus();
		self.bus.add_signal_watch();
		self.bus.connect("message::element", self.app_msg);
