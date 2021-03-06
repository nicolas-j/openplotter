#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
#
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import ConfigParser, subprocess, os, sys, time

home = os.path.expanduser('~')
pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

device=''
ssid=''
passw=''

try:
	boot_conf = ConfigParser.SafeConfigParser()
	boot_conf.read('/boot/config.txt')
	device=boot_conf.get('OPENPLOTTER', 'device')
	ssid=boot_conf.get('OPENPLOTTER', 'ssid')
	passw=boot_conf.get('OPENPLOTTER', 'pass')
except: pass

data_conf = ConfigParser.SafeConfigParser()
data_conf.read(currentpath+'/openplotter.conf')

if device and ssid and passw:
	data_conf.set('WIFI', 'enable', '1')
	data_conf.set('WIFI', 'device', device)
	data_conf.set('WIFI', 'ssid', ssid)
	data_conf.set('WIFI', 'password', passw)
	with open(currentpath+'/openplotter.conf', 'wb') as configfile:
		data_conf.write(configfile)

delay=int(data_conf.get('STARTUP', 'delay'))

kplex=data_conf.get('STARTUP', 'kplex')
opencpn=data_conf.get('STARTUP', 'opencpn')
opencpn_no=data_conf.get('STARTUP', 'opencpn_no_opengl')
opencpn_fullscreen=data_conf.get('STARTUP', 'opencpn_fullscreen')
x11vnc=data_conf.get('STARTUP', 'x11vnc')
gps_time=data_conf.get('STARTUP', 'gps_time')
signalk=data_conf.get('STARTUP', 'signalk')

enable=data_conf.get('AIS-SDR', 'enable')
gain=data_conf.get('AIS-SDR', 'gain')
ppm=data_conf.get('AIS-SDR', 'ppm')
channel=data_conf.get('AIS-SDR', 'channel')

wifi_server=data_conf.get('WIFI', 'enable')
wlan=data_conf.get('WIFI', 'device')
passw2=data_conf.get('WIFI', 'password')
ssid2=data_conf.get('WIFI', 'ssid')

nmea_mag_var=data_conf.get('STARTUP', 'nmea_mag_var')
nmea_hdt=data_conf.get('STARTUP', 'nmea_hdt')
nmea_hdg=data_conf.get('STARTUP', 'nmea_hdg')
nmea_heel=data_conf.get('STARTUP', 'nmea_heel')
nmea_press=data_conf.get('STARTUP', 'nmea_press')
nmea_temp_p=data_conf.get('STARTUP', 'nmea_temp_p')
nmea_hum=data_conf.get('STARTUP', 'nmea_hum')
nmea_temp_h=data_conf.get('STARTUP', 'nmea_temp_h')
nmea_rot=data_conf.get('STARTUP', 'nmea_rot')
nmea_eng_temp=data_conf.get('STARTUP', 'nmea_eng_temp')

TW_STW=data_conf.get('STARTUP', 'tw_stw')
TW_SOG=data_conf.get('STARTUP', 'tw_sog')

switch1=data_conf.get('SWITCH1', 'enable')
switch2=data_conf.get('SWITCH2', 'enable')
switch3=data_conf.get('SWITCH3', 'enable')
switch4=data_conf.get('SWITCH4', 'enable')

#######################################################
time.sleep(delay)

subprocess.call(['pkill', '-9', 'x11vnc'])
if x11vnc=='1':
	subprocess.Popen(['x11vnc', '-forever'])         

opencpn_commands=[]
opencpn_commands.append('opencpn')
if opencpn_no=='1': opencpn_commands.append('-no_opengl')
if opencpn_fullscreen=='1': opencpn_commands.append('-fullscreen')

if opencpn=='1' and len(opencpn_commands)>1: subprocess.Popen(opencpn_commands)
if opencpn=='1' and len(opencpn_commands)==1: subprocess.Popen('opencpn')

subprocess.call(['pkill', '-9', 'aisdecoder'])
subprocess.call(['pkill', '-9', 'rtl_fm'])
if enable=='1':
	frecuency='161975000'
	if channel=='b': frecuency='162025000'
	rtl_fm=subprocess.Popen(['rtl_fm', '-f', frecuency, '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
	aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)
	
if wifi_server=='1':
	subprocess.Popen(['sudo', 'python', currentpath+'/wifi_server.py', '1', wlan, passw2, ssid2])
else:
	subprocess.Popen(['sudo', 'python', currentpath+'/wifi_server.py', '0', wlan, passw2, ssid2])
	
time.sleep(16)

subprocess.call(['pkill', '-9', 'kplex'])
if kplex=='1':
	subprocess.Popen('kplex')        

subprocess.call(["pkill", '-9', "node"])
if signalk=='1':
	subprocess.Popen(home+'/.config/signalk-server-node/bin/nmea-from-10110', cwd=home+'/.config/signalk-server-node')       
	
if gps_time=='1':
	subprocess.call(['sudo', 'python', currentpath+'/time_gps.py'])

subprocess.call(['pkill', '-f', 'sensors.py'])
if nmea_hdg=='1' or nmea_heel=='1' or nmea_press=='1' or nmea_temp_p=='1' or nmea_hum=='1' or nmea_temp_h=='1': 
	subprocess.Popen(['python', currentpath+'/sensors.py'], cwd=currentpath+'/imu')

subprocess.call(['pkill', '-f', 'sensors_b.py'])
if nmea_eng_temp=='1': 
	subprocess.Popen(['python', currentpath+'/sensors_b.py'])

subprocess.call(['pkill', '-f', 'calculate.py'])
if nmea_mag_var=='1' or nmea_hdt=='1' or nmea_rot=='1' or TW_STW=='1' or TW_SOG=='1': 
	subprocess.Popen(['python', currentpath+'/calculate.py'])

subprocess.call(['sudo', 'pkill', '-f', 'switches.py'])
if switch1=='1' or switch2=='1' or switch3=='1' or switch4=='1':
	subprocess.Popen(['sudo', 'python', currentpath+'/switches.py'])