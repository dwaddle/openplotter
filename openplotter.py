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

import wx, sys, os, subprocess, webbrowser, re
import wx.lib.scrolledpanel as scrolled
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from classes.datastream import DataStream
from classes.actions import Actions
from classes.paths import Paths
from classes.conf import Conf
from classes.language import Language
from classes.add_trigger import addTrigger
from classes.add_action import addAction
from classes.add_DS18B20 import addDS18B20

paths=Paths()
home=paths.home
currentpath=paths.currentpath

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(565, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class MainFrame(wx.Frame):
####layout###################
	def __init__(self):
		wx.Frame.__init__(self, None, title="OpenPlotter", size=(700,450))

		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

########reading configuration###################
		self.conf=Conf()
		self.language=self.conf.get('GENERAL','lang')
		Language(self.language)
##########################language
		self.p = scrolled.ScrolledPanel(self, -1, style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
		self.p.SetAutoLayout(1)
		self.p.SetupScrolling()
		self.nb = wx.Notebook(self.p)

		self.page1 = wx.Panel(self.nb)
		self.page2 = wx.Panel(self.nb)
		self.page3 = wx.Panel(self.nb)
		self.page4 = wx.Panel(self.nb)
		self.page5 = wx.Panel(self.nb)
		self.page6 = wx.Panel(self.nb)
		self.page7 = wx.Panel(self.nb)
		self.page8 = wx.Panel(self.nb)
		self.page9 = wx.Panel(self.nb)
		self.page10 = wx.Panel(self.nb)
		self.page11 = wx.Panel(self.nb)
		self.page12 = wx.Panel(self.nb)

		self.nb.AddPage(self.page5, _('NMEA 0183'))
		self.nb.AddPage(self.page3, _('WiFi AP'))
		self.nb.AddPage(self.page10, _('Actions'))
		self.nb.AddPage(self.page8, _('Switches'))
		self.nb.AddPage(self.page6, _('I2C sensors'))
		self.nb.AddPage(self.page11, _('1W sensors'))
		self.nb.AddPage(self.page12, _('SPI sensors'))
		self.nb.AddPage(self.page4, _('SDR-AIS'))
		self.nb.AddPage(self.page2, _('Calculate'))
		self.nb.AddPage(self.page9, _('Accounts'))
		self.nb.AddPage(self.page7, _('Signal K (beta)'))
		self.nb.AddPage(self.page1, _('Startup'))

		sizer = wx.BoxSizer()
		sizer.Add(self.nb, 1, wx.EXPAND)
		self.p.SetSizer(sizer)

		self.icon = wx.Icon(currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		self.CreateStatusBar()
		self.Centre()
########menu###################
		self.menubar = wx.MenuBar()

		self.settings = wx.Menu()
		self.time_item1 = self.settings.Append(wx.ID_ANY, _('Set time zone'), _('Set time zone in the new window'))
		self.Bind(wx.EVT_MENU, self.time_zone, self.time_item1)
		self.time_item2 = self.settings.Append(wx.ID_ANY, _('Set time from NMEA'), _('Set system time from NMEA data'))
		self.Bind(wx.EVT_MENU, self.time_gps, self.time_item2)
		self.settings.AppendSeparator()
		self.gpsd_item1 = self.settings.Append(wx.ID_ANY, _('Set GPSD'), _('Set GPSD in the new window'))
		self.Bind(wx.EVT_MENU, self.reconfigure_gpsd, self.gpsd_item1)
		self.menubar.Append(self.settings, _('Settings'))

		self.lang = wx.Menu()
		self.lang_item1 = self.lang.Append(wx.ID_ANY, _('English'), _('Set English language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_en, self.lang_item1)
		self.lang_item2 = self.lang.Append(wx.ID_ANY, _('Catalan'), _('Set Catalan language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_ca, self.lang_item2)
		self.lang_item3 = self.lang.Append(wx.ID_ANY, _('Spanish'), _('Set Spanish language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_es, self.lang_item3)
		self.lang_item4 = self.lang.Append(wx.ID_ANY, _('French'), _('Set French language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_fr, self.lang_item4)

		self.lang_item5 = self.lang.Append(wx.ID_ANY, _('Dutch'), _('Set Dutch language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_nl, self.lang_item5)
		self.menubar.Append(self.lang, _('Language'))

		self.helpm = wx.Menu()
		self.helpm_item1=self.helpm.Append(wx.ID_ANY, _('&About'), _('About OpenPlotter'))
		self.Bind(wx.EVT_MENU, self.OnAboutBox, self.helpm_item1)
		self.helpm_item2=self.helpm.Append(wx.ID_ANY, _('OpenPlotter online documentation'), _('OpenPlotter online documentation'))
		self.Bind(wx.EVT_MENU, self.op_doc, self.helpm_item2)
		self.helpm_item3=self.helpm.Append(wx.ID_ANY, _('OpenPlotter online guides'), _('OpenPlotter online guides'))
		self.Bind(wx.EVT_MENU, self.op_guides, self.helpm_item3)
		self.menubar.Append(self.helpm, _('&Help'))

		self.SetMenuBar(self.menubar)
###########################menu
########page1###################
		wx.StaticBox(self.page1, size=(330, 50), pos=(10, 10))
		wx.StaticText(self.page1, label=_('Delay (seconds)'), pos=(20, 30))
		self.delay = wx.TextCtrl(self.page1, -1, size=(55, 32), pos=(170, 23))
		self.button_ok_delay =wx.Button(self.page1, label=_('Ok'),size=(70, 32), pos=(250, 23))
		self.Bind(wx.EVT_BUTTON, self.ok_delay, self.button_ok_delay)

		wx.StaticBox(self.page1, size=(330, 230), pos=(10, 65))
		self.startup_opencpn = wx.CheckBox(self.page1, label=_('OpenCPN'), pos=(20, 80))
		self.startup_opencpn.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_opencpn_nopengl = wx.CheckBox(self.page1, label=_('no OpenGL'), pos=(40, 105))
		self.startup_opencpn_nopengl.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_opencpn_fullscreen = wx.CheckBox(self.page1, label=_('fullscreen'), pos=(40, 130))
		self.startup_opencpn_fullscreen.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_multiplexer = wx.CheckBox(self.page1, label=_('NMEA 0183 multiplexer'), pos=(20, 165))
		self.startup_multiplexer.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_nmea_time = wx.CheckBox(self.page1, label=_('Set time from NMEA'), pos=(40, 190))
		self.startup_nmea_time.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_remote_desktop = wx.CheckBox(self.page1, label=_('VNC remote desktop'), pos=(20, 225))
		self.startup_remote_desktop.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_signalk = wx.CheckBox(self.page1, label=_('Signal K server (beta)'), pos=(20, 260))
		self.startup_signalk.Bind(wx.EVT_CHECKBOX, self.startup)

###########################page1
########page2###################
		wx.StaticBox(self.page2, size=(330, 50), pos=(10, 10))
		wx.StaticText(self.page2, label=_('Rate (sec)'), pos=(20, 30))
		self.rate_list = ['0.1', '0.25', '0.5', '0.75', '1', '1.5', '2']
		self.rate2= wx.ComboBox(self.page2, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 32), pos=(150, 23))
		self.button_ok_rate2 =wx.Button(self.page2, label=_('Ok'),size=(70, 32), pos=(250, 23))
		self.Bind(wx.EVT_BUTTON, self.ok_rate2, self.button_ok_rate2)

		wx.StaticBox(self.page2, size=(330, 50), pos=(350, 10))
		wx.StaticText(self.page2, label=_('Accuracy (sec)'), pos=(360, 30))
		self.accuracy= wx.ComboBox(self.page2, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 32), pos=(500, 23))
		self.button_ok_accuracy =wx.Button(self.page2, label=_('Ok'),size=(70, 32), pos=(600, 23))
		self.Bind(wx.EVT_BUTTON, self.ok_accuracy, self.button_ok_accuracy)

		wx.StaticBox(self.page2, size=(330, 65), pos=(10, 65))
		self.mag_var = wx.CheckBox(self.page2, label=_('Magnetic variation'), pos=(20, 80))
		self.mag_var.Bind(wx.EVT_CHECKBOX, self.nmea_mag_var)
		wx.StaticText(self.page2, label=_('Generated NMEA: $OCHDG'), pos=(20, 105))

		wx.StaticBox(self.page2, size=(330, 65), pos=(10, 130))
		self.heading_t = wx.CheckBox(self.page2, label=_('True heading'), pos=(20, 145))
		self.heading_t.Bind(wx.EVT_CHECKBOX, self.nmea_hdt)
		wx.StaticText(self.page2, label=_('Generated NMEA: $OCHDT'), pos=(20, 170))

		wx.StaticBox(self.page2, size=(330, 65), pos=(10, 195))
		self.rot = wx.CheckBox(self.page2, label=_('Rate of turn'), pos=(20, 210))
		self.rot.Bind(wx.EVT_CHECKBOX, self.nmea_rot)
		wx.StaticText(self.page2, label=_('Generated NMEA: $OCROT'), pos=(20, 235))

		wx.StaticBox(self.page2, label=_(' True wind '), size=(330, 90), pos=(350, 65))
		self.TW_STW = wx.CheckBox(self.page2, label=_('Use speed log'), pos=(360, 80))
		self.TW_STW.Bind(wx.EVT_CHECKBOX, self.TW)
		self.TW_SOG = wx.CheckBox(self.page2, label=_('Use GPS'), pos=(360, 105))
		self.TW_SOG.Bind(wx.EVT_CHECKBOX, self.TW)
		wx.StaticText(self.page2, label=_('Generated NMEA: $OCMWV, $OCMWD'), pos=(360, 130))
###########################page2
########page3###################
		wx.StaticBox(self.page3, size=(400, 45), pos=(10, 10))
		self.wifi_enable = wx.CheckBox(self.page3, label=_('Enable WiFi access point'), pos=(20, 25))
		self.wifi_enable.Bind(wx.EVT_CHECKBOX, self.onwifi_enable)

		wx.StaticBox(self.page3, label=_(' Settings '), size=(400, 215), pos=(10, 60))
		
		self.available_wireless = []
		output=subprocess.check_output('iwconfig', stderr=subprocess.STDOUT)
		for i in range (0, 10):
			ii=str(i)
			if 'wlan'+ii in output: self.available_wireless.append('wlan'+ii)
		self.available_share = []
		self.available_share.append(_('none'))
		self.available_share.append('eth0')
		for i in self.available_wireless:
			self.available_share.append(i)
		self.wlan = wx.ComboBox(self.page3, choices=self.available_wireless, style=wx.CB_READONLY, size=(100, 32), pos=(20, 85))
		self.wlan_label=wx.StaticText(self.page3, label=_('AP WiFi device'), pos=(140, 90))

		self.ssid = wx.TextCtrl(self.page3, -1, size=(100, 32), pos=(20, 125))
		self.ssid_label=wx.StaticText(self.page3, label=_('SSID \nmaximum 32 characters'), pos=(140, 125))

		self.passw = wx.TextCtrl(self.page3, -1, size=(100, 32), pos=(20, 165))
		self.passw_label=wx.StaticText(self.page3, label=_('Password \nminimum 8 characters required'), pos=(140, 165))

		self.share = wx.ComboBox(self.page3, choices=self.available_share, style=wx.CB_READONLY, size=(100, 32), pos=(20, 205))
		self.share_label=wx.StaticText(self.page3, label=_('Internet connection to share'), pos=(140, 210))

		wx.StaticBox(self.page3, label=_(' Addresses '), size=(270, 265), pos=(415, 10))
		self.ip_info = wx.TextCtrl(self.page3, -1, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(260, 245), pos=(420, 25))
		self.ip_info.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		self.button_refresh_ip =wx.Button(self.page3, label=_('Refresh'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.show_ip_info, self.button_refresh_ip)
###########################page3
########page4###################
		wx.StaticBox(self.page4, size=(400, 45), pos=(10, 10))
		self.ais_sdr_enable = wx.CheckBox(self.page4, label=_('Enable AIS NMEA generation'), pos=(20, 25))
		self.ais_sdr_enable.Bind(wx.EVT_CHECKBOX, self.OnOffAIS)

		wx.StaticBox(self.page4, label=_(' Settings '), size=(400, 150), pos=(10, 60))

		self.gain = wx.TextCtrl(self.page4, -1, size=(55, 32), pos=(150, 80))
		self.gain_label=wx.StaticText(self.page4, label=_('Gain'), pos=(20, 85))
		self.ppm = wx.TextCtrl(self.page4, -1, size=(55, 32), pos=(150, 115))
		self.correction_label=wx.StaticText(self.page4, label=_('Correction (ppm)'), pos=(20, 120))

		self.ais_frequencies1 = wx.CheckBox(self.page4, label=_('Channel A 161.975Mhz'), pos=(220, 80))
		self.ais_frequencies1.Bind(wx.EVT_CHECKBOX, self.ais_frequencies)
		self.ais_frequencies2 = wx.CheckBox(self.page4, label=_('Channel B 162.025Mhz'), pos=(220, 115))
		self.ais_frequencies2.Bind(wx.EVT_CHECKBOX, self.ais_frequencies)

		self.button_test_gain =wx.Button(self.page4, label=_('Calibration'), pos=(275, 165))
		self.Bind(wx.EVT_BUTTON, self.test_gain, self.button_test_gain)
		self.button_test_ppm =wx.Button(self.page4, label=_('Take a look'), pos=(150, 165))
		self.Bind(wx.EVT_BUTTON, self.test_ppm, self.button_test_ppm)

		wx.StaticBox(self.page4, label=_(' Fine calibration using GSM base stations '), size=(400, 100), pos=(10, 215))
		self.bands_label=wx.StaticText(self.page4, label=_('Band'), pos=(20, 245))
		self.bands_list = ['GSM850', 'GSM-R', 'GSM900', 'EGSM', 'DCS', 'PCS']
		self.band= wx.ComboBox(self.page4, choices=self.bands_list, style=wx.CB_READONLY, size=(100, 32), pos=(150, 240))
		self.band.SetValue('GSM900')
		self.check_bands =wx.Button(self.page4, label=_('Check band'), pos=(275, 240))
		self.Bind(wx.EVT_BUTTON, self.check_band, self.check_bands)
		self.channel_label=wx.StaticText(self.page4, label=_('Channel'), pos=(20, 280))
		self.channel = wx.TextCtrl(self.page4, -1, size=(55, 32), pos=(150, 275))
		self.check_channels =wx.Button(self.page4, label=_('Fine calibration'), pos=(275, 275))
		self.Bind(wx.EVT_BUTTON, self.check_channel, self.check_channels)
###########################page4
########page5###################
		wx.StaticBox(self.page5, label=_(' Inputs '), size=(670, 130), pos=(10, 10))
		self.list_input = CheckListCtrl(self.page5, 102)
		self.list_input.SetPosition((15, 30))
		self.list_input.InsertColumn(0, _('Name'), width=130)
		self.list_input.InsertColumn(1, _('Type'), width=45)
		self.list_input.InsertColumn(2, _('Port/Address'), width=110)
		self.list_input.InsertColumn(3, _('Bauds/Port'))
		self.list_input.InsertColumn(4, _('Filter'))
		self.list_input.InsertColumn(5, _('Filtering'))
		self.add_serial_in =wx.Button(self.page5, label=_('+ serial'), pos=(585, 30))
		self.Bind(wx.EVT_BUTTON, self.add_serial_input, self.add_serial_in)

		self.add_network_in =wx.Button(self.page5, label=_('+ network'), pos=(585, 65))
		self.Bind(wx.EVT_BUTTON, self.add_network_input, self.add_network_in)

		self.button_delete_input =wx.Button(self.page5, label=_('delete'), pos=(585, 100))
		self.Bind(wx.EVT_BUTTON, self.delete_input, self.button_delete_input)

		wx.StaticBox(self.page5, label=_(' Outputs '), size=(670, 130), pos=(10, 145))
		self.list_output = CheckListCtrl(self.page5, 102)
		self.list_output.SetPosition((15, 165))
		self.list_output.InsertColumn(0, _('Name'), width=130)
		self.list_output.InsertColumn(1, _('Type'), width=45)
		self.list_output.InsertColumn(2, _('Port/Address'), width=110)
		self.list_output.InsertColumn(3, _('Bauds/Port'))
		self.list_output.InsertColumn(4, _('Filter'))
		self.list_output.InsertColumn(5, _('Filtering'))
		self.add_serial_out =wx.Button(self.page5, label=_('+ serial'), pos=(585, 165))
		self.Bind(wx.EVT_BUTTON, self.add_serial_output, self.add_serial_out)

		self.add_network_out =wx.Button(self.page5, label=_('+ network'), pos=(585, 200))
		self.Bind(wx.EVT_BUTTON, self.add_network_output, self.add_network_out)

		self.button_delete_output =wx.Button(self.page5, label=_('delete'), pos=(585, 235))
		self.Bind(wx.EVT_BUTTON, self.delete_output, self.button_delete_output)

		self.show_output =wx.Button(self.page5, label=_('Inspector'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output)
		self.restart =wx.Button(self.page5, label=_('Restart'), pos=(130, 285))
		self.Bind(wx.EVT_BUTTON, self.restart_multiplex, self.restart)
		self.advanced =wx.Button(self.page5, label=_('Advanced'), pos=(280, 285))
		self.Bind(wx.EVT_BUTTON, self.advanced_multiplex, self.advanced)
		self.button_apply =wx.Button(self.page5, label=_('Apply changes'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.apply_changes, self.button_apply)
		self.button_cancel =wx.Button(self.page5, label=_('Cancel changes'), pos=(430, 285))
		self.Bind(wx.EVT_BUTTON, self.cancel_changes, self.button_cancel)
###########################page5
########page7###################
		wx.StaticBox(self.page7, label=_(' Inputs '), size=(670, 130), pos=(10, 10))
		self.inSK = wx.TextCtrl(self.page7, -1, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(565, 102), pos=(15, 30))
		self.inSK.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
		self.inSK.SetValue(' NMEA 0183 - system_output  TCP  localhost  10110')

		wx.StaticBox(self.page7, label=_(' Outputs '), size=(670, 130), pos=(10, 145))
		self.outSK = wx.TextCtrl(self.page7, -1, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(565, 102), pos=(15, 165))
		self.outSK.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
		self.outSK.SetValue(' http://localhost:3000/instrumentpanel\n http://localhost:3000/sailgauge\n http://localhost:3000/signalk/stream/v1?stream=delta')
		self.showpanels =wx.Button(self.page7, label=_('Panel'), pos=(585, 165))
		self.Bind(wx.EVT_BUTTON, self.signalKpanels, self.showpanels)
		self.showgauge =wx.Button(self.page7, label=_('Gauge'), pos=(585, 200))
		self.Bind(wx.EVT_BUTTON, self.signalKsailgauge, self.showgauge)

		self.show_outputSK =wx.Button(self.page7, label=_('Show output'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.signalKout, self.show_outputSK)
		self.button_restartSK =wx.Button(self.page7, label=_('Restart'), pos=(130, 285))
		self.Bind(wx.EVT_BUTTON, self.restartSK, self.button_restartSK)
###########################page7
########page6###################
		wx.StaticBox(self.page6, size=(330, 50), pos=(10, 10))
		wx.StaticText(self.page6, label=_('Rate (sec)'), pos=(20, 30))
		self.rate= wx.ComboBox(self.page6, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 32), pos=(150, 23))
		self.button_ok_rate =wx.Button(self.page6, label=_('Ok'),size=(70, 32), pos=(250, 23))
		self.Bind(wx.EVT_BUTTON, self.ok_rate, self.button_ok_rate)

		wx.StaticBox(self.page6, label=_(' IMU '), size=(330, 140), pos=(10, 65))
		self.imu_tag=wx.StaticText(self.page6, label=_('Sensor detected: ')+_('none'), pos=(20, 85))
		self.button_reset_imu =wx.Button(self.page6, label=_('Reset'), pos=(240, 85))
		self.Bind(wx.EVT_BUTTON, self.reset_imu, self.button_reset_imu)
		self.button_calibrate_imu =wx.Button(self.page6, label=_('Calibrate'), pos=(240, 125))
		self.Bind(wx.EVT_BUTTON, self.calibrate_imu, self.button_calibrate_imu)
		self.heading = wx.CheckBox(self.page6, label=_('Heading'), pos=(20, 105))
		self.heading.Bind(wx.EVT_CHECKBOX, self.nmea_hdg)
		self.heading_nmea=wx.StaticText(self.page6, label=_('Generated NMEA: $OSHDG'), pos=(20, 130))
		self.heel = wx.CheckBox(self.page6, label=_('Heel'), pos=(20, 155))
		self.heel.Bind(wx.EVT_CHECKBOX, self.nmea_heel)
		self.heel_nmea=wx.StaticText(self.page6, label=_('Generated NMEA: $OSXDR'), pos=(20, 180))

		wx.StaticBox(self.page6, label=_(' Weather '), size=(330, 270), pos=(350, 10))
		self.press_tag=wx.StaticText(self.page6, label=_('Sensor detected: ')+_('none'), pos=(360, 30))
		self.button_reset_press_hum =wx.Button(self.page6, label=_('Reset'), pos=(580, 30))
		self.Bind(wx.EVT_BUTTON, self.reset_press_hum, self.button_reset_press_hum)
		self.press = wx.CheckBox(self.page6, label=_('Pressure'), pos=(360, 50))
		self.press.Bind(wx.EVT_CHECKBOX, self.nmea_press)
		self.temp_p = wx.CheckBox(self.page6, label=_('Temperature'), pos=(360, 75))
		self.temp_p.Bind(wx.EVT_CHECKBOX, self.nmea_temp_p)
		self.hum_tag=wx.StaticText(self.page6, label=_('Sensor detected: ')+_('none'), pos=(360, 105))
		self.hum = wx.CheckBox(self.page6, label=_('Humidity'), pos=(360, 125))
		self.hum.Bind(wx.EVT_CHECKBOX, self.nmea_hum)
		self.temp_h = wx.CheckBox(self.page6, label=_('Temperature'), pos=(360, 150))
		self.temp_h.Bind(wx.EVT_CHECKBOX, self.nmea_temp_h)

		self.press_nmea=wx.StaticText(self.page6, label=_('Generated NMEA: $OSXDR'), pos=(360, 180))

		self.press_temp_log = wx.CheckBox(self.page6, label=_('Weather data logging'), pos=(360, 210))
		self.press_temp_log.Bind(wx.EVT_CHECKBOX, self.enable_press_temp_log)
		self.button_reset =wx.Button(self.page6, label=_('Reset'), pos=(360, 240))
		self.Bind(wx.EVT_BUTTON, self.reset_graph, self.button_reset)
		self.button_graph =wx.Button(self.page6, label=_('Show'), pos=(475, 240))
		self.Bind(wx.EVT_BUTTON, self.show_graph, self.button_graph)
###########################page6
########page11###################

		wx.StaticBox(self.page11, label=_(' DS18B20 sensors '), size=(670, 265), pos=(10, 10))
		
		self.list_DS18B20 = CheckListCtrl(self.page11, 237)
		self.list_DS18B20.SetPosition((15, 30))
		self.list_DS18B20.InsertColumn(0, _('Name'), width=275)
		self.list_DS18B20.InsertColumn(1, _('Short'), width=60)
		self.list_DS18B20.InsertColumn(2, _('Unit'), width=40)
		self.list_DS18B20.InsertColumn(3, _('ID'))
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_DS18B20, self.list_DS18B20)
			
		self.add_DS18B20_button =wx.Button(self.page11, label=_('add'), pos=(585, 30))
		self.Bind(wx.EVT_BUTTON, self.add_DS18B20, self.add_DS18B20_button)

		self.delete_DS18B20_button =wx.Button(self.page11, label=_('delete'), pos=(585, 65))
		self.Bind(wx.EVT_BUTTON, self.delete_DS18B20, self.delete_DS18B20_button)

		self.button_apply_DS18B20 =wx.Button(self.page11, label=_('Apply changes'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.apply_changes_DS18B20, self.button_apply_DS18B20)
		self.button_cancel_DS18B20 =wx.Button(self.page11, label=_('Cancel changes'), pos=(430, 285))
		self.Bind(wx.EVT_BUTTON, self.cancel_changes_DS18B20, self.button_cancel_DS18B20)

###########################page11
########page12###################
		wx.StaticText(self.page12, label=_('Coming soon'), pos=(20, 30))
###########################page12
########page8###################
		self.pin_list = ['5', '6', '12', '13','16', '17', '18', '19','20', '21', '22', '23','24', '25', '26', '27']
		self.pull_list = ['Pull Down', 'Pull Up']

		wx.StaticBox(self.page8, label=_(' Switch 1 '), size=(330, 60), pos=(10, 10))
		self.switch1_enable = wx.CheckBox(self.page8, label=_('Enable'), pos=(20, 32))
		self.switch1_enable.Bind(wx.EVT_CHECKBOX, self.on_switch1_enable)
		wx.StaticText(self.page8, label=_('GPIO'), pos=(115, 35))
		self.gpio_pin1= wx.ComboBox(self.page8, choices=self.pin_list, style=wx.CB_READONLY, size=(60, 32), pos=(155, 27))
		self.gpio_pull1= wx.ComboBox(self.page8, choices=self.pull_list, style=wx.CB_READONLY, size=(105, 32), pos=(225, 27))

		wx.StaticBox(self.page8, label=_(' Switch 2 '), size=(330, 60), pos=(350, 10))
		self.switch2_enable = wx.CheckBox(self.page8, label=_('Enable'), pos=(360, 32))
		self.switch2_enable.Bind(wx.EVT_CHECKBOX, self.on_switch2_enable)
		wx.StaticText(self.page8, label=_('GPIO'), pos=(455, 35))
		self.gpio_pin2= wx.ComboBox(self.page8, choices=self.pin_list, style=wx.CB_READONLY, size=(60, 32), pos=(495, 27))
		self.gpio_pull2= wx.ComboBox(self.page8, choices=self.pull_list, style=wx.CB_READONLY, size=(105, 32), pos=(565, 27))
		
		wx.StaticBox(self.page8, label=_(' Switch 3 '), size=(330, 60), pos=(10, 75))
		self.switch3_enable = wx.CheckBox(self.page8, label=_('Enable'), pos=(20, 97))
		self.switch3_enable.Bind(wx.EVT_CHECKBOX, self.on_switch3_enable)
		wx.StaticText(self.page8, label=_('GPIO'), pos=(115, 100))
		self.gpio_pin3= wx.ComboBox(self.page8, choices=self.pin_list, style=wx.CB_READONLY, size=(60, 32), pos=(155, 92))
		self.gpio_pull3= wx.ComboBox(self.page8, choices=self.pull_list, style=wx.CB_READONLY, size=(105, 32), pos=(225, 92))
		
		wx.StaticBox(self.page8, label=_(' Switch 4 '), size=(330, 60), pos=(350, 75))
		self.switch4_enable = wx.CheckBox(self.page8, label=_('Enable'), pos=(360, 97))
		self.switch4_enable.Bind(wx.EVT_CHECKBOX, self.on_switch4_enable)
		wx.StaticText(self.page8, label=_('GPIO'), pos=(455, 100))
		self.gpio_pin4= wx.ComboBox(self.page8, choices=self.pin_list, style=wx.CB_READONLY, size=(60, 32), pos=(495, 92))
		self.gpio_pull4= wx.ComboBox(self.page8, choices=self.pull_list, style=wx.CB_READONLY, size=(105, 32), pos=(565, 92))

		wx.StaticBox(self.page8, label=_(' Switch 5 '), size=(330, 60), pos=(10, 140))
		self.switch5_enable = wx.CheckBox(self.page8, label=_('Enable'), pos=(20, 162))
		self.switch5_enable.Bind(wx.EVT_CHECKBOX, self.on_switch5_enable)
		wx.StaticText(self.page8, label=_('GPIO'), pos=(115, 165))
		self.gpio_pin5= wx.ComboBox(self.page8, choices=self.pin_list, style=wx.CB_READONLY, size=(60, 32), pos=(155, 157))
		self.gpio_pull5= wx.ComboBox(self.page8, choices=self.pull_list, style=wx.CB_READONLY, size=(105, 32), pos=(225, 157))
		
		wx.StaticBox(self.page8, label=_(' Switch 6 '), size=(330, 60), pos=(350, 140))
		self.switch6_enable = wx.CheckBox(self.page8, label=_('Enable'), pos=(360, 162))
		self.switch6_enable.Bind(wx.EVT_CHECKBOX, self.on_switch6_enable)
		wx.StaticText(self.page8, label=_('GPIO'), pos=(455, 165))
		self.gpio_pin6= wx.ComboBox(self.page8, choices=self.pin_list, style=wx.CB_READONLY, size=(60, 32), pos=(495, 157))
		self.gpio_pull6= wx.ComboBox(self.page8, choices=self.pull_list, style=wx.CB_READONLY, size=(105, 32), pos=(565, 157))

		wx.StaticBox(self.page8, label=_(' Output 1 '), size=(163, 67), pos=(10, 205))
		self.output1_enable = wx.CheckBox(self.page8, label=_('Enable'), pos=(20, 235))
		self.output1_enable.Bind(wx.EVT_CHECKBOX, self.on_output1_enable)
		wx.StaticText(self.page8, label=_('GPIO'), pos=(105, 217))
		self.gpio_pin7= wx.ComboBox(self.page8, choices=self.pin_list, style=wx.CB_READONLY, size=(60, 32), pos=(105, 235))

		wx.StaticBox(self.page8, label=_(' Output 2 '), size=(163, 67), pos=(179, 205))
		self.output2_enable = wx.CheckBox(self.page8, label=_('Enable'), pos=(189, 235))
		self.output2_enable.Bind(wx.EVT_CHECKBOX, self.on_output2_enable)
		wx.StaticText(self.page8, label=_('GPIO'), pos=(274, 217))
		self.gpio_pin8= wx.ComboBox(self.page8, choices=self.pin_list, style=wx.CB_READONLY, size=(60, 32), pos=(274, 235))
		
		wx.StaticBox(self.page8, label=_(' Output 3 '), size=(163, 67), pos=(348, 205))
		self.output3_enable = wx.CheckBox(self.page8, label=_('Enable'), pos=(358, 235))
		self.output3_enable.Bind(wx.EVT_CHECKBOX, self.on_output3_enable)
		wx.StaticText(self.page8, label=_('GPIO'), pos=(443, 217))
		self.gpio_pin9= wx.ComboBox(self.page8, choices=self.pin_list, style=wx.CB_READONLY, size=(60, 32), pos=(443, 235))
		
		wx.StaticBox(self.page8, label=_(' Output 4 '), size=(163, 67), pos=(517, 205))
		self.output4_enable = wx.CheckBox(self.page8, label=_('Enable'), pos=(527, 235))
		self.output4_enable.Bind(wx.EVT_CHECKBOX, self.on_output4_enable)
		wx.StaticText(self.page8, label=_('GPIO'), pos=(612, 217))
		self.gpio_pin10= wx.ComboBox(self.page8, choices=self.pin_list, style=wx.CB_READONLY, size=(60, 32), pos=(612, 235))

		self.button_apply_switches =wx.Button(self.page8, label=_('Apply changes'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.apply_changes_switches, self.button_apply_switches)
		self.button_cancel_switches =wx.Button(self.page8, label=_('Cancel changes'), pos=(430, 285))
		self.Bind(wx.EVT_BUTTON, self.cancel_changes_switches, self.button_cancel_switches)
###########################page8
########page9###################
		wx.StaticBox(self.page9, label=_(' Twitter '), size=(330, 290), pos=(10, 10))
		self.twitter_enable = wx.CheckBox(self.page9, label=_('Enable'), pos=(20, 32))
		self.twitter_enable.Bind(wx.EVT_CHECKBOX, self.on_twitter_enable)

		self.read_datastream()
		self.datastream_select = wx.ListBox(self.page9, choices=self.datastream_list, style=wx.LB_MULTIPLE, size=(310, 80), pos=(20, 65))
		wx.StaticText(self.page9, label=_('apiKey'), pos=(20, 160))
		self.apiKey = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(150, 155))
		wx.StaticText(self.page9, label=_('apiSecret'), pos=(20, 195))
		self.apiSecret = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(150, 190))
		wx.StaticText(self.page9, label=_('accessToken'), pos=(20, 230))
		self.accessToken = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(150, 225))
		wx.StaticText(self.page9, label=_('accessTokenSecret'), pos=(20, 265))
		self.accessTokenSecret = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(150, 260))

		wx.StaticBox(self.page9, label=_(' Gmail '), size=(330, 200), pos=(350, 10))
		self.gmail_enable = wx.CheckBox(self.page9, label=_('Enable'), pos=(360, 32))
		self.gmail_enable.Bind(wx.EVT_CHECKBOX, self.on_gmail_enable)
		wx.StaticText(self.page9, label=_('Gmail account'), pos=(360, 70))
		self.Gmail_account = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(490, 65))
		wx.StaticText(self.page9, label=_('Gmail password'), pos=(360, 105))
		self.Gmail_password = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(490, 100))
		wx.StaticText(self.page9, label=_('Recipient'), pos=(360, 140))
		self.Recipient = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(490, 135))
###########################page9
########page10###################
		wx.StaticBox(self.page10, label=_(' Triggers '), size=(670, 130), pos=(10, 10))
		
		self.list_triggers = CheckListCtrl(self.page10, 102)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.print_actions, self.list_triggers)
		self.list_triggers.SetPosition((15, 30))
		self.list_triggers.InsertColumn(0, _('trigger'), width=275)
		self.list_triggers.InsertColumn(1, _('operator'), width=170)
		self.list_triggers.InsertColumn(2, _('value'))
			
		self.add_trigger_button =wx.Button(self.page10, label=_('add'), pos=(585, 30))
		self.Bind(wx.EVT_BUTTON, self.add_trigger, self.add_trigger_button)

		self.delete_trigger_button =wx.Button(self.page10, label=_('delete'), pos=(585, 65))
		self.Bind(wx.EVT_BUTTON, self.delete_trigger, self.delete_trigger_button)

		wx.StaticBox(self.page10, label=_(' Actions '), size=(670, 130), pos=(10, 145))
		
		self.list_actions = wx.ListCtrl(self.page10, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(565, 102))
		self.list_actions.SetPosition((15, 165))
		self.list_actions.InsertColumn(0, _('action'), width=200)
		self.list_actions.InsertColumn(1, _('data'), width=220)
		self.list_actions.InsertColumn(2, _('repeat'), width=130)

		self.add_action_button =wx.Button(self.page10, label=_('add'), pos=(585, 165))
		self.Bind(wx.EVT_BUTTON, self.add_action, self.add_action_button)

		self.delete_action_button =wx.Button(self.page10, label=_('delete'), pos=(585, 200))
		self.Bind(wx.EVT_BUTTON, self.delete_action, self.delete_action_button)

		self.stop_all=wx.Button(self.page10, label=_('Stop all'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.stop_actions, self.stop_all)
		self.start_all=wx.Button(self.page10, label=_('Start all'), pos=(130, 285))
		self.Bind(wx.EVT_BUTTON, self.start_actions, self.start_all)

		self.button_apply_actions =wx.Button(self.page10, label=_('Apply changes'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.apply_changes_actions, self.button_apply_actions)
		self.button_cancel_actions =wx.Button(self.page10, label=_('Cancel changes'), pos=(430, 285))
		self.Bind(wx.EVT_BUTTON, self.cancel_changes_actions, self.button_cancel_actions)
###########################page10
		self.actions=Actions()
		self.manual_settings=''
		self.read_kplex_conf()
		self.set_layout_conf()
###########################layout

####definitions###################

	def read_datastream(self):
		self.datastream_list=[]
		self.a=DataStream(self.conf)
		for i in self.a.DataList:
			self.datastream_list.append(i[1]+': '+i[0])

	def set_layout_conf(self):
		if self.language=='en': self.lang.Check(self.lang_item1.GetId(), True)
		if self.language=='ca': self.lang.Check(self.lang_item2.GetId(), True)
		if self.language=='es': self.lang.Check(self.lang_item3.GetId(), True)
		if self.language=='fr': self.lang.Check(self.lang_item4.GetId(), True)
		if self.language=='nl': self.lang.Check(self.lang_item5.GetId(), True)

		self.delay.SetValue(self.conf.get('STARTUP', 'delay'))

		if self.conf.get('STARTUP', 'opencpn')=='1': 
			self.startup_opencpn.SetValue(True)
		else:
			self.startup_opencpn_nopengl.Disable()
			self.startup_opencpn_fullscreen.Disable()
		if self.conf.get('STARTUP', 'opencpn_no_opengl')=='1': self.startup_opencpn_nopengl.SetValue(True)
		if self.conf.get('STARTUP', 'opencpn_fullscreen')=='1': self.startup_opencpn_fullscreen.SetValue(True)
		if self.conf.get('STARTUP', 'kplex')=='1': 
			self.startup_multiplexer.SetValue(True)
		else:
			self.startup_nmea_time.Disable()
		if self.conf.get('STARTUP', 'gps_time')=='1': self.startup_nmea_time.SetValue(True)
		if self.conf.get('STARTUP', 'x11vnc')=='1': self.startup_remote_desktop.SetValue(True)
		if self.conf.get('STARTUP', 'signalk')=='1': self.startup_signalk.SetValue(True)

		if len(self.available_wireless)>0:
			self.wlan.SetValue(self.conf.get('WIFI', 'device'))
			self.ssid.SetValue(self.conf.get('WIFI', 'ssid'))
			if self.conf.get('WIFI', 'password'): self.passw.SetValue('**********')
			if self.conf.get('WIFI', 'share')=='0': self.share.SetValue( _('none'))
			else: self.share.SetValue(self.conf.get('WIFI', 'share'))
			if self.conf.get('WIFI', 'enable')=='1':
				self.wifi_enable.SetValue(True)
				self.wlan.Disable()
				self.passw.Disable()
				self.wlan_label.Disable()
				self.passw_label.Disable()
				self.ssid.Disable()
				self.ssid_label.Disable()
				self.share.Disable()
				self.share_label.Disable()
		else:
			self.wifi_enable.Disable()
			self.wlan.Disable()
			self.passw.Disable()
			self.wlan_label.Disable()
			self.passw_label.Disable()
			self.ssid.Disable()
			self.ssid_label.Disable()
			self.share.Disable()
			self.share_label.Disable()
		self.show_ip_info('')
		
		output=subprocess.check_output('lsusb')
		if 'DVB-T' in output:
			self.gain.SetValue(self.conf.get('AIS-SDR', 'gain'))
			self.ppm.SetValue(self.conf.get('AIS-SDR', 'ppm'))
			self.band.SetValue(self.conf.get('AIS-SDR', 'band'))
			self.channel.SetValue(self.conf.get('AIS-SDR', 'gsm_channel'))
			if self.conf.get('AIS-SDR', 'enable')=='1': 
				self.ais_sdr_enable.SetValue(True)
				self.disable_sdr_controls()
			if self.conf.get('AIS-SDR', 'channel')=='a': self.ais_frequencies1.SetValue(True)
			if self.conf.get('AIS-SDR', 'channel')=='b': self.ais_frequencies2.SetValue(True)
		else:
			self.ais_sdr_enable.Disable()
			self.disable_sdr_controls()
			self.button_test_gain.Disable()
			self.button_test_ppm.Disable()
			self.bands_label.Disable()
			self.channel_label.Disable()
			self.band.Disable()
			self.channel.Disable()
			self.check_channels.Disable()
			self.check_bands.Disable()

		self.rate.SetValue(self.conf.get('STARTUP', 'nmea_rate_sen'))
		self.rate2.SetValue(self.conf.get('STARTUP', 'nmea_rate_cal'))
		self.accuracy.SetValue(self.conf.get('STARTUP', 'cal_accuracy'))
		if self.conf.get('STARTUP', 'nmea_mag_var')=='1': self.mag_var.SetValue(True)
		if self.conf.get('STARTUP', 'nmea_hdt')=='1': self.heading_t.SetValue(True)
		if self.conf.get('STARTUP', 'nmea_rot')=='1': self.rot.SetValue(True)
		if self.conf.get('STARTUP', 'tw_stw')=='1': self.TW_STW.SetValue(True)
		if self.conf.get('STARTUP', 'tw_sog')=='1': self.TW_SOG.SetValue(True)

		detected=subprocess.check_output(['python', currentpath+'/imu/check_sensors.py'], cwd=currentpath+'/imu')
		l_detected=detected.split('\n')
		imu_sensor=l_detected[0]
		calibrated=l_detected[1]
		press_sensor=l_detected[2]
		hum_sensor=l_detected[3]

		if 'none' in imu_sensor:
			self.heading.Disable()
			self.button_calibrate_imu.Disable()
			self.heading_nmea.Disable()
			self.heel.Disable()
			self.heel_nmea.Disable()
			if self.conf.get('STARTUP', 'nmea_hdg')=='1' or self.conf.get('STARTUP', 'nmea_heel')=='1': 
				self.conf.set('STARTUP', 'nmea_hdg', '0')
				self.conf.set('STARTUP', 'nmea_heel', '0')
		else:
			self.imu_tag.SetLabel(_('Sensor detected: ')+imu_sensor)
			if calibrated=='1':self.button_calibrate_imu.Disable()
			if self.conf.get('STARTUP', 'nmea_hdg')=='1': self.heading.SetValue(True)
			if self.conf.get('STARTUP', 'nmea_heel')=='1': self.heel.SetValue(True)

		if 'none' in press_sensor:
			self.press.Disable()
			self.temp_p.Disable()
			if self.conf.get('STARTUP', 'nmea_press')=='1' or self.conf.get('STARTUP', 'nmea_temp_p')=='1': 
				self.conf.set('STARTUP', 'nmea_press', '0')
				self.conf.set('STARTUP', 'nmea_temp_p', '0')
		else:
			self.press_tag.SetLabel(_('Sensor detected: ')+press_sensor)
			if self.conf.get('STARTUP', 'nmea_press')=='1': self.press.SetValue(True)
			if self.conf.get('STARTUP', 'nmea_temp_p')=='1': self.temp_p.SetValue(True)

		if 'none' in hum_sensor:
			self.hum.Disable()
			self.temp_h.Disable()
			if self.conf.get('STARTUP', 'nmea_hum')=='1' or self.conf.get('STARTUP', 'nmea_temp_h')=='1': 
				self.conf.set('STARTUP', 'nmea_hum', '0')
				self.conf.set('STARTUP', 'nmea_temp_h', '0')
		else:
			self.hum_tag.SetLabel(_('Sensor detected: ')+hum_sensor)
			if self.conf.get('STARTUP', 'nmea_hum')=='1': self.hum.SetValue(True)
			if self.conf.get('STARTUP', 'nmea_temp_h')=='1': self.temp_h.SetValue(True)
		
		if 'none' in hum_sensor and 'none' in press_sensor: self.press_nmea.Disable()

		if self.conf.get('STARTUP', 'press_temp_log')=='1': self.press_temp_log.SetValue(True)

		if self.conf.get('TWITTER', 'send_data'):
			selections=eval(self.conf.get('TWITTER', 'send_data'))
			for i in selections:
				for index,item in enumerate(self.a.DataList):
					if i==item[9]: self.datastream_select.SetSelection(index)
		if self.conf.get('TWITTER', 'apiKey'): self.apiKey.SetValue('********************')
		if self.conf.get('TWITTER', 'apiSecret'): self.apiSecret.SetValue('********************')
		if self.conf.get('TWITTER', 'accessToken'): self.accessToken.SetValue('********************')
		if self.conf.get('TWITTER', 'accessTokenSecret'): self.accessTokenSecret.SetValue('********************')
		if self.conf.get('TWITTER', 'enable')=='1':
			self.twitter_enable.SetValue(True)
			self.datastream_select.Disable()
			self.apiKey.Disable()
			self.apiSecret.Disable()
			self.accessToken.Disable()
			self.accessTokenSecret.Disable()

		if self.conf.get('GMAIL', 'gmail'): self.Gmail_account.SetValue(self.conf.get('GMAIL', 'gmail'))
		if self.conf.get('GMAIL', 'password'): self.Gmail_password.SetValue('********************')
		if self.conf.get('GMAIL', 'recipient'): self.Recipient.SetValue(self.conf.get('GMAIL', 'recipient'))
		if self.conf.get('GMAIL', 'enable')=='1':
			self.gmail_enable.SetValue(True)
			self.Gmail_account.Disable()
			self.Gmail_password.Disable()
			self.Recipient.Disable()

		self.read_switches()
		self.read_triggers()
		self.read_DS18B20()

########MENU###################################	

	def time_zone(self,event):
		subprocess.Popen(['lxterminal', '-e', 'sudo dpkg-reconfigure tzdata'])
		self.SetStatusText(_('Set time zone in the new window'))

	def time_gps(self,event):
		self.SetStatusText(_('Waiting for NMEA time data in localhost:10110 ...'))
		time_gps_result=subprocess.check_output(['sudo', 'python', currentpath+'/time_gps.py'])
		msg=''
		re=time_gps_result.splitlines()
		for current in re:
			if 'Failed to connect with localhost:10110.' in current: msg+=_('Failed to connect with localhost:10110.\n')
			if 'Error: ' in current: msg+=current+'\n'
			if 'Unable to retrieve date or time from NMEA data.' in current: msg+=_('Unable to retrieve date or time from NMEA data.\n')
			if 'UTC' in current:
				if not '00:00:00' in current: msg+=current+'\n'
			if 'Date and time retrieved from NMEA data successfully.' in current: msg+=_('Date and time retrieved from NMEA data successfully.')

		self.SetStatusText('')
		self.ShowMessage(msg)

	def reconfigure_gpsd(self,event):
		subprocess.Popen(['lxterminal', '-e', 'sudo nano /etc/default/gpsd'])
		self.SetStatusText(_('Set GPSD in the new window'))
	
	def clear_lang(self):
		self.lang.Check(self.lang_item1.GetId(), False)
		self.lang.Check(self.lang_item2.GetId(), False)
		self.lang.Check(self.lang_item3.GetId(), False)
		self.lang.Check(self.lang_item4.GetId(), False)
		self.lang.Check(self.lang_item5.GetId(), False)
		self.ShowMessage(_('The selected language will be enabled when you restart'))
	
	def lang_en(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item1.GetId(), True)
		self.conf.set('GENERAL', 'lang', 'en')
	def lang_ca(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item2.GetId(), True)
		self.conf.set('GENERAL', 'lang', 'ca')
	def lang_es(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item3.GetId(), True)
		self.conf.set('GENERAL', 'lang', 'es')
	def lang_fr(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item4.GetId(), True)
		self.conf.set('GENERAL', 'lang', 'fr')
	def lang_nl(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item5.GetId(), True)
		self.conf.set('GENERAL', 'lang', 'nl')

	def OnAboutBox(self, e):
		description = _("OpenPlotter is a DIY, open-source, low-cost, low-consumption, modular and scalable sailing platform to run on ARM boards.")			
		licence = """This program is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 2 of 
the License, or any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License 
along with this program.  If not, see http://www.gnu.org/licenses/"""

		info = wx.AboutDialogInfo()
		info.SetName('OpenPlotter')
		info.SetVersion(self.conf.get('GENERAL', 'version'))
		info.SetDescription(description)
		info.SetCopyright('2016 Sailoog')
		info.SetWebSite('http://www.sailoog.com')
		info.SetLicence(licence)
		info.AddDeveloper('Sailoog\nhttp://github.com/sailoog/openplotter\n-------------------\nOpenCPN: http://opencpn.org/ocpn/\nzyGrib: http://www.zygrib.org/\nMultiplexer: http://www.stripydog.com/kplex/index.html\nrtl-sdr: http://sdr.osmocom.org/trac/wiki/rtl-sdr\naisdecoder: http://www.aishub.net/aisdecoder-via-sound-card.html\ngeomag: http://github.com/cmweiss/geomag\nIMU sensor: http://github.com/richards-tech/RTIMULib2\nNMEA parser: http://github.com/Knio/pynmea2\ntwython: http://github.com/ryanmcgrath/twython\npyrtlsdr: http://github.com/roger-/pyrtlsdr\nkalibrate-rtl: http://github.com/steve-m/kalibrate-rtl\nSignalK: http://signalk.org/\n\n')
		info.AddDocWriter('Sailoog\n\nDocumentation: http://sailoog.gitbooks.io/openplotter-documentation/\nGuides: http://sailoog.dozuki.com/c/OpenPlotter')
		info.AddTranslator('Catalan, English and Spanish by Sailoog\nFrench by Nicolas Janvier.')
		wx.AboutBox(info)

	def op_doc(self, e):
		url = "http://sailoog.gitbooks.io/openplotter-documentation/"
		webbrowser.open(url,new=2)

	def op_guides(self, e):
		url = "http://sailoog.dozuki.com/c/OpenPlotter"
		webbrowser.open(url,new=2)

########startup###################################	
	def ok_delay(self, e):
		delay=self.delay.GetValue()
		if not re.match('^[0-9]*$', delay):
				self.ShowMessage(_('You can enter only numbers.'))
				return
		else:
			if delay != '0': delay = delay.lstrip('0')
			self.conf.set('STARTUP', 'delay', delay)
			self.ShowMessage(_('Startup delay set to ')+delay+_(' seconds'))

	def startup(self, e):
		if self.startup_opencpn.GetValue():
			self.startup_opencpn_nopengl.Enable()
			self.startup_opencpn_fullscreen.Enable()
			self.conf.set('STARTUP', 'opencpn', '1')
		else:
			self.startup_opencpn_nopengl.Disable()
			self.startup_opencpn_fullscreen.Disable()
			self.conf.set('STARTUP', 'opencpn', '0')

		if self.startup_opencpn_nopengl.GetValue():
			self.conf.set('STARTUP', 'opencpn_no_opengl', '1')
		else:
			self.conf.set('STARTUP', 'opencpn_no_opengl', '0')

		if self.startup_opencpn_fullscreen.GetValue():
			self.conf.set('STARTUP', 'opencpn_fullscreen', '1')
		else:
			self.conf.set('STARTUP', 'opencpn_fullscreen', '0')

		if self.startup_multiplexer.GetValue():
			self.startup_nmea_time.Enable()
			self.conf.set('STARTUP', 'kplex', '1')
		else:
			self.startup_nmea_time.Disable()
			self.conf.set('STARTUP', 'kplex', '0')

		if self.startup_nmea_time.GetValue():
			self.conf.set('STARTUP', 'gps_time', '1')
		else:
			self.conf.set('STARTUP', 'gps_time', '0')

		if self.startup_remote_desktop.GetValue():
			self.conf.set('STARTUP', 'x11vnc', '1')
		else:
			self.conf.set('STARTUP', 'x11vnc', '0')

		if self.startup_signalk.GetValue():
			self.conf.set('STARTUP', 'signalk', '1')
		else:
			self.conf.set('STARTUP', 'signalk', '0')

########WIFI###################################	


	def onwifi_enable (self, e):
		isChecked = self.wifi_enable.GetValue()
		if not isChecked:
			dlg = wx.MessageDialog(None, _('Are you sure to disable?\nIf you are connected by remote, you may not be able to reconnect again.'), _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
			if dlg.ShowModal() != wx.ID_YES:
				self.wifi_enable.SetValue(True)
				dlg.Destroy()
				return
			dlg.Destroy()
		wlan=self.wlan.GetValue()
		ssid=self.ssid.GetValue()
		share=self.share.GetValue()
		if '*****' in self.passw.GetValue(): passw=self.conf.get('WIFI', 'password')
		else: passw=self.passw.GetValue()
		
		if not wlan or not passw or not ssid or not share:
			self.ShowMessage(_('You must fill in all of the fields.'))
			self.enable_disable_wifi(0)
			return
		if wlan==share:
			self.ShowMessage(_('"AP Wifi Device" and "internet connection to share" must be different'))
			self.enable_disable_wifi(0)
			return
		if len(ssid)>32 or len(passw)<8:
			self.ShowMessage(_('Your SSID must have a maximum of 32 characters and your password a minimum of 8.'))
			self.enable_disable_wifi(0)
			return
		if share==_('none'):share='0'
		self.SetStatusText(_('Configuring WiFi AP, wait please...'))
		if isChecked:
			self.enable_disable_wifi(1)
			wifi_result=subprocess.check_output(['sudo', 'python', currentpath+'/wifi_server.py', '1', wlan, passw, ssid, share])		
		else:
			self.enable_disable_wifi(0)
			wifi_result=subprocess.check_output(['sudo', 'python', currentpath+'/wifi_server.py', '0', wlan, passw, ssid, share])
			
		msg=wifi_result

		if 'WiFi access point failed.' in msg:
			self.enable_disable_wifi(0)
			self.conf.set('WIFI', 'device', '')
			self.conf.set('WIFI', 'password', '')
			self.conf.set('WIFI', 'ssid', '')
			self.conf.set('WIFI', 'share', '')
		if'WiFi access point started.' in msg:
			self.conf.set('WIFI', 'device', wlan)
			self.conf.set('WIFI', 'password', passw)
			self.conf.set('WIFI', 'ssid', ssid)
			self.conf.set('WIFI', 'share', share)
			self.passw.SetValue('**********')

		msg=msg.replace('WiFi access point failed.', _('WiFi access point failed.'))
		msg=msg.replace('WiFi access point started.', _('WiFi access point started.'))
		msg=msg.replace('WiFi access point stopped.', _('WiFi access point stopped.'))
		self.SetStatusText('')
		self.ShowMessage(msg)
		self.show_ip_info('')

	def show_ip_info(self, e):
		ip_info=subprocess.check_output(['hostname', '-I'])
		out=_(' NMEA 0183:\n')
		ips=ip_info.split()
		for ip in ips:
			out+=ip+':10110\n'
		out+=_('\n VNC remote desktop:\n')
		for ip in ips:
			out+=ip+':5900\n'
		out+=_('\n RDP remote desktop:\n')
		for ip in ips:
			out+=ip+'\n'
		out+=_('\n Signal K panel:\n')
		for ip in ips:
			out+=ip+':3000/instrumentpanel\n'
		out+=_('\n Signal K gauge:\n')
		for ip in ips:
			out+=ip+':3000/sailgauge\n'
		out+=_('\n Signal K WebSocket:\n')
		for ip in ips:
			out+=ip+':3000/signalk/stream/v1?stream=delta\n'
		self.ip_info.SetValue(out)

	def enable_disable_wifi(self, s):
		if s==1:
			self.wlan.Disable()
			self.passw.Disable()
			self.ssid.Disable()
			self.share.Disable()
			self.wlan_label.Disable()
			self.passw_label.Disable()
			self.ssid_label.Disable()
			self.share_label.Disable()
			self.wifi_enable.SetValue(True)
			self.conf.set('WIFI', 'enable', '1')
		else:
			self.wlan.Enable()
			self.passw.Enable()
			self.ssid.Enable()
			self.share.Enable()
			self.wlan_label.Enable()
			self.passw_label.Enable()
			self.ssid_label.Enable()
			self.share_label.Enable()
			self.wifi_enable.SetValue(False)
			self.conf.set('WIFI', 'enable', '0')

########SDR-AIS###################################	


	def kill_sdr(self):
		subprocess.call(['pkill', '-9', 'aisdecoder'])
		subprocess.call(['pkill', '-9', 'rtl_fm'])
		subprocess.call(['pkill', '-f', 'waterfall.py'])
		subprocess.call(['pkill', '-9', 'rtl_test'])
		subprocess.call(['pkill', '-9', 'kal'])

	def enable_sdr_controls(self):
		self.gain.Enable()
		self.ppm.Enable()
		self.ais_frequencies1.Enable()
		self.ais_frequencies2.Enable()
		self.gain_label.Enable()
		self.correction_label.Enable()
		self.ais_sdr_enable.SetValue(False)
		self.conf.set('AIS-SDR', 'enable', '0')

	def disable_sdr_controls(self):
		self.gain.Disable()
		self.ppm.Disable()
		self.ais_frequencies1.Disable()
		self.ais_frequencies2.Disable()
		self.gain_label.Disable()
		self.correction_label.Disable()
	
	def ais_frequencies(self, e):
		sender = e.GetEventObject()
		self.ais_frequencies1.SetValue(False)
		self.ais_frequencies2.SetValue(False)
		sender.SetValue(True)

	def OnOffAIS(self, e):
		self.kill_sdr()
		isChecked = self.ais_sdr_enable.GetValue()
		if isChecked:
			self.disable_sdr_controls() 
			gain=self.gain.GetValue()
			ppm=self.ppm.GetValue()
			frecuency='161975000'
			channel='a'
			if self.ais_frequencies2.GetValue(): 
				frecuency='162025000'
				channel='b'
			rtl_fm=subprocess.Popen(['rtl_fm', '-f', frecuency, '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
			aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)         
			self.conf.set('AIS-SDR', 'enable', '1')
			self.conf.set('AIS-SDR', 'gain', gain)
			self.conf.set('AIS-SDR', 'ppm', ppm)
			self.conf.set('AIS-SDR', 'channel', channel)
			msg=_('SDR-AIS reception enabled')
		else:
			self.enable_sdr_controls()
			self.conf.set('AIS-SDR', 'enable', '0')
			msg=_('SDR-AIS reception disabled')

		self.SetStatusText('')
		self.ShowMessage(msg)

	def test_ppm(self,event):
		self.kill_sdr()
		self.enable_sdr_controls()
		gain='25'
		if self.gain.GetValue():
			gain=self.gain.GetValue()
			gain=gain.replace(',', '.')
		ppm='0'
		if self.ppm.GetValue():
			ppm=self.ppm.GetValue()
			ppm=ppm.replace(',', '.')
		channel='a'
		if self.ais_frequencies2.GetValue(): channel='b'
		w_open=subprocess.Popen(['python', currentpath+'/waterfall.py', gain, ppm, channel])
		msg=_('SDR-AIS reception disabled.\nAfter checking the new window enable SDR-AIS reception again.')
		self.ShowMessage(msg)

	def test_gain(self,event):
		self.kill_sdr()
		self.enable_sdr_controls()
		subprocess.Popen(['lxterminal', '-e', 'rtl_test', '-p'])
		msg=_('SDR-AIS reception disabled.\nCheck the new window. Copy the maximum supported gain value. Wait for ppm value to stabilize and copy it too.')
		self.ShowMessage(msg)

	def check_band(self, event):
		self.kill_sdr()
		self.enable_sdr_controls()
		gain=self.gain.GetValue()
		ppm=self.ppm.GetValue()
		band=self.band.GetValue()
		self.conf.set('AIS-SDR', 'gain', gain)
		self.conf.set('AIS-SDR', 'ppm', ppm)
		self.conf.set('AIS-SDR', 'band', band)
		subprocess.Popen(['python',currentpath+'/fine_cal.py', 'b'])

	def check_channel(self, event):
		self.kill_sdr()
		self.enable_sdr_controls()
		gain=self.gain.GetValue()
		ppm=self.ppm.GetValue()
		channel=self.channel.GetValue()
		self.conf.set('AIS-SDR', 'gain', gain)
		self.conf.set('AIS-SDR', 'ppm', ppm)
		self.conf.set('AIS-SDR', 'gsm_channel', channel)
		if channel: subprocess.Popen(['python',currentpath+'/fine_cal.py', 'c'])
########multimpexer###################################	

	def show_output_window(self,event):
		close=subprocess.call(['pkill', '-f', 'output.py'])
		show_output=subprocess.Popen(['python',currentpath+'/output.py'])

	def restart_multiplex(self,event):
		self.restart_kplex()
		self.read_kplex_conf()

	def advanced_multiplex(self,event):
		self.ShowMessage(_('OpenPlotter will close. Add manual settings at the end of the configuration file. Open OpenPlotter again and restart multiplexer to apply changes.'))
		subprocess.Popen(['leafpad',home+'/.kplex.conf'])
		self.Close()

	def restart_kplex(self):
		self.SetStatusText(_('Closing Kplex'))
		subprocess.call(["pkill", '-9', "kplex"])
		subprocess.Popen('kplex')
		self.SetStatusText(_('Kplex restarted'))

	def cancel_changes(self,event):
		self.read_kplex_conf()

	def read_kplex_conf(self):
		self.inputs = []
		self.outputs = []
		try:
			file=open(home+'/.kplex.conf', 'r')
			data=file.readlines()
			file.close()

			l_tmp=[None]*8
			self.manual_settings=''
			for index, item in enumerate(data):
				if self.manual_settings:
					if item!='\n': self.manual_settings+=item
				else:
					if re.search('\[*\]', item):
						if l_tmp[0]=='in': self.inputs.append(l_tmp)
						if l_tmp[0]=='out': self.outputs.append(l_tmp)
						l_tmp=[None]*8
						l_tmp[5]='none'
						l_tmp[6]='nothing'
						if '[serial]' in item: l_tmp[2]='Serial'
						if '[tcp]' in item: l_tmp[2]='TCP'
						if '[udp]' in item: l_tmp[2]='UDP'
						if '#[' in item: l_tmp[7]='0'
						else: l_tmp[7]='1'
					if 'direction=in' in item:
						l_tmp[0]='in'
					if 'direction=out' in item:
						l_tmp[0]='out'
					if 'name=' in item and 'filename=' not in item:
						l_tmp[1]=self.extract_value(item)
					if 'address=' in item or 'filename=' in item:
						l_tmp[3]=self.extract_value(item)
					if 'port=' in item or 'baud=' in item:
						l_tmp[4]=self.extract_value(item)
					if 'filter=' in item and '-all' in item:
						l_tmp[5]='accept'
						l_tmp[6]=self.extract_value(item)
					if 'filter=' in item and '-all' not in item:
						l_tmp[5]='ignore'
						l_tmp[6]=self.extract_value(item)
					if '###Manual settings' in item:
						self.manual_settings='###Manual settings\n\n'

			if l_tmp[0]=='in': self.inputs.append(l_tmp)
			if l_tmp[0]=='out': self.outputs.append(l_tmp)
			self.write_inputs()
			self.write_outputs()

		except IOError:
			self.ShowMessage(_('Multiplexer configuration file does not exist. Add inputs and apply changes.'))

	def extract_value(self,data):
		option, value =data.split('=')
		value=value.strip()
		return value

	def write_inputs(self):
		self.list_input.DeleteAllItems()
		for i in self.inputs:
			if i[1]: index = self.list_input.InsertStringItem(sys.maxint, i[1])
			if i[2]: self.list_input.SetStringItem(index, 1, i[2])
			if i[3]: self.list_input.SetStringItem(index, 2, i[3])
			else: self.list_input.SetStringItem(index, 2, '127.0.0.1')
			if i[4]: self.list_input.SetStringItem(index, 3, i[4])
			if i[5]:
				if i[5]=='none': self.list_input.SetStringItem(index, 4, _('none'))
				if i[5]=='accept': self.list_input.SetStringItem(index, 4, _('accept'))
				if i[5]=='ignore': self.list_input.SetStringItem(index, 4, _('ignore'))
			if i[6]=='nothing':
				self.list_input.SetStringItem(index, 5, _('nothing'))
			else:
				filters=i[6].replace(':-all', '')
				filters=filters.replace('+', '')
				filters=filters.replace('-', '')
				filters=filters.replace(':', ',')
				self.list_input.SetStringItem(index, 5, filters)
			if i[7]=='1': self.list_input.CheckItem(index)
	
	def write_outputs(self):
		self.list_output.DeleteAllItems()
		for i in self.outputs:
			if i[1]: index = self.list_output.InsertStringItem(sys.maxint, i[1])
			if i[2]: self.list_output.SetStringItem(index, 1, i[2])
			if i[3]: self.list_output.SetStringItem(index, 2, i[3])
			else: self.list_output.SetStringItem(index, 2, 'localhost')
			if i[4]: self.list_output.SetStringItem(index, 3, i[4])
			if i[5]:
				if i[5]=='none': self.list_output.SetStringItem(index, 4, _('none'))
				if i[5]=='accept': self.list_output.SetStringItem(index, 4, _('accept'))
				if i[5]=='ignore': self.list_output.SetStringItem(index, 4, _('ignore'))
			if i[6]=='nothing':
				self.list_output.SetStringItem(index, 5, _('nothing'))
			else:
				filters=i[6].replace(':-all', '')
				filters=filters.replace('+', '')
				filters=filters.replace('-', '')
				filters=filters.replace(':', ',')
				self.list_output.SetStringItem(index, 5, filters)
			if i[7]=='1': self.list_output.CheckItem(index)

	def apply_changes(self,event):
		data='# For advanced manual configuration, please visit: http://www.stripydog.com/kplex/configuration.html\n# Please do not modify defaults nor OpenPlotter GUI settings.\n# Add manual settings at the end of the document.\n\n'

		data=data+'###defaults\n\n[udp]\nname=system_input\ndirection=in\noptional=yes\naddress=127.0.0.1\nport=10110\n\n'
		data=data+'[tcp]\nname=system_output\ndirection=out\nmode=server\nport=10110\n\n###end of defaults\n\n###OpenPlotter GUI settings\n\n'

		for index,item in enumerate(self.inputs):
			if 'system_input' not in item[1]:
				if self.list_input.IsChecked(index): state=''
				else: state='#'
				if 'Serial' in item[2]:
					data=data+state+'[serial]\n'+state+'name='+item[1]+'\n'+state+'direction=in\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ifilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ifilter='+item[6]+'\n'
					data=data+state+'filename='+item[3]+'\n'+state+'baud='+item[4]+'\n\n'
				if 'TCP' in item[2]:
					data=data+state+'[tcp]\n'+state+'name='+item[1]+'\n'+state+'direction=in\n'+state+'optional=yes\n'
					if item[1]=='gpsd':data=data+state+'gpsd=yes\n'
					if item[5]=='ignore':data=data+state+'ifilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ifilter='+item[6]+'\n'
					data=data+state+'mode=client\n'+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n'
					data=data+state+'persist=yes\n'+state+'retry=10\n\n'				
				if 'UDP' in item[2]:
					data=data+state+'[udp]\n'+state+'name='+item[1]+'\n'+state+'direction=in\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ifilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ifilter='+item[6]+'\n'
					data=data+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n\n'
		

		for index,item in enumerate(self.outputs):
			if 'system_output' not in item[1]:
				if self.list_output.IsChecked(index): state=''
				else: state='#'
				if 'Serial' in item[2]:
					data=data+state+'[serial]\n'+state+'name='+item[1]+'\n'+state+'direction=out\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ofilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ofilter='+item[6]+'\n'
					data=data+state+'filename='+item[3]+'\n'+state+'baud='+item[4]+'\n\n'
				if 'TCP' in item[2]:
					data=data+state+'[tcp]\n'+state+'name='+item[1]+'\n'+state+'direction=out\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ofilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ofilter='+item[6]+'\n'
					data=data+state+'mode=server\n'+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n\n'				
				if 'UDP' in item[2]:
					data=data+state+'[udp]\n'+state+'name='+item[1]+'\n'+state+'direction=out\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ofilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ofilter='+item[6]+'\n'
					data=data+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n\n'
		
		data=data+'###end of OpenPlotter GUI settings\n\n'
		if self.manual_settings: data+= self.manual_settings
		else: data+= '###Manual settings\n\n'
		
		file = open(home+'/.kplex.conf', 'w')
		file.write(data)
		file.close()
		self.restart_kplex()
		self.read_kplex_conf()

	def delete_input(self,event):
		num = len(self.inputs)
		for i in range(num):
			if self.list_input.IsSelected(i):
				del self.inputs[i]
		self.write_inputs()

	def delete_output(self,event):
		num = len(self.outputs)
		for i in range(num):
			if self.list_output.IsSelected(i):
				del self.outputs[i]
		self.write_outputs()

	def process_name(self,r):
		list_tmp=[]
		l=r.split(',')
		for item in l:
			item=item.strip()
			list_tmp.append(item)
		name=list_tmp[1]
		found=False
		for sublist in self.inputs:
			if sublist[1] == name:
				found=True
		for sublist in self.outputs:
			if sublist[1] == name:
				found=True
		if found==True:
			self.ShowMessage(_('This name already exists.'))
			return False
		else:
			return list_tmp
	
	def add_serial_input(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', 'in', 'serial'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				new_port=list_tmp[3]
				for sublist in self.inputs:
					if sublist[3] == new_port: 
						self.ShowMessage(_('This input is already in use.'))
						return
				self.inputs.append(list_tmp)
				self.write_inputs()


	def add_serial_output(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', 'out', 'serial'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				new_port=list_tmp[3]
				for sublist in self.outputs:
					if sublist[3] == new_port: 
						self.ShowMessage(_('This output is already in use.'))
						return
				self.outputs.append(list_tmp)
				self.write_outputs()

	
	def add_network_input(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', 'in', 'network'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				new_address_port=str(list_tmp[2])+str(list_tmp[3])+str(list_tmp[4])
				for sublist in self.inputs:					
					old_address_port=str(sublist[2])+str(sublist[3])+str(sublist[4])
					if old_address_port == new_address_port: 
						self.ShowMessage(_('This input is already in use.'))
						return
				self.inputs.append(list_tmp)
				self.write_inputs()


	def add_network_output(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', 'out', 'network'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				new_address_port=str(list_tmp[2])+str(list_tmp[3])+str(list_tmp[4])
				for sublist in self.outputs:					
					old_address_port=str(sublist[2])+str(sublist[3])+str(sublist[4])
					if old_address_port == new_address_port: 
						self.ShowMessage(_('This output is already in use.'))
						return
				self.outputs.append(list_tmp)
				self.write_outputs()


######################################multiplexer

	def ShowMessage(self, w_msg):
			wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)

#####sensors#################################
	def start_sensors(self):
		subprocess.call(['pkill', 'RTIMULibCal'])
		subprocess.call(['pkill', '-f', 'i2c.py'])
		if self.heading.GetValue() or self.heel.GetValue() or self.press.GetValue() or self.temp_p.GetValue() or self.hum.GetValue() or self.temp_h.GetValue():
			subprocess.Popen(['python', currentpath+'/i2c.py'], cwd=currentpath+'/imu')

	def ok_rate(self, e):
		rate=self.rate.GetValue()
		self.conf.set('STARTUP', 'nmea_rate_sen', rate)
		self.start_sensors()
		self.start_sensors_b()
		self.ShowMessage(_('Generation rate set to ')+rate+_(' seconds'))
		
	def nmea_hdg(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_hdg', '1')
		else: self.conf.set('STARTUP', 'nmea_hdg', '0')
		self.start_sensors()

	def nmea_heel(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_heel', '1')
		else: self.conf.set('STARTUP', 'nmea_heel', '0')
		self.start_sensors()

	def reset_imu(self, e):
		try:
			os.remove(currentpath+'/imu/RTIMULib.ini')
		except Exception,e: print str(e)
		self.button_calibrate_imu.Enable()
		self.imu_tag.Disable()
		self.heading.SetValue(False)
		self.heel.SetValue(False)
		self.conf.set('STARTUP', 'nmea_hdg', '0')
		self.conf.set('STARTUP', 'nmea_heel', '0')
		self.start_sensors()
		msg=_('Heading and heel disabled.\nClose and open OpenPlotter again to autodetect.')
		self.ShowMessage(msg)

	def reset_press_hum(self, e):
		try:
			os.remove(currentpath+'/imu/RTIMULib2.ini')
		except Exception,e: print str(e)
		try:
			os.remove(currentpath+'/imu/RTIMULib3.ini')
		except Exception,e: print str(e)
		self.press_tag.Disable()
		self.hum_tag.Disable()
		self.press.SetValue(False)
		self.temp_p.SetValue(False)
		self.hum.SetValue(False)
		self.temp_h.SetValue(False)
		self.conf.set('STARTUP', 'nmea_press', '0')
		self.conf.set('STARTUP', 'nmea_temp_p', '0')
		self.conf.set('STARTUP', 'nmea_hum', '0')
		self.conf.set('STARTUP', 'nmea_temp_h', '0')
		self.start_sensors()
		msg=_('Temperature, humidity and pressure disabled.\nClose and open OpenPlotter again to autodetect.')
		self.ShowMessage(msg)

	def calibrate_imu(self, e):
		self.heading.SetValue(False)
		self.heel.SetValue(False)
		self.press.SetValue(False)
		self.temp_p.SetValue(False)
		self.hum.SetValue(False)
		self.temp_h.SetValue(False)
		self.conf.set('STARTUP', 'nmea_hdg', '0')
		self.conf.set('STARTUP', 'nmea_heel', '0')
		self.conf.set('STARTUP', 'nmea_press', '0')
		self.conf.set('STARTUP', 'nmea_temp_p', '0')
		self.conf.set('STARTUP', 'nmea_hum', '0')
		self.conf.set('STARTUP', 'nmea_temp_h', '0')
		self.start_sensors()
		subprocess.Popen(['lxterminal', '-e', 'RTIMULibCal'], cwd=currentpath+'/imu')
		msg=_('Heading, heel, temperature, humidity and pressure disabled.\nAfter calibrating, enable them again.')
		self.ShowMessage(msg)
	
	def nmea_press(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_press', '1')
		else: self.conf.set('STARTUP', 'nmea_press', '0')
		self.start_sensors()

	def nmea_temp_p(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): 
			self.temp_h.SetValue(False)
			self.conf.set('STARTUP', 'nmea_temp_h', '0')
			self.conf.set('STARTUP', 'nmea_temp_p', '1')
		else: 
			self.conf.set('STARTUP', 'nmea_temp_p', '0')
		self.start_sensors()

	def nmea_hum(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_hum', '1')
		else: self.conf.set('STARTUP', 'nmea_hum', '0')
		self.start_sensors()

	def nmea_temp_h(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): 
			self.temp_p.SetValue(False)
			self.conf.set('STARTUP', 'nmea_temp_p', '0')
			self.conf.set('STARTUP', 'nmea_temp_h', '1')
		else: 
			self.conf.set('STARTUP', 'nmea_temp_h', '0')
		self.start_sensors()

	def enable_press_temp_log(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'press_temp_log', '1')
		else: self.conf.set('STARTUP', 'press_temp_log', '0')
		self.start_sensors()

	def show_graph(self, e):
		subprocess.call(['pkill', '-f', 'graph.py'])
		subprocess.Popen(['python', currentpath+'/graph.py'])

	def	reset_graph(self, e):
		data=''
		file = open(currentpath+'/weather_log.csv', 'w')
		file.write(data)
		file.close()
		self.start_sensors()
		self.ShowMessage(_('Weather log restarted'))
######################################calculate

	def start_calculate(self):
		subprocess.call(['pkill', '-f', 'calculate.py'])
		if self.mag_var.GetValue() or self.heading_t.GetValue() or self.rot.GetValue() or self.TW_STW.GetValue() or self.TW_SOG.GetValue():
			subprocess.Popen(['python', currentpath+'/calculate.py'])

	def ok_rate2(self, e):
		rate=self.rate2.GetValue()
		self.conf.set('STARTUP', 'nmea_rate_cal', rate)
		self.start_calculate()
		self.ShowMessage(_('Generation rate set to ')+rate+_(' seconds'))

	def ok_accuracy(self,e):
		accuracy=self.accuracy.GetValue()
		self.conf.set('STARTUP', 'cal_accuracy', accuracy)
		self.start_calculate()
		self.ShowMessage(_('Calculation accuracy set to ')+accuracy+_(' seconds'))

	def nmea_mag_var(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_mag_var', '1')
		else: self.conf.set('STARTUP', 'nmea_mag_var', '0')
		self.start_calculate()

	def nmea_hdt(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_hdt', '1')
		else: self.conf.set('STARTUP', 'nmea_hdt', '0')
		self.start_calculate()

	def nmea_rot(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_rot', '1')
		else: self.conf.set('STARTUP', 'nmea_rot', '0')
		self.start_calculate()

	def	TW(self, e):
		sender = e.GetEventObject()
		state=sender.GetValue()
		self.TW_STW.SetValue(False)
		self.TW_SOG.SetValue(False)
		self.conf.set('STARTUP', 'tw_stw', '0')
		self.conf.set('STARTUP', 'tw_sog', '0')
		if state: sender.SetValue(True)
		if self.TW_STW.GetValue(): self.conf.set('STARTUP', 'tw_stw', '1')
		if self.TW_SOG.GetValue(): self.conf.set('STARTUP', 'tw_sog', '1')
		self.start_calculate()
######################################Signal K
	def signalKpanels(self, e):
		url = 'http://localhost:3000/instrumentpanel'
		webbrowser.open(url,new=2)

	def signalKsailgauge(self, e):
		url = 'http://localhost:3000/sailgauge'
		webbrowser.open(url,new=2)

	def signalKout(self, e):
		url = 'http://localhost:3000/examples/consumer-example.html'
		webbrowser.open(url,new=2)

	def restartSK(self, e):
		self.SetStatusText(_('Closing Signal K server'))
		subprocess.call(["pkill", '-9', "node"])
		subprocess.Popen(home+'/.config/signalk-server-node/bin/nmea-from-10110', cwd=home+'/.config/signalk-server-node')
		self.SetStatusText(_('Signal K server restarted'))
######################################Switches
	def read_switches(self):
		if self.conf.get('SWITCH1', 'enable')=='1':
			self.gpio_pin1.SetValue(self.conf.get('SWITCH1', 'gpio'))
			self.gpio_pull1.SetValue(self.conf.get('SWITCH1', 'pull_up_down'))
			self.switch1_enable.SetValue(True)
			self.gpio_pin1.Disable()
			self.gpio_pull1.Disable()
		if self.conf.get('SWITCH2', 'enable')=='1':
			self.gpio_pin2.SetValue(self.conf.get('SWITCH2', 'gpio'))
			self.gpio_pull2.SetValue(self.conf.get('SWITCH2', 'pull_up_down'))
			self.switch2_enable.SetValue(True)
			self.gpio_pin2.Disable()
			self.gpio_pull2.Disable()
		if self.conf.get('SWITCH3', 'enable')=='1':
			self.gpio_pin3.SetValue(self.conf.get('SWITCH3', 'gpio'))
			self.gpio_pull3.SetValue(self.conf.get('SWITCH3', 'pull_up_down'))
			self.switch3_enable.SetValue(True)
			self.gpio_pin3.Disable()
			self.gpio_pull3.Disable()
		if self.conf.get('SWITCH4', 'enable')=='1':
			self.gpio_pin4.SetValue(self.conf.get('SWITCH4', 'gpio'))
			self.gpio_pull4.SetValue(self.conf.get('SWITCH4', 'pull_up_down'))
			self.switch4_enable.SetValue(True)
			self.gpio_pin4.Disable()
			self.gpio_pull4.Disable()
		if self.conf.get('SWITCH5', 'enable')=='1':
			self.gpio_pin5.SetValue(self.conf.get('SWITCH5', 'gpio'))
			self.gpio_pull5.SetValue(self.conf.get('SWITCH5', 'pull_up_down'))
			self.switch5_enable.SetValue(True)
			self.gpio_pin5.Disable()
			self.gpio_pull5.Disable()
		if self.conf.get('SWITCH6', 'enable')=='1':
			self.gpio_pin6.SetValue(self.conf.get('SWITCH6', 'gpio'))
			self.gpio_pull6.SetValue(self.conf.get('SWITCH6', 'pull_up_down'))
			self.switch6_enable.SetValue(True)
			self.gpio_pin6.Disable()
			self.gpio_pull6.Disable()
		if self.conf.get('OUTPUT1', 'enable')=='1':
			self.gpio_pin7.SetValue(self.conf.get('OUTPUT1', 'gpio'))
			self.output1_enable.SetValue(True)
			self.gpio_pin7.Disable()
		if self.conf.get('OUTPUT2', 'enable')=='1':
			self.gpio_pin8.SetValue(self.conf.get('OUTPUT2', 'gpio'))
			self.output2_enable.SetValue(True)
			self.gpio_pin8.Disable()
		if self.conf.get('OUTPUT3', 'enable')=='1':
			self.gpio_pin9.SetValue(self.conf.get('OUTPUT3', 'gpio'))
			self.output3_enable.SetValue(True)
			self.gpio_pin9.Disable()
		if self.conf.get('OUTPUT4', 'enable')=='1':
			self.gpio_pin10.SetValue(self.conf.get('OUTPUT4', 'gpio'))
			self.output4_enable.SetValue(True)
			self.gpio_pin10.Disable()

	def on_switch1_enable(self, e):
		if self.switch1_enable.GetValue(): 
			if self.gpio_pin1.GetValue() and self.gpio_pull1.GetValue(): 
				self.gpio_pin1.Disable()
				self.gpio_pull1.Disable()
			else:
				self.switch1_enable.SetValue(False)
		else: 
			self.gpio_pin1.Enable()
			self.gpio_pull1.Enable()

	def on_switch2_enable(self, e):
		if self.switch2_enable.GetValue(): 
			if self.gpio_pin2.GetValue() and self.gpio_pull2.GetValue(): 
				self.gpio_pin2.Disable()
				self.gpio_pull2.Disable()
			else:
				self.switch2_enable.SetValue(False)
		else: 
			self.gpio_pin2.Enable()
			self.gpio_pull2.Enable()

	def on_switch3_enable(self, e):
		if self.switch3_enable.GetValue(): 
			if self.gpio_pin3.GetValue() and self.gpio_pull3.GetValue(): 
				self.gpio_pin3.Disable()
				self.gpio_pull3.Disable()
			else:
				self.switch3_enable.SetValue(False)
		else: 
			self.gpio_pin3.Enable()
			self.gpio_pull3.Enable()

	def on_switch4_enable(self, e):
		if self.switch4_enable.GetValue(): 
			if self.gpio_pin4.GetValue() and self.gpio_pull4.GetValue(): 
				self.gpio_pin4.Disable()
				self.gpio_pull4.Disable()
			else:
				self.switch4_enable.SetValue(False)
		else: 
			self.gpio_pin4.Enable()
			self.gpio_pull4.Enable()

	def on_switch5_enable(self, e):
		if self.switch5_enable.GetValue(): 
			if self.gpio_pin5.GetValue() and self.gpio_pull5.GetValue(): 
				self.gpio_pin5.Disable()
				self.gpio_pull5.Disable()
			else:
				self.switch5_enable.SetValue(False)
		else: 
			self.gpio_pin5.Enable()
			self.gpio_pull5.Enable()

	def on_switch6_enable(self, e):
		if self.switch6_enable.GetValue(): 
			if self.gpio_pin6.GetValue() and self.gpio_pull6.GetValue(): 
				self.gpio_pin6.Disable()
				self.gpio_pull6.Disable()
			else:
				self.switch6_enable.SetValue(False)
		else: 
			self.gpio_pin6.Enable()
			self.gpio_pull6.Enable()

	def on_output1_enable(self, e):
		if self.output1_enable.GetValue(): 
			if self.gpio_pin7.GetValue(): 
				self.gpio_pin7.Disable()
				self.output_message()
			else:
				self.output1_enable.SetValue(False)
		else: 
			self.gpio_pin7.Enable()

	def on_output2_enable(self, e):
		if self.output2_enable.GetValue(): 
			if self.gpio_pin8.GetValue(): 
				self.gpio_pin8.Disable()
				self.output_message()
			else:
				self.output2_enable.SetValue(False)
		else: 
			self.gpio_pin8.Enable()

	def on_output3_enable(self, e):
		if self.output3_enable.GetValue(): 
			if self.gpio_pin9.GetValue(): 
				self.gpio_pin9.Disable()
				self.output_message()
			else:
				self.output3_enable.SetValue(False)
		else: 
			self.gpio_pin9.Enable()

	def on_output4_enable(self, e):
		if self.output4_enable.GetValue(): 
			if self.gpio_pin10.GetValue(): 
				self.gpio_pin10.Disable()
				self.output_message()
			else:
				self.output4_enable.SetValue(False)
		else: 
			self.gpio_pin10.Enable()

	def output_message(self):
		self.ShowMessage(_('ATTENTION! if you set this output to "High" and there is not a resistor or a circuit connected to the selected GPIO pin, YOU CAN DAMAGE YOUR BOARD.'))	

	def apply_changes_switches(self, e):
		enabled=[]
		repeated=[]
		if self.switch1_enable.GetValue() and self.gpio_pin1.GetValue() and self.gpio_pull1.GetValue():
			if self.gpio_pin1.GetValue() in enabled: 
				if not self.gpio_pin1.GetValue() in repeated: repeated.append(self.gpio_pin1.GetValue())
				self.switch1_enable.SetValue(False)
				self.gpio_pin1.Enable()
				self.gpio_pull1.Enable()
				self.conf.set('SWITCH1', 'enable', '0')
			else: 
				enabled.append(self.gpio_pin1.GetValue())
				self.conf.set('SWITCH1', 'enable', '1')
				self.conf.set('SWITCH1', 'gpio', self.gpio_pin1.GetValue())
				self.conf.set('SWITCH1', 'pull_up_down', self.gpio_pull1.GetValue())
		else: self.conf.set('SWITCH1', 'enable', '0')
		if self.switch2_enable.GetValue() and self.gpio_pin2.GetValue() and self.gpio_pull2.GetValue():
			if self.gpio_pin2.GetValue() in enabled: 
				if not self.gpio_pin2.GetValue() in repeated: repeated.append(self.gpio_pin2.GetValue())
				self.switch2_enable.SetValue(False)
				self.gpio_pin2.Enable()
				self.gpio_pull2.Enable()
				self.conf.set('SWITCH2', 'enable', '0')
			else: 
				enabled.append(self.gpio_pin2.GetValue())
				self.conf.set('SWITCH2', 'enable', '1')
				self.conf.set('SWITCH2', 'gpio', self.gpio_pin2.GetValue())
				self.conf.set('SWITCH2', 'pull_up_down', self.gpio_pull2.GetValue())
		else: self.conf.set('SWITCH2', 'enable', '0')
		if self.switch3_enable.GetValue() and self.gpio_pin3.GetValue() and self.gpio_pull3.GetValue():
			if self.gpio_pin3.GetValue() in enabled: 
				if not self.gpio_pin3.GetValue() in repeated: repeated.append(self.gpio_pin3.GetValue())
				self.switch3_enable.SetValue(False)
				self.gpio_pin3.Enable()
				self.gpio_pull3.Enable()
				self.conf.set('SWITCH3', 'enable', '0')
			else: 
				enabled.append(self.gpio_pin3.GetValue())
				self.conf.set('SWITCH3', 'enable', '1')
				self.conf.set('SWITCH3', 'gpio', self.gpio_pin3.GetValue())
				self.conf.set('SWITCH3', 'pull_up_down', self.gpio_pull3.GetValue())
		else: self.conf.set('SWITCH3', 'enable', '0')
		if self.switch4_enable.GetValue() and self.gpio_pin4.GetValue() and self.gpio_pull4.GetValue():
			if self.gpio_pin4.GetValue() in enabled: 
				if not self.gpio_pin4.GetValue() in repeated: repeated.append(self.gpio_pin4.GetValue())
				self.switch4_enable.SetValue(False)
				self.gpio_pin4.Enable()
				self.gpio_pull4.Enable()
				self.conf.set('SWITCH4', 'enable', '0')
			else: 
				enabled.append(self.gpio_pin4.GetValue())
				self.conf.set('SWITCH4', 'enable', '1')
				self.conf.set('SWITCH4', 'gpio', self.gpio_pin4.GetValue())
				self.conf.set('SWITCH4', 'pull_up_down', self.gpio_pull4.GetValue())
		else: self.conf.set('SWITCH4', 'enable', '0')
		if self.switch5_enable.GetValue() and self.gpio_pin5.GetValue() and self.gpio_pull5.GetValue():
			if self.gpio_pin5.GetValue() in enabled: 
				if not self.gpio_pin5.GetValue() in repeated: repeated.append(self.gpio_pin5.GetValue())
				self.switch5_enable.SetValue(False)
				self.gpio_pin5.Enable()
				self.gpio_pull5.Enable()
				self.conf.set('SWITCH5', 'enable', '0')
			else: 
				enabled.append(self.gpio_pin5.GetValue())
				self.conf.set('SWITCH5', 'enable', '1')
				self.conf.set('SWITCH5', 'gpio', self.gpio_pin5.GetValue())
				self.conf.set('SWITCH5', 'pull_up_down', self.gpio_pull5.GetValue())
		else: self.conf.set('SWITCH5', 'enable', '0')
		if self.switch6_enable.GetValue() and self.gpio_pin6.GetValue() and self.gpio_pull6.GetValue():
			if self.gpio_pin6.GetValue() in enabled: 
				if not self.gpio_pin6.GetValue() in repeated: repeated.append(self.gpio_pin6.GetValue())
				self.switch6_enable.SetValue(False)
				self.gpio_pin6.Enable()
				self.gpio_pull6.Enable()
				self.conf.set('SWITCH6', 'enable', '0')
			else: 
				enabled.append(self.gpio_pin6.GetValue())
				self.conf.set('SWITCH6', 'enable', '1')
				self.conf.set('SWITCH6', 'gpio', self.gpio_pin6.GetValue())
				self.conf.set('SWITCH6', 'pull_up_down', self.gpio_pull6.GetValue())
		else: self.conf.set('SWITCH6', 'enable', '0')
		if self.output1_enable.GetValue() and self.gpio_pin7.GetValue():
			if self.gpio_pin7.GetValue() in enabled: 
				if not self.gpio_pin7.GetValue() in repeated: repeated.append(self.gpio_pin7.GetValue())
				self.output1_enable.SetValue(False)
				self.gpio_pin7.Enable()
				self.conf.set('OUTPUT1', 'enable', '0')
			else: 
				enabled.append(self.gpio_pin7.GetValue())
				self.conf.set('OUTPUT1', 'enable', '1')
				self.conf.set('OUTPUT1', 'gpio', self.gpio_pin7.GetValue())
		else: self.conf.set('OUTPUT1', 'enable', '0')
		if self.output2_enable.GetValue() and self.gpio_pin8.GetValue():
			if self.gpio_pin8.GetValue() in enabled: 
				if not self.gpio_pin8.GetValue() in repeated: repeated.append(self.gpio_pin8.GetValue())
				self.output2_enable.SetValue(False)
				self.gpio_pin8.Enable()
				self.conf.set('OUTPUT2', 'enable', '0')
			else: 
				enabled.append(self.gpio_pin8.GetValue())
				self.conf.set('OUTPUT2', 'enable', '1')
				self.conf.set('OUTPUT2', 'gpio', self.gpio_pin8.GetValue())
		else: self.conf.set('OUTPUT2', 'enable', '0')
		if self.output3_enable.GetValue() and self.gpio_pin9.GetValue():
			if self.gpio_pin9.GetValue() in enabled: 
				if not self.gpio_pin9.GetValue() in repeated: repeated.append(self.gpio_pin9.GetValue())
				self.output3_enable.SetValue(False)
				self.gpio_pin9.Enable()
				self.conf.set('OUTPUT3', 'enable', '0')
			else: 
				enabled.append(self.gpio_pin9.GetValue())
				self.conf.set('OUTPUT3', 'enable', '1')
				self.conf.set('OUTPUT3', 'gpio', self.gpio_pin9.GetValue())
		else: self.conf.set('OUTPUT3', 'enable', '0')
		if self.output4_enable.GetValue() and self.gpio_pin10.GetValue():
			if self.gpio_pin10.GetValue() in enabled: 
				if not self.gpio_pin10.GetValue() in repeated: repeated.append(self.gpio_pin10.GetValue())
				self.output4_enable.SetValue(False)
				self.gpio_pin10.Enable()
				self.conf.set('OUTPUT4', 'enable', '0')
			else: 
				enabled.append(self.gpio_pin10.GetValue())
				self.conf.set('OUTPUT4', 'enable', '1')
				self.conf.set('OUTPUT4', 'gpio', self.gpio_pin10.GetValue())
		else: self.conf.set('OUTPUT4', 'enable', '0')
		if repeated: self.ShowMessage(_('GPIO pins must be unique. Repeated pins: ')+', '.join(repeated)+'.')
		else: self.ShowMessage(_('Switches set successfully'))
		self.SetStatusText(_('Switches changes applied and restarted'))
		self.start_monitoring()

	def cancel_changes_switches(self, e):
		self.switch1_enable.SetValue(False)
		self.gpio_pin1.Enable()
		self.gpio_pull1.Enable()
		self.switch2_enable.SetValue(False)
		self.gpio_pin2.Enable()
		self.gpio_pull2.Enable()
		self.switch3_enable.SetValue(False)
		self.gpio_pin3.Enable()
		self.gpio_pull3.Enable()
		self.switch4_enable.SetValue(False)
		self.gpio_pin4.Enable()
		self.gpio_pull4.Enable()
		self.switch5_enable.SetValue(False)
		self.gpio_pin5.Enable()
		self.gpio_pull5.Enable()
		self.switch6_enable.SetValue(False)
		self.gpio_pin6.Enable()
		self.gpio_pull6.Enable()
		self.output1_enable.SetValue(False)
		self.gpio_pin7.Enable()
		self.output2_enable.SetValue(False)
		self.gpio_pin8.Enable()
		self.output3_enable.SetValue(False)
		self.gpio_pin9.Enable()
		self.output4_enable.SetValue(False)
		self.gpio_pin10.Enable()
		self.read_switches()
		self.SetStatusText(_('Switches changes cancelled'))

#######################twitterbot

	def start_monitoring(self):
		self.ShowMessage(_('Actions will be restarted.'))
		subprocess.call(['pkill', '-f', 'monitoring.py'])
		subprocess.Popen(['python',currentpath+'/monitoring.py'])

	def on_twitter_enable(self,e):
		if not self.apiKey.GetValue() or not self.apiSecret.GetValue() or not self.accessToken.GetValue() or not self.accessTokenSecret.GetValue():
			self.twitter_enable.SetValue(False)
			self.ShowMessage(_('Enter valid Twitter apiKey, apiSecret, accessToken and accessTokenSecret.'))
			return
		if not self.datastream_select.GetSelections():
			self.twitter_enable.SetValue(False)
			self.ShowMessage(_('Select some data to publish.'))
			return
		if self.twitter_enable.GetValue():
			self.datastream_select.Disable()
			self.apiKey.Disable()
			self.apiSecret.Disable()
			self.accessToken.Disable()
			self.accessTokenSecret.Disable()
			self.conf.set('TWITTER', 'enable', '1')
			temp_list=[]
			for i in self.datastream_select.GetSelections():
				temp_list.append(self.a.DataList[i][9])
			self.conf.set('TWITTER', 'send_data', str(temp_list))
			if not '*****' in self.apiKey.GetValue(): 
				self.conf.set('TWITTER', 'apiKey', self.apiKey.GetValue())
				self.apiKey.SetValue('********************')
			if not '*****' in self.apiSecret.GetValue(): 
				self.conf.set('TWITTER', 'apiSecret', self.apiSecret.GetValue())
				self.apiSecret.SetValue('********************')
			if not '*****' in self.accessToken.GetValue(): 
				self.conf.set('TWITTER', 'accessToken', self.accessToken.GetValue())
				self.accessToken.SetValue('********************')
			if not '*****' in self.accessTokenSecret.GetValue(): 
				self.conf.set('TWITTER', 'accessTokenSecret', self.accessTokenSecret.GetValue())
				self.accessTokenSecret.SetValue('********************')
		else:
			self.conf.set('TWITTER', 'enable', '0')
			self.datastream_select.Enable()
			self.apiKey.Enable()
			self.apiSecret.Enable()
			self.accessToken.Enable()
			self.accessTokenSecret.Enable()
		self.start_monitoring()

	def on_gmail_enable(self,e):
		if not self.Gmail_account.GetValue() or not self.Gmail_password.GetValue() or not self.Recipient.GetValue():
			self.gmail_enable.SetValue(False)
			self.ShowMessage(_('Enter valid Gmail account, Gmail password and Recipient.'))
			return
		if self.gmail_enable.GetValue():
			self.Gmail_account.Disable()
			self.Gmail_password.Disable()
			self.Recipient.Disable()
			self.conf.set('GMAIL', 'enable', '1')
			self.conf.set('GMAIL', 'gmail', self.Gmail_account.GetValue())
			if not '*****' in self.Gmail_password.GetValue(): 
				self.conf.set('GMAIL', 'password', self.Gmail_password.GetValue())
				self.Gmail_password.SetValue('********************')
			self.conf.set('GMAIL', 'recipient', self.Recipient.GetValue())
		else:
			self.conf.set('GMAIL', 'enable', '0')
			self.Gmail_account.Enable()
			self.Gmail_password.Enable()
			self.Recipient.Enable()
		self.start_monitoring()

#######################actions

	def read_triggers(self):
		self.triggers=[]
		self.list_triggers.DeleteAllItems()
		data=self.conf.get('ACTIONS', 'triggers')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for ii in temp_list:
			if ii[1]==-1:
				self.triggers.append(ii)
				self.list_triggers.Append([_('None (always true)'),'','',])
				if ii[0]==1:
					last=self.list_triggers.GetItemCount()-1
					self.list_triggers.CheckItem(last)
			else:
				x=self.a.getDataListIndex(ii[1])
				if x:
					self.triggers.append(ii)
					self.list_triggers.Append([self.a.DataList[x][0].decode('utf8'),self.a.operators_list[ii[2]].decode('utf8'),ii[3]])
					if ii[0]==1:
						last=self.list_triggers.GetItemCount()-1
						self.list_triggers.CheckItem(last)
				else: self.ShowMessage(_('Problem with Actions detected. Please check and save again.'))

	def print_actions(self, e):
		selected_trigger=e.GetIndex()
		self.list_actions.DeleteAllItems()
		for i in  self.triggers[selected_trigger][4]:
			if i[2]==0.0: repeat=''
			else: repeat=str(i[2])
			time_units=self.actions.time_units[i[3]]
			repeat2=repeat+' '+time_units
			self.list_actions.Append([self.actions.options[i[0]][0].decode('utf8'),i[1].decode('utf8'),repeat2.decode('utf8')])

	def add_trigger(self,e):
		dlg = addTrigger(self.datastream_list, self.a)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			trigger_selection=dlg.trigger_select.GetCurrentSelection()
			if trigger_selection==len(self.datastream_list):
				self.list_triggers.Append([_('None (always true)'),'',''])
				tmp=[]
				tmp.append(1)
				tmp.append(-1)
				tmp.append(-1)
				tmp.append(-1)
				tmp.append([])
				self.triggers.append(tmp)
			else:
				if trigger_selection == -1 or dlg.operator_select.GetCurrentSelection() == -1:
					self.ShowMessage(_('Failed. Select trigger and operator.'))
					dlg.Destroy()
					return
				trigger0=self.a.DataList[trigger_selection]
				operator_selection=trigger0[7][dlg.operator_select.GetCurrentSelection()]
				if dlg.value.GetValue(): value=dlg.value.GetValue()
				else: value='0'
				try: value2=float(value)
				except:
					self.ShowMessage(_('Failed. Value must be a number.'))
					dlg.Destroy()
					return
				operator=self.a.operators_list[operator_selection]
				self.list_triggers.Append([trigger0[0].decode('utf8'),operator.decode('utf8'),value])
				tmp=[]
				tmp.append(1)
				tmp.append(trigger0[9])
				tmp.append(operator_selection)
				tmp.append(value2)
				tmp.append([])
				self.triggers.append(tmp)
			dlg.Destroy()
			total=self.list_triggers.GetItemCount()
			for x in xrange(0, total, 1):
				self.list_triggers.Select(x, on=0)
			self.list_triggers.Select(total-1, on=1)
			self.list_triggers.CheckItem(total-1)

	def add_action(self,e):
		selected_trigger_position= self.list_triggers.GetFirstSelected()
		if selected_trigger_position==-1:
			self.ShowMessage(_('Select a trigger to add actions.'))
			return
		dlg = addAction(self.actions.options,self.actions.time_units)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			action_selection=dlg.action_select.GetCurrentSelection()
			if action_selection == -1:
				self.ShowMessage(_('Failed. Select an action.'))
				dlg.Destroy()
				return
			if dlg.repeat.GetValue(): repeat=dlg.repeat.GetValue()
			else: repeat='0'
			try: repeat=float(repeat)
			except:
				self.ShowMessage(_('Failed. "Repeat after" must be a number.'))
				dlg.Destroy()
				return
			action=self.actions.options[action_selection][0]
			data0=dlg.data.GetValue()
			data=data0.encode('utf8')
			time_units_selection=dlg.repeat_unit.GetCurrentSelection()
			time_units=self.actions.time_units[time_units_selection]
			if repeat==0.0: repeat2=time_units
			else: repeat2=str(repeat)+' '+time_units
			self.list_actions.Append([action.decode('utf8'),data.decode('utf8'),repeat2.decode('utf8')])
			tmp=[]
			tmp.append(action_selection)
			tmp.append(data)
			tmp.append(repeat)
			tmp.append(time_units_selection)
			self.triggers[selected_trigger_position][4].append(tmp)
		dlg.Destroy()

	def delete_trigger(self,e):
		selected=self.list_triggers.GetFirstSelected()
		if selected==-1: 
			self.ShowMessage(_('Select a trigger to delete.'))
		else:
			del self.triggers[selected]
			self.list_triggers.DeleteItem(selected)
			self.list_actions.DeleteAllItems()

	def delete_action(self,e):
		selected_trigger=self.list_triggers.GetFirstSelected()
		selected_action=self.list_actions.GetFirstSelected()
		if selected_action==-1: 
			self.ShowMessage(_('Select an action to delete.'))
		else: 
			del self.triggers[selected_trigger][4][selected_action]
			self.list_actions.DeleteItem(selected_action)

	def apply_changes_actions(self,e):
		i=0
		for ii in self.triggers:
			if self.list_triggers.IsChecked(i): self.triggers[i][0]=1
			else: self.triggers[i][0]=0
			i=i+1
		self.conf.set('ACTIONS', 'triggers', str(self.triggers))
		self.SetStatusText(_('Actions changes applied and restarted'))
		self.start_monitoring()

	def cancel_changes_actions(self,e):
		self.read_triggers()
		self.SetStatusText(_('Actions changes cancelled'))

	def stop_actions(self,e):
		subprocess.call(['python', currentpath+'/ctrl_actions.py', '0'])
		self.SetStatusText(_('Actions stopped'))
		self.conf.read()
		self.read_triggers()
		self.list_actions.DeleteAllItems()

	def start_actions(self,e):
		subprocess.call(['python', currentpath+'/ctrl_actions.py', '1'])
		self.SetStatusText(_('Actions started'))
		self.conf.read()
		self.read_triggers()
		self.list_actions.DeleteAllItems()

#######################DS18B20

	def start_1w(self):
		subprocess.call(['pkill', '-f', '1w.py'])
		subprocess.Popen(['python',currentpath+'/1w.py'])

	def read_DS18B20(self):
		self.DS18B20=[]
		self.list_DS18B20.DeleteAllItems()
		data=self.conf.get('1W', 'DS18B20')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for ii in temp_list:
			self.DS18B20.append(ii)
			self.list_DS18B20.Append([ii[0],ii[1],ii[2],ii[3]])
			if ii[5]=='1':
				last=self.list_DS18B20.GetItemCount()-1
				self.list_DS18B20.CheckItem(last)
	
	def edit_DS18B20(self,e):
		selected_DS18B20=e.GetIndex()
		edit=[selected_DS18B20,self.DS18B20[selected_DS18B20][0],self.DS18B20[selected_DS18B20][1],self.DS18B20[selected_DS18B20][2],self.DS18B20[selected_DS18B20][3]]
		self.edit_add_DS18B20(edit)

	def add_DS18B20(self,e):
		self.edit_add_DS18B20(0)

	def edit_add_DS18B20(self,edit):
		dlg = addDS18B20(edit)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			name=dlg.name.GetValue()
			name=name.encode('utf8')
			short=dlg.short.GetValue()
			short=short.encode('utf8')
			unit_selection=dlg.unit_select.GetValue()
			id_selection=dlg.id_select.GetValue()
			id_selection=id_selection.encode('utf8')
			if not name or not short:
				self.ShowMessage(_('Failed. Write a name and a short name.'))
				dlg.Destroy()
				return				
			if unit_selection == '':
				self.ShowMessage(_('Failed. Select unit.'))
				dlg.Destroy()
				return
			if id_selection == '':
				self.ShowMessage(_('Failed. Select sensor ID.'))
				dlg.Destroy()
				return
			if unit_selection=='Celsius': unit_selection='C'
			if unit_selection=='Fahrenheit': unit_selection='F'
			if unit_selection=='Kelvin': unit_selection='K'
			if edit==0:
				self.list_DS18B20.Append([name.decode('utf8'),short.decode('utf8'),unit_selection,id_selection])
				last=self.list_DS18B20.GetItemCount()-1
				self.list_DS18B20.CheckItem(last)
				if len(self.DS18B20)==0: ID='1W0'
				else:
					last=len(self.DS18B20)-1
					x=int(self.DS18B20[last][4][2:])
					ID='1W'+str(x+1)
				self.DS18B20.append([name,short,unit_selection,id_selection,ID,'1'])
			else:
				self.list_DS18B20.SetStringItem(edit[0],0,name.decode('utf8'))
				self.list_DS18B20.SetStringItem(edit[0],1,short.decode('utf8'))
				self.list_DS18B20.SetStringItem(edit[0],2,unit_selection)
				self.list_DS18B20.SetStringItem(edit[0],3,id_selection)
				self.DS18B20[edit[0]][0]=name
				self.DS18B20[edit[0]][1]=short
				self.DS18B20[edit[0]][2]=unit_selection
				self.DS18B20[edit[0]][3]=id_selection
		dlg.Destroy()


	def delete_DS18B20(self,e):
		selected_DS18B20=self.list_DS18B20.GetFirstSelected()
		if selected_DS18B20==-1: 
			self.ShowMessage(_('Select a sensor to delete.'))
			return
		data=self.conf.get('ACTIONS', 'triggers')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for i in temp_list:
			if i[1]==self.DS18B20[selected_DS18B20][4]:
				self.read_triggers()
				self.ShowMessage(_('You have an action defined for this sensor. You must delete that action before deleting this sensor.'))
				return
		del self.DS18B20[selected_DS18B20]
		self.list_DS18B20.DeleteItem(selected_DS18B20)

	def apply_changes_DS18B20(self,e):
		for i in self.DS18B20:
			index=self.DS18B20.index(i)
			if self.list_DS18B20.IsChecked(index): self.DS18B20[index][5]='1'
			else: self.DS18B20[index][5]='0'
		self.conf.set('1W', 'DS18B20', str(self.DS18B20))
		self.start_1w()
		self.start_monitoring()
		self.read_datastream()
		self.read_triggers()
		self.SetStatusText(_('DS18B20 sensors changes applied and restarted'))

	def cancel_changes_DS18B20(self,e):
		self.read_DS18B20()
		self.SetStatusText(_('DS18B20 sensors changes cancelled'))
#Main#############################
if __name__ == "__main__":
	app = wx.App()
	MainFrame().Show()
	app.MainLoop()
