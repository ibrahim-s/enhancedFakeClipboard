# -*- coding: UTF-8 -*-
# installTasks for enhancedFakeClipboard add-on
# During installing enhancedFakeClipboard, we aim to remove fakeClipboardAnouncement if it exist.

import addonHandler

def onInstall():
	for addon in addonHandler.getAvailableAddons():
		if addon.name == 'fakeClipboardAnouncement':
			addon.requestRemove()
			return
