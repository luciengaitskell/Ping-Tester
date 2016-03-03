from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit
import platform
import os
import calendar
import time
import threading
import json
import subprocess
import eventlet
eventlet.monkey_patch()

print( "\n---------------\nExecuting pintTest.py with __name__ = "+__name__+"\n" )

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet') # instance of the web server

saveFileFolder="pingData/"
saveFile="pingData.txt" # Name gets changed later
exitHandler=False;
requestWait=1
print("requestWait = " + str(requestWait))

if True:
	samplePeriod=60
else:
	samplePeriod=5
print("samplePeriod = " + str(samplePeriod))

def find_between( s, first, last ):
	try:
		start = s.index( first ) + len( first )
		end = s.index( last, start )
		return s[start:end]
	except ValueError:
		return -1

def getFileDataArray(fileName):
	returnJson=[]
	f = open(fileName, 'r')

	# RETURN CURRENT GATHERED DATA
	for line in f:
		returnJson.append(json.loads(line.strip()))

	return returnJson

# socketio methods
@socketio.on('connect')
def test_connect():
	print("User: " + str(request.sid) + " has joined!")
	emit('initialData', {"requestWait": requestWait, "samplePeriod": samplePeriod,"saveFile": saveFile})

	# Comment the print satement out when not debugging as it will slow down the script
	#print("Giving new user: " + str(returnJson))
	emit('initialPingData', getFileDataArray(saveFile))
	#emit('pingData', {'data': 'Connected'})

def testPing():
	hostname = "8.8.8.8"

	try:
		if "darwin" in platform.platform().lower(): # If it is mac
			return find_between( subprocess.check_output("ping -t 1 " + hostname, shell=True)
				, "time=", " ")
		else:
			return find_between( subprocess.check_output("ping -W 1 -c 1 " + hostname, shell=True)
				, "time=", " ")

	except subprocess.CalledProcessError as grepexc:
		return -1

def pingHandler():
	global exitHandler

	f = open(saveFile,"w")
	f.write("")
	f.close()

	while not exitHandler:
		readings=[]
		startTime=time.time()
		maxPing=0.0

		while time.time()-startTime<samplePeriod:
			ping = float(testPing())
			readings.append(ping)

			if ping>maxPing:
				maxPing=ping

			time.sleep(requestWait)

		pingAverage=0
		failed=False
		numGoodPings=0
		for ii in readings:
			if ii == -1:
				failed=True
			else:
				numGoodPings += 1
				pingAverage += ii

		if numGoodPings>0:
			pingAverage = pingAverage/numGoodPings
		else:
			pingAverage=-1

		if failed:
			extremeValue=-1
		else:
			extremeValue=maxPing

		returnData={"time": calendar.timegm(time.gmtime()),
			"mean": pingAverage, "extreme": extremeValue}

		with open(saveFile,"a") as of:
			of.write(json.dumps(returnData) + "\n")

		socketio.emit('pingData', returnData)

@app.route('/')
def main():
	return render_template('main.html')

@app.route('/archive/')
def archiveRoot():
	files = []
	for ii in os.listdir(saveFileFolder):
		if ii.startswith("pingData"):
			files.append(ii)
		else:
			print("Archive list is ignoring \"" + ii + "\"")


	return render_template('archive.html', files=files)
	return "Please go to: /archive/fileName"

@app.route('/archive/<fileName>/')
def archive(fileName):
	print("Recieved archive request for: " + fileName)
	fileName = saveFileFolder + fileName
	if fileName == saveFile:
		return redirect("/")
		#return "File is current!"

	if fileName == "README.md":
		return "File doesn't exist!"

	try:
		data=getFileDataArray(fileName)
	except IOError:
		return "File doesn't exist!"
	# in progress - serve file if valid name
	return render_template('archiveDisplay.html', data=data)

if __name__ == '__main__':
	if os.environ.get("WERKZEUG_RUN_MAIN") == "true": # The current thread is the child process
		print("\nChild web server thread started!")
		saveFile=saveFileFolder + "pingData-" + time.strftime("%Y%m%d") + "-" + time.strftime("%H:%M:%S") + ".pingData"
		print("\nLaunch pingHandler with o/p to "+saveFile)
		t1 = threading.Thread(target=pingHandler)
		t1.daemon=True # quits this thread when parent thread exits
		t1.start()

	'''while True:
		try:
			pass
		except (KeyboardInterrupt, SystemExit):
			exitHandler=True
			break'''

	print("\nLaunch web server")
	socketio.run(app,host="0.0.0.0",port=80,debug=True)
	exitHandler=True
	print("pingHandler shutdown\n waiting...")
	time.sleep(0.2)
