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

import wx, socket, threading, time, webbrowser
from classes.datastream import DataStream
from classes.paths import Paths
from classes.conf import Conf
from classes.language import Language
import RPi.GPIO as GPIO


class MyFrame(wx.Frame):
		
		def __init__(self, parent):

			paths=Paths()
			self.currentpath=paths.currentpath

			self.conf=Conf()

			Language(self.conf.get('GENERAL','lang'))

			GPIO.setmode(GPIO.BCM)
			GPIO.setwarnings(False)

			wx.Frame.__init__(self, parent, title="Inspector", size=(650,435))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(650,150), pos=(0,0))

			self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(540, 220), pos=(5, 155))
			self.list.InsertColumn(0, _('Type'), width=205)
			self.list.InsertColumn(1, _('Value'), width=130)
			self.list.InsertColumn(2, _('Source'), width=90)
			self.list.InsertColumn(3, _('NMEA'), width=50)
			self.list.InsertColumn(4, _('Age'), width=59)

			self.button_pause =wx.Button(self, label=_('Pause'), pos=(555, 160))
			self.Bind(wx.EVT_BUTTON, self.pause, self.button_pause)

			self.button_reset =wx.Button(self, label=_('Reset'), pos=(555, 200))
			self.Bind(wx.EVT_BUTTON, self.reset, self.button_reset)

			self.button_nmea =wx.Button(self, label=_('NMEA info'), pos=(555, 240))
			self.Bind(wx.EVT_BUTTON, self.nmea_info, self.button_nmea)

			self.reset(0)

			self.pause_all=0

			self.CreateStatusBar()

			self.Centre()

			self.Show(True)

			self.thread1=threading.Thread(target=self.parse_data)
			self.thread2=threading.Thread(target=self.refresh_loop)
			
			self.s2=''
			self.error=''
			self.frase_nmea_log=''
			self.data=[]

			if not self.thread1.isAlive(): self.thread1.start()
			if not self.thread2.isAlive(): self.thread2.start()


		def check_switches(self):
			self.channel1=''
			self.channel2=''
			self.channel3=''
			self.channel4=''
			self.channel5=''
			self.channel6=''
			self.channel7=''
			self.channel8=''
			self.channel9=''
			self.channel10=''
			if self.conf.get('SWITCH1', 'enable')=='1':
				self.channel1=int(self.conf.get('SWITCH1', 'gpio'))
				pull_up_down=GPIO.PUD_DOWN
				if self.conf.get('SWITCH1', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
				GPIO.setup(self.channel1, GPIO.IN, pull_up_down=pull_up_down)
			if self.conf.get('SWITCH2', 'enable')=='1':
				self.channel2=int(self.conf.get('SWITCH2', 'gpio'))
				pull_up_down=GPIO.PUD_DOWN
				if self.conf.get('SWITCH2', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
				GPIO.setup(self.channel2, GPIO.IN, pull_up_down=pull_up_down)
			if self.conf.get('SWITCH3', 'enable')=='1':
				self.channel3=int(self.conf.get('SWITCH3', 'gpio'))
				pull_up_down=GPIO.PUD_DOWN
				if self.conf.get('SWITCH3', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
				GPIO.setup(self.channel3, GPIO.IN, pull_up_down=pull_up_down)
			if self.conf.get('SWITCH4', 'enable')=='1':
				self.channel4=int(self.conf.get('SWITCH4', 'gpio'))
				pull_up_down=GPIO.PUD_DOWN
				if self.conf.get('SWITCH4', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
				GPIO.setup(self.channel4, GPIO.IN, pull_up_down=pull_up_down)
			if self.conf.get('SWITCH5', 'enable')=='1':
				self.channel5=int(self.conf.get('SWITCH5', 'gpio'))
				pull_up_down=GPIO.PUD_DOWN
				if self.conf.get('SWITCH5', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
				GPIO.setup(self.channel5, GPIO.IN, pull_up_down=pull_up_down)
			if self.conf.get('SWITCH6', 'enable')=='1':
				self.channel6=int(self.conf.get('SWITCH6', 'gpio'))
				pull_up_down=GPIO.PUD_DOWN
				if self.conf.get('SWITCH6', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
				GPIO.setup(self.channel6, GPIO.IN, pull_up_down=pull_up_down)
			if self.conf.get('OUTPUT1', 'enable')=='1':
				self.channel7=int(self.conf.get('OUTPUT1', 'gpio'))
				GPIO.setup(self.channel7, GPIO.OUT)
			if self.conf.get('OUTPUT2', 'enable')=='1':
				self.channel8=int(self.conf.get('OUTPUT2', 'gpio'))
				GPIO.setup(self.channel8, GPIO.OUT)
			if self.conf.get('OUTPUT3', 'enable')=='1':
				self.channel9=int(self.conf.get('OUTPUT3', 'gpio'))
				GPIO.setup(self.channel9, GPIO.OUT)
			if self.conf.get('OUTPUT4', 'enable')=='1':
				self.channel10=int(self.conf.get('OUTPUT4', 'gpio'))
				GPIO.setup(self.channel10, GPIO.OUT)

 		# thread 1
		def connect(self):
			try:
				self.s2 = socket.socket()
				self.s2.connect(("localhost", 10110))
				self.s2.settimeout(5)
			except socket.error, error_msg:
				self.error= _('Failed to connect with localhost:10110. Error: ')+ str(error_msg[0])+_(', trying to reconnect...')
				self.s2=''
				time.sleep(7)
			else: self.error=''
			

		def parse_data(self):
			while True:
				if not self.s2: self.connect()
				else:
					frase_nmea=''
					try:
						frase_nmea = self.s2.recv(1024)
					except socket.error, error_msg:
						self.error= _('Connected with localhost:10110. Error: ')+ str(error_msg[0])+_(', waiting for data...')
					else:
						if frase_nmea and self.pause_all==0:
							self.a.parse_nmea(frase_nmea)
							self.frase_nmea_log+=frase_nmea
							self.error = _('Connected with localhost:10110.')
						else:
							self.s2=''
		# end thread 1

		# thread 2
		def refresh_loop(self):
			while True:	
				if self.pause_all==0:

					if self.channel1:
						if GPIO.input(self.channel1):
							self.a.DataList[self.a.getDataListIndex('SW1')][2]=1
							self.a.DataList[self.a.getDataListIndex('SW1')][4]=time.time()
						else:
							self.a.DataList[self.a.getDataListIndex('SW1')][2]=0
							self.a.DataList[self.a.getDataListIndex('SW1')][4]=time.time()
					if self.channel2:
						if GPIO.input(self.channel2):
							self.a.DataList[self.a.getDataListIndex('SW2')][2]=1
							self.a.DataList[self.a.getDataListIndex('SW2')][4]=time.time()
						else:
							self.a.DataList[self.a.getDataListIndex('SW2')][2]=0
							self.a.DataList[self.a.getDataListIndex('SW2')][4]=time.time()
					if self.channel3:
						if GPIO.input(self.channel3):
							self.a.DataList[self.a.getDataListIndex('SW3')][2]=1
							self.a.DataList[self.a.getDataListIndex('SW3')][4]=time.time()
						else:
							self.a.DataList[self.a.getDataListIndex('SW3')][2]=0
							self.a.DataList[self.a.getDataListIndex('SW3')][4]=time.time()
					if self.channel4:
						if GPIO.input(self.channel4):
							self.a.DataList[self.a.getDataListIndex('SW4')][2]=1
							self.a.DataList[self.a.getDataListIndex('SW4')][4]=time.time()
						else:
							self.a.DataList[self.a.getDataListIndex('SW4')][2]=0
							self.a.DataList[self.a.getDataListIndex('SW4')][4]=time.time()
					if self.channel5:
						if GPIO.input(self.channel5):
							self.a.DataList[self.a.getDataListIndex('SW5')][2]=1
							self.a.DataList[self.a.getDataListIndex('SW5')][4]=time.time()
						else:
							self.a.DataList[self.a.getDataListIndex('SW5')][2]=0
							self.a.DataList[self.a.getDataListIndex('SW5')][4]=time.time()
					if self.channel6:
						if GPIO.input(self.channel6):
							self.a.DataList[self.a.getDataListIndex('SW6')][2]=1
							self.a.DataList[self.a.getDataListIndex('SW6')][4]=time.time()
						else:
							self.a.DataList[self.a.getDataListIndex('SW6')][2]=0
							self.a.DataList[self.a.getDataListIndex('SW6')][4]=time.time()
					if self.channel7:
						if GPIO.input(self.channel7):
							self.a.DataList[self.a.getDataListIndex('OUT1')][2]=1
							self.a.DataList[self.a.getDataListIndex('OUT1')][4]=time.time()
						else:
							self.a.DataList[self.a.getDataListIndex('OUT1')][2]=0
							self.a.DataList[self.a.getDataListIndex('OUT1')][4]=time.time()
					if self.channel8:
						if GPIO.input(self.channel8):
							self.a.DataList[self.a.getDataListIndex('OUT2')][2]=1
							self.a.DataList[self.a.getDataListIndex('OUT2')][4]=time.time()
						else:
							self.a.DataList[self.a.getDataListIndex('OUT2')][2]=0
							self.a.DataList[self.a.getDataListIndex('OUT2')][4]=time.time()
					if self.channel9:
						if GPIO.input(self.channel9):
							self.a.DataList[self.a.getDataListIndex('OUT3')][2]=1
							self.a.DataList[self.a.getDataListIndex('OUT3')][4]=time.time()
						else:
							self.a.DataList[self.a.getDataListIndex('OUT3')][2]=0
							self.a.DataList[self.a.getDataListIndex('OUT3')][4]=time.time()
					if self.channel10:
						if GPIO.input(self.channel10):
							self.a.DataList[self.a.getDataListIndex('OUT4')][2]=1
							self.a.DataList[self.a.getDataListIndex('OUT4')][4]=time.time()
						else:
							self.a.DataList[self.a.getDataListIndex('OUT4')][2]=0
							self.a.DataList[self.a.getDataListIndex('OUT4')][4]=time.time()

					index=0
					for i in self.a.DataList:
						timestamp=i[4]
						if timestamp:
							now=time.time()
							age=now-timestamp
							value=''
							unit=''
							talker=''
							sentence=''
							value=i[2]
							unit=i[3]
							talker=i[5]
							sentence=i[6]
							if talker=='OC': talker=_('Calculated')
							if talker=='OS': talker=_('Sensor')
							if unit: data = str(value)+' '+str(unit)
							else: data = str(value)
							self.data=[index,1,data]
							wx.CallAfter(self.refresh_data)
							time.sleep(0.001)
							if talker:
								self.data=[index,2,talker]
								wx.CallAfter(self.refresh_data)
								time.sleep(0.001)
							if sentence: 
								self.data=[index,3,sentence]
								wx.CallAfter(self.refresh_data)
								time.sleep(0.001)
							self.data=[index,4,str(round(age,1))]
							wx.CallAfter(self.refresh_data)
							time.sleep(0.001)
						index=index+1
					wx.CallAfter(self.refresh_data)
					time.sleep(0.001)
					
				else: time.sleep(0.001)
		# end thread 2

		def refresh_data(self):
			if self.data: self.list.SetStringItem(self.data[0],self.data[1],self.data[2])
			if self.frase_nmea_log: 
				self.logger.AppendText(self.frase_nmea_log)
				self.frase_nmea_log=''
			self.SetStatusText(self.error)

		def pause(self, e):
			if self.pause_all==0: 
				self.pause_all=1
				self.button_pause.SetLabel(_('Resume'))
			else: 
				self.pause_all=0
				self.button_pause.SetLabel(_('Pause'))

		def reset(self, e):
			self.pause_all=1
			self.list. DeleteAllItems()
			self.logger.SetValue('')
			time.sleep(1)
			self.conf.read()
			self.check_switches()
			self.a=DataStream(self.conf)
			index=0
			for i in self.a.DataList:
				data=i[0]
				self.list.InsertStringItem(index,data)
				index=index+1

			self.pause_all=0

		def nmea_info(self, e):
			url = self.currentpath+'/docs/NMEA.html'
			webbrowser.open(url,new=2)

app = wx.App(False)
frame = MyFrame(None)
app.MainLoop()