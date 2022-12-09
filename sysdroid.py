#!/data/data/com.termux/files/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import psutil
import signal
import os
from configparser import ConfigParser
from colorama import Fore, Back, Style
import subprocess

config = os.path.isfile(os.path.expanduser("~") + "/.config/sysdroid/sysdroid.cfg")
__ = os.system("clear")
print(Style.BRIGHT)

if os.geteuid() != 0: #Checking whether root user
	exit("App doesn't seem to be running as root \n Exiting.")

if config == False: #Creates config file if missing
	print("Config file not found. Generating one with default Values")

	os.system("mkdir -p ~/.config/sysdroid/")
	config = open(os.path.expanduser("~") + "/.config/sysdroid/sysdroid.cfg", "w+")

	config.write("[MAIN]\n\n")

	config.write ("CPU Name = Unspecified CPU\n")
	config.write ("GPU Name = Unspecified GPU\n")
	config.write ("Automatically get CPU and GPU name = 1\n\n")

	config.write ("CPU Temperature Probe = thermal_zone9\n")
	config.write ("GPU Temperature Probe = thermal_zone12\n")
	config.write ("Use Kernel battery Current Info = 1\n\n")

	config.write ("Progress Bar Length = 40\n")
	config.write ("Update Interval = 2\n")
	config.write ("Splash Screen = 1\n\n")

	config.close()

if True: #Loads Config File
	configfile = ConfigParser()
	configfile.read(os.path.expanduser("~") + "/.config/sysdroid/sysdroid.cfg")
	config = configfile["MAIN"]

	getcgpuname = int(config["Automatically get CPU and GPU name"])

	if getcgpuname != 1:
		cpu_name = str(config["CPU Name"])
		gpu_name = str(config["GPU Name"])

	cpu_probe = str(config["CPU Temperature Probe"])
	gpu_probe = str(config["GPU Temperature Probe"])
	kernelbat_mA = int(config["Use Kernel battery Current Info"])

	pslength = int(config["Progress Bar Length"])
	interval = int(config["Update Interval"])
	splash = int(config["Splash Screen"])

	 #Checks whether loaded probe files exist.

	if os.path.isfile(f"/sys/class/thermal/{cpu_probe}/temp") == False:
		print( Fore.RED + "Thermal Probe for CPU not found",\
			Fore.GREEN + f"	(/sys/class/thermal/{cpu_probe}/temp)")
		print(Fore.RED + "Check the sysdroid.cfg file.",\
		 	Style.RESET_ALL + "Program Exiting.")
		exit(1)
	
	if os.path.isfile(f"/sys/class/thermal/{gpu_probe}/temp") == False:
		print( Fore.RED + "Thermal Probe for CPU not found",\
		 	Fore.GREEN + f"	(/sys/class/thermal/{gpu_probe}/temp)")
		print(Fore.RED + "Check the sysdroid.cfg file.",\
		 	Style.RESET_ALL + "Program Exiting.")
		exit()
	



#Initializing all required Variables
t_update = 0
y = 0
w2s = 0
w10s = 0
w10 = 0
sleepintv = interval / 10

if kernelbat_mA == 0: #In the case user wants manual Battery Current calculation.
	w2s = 0
	w10s = 0
	w10 = 0

if splash == 1:
	print(Fore.GREEN + "sysdroid", Fore.CYAN + " - alou S", Fore.YELLOW + "	(https://github.com/alou-S) \n" + Fore.WHITE)
	print("A simple Python program to display CPU, GPU and Battery info on an Android device via Termux.")
	print("You can check the sysdroid.cfg file for changing the programs configuration. \n\n")

	if config == False:
		print(Back.RED + "Warning : Config File not found. Using default values.\n\n" + Back.RESET)

	input("Press Enter to continue...")



#Opening required files
pcpu_t = open(f"/sys/class/thermal/{cpu_probe}/temp", "r")

pbat_u = open("/sys/class/power_supply/battery/capacity", "r")
pbat_v = open("/sys/class/power_supply/battery/voltage_now", "r")
pbat_mAH = open("/sys/class/power_supply/battery/charge_counter", "r")
pbat_t = open("/sys/class/power_supply/battery/temp", "r")
pbat_mA = open("/sys/class/power_supply/battery/current_now", "r")

pgpu_u = open("/sys/kernel/gpu/gpu_busy", "r")
pgpu_t = open(f"/sys/class/thermal/{gpu_probe}/temp", "r")
pgpu_c = open("/sys/kernel/gpu/gpu_clock", "r")

cc = len(psutil.cpu_percent(percpu=True)) #This gets the number of CPU Cores

temp = 0
while temp != cc: #Simple Loop to detect all CPU cores in sysfs
	globals()[f"pcpu_c{temp}"] = \
		open(f"/sys/devices/system/cpu/cpu{temp}/cpufreq/cpuinfo_cur_freq", "r")
	temp += 1

if getcgpuname == 1:
	temp = open("/proc/cpuinfo", "r")
	#Yes there are better ways to filter out the unneeded stuff, But I was really lazy
	cpu_name = temp.readlines()[-1].replace("Technologies", "").\
	replace("Hardware", "").replace(":", "").replace(",", "").\
	replace("Inc", "").replace("\t ", "").replace("\t", "").\
	replace("\n", "").replace("  ", "")
	temp.close()

	gpu_name = str(subprocess.check_output("dumpsys SurfaceFlinger | grep GLES",\
		shell=True).decode("utf-8")).replace("GLES: ", "").replace(",", "").\
			replace("  ", " ").split("OpenGL", 1)[0]

def KBInterruptHandler(signal, frame): #Function that is called on Interrupt Signal
	print(f"KeyboardInterrupt (ID: {signal}) has been caught. Closing...")
	exit(0)

def mkpstring(rawval): #Function that generates the Percentage Progress Bar.
	val = int(rawval/100 * pslength)

	if rawval>0 and rawval<(100/pslength):
		val=1

	pstring=Fore.YELLOW + "[" + Fore.BLUE
	pstring+= "|" * val
	pstring+= " " * (pslength - val)
	pstring += Fore.YELLOW + "]  " + Fore.CYAN + \
		str(rawval) + "%" + Fore.WHITE
	return pstring

def printcgpu():

	global superchar

	if(cpu_t < 35):
		tempcolor = Fore.CYAN
	elif(cpu_t < 50):
		tempcolor = Fore.GREEN
	elif(cpu_t < 60):
		tempcolor = Fore.YELLOW
	elif(cpu_t > 59):
		tempcolor = Fore.RED

	superchar += Fore.GREEN + cpu_name
	superchar += Fore.CYAN + f" {psutil.cpu_percent()}% "
	superchar += tempcolor + str(cpu_t) + "°C \n"
	temp = 0

	while temp != cc:
		superchar += Fore.GREEN + "CPU"
		superchar += str(temp + 1)
		superchar += Fore.YELLOW + " @ "
		superchar += Fore.CYAN + str(globals()[f"cpu_c{temp}"]) + "MHz	"
		superchar += mkpstring(usage[temp]) + "\n"
		temp += 1

	superchar += ("\n\n")

	if(gpu_t < 35):
		tempcolor = Fore.CYAN
	elif(gpu_t < 50):
		tempcolor = Fore.GREEN
	elif(gpu_t < 60):
		tempcolor = Fore.YELLOW
	elif(gpu_t > 59):
		tempcolor = Fore.RED

	superchar += Fore.GREEN + gpu_name + tempcolor + str(gpu_t) + "°C \n"
	superchar += Fore.CYAN + str(gpu_c) + "MHz	" + mkpstring(gpu_u)

def printmem():
	global superchar

	superchar += Fore.GREEN + "Memory	" + mkpstring(psutil.virtual_memory()[2])
	superchar += "\n"
	superchar += Fore.GREEN + "Swap	" + mkpstring(psutil.swap_memory()[3])

def printbat():
	global superchar

	superchar += Fore.GREEN + "Battery	" + mkpstring(bat_u) + "\n"
	superchar += Fore.CYAN + str(bat_v / 1000) + "mV \n"

	if(bat_t < 27):
		tempcolor = Fore.CYAN
	elif(bat_t < 35):
		tempcolor = Fore.GREEN
	elif(bat_t < 45):
		tempcolor = Fore.YELLOW
	elif(bat_t > 44):
		tempcolor = Fore.RED

	if kernelbat_mA == 0:
		superchar += str(w2) + " mA" + str(w10) + plusplus + " mA"
		superchar += str(int(w2 * bat_v / 1000000)) + " mW" + \
			str(int(w10 * bat_v / 1000000)) + plusplus + " mW"

		superchar += str(bat_mAH / 1000) + " mAH"
		superchar += tempcolor + str(bat_t) + "°C"
	else :
		superchar += Fore.CYAN + str(int(bat_mA / 1000)) + plusplus + " mA \n"
		superchar += str(int(bat_mA * bat_v / 1000000000)) + plusplus + " mW \n"
		superchar += str(bat_mAH / 1000) + " mAH \n"
		superchar += tempcolor + str(bat_t) + "°C \n"

def reloadall(): #Syncs all file pointer values to variables each cycle
	global cpu_t
	global bat_u
	global bat_v
	global bat_mAH
	global bat_t
	global bat_mA
	global gpu_u
	global gpu_t
	global gpu_c
	global plusplus #This is basically used as a Charging Indicator
	global usage

	temp = 0
	while temp != cc: #Simple loop to update all CPU frequency values
		globals()[f"cpu_c{temp}"] =  int( int(globals()[f"pcpu_c{temp}"]\
			.read()) / 1000 )
		temp += 1
	cpu_t = int(pcpu_t.read()) / 1000
	usage = psutil.cpu_percent(percpu=True) #Updates CPU usage value

	#Battery Values Update
	if int(pbat_mA.read()) > 0: #This checks whether battery is charging and changes plusplus value
		plusplus = Fore.YELLOW + "++" + Fore.CYAN
	else:
		plusplus = ""
	pbat_mA.seek(0)

	bat_u = int(pbat_u.read())
	bat_v = int(pbat_v.read())
	bat_mAH = int(pbat_mAH.read())
	bat_t = int(pbat_t.read()) / 10
	bat_mA = abs(int(pbat_mA.read()))

	#GPU Values Update
	gpu_u = int( pgpu_u.read().replace("%", "") )
	gpu_t = int(pgpu_t.read()) / 1000
	gpu_c = int(pgpu_c.read())

	temp = 0
	while temp != cc:
	    globals()[f"pcpu_c{temp}"].seek(0)
	    temp += 1


	#Seek all file pointers
	pcpu_t.seek(0)

	pbat_mAH.seek(0)
	pbat_v.seek(0)
	pbat_u.seek(0)
	pbat_t.seek(0)
	pbat_mA.seek(0)

	pgpu_t.seek(0)
	pgpu_u.seek(0)
	pgpu_c.seek(0)

def calcbat_mA(): #This is for calculating battery Current based on Battery Charge Values
	global w2
	global w10
	global w2s
	global w10s
	#w2 is the 2 second average and w10 is the 10 second average
	w2 = int( (w2s - bat_mAH) * 1.8)
	w2s = bat_mAH
	if t_update != y and t_update % 5 == 0:
		w10 = int((w10s - w2s) * 0.36)
		w10s = w2s


while True:
	t = int( (time.time() * 100) / (interval * 100) )
	if t != t_update:
		t_update = t

		reloadall()

		if kernelbat_mA == 0:
			calcbat_mA()

		superchar = ""
		printcgpu()
		superchar += ("\n\n")
		printmem()
		superchar += ("\n\n")
		printbat()
		_ = os.system("clear")
		print(superchar)

	signal.signal(signal.SIGINT, KBInterruptHandler)
	time.sleep(sleepintv)

