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
errors={"PT-Suction":[1,2,0],"PT-Discharge":[1,4,0],"ACT1-Position":[1,6,0],
	"ACT2-Position":[1,7,0],"TC-105":[1,8,0],"TC-205":[1,9,0],"TC-313":[1,10,0],
	"TC-444":[1,11,0],"TC-447":[1,12,0],"PSA1-Flow":[1,16,0],"PSA2-Flow":[1,17,0],
	"PT-PSA1-Inter":[1,18,0],"PT-PSA2-Inter":[1,12,0],"TC-PSA1":[1,13,0],"TC-PSA2":[1,14,0],
	"TC-SPARE":[1,15,0],"FM-FM904":[1,23,0],"FM-TC904":[1,24,0],"FM-PT904":[1,25,0],
	"WaterLevel1":[2,0,0],"WaterLevel2":[2,1,0],"WaterLevel3":[2,2,0],"Cold Oil":[2,3,0],
	"Heater Failure":[2,4,0],"EVO PID Nan":[2,5,0],"PSA1 PID Nan":[2,6,0],"PSA2 PID Nan":[2,7,0]
}

#[addr,data,bit#,side]
devices={"PT-Suction":[11,0],"PT-Discharge":[13,0],"ACT1-Position":[15,0],"ACT2-Position":[16,0],"PT-PSA1-Inter":[17,0],"PT-PSA2-Inter":[18,0],
	"PSA1-Flow":[19,0],"PSA2-Flow":[20,0],"TC-105":[29,0],"TC-205":[30,0],"TC-313":[31,0],"TC-444":[32,0],
	"TC-447":[33,0],"TC-RPSA1":[37,0],"TC-RPSA2":[38,0],"TC-SPARE":[39,0],"AO-FCV1":[75,0],"AO-FCV2":[77,0],
	"AO-EVO":[81,0],"FM-FM904":[83,0],"FM-TC904":[85,0],"FM-PT904":[87,0]
}

canvas = Canvas(window,bg = "#DFDFDF",height = 1080,width = 1080,bd = 0,highlightthickness = 0,relief = "ridge")

canvas.place(x = 0, y = 0)

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

def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
 
  return cpuserial

def main():
	try:
		displayState = 1 #starting state
		prevDisplayState = -1
		operating = ctypes.c_uint32(0).value
		digitalInputs = ctypes.c_uint32(0).value
		digitalOutputs = ctypes.c_uint32(0).value
		errorWord1 = ctypes.c_uint32(0).value
		errorWord2 = ctypes.c_uint32(0).value

		#Blue Screen of Death
		canvas.create_rectangle(0,230,1080,1080,tags="BSOD",fill="#0000FF",outline="")
		canvas.create_text(540,540,anchor="center",text="",tags=("BSOD","BSOD_text"),state="hidden",fill="#FFFFFF",font=("Inter Bold", 40 * -1))

		#HEADER
		
		canvas.create_rectangle(0,0,1080,230.0,tags="header",fill="#C3C3C3",outline="")
		canvas.create_rectangle(0.0,0.0,1080.0,116.0,tags="header",fill="#EFEFEF",outline="")
		
		#canvas.create_text(540,150,anchor="center",text="System State:",tags="systemState",fill="#000000",font=("Inter Medium", 40 * -1))
		canvas.create_text(540,150,anchor="center",text="E100",tags="systemState",fill="#000000",font=("Inter Medium", 40 * -1))
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
		#heater
		canvas.create_rectangle(553.0,261.0,858.0,586.0,tags="mainpage",fill="#BFBFBF",outline="")
		canvas.create_text(638.0,264.0,anchor="nw",text="Heater",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 40 * -1))
		canvas.create_text(740.0,345.9673156738281,anchor="nw",text="999",tags=("TC-313","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(740.0,391.63726806640625,anchor="nw",text="999",tags=("TC-444","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(740.0,437.30718994140625,anchor="nw",text="999",tags=("TC-447","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(620.0,345.9673156738281,anchor="nw",text="TC-313:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(614.0,391.63726806640625,anchor="nw",text="TC-444:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(617.0,437.30718994140625,anchor="nw",text="TC-447:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(617.0,533.95751953125,anchor="nw",text="Heater Element",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(616.0,490.4117431640625,anchor="nw",text="Cooling Fan",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_rectangle(580.0,539.2679443359375,604.0,564.7581405639648,tags="mainpage",fill="#FF0000",outline="")#heater element
		canvas.create_rectangle(580.0,539.2679443359375,604.0,564.7581405639648,tags=("heater","mainpage"),state="hidden",fill="#00FF00",outline="")#heater element
		canvas.create_rectangle(580.0,495.72222900390625,604.0,521.2124252319336,tags="mainpage",fill="#FF0000",outline="")#cooling fan
		canvas.create_rectangle(580.0,495.72222900390625,604.0,521.2124252319336,tags=("cooler","mainpage"),state="hidden",fill="#00FF00",outline="")#cooling fan

		#evo
		canvas.create_rectangle(222.0,264.0,527.0,584.0,tags="mainpage",fill="#BFBFBF",outline="")
		canvas.create_text(332.0,268.0,anchor="nw",text="EVO",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 40 * -1))
		canvas.create_text(314.0,539.0,anchor="nw",text="VFD Enable",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_rectangle(277.0,542.0,301.0,566.0,tags="mainpage",fill="#FF0000",outline="")#evo enable
		canvas.create_rectangle(277.0,542.0,301.0,566.0,tags=("evoEnable","mainpage"),state="hidden",fill="#00FF00",outline="")#evo enable
		canvas.create_text(391.0,330.0,anchor="nw",text="AO: ",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(329.0,368.0,anchor="nw",text="TC-105:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(326.0,406.0,anchor="nw",text="TC-205:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(243.0,482.0,anchor="nw",text="PT-Discharge:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(277.0,444.0,anchor="nw",text="PT-Suction:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(449.0,330.0,anchor="nw",text="999",tags=("AO-EVO","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(449.0,368.0,anchor="nw",text="999",tags=("TC-105","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(449.0,406.0,anchor="nw",text="999",tags=("TC-205","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(449.0,444.0,anchor="nw",text="999",tags=("PT-Suction","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(449.0,482.0,anchor="nw",text="999",tags=("PT-Discharge","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		#psa1
		canvas.create_rectangle(222.0,609.0,527.0,929.0,tags="mainpage",fill="#BFBFBF",outline="")
		canvas.create_text(324.0,611.0,anchor="nw",text="PSA1",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 40 * -1))
		canvas.create_text(314.0,885.0,anchor="nw",text="VFD Enable",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_rectangle(277.0,888.0094604492188,301.0,912.08469581604,tags="mainpage",fill="#FF0000",outline="") #psa1 enable
		canvas.create_rectangle(277.0,888.0094604492188,301.0,912.08469581604,tags=("psa1Enable","mainpage"),state="hidden",fill="#00FF00",outline="") #psa1 enable
		canvas.create_text(314.0,842.0,anchor="nw",text="Feed XV",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_rectangle(277.0,845.0094604492188,301.0,869.08469581604,tags="mainpage",fill="#FF0000",outline="")#psa1 feed
		canvas.create_rectangle(277.0,845.0094604492188,301.0,869.08469581604,tags=("psa1Feed","mainpage"),state="hidden",fill="#00FF00",outline="")#psa1 feed
		canvas.create_text(350.0,659.0,anchor="nw",text="FCV: ",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(279.0,741.257080078125,anchor="nw",text="PT-Inter1:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(266.0,700.1284790039062,anchor="nw",text="TC-RPSA1:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(287.0,782.3855590820312,anchor="nw",text="Flowrate:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(426.0,659.0,anchor="nw",text="999",tags=("AO-FCV1","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(426.0,700.1284790039062,anchor="nw",text="999",tags=("TC-RPSA1","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(426.0,741.257080078125,anchor="nw",text="999",tags=("PT-PSA1-Inter","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(426.0,782.3855590820312,anchor="nw",text="999",tags=("PSA1-Flow","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))

		#psa2
		canvas.create_rectangle(553.0,609.0,858.0,929.0,tags="mainpage",fill="#BFBFBF",outline="")
		canvas.create_text(652.0,611.0,anchor="nw",text="PSA2",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 40 * -1))
		canvas.create_text(645.0,886.0,anchor="nw",text="VFD Enable",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_rectangle(608.0,889.13720703125,632.0,914.2352466583252,tags="mainpage",fill="#FF0000",outline="") #psa2 enable
		canvas.create_rectangle(608.0,889.13720703125,632.0,914.2352466583252,tags=("psa2Enable","mainpage"),state="hidden",fill="#00FF00",outline="") #psa2 enable
		canvas.create_text(645.0,845.0,anchor="nw",text="Feed XV",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_rectangle(608.0,848.13720703125,632.0,873.2352466583252,tags="mainpage",fill="#FF0000",outline="")#psa2 feed
		canvas.create_rectangle(608.0,848.13720703125,632.0,873.2352466583252,tags=("psa2Feed","mainpage"),state="hidden",fill="#00FF00",outline="")#psa2 feed
		canvas.create_text(679.0,661.0,anchor="nw",text="FCV: ",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(606.0,746.7516479492188,anchor="nw",text="PT-Inter2:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(592.0,703.8757934570312,anchor="nw",text="TC-RPSA2:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(616.0,789.62744140625,anchor="nw",text="Flowrate:",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(755.0,661.0,anchor="nw",text="999",tags=("AO-FCV2","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(755.0,789.62744140625,anchor="nw",text="999",tags=("TC-RPSA2","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(755.0,703.8757934570312,anchor="nw",text="999",tags=("PT-PSA2-Inter","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))
		canvas.create_text(755.0,746.7516479492188,anchor="nw",text="999",tags=("PSA2-Flow","mainpage"),fill="#000000",font=("Inter ExtraBold", 28 * -1))

		#r50in
		canvas.create_rectangle(71.0,527.0,197.0,675.0,tags="mainpage",fill="#BFBFBF",outline="")
		canvas.create_text(84.0,538.0,anchor="nw",text="R050-in",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 24 * -1))
		canvas.create_text(113.0,589.0,anchor="nw",text="R050-1",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 20 * -1))
		canvas.create_rectangle(76.0,588.0,101.0,613.0,tags="mainpage",fill="#FF0000",outline="")#in1
		canvas.create_rectangle(76.0,588.0,101.0,613.0,tags=("r50in1","mainpage"),state="hidden",fill="#00FF00",outline="")#in1
		canvas.create_text(112.0,631.0,anchor="nw",text="R050-2",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 20 * -1))
		canvas.create_rectangle(76.0,630.0,101.0,655.0,tags="mainpage",fill="#FF0000",outline="")#in2
		canvas.create_rectangle(76.0,630.0,101.0,655.0,tags=("r50in2","mainpage"),state="hidden",fill="#00FF00",outline="")#in2

		#r50out
		canvas.create_rectangle(883.0,527.0,1009.0,675.0,tags="mainpage",fill="#BFBFBF",outline="")
		canvas.create_text(888.0,538.0,anchor="nw",text="R050-out",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 24 * -1))
		canvas.create_text(925.0,589.0,anchor="nw",text="R050-1",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 20 * -1))
		canvas.create_rectangle(888.0,588.0,913.0,613.0,tags="mainpage",fill="#FF0000",outline="")#out1
		canvas.create_rectangle(888.0,588.0,913.0,613.0,tags=("r50out1","mainpage"),state="hidden",fill="#00FF00",outline="")#out1
		canvas.create_text(924.0,631.0,anchor="nw",text="R050-2",tags="mainpage",fill="#000000",font=("Inter ExtraBold", 20 * -1))
		canvas.create_rectangle(888.0,630.0,913.0,655.0,tags="mainpage",fill="#FF0000",outline="")#out2
		canvas.create_rectangle(888.0,630.0,913.0,655.0,tags=("r50out2","mainpage"),state="hidden",fill="#00FF00",outline="")#out2

		canvas.create_rectangle(346.0,953.0,740.0,1080.0,fill="#BFBFBF",outline="")
		canvas.create_text(494.0,953.0,anchor="nw",text="FM-904",fill="#000000",font=("Inter ExtraBold", 24 * -1))
		canvas.create_text(370.0,986.0,anchor="nw",text="Flow:",fill="#000000",font=("Inter ExtraBold", 20 * -1))
		canvas.create_text(428.0,987.0,anchor="nw",text="999.999",tags=("FM-FM904","mainpage"),fill="#000000",font=("Inter ExtraBold", 20 * -1))
		canvas.create_text(563.0,986.0,anchor="nw",text="Temp:",fill="#000000",font=("Inter ExtraBold", 20 * -1))
		canvas.create_text(629.0,987.0,anchor="nw",text="999.999",tags=("FM-TC904","mainpage"),fill="#000000",font=("Inter ExtraBold", 20 * -1))
		canvas.create_text(450.0,1016.0,anchor="nw",text="Pressure:",fill="#000000",font=("Inter ExtraBold", 20 * -1))
		canvas.create_text(549.0,1017.0,anchor="nw",text="999.999",tags=("FM-PT904","mainpage"),fill="#000000",font=("Inter ExtraBold", 20 * -1))
		
		canvas.create_rectangle(310.0,242,770.0,882.0,tags="lsrPage",fill="#F0F0F0",state="hidden",outline="red",width=10)
		canvas.create_text(540.0,285,anchor="center",text="  Error(s) Detected  ",tags="lsrPage",state="hidden",fill="#000000",font=("Inter ExtraBold", 50 * -1))
		canvas.create_line(400,310,685,310,width=5,tags="lsrPage",state="hidden",fill="#000000")
		canvas.create_rectangle(0,900,1080,970,tags="lsrPage",fill="orange",outline="black",state="hidden",width=10)
		canvas.create_text(540.0,935,anchor="center",text="Press red button to reset Errors",tags=("lsrPage","LSRwarning"),fill="#000000",state="hidden",font=("Inter ExtraBold", 40 * -1))
		for i in range(10):
			canvas.create_text(540.0,i*60+345,anchor="center",text="",tags=("lsrData","lsrPage","lsrRow"+str(i)),state="hidden",fill="#000000",font=("Inter Medium", 40 * -1))
		


		clock = StringVar()
		date = StringVar()
		clockLabel = Label(window, bg='#C3C3C3',textvariable=clock)
		clockLabel.place(anchor="nw", x=778, y=186)
		clockLabel.configure(font="{Inter} 16 {}")
		canvas.create_text(540.0,215,anchor="center",text=getserial(),tags=("serial","header"),fill="#000000",font=("Inter ExtraBold", 14 * -1))
		dateLabel = Label(window, bg='#C3C3C3',textvariable=date)
		dateLabel.place(anchor="nw", x=186, y=186)
		dateLabel.configure(font="{Inter} 16 {}")

		#canvas.create_text(540,1020,anchor="center",text="E100",tags="E100Num",fill="#000000",font=("Inter ExtraBold", 50 * -1))
		canvas.tag_raise("outerCircle")
		
		
		while True:
			signalStrength()
			
			now = datetime.datetime.now()
			today = datetime.datetime.today()
			date.set(today.strftime("%B %d, %Y"))
			clock.set(now.strftime("%H:%M:%S"))
			data = []
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
							ln = line.strip().split(",")
							data = [eval(i) for i in ln]
							if not data:
								continue
							if not len(data) == 100:
								raise Exception("Data Mismatch")
			except Exception as e:
				print(e)
				continue
			try:
				operating = data[94] << 16
				operating |= data[93]

				digitalInputs = data[4] << 16
				digitalInputs |= data[3]

				digitalOutputs = data[2] << 16
				digitalOutputs |= data[1]

				errorWord1 = data[90] << 16
				errorWord1 |= data[89]

				errorWord2 = data[92] << 16
				errorWord2 |= data[91]

			except:
				window.update()
				window.update_idletasks()
				continue

			for key in errors:
				if errors[key][0] == 2:
					errWrd = errorWord2
				else:
					errWrd = errorWord1
				errors[key][2] = bitRead(errWrd,errors[key][1])

			for dev in devices:
				devices[dev][1] = data[devices[dev][0]]

			#################################
			if errorMsg[0] == "2":
				displayState = 3
			# elif errorWord1 or errorWord2:
			# 	displayState = 1
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
				canvas.itemconfig("outerCircle", outline="red")
				j = 0
				for key in errors:
					if errors[key][2]:
						canvas.itemconfig("lsrRow"+str(j),state="normal",text=key)
						j += 1
				for i in range(j,10):
					canvas.itemconfig("lsrRow"+str(i),state="hidden",text="")
							
			elif displayState == 2:
				canvas.itemconfig("outerCircle", outline="green")
				try:
					for dev in devices:
						unit = ""
						if "PT" in dev:
							unit = "psi"
						elif "TC" in dev:
							unit = "C"
						elif "Flow" in dev or "FM" in dev:
							unit = "kg/d"
						elif "AO" in dev:
							unit = "%"

						if isinstance(devices[dev][1],float):
							canvas.itemconfig(dev,text="%.2f%s" % (devices[dev][1],unit))
						else:
							canvas.itemconfig(dev,text=str(devices[dev][1])+unit)
					canvas.itemconfig("heater",state=hide(bitRead(digitalOutputs,3)))
					canvas.itemconfig("cooler",state=hide(not bitRead(digitalOutputs,3)))
					canvas.itemconfig("evoEnable",state=hide(bitRead(digitalOutputs,9)))
					canvas.itemconfig("psa1Enable",state=hide(bitRead(digitalOutputs,27)))
					canvas.itemconfig("psa2Enable",state=hide(bitRead(digitalOutputs,28)))
					canvas.itemconfig("psa1Feed",state=hide(bitRead(digitalOutputs,23)))
					canvas.itemconfig("psa2Feed",state=hide(bitRead(digitalOutputs,24)))
					canvas.itemconfig("r50out1",state=hide(bitRead(digitalOutputs,15)))
					canvas.itemconfig("r50out2",state=hide(bitRead(digitalOutputs,16)))
					canvas.itemconfig("r50in1",state=hide(bitRead(digitalInputs,6)))
					canvas.itemconfig("r50in2",state=hide(bitRead(digitalInputs,7)))


				except ValueError:
					pass

			elif displayState == 3:
				canvas.itemconfig("BSOD_text",text=errorMsg)
				canvas.itemconfig("outerCircle", outline="blue")
			
			window.update()
			window.update_idletasks()
			time.sleep(0.5)

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
