from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import test_bit
import datetime,subprocess,re,time,datetime,ctypes,os,sys,optparse,socket

parser = optparse.OptionParser()

parser.add_option('-I','--ip',action="store",type="string",dest='ip',help ='Set device IP (Default: "127.0.0.1")',default='127.0.0.1')
parser.add_option('-p','--port',action="store",type="string",dest='port',help ='Set device port (Default: 520)',default='520')
parser.add_option('-d','--id',action="store",type="string",dest='idList',help ='Specify list of Compressor ID\'s (Default:"1,2,3,4")',default='1,2,3,4')
parser.add_option('-v','--verbose',action="store_true",dest='verb',help ='Print out all values')
parser.add_option('-g','--gui',action="store_true",dest='gui',help ='Choose NOT to start GUI')

(options, args) = parser.parse_args()

compressorIDs = options.idList.split(",")

for i in range(len(compressorIDs)):
	compressorIDs[i] = int(compressorIDs[i])

if not options.gui:
	htop = subprocess.Popen(["/usr/bin/python3", "/home/pi/C200/C200GUI.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

#[addr,data,prevData,labelVar,bit#,side]
compressor=[0]*100
compressors = [compressor]*len(compressorIDs)

def main():
	global htop
	try:
		mb = []
		cnt = 0
		errorMsg = ""
		tmout = False
		socketError = True
		activeCompressors = [True]*len(compressors)
		for i in compressorIDs:
			mb.append(ModbusClient(host=options.ip, port=int(options.port), unit_id=i, timeout=5,auto_open=True))
		while True:
			try:
				data = mb[cnt].read_holding_registers(0, 100)
				if not mb[cnt].is_open:
					if not socketError:
						if not tmout:
							tmout = True
							continue
						else:
							tmout = False
							raise RuntimeError("Compressor Read Failure")
				else:
					if not len(data) >= 100:
						errorMsg = "0"
					if options.verb:
						print(data)
					errorMsg = ""
					activeCompressors[cnt] = True
					socketError = False
					compressors[cnt] = data
			except socket.gaierror:
				errorMsg = "2Port ("+options.port+"): Connection Failure" #\n[error msg: "+str(mb[cnt].last_error_as_txt)+"]"
				socketError = True
			except RuntimeError:
				activeCompressors[cnt] = False
				lst = ""
				for i in range(len(compressors)):
					if activeCompressors[i]:
						lst = lst + str(i) + ","
				if lst:
					if lst[-1] == ",":
						lst = lst[:-1]
					errorMsg = "1Compressor #(s)"+lst+" connection timed out"
			except KeyboardInterrupt:
				if not options.gui:
					htop.terminate()
				for i in len(mb):
					mb[i].close()
				sys.exit()
			if all(v == 0 for v in activeCompressors):
				errorMsg = "2No Compressors connected"
			
			with open('data.txt', 'w') as fd:
					fd.write(errorMsg+"\n")
					fd.close()
			with open('data.txt', 'a') as fd:
				for comp in compressors:
					fd.write(','.join(map(str, comp))+"\n")
			if not options.gui:
				if htop.poll() != None:
					print("GUI quit")
					for i in len(mb):
						mb[i].close()
					sys.exit(1)
			if cnt >= (len(compressors)-1):
				cnt = 0
			else:
				cnt = cnt + 1
			continue
	except KeyboardInterrupt:
		if not options.gui:
			htop.terminate()
		for i in len(mb):
			mb[i].close()
		sys.exit()
	except Exception as e:
		for i in len(mb):
			mb[i].close()
		if not options.gui:
			htop.terminate()
		sys.exit(1)

if __name__ == '__main__':
	main()
