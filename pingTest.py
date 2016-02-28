from flask import Flask, render_template
from flask_socketio import SocketIO
import os
import calendar
import time
import threading
import json
import subprocess
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

saveFile="pingData.txt"
exitHandler=False;

def find_between( s, first, last ):
	try:
		start = s.index( first ) + len( first )
		end = s.index( last, start )
		return s[start:end]
	except ValueError:
		return -1

# socketio methods
@socketio.on('connect')
def test_connect():
	f = open(saveFile, 'r')

	# RETURN CURRENT GATHERED DATA
	for line in f:
		socketio.emit('pingData', json.loads(line.strip()))
	#emit('pingData', {'data': 'Connected'})

def testPing():
	hostname = "8.8.8.8"
	return find_between(subprocess.check_output("ping -c 1 " + hostname, shell=True)
		, "time=", " ")

def pingHandler():
	global exitHandler
	f = open(saveFile,"w")
	f.write("")
	f.close()

	while not exitHandler:
		data = {'time': calendar.timegm(time.gmtime()), 'ping': float(testPing())}

		with open(saveFile,"a") as of:
			of.write(json.dumps(data) + "\n")

		socketio.emit('pingData', data)
		time.sleep(20)

@app.route('/')
def main():
	return render_template('main.html')

if __name__ == '__main__':
	if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
		saveFile="pingData-" + time.strftime("%H:%M:%S") + "-" + time.strftime("%Y%m%d") + ".pingData"
		print(saveFile)
		t1 = threading.Thread(target=pingHandler)
		t1.daemon=True # quits thread on main thread exit
		t1.start()

	'''while True:
		try:
			pass
		except (KeyboardInterrupt, SystemExit):
			exitHandler=True
			break'''
	socketio.run(app,host="0.0.0.0",port=80,debug=True)
