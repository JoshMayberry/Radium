__version__ = "0.0.1"

#Show splash screen
if (__name__ != "__main__"):
	from GUI_Maker.Splash import SplashScreen
	splashScreen = SplashScreen()
	splashScreen.setTimeout(1500)
	imagePath = "resources/splashScreen.bmp"
	splashScreen.setImage(imagePath)
	splashScreen.finish()

	isNotMain = True
else:
	isNotMain = False

import warnings

import GUI_Maker
import API_Database as Database

class Utilities(GUI_Maker.User_Utilities):
	def __init__(self, dataCatalogue = None):
		GUI_Maker.User_Utilities.__init__(self, dataCatalogue)

class Settings():
	def __init__(self):
		self.database = Database.build("data.db", multiThread = True)

class Module_Submit():
	def __init__(self):
		Utilities.__init__(self, "submissionCatalogue")

		#Internal Variables
		self.submissionCatalogue = {} #{label (str): submission handle (Module_Submit.Submission)}

	def onSubmit(self, event):
		"""Send changes for verification."""

		with self.frame_addSubmission as myFrame:
			myFrame.switchWindow(self.frame_mainMenu)

		event.Skip()

	def onSaveDraft(self, event):
		"""Save changes and go back to the main menu."""

		with self.frame_addSubmission as myFrame:
			myFrame.switchWindow(self.frame_mainMenu)

		event.Skip()

	def onCancel(self, event):
		"""Discard all changes and go back to the main menu."""

		with self.frame_addSubmission as myFrame:
			myFrame.switchWindow(self.frame_mainMenu)

		event.Skip()

	def onClear(self, event):
		"""Discard all changes."""

		with self.frame_addSubmission as myFrame:
			myFrame.switchWindow(self.frame_mainMenu)

		event.Skip()

	class Submission():
		def __init__(self, parent, caseNumber):
			"""A submission to be sent."""

			#Internal Variables
			self.parent = parent
			self.caseNumber = caseNumber
			self.table = "Submissions_05_2018"
			self.title = None
			self.attribute_1 = None
			self.attribute_2 = None
			self.attribute_3 = None
			self.attribute_4 = None
			
			self.databaseVariables = {"caseNumber": "caseNumber", "title": "title", "attribute_1": "attribute_1", "attribute_2": "attribute_2", "attribute_3": "attribute_3", "attribute_4": "attribute_4"} #{class variable name (str): database variable name (str)}

		def setValues(self):
			"""Takes the values provided on the submission window."""

			with self.parent.frame_addSubmission as myFrame:
				self.title = myFrame.getValue("title")
				self.attribute_1 = myFrame.getValue("attribute_1")
				self.attribute_2 = myFrame.getValue("attribute_2")
				self.attribute_3 = myFrame.getValue("attribute_3")
				self.attribute_4 = myFrame.getValue("attribute_4")

		def save(self):
			"""Saves the current values in the database."""

			self.parent.

			if (len(args) == 0):
				args = (item for item in self.databaseVariables.keys())

			for variable in args:
				#Error Checking
				if (variable not in self.databaseVariables):
					warnings.warn(f"{variable} was given to {self.__repr__()} to save, but it has no place in the database", Warning, stacklevel = 2)
					continue
					
				value = getattr(self, variable)
				self.parent.database.changeCell({self.table: self.databaseVariables[variable]}, {"caseNumber": self.caseNumber}, value)

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
		self.buildAddSubmission()

	def createWindows(self):
		"""Creates all the window frames before they are built.
		This is because frames that would have been created first may need to address frames that would have been created after.

		Example Input: createWindows()
		"""

		self.frame_mainMenu      = self.gui.addWindow(label = "mainMenu",      title = f"Main Menu v.{__version__}",         icon = "resources/startIcon.ico")
		self.frame_addSubmission = self.gui.addWindow(label = "addSubmission", title = f"Create Submission v.{__version__}", icon = "addBookmark", internal = True)

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
			myFrame.setMinimumFrameSize((200, 200))
			myFrame.addStatusBar()
			# myFrame.setStatusText(self.defaultStatus)

			#Build menu bar
			self.addCommonMenu(myFrame)

			#Setup for content
			with myFrame.addSizerGridFlex(rows = 4, columns = 1) as mainSizer:
				mainSizer.growFlexColumnAll()
				mainSizer.growFlexRowAll()

				with mainSizer.addButton("Create Submission") as myWidget:
					myWidget.addToolTip("Create a submission")
					myWidget.setFunction_click(myFunction = myFrame.onSwitchWindow, myFunctionArgs = self.frame_addSubmission)

				with mainSizer.addButton("View Submissions") as myWidget:
					myWidget.addToolTip("View submitted reports")
					# myWidget.setFunction_click(myFunction = myFrame.onSwitchWindow, myFunctionArgs = self.frame_viewSubmission)

	def buildAddSubmission(self):
		"""Creates the main window.

		Example Input: buildAddSubmission()
		"""

		with self.frame_addSubmission as myFrame:
			#Initialize GUI
			myFrame.setMinimumFrameSize((200, 200))
			myFrame.addStatusBar()
			# myFrame.setStatusText(self.defaultStatus)

			#Build menu bar
			self.addCommonMenu(myFrame)

			#Setup for content
			with myFrame.addSizerGridFlex(rows = 4, columns = 1) as mainSizer:
				mainSizer.growFlexColumnAll()
				mainSizer.growFlexRowAll()

				with mainSizer.addSizerGridFlex(rows = 3, columns = 4) as mySizer:
					mainSizer.growFlexColumn(1)
					# mainSizer.growFlexRowAll()

					mySizer.addText("Title")
					mySizer.addInputBox(label = "title")

					mySizer.addText("Attribute 1")
					mySizer.addInputBox(label = "attribute_1")

					mySizer.addText("Attribute 2")
					mySizer.addInputBox(label = "attribute_2")

					mySizer.addText("Attribute 3")
					mySizer.addInputBox(label = "attribute_3")

					mySizer.addText("Attribute 4")
					mySizer.addInputBox(label = "attribute_4")

				with mainSizer.addSizerGridFlex(rows = 1, columns = 4) as mySizer:
					mainSizer.growFlexColumnAll()

					with mySizer.addButton("Submit") as myWidget:
						myWidget.setFunction_click(self.onSubmit)
						myWidget.addToolTip("Submit this report")

					with mySizer.addButton("Save for Later") as myWidget:
						myWidget.setFunction_click(self.onSaveDraft)
						myWidget.addToolTip("Save what is done as a draft and go back")

					with mySizer.addButton("Cancel") as myWidget:
						myWidget.setFunction_click(self.onCancel)
						myWidget.addToolTip("Discard all work done and go back")

					with mySizer.addButton("Clear") as myWidget:
						myWidget.setFunction_click(self.onClear)
						myWidget.addToolTip("Discard all work done")

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