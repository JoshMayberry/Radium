__version__ = "0.0.1"

#Show splash screen
if (__name__ != "__main__"):
	from GUI_Maker.Splash import SplashScreen
	splashScreen = SplashScreen()
	splashScreen.setTimeout(1500)
	imagePath = "resources/splashScreen.bmp"
	splashScreen.setImage(imagePath)
	splashScreen.finish()

	isMain = False
else:
	isMain = True

import ast
import warnings

import GUI_Maker
import API_Database as Database

class Utilities(GUI_Maker.User_Utilities):
	def __init__(self, dataCatalogue = None):

		#Initialize Inherited Modules
		GUI_Maker.User_Utilities.__init__(self, dataCatalogue)

		#Internal Variables
		self.evalList = []
		self.databaseVariables = {}

	def util_save(self, table, nextTo, args = None, labelValue = False):
		"""An abstraction that saves the current values in the database.

		table (str)  - Which table to save data to
		nextTo (str) - Which row to check for a unique variable in
		args (list)  - The variable names to save as strings. A single string can also be given
			- If None: Will save all
		labelValue (bool) - Determines what column names it looks for
			- If True: Will use the column names "label" and "value" for 'nextTo' and 'args' respectively
			- If False: Will use the name in self.databaseVariables

		Example Input: util_save("Settings_User", "name")
		Example Input: util_save("Settings_User", "name", "saved_draft")
		Example Input: util_save("Settings_User", "name", ["username", "password"])
		Example Input: util_save("Settings_General", "lastSubmission", labelValue = True)
		"""
		
		#Setup
		if (not labelValue):
			if (nextTo not in self.databaseVariables):
				warnings.warn(f"{nextTo} was given to {self.__repr__()} as nextTo to save, but it has no place in the database", Warning, stacklevel = 2)
				return
			nextTo = {self.databaseVariables[nextTo]: getattr(self, nextTo)}

		if ((args == None) or ((isinstance(args, (list, tuple))) and (len(args) == 0))):
			args = (item for item in self.databaseVariables.keys())
		elif (not isinstance(args, (list, tuple))):
			args = [args]

		#Save
		for variable in args:
			if (not labelValue):
				if (variable not in self.databaseVariables):
					warnings.warn(f"{variable} was given to {self.__repr__()} to save, but it has no place in the database", Warning, stacklevel = 2)
					continue
				key = self.databaseVariables[variable]
			else:
				key = "value"
				nextTo = {"label": variable}
				
			value = getattr(self, variable)
			self.root.database.changeCell({table: key}, nextTo, value, forceMatch = True)

	def util_load(self, table, nextTo, args = None, labelValue = False):
		"""An abstraction that loads what is in the database

		table (str) - Which table to load data from
		nextTo (str) - Which row to check for a unique variable in
			- If dict: {Column Name (str): Value (str)}
		args (list) - The variable names to load as strings. A single string can also be given
			- If None: Will load all
		labelValue (bool) - Determines what column names it looks for
			- If True: Will use the column names "label" and "value" for 'nextTo' and 'args' respectively
			- If False: Will use the name in self.databaseVariables

		Example Input: util_load("Settings_User", "name")
		Example Input: util_load("Settings_User", "name", "saved_draft")
		Example Input: util_load("Settings_User", "name", ["username", "password"])
		Example Input: util_save("Settings_General", "lastSubmission", labelValue = True)
		"""
		
		#Setup
		if (not labelValue):
			#Error Checking
			if (not isinstance(nextTo, dict)):
				if (nextTo not in self.databaseVariables):
					warnings.warn(f"{nextTo} was given to {self.__repr__()} as nextTo to load, but it has no place in the database", Warning, stacklevel = 2)
					return
				nextTo = {self.databaseVariables[nextTo]: getattr(self, nextTo)}

		if ((args == None) or ((isinstance(args, (list, tuple))) and (len(args) == 0))):
			args = (item for item in self.databaseVariables.keys())
		elif (not isinstance(args, (list, tuple))):
			args = [args]

		#Load
		for variable in args:
			if (not labelValue):
				if (variable not in self.databaseVariables):
					warnings.warn(f"{variable} was given to {self.__repr__()} to load, but it has no place in the database", Warning, stacklevel = 2)
					continue
				key = self.databaseVariables[variable]
			else:
				key = "value"
				nextTo = {"label": variable}
			
			data = self.root.database.getValue({table: key}, nextTo = nextTo)

			if (len(data[key]) == 0):
				errorMessage = f"The column {key} does not exist in table {table}, next to {nextTo}"
				raise KeyError(errorMessage)

			if (variable in self.evalList):
				value = ast.literal_eval(data[key][0]) #Safely eval a string into it's correct datatype
			else:
				value = data[key][0]

				if (value == "None"):
					value = None

			setattr(self, variable, value)

class Module_Settings():
	def __init__(self):
		self.database = Database.build("data.db", multiThread = True)

		self.settings = self.Settings(self)
		self.loadSetting()

	def loadSetting(self, label = None):
		"""Loads the requested setting.

		label (list) - The settings to load as strings. A single string can also be given
			- If None: Will load all

		Example Input: loadSetting()
		Example Input: loadSetting("lastSubmission")
		Example Input: loadSetting(["lastSubmission", "startup_user"])
		"""

		if ((label == None) or ((isinstance(label, (list, tuple))) and (len(label) == 0))):
			label = self.database.getValue({"Settings_General": "label"})["label"]
		elif (not isinstance(label, (list, tuple))):
			label = [label]

		self.settings.load(label)

	def saveSetting(self, label = None):
		"""Saves the requested setting.

		label (list) - The settings to save as strings. A single string can also be given
			- If None: Will save all

		Example Input: saveSetting()
		Example Input: saveSetting("lastSubmission")
		Example Input: saveSetting(["lastSubmission", "startup_user"])
		"""

		if ((label == None) or ((isinstance(label, (list, tuple))) and (len(label) == 0))):
			label = self.database.getValue({"Settings_General": "label"})["label"]
		elif (not isinstance(label, (list, tuple))):
			label = [label]

		self.settings.save(label)

	class Settings(Utilities):
		def __init__(self, parent):
			"""A place to store all currently applied settings."""

			#Initialize Inherited Modules
			Utilities.__init__(self, "userCatalogue")

			#Internal Variables
			self.root = parent
			self.parent = parent
			self.defaultStatus = None

			self.databaseVariables = {item: item for item in self.root.database.getValue({"Settings_General": "label"})["label"]}

		def __str__(self):
			"""Gives diagnostic information on this when it is printed out."""

			output = Utilities.__str__(self)

			for item in self.databaseVariables.keys():
				if (hasattr(self, item) and (getattr(self, item) != None)):
					output += f"-- {item}: {getattr(self, item)}\n"

			return output

		def save(self, args = None):
			"""Saves the current values in the database.

			args (list) - The variable names to save as strings. A single string can also be given
				- If None: Will save all

			Example Input: save()
			Example Input: save("lastSubmission")
			Example Input: save(["lastSubmission", "startup_user"])
			"""

			self.util_save("Settings_General", "name", args = args, labelValue = True)

		def load(self, args = None):
			"""Loads what is in the database.

			args (list) - The variable names to load as strings. A single string can also be given
				- If None: Will load all

			Example Input: load()
			Example Input: load("lastSubmission")
			Example Input: load(["lastSubmission", "startup_user"])
			"""

			self.util_load("Settings_General", "name", args = args, labelValue = True)

		def setDefaultStatus(self):
			"""Allows the user to change what shows in the status bar when there is nothing to show."""

			if (self.defaultStatus_label == "Current User"):
				if (self.root.users.currentUser == None):
					self.defaultStatus = "Current User: All Access"

				# elif (self.root.users.currentUser == -1):
				# 	self.defaultStatus = f"Temporary User Until: {self.tempPermissions_timeoutStamp}"

				else:
					self.defaultStatus = f"Current User: {self.root.users.currentUser.name}"

			elif (self.defaultStatus_label == "Ready"):
				self.defaultStatus = "Ready"

			else:
				warnings.warn(f"Unknown default status {self.defaultStatus_label} for setDefaultStatus()", Warning, stacklevel = 2)

class Module_Users():
	def __init__(self):
		"""Contains all functions pertaining to users."""
		
		self.users = self.Users(self)
		self.users.load()

	class Users(Utilities):
		def __init__(self, parent):

			#Initialize Inherited Modules
			Utilities.__init__(self, "userCatalogue")

			#Internal Variables
			self.root = parent
			self.parent = parent
			self.currentUser = None
			self.userCatalogue = {} #{label (str): user handle (Module_Users.Users.User)}

		def getUser(self, username = None):
			"""Returns the requested user.

			username (str) - Which user to return

			Example Input: getUser()
			Example Input: getUser(username = "Guest")
			"""

			#Error Checking
			if (username == None):
				user = self.currentUser
			elif (username not in self):
				warnings.warn(f"User {username} does not exist in {self.__repr__()}", Warning, stacklevel = 2)
				return
			else:
				user = self[username]

			return user

		def save(self, username = None, args = None):
			"""Saves the requested user.

			username (list) - The usernames of the users to save as strings. A single string can also be given
				- If None: Will save all
			args (list) - The variable names to save as strings. A single string can also be given
				- If None: Will save all

			Example Input: save("Guest")
			Example Input: save("Guest", "saved_draft")
			Example Input: save("Guest", ["username", "password"])

			Example Input: save(["Guest", "Lorem"])
			Example Input: save(["Guest", "Lorem"], "saved_draft")
			Example Input: save(["Guest", "Lorem"], ["username", "password"])
			"""

			#Error Checking
			if (not isinstance(username, (list, tuple))):
				username = [username]

			for item in username:
				user = self.getUser(item)
				user.save(args)

		def load(self, username = None, args = None):
			"""Loads the requested user.

			username (list) - The username of the users to load as strings. A single string can also be given
				- If None: Will load all
			args (list) - The variable names to load as strings. A single string can also be given
				- If None: Will load all

			Example Input: load("Guest")
			Example Input: load("Guest", "saved_draft")
			Example Input: load("Guest", ["username", "password"])
			
			Example Input: load(["Guest", "Lorem"])
			Example Input: load(["Guest", "Lorem"], "saved_draft")
			Example Input: load(["Guest", "Lorem"], ["username", "password"])
			"""

			#Error Checking
			if (username == None):
				username = self.root.database.getValue({"Settings_User": "username"})["username"]
			elif (not isinstance(username, (list, tuple))):
				username = [username]

			for item in username:
				if (item in self):
					user = self.getUser(item)
				else:
					user = self.User(self, name = item)
				user.load(args)

		class User(Utilities):
			def __init__(self, parent, name = None):
				"""A user for this program."""

				#Initialize Inherited Modules
				Utilities.__init__(self)

				#Internal Variables
				self.parent = parent
				self.root = parent.root
				self.password = None
				self.twitter_handle = None
				self.saved_draft = None
				
				self.databaseVariables = {"name": "username", "password": "password", "twitter_handle": "twitter_handle", "saved_draft": "saved_draft"} #{class variable name (str): database variable name (str)}
				self.evalList = ["saved_draft"]

				#Nest in parent
				if (name != None):
					self.name = name
				else:
					self.name = self.getUnique("User_{}", exclude = [item.name for item in self.parent])
				self.parent[self.name] = self

			def __str__(self):
				"""Gives diagnostic information on this when it is printed out."""

				output = Utilities.__str__(self)
				if (self.name != None):
					output += f"-- Username: {self.name}\n"
				if (self.password != None):
					output += f"-- Password: {self.password}\n"
				if (self.twitter_handle != None):
					output += f"-- Twitter Handle: {self.twitter_handle}\n"
				if (self.saved_draft != None):
					output += f"-- Saved Draft: {self.saved_draft}\n"
				return output

			def setDraft(self):
				"""Saves the current work as a draft.

				Example Input: setDraft()
				"""

				data = {}
				with self.root.submit.currentSubmission as mySubmission:
					for variable, key in mySubmission.databaseVariables.items():
						data[key] = getattr(mySubmission, variable)

				self.saved_draft = str(data)

			def save(self, args = None):
				"""Saves the current values in the database.

				args (list) - The variable names to save as strings. A single string can also be given
					- If None: Will save all

				Example Input: save()
				Example Input: save("saved_draft")
				Example Input: save(["username", "password"])
				"""

				self.util_save("Settings_User", "name", args = args)

			def load(self, args = None):
				"""Loads what is in the database.

				args (list) - The variable names to load as strings. A single string can also be given
					- If None: Will load all

				Example Input: load()
				Example Input: load("saved_draft")
				Example Input: load(["username", "password"])
				"""

				self.util_load("Settings_User", "name", args = args)

			def loadDraft(self, username = None):
				"""Loads the saved draft of the provided user.
				
				username (str) - Which user to use
					- If None: Will use the user that is currently logged in

				Example Input: loadDraft()
				Example Input: loadDraft(username = "Guest")
				"""

				user = self.root.users.getUser(username)
				data = self.root.database.getValue({"Settings_User": "saved_draft"}, nextTo = {"username": user.name})

				if (len(data["saved_draft"]) == 0):
					errorMessage = f"User {user.name} does not exist in Settings_User"
					raise KeyError(errorMessage)

				data = eval(data)
				if (data == None):
					self.clear()
				else:
					for tagName, key in self.databaseVariables.items():
						value = data[key]
						setattr(self, tagName, value)

class Module_Submit():
	def __init__(self):
		"""Contains all functions pertaining to submissions."""

		self.submit = self.Submit(self)

	class Submit(Utilities):
		def __init__(self, parent):

			#Initialize Inherited Modules
			Utilities.__init__(self, "submissionCatalogue")

			#Internal Variables
			self.root = parent
			self.parent = parent
			self.currentTable = None
			self.currentSubmission = None
			self.submissionCatalogue = {} #{label (str): submission handle (Module_Submit.Submit.Submission)}

		def getSubmission(self, caseNumber = None):
			"""Returns the requested submission.

			caseNumber (str) - Which submission to return

			Example Input: getSubmission()
			Example Input: getSubmission(caseNumber = 12)
			"""

			#Error Checking
			if (caseNumber == None):
				submission = self.currentSubmission
			elif (caseNumber not in self):
				# warnings.warn(f"Submission case number {caseNumber} does not exist in {self.__repr__()}", Warning, stacklevel = 2)
				submission = Submission(self, caseNumber = caseNumber)
			else:
				submission = self[caseNumber]

			return submission

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onNew(self, event):
			"""Creates a new submission form."""

			with self.root.frame_mainMenu as myFrame:
				submission = Submission(self)
				with submission as mySubmission:
					mySubmission.clear()
					mySubmission.saveDraft()
					mySubmission.show()
					self.currentSubmission = mySubmission

				myFrame.switchWindow(self.frame_addSubmission)

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onSubmit(self, event):
			"""Send changes for verification."""

			with self.currentSubmission as mySubmission:
				mySubmission.save()
				#manager.tweet()

				with self.root.frame_addSubmission as myFrame:
					myFrame.switchWindow(self.frame_mainMenu)

				with self.frame_mainMenu as myFrame:
					myFrame.setStatusText({f"Case {mySubmission.caseNumber} Submitted": 2000, self.root.settings.defaultStatus: None})

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onSaveDraft(self, event):
			"""Save changes and go back to the main menu."""

			with self.currentSubmission as mySubmission:
				mySubmission.saveDraft()

			with self.root.frame_addSubmission as myFrame:
				myFrame.switchWindow(self.frame_mainMenu)

				with self.frame_mainMenu as myFrame:
					myFrame.setStatusText({f"Case {mySubmission.caseNumber} Saved as Draft for {self.root.users.currentUser}": 2000, self.root.settings.defaultStatus: None})

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onCancel(self, event):
			"""Discard all changes and go back to the main menu."""

			with self.currentSubmission as mySubmission:
				mySubmission.clear()
				mySubmission.saveDraft()
				mySubmission.show()

			with self.root.frame_addSubmission as myFrame:
				myFrame.switchWindow(self.frame_mainMenu)

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onClear(self, event):
			"""Discard all changes."""

			with self.currentSubmission as mySubmission:
				mySubmission.clear()
				mySubmission.show()

			event.Skip()

		class Submission(Utilities):
			def __init__(self, parent, caseNumber = None):
				"""A submission to be sent."""

				#Initialize Inherited Modules
				Utilities.__init__(self)

				#Internal Variables
				self.parent = parent
				self.root = parent.root
				self.table = parent.currentTable
				self.title = None
				self.attribute_1 = None
				self.attribute_2 = None
				self.attribute_3 = None
				self.attribute_4 = None
				
				self.databaseVariables = {"caseNumber": "caseNumber", "title": "title", "attribute_1": "attribute_1", "attribute_2": "attribute_2", "attribute_3": "attribute_3", "attribute_4": "attribute_4"} #{class variable name (str): database variable name (str)}

				#Nest in parent
				if (caseNumber != None):
					self.caseNumber = caseNumber
				else:
					self.caseNumber = self.getUnique(exclude = [item.caseNumber for item in self.parent])
				self.parent[self.caseNumber] = self

			def __str__(self):
				"""Gives diagnostic information on this when it is printed out."""

				output = Utilities.__str__(self)
				if (self.table != None):
					output += f"-- Table: {self.table}\n"
				if (self.caseNumber != None):
					output += f"-- Case Number: {self.caseNumber}\n"
				if (self.title != None):
					output += f"-- Title: {self.title}\n"
				if (self.attribute_1 != None):
					output += f"-- Attribute 1: {self.attribute_1}\n"
				if (self.attribute_2 != None):
					output += f"-- Attribute 2: {self.attribute_2}\n"
				if (self.attribute_3 != None):
					output += f"-- Attribute 3: {self.attribute_3}\n"
				if (self.attribute_4 != None):
					output += f"-- Attribute 4: {self.attribute_4}\n"
				return output

			#Change Values
			def clear(self):
				"""Returns all variables to their default state.

				Example Input: clear()
				"""

				with self.root.frame_addSubmission as myFrame:
					for tagName in self.databaseVariables.keys():
						setattr(self, tagName, None)

			def setValues(self):
				"""Takes the values provided on the submission window.

				Example Input: setValues()
				"""

				with self.root.frame_addSubmission as myFrame:
					for tagName in self.databaseVariables.keys():
						value = myFrame.getValue(tagName)
						setattr(self, tagName, value)

			def loadDraft(self, username = None):
				"""Loads the saved draft of the provided user.
				
				username (str) - Which user to use
					- If None: Will use the user that is currently logged in

				Example Input: loadDraft()
				Example Input: loadDraft(username = "Guest")
				"""

				user = self.root.users.getUser(username)
				user.load("saved_draft")

				if (user.saved_draft == None):
					self.clear()
				else:
					for tagName, key in self.databaseVariables.items():
						value = user.saved_draft[key]
						setattr(self, tagName, value)

			def load(self, args = None):
				"""Loads what is in the database.

				args (list) - The variable names to load as strings. A single string can also be given
					- If None: Will load all

				Example Input: load()
				Example Input: load("caseNumber")
				Example Input: load(["caseNumber", "title"])
				"""

				self.util_load(self.table, "caseNumber", args = args)

			#Save Values
			def save(self, args = None):
				"""Saves the current values in the database.

				args (list) - The variable names to save as strings. A single string can also be given
					- If None: Will save all

				Example Input: save()
				Example Input: save("caseNumber")
				Example Input: save(["caseNumber", "title"])
				"""

				self.util_save(self.table, "caseNumber", args = args)

			def saveDraft(self, username = None):
				"""Saves the current work as a draft for the provided user.

				username (str) - Which user to use
					- If None: Will use the user that is currently logged in

				Example Input: saveDraft()
				Example Input: saveDraft(username = "Guest")
				"""

				user = self.root.users.getUser(username)
				user.setDraft()
				user.save("saved_draft")

			#Display Values
			def show(self):
				"""Places the values of the submission on the submission screen.

				Example Input: show()
				"""

				self.parent.currentSubmission = self

				with self.root.frame_addSubmission as myFrame:
					for tagName in self.databaseVariables.keys():
						value = getattr(self, tagName)
						myFrame.setValue(tagName, value)

class GUI_Builder():
	def __init__(self):
		self.gui = GUI_Maker.build()

	@GUI_Maker.wrap_showError(makeDialog = not isMain)
	def buildGUI(self):
		"""The GUI build routine.

		Example Input: buildGUI()
		"""

		self.settings.setDefaultStatus()

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

		myFrame (handle_window) - Which frame to add the menu to

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
			myFrame.setStatusText(self.settings.defaultStatus)

			#Build menu bar
			self.addCommonMenu(myFrame)

			#Setup for content
			with myFrame.addSizerGridFlex(rows = 4, columns = 1) as mainSizer:
				mainSizer.growFlexColumnAll()
				mainSizer.growFlexRowAll()

				with mainSizer.addButton("Create Submission") as myWidget:
					myWidget.addToolTip("Create a submission")
					myWidget.setFunction_click(self.submit.onNew)

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
			myFrame.setStatusText(self.settings.defaultStatus)

			#Build menu bar
			self.addCommonMenu(myFrame)

			#Setup for content
			with myFrame.addSizerGridFlex(rows = 4, columns = 1) as mainSizer:
				mainSizer.growFlexColumnAll()
				mainSizer.growFlexRowAll()

				with mainSizer.addSizerGridFlex(rows = 3, columns = 4) as mySizer:
					mySizer.growFlexColumn(1)
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
					mySizer.growFlexColumnAll()

					with mySizer.addButton("Submit") as myWidget:
						myWidget.setFunction_click(self.submit.onSubmit)
						myWidget.addToolTip("Submit this report")

					with mySizer.addButton("Save for Later") as myWidget:
						myWidget.setFunction_click(self.submit.onSaveDraft)
						myWidget.addToolTip("Save what is done as a draft and go back")

					with mySizer.addButton("Cancel") as myWidget:
						myWidget.setFunction_click(self.submit.onCancel)
						myWidget.addToolTip("Discard all work done and go back")

					with mySizer.addButton("Clear") as myWidget:
						myWidget.setFunction_click(self.submit.onClear)
						myWidget.addToolTip("Discard all work done")

class Controller(Utilities, Module_Settings, Module_Users, Module_Submit, GUI_Builder):
	def __init__(self):
		#Initialize inherited modules
		Utilities.__init__(self)
		Module_Settings.__init__(self)
		Module_Users.__init__(self)
		Module_Submit.__init__(self)
		GUI_Builder.__init__(self)

	def __str__(self):
		"""Gives diagnostic information on this when it is printed out."""
		
		output = Utilities.__str__(self)
		if (self.users != None):
			output += f"-- Users: {len(self.users)}\n"
		if (self.submit != None):
			output += f"-- Tables: {len(self.submit)}\n"
		return output

	def begin(self):
		self.buildGUI()
		self.frame_mainMenu.showWindow()

		if __name__ == '__main__':
			print("GUI Finished Bulding")

		print("@1", self)
		print("@2", self.settings)

		# self.gui.finish()

#Run Program
if __name__ == '__main__':
	controller = Controller()
	controller.begin()