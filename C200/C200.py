from pathlib import Path
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import *
from tkinter import *
import datetime,subprocess,re,time,datetime,ctypes

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame0")

timer = time.perf_counter()

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

window = Tk()
width= window.winfo_screenwidth()	#add this
height= window.winfo_screenheight() #add this
window.geometry("%dx%d" % (width, height)) #add this
window.configure(bg = "#FFFFFF")

LSR={"Schmersal":[0,0,0],"Global Interlock":[0,0,0],"DPS469 DPS563":[0,0,0],"Hydraulic Level":[0,0,0],\
	"Coolant Flow":[0,0,0],"P2 Pressure":[0,0,0],"Contamination 1":[0,0,0],"Contamination 2":[0,0,0],\
	"E-STOP":[0,0,0],"Suction Pressure":[0,0,0],"Discharge Flow":[0,0,0],"H2 Detector":[0,0,0],\
	"CPM Rate":[0,0,0],"Oil Temp":[0,0,0],"Coolant Temp":[0,0,0],"Suction Tank Psi":[0,0,0],"Gas Temp":[0,0,0],\
	"IDLE Psi":[0,0,0],"Uneven Psi":[0,0,0],"S1 Timeout":[0,0,0],"S2 Timeout":[0,0,0],"TT-810":[0,0,0],\
	"TT-809":[0,0,0],"TT-715":[0,0,0],"TT-520":[0,0,0],"TT-521":[0,0,0],"PT-519":[0,0,0],"PT-407":[0,0,0],\
	"PT-410":[0,0,0],"PT-113":[0,0,0]
}

#[data,prevData,label#,circle#,bit#,side]
devices={"PM-904":[0,0,0,0,1],"PT-911":[0,0,0,1,1],"PT-716":[0,0,0,2,1],"PT-712":[0,0,0,3,2],"PT-519":[0,0,0,4,2],"PT-407":[0,0,0,5,2],"PT-410":[0,0,0,-1,2],\
	"PT-467":[0,0,0,-1,1],"PT-561":[0,0,0,-1,2],"PT-556":[0,0,0,-1,2],"PT-555":[0,0,0,-1,2],"PT-113":[0,0,0,6,1],"PT-213":[0,0,0,7,2],\
	"TT-917":[0,0,0,16,1],"TT-809":[0,0,0,17,1],"TT-810":[0,0,0,18,1],"TT-715":[0,0,0,19,2],"TT-520":[0,0,0,22,2],"TT-521":[0,0,0,23,2],\
	"TT-522":[0,0,0,24,2],"TT-454":[0,0,0,13,0],"TT-107":[0,0,0,20,1],"TT-207":[0,0,0,21,2]
}


indicator1 = 0
indicator2 = 0

sigStrength = [0]*6


canvas = Canvas(window,bg = "#DFDFDF",height = 1080,width = 1080,bd = 0,highlightthickness = 0,relief = "ridge")

canvas.place(x = 0, y = 0)

image_red_circle = PhotoImage(file=relative_to_assets("image_1.png"))#red Circle
image_green_circle = PhotoImage(file=relative_to_assets("image_2.png"))#green Circle
image_red_LED = PhotoImage(file=relative_to_assets("image_3.png"))
image_green_LED = PhotoImage(file=relative_to_assets("image_4.png"))
image_amber_LED = PhotoImage(file=relative_to_assets("image_11.png"))
image_intenseifier = PhotoImage(file=relative_to_assets("image_10.png"))
image_greenIndicator = PhotoImage(file=relative_to_assets("image_8.png"))
image_amberIndicator = PhotoImage(file=relative_to_assets("image_7.png"))
image_redIndicator = PhotoImage(file=relative_to_assets("image_6.png"))
image_upArrow = PhotoImage(file=relative_to_assets("image_5.png"))
image_downArrow = PhotoImage(file=relative_to_assets("image_9.png"))
image_signal = PhotoImage(file=relative_to_assets("signal.png"))
window.resizable(False, False)
window.wm_attributes('-fullscreen', 'True')
###############################################

def page_LSR_errors(canvasData):
	if not canvasData:
		canvasData.append(canvas.create_text(385.0,76.0+50,anchor="nw",text="LSR Errors",fill="#000000",font=("Inter ExtraBold", 60 * -1)))
		canvasData.append(canvas.create_rectangle(310.0,162.0+50,770.0,982.0,fill="#F0F0F0",outline=""))
	y = 0
	for key in LSR:
		if LSR[key][0] and not LSR[key][2]:
			y = 1
		elif not LSR[key][0] and LSR[key][2]:
			y = 1

		if y:
			y = 0
			for key in LSR:
				if LSR[key][0]:
					canvas.delete(LSR[key][1])
					LSR[key][1] = 0
					canvas.delete(LSR[key][2])
					LSR[key][2] = 0
					LSR[key][1] = canvas.create_text(415.0,185.0+y+50,anchor="nw",text=key,fill="#000000",font=("Inter Medium", 40 * -1))
					LSR[key][2] = canvas.create_image(390.0,209.0+y+50,image=image_red_LED)
					y = y + 60
				else:
					canvas.delete(LSR[key][1])
					LSR[key][1] = 0
					canvas.delete(LSR[key][2])
					LSR[key][2] = 0
	

def page_main(canvasData,pauseCause1,pauseCause2):
	global indicator1
	global indicator2
	if not canvasData:
		canvasData.append(canvas.create_image(201.0,596.0,image=image_intenseifier))
		canvasData.append(canvas.create_image(879.0,596.0,image=image_intenseifier))
		canvasData.append(canvas.create_text(310.0,122.0,anchor="nw",text="System State:",fill="#000000",font=("Inter Medium", 40 * -1)))
		canvasData.append(canvas.create_rectangle(280.0,303.0,531.0,887.0,fill="#F0F0F0",outline=""))
		canvasData.append(canvas.create_rectangle(549.0,303.0,800.0,887.0,fill="#F0F0F0",outline=""))
		canvasData.append(canvas.create_image(201.0,251.0,image=image_greenIndicator))
		canvasData.append(canvas.create_image(879.0,251.0,image=image_greenIndicator))

	y1 = 0
	y2 = 0
	
	for dev in devices:
		unit = ""
		if "TT" in dev:
			unit = "C"
		elif "PT" in dev:
			unit = "psi"
		
			
		if devices[dev][4] == 1 or not devices[dev][4]: #if sensor is on low side
			if devices[dev][1]: #delete previous text/data
				canvas.delete(devices[dev][1])
				canvas.delete(devices[dev][2])
			if pauseCause1:
				if devices[dev][3] >= 0:
					if test_bit(pauseCause1,devices[dev][3]):
						devices[dev][1] = canvas.create_text(322.0,310.0+y1,anchor="nw",text=dev + " - " + str(devices[dev][0]) + unit,fill="#000000",font=("Inter Medium", 24 * -1))
						devices[dev][2] = canvas.create_image(301.0,324.0+y1,image=image_amber_LED)
						if not indicator1:
							indicator1 = canvas.create_image(201.0,251.0,image=image_amberIndicator)
						y1 = y1 + 36
			else:
				devices[dev][1] = canvas.create_text(322.0,310.0+y1,anchor="nw",text=dev + " - " + str(devices[dev][0]) + unit,fill="#000000",font=("Inter Medium", 24 * -1))
				devices[dev][2] = canvas.create_image(301.0,324.0+y1,image=image_green_LED)
				if indicator1:
					canvas.delete(indicator1)
					indicator1 = 0
				y1 = y1 + 36
			
		if devices[dev][4] == 2 or not devices[dev][4]: #if sensor is on low side
			if devices[dev][1]: #delete previous text/data
				canvas.delete(devices[dev][1])
				canvas.delete(devices[dev][2])
			if pauseCause2:
				if devices[dev][3] >= 0:
					if test_bit(pauseCause2,devices[dev][3]):
						devices[dev][1] = canvas.create_text(592.0,310.0+y2,anchor="nw",text=dev + " - " + str(devices[dev][0]) + unit,fill="#000000",font=("Inter Medium", 24 * -1))
						devices[dev][2] = canvas.create_image(571.0,324.0+y2,image=image_amber_LED)
						if not indicator2:
							indicator2 = canvas.create_image(879.0,251.0,image=image_amberIndicator)
						y2 = y2 + 36
			else:
				devices[dev][1] = canvas.create_text(592.0,310.0+y2,anchor="nw",text=dev + " - " + str(devices[dev][0]) + unit,fill="#000000",font=("Inter Medium", 24 * -1))
				devices[dev][2] = canvas.create_image(571.0,324.0+y2,image=image_green_LED)
				if indicator2:
					canvas.delete(indicator2)
					indicator2 = 0
				y2 = y2 + 36
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


def gui():
	global timer
	if time.perf_counter() - timer > 1:
		try:
			timer = time.perf_counter()
			result = subprocess.run(['sudo', 'qmicli', '-d', '/dev/cdc-wdm0','--nas-get-signal-strength','2>/dev/null'], stderr=subprocess.DEVNULL,stdout=subprocess.PIPE)
			result = result.stdout.decode('utf-8')
			RSSI = re.search("RSSI:.*\n.*': '(.+?) dBm'", result).group(1)
			ECIO = re.search("ECIO:.*\n.*': '(.+?) dBm'", result).group(1)
			SINR = re.search("SINR.* '(.+?) dB'", result).group(1)
			if isfloat(SINR):
				canvas.delete(sigStrength[0])
				sigStrength[0] = canvas.create_text(470.0,49.0,anchor="nw",text=SINR,fill="#000000",font=("Inter Bold", 14 * -1))
				intSINR = float(SINR)
				if intSINR >= 20:
					color = "#29FF32" #green
				elif 13 <= intSINR < 20:
					color = "#FFEB32" #yellow
				elif 6 <= intSINR < 13:
					color = "#FFA032" #orange
				elif 0 < intSINR < 6:
					color = "#FF0000" #red
				else:
					color = "#000000" #black
				canvas.delete(sigStrength[1])
				sigStrength[1] = canvas.create_rectangle(535.0,53.0,fmap(intSINR,0,25,550,713),62.0,fill=color,outline="")
			if isfloat(RSSI):
				canvas.delete(sigStrength[2])
				sigStrength[2] = canvas.create_text(463.0,70.0,anchor="nw",text=RSSI,fill="#000000",font=("Inter Bold", 14 * -1))
				intRSSI = float(RSSI)*-1
				if intRSSI <= 65:
					color = "#29FF32" #green
				elif 65 < intRSSI <= 75:
					color = "#FFEB32" #yellow
				elif 75 <= intRSSI <= 85:
					color = "#FFA032" #orange
				elif 85 < intRSSI <= 95:
					color = "#FF0000" #red
				else:
					color = "#000000" #black
				canvas.delete(sigStrength[3])
				sigStrength[3] = canvas.create_rectangle(535.0,74.0,fmap(100 - intRSSI,50,100,550,713),83,fill=color,outline="")
			if isfloat(ECIO):
				canvas.delete(sigStrength[4])
				sigStrength[4] = canvas.create_text(460.0,91.0,anchor="nw",text=ECIO,fill="#000000",font=("Inter Bold", 14 * -1))
				intECIO = float(ECIO) * -1
				if intECIO <= 4:
					color = "#29FF32" #green
				elif 4 < intECIO <= 8:
					color = "#FFEB32" #yellow
				elif 8 < intECIO <= 11:
					color = "#FFA032" #orange
				elif 11 < intECIO < 20:
					color = "#FF0000" #red
				else:
					color = "#000000" #black
				canvas.delete(sigStrength[5])
				sigStrength[5] =canvas.create_rectangle(535.0,96.0,fmap(20 - intECIO,0,20,550,713),105,fill=color,outline="")
		except:
			pass

def binStr(num):
	list1 = []
	while (num > 0):
		list1.append(num % 2)
		num = num//2
	return list1

def bitRead(value,bit):
	return value & 1 << bit != 0

def main():
	try:
		c = ModbusClient(host="58.105.200.89", port=502, unit_id=1, auto_open=True)
		displayState = 0
		prevDisplayState = 0
		canvasData = []
		greenCircle = 0
		systemState = 0
		DCV1A = 0
		DCV1B = 0
		DCV2A = 0
		DCV2B = 0
		state = -1
		rect2 = canvas.create_rectangle(0,0,1080,200.0,fill="#C3C3C3",outline="")
		rect1 = canvas.create_rectangle(0.0,0.0,1080.0,116.0,fill="#EFEFEF",outline="")
		
		greenCircle = canvas.create_image(540.0,540.0,image=image_green_circle)
		redCircle = canvas.create_image(540.0,540.0,image=image_red_circle)
		canvas.create_text(419.0,49.0,anchor="nw",text="SINR (",fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_text(494.0,49.0,anchor="nw",text="dB):",fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_text(419.0,70.0,anchor="nw",text="RSSI (",fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_text(488.0,70.0,anchor="nw",text="dBm):",fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_text(419.0,91.0,anchor="nw",text="ECIO(",fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_text(488.0,91.0,anchor="nw",text="dBm):",fill="#000000",font=("Inter Bold", 14 * -1))
		clock = StringVar()
		date = StringVar()
		clockLabel = Label(window, bg='#C3C3C3',textvariable=clock)
		clockLabel.place(anchor="nw", x=768, y=166)
		clockLabel.configure(font="{Inter} 16 {}")

		dateLabel = Label(window, bg='#C3C3C3',textvariable=date)
		dateLabel.place(anchor="nw", x=186, y=166)
		dateLabel.configure(font="{Inter} 16 {}")
		signal = canvas.create_image(390.0,78.0,image=image_signal)

		while True:
			gui()
			now = datetime.datetime.now()
			today = datetime.datetime.today()
			date.set(today.strftime("%B %d, %Y"))
			clock.set(now.strftime("%H:%M:%S"))
			data = c.read_holding_registers(0, 100)
			#settings = c.read_holding_registers(2001, 100)
			operating = ctypes.c_uint32(0).value
			operating |= (data[92] << 16) 
			operating |= data[91]

			pauseCauseLow = ctypes.c_uint32(0).value
			pauseCauseLow |= (data[96] << 16) 
			pauseCauseLow |= data[95]

			pauseCauseHigh = ctypes.c_uint32(0).value
			pauseCauseHigh |= (data[98] << 16) 
			pauseCauseHigh |= data[97]

			systemState = data[1]
			i = 0
			for key in LSR:
				LSR[key][0] = bitRead((data[90] << 16) | data[89],i)
				i = i + 1
			
			i = 10
			for dev in devices:
				devices[dev][0] = data[i]
				if i == 21:
					i = i + 9
				else:
					i = i + 1
			
			if not data[89] and not greenCircle:
				greenCircle = canvas.create_image(540.0,540.0,image=image_green_circle)
				if redCircle:
					canvas.delete(redCircle)
			elif data[89] and greenCircle:
				canvas.delete("all")
				canvas.create_rectangle(0,0,1080,200.0,fill="#C3C3C3",outline="")
				canvas.create_rectangle(0.0,0.0,1080.0,116.0,fill="#EFEFEF",outline="")
				signal = canvas.create_image(390.0,78.0,image=image_signal)
				redCircle = canvas.create_image(540.0,540.0,image=image_red_circle)
				canvas.create_text(419.0,49.0,anchor="nw",text="SINR (",fill="#000000",font=("Inter Bold", 14 * -1))
				canvas.create_text(494.0,49.0,anchor="nw",text="dB):",fill="#000000",font=("Inter Bold", 14 * -1))
				canvas.create_text(419.0,70.0,anchor="nw",text="RSSI (",fill="#000000",font=("Inter Bold", 14 * -1))
				canvas.create_text(488.0,70.0,anchor="nw",text="dBm):",fill="#000000",font=("Inter Bold", 14 * -1))
				canvas.create_text(419.0,91.0,anchor="nw",text="ECIO(",fill="#000000",font=("Inter Bold", 14 * -1))
				canvas.create_text(488.0,91.0,anchor="nw",text="dBm):",fill="#000000",font=("Inter Bold", 14 * -1))
				greenCircle = 0
				displayState = 1

			
			if displayState == 1:
				if displayState != prevDisplayState:
					for can in canvasData:
						canvas.delete(can)
					canvasData = []
					prevDisplayState = displayState
				page_LSR_errors(canvasData)
				if not data[89]:
					displayState = 2


			elif displayState == 2:
				if displayState != prevDisplayState:
					for can in canvasData:
						canvas.delete(can)
					canvasData = []
					prevDisplayState = displayState
				page_main(canvasData,pauseCauseLow,pauseCauseHigh)
				if state != data[1]:
					stateMsg = ""
					state = data[1]
					if systemState:
						canvas.delete(systemState)
					if data[1] == 0:
						stateMsg = "STOP"
					elif data[1] == 1:
						stateMsg = "IDLE"
					elif data[1] == 2:
						stateMsg = "STANDBY"
					elif data[1] == 3:
						stateMsg = "START"
					elif data[1] == 4:
						stateMsg = "RUN"
					systemState = canvas.create_text(600.0,122.0,anchor="nw",text=stateMsg,fill="#000000",font=("Inter Bold", 40 * -1))

				if test_bit(operating,1) and not DCV1A:
					DCV1A = canvas.create_image(201.0,743.0,image=image_upArrow)
				if not test_bit(operating,1) and DCV1A:
					canvas.delete(DCV1A)
					DCV1A = 0

				if test_bit(operating,2) and not DCV1B:
					DCV1B = canvas.create_image(201.0,452.0,image=image_downArrow)
				if not test_bit(operating,2) and DCV1B:
					canvas.delete(DCV1B)
					DCV1B = 0

				if test_bit(operating,3) and not DCV2A:
					DCV2A = canvas.create_image(879.0,743.0,image=image_upArrow)
				if not test_bit(operating,3) and DCV2A:
					canvas.delete(DCV2A)
					DCV2A = 0

				if test_bit(operating,4) and not DCV2B:
					DCV2B = canvas.create_image(879.0,452.0,image=image_downArrow)
				if not test_bit(operating,4) and DCV2B:
					canvas.delete(DCV2B)
					DCV2B = 0


			window.update()
			window.update_idletasks()
	except KeyboardInterrupt:
		pass
	except Exception as e:
		print(e)

			

if __name__ == '__main__':
	main()