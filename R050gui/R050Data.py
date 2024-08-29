from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import test_bit
import sys, time, ctypes,subprocess

htop = subprocess.Popen(["/usr/bin/python3", "/home/pi/R050gui/R050GUI.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

ReformerIDs = [1,2,3,4]

#[deviceAddr	configAddr	group#	errorBits	data	prevData	warning	error]
devices = {
	"TT142":[29,2600,1,0,0,0,0,0],"TT301":[30,2610,1,1,0,0,0,0],"TT303":[31,2620,1,2,0,0,0,0],\
	"TT306":[32,2630,1,3,0,0,0,0],"TT313":[33,2640,1,4,0,0,0,0],"TT319":[34,2650,1,5,0,0,0,0],\
	"TT407":[35,2660,1,6,0,0,0,0],"TT408":[36,2670,1,7,0,0,0,0],"TT410":[37,2680,1,8,0,0,0,0],\
	"TT411":[38,2690,1,9,0,0,0,0],"TT430":[39,2700,1,10,0,0,0,0],"TT511":[40,2710,1,11,0,0,0,0],\
	"TT512":[41,2720,1,12,0,0,0,0],"TT513":[42,2730,1,13,0,0,0,0],"TT514":[43,2740,1,14,0,0,0,0],\
	"TT441":[44,2750,1,15,0,0,0,0],"TT442":[45,2760,1,16,0,0,0,0],"TT443":[46,2770,1,17,0,0,0,0],\
	"TT444":[47,2780,1,18,0,0,0,0],"TT445":[48,2790,1,19,0,0,0,0],"TT446":[129,2800,1,20,0,0,0,0],\
	"TT447":[130,2810,1,21,0,0,0,0],"TT448":[131,2820,1,22,0,0,0,0],"TT449":[132,2830,1,23,0,0,0,0],\
	"TT109":[133,2840,1,24,0,0,0,0],"FT132":[9,2850,2,0,0,0,0,0],"FCV134":[10,2860,2,1,0,0,0,0],\
	"FCV141":[11,2870,2,2,0,0,0,0],"FCV474":[12,2880,2,3,0,0,0,0],"FCV205":[13,2890,2,4,0,0,0,0],\
	"BL508":[14,2900,2,5,0,0,0,0],"PT107":[15,2910,2,6,0,0,0,0],"PT213":[16,2920,2,7,0,0,0,0],\
	"PT318":[17,2930,2,8,0,0,0,0],"PT304":[18,2940,2,9,0,0,0,0],"PT420":[19,2950,2,10,0,0,0,0],\
	"PMP204":[20,2960,2,11,0,0,0,0],\
	
	"TWV308":[None,None,2,24,None,None,0,0],"TWV310":[None,None,2,25,None,None,0,0],\
	"W400":[None,None,2,26,None,None,0,0],"(L)ESTOP":[None,None,2,27,None,None,0,0],\
	"(G)ESTOP)":[None,None,2,28,None,None,0,0],"BURNER":[None,None,2,29,None,None,0,0],\
	"LOF":[None,None,2,30,None,None,0,0],"BMM":[None,None,2,31,None,None,0,0]
}

reformers=[devices,devices,devices,devices]

def isfloat(num):
	try:
		float(num)
		return True
	except ValueError:
		return False

def fmap(x, a, b, c, d):
	f = x/(b-a)*(d-c)+c
	if f > d:
		f = d
	elif f < c:
		f = c
	return f

def u2s(unsigned_int):
	if unsigned_int >= 2**15:
		return -((1 << 16) - unsigned_int)
	return unsigned_int

def binStr(num):
	list1 = []
	while (num > 0):
		list1.append(num % 2)
		num = num//2
	return list1

def bitRead(value,bit):
	return value & 1 << bit != 0

def main():
	global htop
	
	try:
		mb = []
		for i in ReformerIDs:
			#mb.append(ModbusClient(host="127.0.0.1", port=502, unit_id=i, timeout=1,auto_open=True))
			mb.append(ModbusClient(host="uk1.pitunnel.com", port=21792, unit_id=i, timeout=5,auto_open=True))
		
		seconds = [ctypes.c_uint32(0).value]*len(ReformerIDs)
		prevSeconds = [0]*len(ReformerIDs)
		activeReformers = [True]*len(ReformerIDs)
		warning1 = ctypes.c_uint32(0).value
		warning2 = ctypes.c_uint32(0).value
		error1 = ctypes.c_uint32(0).value
		error2 = ctypes.c_uint32(0).value

		allErrors = [0]*len(ReformerIDs)
		allWarnings = [0]*len(ReformerIDs)
		tableData = {}
		tmr = time.perf_counter()
		cnt = 0
		while(1):
			try:
				data = mb[cnt].read_holding_registers(9, 125)
				if not len(data) >= 100:
					raise Exception("data read failure")
			except KeyboardInterrupt:
				htop.terminate()
				sys.exit()
			except:
				if cnt >= (len(ReformerIDs)-1):
					cnt = 0
				else:
					cnt = cnt + 1
				continue
			
			tmp = data[100-9] << 16
			tmp |= data[99-9]
			seconds[cnt] = tmp

			if time.perf_counter() - tmr > 60:
				print(prevSeconds)
				for i in range(len(ReformerIDs)):
					if seconds[i] == prevSeconds[i]:
						activeReformers[i] = False
					else:
						activeReformers[i] = True
						prevSeconds[i] = seconds[i]
				tmr = time.perf_counter()

			if activeReformers[cnt]:
				warning1 = data[96-9] << 16
				warning1 |= data[95-9]
				warning1 &= 0x1FFFFFF

				warning2 = data[98-9] << 16
				warning2 |= data[97-9]
				warning2 &= 0xFF000FFF

				error1 = data[90-9] << 16
				error1 |= data[89-9]
				error1 &= 0x1FFFFFF

				error2 = data[92-9] << 16
				error2 |= data[91-9]
				error2 &= 0xFF000FFF

				if error1 or error2:
					allErrors[cnt] = 1
				else:
					allErrors[cnt] = 0
				if warning1 or warning2:
					allWarnings[cnt] = 1
				else:
					allWarnings[cnt] = 0
				try:
					for dev in reformers[cnt]:
						if reformers[cnt][dev][0] != None:
							reformers[cnt][dev][4] = u2s(data[reformers[cnt][dev][0]-9])
						else:
							reformers[cnt][dev][4] = " "
						if reformers[cnt][dev][2] == 1:
							reformers[cnt][dev][6] = bitRead(warning1,reformers[cnt][dev][3])
							reformers[cnt][dev][7] = bitRead(error1,reformers[cnt][dev][3])
						elif reformers[cnt][dev][2] == 2:
							reformers[cnt][dev][6] = bitRead(warning2,reformers[cnt][dev][3])
							reformers[cnt][dev][7] = bitRead(error2,reformers[cnt][dev][3])

						if reformers[cnt][dev][6] or reformers[cnt][dev][7]:
							if reformers[cnt][dev][1] != None:
								
								extraData = mb[cnt].read_holding_registers(reformers[cnt][dev][1], 7)
								timeout = extraData[0] #lowTimeout
								if reformers[cnt][dev][4] >= u2s(extraData[6]):
									timeout = extraData[1] #highTimeout
								timer = str(extraData[2])+"s/"+str(timeout)+"s"
								extraData[4] = u2s(extraData[4])
								extraData[6] = u2s(extraData[6])
							else:
								extraData = [" "]*10
							#reformer#, sensor, value, min, max, timer/timeout, error
							tableData[str(cnt)+dev] = str(cnt+1)+"|"+dev+"|"+str(reformers[cnt][dev][4])+"|"+str(extraData[4])+"|"+str(extraData[6])+"|"+timer+"|"+str(int(reformers[cnt][dev][7]))+"\n"
						else:
							tableData.pop(str(cnt)+dev,None)
				except TypeError:
					pass
			
			else:
				for row in tableData:
					if row[0] == str(cnt):
						tableData.pop(row,None)
			
			with open('data.txt', 'w') as fd:
				for a in tableData:
					fd.write(tableData[a])
			if htop.poll() != None:
				print("GUI quit")
				sys.exit(1)
			if cnt >= (len(ReformerIDs)-1):
				cnt = 0
			else:
				cnt = cnt + 1
			continue
	except KeyboardInterrupt:
		htop.terminate()
		sys.exit()

if __name__ == '__main__':
	main()
