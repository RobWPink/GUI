from pathlib import Path
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import test_bit
from tkinter import *
import datetime,subprocess,re,time,datetime,ctypes,os,sys

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame0")

timer = time.perf_counter()

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

ReformerIDs = [1,2,3,4]

window = Tk()

width= window.winfo_screenwidth()	#add this
height= window.winfo_screenheight() #add this
window.geometry("%dx%d" % (width, height)) #add this
window.overrideredirect(True)
window.configure(bg = "#FFFFFF",cursor="none")
#[deviceAddr	configAddr	group#	errorBits	labelVar	data	prevData	warning	error]
devices = {
	"TT142":[29,2600,1,0,StringVar(),0,0,0,0],"TT301":[30,2610,1,1,StringVar(),0,0,0,0],"TT303":[31,2620,1,2,StringVar(),0,0,0,0],\
	"TT306":[32,2630,1,3,StringVar(),0,0,0,0],"TT313":[33,2640,1,4,StringVar(),0,0,0,0],"TT319":[34,2650,1,5,StringVar(),0,0,0,0],\
	"TT407":[35,2660,1,6,StringVar(),0,0,0,0],"TT408":[36,2670,1,7,StringVar(),0,0,0,0],"TT410":[37,2680,1,8,StringVar(),0,0,0,0],\
	"TT411":[38,2690,1,9,StringVar(),0,0,0,0],"TT430":[39,2700,1,10,StringVar(),0,0,0,0],"TT511":[40,2710,1,11,StringVar(),0,0,0,0],\
	"TT512":[41,2720,1,12,StringVar(),0,0,0,0],"TT513":[42,2730,1,13,StringVar(),0,0,0,0],"TT514":[43,2740,1,14,StringVar(),0,0,0,0],\
	"TT441":[44,2750,1,15,StringVar(),0,0,0,0],"TT442":[45,2760,1,16,StringVar(),0,0,0,0],"TT443":[46,2770,1,17,StringVar(),0,0,0,0],\
	"TT444":[47,2780,1,18,StringVar(),0,0,0,0],"TT445":[48,2790,1,19,StringVar(),0,0,0,0],"TT446":[129,2800,1,20,StringVar(),0,0,0,0],\
	"TT447":[130,2810,1,21,StringVar(),0,0,0,0],"TT448":[131,2820,1,22,StringVar(),0,0,0,0],"TT449":[132,2830,1,23,StringVar(),0,0,0,0],\
	"TT109":[133,2840,1,24,StringVar(),0,0,0,0],"FT132":[9,2850,2,0,StringVar(),0,0,0,0],"FCV134":[10,2860,2,1,StringVar(),0,0,0,0],\
	"FCV141":[11,2870,2,2,StringVar(),0,0,0,0],"FCV474":[12,2880,2,3,StringVar(),0,0,0,0],"FCV205":[13,2890,2,4,StringVar(),0,0,0,0],\
	"BL508":[14,2900,2,5,StringVar(),0,0,0,0],"PT107":[15,2910,2,6,StringVar(),0,0,0,0],"PT213":[16,2920,2,7,StringVar(),0,0,0,0],\
	"PT318":[17,2930,2,8,StringVar(),0,0,0,0],"PT304":[18,2940,2,9,StringVar(),0,0,0,0],"PT420":[19,2950,2,10,StringVar(),0,0,0,0],\
	"PMP204":[20,2960,2,11,StringVar(),0,0,0,0]
}
reformers=[devices,devices,devices,devices]

canvas = Canvas(window,bg = "#DFDFDF",height = 2080,width = 1080,bd = 0,highlightthickness = 0,relief = "ridge")

canvas.place(x = 0, y = 0)
tog = False
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

def u2s(unsigned_int):
	if unsigned_int >= 2**15:
		return -((1 << 16) - unsigned_int)
	return unsigned_int


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
	global tog
	try:
		mb = []
		for i in ReformerIDs:
			#mb.append(ModbusClient(host="127.0.0.1", port=502, unit_id=i, timeout=1,auto_open=True))
			mb.append(ModbusClient(host="uk1.pitunnel.com", port=21792, unit_id=i, timeout=3,auto_open=True))

		warning1 = ctypes.c_uint32(0).value
		warning2 = ctypes.c_uint32(0).value
		error1 = ctypes.c_uint32(0).value
		error2 = ctypes.c_uint32(0).value

		cnt = 0
		canvas.create_rectangle(0,0,1080,230.0,tags="header",fill="#C3C3C3",outline="")
		canvas.create_rectangle(0.0,0.0,1080.0,116.0,tags="header",fill="#EFEFEF",outline="")
		canvas.create_text(540,150,anchor="center",text="Reformer Group A",tags="systemState",fill="#000000",font=("Inter Medium", 40 * -1))
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

		canvas.create_circle(540, 540, 530,tags="outerCircle", fill="", outline="green", width=50)
		spaceSize = 10
		clock = StringVar()
		date = StringVar()
		clockLabel = Label(window, bg='#C3C3C3',textvariable=clock)
		clockLabel.place(anchor="nw", x=778, y=186)
		clockLabel.configure(font="{Inter} 16 {}")

		dateLabel = Label(window, bg='#C3C3C3',textvariable=date)
		dateLabel.place(anchor="nw", x=186, y=186)
		dateLabel.configure(font="{Inter} 16 {}")

		allErrors = [0,0,0,0]
		allWarnings = [0,0,0,0]
		tableData = {}
		tmr = time.perf_counter()
		tableHeader = "Reformer#".center(spaceSize,' ')+ "Sensor".center(spaceSize,' ')+ "Value".center(spaceSize,' ')+ "Min".center(spaceSize,' ')+ "Max".center(spaceSize,' ')+ "Timer".center(spaceSize,' ')
		canvas.create_text(540.0,300,anchor="center",text=tableHeader,tags=("tableHeader"),fill="#000000",font=("Inter ExtraBold", 30 * -1))
		for i in range(10):
			canvas.create_text(540.0,360+i*60,anchor="center",text="",tags=("row"+str(i)),fill="#000000",font=("Inter ExtraBold", 30 * -1))
		while True:
			try:
				
				signalStrength()
				now = datetime.datetime.now()
				today = datetime.datetime.today()
				date.set(today.strftime("%B %d, %Y"))
				clock.set(now.strftime("%H:%M:%S"))
				try:
					data = mb[cnt].read_holding_registers(9, 125)
					if not len(data) >= 100:
						raise Exception("data read failure")
				except:
					if cnt >= 3:
						cnt = 0
					else:
						cnt = cnt + 1
					continue

				warning1 = data[96-9] << 16
				warning1 |= data[95-9]
				warning1 &= 0x1FFFFFF

				warning2 = data[98-9] << 16
				warning2 |= data[97-9]
				warning2 &= 0xFFF

				error1 = data[90-9] << 16
				error1 |= data[89-9]
				error1 &= 0x1FFFFFF

				error2 = data[92-9] << 16
				error2 |= data[91-9]
				error2 &= 0xFFF

				if error1 or error2:
					allErrors[cnt] = 1
				else:
					allErrors[cnt] = 0
				if warning1 or warning2:
					allWarnings[cnt] = 1
				else:
					allWarnings[cnt] = 0

				if not all(v == 0 for v in allErrors):
					if time.perf_counter() - tmr > 2:
						canvas.itemconfig("outerCircle", state=hide(tog))
						tog = not tog
						tmr = time.perf_counter()
					canvas.itemconfig("outerCircle", outline="red")
				elif not all(v == 0 for v in allWarnings):
					canvas.itemconfig("outerCircle", outline="orange")
					if time.perf_counter() - tmr > 2:
						canvas.itemconfig("outerCircle", state=hide(tog))
						if tog:
							tog = False
						else:
							tog = True
						tmr = time.perf_counter()
				else:
					canvas.itemconfig("outerCircle", outline="green")

				for dev in reformers[cnt]:
					reformers[cnt][dev][5] = u2s(data[reformers[cnt][dev][0]-9])
					if reformers[cnt][dev][2] == 1:
						reformers[cnt][dev][7] = bitRead(warning1,reformers[cnt][dev][3])
						reformers[cnt][dev][8] = bitRead(error1,reformers[cnt][dev][3])
					elif reformers[cnt][dev][2] == 2:
						reformers[cnt][dev][7] = bitRead(warning2,reformers[cnt][dev][3])
						reformers[cnt][dev][8] = bitRead(error2,reformers[cnt][dev][3])

					if reformers[cnt][dev][7] or reformers[cnt][dev][8]:
						extraData = mb[cnt].read_holding_registers(reformers[cnt][dev][1], 7)
						timeout = extraData[0] #lowTimeout
						if reformers[cnt][dev][5] >= u2s(extraData[6]):
							timeout = extraData[1] #highTimeout
						timer = str(extraData[2])+"s/"+str(timeout)+"s"
						#reformer#, sensor, value, min, max, timer/timeout
						tableData[str(cnt)+dev] = [str(cnt+1).center(spaceSize,' ')+dev.center(spaceSize,' ')+str(reformers[cnt][dev][5]).center(spaceSize,' ')+str(u2s(extraData[4])).center(spaceSize,' ')+str(u2s(extraData[6])).center(spaceSize,' ') + timer.center(spaceSize,' '),reformers[cnt][dev][8]]

					else:
						tableData.pop(str(cnt)+dev,None)

				#################################
				s = 0
				#[deviceAddr	configAddr	group#	errorBits	labelVar	data	prevData	warning	error]
				if tableData:
					for row in tableData:
						canvas.itemconfig("row"+str(s),text=tableData[row][0],state="normal")
						if tableData[row][1]:
							canvas.itemconfig("row"+str(s),fill="red")
						else:
							canvas.itemconfig("row"+str(s),fill="orange")
						s += 1
					for i in range(s,10):
						canvas.itemconfig("row"+str(i),text="",state="hidden")


				canvas.tag_raise("outerCircle")

				#################################

				window.update()
				window.update_idletasks()
				if cnt >= 3:
						cnt = 0
				else:
					cnt = cnt + 1
			except ValueError:
				time.sleep(0.5)
	except TclError:
		print("User Manually Exitied")
	except KeyboardInterrupt:
		pass
	except Exception as e:
		print(e)
		os.execv(sys.argv[0], sys.argv)

if __name__ == '__main__':
	main()
