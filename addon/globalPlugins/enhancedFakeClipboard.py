# -*- coding: utf-8 -*-
#fakeClipboardAnouncement.py
#A simple NVDA Global Plugin
#Written by Peter Vagner <peter.v@datagate.sk>
# 2011/08/20: initial version
# 2024/1/21, Modified by Ibrahim Hamadeh
# When pressing ctrl+a, ctrl+x, ctrl+c, ctrl+v NVDA will say the message predefined in the dictionary below and then send the gesture back to the active app.


import globalPluginHandler
import ui
import api
import inputCore
import scriptHandler
import os
import textInfos
import controlTypes
import NVDAObjects
from logHandler import log

if hasattr(controlTypes, 'State'):
	controlTypes.STATE_SELECTED= controlTypes.State.SELECTED
	controlTypes.STATE_READONLY = controlTypes.State.READONLY

import addonHandler
addonHandler.initTranslation()

messagesDict={
	# Translations: Message to announce select all action.
	"control+a":_("Select all"),
	# Translations: Message to announce cut action.
	"control+x":_("Cut"),
	# Translations: Message to announce copy action.
	"control+c":_("Copy"),
	# Translations: Message to announce paste action.
	"control+v":_("Paste")
}

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""
	This is our plugin class, that must be present in order for plugin to work. It must be named exactly as shown above, otherwise the plugin will not be recognized by NVDA.
	"""

	#the function that specifies if a certain text is selected or not
	def isSelectedText(self):
		obj=api.getFocusObject()
		treeInterceptor=obj.treeInterceptor
		if hasattr(treeInterceptor,'TextInfo') and not treeInterceptor.passThrough:
			obj=treeInterceptor
		try:
			info=obj.makeTextInfo(textInfos.POSITION_SELECTION)
		except (RuntimeError, NotImplementedError):
			info=None
		if not info or info.isCollapsed:
			return False
		else:
			return True

	def clipboardHasText(self):
		''' If clipboard contains text return True, otherwise return False.'''
		try:
			api.getClipData()
		except:
			return False
		else:
			return True

	def script_fakeClipboardAnouncement(self,gesture):
		focus = api.getFocusObject()
		myGesture= ("+".join(gesture.modifierNames)+"+"+gesture.mainKeyName)
		#dealing with regions like editableText for 8 and cumboBox as in google search box for 13
		# 52 is ROLE.Document, denoting notepad in windows11.
		if focus.role in (8, 13, 52):
			# copy and paste in readonly edit controls.
			if controlTypes.STATE_READONLY in focus.states and (myGesture == "control+x" or myGesture== "control+v"):
				gesture.send()
				return
			# copy and text not selected.
			if not self.isSelectedText() and myGesture=="control+c":
				#log.info('under copy and text not selected ind edit block')
				ui.message(_("no selection"))
				return
			# cut and text not selected ind edit controls, or in focus mode
			if (not self.isSelectedText() and myGesture== "control+x" ) and (not focus.treeInterceptor or (focus.treeInterceptor and focus.treeInterceptor.passThrough)):
				# Translations: Message displayed when no text selected.
				ui.message(_("no selection"))
				return
			# copy and cut while text selected in focus mode.
			if self.isSelectedText() and focus.treeInterceptor and focus.treeInterceptor.passThrough and (myGesture=="control+x" or myGesture=="control+c"):
				gesture.send()
				ui.message(messagesDict[myGesture])
				return
			# paste in focus mode
			if focus.treeInterceptor and focus.treeInterceptor.passThrough and myGesture== "control+v" :
				#log.info('under condition: treeInterceptor and passThrough if myGesture== "control+v"  : in edit block')
				gesture.send()
				ui.message(messagesDict[myGesture])
				return
		#log.info('sending gesture at end of edit block... ')
		#log.info(f'myGesture: {myGesture} and role: {focus.role}')
		gesture.send()

		if not focus:
			return 

	# In console window or terminal
		if focus.windowClassName == 'ConsoleWindowClass' and focus.name== 'Select Command Prompt' and myGesture== "control+c":
			ui.message(messagesDict[myGesture])
			return
		if focus.windowClassName in ('ConsoleWindowClass', 'Windows.UI.Input.InputSite.WindowClass') and (myGesture== "control+c" or myGesture== "control+x"):
			#log.info('under console window...')
			return

#now we suppose the object is  a list item
		if focus.role==15 :
			#log.info('start of list item block...')
			if controlTypes.STATE_SELECTED not in focus.states and (myGesture=="control+x" or myGesture=="control+c"):
				# Translations: Message displayed when no files selected.
				ui.message(_("No file selected"))
				return
			# clipboard contains text and not files.
			if myGesture== "control+v" and self.clipboardHasText():
				# Translations: Message to denote that there are no files in clipboard.
				ui.message(_("No files in clipboard"))
				return
			else:
				pass

		globalMapScripts = []
		globalMaps = [inputCore.manager.userGestureMap, inputCore.manager.localeGestureMap]
		for globalMap in globalMaps:
			for identifier in gesture.normalizedIdentifiers:
				#log.info(f'identifier: {identifier}')
				#log.info(f'script: {list(globalMap.getScriptsForGesture(identifier))}')
				globalMapScripts.extend(globalMap.getScriptsForGesture(identifier))
		treeInterceptor = focus.treeInterceptor
		if treeInterceptor and treeInterceptor.isReady:
			if myGesture=="control+c" or myGesture== "control+a":# or myGesture== "control+x":
				#log.info('trying to get func in treeInterceptor...')
				func = scriptHandler._getObjScript(treeInterceptor, gesture, globalMapScripts)
				#log.info(f'func from scriptHandler._getObjScript: {func}')
				if func and (not treeInterceptor.passThrough or getattr(func,"ignoreTreeInterceptorPassThrough",False)):
					#log.info(f'func: {func}')
					#func(treeInterceptor)
					# Change func calling, for the previous way has produced an error in native copy in firefox.
					scriptHandler.executeScript(func, gesture)
					return
			elif myGesture in ("control+x", "control+v") and isinstance(focus.treeInterceptor, NVDAObjects.window.winword.WordDocumentTreeInterceptor ):
				ui.message(messagesDict[myGesture])
				return
			else:
				return
		ui.message(messagesDict[myGesture])


#: Now defining a dictionary with key bindings for this plugin
	__gestures = {
		"kb:Control+a": "fakeClipboardAnouncement", #will execute our script on pressing the designated key
		"kb:Control+x": "fakeClipboardAnouncement", #will execute our script on pressing the designated key
		"kb:Control+c": "fakeClipboardAnouncement", #will execute our script on pressing the designated key
		"kb:Control+v": "fakeClipboardAnouncement", #will execute our script on pressing the designated key
	}
