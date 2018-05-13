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
import math
import warnings

import GUI_Maker
import API_Database as Database

class Utilities(GUI_Maker.User_Utilities):
	def __init__(self, dataCatalogue = None, label = None):

		#Initialize Inherited Modules
		GUI_Maker.User_Utilities.__init__(self, dataCatalogue, label)

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
			self.root.database.changeCell({table: key}, nextTo, value)#, forceMatch = True)

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
			Utilities.__init__(self)

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
		self.users.switchUser(self.settings.startup_user)

	class Users(Utilities):
		def __init__(self, parent):

			#Initialize Inherited Modules
			Utilities.__init__(self, "userCatalogue", "name")

			#Internal Variables
			self.root = parent
			self.parent = parent
			self.currentUser = None
			self.userCatalogue = {} #{label (str): user handle (Module_Users.Users.User)}

			self.listeningToLogout = False
			self.stop_listeningToLogout = False

		def __str__(self):
			"""Gives diagnostic information on this when it is printed out."""

			output = Utilities.__str__(self)
			if (len(self) > 0):
				output += f"-- Users: {len(self)}\n"

			return output

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

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onLogin(self, event):
			"""Lets the user login."""

			with self.frame_login as myFrame:
				myFrame.setValue("passwordBox", "")

				myFrame.backgroundRun(self.listenCapsLock, shown = True)
				myFrame.showWindow()

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onLogout(self, event):
			"""A wxEvent version of logout()."""

			self.switchUser("Guest")
			event.Skip()

		def switchUser(self, username):
			"""Lets the user logout."""

			if (isinstance(username, str)):
				self.currentUser = self.getUser(username)
			else:
				self.currentUser = username

			#Update default status
			self.root.settings.setDefaultStatus()

			if (hasattr(self.root, "frame_mainMenu")):
				self.root.frame_mainMenu.setStatusText(self.root.settings.defaultStatus)
				self.root.frame_addSubmission.setStatusText(self.root.settings.defaultStatus)
				self.root.frame_viewHistory.setStatusText(self.root.settings.defaultStatus)
				self.root.frame_login.setStatusText(self.root.settings.defaultStatus)

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onChangePassword(self, event):
			"""Lets the user change the password when they are already logged in."""

			with self.frame_changePassword as myFrame:
				myFrame.setValue("passwordBox", "")
				myFrame.setValue("confirmPasswordBox", "")

				myFrame.showWindow()

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onEnterPassword(self, event):
			"""Checks that the user entered the correct password."""

			with self.frame_login as myFrame:
				#Get necissary objects
				passwordValue = myFrame.getValue("passwordBox")

				#Check the password
				for user in self:
					if (user.password == passwordValue):
						self.switchUser(user)

						#Clear Password buffer
						myFrame.hide("wrongPasswordMessage")
						myFrame.setValue("passwordBox", "")
						myFrame.hideWindow()

						if (self.settings.autoLogout != -1):
							self.trigger_listenAutoLogout()
						
						break
				else:
					myFrame.show("wrongPasswordMessage")
					myFrame.updateWindow()

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onEnterChangePassword(self, event):
			"""Allows the user to change the password."""

			with self.frame_changePassword as myFrame:
				#Get necissary objects
				newPasswordValue = myFrame.getQueueValue(newPassword)
				confirmPasswordValue = myFrame.getQueueValue(confirmPassword)

				if (newPasswordValue != confirmPasswordValue):
					myFrame.show("mismatchPasswordMessage")
					myFrame.updateWindow()
				else:
					self.currentUser.password = newPasswordValue
					self.currentUser.save("password")
					myFrame.hideWindow()

			event.Skip()

		def listenCapsLock(self):
			"""Listens for the state of the caps lock key"""

			while True:
				#Listen for break
				if (not self.frame_login.checkShown(window = True)):
					break

				#Do stuff
				self.checkCapsLock()
				time.sleep(1)

		def checkCapsLock(self, event = None):
			"""Checks if the caps lock key is pressed."""

			#Get key state
			state = self.gui.getKeyState("cl", event = event)

			#Update GUI
			if (state):
				self.frame_login.show("capsLockMessage")
			else:
				self.frame_login.hide("capsLockMessage")

			self.frame_login.updateWindow()

		def trigger_listenAutoLogout(self):
			"""Triggers the listenAutoLogout routine."""

			if (self.listeningToLogout):
				self.stop_listeningToLogout = True
			self.frame_mainMenu.backgroundRun(self.listenAutoLogout)

		def listenAutoLogout(self):
			"""Listens for the user to have been logged in for too long."""

			#Account for other thread running this
			while self.stop_listeningToLogout:
				time.sleep(1)

			loginTime = 0
			self.listeningToLogout = True
			while True:
				#Listen for break
				if ((self.stop_listeningToLogout) or (self.settings.autoLogout == -1) or (self.currentUserLabel == "Operator")):
					self.stop_listeningToLogout = False
					break

				time.sleep(1)
				loginTime += 1

				if (loginTime >= self.settings.autoLogout):
					self.logout()
					break

			self.listeningToLogout = False

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
			Utilities.__init__(self, "submissionCatalogue", "caseNumber")

			#Internal Variables
			self.root = parent
			self.parent = parent
			self.currentTable = None
			self.currentSubmission = None
			self.submissionCatalogue = {} #{label (str): submission handle (Module_Submit.Submit.Submission)}

			self.databaseVariables = {"caseNumber": "caseNumber", "title": "title", "attribute_1": "attribute_1", "attribute_2": "attribute_2", "attribute_3": "attribute_3", "attribute_4": "attribute_4"} #{class variable name (str): database variable name (str)}
			self.aliasVariables = {"caseNumber": "Case Number", "title": "Title", "attribute_1": "Attribute 1", "attribute_2": "Attribute 2", "attribute_3": "Attribute 3", "attribute_4": "Attribute 4"} #{class variable name (str): what shows on the GUI (str)}

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
				submission = self.Submission(self, caseNumber = caseNumber)
			else:
				submission = self[caseNumber]

			return submission

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onNew(self, event):
			"""Creates a new submission form."""

			with self.root.frame_mainMenu as myFrame:
				self.currentSubmission = self.Submission(self)
				with self.currentSubmission as mySubmission:
					mySubmission.clear()
					mySubmission.saveDraft()
					mySubmission.show()

				myFrame.switchWindow(self.root.frame_addSubmission)

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onSubmit(self, event):
			"""Send changes for verification."""

			with self.currentSubmission as mySubmission:
				mySubmission.save()
				#manager.tweet()

				with self.root.frame_addSubmission as myFrame:
					myFrame.switchWindow(self.root.frame_mainMenu)

				with self.frame_mainMenu as myFrame:
					myFrame.setStatusText({f"Case {mySubmission.caseNumber} Submitted": 2000, self.root.settings.defaultStatus: None})

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onSaveDraft(self, event):
			"""Save changes and go back to the main menu."""

			with self.currentSubmission as mySubmission:
				mySubmission.saveDraft()

			with self.root.frame_addSubmission as myFrame:
				myFrame.switchWindow(self.root.frame_mainMenu)

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
				myFrame.switchWindow(self.root.frame_mainMenu)

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onClear(self, event):
			"""Discard all changes."""

			with self.currentSubmission as mySubmission:
				mySubmission.clear()
				mySubmission.show()

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onView(self, event):
			"""Opens the view submissions and drafts form."""

			with self.root.frame_mainMenu as myFrame:
				myFrame.switchWindow(self.root.frame_viewHistory)

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onEdit(self, event):
			"""Edit this draft."""

			# with self.root.frame_mainMenu as myFrame:
			# 	myFrame.switchWindow(self.root.frame_viewHistory)

			event.Skip()

		@GUI_Maker.wrap_showError(makeDialog = not isMain)
		def onTweet(self, event):
			"""Send the tweet to your manager again."""

			# with self.root.frame_mainMenu as myFrame:
			# 	myFrame.switchWindow(self.root.frame_viewHistory)

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
				
				self.databaseVariables = parent.databaseVariables

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

				for variable, alias in self.parent.aliasVariables.items():
					if (hasattr(self, variable) and (getattr(self, variable) != None)):
						output += f"-- {alias}: {getattr(self, variable)}\n"

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
		self.buildViewHistory()
		self.buildLogin()
		self.buildChangePassword()

	def createWindows(self):
		"""Creates all the window frames before they are built.
		This is because frames that would have been created first may need to address frames that would have been created after.

		Example Input: createWindows()
		"""

		self.frame_mainMenu       = self.gui.addWindow(label = "mainMenu",       title = f"Main Menu v.{__version__}",          icon = "resources/startIcon.ico")
		self.frame_addSubmission  = self.gui.addWindow(label = "addSubmission",  title = f"Create Submission v.{__version__}",  icon = "folderNew",  internal = True)
		self.frame_viewHistory    = self.gui.addWindow(label = "viewHistory",    title = f"Submission History v.{__version__}", icon = "viewReport", internal = True)
		self.frame_login          = self.gui.addWindow(label = "login",          title = f"Login v.{__version__}",              icon = "resources/key.ico", topBar = False)
		self.frame_changePassword = self.gui.addWindow(label = "changePassword", title = f"Change Password v.{__version__}",    icon = "resources/key.ico", topBar = False)
	
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

			# myMenu.addMenuSeparator()

			# if (myFrame != self.frame_mainMenu):
			# 	with myMenu.addMenuItem(text = "Main Menu") as myMenuItem:
			# 		myMenuItem.addToolTip("Returns to the main menu")
			# 		myMenuItem.setFunction_click(myFunction = myFrame.onSwitchWindow, myFunctionArgs = self.frame_mainMenu)

		with myFrame.addMenu(text = "&Security") as myMenu:
			with myMenu.addMenuItem(text = "Login", label = "menuLogin") as myMenuItem:
				myMenuItem.addToolTip("Allows the user to edit things and enables locked options")
				myMenuItem.setFunction_click(myFunction = self.users.onLogin)
			
			with myMenu.addMenuItem(text = "Logout", label = "menuLogout") as myMenuItem:
				myMenuItem.addToolTip("Keeps the user from editing things and disables some options")
				myMenuItem.setFunction_click(myFunction = self.users.onLogout)

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
					myWidget.setFunction_click(self.submit.onView)

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
			with myFrame.addSizerGridFlex(rows = 2, columns = 1) as mainSizer:
				mainSizer.growFlexColumnAll()
				mainSizer.growFlexRow(0)

				n = math.ceil(len(self.submit.aliasVariables) / 2)
				with mainSizer.addSizerGridFlex(rows = n, columns = 4) as mySizer:
					mySizer.growFlexColumn(1)
					mySizer.growFlexColumn(3)
					mySizer.growFlexRowAll()

					for variable, alias in self.submit.aliasVariables.items():
						mySizer.addText(alias)
						mySizer.addInputBox(label = variable)

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

	def buildViewHistory(self):
		"""Creates the main window.

		Example Input: buildViewHistory()
		"""

		with self.frame_viewHistory as myFrame:
			#Initialize GUI
			myFrame.setMinimumFrameSize((200, 200))
			myFrame.addStatusBar()
			myFrame.setStatusText(self.settings.defaultStatus)

			#Build menu bar
			self.addCommonMenu(myFrame)

			#Setup for content
			with myFrame.addSizerGridFlex(rows = 1, columns = 1) as mainSizer:
				mainSizer.growFlexColumnAll()
				mainSizer.growFlexRowAll()

				leftSizer, rightSizer = mainSizer.addSplitterDouble(minimumSize = 20, vertical = True, dividerPosition = 130, dividerGravity = 0, panel_0 = {"border": "raised"}, panel_1 = {"border": "raised"},
					sizer_0 = {"type": "flex", "rows": 1, "columns": 1}, sizer_1 = {"type": "flex", "rows": 2, "columns": 1})

				with leftSizer as mySizer:
					mySizer.growFlexColumnAll()
					mySizer.growFlexRowAll()

					mySizer.addListTree(choices = {"Drafts": ["Guest"], "Pending Approval": {"2018": None}, "Completed": {"2018": None}}, label = "chosen")

				with rightSizer as mySizer:
					mySizer.growFlexColumnAll()
					mySizer.growFlexRow(0)

					valueList = [[self.submit.aliasVariables[key], ""] for key in self.submit.databaseVariables.keys()]
					with mySizer.addListFull(choices = valueList, label = "values", report = True, columns = 2, columnNames = {0: "Variable", 1: "Value"}, rowLines = False) as myWidget:
						myWidget.setRowColor(slice(1, None, 2), color = (0.9, 0.9, 0.9))

					with mySizer.addSizerGridFlex(rows = 1, columns = 3) as mySubSizer:
						with mySubSizer.addButton("Edit", label = "edit", enabled = False) as myWidget:
							myWidget.setFunction_click(self.submit.onEdit)
							myWidget.addToolTip("Edit this draft")

						with mySubSizer.addButton("Tweet Again", label = "tweet", enabled = False) as myWidget:
							myWidget.setFunction_click(self.submit.onTweet)
							myWidget.addToolTip("Send the tweet again to your manager")

						with mySubSizer.addButton("Back", label = "back") as myWidget:
							myWidget.setFunction_click(myFrame.onSwitchWindow, myFunctionArgs = self.frame_mainMenu)
							myWidget.addToolTip("Go back to the main menu")

	def buildLogin(self):
		"""Creates the popup login window.

		Example Input: buildLogin()
		"""

		with self.frame_login as myFrame:
			#Initialize GUI
			myFrame.setMinimumFrameSize(200, 150)

			with myFrame.addSizerBox() as mainSizer:
				#Add content
				mainSizer.addText("Password")
				
				with mainSizer.addInputBox(label = "passwordBox", password = True) as myWidget:
					myWidget.setFunction_enter(myFunction = self.users.onEnterPassword)
					myWidget.addToolTip("Enter the password here\nDifferent passwords allow different things")

				#Finalize
				mainSizer.addText("Caps Lock is ON", label = "capsLockMessage", hidden = True)
				mainSizer.addText("Incorrect Password", label = "wrongPasswordMessage", hidden = True)
				with mainSizer.addSizerGrid(rows = 1, columns = 2) as mySizer:
					with mySizer.addButton(text = "Back") as myWidget:
						myWidget.setFunction_click(myFunction = [myFrame.onHideWindow, myFrame.onHide], myFunctionArgs = [None, "wrongPasswordMessage"])
						myWidget.addToolTip("Cancel this operation")
					
					with mySizer.addButton(text = "Ok") as myWidget:
						myWidget.setFunction_click(myFunction = self.users.onEnterPassword)
						myWidget.addToolTip("Submit password")

	def buildChangePassword(self):
		"""Creates the popup password change window.

		Example Input: buildChangePassword()
		"""

		with self.frame_changePassword as myFrame:
			#Initialize GUI
			myFrame.setMinimumFrameSize(200, 150)

			with myFrame.addSizerBox() as mainSizer:
				#Add content
				mainSizer.addText("New Password")
				
				with mainSizer.addInputBox(label = "passwordBox", password = True) as myWidget:
					myWidget.addToolTip("Enter the new password here to enable editing and unlock certain options")
				mainSizer.addLine()
				mainSizer.addText("Confirm Password")
				
				with mainSizer.addInputBox(label = "confirmPasswordBox", password = True) as myWidget:
					myWidget.setFunction_click(myFunction = self.users.onEnterChangePassword)
					myWidget.addToolTip("The text in here must match the text in the box above")
				
				mainSizer.addText("Passwords do not match", label = "mismatchPasswordMessage", hidden = True)

				#Finalize
				with mainSizer.addSizerGrid(rows = 1, columns = 2) as mySizer:
					with mySizer.addButton(text = "Back") as myWidget:
						myWidget.setFunction_click(myFunction = [myFrame.onHideWindow, myFrame.onHide], myFunctionArgs = [None, "mismatchPasswordMessage"])
						myWidget.addToolTip("Cancel this operation")
					
					with mySizer.addButton(text = "Ok") as myWidget:
						myWidget.setFunction_click(myFunction = self.users.onEnterChangePassword)
						myWidget.addToolTip("Submit new password")

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
		if (hasattr(self, "users") and (self.users != None)):
			output += f"-- Users: {len(self.users)}\n"
		if (hasattr(self, "submit") and (self.submit != None)):
			output += f"-- Tables: {len(self.submit)}\n"
		return output

	def begin(self):
		self.buildGUI()
		self.frame_mainMenu.showWindow()

		if __name__ == '__main__':
			print("GUI Finished Bulding")

		# print("@1", self)
		# print("@2", self.settings)

		self.gui.finish()

#Run Program
if __name__ == '__main__':
	controller = Controller()
	controller.begin()