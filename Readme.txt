pyScanBookApp
 An application for Scanning and performing OCR on individual pages or a Book.

Features 
---------

A light weight gnome based GUI for organising the scanning and converting printed materials to text files. The application  supports a user to organise his scanned books images as text files in a folder named 'Books' in the home folder of the system. 
A user can easily scan papers or pages individually just by one key press. While scanning a book or pages in bulk amount, application creates a folder, and subsequent scanned pages are automatically added to this created folder. 

The application detects the ocr in the system and the user can specify the needed engine while scanning a book.
User can add/remove any book or pages at one click
User can select the sound engine, espeak or festival, if available in the system.
While reading, user can zoomin, zoom out or invert color of display

Requirements
------------
Gtk, python, espeak or festival, ocr ocropus or cuneiform

Usage
-----
Enter the folder where this application resides using cd command in terminal
to excecute the programme type at $python pyScanBook_alpha.py

Shortcuts
----------
Main/Books View Window
	Control N       -     New Page Scanning
	Control B       -     New Book Scanning
	Control T       -     Move Selected Book to Trash
	Control S       -     Settings (not available in this version)

Pages View Window
	Control R/Enter on selected page    -     Read Window
	Control A      				 -     Add New Page
	Control T       			 -     Move Selected Page to Trash
	Control H      				 -     Main/Books Window 

Read Window
	U 	-	  Up/ Back	
	Control N    	-	  Next Page
	Control P    	-     Previous Page
	Control+Shift+z -     Zoom In
	Shift+z      	-     Zoom In
	Control+z     	-     Zoom Original
	Control+I	-     invert Color
