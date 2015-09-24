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

import sys, ConfigParser, os, socket, time, pynmea2, RTIMU, math, csv

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

data_conf = ConfigParser.SafeConfigParser()
data_conf.read(currentpath+'/openplotter.conf')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


if data_conf.get('STARTUP', 'nmea_hdg')=='1' or data_conf.get('STARTUP', 'nmea_heel')=='1':
	SETTINGS_FILE = "RTIMULib"
	s = RTIMU.Settings(SETTINGS_FILE)
	imu = RTIMU.RTIMU(s)
	imu.IMUInit()
	imu.setSlerpPower(0.02)
	imu.setGyroEnable(True)
	imu.setAccelEnable(True)
	imu.setCompassEnable(True)
	poll_interval = imu.IMUGetPollInterval()

if data_conf.get('STARTUP', 'nmea_press')=='1':
	SETTINGS_FILE2 = "RTIMULib2"
	s2 = RTIMU.Settings(SETTINGS_FILE2)
	pressure_val = RTIMU.RTPressure(s2)
	pressure_val.pressureInit()

if data_conf.get('STARTUP', 'press_temp_log')=='1':
	ifile  = open(currentpath+'/weather_log.csv', "r")
	reader = csv.reader(ifile)
	log_list = []
	for row in reader:
		log_list.append(row)
	ifile.close()
	if log_list: last_log=float(log_list[len(log_list)-1][0])
	else: last_log=0

heading_m=''
heel=''
pressure=''
temperature=''

tick=time.time()

while True:
	tick2=time.time()
# read IMU
	if data_conf.get('STARTUP', 'nmea_hdg')=='1' or data_conf.get('STARTUP', 'nmea_heel')=='1':
		if imu.IMURead():
			data = imu.getIMUData()
			fusionPose = data["fusionPose"]
			heading_m0=math.degrees(fusionPose[2])
			heel=math.degrees(fusionPose[0])
			if heading_m0<0:
				heading_m0=360+heading_m0
			heading_m=round(heading_m0,1)
		else:
			heading_m=''
			heel=''
		time.sleep(poll_interval*1.0/1000.0)

	# read Pressure
	if data_conf.get('STARTUP', 'nmea_press')=='1':
		read=pressure_val.pressureRead()
		if read:
			if (read[0]):
				pressure=read[1]
			if (read[2]):
				temperature=read[3]
		else:
			pressure=''
			temperature=''
	
	#GENERATE
	if tick2-tick > float(data_conf.get('STARTUP', 'nmea_rate_sen')):
		tick=time.time()
		# HDG
		if data_conf.get('STARTUP', 'nmea_hdg')=='1' and heading_m:
			hdg = pynmea2.HDG('OP', 'HDG', (str(heading_m),'','','',''))
			hdg1=str(hdg)
			hdg2=hdg1+"\r\n"
			sock.sendto(hdg2, ('localhost', 10110))
		# XDR			
		if data_conf.get('STARTUP', 'nmea_press')=='1' or data_conf.get('STARTUP', 'nmea_heel')=='1':
			list_tmp=[]
			if pressure and temperature:
				press=round(pressure/1000,4)
				list_tmp.append('P')
				list_tmp.append(str(press))
				list_tmp.append('B')
				list_tmp.append('PPRS')
				temp= round(temperature,1)
				list_tmp.append('C')
				list_tmp.append(str(temp))
				list_tmp.append('C')
				list_tmp.append('TPRS')
			if heel:
				list_tmp.append('A')
				list_tmp.append(str(heel))
				list_tmp.append('D')
				list_tmp.append('RIMS')

			xdr = pynmea2.XDR('OP', 'XDR', (list_tmp))
			xdr1=str(xdr)
			xdr2=xdr1+"\r\n"
			sock.sendto(xdr2, ('localhost', 10110))
		# log temperature pressure
		if data_conf.get('STARTUP', 'press_temp_log')=='1' and pressure and temperature:
			if tick-last_log > 300:
				last_log=tick
				new_row=[tick,pressure,temperature]
				if len(log_list) < 288:
					log_list.append(new_row)
					ofile = open(currentpath+'/weather_log.csv', "a")
					writer = csv.writer(ofile)
					writer.writerow(new_row)
				if len(log_list) >= 288:
					del log_list[0]
					log_list.append(new_row)
					ofile = open(currentpath+'/weather_log.csv', "w")
					writer = csv.writer(ofile)
					for row in log_list:
						writer.writerow(row)
				ofile.close()
