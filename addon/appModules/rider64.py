# Rider Support App Module for NVDA
#inspired by the addon IntelliJ-Improved written by Samuel Kacer
#Copyright (C) 2024 Christopher Proß
#GNU GENERAL PUBLIC LICENSE V2
#Author: Christopher Proß <christopherpross.dev@mailbox.org>


import NVDAObjects
import NVDAObjects.JAB
from buildVersion import version_year
from dataclasses import dataclass
from unicodedata import category
import appModuleHandler
import textInfos
import tones
import controlTypes
import config
from editableText import EditableTextWithoutAutoSelectDetection
from logHandler import log
import gui
from gui.settingsDialogs import SettingsPanel
from scriptHandler import script
import speech
import ui
import api
import threading
import time
from winsound import PlaySound, SND_ASYNC, SND_ALIAS
import wx

# handle both pre and post 2022 controlTypes
if version_year >= 2022:
	EDITABLE_TEXT = controlTypes.Role.EDITABLETEXT
	STATUSBAR = controlTypes.Role.STATUSBAR
else:
	EDITABLE_TEXT = controlTypes.ROLE_EDITABLETEXT
	STATUSBAR = controlTypes.ROLE_STATUSBAR

CONF_KEY = 'rider'
BEEP_ON_STATUS_CHANGED_KEY = 'beepOnStatusChange'
BEEP_ON_STATUS_CLEARED_KEY = 'beepOnStatusCleared'
SPEAK_ON_STATUS_CHANGED_KEY = 'speakOnStatusChange'
INTERRUPT_SPEECH_KEY = 'interruptOnStatusChange'
BEEP_BEFORE_READING_KEY = 'beepBeforeReadingStatus'
BEEP_AFTER_READING_KEY = 'beepAfterReadingStatus'

DEFAULT_BEEP_ON_CHANGE = False
DEFAULT_BEEP_ON_STATUS_CLEARED = False
DEFAULT_SPEAK_ON_CHANGE = True
DEFAULT_INTERRUPT_SPEECH = False
DEFAULT_BEEP_BEFORE_READING = True
DEFAULT_BEEP_AFTER_READING = False

config.conf.spec[CONF_KEY] = {
	BEEP_ON_STATUS_CHANGED_KEY : f'boolean(default={DEFAULT_BEEP_ON_CHANGE})',
	BEEP_ON_STATUS_CLEARED_KEY : f'boolean(default={DEFAULT_BEEP_ON_STATUS_CLEARED})',
	SPEAK_ON_STATUS_CHANGED_KEY : f'boolean(default={DEFAULT_SPEAK_ON_CHANGE})',
	INTERRUPT_SPEECH_KEY : f'boolean(default={DEFAULT_INTERRUPT_SPEECH})',
	BEEP_BEFORE_READING_KEY : f'boolean(default={DEFAULT_BEEP_BEFORE_READING})',
	BEEP_AFTER_READING_KEY : f'boolean(default={DEFAULT_BEEP_AFTER_READING})'
}

class RiderAddonSettings(SettingsPanel):
	title = "Rider Improved"

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		conf = config.conf[CONF_KEY]
		self.beepOnChange= sHelper.addItem(wx.CheckBox(self, label="Beep when status bar changes"))
		self.beepOnChange.SetValue(conf[BEEP_ON_STATUS_CHANGED_KEY])
		self.beepOnClear= sHelper.addItem(wx.CheckBox(self, label="Beep when status bar is cleared"))
		self.beepOnClear.SetValue(conf[BEEP_ON_STATUS_CLEARED_KEY])
		self.speakOnChange = sHelper.addItem(wx.CheckBox(self, label="Automatically read status bar changes"))
		self.speakOnChange.SetValue(conf[SPEAK_ON_STATUS_CHANGED_KEY])
		self.beepBeforeReading = sHelper.addItem(wx.CheckBox(self, label="Beep before status bar change is read"))
		self.beepBeforeReading.SetValue(conf[BEEP_BEFORE_READING_KEY])
		self.beepAfterReading = sHelper.addItem(wx.CheckBox(self, label="Beep after status bar change is read"))
		self.beepAfterReading.SetValue(conf[BEEP_AFTER_READING_KEY])
		self.interruptSpeech = sHelper.addItem(wx.CheckBox(self, label="Interrupt speech when automatically reading status bar changes"))
		self.interruptSpeech.SetValue(conf[INTERRUPT_SPEECH_KEY])

	def onSave(self):
		conf = config.conf[CONF_KEY]
		conf[BEEP_ON_STATUS_CHANGED_KEY] = self.beepOnChange.Value
		conf[BEEP_ON_STATUS_CLEARED_KEY] = self.beepOnClear.Value
		conf[SPEAK_ON_STATUS_CHANGED_KEY] = self.speakOnChange.Value
		conf[INTERRUPT_SPEECH_KEY] = self.interruptSpeech.Value
		conf[BEEP_BEFORE_READING_KEY] = self.beepBeforeReading.Value
		conf[BEEP_AFTER_READING_KEY] = self.beepAfterReading.Value
		setGlobalVars()

@dataclass
class Vars:
	beepOnChange: bool = DEFAULT_BEEP_ON_CHANGE
	beepOnClear: bool = DEFAULT_BEEP_ON_STATUS_CLEARED
	speakOnChange: bool = DEFAULT_SPEAK_ON_CHANGE
	interruptSpeech: bool = DEFAULT_INTERRUPT_SPEECH
	beepBeforeReading: bool = DEFAULT_BEEP_BEFORE_READING
	beepAfterReading: bool = DEFAULT_BEEP_AFTER_READING

vars = Vars()

def setGlobalVars():
	conf = config.conf[CONF_KEY]
	vars.beepOnChange = conf[BEEP_ON_STATUS_CHANGED_KEY]
	vars.beepOnClear = conf[BEEP_ON_STATUS_CLEARED_KEY]
	vars.speakOnChange = conf[SPEAK_ON_STATUS_CHANGED_KEY]
	vars.interruptSpeech = conf[INTERRUPT_SPEECH_KEY]
	vars.beepBeforeReading = conf[BEEP_BEFORE_READING_KEY]
	vars.beepAfterReading = conf[BEEP_AFTER_READING_KEY]

# initialize conf in case being run for the first time
if config.conf.get(CONF_KEY) is None:
	config.conf[CONF_KEY] = {}
setGlobalVars()

class EnhancedEditableText(EditableTextWithoutAutoSelectDetection):
	def _get_caretMovementDetectionUsesEvents(self) -> bool:
		return True
	
	__gestures = {
		# these Rider commands change caret position, so they should trigger reading new line position
		"kb:alt+downArrow" : "caret_moveByLine",
		"kb:alt+upArrow" : "caret_moveByLine",
		"kb:control+[" : "caret_moveByLine",
		"kb:control+]" : "caret_moveByLine",
		"kb:f2" : "caret_moveByLine",
		"kb:shift+f2" : "caret_moveByLine",
		"kb:control+b" : "caret_moveByLine",
		"kb:control+alt+leftArrow" : "caret_moveByLine",
		"kb:control+alt+rightArrow" : "caret_moveByLine",
		"kb:control+y" : "caret_moveByLine",
		"kb:f3" : "caret_moveByLine",
		"kb:shift+f3" : "caret_moveByLine",
		"kb:control+u" : "caret_moveByLine",
		"kb:control+shift+backspace" : "caret_moveByLine",
		"kb:control+/" : "caret_moveByLine",
		"kb:alt+j" : "caret_moveByLine",
		"kb:alt+control+downArrow" : "caret_moveByLine",
		"kb:alt+control+upArrow" : "caret_moveByLine",
		"kb:alt+pageUp" : "caret_moveByLine",
		"kb:alt+pageDown" : "caret_moveByLine",
		# these gestures trigger selection change
		"kb:control+w": "caret_changeSelection",
		"kb:control+shift+w": "caret_changeSelection",
		"kb:alt+shift+j": "caret_changeSelection",
		"kb:control+shift+[": "caret_changeSelection",
		"kb:control+shift+]": "caret_changeSelection",
	}

	shouldFireCaretMovementFailedEvents = True

	def event_caretMovementFailed(self, gesture):
		PlaySound('SystemExclamation', SND_ASYNC | SND_ALIAS)


"""
Custom object for the list item in the code completion view.
"""
class CodeCompletionItem(NVDAObjects.JAB.JAB):
	"""
	Gets the content, of the documentation tooltip of a code completion item, if avaiable. 
	If no documentation was found, None is returned.
	"""
	def getDocumentation(self) -> str:
		if (not isinstance(self.parent, NVDAObjects.JAB.JAB)):
			log.warn("fetching documentation failed, parent is not a JAB-Object.")
			return None

		if (self.parent.role != controlTypes.ROLE_LIST):
			log.warn("fetching documentation failed, parent is not a list.")
			return None
		
		if (not isinstance(self.parent.previous, NVDAObjects.JAB.JAB) 
			or not isinstance(self.parent.previous.previous, NVDAObjects.JAB.JAB)
			or self.parent.previous.previous.role != controlTypes.ROLE_WINDOW):
			log.warn("fetching documentation failed, tooltip window not found.")
			return None
		
		tooltipWindow = self.parent.previous.previous
		currentObj = tooltipWindow
		while currentObj is not None:
			# search pattern for the documentation tooltip
			if (currentObj.role == controlTypes.ROLE_SCROLLPANE):
				# we have found the scrollpane, so let's search for the documentation textfield
				currentObj = currentObj.firstChild
				while currentObj is not None:	
					if (currentObj.childCount > 0 and currentObj.firstChild.role == controlTypes.ROLE_LIST
						and currentObj.firstChild.childCount > 0
						and currentObj.firstChild.firstChild.role == controlTypes.ROLE_EDITABLETEXT
						and currentObj.firstChild.firstChild.description == "text/html"):
						# we found the documentation textfield, so let's extract the text
						currentObj = currentObj.firstChild.firstChild
						return currentObj.makeTextInfo(textInfos.POSITION_ALL).text
					else:
						currentObj = currentObj.next
						continue
			else:
				currentObj = currentObj.firstChild

		# the search pattern has failed
		log.warn("fetching documentation failed, documentation textfield was not found.")
		return None


class AppModule(appModuleHandler.AppModule):
	def __init__(self, pid, appName=None):
		super(AppModule, self).__init__(pid, appName)
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(RiderAddonSettings)
		self.status = None
		self.watcher = StatusBarWatcher(self)
		self.watcher.start()

	def terminate(self):
		self.watcher.stopped = True
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(RiderAddonSettings)


	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.role == EDITABLE_TEXT:
			clsList.insert(0, EnhancedEditableText)
		if (self.isCodeCompletionItem(obj)):
			clsList.insert(0, CodeCompletionItem)



	def isCodeCompletionItem(self, obj):
		if (obj.role == controlTypes.ROLE_LISTITEM
			and obj.parent.parent == api.getDesktopObject()
			and obj.childCount == 3):
			for child in obj.children:
				if (child.role is not controlTypes.ROLE_STATICTEXT):
					# this is not a code completion item
					return False
			return True;
		return False

	@script(
		"Read the documentation",
		gesture = 'kb:NVDA+d',
		category="Rider")
	def script_readDocumentation(self, gesture):
		obj = api.getFocusObject()
		if isinstance(obj, CodeCompletionItem):
			documentationText = obj.getDocumentation()
			if (documentationText == None):
				ui.message("Documentation not found!")
			else:
				ui.message(documentationText)


	@script(
		"Read the status bar",
		gesture = 'kb:NVDA+i',
		category="Rider")
	def script_readStatusBar(self, gesture):
		status = self.getStatusBar()
		if status is None:
			ui.message('couldnt find status bar')
		else:
			msg = status.simpleFirstChild.name
			ui.message(msg)

	def getStatusBar(self, refresh: bool = False):
		obj = api.getForegroundObject()
		if obj is None or not obj.appModule.appName == "rider64":
			# Ignore cases nvda is lost
			return
		if self.status and not refresh:
			return self.status
		else:
			obj = obj.simpleFirstChild
			while obj is not None:
				# This first searching pattern is for IntelliJ post v2023
				if obj.name == "Status Bar":
					child = obj.simpleFirstChild
					if child.role == STATUSBAR:
						obj = child
						self.status = obj
						break
				# this second searching pattern is for IntelliJ pre v2023
				if obj.role == STATUSBAR:
					self.status = obj
					break

				obj = obj.simpleNext

			return obj

	@script("Toggle automatically reading status bar changes", category="Rider")
	def script_toggleSpeakOnStatusChanged(self, gesture):
		newVal = not vars.speakOnChange
		config.conf[CONF_KEY][SPEAK_ON_STATUS_CHANGED_KEY] = newVal
		vars.speakOnChange = newVal
		if newVal:
			ui.message("Enabled automatically reading status bar changes")
		else:
			ui.message("Disabled automatically reading status bar changes")

	@script("Toggle interrupting speech when automatically reading status bar changes", category="Rider")
	def script_toggleInterruptSpeech(self, gesture):
		newVal = not vars.interruptSpeech
		config.conf[CONF_KEY][INTERRUPT_SPEECH_KEY] = newVal
		vars.interruptSpeech = newVal
		if newVal:
			ui.message("Enabled interrupting speech while automatically reading status bar changes")
		else:
			ui.message("Disabled interrupting speech while automatically reading status bar changes")


class StatusBarWatcher(threading.Thread):
	STATUS_CHANGED_TONE = 1000
	AFTER_TONE = 800
	STATUS_CLEARED_TONE = 500
	SLEEP_DURATION = 0.25
	REFRESH_INTERVAL = 5 # seconds

	def __init__(self, addon):
		super(StatusBarWatcher, self).__init__()
		self.stopped = False
		self._lastText = ""
		self.addon = addon
		self.lastRefresh = time.time()

	def _statusBarFound(self, obj):
		# Don't use simpleFirstChild here since we need to know wether the error is fixed
		if not obj.firstChild:
			return

		msg = obj.firstChild.name

		if self._lastText != msg:
			if msg and vars.beepOnChange:
				tones.beep(StatusBarWatcher.STATUS_CHANGED_TONE, 50)
			elif not msg and vars.beepOnClear:
				tones.beep(StatusBarWatcher.STATUS_CLEARED_TONE, 50)

			if msg and vars.speakOnChange:
				seq = []
				if vars.beepBeforeReading:
					seq.append(speech.commands.BeepCommand(StatusBarWatcher.STATUS_CHANGED_TONE, 50))
				seq.append(msg)
				if vars.beepAfterReading:
					seq.append(speech.commands.BeepCommand(StatusBarWatcher.AFTER_TONE, 50))
				speech.speak(seq, priority= speech.Spri.NOW if vars.interruptSpeech else speech.Spri.NORMAL)

			self._lastText = msg

	def _runLoopIteration(self):
		now = time.time()
		shouldRefresh = now - self.lastRefresh > StatusBarWatcher .REFRESH_INTERVAL
		if shouldRefresh:
			self.lastRefresh = now
		status = self.addon.getStatusBar(refresh=shouldRefresh)
		if status:
			self._statusBarFound(status)

	def run(self):
		while not self.stopped:
			try:
				self._runLoopIteration()
			except Exception as error:
				log.warn("Error on watcher thread: %s" % error)
			time.sleep(StatusBarWatcher.SLEEP_DURATION)
