# Voice Counter
This project uses SpeakPython (https://bitbucket.org/matthew3/speakpython) updated to support keyword based
searches in the latest version of CMU PocketSphinx, SphinxBase and GStreamer 1.0. along with a simple python program to 
count occurrences of a set of words/phrases in free form speech.   This differs from the original SpeakPython use case
which is to support detection and interpretation of structured commands in a predefined grammar.  

The components of the project are:
1) the SpeakPython library with
    - modifications to one file to support changes in GStreamer API, which in turn supports the latest version of PocketSphinx
    - this code and the modifications to it are GPL v3 licensed.
2) a grammar (.gram) file defining the set of words/phrases to detect and their thresholds
3) a SPS file to define how the phrases are matched to return values [this is the input the the MakeSpeechProject.py script which generates
the runtime DB, grammar and dictionary files (run once after modifying the SPS file)
4) the python program that uses this library to detect words and emit them as websocket messages.
5) the node.js websocket/web server to connect to - note that this is configured in the root of the repo to support continuous delivery to Azure Web Apps

All remaining code is MIT licensed.


