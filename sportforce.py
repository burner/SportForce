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

filename = ".sportforce.db"

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
		conn = sqlite3.connect(filename)
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
		if not os.path.isfile(filename):
			conn = sqlite3.connect(filename)
			cur = conn.cursor()
			cur.execute("INSERT into current VALUES(?, ?, ?, ?, ?)", ("pushups", 13.0, 5.0, 50.0, 0.2))
			cur.execute("INSERT into current VALUES(?, ?, ?, ?, ?)", ("pullups", 6.0, 3.0, 20.0, 0.2))
			conn.commit()
			liststore.append(["pushups", 10.0, 5.0, 50.0, 0.1])
			liststore.append(["pullups", 6.0, 3.0, 20.0, 0.1])
			return liststore
		else:
			conn = sqlite3.connect(filename)
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
		conn = sqlite3.connect(filename)
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
		conn = sqlite3.connect(filename)
		cur = conn.cursor()
		cur.execute("CREATE TABLE current (type TEXT, current DEC, minimal DEC,"
			+ " maximal DEC, growth DEC)")
		cur.execute("CREATE TABLE save (type TEXT, cnt DEC, date DATETIME)")
		cur.execute("CREATE TABLE pref (dur INT)")
		conn.commit()

	def __init__(self):
		if not os.path.isfile(filename):
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

		self.tray_icon.set_from_file("/usr/share/sport.png")

		#Menu
		self.menu_mute = gtk.CheckMenuItem(_("Pause"))
		self.menu_mute.connect("activate", self.togglePause)
		menu_separator0 = gtk.MenuItem()
		menu_preferences = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
		menu_separator2 = gtk.MenuItem()
		menu_about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
		menu_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
		menu_quit.connect("activate", gtk.main_quit)
		self.activateCounter()

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

	def activateCounter(self):
		time = 40*60
		if len(sys.argv) > 1:
			try:
				time = int(sys.argv[1]) * 60
				print time
			except:
				print "fuck"
				None
		gobject.timeout_add_seconds(time, self.popup)

	def popup(self):
		insults = ["Get moving", "Fat people have less sex.", "Move your ass", "Move your lazy ass", 
			"Move your fat ass", "Move your slow ass", "Move your ugly ass", "Ha, another donout is that it",
			"You're so fat when you sit around the house, you sit AROUND the HOUSE",
			"You're so fat a picture of you would fall off the wall!",
			"You're  so  fat  if  you  weighed  five  more  pounds,  you could get group insurance!",
			"You're  so  fat  you  get  clothes in three sizes:  extra large, jumbo, and oh-my-god-it's-coming-towards-us!",
			"You're so fat if you got your shoes shined, you'd have to take his word for it!",
			"Your  so  fat,  that you have to strap a beeper on your belt to warn people you are backing up.",
			"Your so fat, that you have to use a mattress as a maxi-pad.",
			"Get moving",
			"Hey!! they made a song about your weight 8675309",
			"Can fat people go skinny dipping?",
			"At fat camp, the guys have bigger boobs",
			"Bored as a fat person without food",
			"Fat people are harder to kidnap",
			"Never under estimate fat people in large groups",
			"Dear Lord,",
			"If you can't make me SKINNY, Please make my friends FAT!",
			"I would probably cry too, if I had a stomach the size of the ocean blue!",
			"Only in America are \"poor\" people fat.",
			"One day a woman asked her daughter to go get some jellyrolls. The girl went to the bakery and ordered all of the jellyrolls that the bakery had. Then she stuffed them all in her mouth and swallowed. When she got home her mom asked where the jellyrolls were. The girl lifts up her shirt and says here, these are the jelly rolls.",
			"Losers quit when they're tired. Winners quit when they've won.",
			"Nobody who ever gave his best regretted it.",
			"The greatest efforts in sports came when the mind is as still as a glass lake.",
			"Nobody's a natural. You work hard to get good and then work to get better. It's hard to stay on top.",
			"You are never really playing an opponent. You are playing yourself, your own highest standards, and when you reach your limits, that is real joy.",
			"It's not so important who starts the game but who finishes it.",
			"Concentration is the ability to think about absolutely nothing when it is absolutely necessary.",
			"One man practicing sportsmanship is far better than fifty preaching it.",
			"Pain is temporary. It may last a minute, or an hour, or a day, or a year, but eventually it will subside and something else will take its place. If I quit, however, it lasts forever.",
			"Losers visualize the penalties of failure, but winners visualize the rewards of success.",
			"The strength of the group is the strength of the leaders.",
			"If you are going to be a champion, you must be willing to pay a greater price.",
			"Success is about having, excellence is about being. Success is about having money and fame, but excellence is being the best you can be.",
			"The harder you work, the harder it is to surrender.",
			"You can't make a great play unless you do it first in practice.",
			"Never let your head hang down. Never give up and sit down and grieve. Find another way.",
			"Things that hurt, instruct.",
			"Everybody pulls for David, nobody roots for Goliath.",
			"One man can be a crucial ingredient on a team, but one man cannot make a team.",
			"When I was young, I never wanted to leave the court until I got things exactly correct. My dream was to become a pro.",
			"My responsibility is getting all my players playing for the name on the front of the jersey, not the one on the back.",
			"Good, better, best. Never let it rest. Until your good is better and your better is best.",
			"The pitcher has got only a ball. I've got a bat. So the percentage of weapons is in my favor and I let the fellow with the ball do the fretting.",
			"During my 18 years I came to bat almost 10,000 times. I struck out about 1,700 times and walked maybe 1,800 times. You figure a ballplayer will average about 500 at bats a season. That means I played seven years without ever hitting the ball.",
			"You owe it to yourself to be the best you can possible be - in baseball and in life.",
			"It takes a lot of hard work and dedication just like any pro sport. Especially for beach volleyball you don't have to be tall or as fast as other sports. You just have to have the skills.",
			"Make sure that team members know they are working with you, not for you.",
			"Leadership, like coaching, is fighting for the hearts and souls of men and getting them to believe in you.",
			"What makes a good coach? Complete dedication.",
			"I learn teaching from teachers. I learn golf from golfers. I learn winning from coaches.",
			"You can motivate by fear, and you can motivate by reward. But both those methods are only temporary. The only lasting thing is self motivation.",
			"My responsibility is leadership, and the minute I get negative, that is going to have an influence on my team.",
			"In the end, the game comes down to one thing: man against man. May the best man win.",
			"Victory belongs to the most persevering.",
			"You are never really playing an opponent. You are playing yourself, your own highest standards, and when you reach your limits, that is real joy.",
			"A life of frustration is inevitable for any coach whose main enjoyment is winning.",
			"Every game is an opportunity to measure yourself against your own potential.",
			"It is how you show up at the showdown that counts.",
			"Without self-discipline, success is impossible, period.",
			"If you aren't going all the way, why go at all?",
			"If you don't practice you don't deserve to win.",
			"If you ask me anything I don't know, I'm not going to answer.",
			"You can always become better.",
			"I've always believed that if you put in the work, the results will come.",
			"If you don't invest very much, then defeat doesn't hurt very much and winning is not very exciting.",
			"The spirit, the will to win, and the will to excel are the things that endure. These qualities are so much more important than the events that occur.",
			"The difference between the impossible and the possible lies in a man's determination.",
			"There are only two options regarding commitment; you're either in or you're out. There's no such thing as life in-between.",
			"The difference between a successful person and others is not a lack of strength, not a lack of knowledge, but rather in a lack of will.",
			"The man who has no imagination has no wings.",
			"I always turn to the sports section first. The sports page records people's accomplishments; the front page has nothing but man's failures.",
			"The difference between the old ballplayer and the new ballplayer is the jersey. The old ballplayer cared about the name on the front. The new ballplayer cares about the name on the back.",
			"If a tie is like kissing your sister, losing is like kissing your grandmother with her teeth out.",
			"The fewer rules a coach has, the fewer rules there are for players to break.",
			"We didn't lose the game; we just ran out of time.",
			"When we played, World Series checks meant something. Now all they do is screw up your taxes.",
			"The more you sweat in practice, the less you bleed in battle.",
			"I wanted to have a career in sports when I was young, but I had to give it up. I'm only six feet tall, so I couldn't play basketball. I'm only 190 pounds, so I couldn't play football. And I have 20-20 vision, so I couldn't be a referee.",
			"Playing polo is like trying to play golf during an earthquake.",
			"The breakfast of champions is not cereal, it's the opposition.",
			"I figure practice puts your brains in your muscles.",
			"An athlete cannot run with money in his pockets. He must run with hope in his heart and dreams in his head.",
			"In play there are two pleasures for your choosing. One is winning, and the other losing.",
			"All sports are games of inches.",
			"Most people give up just when they're about to achieve success. They quit on the one yard line. They give up at the last minute of the game, one foot from a winning touchdown.",
			"Pain is nothing compared to what it feels like to quit."]

		conn = sqlite3.connect(filename)
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
			print "UPDATE current SET current = %f WHERE type='%s'"%(new, sel[0])	
			cur.execute("UPDATE current SET current = %f WHERE type='%s'"%
				(new, sel[0]))
			conn.commit()

		d = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
			gtk.BUTTONS_CLOSE,random.choice(insults))
		if not self.pause:
			d.vbox.pack_start(gtk.Label("You have to do %d %s"%(int(new), sel[0])))
			d.show_all()
			d.run()
			d.destroy()

		self.activateCounter()

	def togglePause(self, widget):
		self.pause = not self.pause
		#if self.pause:
		#	gobject.timeout_add_seconds(60*60*24, self.popup)
		#else:
		#	self.activateCouter()

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
	os.chdir(os.path.expanduser('~'))
	sportForce = SportForce()
	try:
		gtk.main()
	except KeyboardInterrupt:
		sys.exit(0)
