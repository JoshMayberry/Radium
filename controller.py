__version__ = "0.0.1"

import GUI_Maker

if (__name__ == "__main__"):
	isMain = True
else:
	isMain = False

class GUI_Builder():
	def __init__(self):
		self.gui = GUI_Maker.build()

	@GUI_Maker.wrap_showError(makeDialog = not isMain)
	def buildGUI(self):
		"""The GUI build routine.

		Example Input: buildGUI()
		"""

		self.createWindows()
		self.buildMainWindow()

	def createWindows(self):
		"""Creates all the window frames before they are built.
		This is because frames that would have been created first may need to address frames that would have been created after.

		Example Input: createWindows()
		"""

		self.frame_mainMenu = self.gui.addWindow(label = "mainMenu",    title = f"Main Menu v.{__version__}")

	def addCommonMenu(self, myFrame):
		"""Makes a common menu for all frames.

		Example Input: addCommonMenu(self.frame_mainMenu)
		"""
		with myFrame.addMenu(text = "&File") as myMenu:
			with myMenu.addMenuItem(text = "Exit") as myMenuItem:
				myMenuItem.addToolTip("Closes the software")
				myMenuItem.setFunction_click(myFunction = myFrame.onExit)
			
			with myMenu.addMenuItem(text = "Save", label = "menuUpdateLocalDatabase") as myMenuItem:
				myMenuItem.addToolTip("Save changes made to local database")
			# 	myMenuItem.setFunction_click(myFunction = self.onSave)

			myMenu.addMenuSeparator()

			if (myFrame != self.frame_mainMenu):
				with myMenu.addMenuItem(text = "Main Menu") as myMenuItem:
					myMenuItem.addToolTip("Returns to the main menu")
					myMenuItem.setFunction_click(myFunction = myFrame.onSwitchWindow, myFunctionArgs = self.frame_mainMenu)

		with myFrame.addMenu(text = "&Security") as myMenu:
			with myMenu.addMenuItem(text = "Login", label = "menuLogin") as myMenuItem:
				myMenuItem.addToolTip("Allows the user to edit things and enables locked options")
				# myMenuItem.setFunction_click(myFunction = self.onLogin)
			
			with myMenu.addMenuItem(text = "Logout", label = "menuLogout") as myMenuItem:
				myMenuItem.addToolTip("Keeps the user from editing things and disables some options")
				# myMenuItem.setFunction_click(myFunction = self.onLogout)

		with myFrame.addMenu(text = "&Settings") as myMenu:
			with myMenu.addMenuItem(text = "User Settings", label = "menuUserSettings") as myMenuItem:
				myMenuItem.addToolTip("View and change various parameters for how this software operates")
				# myMenuItem.setFunction_click(myFunction = self.frame_16.onShowWindow)

		# with myFrame.addMenu(text = "&Utilities") as myMenu:			
		# 	with myMenu.addMenuItem(text = "Debugging", label = "menuDebugging", check = True, default = self.debugging, enabled = self.enableDebugging) as myMenuItem:
		# 		myMenuItem.addToolTip("If debugging information should be printed to the cmd window and/or written in the cmd log")
		# 		myMenuItem.setFunction_click(myFunction = self.onSetDebugging)

	def buildMainWindow(self):
		"""Creates the main window.

		Example Input: buildMainWindow()
		"""

		with self.frame_mainMenu as myFrame:
			#Initialize GUI
			myFrame.setMinimumFrameSize(size = (200, 200))
			myFrame.addStatusBar()
			# myFrame.setStatusText(self.defaultStatus)

			#Build menu bar
			self.addCommonMenu(myFrame)

			#Setup for content
			with myFrame.addSizerGridFlex(rows = 4, columns = 1) as mainSizer:
				mainSizer.growFlexColumnAll()
				mainSizer.growFlexRowAll()

				with mainSizer.addButton("Create Submission") as myWidget:
					myWidget.addToolTip("ECreate a submission")
					myWidget.setFunction_click(myFunction = myFrame.onSwitchWindow, myFunctionArgs = self.frame_editCards)

				with mainSizer.addButton("View Submissions") as myWidget:
					myWidget.addToolTip("EView submitted reports")
					myWidget.setFunction_click(myFunction = myFrame.onSwitchWindow, myFunctionArgs = self.frame_editFormats)

class Controller(GUI_Builder):
	def __init__(self):
		#Initialize inherited modules
		GUI_Builder.__init__(self)

	def begin(self):
		self.buildGUI()
		# self.gui.centerWindowAll()

		self.frame_mainMenu.showWindow()

		if __name__ == '__main__':
			print("GUI Finished Bulding")

		self.gui.finish()

#Run Program
if __name__ == '__main__':
	controller = Controller()
	controller.begin()