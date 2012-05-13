#!/usr/bin/python


import subprocess,signal												#for running system commands on another thread
import gtk	
import os
import pango															#for zoom options
import commands															#for running system commands		


class pyScanBookApp(gtk.Window): 
	def __init__(self):
		super(pyScanBookApp, self).__init__()

#some app initialisations		
		self.set_title("pyScanBookApp")									
		self.set_size_request(900,500)
		self.set_position(gtk.WIN_POS_CENTER)

#connect quit to destroy app
		self.connect("destroy", gtk.main_quit)

#create Books directory in HomeFolder and exceot if already present		
		try:
			self.books_directory = os.path.realpath(os.path.expanduser('~/Books'))
			os.mkdir(self.books_directory,0700)
		except:
			pass

#Create the GUI MainWindow without main menu tobe shown first		
		self.vbox = gtk.VBox(False, 0)
		self.toolbar = gtk.Toolbar()
		self.vbox.pack_start(self.toolbar, False, False, 0)
		
		self.agr = gtk.AccelGroup()
		self.add_accel_group(self.agr)

		self.buttonList1 = []
		self.createButton('newPageButton',gtk.STOCK_NEW,'New Paper/Page','Scan a New Paper or Page',self.newPage,self.toolbar,"<Control>N")
		self.buttonList1.append(self.button)
		self.createButton('newBookButton',gtk.STOCK_DND_MULTIPLE,'New Book','Scan a new Book',self.newBook,self.toolbar,"<Control>B")
		self.buttonList1.append(self.button)
		self.createButton('deleteBookButton',gtk.STOCK_DND_MULTIPLE,'Delete Book','Delete a Book',self.deleteBook,self.toolbar,"<Control>T>")
		self.buttonList1.append(self.button)
		self.buttonList1[2].set_sensitive(False)
		self.createButton('settingsButton',gtk.STOCK_PREFERENCES,'Settings','Change Settings',self.settings,self.toolbar,"<Control>S")
		self.buttonList1.append(self.button)
		self.buttonList1[3].set_sensitive(False)
		self.pageIcon = self.get_icon(gtk.STOCK_DND)
		self.bookIcon = self.get_icon(gtk.STOCK_DND_MULTIPLE)
		
		self.sw = gtk.ScrolledWindow()
		self.sw.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.vbox.pack_end(self.sw, True, True, 0)
		
		self.store = self.create_store()
		self.fill_store()
		self.iconView = gtk.IconView(self.store)
		self.iconView.set_text_column(0)
		self.iconView.set_pixbuf_column(1)		
		self.sw.add(self.iconView)
		self.iconView.grab_focus()		
		self.iconView.connect("item-activated", self.on_item_activated)
		self.iconView.connect("selection-changed", self.selectionchanged)
		self.add(self.vbox)
#some initialisations		
		self.zoom = 16
		self.zoomCount = 0
		self.playing = 0
		self.ocr_engine = 'tesseract'
		self.show_all()

#check whether selected icon is file/folder		
	def selectionchanged(self,item):
		if item.get_selected_items():
			self.buttonList1[2].set_sensitive(True)
			self.index=item.get_selected_items()[0][0]
			os.chdir(self.books_directory)
			dirlist=commands.getoutput('ls')
			self.reallist=dirlist.splitlines()
		else:
			self.buttonList1[2].set_sensitive(False)

#if clicked on a file open the contents with some toolbar buttons else open the directory and list files		   
	def on_item_activated(self, widget, item):
		self.item = item[0]
		self.model = widget.get_model()
		self.path = self.model[item][0]
		isDir = self.model[item][2]
		if not isDir:
			self.openTextEditor(widget)
			return
		self.set_title(self.path)
		self.books_directory = self.books_directory + os.path.sep + self.path
		self.fill_store()
		self.buttonList2 = []
		self.createButton('readButton',gtk.STOCK_INDEX,'Read ','Read or Edit the Selected Page',self.read,self.toolbar,"<Control>R")
		self.buttonList2.append(self.button)
		self.createButton('AddButton',gtk.STOCK_ADD,'Add Page','Scan a page of this Book',self.addpage,self.toolbar,"<Control>A")
		self.buttonList2.append(self.button)
		self.createButton('DeleteButton',gtk.STOCK_REMOVE,'Remove Page','Remove a page of this Book',self.remove,self.toolbar,"<Control>T>")
		self.buttonList2.append(self.button)
		self.createButton('HomeButton',gtk.STOCK_HOME,'Books Home','Back to Books Folder',self.home,self.toolbar,"<Control>H")
		self.buttonList2.append(self.button)
		self.buttonList2[-1].set_label('UP')
		self.showhide(self.buttonList2,True)
		self.showhide(self.buttonList1,False)
		
#populate the toolbar with media+accessible options to see clearly or hear 
	def openTextEditor(self,widget):
		self.toolbar2 = gtk.Toolbar()
		self.hboxtoolbar = gtk.HBox(False, 0)
		self.combo = gtk.combo_box_new_text()
		#self.combo.append_text('Festival')
		self.combo.append_text('eSpeak')
		self.combo.set_active(0)
		self.sound_engine='eSpeak'
		self.hboxtoolbar.pack_start(self.combo, False, False, 0)
		self.hboxtoolbar.pack_start(self.toolbar2, True, True, 0)
		#self.combo.connect("changed", self.changed)
		self.vbox.pack_start(self.hboxtoolbar, False, False, 0)
		self.hboxtoolbar.show()
		self.toolbar2.show()
		self.combo.show()
		self.buttonList3 = []
		self.createButton('upButton',gtk.STOCK_GO_UP,'UP','Back to Pages',self.up,self.toolbar,"U")
		self.buttonList3.append(self.button)
		self.createButton('previousButton',gtk.STOCK_GO_BACK,'Previous Page','Navigate to Previous Page of this Book',self.previous,self.toolbar,"<Control>P")
		self.buttonList3.append(self.button)
		self.createButton('nextButton',gtk.STOCK_GO_FORWARD,'Next Page','Navigate to Next Page of this Book',self.next,self.toolbar,"<Control>N")
		self.buttonList3.append(self.button)
		self.createButton('zoomInButton',gtk.STOCK_ZOOM_IN,'Zoom In','Zoom the Page',self.zoomIn,self.toolbar,"<Control><Shift>Z")
		self.buttonList3.append(self.button)
		self.createButton('zoomOriginalButton',gtk.STOCK_ZOOM_100,'Zoom Original','1:1',self.zoomOriginal,self.toolbar,"<Shift>Z")
		self.buttonList3.append(self.button)
		self.createButton('zoomOutButton',gtk.STOCK_ZOOM_OUT,'Zoom Out','Zoom Out the page',self.zoomOut,self.toolbar,"<Control><Alt>z")
		self.buttonList3.append(self.button)
		
		self.createButton('windowStyle',gtk.STOCK_SELECT_COLOR,'Invert Colours','Invert the contrast of the page',self.contrast,self.toolbar,"<Control>i")
		self.buttonList3.append(self.button)
		self.toggle = gtk.ToggleToolButton('self.buttonList3[-1]')
		self.toggle.set_active(False)
		self.createButton('play',gtk.STOCK_MEDIA_PLAY,'Play','Hear this page',self.play,self.toolbar2,"P")
		self.buttonList3.append(self.button)
		self.createButton('pause',gtk.STOCK_MEDIA_PAUSE,'Pause','Pause Play',self.pause,self.toolbar2,"P",-1)
		self.buttonList3.append(self.button)
		
		self.createButton('stop',gtk.STOCK_MEDIA_STOP,'Stop','Stop Play',self.stop,self.toolbar2,"S")
		self.buttonList3.append(self.button)
		self.buttonList3[9].set_sensitive(False)
		
		self.showhide(self.buttonList3,True)
		self.buttonList3[8].hide()
		self.showhide(self.buttonList2,False)
		self.buttonList2[3].set_label('Books Home')
		self.buttonList2[3].show()
		self.sw.hide()
		self.sw.remove(self.iconView)
		try:
			#print os.path.join(self.books_directory ,self.path)
			self.textview = gtk.TextView()
			pangoFont = pango.FontDescription('Sans 15')
			self.textview.modify_font(pangoFont)
			self.textbuffer = self.textview.get_buffer()
			self.sw.add(self.textview)
			self.sw.show()
			self.textview.set_can_focus(False)
			self.textview.show()
			self.set_title(os.path.join(self.books_directory ,self.path))
			self.loadfile((os.path.join(self.books_directory ,self.path)),'r')
		except:
			pass

#function opens a file, retrievs data and finally closes it			
	def loadfile(self,filename,mode):
		self.openfilename =filename
		fileopen = open(filename, mode)
		if fileopen:
			string = fileopen.read()
			fileopen.close()
			self.textbuffer.set_text(string)

#get the gtk icon set from sytem		
	def get_icon(self, name):
		theme = gtk.icon_theme_get_default()
		return theme.load_icon(name, 48, 0)

#function populates the mainwindow with booknames sorted ascending		
	def create_store(self):
		store = gtk.ListStore(str, gtk.gdk.Pixbuf, bool)
		store.set_sort_column_id(0, gtk.SORT_ASCENDING)
		return store

#populates the mainwindow with folder type/ file type 		
	def fill_store(self):
		try:
				os.chdir(self.books_directory)
				os.system('rm temp.txt')
		except:
				pass
		
		self.store.clear()
		if self.books_directory == None:
			return
		for fl in os.listdir(self.books_directory):

			if not fl[0] == '.':
			   if os.path.isdir(os.path.join(self.books_directory, fl)):
				   self.store.append([fl, self.bookIcon, True])
			   else:
				   pass
				   self.store.append([fl, self.pageIcon, False])

#check if the page is already present inside the book folder otherwise increment page number
	def checkpage(self):
		print "checking Page"
		try:			
			txt=commands.getoutput('ls P*.txt')
			fill=txt.splitlines()
			fillNo=[]
			for i in fill:
				split=i.split('.')
				split2=split[0].split('Page')
				fillNo.append(int(split2[1]))
				fillNo.sort()
			last_name=(fill[len(fill)-1])
			#print last_name,"lastname",fill,fill[1]		
			count=int(last_name[-5])
			#print last_name[-5],count,"print"
			type(count)
			#self.no=count+1
			self.no=fillNo[-1]+1
			#print self.no
			return self.no
		except:
			self.no=1

#function called when activating newpage button on mainwindow. these scanned pages are saved in '1Pages' directory				
	def newPage(self,widget):
		try:
			self.pages_directory = os.path.realpath(os.path.expanduser('~/Books/1Pages'))
			os.mkdir(self.pages_directory,0700)
		except:
			pass
		self.path = os.chdir(self.books_directory+"/1Pages")
		try:
			self.checkScanner()	
			if self.scanner=='OK':
				print "newpage"
				self.checkpage()
				#self.ocr_engine = 'tesseract'
				self.dependancy()
				self.scan_on()
				print "OK"		
		except:
			print "not done"
			
#function to delete a book directory from the system			
	def deleteBook(self,item):
		#if self.selection!= 1:
		path=(os.path.realpath(os.path.expanduser('~/Books/'+'%s'%self.reallist[self.index])))
		os.system('rm -r %s'%path)	
		self.fill_store()

#function called when newBook button activated.		
	def newBook(self,widget):
		try:
			self.checkScanner()	
			if self.scanner=='OK':
				self.dependancy()
				label1 = gtk.Label('Book Name')
				bookNameLine = gtk.Entry(20)
				label2 = gtk.Label('Select Engine')
				liststore = gtk.ListStore(str)    
				for item in self.lis:
					liststore.append([item]) 
				engineCombo = gtk.ComboBoxEntry(liststore)
				#engineCombo.set_sensitivity(False)
				engineCombo.set_button_sensitivity(gtk.SENSITIVITY_ON)
				engineCombo.set_focus_on_click(True)
				#engineCombo.set_active(0)
				table = gtk.Table(3, 2, True)
				table.attach(label1, 0, 1, 0, 1)
				table.attach(bookNameLine, 1, 2, 0, 1)
				table.attach(label2, 0, 1, 1, 2)
				table.attach(engineCombo, 1, 2, 1, 2)
				engineCombo.connect("changed", self.changed_item)
#dialog box to get user preference
				self.dia = gtk.Dialog("Scan a Book Dialog", None, 0,(gtk.STOCK_CANCEL,gtk.RESPONSE_REJECT,gtk.STOCK_OK,gtk.RESPONSE_ACCEPT))
				self.dia.set_geometry_hints(self.dia,350,250,350,250)
				self.dia.vbox.pack_start(gtk.Label('Please Enter Book Name and \nSelect the Ocr Engine'),True,True,0) 
				
				self.dia.vbox.pack_end(table,True,False,0)
				self.dia.show_all() 
				response = self.dia.run()
				if response ==gtk.RESPONSE_ACCEPT:
					#print 'run', 
					self.text = bookNameLine.get_text()
					#print self.text
					if self.text == "" or os.path.isdir(os.path.realpath(os.path.expanduser('~/Books/'+'%s'%self.text))):
						msg = gtk.MessageDialog(None,type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK,)
						msg.set_markup('Please Dont Leave the<b> Book name</b> Blank or Name <b> %s </b> Already Exists:'%self.text)
						if msg.run():
							msg.destroy()
							self.dia.destroy()
							self.newBook(widget)
							return
					else:
						os.system("espeak 'Folder for %s created'"%self.text)
						self.path=(os.path.realpath(os.path.expanduser('~/Books/'+'%s'%self.text)))
						
						os.mkdir(self.path,0700)
						self.fill_store()
						self.dia.destroy()
						#print self.ocr_engine
						os.chdir('%s'%self.path)
						self.no=1
						self.scan_on()
				elif response == gtk.RESPONSE_REJECT:
					self.dia.destroy()	   
		except:
			print "not done"

#scan fuction using scanimage command with default setting			
	def scan_on(self):
		os.system("espeak 'scanning started, please wait'")
		scanimage=1        
		
		while scanimage!=0:
			#scanimage=os.system('scanimage -x 1000 -y 1000 > temp.pnm')
			scanimage=os.system('scanimage -x 1000 -y 1000 --resolution 200 > temp.pnm')
		os.system('convert temp.pnm temp.png')
		
		if self.ocr_engine=='tesseract':
			#print 'ok'
			os.system('ocroscript recognize temp.png > temp.html')
			os.system('ls')
			#print self.no
			os.system('html2text -o Page%d.txt temp.html'%self.no)    
			os.system('rm temp.*')
			self.fill_store() 
		else:# self.ocr_engine=='cuneiform':
			os.system('cuneiform -f text -l eng -o Page%d.txt temp.png'%self.no)
			os.system('rm temp.*')
			self.fill_store()
		os.system("espeak 'page saved as Page%d'"%self.no)
		table = gtk.Table(3, 2, True)
		dia = gtk.Dialog("Scan a Book Dialog", None, 0,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OK, gtk.RESPONSE_OK))
		dia.set_geometry_hints(dia,300,100,300,100)
		dia.vbox.pack_start(gtk.Label('Do You Want To Continue Scanning ...'),True,True,0)
		dia.show_all()
		button = gtk.Button("Run Dialog")
		button.show()
		response=dia.run()    
		if response == gtk.RESPONSE_OK :  
			try:
				os.chdir('%s'%self.path) 
			except:
				pass
			self.no+=1
			dia.destroy()
			self.scan_on()
		elif response == gtk.RESPONSE_CANCEL :            
		   dia.destroy()

#dynamically updates folder		   				
	def changed_item(self, widget):
			self.ocr_engine=widget.get_active_text()
			#print self.ocr_engine

#check for the OCR tools present in the system			 
	def dependancy(self):
		self.lis = []
		dep1=commands.getoutput('which tesseract')
		dep2=commands.getoutput('which cuneiform')
		if os.path.exists(dep1):
			self.lis.append('tesseract')
		elif os.path.exists(dep1):
			self.lis.append('cuniform')
		else:
			info = gtk.MessageDialog(self,gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,gtk.BUTTONS_OK, "No OCR Engines Were Found On Your System, you can just scan")
			if info.run():
				info.destroy()

		return self.lis

#function to continue next page scan	
	def scan_continue(self):
		table = gtk.Table(3, 2, True)
		dia = gtk.Dialog("Scan a Book Dialog", None, 0,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OK, gtk.RESPONSE_OK))
		dia.set_geometry_hints(dia,300,100,300,100)
		dia.vbox.pack_start(gtk.Label('Do You Want To Continue Scanning ...'),True,True,0)
		dia.show_all()		
		self.response=dia.run()	 
		if self.response == gtk.RESPONSE_OK :			 
			self.no+=1
			dia.destroy()
			self.scan_on()			
			return
		elif self.response == gtk.RESPONSE_CANCEL :			 
			dia.destroy()

#dynamically remove files deleted				
	def remove(self,widget):
		path= self.books_directory+'/'+self.reallist[self.index]
		os.system('rm %s'%path)	
		self.fill_store()
#settings function...yet to come..:-P	
	def settings(self,widget):
		print 'settings'	

#while Home button clicked, following happens..!		
	def home(self,widget):
		self.set_title('Books Home')
		self.showhide(self.buttonList1,True)
		self.showhide(self.buttonList2,False)
		if self.buttonList2[3].get_label() == 'Books Home':
			self.toolbar2.hide()
			self.showhide(self.buttonList3,False)
			self.combo.hide()
			self.sw.remove(self.textview)
			self.sw.add(self.iconView)
			self.sw.show()
		self.books_directory = os.path.realpath(os.path.expanduser('~/Books'))
		self.fill_store()
		try:
			self.playing = 0
			self.ply.send_signal(signal.SIGKILL)
		except:
			pass

#if read button clicked...			
	def read(self,widget):
		
		self.path = self.reallist[self.index]
		self.openfilename = self.path
		self.openTextEditor(widget)
		#self.index +=1 
		
#go one level up when up button clicked		
	def up(self,widget):
		self.showhide(self.buttonList2,True)
		self.showhide(self.buttonList1,False)
		self.sw.remove(self.textview)
		self.sw.add(self.iconView)
		self.sw.show()
		try:
			self.showhide(self.buttonList3,False)
			self.combo.hide()
			self.toolbar2.hide()
			self.playing = 0
			self.ply.send_signal(signal.SIGKILL)
		except:
			return
		self.books_directory = self.books_directory + os.path.sep 
		self.fill_store()

#add a page to this book	
	def addpage(self,widget):
		path=os.chdir(self.books_directory)		
		print "Page added"
		
		try:
			self.checkScanner()	
			if self.scanner=='OK':
				self.checkpage()
				self.ocr_engine = 'tesseract'
				self.scan_on()	
		except:
			print "not done"

#go to previous page of this book	
	def previous(self,widget):
		bookList = []
		for fl in os.listdir(os.path.dirname(self.openfilename)):
			bookList.append(fl)
		bookList.sort()
		self.index -= 1
		if self.index < 0:
			 md = gtk.MessageDialog(self,gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,gtk.BUTTONS_CLOSE, "No More Pages")
			 md.run()
			 md.destroy()
			 self.index += 1
		else:
			try:
				self.playing = 0
				self.ply.send_signal(signal.SIGKILL)
			except:
				pass
				
			self.buttonList3[8].hide()
			self.buttonList3[7].show()
			self.set_title(os.path.join(os.path.dirname(self.openfilename),bookList[self.index]))
			self.loadfile(os.path.join(os.path.dirname(self.openfilename),bookList[self.index]),'r')

#go to next page of this book
	def next(self,widget):
		bookList = []
		for fl in os.walk(os.path.dirname(self.openfilename)).next()[2]:
			bookList.append(fl)
		bookList.sort()
		self.index += 1
		
		if self.index >= len(bookList):
			# print 'No more Pages'
			 md = gtk.MessageDialog(self,gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,gtk.BUTTONS_CLOSE, "No More Pages")
			 md.run()
			 md.destroy()
			 self.index -= 1
		else:
			try:
				self.playing = 0
				self.ply.send_signal(signal.SIGKILL)
			except:
				pass
			self.buttonList3[8].hide()
			self.buttonList3[7].show()
			self.set_title(os.path.join(os.path.dirname(self.openfilename),bookList[self.index]))
			self.loadfile(os.path.join(os.path.dirname(self.openfilename),bookList[self.index]),'r')

#Zoom the contents for partially blind					
	def zoomIn(self,widget):
		self.zoom =self.zoom + 15
		pangoFont = pango.FontDescription('Sans'+' '+str(self.zoom))
		self.textview.modify_font(pangoFont)
		self.zoomCount += 1
		print self.zoom

#Zoomout the contents if over zoomed		
	def zoomOut(self,widget):
		if self.zoom < 30:
			pangoFont = pango.FontDescription('Sans 15')
			print self.zoom
			return
		self.zoom = self.zoom - 15
		pangoFont = pango.FontDescription('Sans'+' '+str(self.zoom))
		self.textview.modify_font(pangoFont)
		print self.zoom		

#back to default font and font size		
	def zoomOriginal(self,widget):
		pangoFont = pango.FontDescription('Sans 15')
		self.textview.modify_font(pangoFont)
		self.zoom = 15

#while play button clicked, play the file diplayed by espeak or by festival		
	def play(self,widget):
		self.buttonList3[8].show()
		self.buttonList3[7].hide()
		self.buttonList3[9].set_sensitive(True)
		if self.playing == 1:
			self.ply.send_signal(signal.SIGCONT)
		else:
			if self.sound_engine=='eSpeak':
				self.ply = subprocess.Popen(['espeak','-f',self.openfilename])
			elif self.sound_engine=='Festival':
				self.ply = subprocess.Popen(['festival','--tts',self.openfilename])
				#self.playtoggle.set_icon_name(gtk.STOCK_MEDIA_PLAY)

#pause the play thread		
	def pause(self,widget):
		self.buttonList3[8].hide()
		self.buttonList3[7].show()
		self.playing = 1
		self.ply.send_signal(signal.SIGSTOP)

#stop the current process		
	def stop(self,widget):
		self.buttonList3[8].hide()
		self.buttonList3[7].show()
		self.playing = 0
		self.ply.send_signal(signal.SIGKILL)
		
#interchange font color and background color
	def contrast(self,widget):
		if self.toggle.get_active() == False:
			self.textview.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))
			self.textview.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
			self.toggle.set_active(True)
		else:
			self.textview.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
			self.textview.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))
			self.toggle.set_active(False)

#show or hide the buttons on each page 			
	def showhide(self,buttonList,boolean):
		buttons = 0
		while buttons < len(buttonList):
			if boolean == True:
				buttonList[buttons].show()
			else:
				buttonList[buttons].hide()
			buttons +=1

#function to create a button			
	def createButton(self,button,icon,label,tip,slot,toolbar,shortcut="",position = -1):
		self.button=gtk.ToolButton(icon)
			
		self.button.set_label(label)
		self.button.set_tooltip_text(tip)
		self.button.set_is_important(True)
		self.button.set_sensitive(True)
		toolbar.insert(self.button,position)
		self.button.connect("clicked", slot)
		key, mod = gtk.accelerator_parse(shortcut)
		self.button.add_accelerator("clicked",self.agr, key,mod, gtk.ACCEL_VISIBLE)
		return self.button

#check scanner connected and working...!
	def checkScanner(self):
		os.system('sane-find-scanner -q | wc -l > temp.txt')
		if file('temp.txt','r').readline(1) == '0' :   																	 
			md = gtk.MessageDialog(self,gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,gtk.BUTTONS_CLOSE, "No Scanner Found")
			md.run()
			md.destroy()
		else:
			self.scanner='OK'
   		 	
	def changed(self,widget):
		self.buttonList3[7].show()
		self.buttonList3[8].hide()
		self.playing = 0
		self.ply.send_signal(signal.SIGKILL)
		self.sound_engine=self.combo.get_active_text()
		#print self.sound_engine
		

#run the pyqt app
pyScanBookApp()
gtk.main()
