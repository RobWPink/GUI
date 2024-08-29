from pathlib import Path
from tkinter import *
import datetime,subprocess,re,time,datetime,ctypes,os,sys,math

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
		canvas.create_text(540,1000,anchor="center",text="Page 1/1",tags="pageNum",fill="#000000",font=("Inter Medium", 25 * -1))
		canvas.create_circle(540, 540, 530,tags="outerCircle", fill="", outline="green", width=50)
		clock = StringVar()
		date = StringVar()
		clockLabel = Label(window, bg='#C3C3C3',textvariable=clock)
		clockLabel.place(anchor="nw", x=778, y=186)
		clockLabel.configure(font="{Inter} 16 {}")

		dateLabel = Label(window, bg='#C3C3C3',textvariable=date)
		dateLabel.place(anchor="nw", x=186, y=186)
		dateLabel.configure(font="{Inter} 16 {}")
		page = 0
		pageTmr = time.perf_counter()

		tmr = time.perf_counter_ns()
		tableHeader = ["Reformer#","Sensor","Value","Min","Max","Timer"]
		tableData = {}
		color = "green"
		flash = 0
		for i in range(10):
			for j in range(len(tableHeader)):
				if not i:
					if not j:
						canvas.create_text(235+120*j,280,anchor="center",text=tableHeader[j],tags=("tableHeader"),fill="#000000",font=("Inter ExtraBold", 30 * -1))
					else:
						canvas.create_text(285+120*j,280,anchor="center",text=tableHeader[j],tags=("tableHeader"),fill="#000000",font=("Inter ExtraBold", 30 * -1))
				if not j:
					canvas.create_text(235+120*j,340+i*60,anchor="center",text="",tags=("row"+str(j)+str(i)),fill="#000000",font=("Inter ExtraBold", 30 * -1))
				else:
					canvas.create_text(285+120*j,340+i*60,anchor="center",text="",tags=("row"+str(j)+str(i)),fill="#000000",font=("Inter ExtraBold", 30 * -1))
		while True:
			try:
				signalStrength()
				now = datetime.datetime.now()
				today = datetime.datetime.today()
				date.set(today.strftime("%B %d, %Y"))
				clock.set(now.strftime("%H:%M:%S"))
				try:
					with open("data.txt", "r") as file:
						for line in file:
							route = line.strip().split("|")  # Split each line into a list
							tableData[route[0]+route[1]] = route
				except FileNotFoundError:
					continue
				if flash:
					if time.perf_counter_ns() - tmr > flash:
						canvas.itemconfig("outerCircle", state=hide(tog))
						tog = not tog
						tmr = time.perf_counter_ns()
				else:
					canvas.itemconfig("outerCircle", state="normal")

				canvas.itemconfig("outerCircle", outline=color)

				#################################
				s = 0
				c = 0
				#[deviceAddr	configAddr	group#	errorBits	data	prevData	warning	error]

				if tableData:
					color = "green"
					for row in tableData:
						if page*10 <= c < (page+1)*10:
							for x in range(len(tableHeader)):
								canvas.itemconfig("row"+str(x)+str(s),text=tableData[row][x],state="normal")
								if tableData[row][-1]:
									canvas.itemconfig("row"+str(x)+str(s),fill="red")
									color = "red"
									flash = 250000000
								else:
									canvas.itemconfig("row"+str(x)+str(s),fill="orange")
									if "green" in color:
										color = "orange"
										flash = 500000000
							s += 1
							canvas.itemconfig("pageNum",text="Page "+str(page+1)+"/"+str(math.ceil(len(tableData)/10)))
						c += 1
					if s < 9:
						for i in range(s,10):
							for x in range(len(tableHeader)):
								canvas.itemconfig("row"+str(x)+str(i),text="",state="hidden")
				# else:
				# 	if tableData:
				# 		for row in tableData:
				# 			if row[0] == str(cnt):
				# 				tableData.pop(str(cnt)+dev,None)

				if time.perf_counter() - pageTmr > 10:
					pageTmr = time.perf_counter()
					if page >= math.floor(len(tableData)/10):
						page = 0
					else:
						page = page + 1

				canvas.tag_raise("outerCircle")

				#################################

				window.update()
				window.update_idletasks()

			except ValueError:
				time.sleep(0.5)
			except KeyboardInterrupt:
				sys.exit()
	except TclError:
		print("User Manually Exitied")
	except KeyboardInterrupt:
		sys.exit()
	except Exception as e:
		print(e)
		os.execv(sys.argv[0], sys.argv)

if __name__ == '__main__':
	main()
