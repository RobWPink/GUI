from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import decode_ieee
import datetime,subprocess,re,time,datetime,ctypes,os,sys,optparse,socket

parser = optparse.OptionParser()

parser.add_option('-I','--ip',action="store",type="string",dest='ip',help ='Set device IP (Default: "127.0.0.1")',default='127.0.0.1')
parser.add_option('-p','--port',action="store",type="string",dest='port',help ='Set device port (Default: 520)',default='520')
parser.add_option('-v','--verbose',action="store_true",dest='verb',help ='Print out all values')
parser.add_option('-g','--gui',action="store_true",dest='gui',help ='Choose NOT to start GUI')

(options, args) = parser.parse_args()

if not options.gui:
	htop = subprocess.Popen(["/usr/bin/python3", "/home/pi/E100/E100GUI.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def main():
	global htop
	try:
		temp = ctypes.c_uint32(0).value
		cnt = 0
		errorMsg = ""
		tmout = False
		socketError = True
		mb = ModbusClient(host=options.ip, port=int(options.port), unit_id=21, timeout=5,auto_open=True)
		data = []
		while True:
			try:
				data = mb.read_holding_registers(0, 100)
				if not mb.is_open:
					if not socketError:
						if not tmout:
							tmout = True
							continue
						else:
							tmout = False
							raise RuntimeError("device Read Failure")
				else:
					if not len(data) >= 100:
						errorMsg = "0"
					if options.verb:
						print(data)
					errorMsg = ""
					socketError = False
			except socket.gaierror:
				errorMsg = "2Port ("+options.port+"): Connection Failure" #\n[error msg: "+str(mb.last_error_as_txt)+"]"
				socketError = True
			except KeyboardInterrupt:
				if not options.gui:
					htop.terminate()
					mb.close()
				sys.exit()
			if data:
				temp = data[83] << 16
				temp |= data[84]
				data[83] = decode_ieee(temp)
				data[84] = 0
				temp = 0
				temp = data[85] << 16
				temp |= data[86]
				data[85] = decode_ieee(temp)
				data[86] = 0
				temp = 0
				temp = data[87] << 16
				temp |= data[88]
				data[87] = decode_ieee(temp)
				data[88] = 0
				with open('data.txt', 'w') as fd:
						fd.write(errorMsg+"\n")
						fd.close()
				with open('data.txt', 'a') as fd:
					fd.write(','.join(map(str, data))+"\n")
			if not options.gui:
				if htop.poll() != None:
					print("GUI quit")
					mb.close()
					sys.exit(1)
			continue
	except KeyboardInterrupt:
		if not options.gui:
			htop.terminate()
			mb.close()
		sys.exit()
	except Exception as e:
		mb.close()
		if not options.gui:
			htop.terminate()
		sys.exit(1)

if __name__ == '__main__':
	main()
