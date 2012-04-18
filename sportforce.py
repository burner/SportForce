#!/usr/bin/python2
# -*- coding: UTF-8 -*-

__version__ = "0.1"
__author__ = "Robert BuRnEr Schadek <rburners@gmail.com>"
__copyright__ = "Copyright © 2012 Robert BuRnEr Schadek"
__license__ = "GPL 3"
__appdispname__ = "Sport Force"
__appname__ = "sportforce"
__website__ = "http://github.com/burner/sportforce/"

import sys
import os
import gettext
import sqlite3
import threading
import random
gettext.install(__appname__)

try:
	import gobject
	import gtk
	import pygtk
	pygtk.require("2.0")
	PYGTK = True
except ImportError:
	PYGTK = False
	print "gtk not presend"
	sys.exit(1);

class SportForce(object):
	def removeItem(self, widget):
		it = self.sportList.get_selection()
		toRemove = it.get_selected()[0].get_value(it.get_selected()[1], 0)
		conn = sqlite3.connect('sportforce.db')
		cur = conn.cursor()
		cur.execute("DELETE FROM current WHERE type='%s'"%toRemove)
		conn.commit()

		self.sportList.get_model().remove(it.get_selected()[1])

	def inactive(self, widget):
		return

	def create_columns(self, treeView):
		rendererText = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Activity", rendererText, text=0)
		column.set_sort_column_id(0)	
		treeView.append_column(column)
		
		rendererText = gtk.CellRendererText()
		column = gtk.TreeViewColumn("current value", rendererText, text=1)
		column.set_sort_column_id(1)
		treeView.append_column(column)

		rendererText = gtk.CellRendererText()
		column = gtk.TreeViewColumn("minimal value", rendererText, text=2)
		column.set_sort_column_id(2)
		treeView.append_column(column)

		rendererText = gtk.CellRendererText()
		column = gtk.TreeViewColumn("maximal value", rendererText, text=3)
		column.set_sort_column_id(3)
		treeView.append_column(column)

		rendererText = gtk.CellRendererText()
		column = gtk.TreeViewColumn("growth value", rendererText, text=4)
		column.set_sort_column_id(4)
		treeView.append_column(column)

	def fill(self):
		liststore = gtk.ListStore(str, float, float, float, float)
		if not os.path.isfile("sportforce.db"):
			liststore.append(["pushups", 10.0, 5.0, 50.0, 0.1])
			liststore.append(["pullups", 6.0, 3.0, 20.0, 0.1])
			return liststore
		else:
			conn = sqlite3.connect('sportforce.db')
			cur = conn.cursor()
			cur.execute("SELECT * FROM current")
			rslt = cur.fetchone()
			while rslt is not None:
				liststore.append([rslt[0], rslt[1], rslt[2], rslt[3], rslt[4]])	
				rslt = cur.fetchone()

			return liststore

	def insertNewItem(self, widget):
		payload = (self.ac.get_text(), self.cur.get_text(), self.mn.get_text(), 
			self.mx.get_text(), self.gr.get_text())
		print payload	
		conn = sqlite3.connect('sportforce.db')
		cur = conn.cursor()
		stmt = "SELECT * FROM current WHERE type='%s'"%payload[0]
		print stmt
		cur.execute(stmt)
		if cur.fetchone() is not None:
			d = gtk.Dialog("An entry for type %s allready exists"%payload[0])
			d.show()
			return

		cur.execute("INSERT into current VALUES(?, ?, ?, ?, ?)", payload)
		conn.commit()

		self.newActWin.hide()

	def insertNewItemWidget(self, widget):
		self.newActWin = gtk.Window(gtk.WINDOW_TOPLEVEL)	
		hbox = gtk.HBox()
		vbox = gtk.VBox()
		vbox.pack_start(hbox)
		self.ac = gtk.Entry()
		self.ac.set_text("Activity (String)")
		self.ac.show()
		self.cur = gtk.Entry()
		self.cur.set_text("Current (Float)")
		self.cur.show()
		self.mn = gtk.Entry()
		self.mn.set_text("Minimal (Float)")
		self.mn.show()
		self.mx = gtk.Entry()
		self.mx.set_text("Maximal (Float)")
		self.mx.show()
		self.gr = gtk.Entry()
		self.gr.set_text("Growth (Float)")
		self.gr.show()
		hbox.pack_start(self.ac)
		hbox.pack_start(self.cur)
		hbox.pack_start(self.mn)
		hbox.pack_start(self.mx)
		hbox.pack_start(self.gr)
		s = gtk.Button("SAVE")
		s.connect("clicked", self.insertNewItem)
		vbox.show()
		s.show()
		vbox.pack_start(s)
		self.newActWin.add(vbox)
		hbox.show()
		self.newActWin.show()

	def makeAdjustmentWindow(self):
		self.startWin = gtk.Window(gtk.WINDOW_TOPLEVEL)
		liststore = self.fill()
		self.sportList = gtk.TreeView(liststore)
		self.sportList.connect("row-activated", self.inactive)
		self.sportList.set_rules_hint(True)
		self.create_columns(self.sportList)

		self.sportList.show()
		vbox = gtk.VBox()
		newAct = gtk.Button("New Activity")
		newAct.connect("clicked", self.insertNewItemWidget)
		newAct.show()
		remAct = gtk.Button("Remove Activity")
		remAct.connect("clicked", self.removeItem)
		remAct.show()
		vbox.pack_start(self.sportList)
		vbox.pack_start(newAct)
		vbox.pack_start(remAct)
		vbox.show()
		self.startWin.add(vbox)
		self.startWin.show()

	def makeTable(self):
		conn = sqlite3.connect('sportforce.db')
		cur = conn.cursor()
		cur.execute("CREATE TABLE current (type TEXT, current DEC, minimal DEC,"
			+ " maximal DEC, growth DEC)")
		cur.execute("CREATE TABLE save (type TEXT, cnt DEC, date DATETIME)")
		cur.execute("CREATE TABLE pref (dur INT)")
		conn.commit()

	def __init__(self):
		if not os.path.isfile("sportforce.db"):
			self.makeAdjustmentWindow()
			self.makeTable()
			
		self.handle_menu_mute = True
		self.pause = False
		#### Widgets ####
		#Tray icon
		self.tray_icon = gtk.StatusIcon()
		#Slider
		#Window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_decorated(False)
		self.window.set_skip_taskbar_hint(True)
		self.window.set_skip_pager_hint(True)
		self.window.set_border_width(3)

		self.tray_icon.set_from_file("sport.png")

		#Menu
		self.menu_mute = gtk.CheckMenuItem(_("Pause"))
		self.menu_mute.connect("activate", self.togglePause)
		menu_separator0 = gtk.MenuItem()
		menu_preferences = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
		menu_separator2 = gtk.MenuItem()
		menu_about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
		menu_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
		menu_quit.connect("activate", gtk.main_quit)
		gobject.timeout_add_seconds(10, self.popup)

		self.menu = gtk.Menu()
		self.menu.append(self.menu_mute)
		self.menu.append(menu_separator0)

		self.menu.append(menu_preferences)
		self.menu.append(menu_separator2)
		self.menu.append(menu_about)
		menu_about.connect("activate", self.on_menu_about_activate)
		self.menu.append(menu_quit)
		#### Signals ####
		#Tray icon
		self.tray_icon.connect("activate", self.on_tray_icon_activate)
		self.tray_icon.connect("button-release-event",
				self.on_tray_icon_button_release_event,)
		self.tray_icon.connect("scroll-event", self.on_tray_icon_scroll_event)
		self.tray_icon.connect("popup-menu", self.on_tray_icon_popup_menu)
		self.window.connect("focus-out-event", self.on_window_focus_out_event)

	def popup(self):
		conn = sqlite3.connect('sportforce.db')
		cur = conn.cursor()
		s = cur.execute("SELECT * FROM current")
		rslt = s.fetchone()
		sel = []
		while rslt is not None:
			sel.append(rslt)
			rslt = s.fetchone()

		sel = random.choice(sel)
		new = sel[1] + sel[4]
		if new < sel[3]:
			cur.execute("UPDATE current SET current = %f WHERE %s"%
				(new, sel[1]))
			conn.commit()

		d = gtk.Dialog("Do do")
		d.vbox.pack_start(gtk.Label("You have to do %d %s"%(int(new), sel[0])))
		d.show_all()
		d.run()
		gobject.timeout_add_seconds(10, self.popup)

	def togglePause(self, widget):
		self.pause = not self.pause
		if self.pause:
			gobject.timeout_add_seconds(1000000000000, self.popup)
		else:
			gobject.timeout_add_seconds(10, self.popup)

	def _set_win_position(self):
		screen, geometry, orient = self.tray_icon.get_geometry()
		#Calculate window position
		if orient == gtk.ORIENTATION_HORIZONTAL:
			if geometry.y < screen.get_height()/2: #Panel at TOP
				win_x = geometry.x
				win_y = geometry.y + geometry.width
			else:								  #Panel at BOTTOM
				win_x = geometry.x
				win_y = geometry.y - geometry.width - 150
		else:
			if geometry.x < screen.get_width():	#Panel at LEFT
				win_x = geometry.x + geometry.width
				win_y = geometry.y
			else:								  #Panel at RIGHT
				win_x = geometry.x - geometry.width - 32
				win_y = geometry.y
		#Move window
		self.window.move(win_x, win_y)

	def on_tray_icon_activate(self, widget):
		self.makeAdjustmentWindow()
		'''
		if self.window.get_visible():
			self.window.hide()
		else:
			self._set_win_position()
			self.window.show_all()
		'''

	def on_tray_icon_button_release_event(self, widget, event):
		return

	def on_tray_icon_scroll_event(self, widget, event):
		return

	def on_tray_icon_popup_menu(self, widget, button, time):
		self.menu.show_all()
		self.menu.popup(None, None, None, button, time)

	def on_slider_value_changed(self, widget):
		return

	def on_window_focus_out_event(self, widget, event):
		self.window.hide()

	def on_menu_mute_activate(self, widget):
		if self.handle_menu_mute:
			self._toggle_mute(False)

	def on_menu_mixer_activate(self, widget, command):
		os.popen(command)

	def on_menu_preferences_avtivate(self, widget):
		return

	def on_menu_about_activate(self, widget):
		aboutdlg = gtk.AboutDialog()
		aboutdlg.set_name(__appdispname__)
		aboutdlg.set_version(__version__)
		aboutdlg.set_copyright(__copyright__)
		aboutdlg.set_copyright(__license__)
		aboutdlg.set_website(__website__)
		aboutdlg.set_translator_credits(_("translator-credits"))
		aboutdlg.connect("response", self.on_aboutdlg_response)
		aboutdlg.show()

	def on_menu_quit_activate(self, widget):
		self.timer.cancel()
		gtk.main_quit()

	def on_aboutdlg_response(self, widget, response):
		if response < 0:
			widget.destroy()

if __name__ == "__main__":
	sportForce = SportForce()
	try:
		gtk.main()
	except KeyboardInterrupt:
		sys.exit(0)
