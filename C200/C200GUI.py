from pathlib import Path
from tkinter import *
import datetime,subprocess,re,time,datetime,ctypes,os,sys

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame0")

timer = time.perf_counter()

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

window = Tk()

width= window.winfo_screenwidth()	#add this
height= window.winfo_screenheight() #add this
window.geometry("%dx%d" % (width, height)) #add this
window.overrideredirect(True)
window.configure(bg = "#FFFFFF",cursor="none")
#[bit#,data]
LSR={"Schmersal":[0,0],"Global Interlock":[1,0],"DPS469 DPS563":[2,0],"Hydraulic Level":[3,0],\
	"Coolant Flow":[4,0],"P2 Pressure":[5,0],"Contamination 1":[6,0],"Contamination 2":[7,0],\
	"E-STOP":[8,0],"Suction Pressure":[9,0],"Discharge Flow":[10,0],"H2 Detector":[11,0],\
	"CPM Rate":[12,0],"Oil Temp":[13,0],"Coolant Temp":[14,0],"Suction Tank Psi":[15,0],"Gas Temp":[16,0],\
	"IDLE Psi":[17,0],"Uneven Psi":[18,0],"S1 Timeout":[19,0],"S2 Timeout":[20,0],"TT-810":[21,0],\
	"TT-809":[22,0],"TT-715":[23,0],"TT-520":[24,0],"TT-521":[25,0],"PT-519":[26,0],"PT-407":[27,0],\
	"PT-410":[28,0],"PT-113":[29,0]
}

#[addr,data,bit#,side]
devices={"PM-904":[0,0,0,1],"PT-911":[9,0,1,1],"PT-716":[10,0,2,1],"PT-712":[11,0,3,2],"PT-519":[12,0,4,2],"PT-407":[13,0,5,2],"PT-410":[14,0,-1,2],\
	"PT-467":[15,0,-1,1],"PT-561":[16,0,-1,2],"PT-556":[17,0,-1,2],"PT-555":[18,0,-1,2],"PT-113":[19,0,6,1],"PT-213":[20,0,7,2],\
	"TT-917":[29,0,16,1],"TT-809":[30,0,17,1],"TT-810":[31,0,18,1],"TT-715":[32,0,19,2],"TT-520":[33,0,22,2],"TT-521":[34,0,23,2],\
	"TT-522":[35,0,24,2],"TT-454":[36,0,13,1],"TT-107":[37,0,20,1],"TT-207":[38,0,21,2]
}

canvas = Canvas(window,bg = "#DFDFDF",height = 1080,width = 1080,bd = 0,highlightthickness = 0,relief = "ridge")

canvas.place(x = 0, y = 0)

image_intenseifier = PhotoImage(file=relative_to_assets("intensifier.png"))
image_upArrow = PhotoImage(file=relative_to_assets("upArrow.png"))
image_downArrow = PhotoImage(file=relative_to_assets("downArrow.png"))
image_signal = PhotoImage(file=relative_to_assets("signal.png"))
window.resizable(False, False)
window.wm_attributes('-fullscreen', 'True')
###############################################

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

def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
Canvas.create_circle = _create_circle

def signalStrength():
	global timer
	if time.perf_counter() - timer > 10:
		try:
			timer = time.perf_counter()
			result = subprocess.run(['sudo', 'qmicli', '-d', '/dev/cdc-wdm0','--nas-get-signal-strength','2>/dev/null'], stderr=subprocess.DEVNULL,stdout=subprocess.PIPE)
			result = result.stdout.decode('utf-8')
			RSSI = re.search("RSSI:.*\n.*': '(.+?) dBm'", result).group(1)
			ECIO = re.search("ECIO:.*\n.*': '(.+?) dBm'", result).group(1)
			SINR = re.search("SINR.* '(.+?) dB'", result).group(1)
			if isfloat(SINR):
				canvas.itemconfig("SINR", text=SINR)
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
				canvas.itemconfig("SINRrect", fill=color)
				canvas.coords("SINRrect",535.0,53.0,fmap(intSINR,0,25,550,713),62.0)
			if isfloat(RSSI):
				canvas.itemconfig("RSSI", text=RSSI)
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
				canvas.itemconfig("RSSIrect", fill=color)
				canvas.coords("RSSIrect",535.0,74.0,fmap(100 - intRSSI,50,100,550,713),83)
			if isfloat(ECIO):
				canvas.itemconfig("ECIO", text=ECIO)
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
				canvas.itemconfig("ECIOrect", fill=color)
				canvas.coords("ECIOrect",535.0,96.0,fmap(20 - intECIO,0,20,550,713),105)
		except:
			pass

def hide(onOff):
	if onOff:
		return "normal"
	else:
		return "hidden"

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
		
		displayState = 1 #starting state
		prevDisplayState = -1
		prevSystemState = -1
		operating = ctypes.c_uint32(0).value
		pauseCauseLow = ctypes.c_uint32(0).value
		pauseCauseHigh = ctypes.c_uint32(0).value
		LSRword = ctypes.c_uint32(0).value
		prevLSRword = -1
		cnt = 0

		#Blue Screen of Death
		canvas.create_rectangle(0,230,1080,1080,tags="BSOD",fill="#0000FF",outline="")
		canvas.create_text(540,540,anchor="center",text="",tags=("BSOD","BSOD_text"),state="hidden",fill="#FFFFFF",font=("Inter Bold", 40 * -1))

		#HEADER
		
		canvas.create_rectangle(0,0,1080,230.0,tags="header",fill="#C3C3C3",outline="")
		canvas.create_rectangle(0.0,0.0,1080.0,116.0,tags="header",fill="#EFEFEF",outline="")
		
		canvas.create_text(540,150,anchor="center",text="System State:",tags="systemState",fill="#000000",font=("Inter Medium", 40 * -1))
		canvas.create_text(419.0,49.0,anchor="nw",text="SINR (",tags="signalStrength",fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_text(470.0,49.0,anchor="nw",text="N/A",tags=("signalStrength","SINR"),fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_text(494.0,49.0,anchor="nw",text="dB):",tags="signalStrength",fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_rectangle(535.0,53.0,550,62.0,fill="black",tags=("signalStrength","SINRrect"),outline="")
		canvas.create_text(419.0,70.0,anchor="nw",text="RSSI (",tags="signalStrength",fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_text(463.0,70.0,anchor="nw",text="N/A",tags=("signalStrength","RSSI"),fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_text(488.0,70.0,anchor="nw",text="dBm):",tags="signalStrength",fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_rectangle(535.0,74.0,550,83,fill="black",tags=("signalStrength","RSSIrect"),outline="")
		canvas.create_text(419.0,91.0,anchor="nw",text="ECIO(",tags="signalStrength",fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_text(460.0,91.0,anchor="nw",text="N/A",tags=("signalStrength","ECIO"),fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_text(488.0,91.0,anchor="nw",text="dBm):",tags="signalStrength",fill="#000000",font=("Inter Bold", 14 * -1))
		canvas.create_rectangle(535.0,96.0,550,105,fill="black",tags=("signalStrength","ECIOrect"),outline="")
		canvas.create_image(390.0,78.0,tags="signalStrength",image=image_signal)

		canvas.create_circle(540, 540, 530,tags="outerCircle", fill="", outline="red", width=30)


		#MAIN PAGE
		centerLow = 405
		centerHigh = 672
		canvas.create_image(201.0,596.0,tags="mainPage",state="hidden",image=image_intenseifier)
		canvas.create_image(879.0,596.0,tags="mainPage",state="hidden",image=image_intenseifier)
		canvas.create_rectangle(280.0,303.0,531.0,887.0,tags=("mainPage","outlineLow"),state="hidden",fill="#F0F0F0",outline="green",width=10)
		canvas.create_rectangle(549.0,303.0,800.0,887.0,tags=("mainPage","outlineHigh"),state="hidden",fill="#F0F0F0",outline="green",width=10)
		canvas.create_text(centerLow,275,anchor="center",text="LOW",tags=("mainPage"),state="hidden",fill="#000000",font=("Inter Medium", 40 * -1))
		canvas.create_text(centerHigh,275,anchor="center",text="HIGH",tags=("mainPage"),state="hidden",fill="#000000",font=("Inter Medium", 40 * -1))
		canvas.create_image(201.0,743.0,tags=("mainPage","DCV1A"),state="hidden",image=image_downArrow)
		canvas.create_image(201.0,452.0,tags=("mainPage","DCV1B"),state="hidden",image=image_upArrow)
		canvas.create_image(879.0,743.0,tags=("mainPage","DCV2A"),state="hidden",image=image_downArrow)
		canvas.create_image(879.0,452.0,tags=("mainPage","DCV2B"),state="hidden",image=image_upArrow)
		canvas.create_rectangle(0,910,1080,980,tags=("mainPage","MAINwarningRect"),state="hidden",fill="white",outline="green",width=10)
		canvas.create_text(540.0,945,anchor="center",text="",tags=("mainPage","MAINwarning"),state="hidden",fill="#000000",font=("Inter ExtraBold", 40 * -1))
		for i in range(16):
			canvas.create_text(centerLow,i*35+325,anchor="center",text="",tags=("mainData","mainPage","lowRow"+str(i)),state="hidden",font=("Inter Medium", 24 * -1))
			canvas.create_text(centerHigh,i*35+325,anchor="center",text="",tags=("mainData","mainPage","highRow"+str(i)),state="hidden",font=("Inter Medium", 24 * -1))


		canvas.create_rectangle(310.0,242,770.0,882.0,tags="lsrPage",fill="#F0F0F0",state="hidden",outline="red",width=10)
		canvas.create_text(540.0,285,anchor="center",text="  LSR Errors  ",tags="lsrPage",state="hidden",fill="#000000",font=("Inter ExtraBold", 50 * -1))
		canvas.create_line(400,310,685,310,width=5,tags="lsrPage",state="hidden",fill="#000000")
		canvas.create_rectangle(0,900,1080,970,tags="lsrPage",fill="orange",outline="black",state="hidden",width=10)
		canvas.create_text(540.0,935,anchor="center",text="",tags=("lsrPage","LSRwarning"),fill="#000000",state="hidden",font=("Inter ExtraBold", 40 * -1))
		for i in range(10):
			canvas.create_text(540.0,i*60+345,anchor="center",text="",tags=("lsrData","lsrPage","lsrRow"+str(i)),state="hidden",fill="#000000",font=("Inter Medium", 40 * -1))

		clock = StringVar()
		date = StringVar()
		clockLabel = Label(window, bg='#C3C3C3',textvariable=clock)
		clockLabel.place(anchor="nw", x=778, y=186)
		clockLabel.configure(font="{Inter} 16 {}")

		dateLabel = Label(window, bg='#C3C3C3',textvariable=date)
		dateLabel.place(anchor="nw", x=186, y=186)
		dateLabel.configure(font="{Inter} 16 {}")
		centerLow = 405
		centerHigh = 672
		tmr = time.perf_counter()
		canvas.create_text(540,1020,anchor="center",text="C400-1",tags="C200Num",fill="#000000",font=("Inter ExtraBold", 50 * -1))
		canvas.tag_raise("outerCircle")
		
		
		while True:
			signalStrength()
			now = datetime.datetime.now()
			today = datetime.datetime.today()
			date.set(today.strftime("%B %d, %Y"))
			clock.set(now.strftime("%H:%M:%S"))
			if (time.perf_counter() - tmr) > 10:
				if cnt >= 3:
					cnt = 0
				else:
					cnt = cnt + 1				
				tmr = time.perf_counter()
			try:
				errorMsg = "0"
				l = 0
				with open("data.txt", "r") as file:
					for line in file:
						l += 1
						if l == 1:
							if line.strip():
								errorMsg = line.strip()
						else:
							if l == cnt+2:
								lst = line.strip().split(",")
								data = [eval(i) for i in lst]  # Split each line into a list
								if not len(data) == 100:
									raise Exception("Data Mismatch")
			except Exception as e:
				print(e)
				continue
			if all(v == 0 for v in data):
				if cnt >= 3:
					cnt = 0
				else:
					cnt = cnt + 1
				continue
			operating = data[92] << 16
			operating |= data[91]

			pauseCauseLow = data[96] << 16
			pauseCauseLow |= data[95]

			pauseCauseHigh = data[98] << 16
			pauseCauseHigh |= data[97]

			LSRword = data[90] << 16
			LSRword |= data[89]
			systemState = data[1]
			for key in LSR:
				LSR[key][1] = bitRead(LSRword,LSR[key][0])

			for dev in devices:
				devices[dev][1] = ctypes.c_int16(data[devices[dev][0]]).value

			if cnt == 0:
				canvas.itemconfig("C200Num", text="C400-1")
			elif cnt == 1:
				canvas.itemconfig("C200Num", text="C400-2")
			elif cnt == 2:
				canvas.itemconfig("C200Num", text="C200-1")
			elif cnt == 3:
				canvas.itemconfig("C200Num", text="C200-2")		

			if systemState != prevSystemState:
				if systemState == 0:
					canvas.itemconfig("outerCircle", outline="red")
					canvas.itemconfig("systemState", text="System State: STOP")
				elif systemState == 1:
					canvas.itemconfig("outerCircle", outline="orange")
					canvas.itemconfig("systemState", text="System State: IDLE")
				elif systemState == 2:
					canvas.itemconfig("outerCircle", outline="orange")
					canvas.itemconfig("systemState", text="System State: STANDBY")
				elif systemState == 3:
					canvas.itemconfig("outerCircle", outline="green")
					canvas.itemconfig("systemState", text="System State: START")
				elif systemState == 4:
					canvas.itemconfig("outerCircle", outline="green")
					canvas.itemconfig("systemState", text="System State: RUN")
				prevSystemState = systemState

			#################################
			
			if errorMsg[0] == "2":
				displayState = 3
			elif LSRword:
				displayState = 1
			else:
				displayState = 2

			if displayState != prevDisplayState:
				canvas.itemconfig("mainPage",state="hidden")
				canvas.itemconfig("lsrPage",state="hidden")
				canvas.itemconfig("BSOD",state="hidden")
				if displayState == 1:
					canvas.itemconfig("lsrPage",state="normal")
				elif displayState == 2:
					canvas.itemconfig("mainPage",state="normal")
				elif displayState == 3:
					canvas.itemconfig("BSOD",state="normal")
				else:
					pass
					
				prevDisplayState = displayState
			#################################
			if displayState == 1:
				canvas.itemconfig("outerCircle", state="normal")
				canvas.itemconfig("C200Num", state="normal")
				if LSR["E-STOP"][1]:
					canvas.itemconfig("LSRwarning",text="Pull ESTOP button to continue.")
				elif not LSR["Schmersal"][1] and not LSR["Coolant Flow"][1]:
					canvas.itemconfig("LSRwarning",text="Push red button to clear errors.")
				else:
					canvas.itemconfig("LSRwarning",text="Hold amber button to continue.")
				j = 0
				for key in LSR:
					if LSR[key][1]:
						canvas.itemconfig("lsrRow"+str(j),state="normal",text=key)
						j += 1
				for i in range(j,10):
					canvas.itemconfig("lsrRow"+str(i),state="hidden",text="")
							
			elif displayState == 2:
				canvas.itemconfig("C200Num", state="normal")
				canvas.itemconfig("outerCircle", state="normal")
				if pauseCauseHigh:
					canvas.itemconfig("outlineHigh", outline="orange")
				else:
					canvas.itemconfig("outlineHigh", outline="green")
				if pauseCauseLow:
					canvas.itemconfig("outlineLow", outline="orange")
				else:
					canvas.itemconfig("outlineLow", outline="green")
				try:
					canvas.itemconfig("DCV1A",state=hide(bitRead(operating,1)))
					canvas.itemconfig("DCV1B",state=hide(bitRead(operating,2)))
					canvas.itemconfig("DCV2A",state=hide(bitRead(operating,3)))
					canvas.itemconfig("DCV2B",state=hide(bitRead(operating,4)))

					if systemState < 2:
						canvas.itemconfig("MAINwarning",state="normal",text="Press green button to run.")
						canvas.itemconfig("MAINwarningRect",state="normal")
					else:
						canvas.itemconfig("MAINwarning",state="hidden")
						canvas.itemconfig("MAINwarningRect",state="hidden")
					j = 0
					k = 0
					for dev in devices:
						unit = ""
						if "TT" in dev:
							unit = "C"
						elif "PT" in dev:
							unit = "psi"
						if devices[dev][3] == 1: #if sensor is on low side
							if pauseCauseLow:
								if bitRead(pauseCauseLow,devices[dev][2]):
									canvas.itemconfig("lowRow"+str(j),state="normal",text=dev+": "+str(devices[dev][1])+unit)
									j += 1
									
							else:
								canvas.itemconfig("lowRow"+str(j),state="normal",text=dev+": "+str(devices[dev][1])+unit)
								j += 1
							
						if devices[dev][3] == 2: #if sensor is on high side
							if pauseCauseHigh:
								if bitRead(pauseCauseHigh,devices[dev][2]):
									canvas.itemconfig("highRow"+str(k),state="normal",text=dev+": "+str(devices[dev][1])+unit)
									k += 1
									
							else:
								canvas.itemconfig("highRow"+str(k),state="normal",text=dev+": "+str(devices[dev][1])+unit)
								k += 1
						for i in range(j,16):
								canvas.itemconfig("lowRow"+str(i),state="hidden",text="")
						for i in range(k,16):
								canvas.itemconfig("highRow"+str(i),state="hidden",text="")		
				except ValueError:
					time.sleep(0.5)

			elif displayState == 3:
				canvas.itemconfig("BSOD_text",text=errorMsg)
				canvas.itemconfig("C200Num", state="hidden")
				canvas.itemconfig("outerCircle", state="hidden")
			window.update()
			window.update_idletasks()

	except TclError as e:
		print(e)
		print("User Manually Exitied")
	except KeyboardInterrupt:
		pass
	except Exception as e:
		with open('log.txt', 'a+') as fd:
			fd.write(str(e))
		sys.exit(1)

if __name__ == '__main__':
	main()
