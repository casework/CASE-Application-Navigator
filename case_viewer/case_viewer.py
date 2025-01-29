# Portions of this file contributed by NIST are governed by the
# following statement:
#
# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to Title 17 Section 105 of the
# United States Code, this software is not subject to copyright
# protection within the United States. NIST assumes no responsibility
# whatsoever for its use by other parties, and makes no guarantees,
# expressed or implied, about its quality, reliability, or any other
# characteristic.
#
# We would appreciate acknowledgement if the software is used.

import argparse
import json
import codecs
import sys
from collections import deque
from typing import Optional, Union, List, Dict
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import logging

from .lib import JSONLD, get_attribute, get_optional_integer_attribute, \
						get_optional_string_attribute, get_optional_dict_attribute, \
						get_optional_list_attribute

class TableModel(QtCore.QAbstractTableModel):
	def __init__(self, data):
		super(TableModel, self).__init__()
		self._data = data

	def data(self, index, role):
		if role == QtCore.Qt.DisplayRole:
			# See below for the nested-list data structure.
			# .row() indexes into the outer list,
			# .column() indexes into the sub-list
			return self._data[index.row()][index.column()]

	def rowCount(self, index):
		# The length of the outer list.
		return len(self._data)

	def columnCount(self, index):
		# The following takes the first sub-list, and returns
		# the length (only works if all rows are an equal length)
		return len(self._data[0])

class view(QWidget):
	def __init__(self, treeData, tableData):
		super(view, self).__init__()
		self.tree = QTreeView(self)

		self.tree_cyber_item = ''

		self.table = QTableView(self)
		self.table.setVisible(True)
		self.tableData = tableData
		self.treeData = treeData
		
		self.font = QFont("Helvetica", pointSize=12, weight=QFont.Medium)

		self.textEdit = QTextEdit()
		self.textEdit.setFont(self.font)
		self.textEdit.setDocumentTitle("Details")
		self.textEdit.setHtml('<h2>Here the details will be displayed</h2>')


		self.modelTable = TableModel(tableData)
		self.table.setModel(self.modelTable)

		self.table.headers = []


		grid = QGridLayout()
		grid.setSpacing(10)

		#grid.addWidget(widget, row, column, row_span, col_span)
		grid.addWidget(self.tree, 1, 0, 10, 4)
		#grid.addWidget(self.table, 1, 2, 8, 8)
		grid.addWidget(self.table, 1, 4, 10, 10)
		grid.addWidget(self.textEdit, 1, 14, 10, 6)

		self.setLayout(grid)

		self.model = QStandardItemModel()
		self.model.setHorizontalHeaderLabels(['Cyber item'])
		self.tree.setModel(self.model)
		self.importData(self.treeData)
		self.tree.clicked.connect(self.select_left_bar)
		self.tree.collapseAll()
		self.table.clicked.connect(self.select_main_panel)

	# Function to save populate treeview with a dictionary
	def importData(self, data, root=None):
		self.model.setRowCount(0)
		if root is None:
			root = self.model.invisibleRootItem()
		seen = {}   # List of  QStandardItem
		values = deque(data)
		while values:
			value = values.popleft()
			if value['unique_id'] == ':00000000':
				parent = root
			else:
				pid = value['parent_id']
				if pid not in seen:
					values.append(value)
					continue
				parent = seen[pid]
			unique_id = value['unique_id']
			parent.appendRow([
				QStandardItem(value['short_name']),
			])
			seen[unique_id] = parent.child(parent.rowCount() - 1)

	# Function to transverse treeview and derive tree_list
	def transverse_tree(self):
		tree_list = []
		for i in range(self.model.rowCount()):
			item = self.model.item(i)
			level = 0
			self.GetItem(item, level, tree_list)
		return tree_list

	def GetItem(self, item, level, tree_list):
		if item != None:
			if item.hasChildren():
				level = level + 1
				short_name = ' '
				height = ' '
				weight = ' '
				id = 0
				for i in range(item.rowCount()):
					id = id + 1
					for j in reversed([0, 1, 2]):
						childitem = item.child(i, j)
						if childitem != None:
							if j == 0:
								short_name = childitem.data(0)
							else:
								short_name = short_name
							if j == 1:
								height = childitem.data(0)
							else:
								height = height
							if j == 2:
								weight = childitem.data(0)
							else:
								weight = weight

							if j == 0:
								dic = {}
								dic['level'] = level
								dic['id'] = id
								dic['short_name'] = short_name
								tree_list.append(dic)
							self.GetItem(childitem, level, tree_list)
				return tree_list



	def buildTableData(self, idObject: str) -> list:
		self.headers: list[str] = []
		tData = self.buildDataChatMessages(idObject)
		if len(tData) == 0:
			tData = self.buildDataPhoneCalls(idObject)
		if len(tData) == 0:
			tData = self.buildDataCalendars(idObject)
		if len(tData) == 0:
			tData = self.buildDataBluetooths(idObject)
		if len(tData) == 0:
			tData = self.buildDataSms(idObject)
		if len(tData) == 0:
			tData = self.buildDataContacts(idObject)
		if len(tData) == 0:
			tData = self.buildDataCellSites(idObject)
		if len(tData) == 0:
			tData = self.buildDataWirelessNet(idObject)
		if len(tData) == 0:
			tData = self.buildDataSearchedItems(idObject)
		if len(tData) == 0:
			tData = self.buildDataSocialMediaActivities(idObject)
		if len(tData) == 0:
			tData = self.buildDataEvents(idObject)
		if len(tData) == 0:
			tData = self.buildDataCookies(idObject)
		if len(tData) == 0:
			tData = self.buildDataEmailMessages(idObject)
		if len(tData) == 0:
			tData = self.buildDataFiles(idObject)
		if len(tData) == 0:
			tData = self.buildDataWebBookmarks(idObject)
		if len(tData) == 0:
			tData = self.buildDataWebHistories(idObject)
		if len(tData) == 0:
			tData = self.buildDataWebSearchTerm(idObject)
		if len(tData) == 0:
			tData = self.buildDataLocationDevice(idObject)

		return tData


	def buildDataChatMessages(self, idObject):

		tData = []
		threadFound = False
		threadSlot = []

		for t in chatThreads:
			if t["@id"] == idObject:
				threadFound = True
				threadSlot = t["thread:messages"]
				break

		if not threadFound:
			print('Thread not found')
			return tData
		#print(f"threadSlot=\n{threadSlot}")
		self.headers = ["Date", "Attachments"]
		for idMsg in threadSlot:
			for m in chatMessages:
				if idMsg == m["@id"]:
					msgDate = m["uco-observable:sentTime"]
					msgAttachments = m["uco-observable:attachedFiles"]
					tData.append([msgDate, msgAttachments])

		return tData

	def buildDataContacts(self, idObject):
		tData = []
		if idObject == ':Accounts':
			self.headers = ["Identifier", "Phone", "Display name", "Application"]
			for a in accounts:
				accountIdentifier = a["uco-observable:accountIdentifier"]
				accountPhone = a["uco-observable:phoneAccount"]
				accountApplication = a["uco-observable:application"]
				accountDiplayName = a["uco-observable:displayName"]
				tData.append([accountIdentifier, accountPhone, accountDiplayName, accountApplication])
		return tData


	def buildDataBluetooths(self, idObject):
		tData = []
		if idObject == ':Bluetooths':
			self.headers = ["Address"]
			for b in bluetooths:
				tData.append([b["uco-observable:addressValue"]])
		return tData


	def buildDataCalendars(self, idObject):
		tData = []
		if idObject != ':Calendars':
			print('Calendar not found')
			return tData
		else:
			self.headers = ["Subject", "Repeat", "Start time", "End time", "Status"]
			for c in calendars:
				calendarSubject = c["uco-observable:subject"]
				calendarRepeatInterval = c["uco-observable:recurrence"]
				calendarStartDate = c["uco-observable:startTime"]
				calendarEndDate = c["uco-observable:endTime"]
				calendarStatus = c["uco-observable:eventStatus"]
				tData.append([calendarSubject, calendarRepeatInterval, calendarStartDate, calendarEndDate, calendarStatus])
		return tData


	def buildDataPhoneCalls(self, idObject):
		tData = []
		if idObject == ':Calls':
			self.headers = ["From", "To", "Date", "Duration"]
			for c in phoneCalls:
				callDate = c["uco-observable:startTime"]
				callDuration = c["uco-observable:duration"]
				callFrom = c["uco-observable:from"]
				callTo = c["uco-observable:to"]
				tData.append([callFrom, callTo, callDate, callDuration])
		return tData


	def buildDataCellSites(self, idObject):
		tData = []
		if idObject == ':CellSites':
			self.headers = ["MCC", "MNC", "LAC", "CID", "Type"]
			for c in cell_sites:
				cellMCC = c["uco-observable:cellSiteCountryCode"]
				cellMNC = c["uco-observable:cellSiteNetworkCode"]
				cellLAC = c["uco-observable:cellSiteLocationAreaCode"]
				cellCID = c["uco-observable:cellSiteIdentifier"]
				cellType = c["uco-observable:cellSiteType"]
				tData.append([cellMCC, cellMNC, cellLAC, cellCID, cellType])
		return tData


	def buildDataWirelessNet(self, idObject: str) -> list[list[str]]:
		global wireless_net
		tData = []
		if idObject == ':WirelessNet':
			self.headers = ["SSID", "BSID"]
			for w in wireless_net:
				wirelessSsid = w["uco-observable:ssid"]
				wirelessBsid = w["uco-observable:baseStation"]
				tData.append([wirelessSsid, wirelessBsid])
		return tData


	def buildDataSearchedItems(self, idObject):
		tData = []
		if idObject == ':SearchedItems':
			self.headers = ["Source", "Launched time", "Value"]
			for s in searched_items:
				searchedSource = s["drafting:searchSource"]
				searchedTime = s["drafting:searchLaunchedTime"]
				searchedValue = s["drafting:searchValue"]
				tData.append([searchedSource, searchedTime, searchedValue])
		return tData


	def buildDataSocialMediaActivities(self, idObject):
		tData = []
		if idObject == ':SocialMediaActivities':
			self.headers = ["Body", "Title", "Date", "App", "Author Identifier", "Name", "Type", "Account identifier"]
			for s in social_media_activities:
				socialBody = s["uco-observable:body"]
				socialTitle = s["uco-observable:pageTitle"]
				socialDate = s["uco-observable:observableCreatedTime"]
				socialApp = s["uco-observable:application"]
				socialAuthorId = s["drafting:authorIdentifier"]
				socialAccountId = s["uco-observable:accountIdentifier"]
				socialName = s["drafting:authorName"]
				socialType = s["drafting:activityType"]
				tData.append([socialBody, socialTitle, socialDate, socialApp, socialAuthorId,
							  socialName, socialType, socialAccountId])
		return tData


	def buildDataEvents(self, idObject):
		tData = []
		if idObject == ':Events':
			self.headers = ["Date Time", "Type", "Text"]
			for e in events:
				eCreated = e["uco-observable:observableCreatedTime"]
				eType = e["uco-observable:eventType"]
				eText = e["uco-observable:eventText"]
				tData.append([eCreated, eType, eText])
		return tData


	def buildDataCookies(self, idObject):
		tData = []
		if idObject == ':Cookies':
			self.headers = ["Name", "Path", "Application", "Created time", "Expiration time"]
			for c in cookies:
				cookieName = c["uco-observable:cookieName"]
				cookiePath = c["uco-observable:cookiePath"]
				cookieApp = c["uco-observable:cookieApp"]
				cookieCreatedTime = c["uco-observable:observableCreatedTime"]
				cookieExpirationTime = c["uco-observable:expirationTime"]
				tData.append([cookieName, cookiePath, cookieApp, cookieCreatedTime, cookieExpirationTime])
		return tData


	def buildDataEmailMessages(self, idObject):
		tData = []
		if idObject == ':EmailMessages':
			self.headers = ["From", "To", "Date", "Subject"]
			for e in emailMessages:
				emailSubject = e["uco-observable:subject"]
				emailDate = e["uco-observable:sentTime"]
				emailFrom = e["uco-observable:from"]
				emailTo = e["uco-observable:to"]
				tData.append([emailFrom, emailTo, emailDate, emailSubject])
		return tData

	def buildDataFiles(self, idObject):
		tData = []
		self.headers = ["Name", "Path", "Size"]
		
		if idObject == ':Images':
			for f in filesImage:
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]
				tData.append([fileName, filePath, fileSize])

		if idObject == ':Texts':
			for f in filesText:
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]
				tData.append([fileName, filePath, fileSize])

		if idObject == ':PDFs':
			for f in filesPDF:
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]
				tData.append([fileName, filePath, fileSize])

		if idObject == ':Words':
			for f in filesWord:
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]
				tData.append([fileName, filePath, fileSize])

		if idObject == ':RTFs':
			for f in filesRTF:
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]
				tData.append([fileName, filePath, fileSize])

		if idObject == ':Audios':
			for f in filesAudio:
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]
				tData.append([fileName, filePath, fileSize])

		if idObject == ':Videos':
			for f in filesVideo:
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]
				tData.append([fileName, filePath, fileSize])

		if idObject == ':Archives':
			for f in filesArchive:
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]
				tData.append([fileName, filePath, fileSize])

		if idObject == ':Databases':
			for f in filesDatabase:
				#fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]
				tData.append([fileName, filePath, fileSize])

		if idObject == ':Applications':
			for f in filesApplication:
				#fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]
				tData.append([fileName, filePath, fileSize])

		if idObject == ':Uncategorized':
			for f in filesUncategorized:
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]
				tData.append([fileName, filePath, fileSize])
				
		return tData


	def buildDataSms(self, idObject):
		tData = []
		if idObject == ':Sms':
			self.headers = ["From", "To", "Date", "Text", "Status"]
			for m in smsMessages:
				smsText = m["uco-observable:messageText"]
				#smsApp = m["uco-observable:application"]
				smsSentTime = m["uco-observable:sentTime"]
				smsStatus = m["uco-observable:allocationStatus"]
				smsFrom = m["uco-observable:from"]
				smsTo = m["uco-observable:to"]
				tData.append([smsFrom, smsTo, smsSentTime, smsText, smsStatus])
		return tData


	def buildDataWebBookmarks(self, idObject):
		tData = []
		if idObject == ':WebBookmarks':
			self.headers = ["Url", "App", "Path", "Crteated date"]
			for w in webBookmark:
				webUrl = w["uco-observable:urlTargeted"]
				webApp = w["uco-observable:application"]
				webPath = w["uco-observable:bookmarkPath"]
				webDate = w["uco-observable:observableCreatedTime"]
				tData.append([webUrl, webApp, webPath, webDate])
		return tData


	def buildDataWebHistories(self, idObject):
		tData = []
		webApp = ''
		if idObject == ':WebHistories':
			self.headers = ["Url", "Title", "Last visited", "App"]
			for w in webURLHistory:
				webUrl = w["uco-observable:url"]
				webTitle = w["uco-observable:title"]
				webLastVisited = w["uco-observable:lastVisited"]
				webApp = w["uco-observable:browserInformation"]
				tData.append([webUrl, webTitle, webLastVisited, webApp])
		return tData


	def buildDataWebSearchTerm(self, idObject):
		tData = []
		print(f"idObject={idObject}")
		if idObject == ':WebSearchTerms':
			self.headers = ["Web search term"]
			for w in webSearchTerm:
				webTerm = w["uco-observable:searchTerm"]
				tData.append([webTerm])
		return tData


	def buildDataLocationDevice(self, idObject):
		tData = []
		if idObject == ':LocationDevice':
			self.headers = ["Latitude", "Longitude", "Start date"]
			for l in relationMappedBy:
				lDate = l["uco-observable:mappedByStartDate"]
				lLat = l["uco-observable:mappedByLatitude"]
				lLong = l["uco-observable:mappedByLongitude"]
				tData.append([lLat, lLong, lDate])
		return tData


	def select_left_bar(self, index):
		text = index.data(QtCore.Qt.DisplayRole)
		threadId = ''
		for i, dic in enumerate(treeData):
			if dic['short_name'] == text:
				print('text: ' + text + ', selected thread id: ' + str(treeData[i]['unique_id']))
				threadId = treeData[i]['unique_id']
				break
		if threadId == '':
			print('Thread id not found')
			self.tree_cyber_item = ''
		else:
			self.tree_cyber_item = text
			self.tableData = self.buildTableData(threadId)
			self.tableData.insert(0, self.headers)
			print(f"self.tree_cyber_item={self.tree_cyber_item}")
			file_type = self.tree_cyber_item.split()[0]
			html_text = ""
			if "chat N." in self.tree_cyber_item:
				html_text = self.gather_all_chats()
				self.textEdit.setHtml(html_text)
			elif "Accounts " in self.tree_cyber_item:
				html_text = self.gather_all_accounts()
				self.textEdit.setHtml(html_text)
			elif "Calendars " in self.tree_cyber_item:
				html_text = self.gather_all_calendars()
				self.textEdit.setHtml(html_text)
			elif "Calls " in self.tree_cyber_item:
				html_text = self.gather_all_calls()
				self.textEdit.setHtml(html_text)
			elif "CellSite " in self.tree_cyber_item:
				html_text = self.gather_all_cellsites()
				self.textEdit.setHtml(html_text)
			elif "Cookies " in self.tree_cyber_item:
				html_text = self.gather_all_cookies()
				self.textEdit.setHtml(html_text)
			elif "Device connection " in self.tree_cyber_item:
				html_text = self.gather_all_device_connection()
				self.textEdit.setHtml(html_text)
			elif "Emails " in self.tree_cyber_item:
				html_text = "<h3>Please, select single messages from the main panel.</br/><br/>" + \
				"Viewing all messages will take too much time.</h3>"
				#html_text = self.gather_all_emails()
				self.textEdit.setHtml(html_text)
			elif "Events " in self.tree_cyber_item:
				html_text = self.gather_all_events()
				self.textEdit.setHtml(html_text)
			elif "Location device " in self.tree_cyber_item:
				html_text = self.gather_all_locations()
				self.textEdit.setHtml(html_text)
			elif file_type in ("Images", "Audios", "Videos",
					"Texts", "Archives", "Databases", "Applications", "Uncategorized"):
					print(f"Here you are! [{self.tree_cyber_item}]")
					if file_type == "Images":
						html_text = "<h3>Please, select single image from the main panel.</br/><br/>" + \
							"Viewing all images will take too much time.</h3>"
					elif file_type == "Audios":
						html_text = self.gather_all_files(file_type, filesAudio)
					elif file_type == "Videos":
						html_text = "<h3>Please, select single video from the main panel.</br/><br/>" + \
							"Viewing all videos will take too much time.</h3>"
					elif file_type == "Texts":
						html_text = "<h3>Please, select single text from the main panel.</br/><br/>" + \
							"Viewing all texts will take too much time.</h3>"
					elif file_type == "Archives":
						html_text = self.gather_all_files(file_type, filesArchive)
					elif file_type == "Databases":
						html_text = self.gather_all_files(file_type, filesDatabase)
					elif file_type == "Applications":
						html_text = self.gather_all_files(file_type, filesApplication)
					elif file_type == "Uncategorized":
						html_text = self.gather_all_files(file_type, filesUncategorized)
					self.textEdit.setHtml(html_text)
			elif "Social media activities" in self.tree_cyber_item:
				html_text = self.gather_all_social_media_activities()
				self.textEdit.setHtml(html_text)
			elif "Web Bookmarks " in self.tree_cyber_item:
				html_text = self.gather_all_web_bookmarks()
				self.textEdit.setHtml(html_text)
			elif "Web Histories " in self.tree_cyber_item:
				html_text = self.gather_all_web_histories()
				self.textEdit.setHtml(html_text)
			elif "Web Search Terms " in self.tree_cyber_item:
				html_text = self.gather_all_web_search_terms()
				self.textEdit.setHtml(html_text)
			elif "Wireless Net " in self.tree_cyber_item:
				html_text = self.gather_all_wireless_nets()
				self.textEdit.setHtml(html_text)

		self.model = TableModel(self.tableData)
		self.table.setModel(self.model)


	def select_main_panel(self, item):
		#text = index.data(Qt.DisplayRole)
		#print(f"in itemTableSelected, item row={item.row()}, cyber items={self.tree_cyber_item}")
		if item.row():
			row = int(item.row() - 1)
			if 'Email' in self.tree_cyber_item:
				row = emailMessages[row]
				detail = "<strong>From</strong> " + str(row["uco-observable:from"]) + "<br/>" + \
				"<strong>To</strong> " + str(row["uco-observable:to"]) + "<br/>" + \
				"<strong>Cc </strong> " + str(row["uco-observable:cc"]) + "<br/>" + \
				"<strong>Bcc </strong> " + str(row["uco-observable:bcc"]) + "<br/>" + \
				"<strong>Subject</strong> " + str(row["uco-observable:subject"]) + "<br/>" + \
				"<strong>Sent time</strong> " + str(row["uco-observable:sentTime"]) + "<br/>" + \
				"<strong>Body</strong> " + str(row["uco-observable:body"]) + "<hr/>"
				self.textEdit.setHtml('<h2>Email</h2>' + detail)
			elif "chat N." in self.tree_cyber_item:
				row = chatMessages[row]
				to_participants = ""
				for p in row["uco-observable:to"]:
					to_participants = to_participants + p + "; "
				detail = "<strong>From</strong> " + str(row["uco-observable:from"]) + "<br/>" + \
				"<strong>To</strong> " + str(to_participants) + "<br/>" + \
				"<strong>Message</strong><br/>" + row["uco-observable:messageText"] + '<hr/>'
				self.textEdit.setHtml('<h2>Chat message</h2>' + detail)
			elif "Accounts " in self.tree_cyber_item:
				row = accounts[row]
				detail = "<strong>Name</strong> " + row["uco-observable:displayName"] + "<br/>" + \
				"<strong>Phone n.</strong> " + row["uco-observable:phoneAccount"] + "<br>" + \
				"<strong>Identifier</strong> " + row["uco-observable:accountIdentifier"]
				self.textEdit.setHtml('<h2>Account</h2>' + detail)
			elif "Calendar" in self.tree_cyber_item:
				row = calendars[row]
				detail = "<strong>Subject</strong> " + str(row["uco-observable:subject"]) + "<br/>" + \
				"<strong>Start</strong> " + str(row["uco-observable:startTime"]) + "<br/>" + \
				"<strong>End</strong> " + str(row["uco-observable:endTime"]) + "<br/>" + \
				"<strong>Recurrence</strong> " + str(row["uco-observable:recurrence"])
				self.textEdit.setHtml('<h2>Calendar</h2>' + detail)
			elif "Calls" in self.tree_cyber_item:
				row = phoneCalls[row]
				detail = "<strong>From</strong> " + str(row["uco-observable:from"]) + "<br/>" + \
				"<strong>To</strong> " + str(row["uco-observable:to"]) + "<br/>" + \
				"<strong>Name</strong> " + row["uco-core:name"] + "<br/>" + \
				"<strong>Start time</strong> " + str(row["uco-observable:startTime"]) + "<br/>" + \
				"<strong>Duration (s.)</strong> " + str(row["uco-observable:duration"])
				self.textEdit.setHtml('<h2>Call</h2>' + detail)
			elif "CellSite" in self.tree_cyber_item:
				row = cell_sites[row]
				detail = "<strong>Country code</strong> " + str(row["uco-observable:cellSiteCountryCode"]) + "<br/>" + \
				"<strong>Identifier</strong> " + str(row["uco-observable:cellSiteIdentifier"]) + "<br/>" + \
				"<strong>Network code</strong> " + str(row["uco-observable:cellSiteNetworkCode"]) + "<br/>" + \
				"<strong>Location area code </strong> " + str(row["uco-observable:cellSiteLocationAreaCode"]) + "<br/>" + \
				"<strong>Site type </strong> " + str(row["uco-observable:cellSiteType"])
				self.textEdit.setHtml('<h2>Cell site</h2>' + detail)
			elif "Cookies" in self.tree_cyber_item:
				row= cookies[row]
				detail = "<strong>Name</strong> " + str(row["uco-observable:cookieName"]) + "<br/>" + \
				"<strong>Path</strong> " + str(row["uco-observable:cookiePath"]) + "<br/>" + \
				"<strong>Application </strong> " + str(row["uco-observable:cookieApp"]) + "<br/>" + \
				"<strong>Crreated time </strong> " + str(row["uco-observable:accessedTime"]) + "<br/>" + \
				"<strong>Expiration time </strong> " + str(row["uco-observable:expirationTime"]) + "<hr/>"
				self.textEdit.setHtml('<h2>Cookies</h2>' + detail)
			elif "Device connection" in self.tree_cyber_item:
				row = bluetooths[row]
				detail = "<strong>Address</strong> " + str(row["uco-observable:addressValue"]) + "<hr/>"
				self.textEdit.setHtml('<h2>Device connection (bluetooth)</h2>' + detail)
			elif "Events" in self.tree_cyber_item:
				row = events[row]
				detail = "<strong>Type</strong> " + str(row["uco-observable:eventType"]) + "<br/>" + \
				"<strong>Text</strong> " + str(row["uco-observable:eventText"]) + "<br/>" + \
				"<strong>Created time</strong> " + str(row["uco-observable:observableCreatedTime"]) + "<hr/>"
				self.textEdit.setHtml('<h2>Events</h2>' + detail)
			elif "Images" in self.tree_cyber_item:
				row = filesImage[row]
				detail = self.gather_data_file(row)
				self.textEdit.setHtml('<h2>Image</h2>' + detail)
			elif "Audios" in self.tree_cyber_item:
				row = filesAudio[row]
				detail = self.gather_data_file(row)
				self.textEdit.setHtml('<h2>Audio</h2>' + detail)
			elif "Texts" in self.tree_cyber_item:
				row = filesText[row]
				detail = self.gather_data_file(row)
				self.textEdit.setHtml('<h2>Text</h2>' + detail)
			elif "Videos" in self.tree_cyber_item:
				row = filesVideo[row]
				detail = self.gather_data_file(row)
				self.textEdit.setHtml('<h2>Video</h2>' + detail)
			elif "Archives" in self.tree_cyber_item:
				row = filesArchive[row]
				detail = self.gather_data_file(row)
				self.textEdit.setHtml('<h2>Archive</h2>' + detail)
			elif "Databases" in self.tree_cyber_item:
				row = filesDatabase[row]
				detail = self.gather_data_file(row)
				self.textEdit.setHtml('<h2>Database</h2>' + detail)
			elif "Applications" in self.tree_cyber_item:
				row = filesApplication[row]
				detail = self.gather_data_file(row)
				self.textEdit.setHtml('<h2>Application</h2>' + detail)
			elif "Uncategorized" in self.tree_cyber_item:
				row = filesUncategorized[row]
				detail = self.gather_data_file(row)
				self.textEdit.setHtml('<h2>Uncategorized</h2>' + detail)
			elif "Location device" in self.tree_cyber_item:
				item =relationMappedBy[row]
				detail = "<strong>Start date</strong> " + str(item["uco-observable:mappedByStartDate"]) + "<br/>" + \
				"<strong>Latitude</strong> " + str(item["uco-observable:mappedByLatitude"]) + "<br/>" + \
				"<strong>Longitude</strong> " + str(item["uco-observable:mappedByLongitude"]) + "<hr/>"
				self.textEdit.setHtml('<h2>Location device</h2>' + detail)
			elif "Social media activities" in self.tree_cyber_item:
				item =social_media_activities[row]
				detail = "<strong>Body</strong> " + str(item["uco-observable:body"]) + "<br/>" + \
				"<strong>Title</strong> " + str(item["uco-observable:pageTitle"]) + "<br/>" + \
				"<strong>Date</strong> " + str(item["uco-observable:observableCreatedTime"]) + "<br/>"
				"<strong>ApplicationName</strong> " + str(item["uco-observable:application"]) + "<br/>"
				"<strong>Author ID</strong> " + str(item["drafting:authorIdentifier"]) + "<br/>"
				"<strong>Account ID</strong> " + str(item["drafting:authorName"]) + "<br/>"
				"<strong>Name</strong> " + str(item["uco-observable:application"]) + "<br/>"
				"<strong>Type</strong> " + str(item["drafting:activityType"])
				self.textEdit.setHtml('<h2>Social media activity</h2>' + detail)
			elif "Web Bookmarks" in self.tree_cyber_item:
				row =webBookmark[row]
				detail = "<strong>Url</strong> " + str(row["uco-observable:urlTargeted"]) + "<br/>" + \
				"<strong>Path</strong> " + str(row["uco-observable:bookmarkPath"]) + "<br/>" + \
				"<strong>Application</strong> " + str(row["uco-observable:application"]) + "<br/>" + \
				"<strong>Created time</strong> " + str(row["uco-observable:observableCreatedTime"]) + "<hr/>"
				self.textEdit.setHtml('<h2>Web Bookmark</h2>' + detail)
			elif "Web Histories" in self.tree_cyber_item:
				row =webURLHistory[row]
				detail = "<strong>Url</strong> " + str(row["uco-observable:url"]) + "<br/>" + \
				"<strong>Title</strong> " + str(row["uco-observable:title"]) + "<br/>" + \
				"<strong>Browser</strong> " + str(row["uco-observable:browserInformation"]) + "<br/>" + \
				"<strong>Last visited</strong> " + str(row["uco-observable:lastVisited"]) + "<hr/>"
				self.textEdit.setHtml('<h2>Web History</h2>' + detail)
			elif "Web Search Terms" in self.tree_cyber_item:
				row =webSearchTerm[row]
				detail = "<strong>Web Search Term</strong> " + str(row["uco-observable:searchTerm"]) + "<hr/>"
				self.textEdit.setHtml('<h2>Web Search Terms</h2>' + detail)
			elif "Wireless Net" in self.tree_cyber_item:
				row =wireless_net[row]
				detail = "<strong>SSID</strong> " + str(row["uco-observable:ssid"]) + "<br/>" + \
				"<strong>Base Station</strong> " + str(row["uco-observable:baseStation"]) + "<hr/>"
				self.textEdit.setHtml('<h2>Wireless Network Connection</h2>' + detail)
			else:
				self.textEdit.setHtml('<h2>Here the details of the cyber item will be displayed</h2>')
				print("item selected is not an Email")


	def gather_all_chats(self):
		pos = self.tree_cyber_item.find('(')
		idx = int((self.tree_cyber_item[7:pos])) - 1
		html_text="<h2>Chat messages</h2><br/>"
		for t in chatThreads[idx]['thread:messages']:
			for m in chatMessages:
				if m["@id"] == t:
					html_text += "<strong>From</strong> " + m["uco-observable:from"] + "<br/>" + \
					"<strong>To</strong> " + " ".join(m["uco-observable:to"]) + "<br/>" + \
					"<strong>Application</strong> " + m["uco-observable:application"] + "<br/>" + \
					"<strong>Message</strong><br/>" + m["uco-observable:messageText"] + "<hr/>"
		return html_text


	def gather_all_accounts(self):
		html_text="<h2>Accounts data</h2><br/>"
		for a in accounts:
			html_text = html_text + \
			"<strong>Identifier</strong> " + a["uco-observable:accountIdentifier"] + "<br/>" + \
			"<strong>Phone number</strong> " + a["uco-observable:phoneAccount"] + "<br/>" + \
			"<strong>Application</strong> " + a["uco-observable:application"] + "<br/>" + \
			"<strong>Display name</strong> " + a["uco-observable:displayName"] + "<hr/>"
		return html_text


	def gather_all_calendars(self):
		html_text="<h2>Calendars data</h2><br/>"
		for c in calendars:
			html_text = html_text + \
			"<strong>Subject</strong> " + str(c["uco-observable:subject"]) + "<br/>" + \
			"<strong>Start</strong> " + str(c["uco-observable:startTime"]) + "<br/>" + \
			"<strong>End</strong> " + str(c["uco-observable:endTime"]) + "<br/>" + \
			"<strong>Recurrence</strong> " + str(c["uco-observable:recurrence"]) + "<hr/>"
		return html_text


	def gather_all_calls(self):
		html_text="<h2>Calls data</h2><br/>"
		for a in phoneCalls:
			html_text = html_text + \
			"<strong>From</strong> " + str(a["uco-observable:from"]) + "<br/>" + \
			"<strong>To</strong> " + str(a["uco-observable:to"]) + "<br/>" + \
			"<strong>Name</strong> " + a["uco-core:name"] + "<br/>" + \
			"<strong>Start time</strong> " + str(a["uco-observable:startTime"]) + "<br/>" + \
			"<strong>Duration (s.)</strong> " + str(a["uco-observable:duration"]) + "<hr/>"
		return html_text

	def gather_all_cellsites(self):
		html_text="<h2>Cellsites data</h2><br/>"
		for a in cell_sites:
			html_text = html_text + \
			"<strong>Country code</strong> " + str(a["uco-observable:cellSiteCountryCode"]) + "<br/>" + \
				"<strong>Identifier</strong> " + str(a["uco-observable:cellSiteIdentifier"]) + "<br/>" + \
				"<strong>Network code</strong> " + str(a["uco-observable:cellSiteNetworkCode"]) + "<br/>" + \
				"<strong>Location area code </strong> " + str(a["uco-observable:cellSiteLocationAreaCode"]) + "<br/>" + \
				"<strong>Site type </strong> " + str(a["uco-observable:cellSiteType"]) + "<hr/>"
		return html_text


	def gather_all_cookies(self):
		html_text="<h2>Cookies data</h2><br/>"
		for item in cookies:
			html_text = html_text + \
			"<strong>Name</strong> " + str(item["uco-observable:cookieName"]) + "<br/>" + \
			"<strong>Path</strong> " + str(item["uco-observable:cookiePath"]) + "<br/>" + \
			"<strong>Application </strong> " + str(item["uco-observable:cookieApp"]) + "<br/>" + \
			"<strong>Crreated time </strong> " + str(item["uco-observable:accessedTime"]) + "<br/>" + \
			"<strong>Expiration time </strong> " + str(item["uco-observable:expirationTime"]) + "<hr/>"
		return html_text


	def gather_all_device_connection(self):
		html_text="<h2>Device connection data</h2><br/>"
		for item in bluetooths:
			html_text = html_text + \
			"<strong>Address</strong> " + str(item["uco-observable:addressValue"]) + "<hr/>"
		return html_text


	def gather_all_emails(self):
		html_text="<h2>Email data</h2><br/>"
		for item in emailMessages:
			html_text = html_text + \
			"<strong>From</strong> " + str(item["uco-observable:from"]) + "<br/>" + \
			"<strong>To</strong> " + str(item["uco-observable:to"]) + "<br/>" + \
			"<strong>Cc</strong> " + str(item["uco-observable:cc"]) + "<br/>" + \
			"<strong>Bcc</strong> " + str(item["uco-observable:bcc"]) + "<br/>" + \
			"<strong>Subject</strong> " + str(item["uco-observable:subject"]) + "<br/>" + \
			"<strong>Sent time</strong> " + str(item["uco-observable:sentTime"]) + "<br/>" + \
			"<strong>Body</strong> " + str(item["uco-observable:body"]) + "<hr/>"
		return html_text


	def gather_all_events(self):
		html_text="<h2>Events data</h2><br/>"
		for item in events:
			html_text = html_text + \
			"<strong>Tipo</strong> " + str(item["uco-observable:eventType"]) + "<br/>" + \
			"<strong>Text</strong> " + str(item["uco-observable:eventText"]) + "<br/>" + \
			"<strong>Created time</strong> " + str(item["uco-observable:observableCreatedTime"]) + "<hr/>"
		return html_text


	def gather_all_files(self, type, arrayFiles):
		html_text="<h2>" + type + " data</h2><br/>"
		for item in arrayFiles:
			html_text = html_text + \
			"<strong>Name</strong> " + str(item["uco-observable:fileName"]) + "<br/>" + \
			"<strong>Path</strong> " + str(item["uco-observable:filePath"]) + "<br/>" + \
			"<strong>Size</strong> " + str(item["uco-observable:fileSize"]) + "<hr/>"
		return html_text


	def gather_all_locations(self):
		html_text="<h2>Location device data</h2><br/>"
		for item in relationMappedBy:
			html_text = html_text + \
			"<strong>Start date</strong> " + str(item["uco-observable:mappedByStartDate"]) + "<br/>" + \
			"<strong>Latitude</strong> " + str(item["uco-observable:mappedByLatitude"]) + "<br/>" + \
			"<strong>Longitude</strong> " + str(item["uco-observable:mappedByLongitude"]) + "<hr/>"
		return html_text


	def gather_data_file(self, row):
		detail = "<strong>Name</strong> " + str(row["uco-observable:fileName"]) + "<br/>" + \
		"<strong>Path</strong> " + str(row["uco-observable:filePath"]) + "<br/>" + \
		"<strong>Size</strong> " + str(row["uco-observable:fileSize"]) + "<hr/>"
		return(detail)


	def gather_all_social_media_activities(self):
		html_text="<h2>Social Media Activities data</h2><br/>"
		for item in social_media_activities:
			html_text = html_text + \
			"<strong>Body</strong> " + str(item["uco-observable:body"]) + "<br/>" + \
			"<strong>Title</strong> " + str(item["uco-observable:pageTitle"]) + "<br/>" + \
			"<strong>Date</strong> " + str(item["uco-observable:observableCreatedTime"]) + "<br/>" + \
			"<strong>ApplicationName</strong> " + str(item["uco-observable:application"]) + "<br/>" + \
			"<strong>Author ID</strong> " + str(item["drafting:authorIdentifier"]) + "<br/>" + \
			"<strong>Account ID</strong> " + str(item["drafting:authorName"]) + "<br/>" + \
			"<strong>Name</strong> " + str(item["uco-observable:application"]) + "<br/>" + \
			"<strong>Type</strong> " + str(item["drafting:activityType"]) + "<hr/>"
		return html_text


	def gather_all_web_histories(self):
		html_text="<h2>Web History data</h2><br/>"
		for item in webURLHistory:
			html_text = html_text + \
			"<strong>Url</strong> " + str(item["uco-observable:url"]) + "<br/>" + \
			"<strong>Title</strong> " + str(item["uco-observable:title"]) + "<br/>" + \
			"<strong>Browser</strong> " + str(item["uco-observable:browserInformation"]) + "<br/>" + \
			"<strong>Last visited</strong> " + str(item["uco-observable:lastVisited"]) + "<hr/>"
		return html_text


	def gather_all_web_bookmarks(self):
		html_text="<h2>Web Bookmark data</h2><br/>"
		for item in webBookmark:
			html_text = html_text + \
			"<strong>Url</strong> " + str(item["uco-observable:urlTargeted"]) + "<br/>" + \
			"<strong>Path</strong> " + str(item["uco-observable:bookmarkPath"]) + "<br/>" + \
			"<strong>Application</strong> " + str(item["uco-observable:application"]) + "<br/>" + \
			"<strong>Created time</strong> " + str(item["uco-observable:observableCreatedTime"]) + "<hr/>"
		return html_text


	def gather_all_web_search_terms(self):
		html_text="<h2>Web Search Terms data</h2><br/>"
		for item in webSearchTerm:
			html_text = html_text + \
			"<strong>Search term</strong> " + str(item["uco-observable:searchTerm"]) + "<hr/>"
		return html_text


	def gather_all_wireless_nets(self) -> str:
		html_text="<h2>Wireless Network connections</h2><br/>"
		for item in wireless_net:
			html_text = html_text + \
			"<strong>SSID</strong> " + str(item["uco-observable:ssid"]) + "<br/>" + \
			"<strong>Base station</strong> " + str(item["uco-observable:baseStation"]) + "<hr/>"
		return html_text


### global funtions
def process_id_messages():
	for m in chatMessages:
		if m["uco-observable:application-id"]:
			for a in applications:
				if a["@id"] == m["uco-observable:application-id"]:
					m["uco-observable:application"] = a["uco-core:name"]
					break
		if m["uco-observable:from-id"]:
			for a in accounts:
				if a["@id"] == m["uco-observable:from-id"]:
					msg_from = a["uco-observable:phoneAccount"] + " " + \
					a["uco-observable:accountIdentifier"] + " / " + a["uco-observable:displayName"]
					m["uco-observable:from"] = msg_from
					break
		
		msg_to = []
		if m["uco-observable:to-id"]:
			if len(m["uco-observable:to-id"]) > 0:
				for toId in m["uco-observable:to-id"]:
					for a in accounts:
						if a["@id"] == toId["@id"]:
							msg_to.append(a["uco-observable:phoneAccount"] + " " + \
							a["uco-observable:accountIdentifier"] + " / " + a["uco-observable:displayName"])
							break
				m["uco-observable:to"] = msg_to
			
	for m in smsMessages:
		if m["uco-observable:from-id"]:
			for a in accounts:
				if a["@id"] == m["uco-observable:from-id"]:
					msg_from = a["uco-observable:phoneAccount"] + " " + \
					a["uco-observable:accountIdentifier"] + " / " + a["uco-observable:displayName"]
					m["uco-observable:from"] = msg_from
					break
		if len(m["uco-observable:to-id"]) > 0:
			msg_to = []
			for toId in m["uco-observable:to-id"]:
				for a in accounts:
					if a["@id"] == toId["@id"]:
						msg_to.append(a["uco-observable:phoneAccount"] + " " + \
						a["uco-observable:accountIdentifier"] + " / " + a["uco-observable:displayName"])
						break
			m["uco-observable:to"] = msg_to

def process_id_cookies():
	for c in cookies:
		if c["uco-observable:cookieAppId"]:
			for a in applications:
				if a["@id"] == c["uco-observable:cookieAppId"]:
					c["uco-observable:cookieApp"] = a["uco-core:name"]
					break


def process_id_email_accounts():
	for e in emailAccounts:
		for a in emailAddresses:
			if a["@id"] == e["uco-observable:addressId"]:
				e["uco-observable:addressValue"] = a["uco-observable:addressValue"]
				break

def process_id_email_messages():
	for m in emailMessages:
		for e in emailAccounts:
			if e["@id"] == m["uco-observable:fromId"]:
				m["uco-observable:from"] = e["uco-observable:addressValue"]
				break
		
		if len(m["uco-observable:toId"]) > 0:
			emailToId = m["uco-observable:toId"][0]["@id"]
			for e in emailAccounts:
				if e["@id"] == emailToId:
					m["uco-observable:to"] = e["uco-observable:addressValue"]
		
		if len(m["uco-observable:ccId"]) > 0:
			emailCcId = m["uco-observable:ccId"][0]["@id"]
			for e in emailAccounts:
				if e["@id"] == emailCcId:
					m["uco-observable:cc"] = e["uco-observable:addressValue"]
					break
		if len(m["uco-observable:bccId"]) > 0:
			emailBccId = m["uco-observable:bccId"][0]["@id"]
			for e in emailAccounts:
				if e["@id"] == emailBccId:
					m["uco-observable:bcc"] = e["uco-observable:addressValue"]
					break

def process_attachments():
	for item in chatMessages:
		for attachment in relationAttachmentsTo:
			if item["@id"] == attachment["uco-observable:attachmentTarget"]:
				fileAttached = ''
				for f in filesImage:
					if f["@id"] == attachment["uco-observable:attachmentSource"]:
						fileAttached += f["uco-observable:fileName"] + ';'
						break
				for f in filesVideo:
					if f["@id"] == attachment["uco-observable:attachmentSource"]:
						fileAttached += f["uco-observable:fileName"] + ';'
						break
				for f in filesAudio:
					if f["@id"] == attachment["uco-observable:attachmentSource"]:
						fileAttached += f["uco-observable:fileName"] + ';'
						break
				item["uco-observable:attachedFiles"] = fileAttached


def processRelationAttachments(jsonObj):
	id_attachment_source = jsonObj["uco-core:source"]["@id"]
	id_attachment_target = jsonObj["uco-core:target"]["@id"]
	try:
		relationAttachmentsTo.append(
			{
				"uco-observable:attachmentSource":id_attachment_source,
				"uco-observable:attachmentTarget":id_attachment_target
			})
	except Exception as e:
		print("ERROR: in appending dictionary to chatMessages")
		print (e)


def processRelationConnectedTo(jsonObj):
	id_connected_source = jsonObj["uco-core:source"]["@id"]
	id_connected_target = jsonObj["uco-core:target"]["@id"]
	
	startTime = get_optional_dict_attribute(jsonObj, "uco-observable:startTime", {})
	if startTime:
		startTime = jsonObj["uco-observable:startTime"]["@value"]
	
	endTime = get_optional_dict_attribute(jsonObj, "uco-observable:endTime", {})
	if endTime:
		endTime = jsonObj["uco-observable:endTime"]["@value"]
	
	try:
		relationConnectedTo.append(
			{
				"uco-core:source":id_connected_source,
				"uco-core:target":id_connected_target,
				"uco-observable:startTime": startTime,
				"uco-observable:endTime": endTime
			})
	except Exception as e:
		print("ERROR: in appending dictionary to chatMessages")
		print (e)


def processRelationMappedBy(jsonObj):
	id_mapped_by_target = jsonObj["uco-core:target"]["@id"]
	latitude_mapped_by = ''
	longitude_mapped_by = ''
	for c in geo_coordinates:
		if c["@id"] == id_mapped_by_target:
			latitude_mapped_by = c["uco-location:latitude"]
			longitude_mapped_by = c["uco-location:longitude"]
			break
	start_date = get_optional_dict_attribute(jsonObj, "uco-observable:startTime", {})
	if start_date:
		start_date = jsonObj["uco-observable:startTime"]["@value"]
	try:
		relationMappedBy.append(
			{
				"uco-observable:mappedByLatitude":latitude_mapped_by,
				"uco-observable:mappedByLongitude":longitude_mapped_by,
				"uco-observable:mappedByStartDate":start_date
				#"not-in-ontology:locationType":category
			})
	except Exception as e:
		print("ERROR: in appending dictionary to Relation Mapped_By")
		print (e)


def processMessage(uuid_object=None, facet=None):
	msg_text = get_optional_string_attribute(facet, "uco-observable:messageText", '')
	msg_app_id = get_optional_dict_attribute(facet, "uco-observable:application", {})
	if msg_app_id:
		msg_app_id = facet["uco-observable:application"]["@id"]

	msg_sent_time = get_optional_dict_attribute(facet, "uco-observable:sentTime", {})
	if msg_sent_time:
		msg_sent_time = facet["uco-observable:sentTime"]["@value"]
	
	msg_from_id = get_optional_dict_attribute(facet, "uco-observable:from", {})
	if msg_from_id:
		msg_from_id = facet["uco-observable:from"]["@id"]
	
	msg_to_id = get_optional_list_attribute(facet, "uco-observable:to", [])
	if msg_to_id:
		msg_to_id = facet["uco-observable:to"]

	msg_type = get_optional_string_attribute(facet, "uco-observable:messageType", "")

	try:
		if msg_type == "SMS/Native Message":
			smsMessages.append(
				{
					"@id":uuid_object,
					"uco-observable:messageText":msg_text,
					"uco-observable:messageTypte":msg_type,
					"uco-observable:application":'Native',
					"uco-observable:sentTime": msg_sent_time,
					"uco-observable:from-id":msg_from_id,
					"uco-observable:from":"-",
					"uco-observable:to-id":msg_to_id,
					"uco-observable:to":"",
					"uco-observable:messageType":'SMS/Native Message'
				})
		else:
			chatMessages.append(
				{
					"@id":uuid_object,
					"uco-observable:messageText":msg_text,
					"uco-observable:application-id":msg_app_id,
					"uco-observable:application":"-",
					"uco-observable:sentTime": msg_sent_time,
					"uco-observable:from-id":msg_from_id,
					"uco-observable:from":"-",
					"uco-observable:to-id":msg_to_id,
					"uco-observable:to":"-",
					"uco-observable:attachedFiles": "",
					"uco-observable:messageType":'CHAT Message'
				}
			)
	except Exception as e:
		print("ERROR: in appending dictionary to either ChatMessages or SMSmessages")
		print (e)


def processThread(uuid_object=None, facet=None):
	thread_participants = list()
	for p in facet["uco-observable:participant"]:
		thread_participants.append(p["@id"])
	thread = facet["uco-observable:messageThread"]
	thread_len = get_optional_integer_attribute(thread, "co:size", "-")
	thread_messages = list()
	thread_elements = facet["uco-observable:messageThread"]["co:element"]
	if isinstance(thread_elements, dict):
		thread_elements = [thread_elements]
	for m in thread_elements:
		thread_messages.append(m["@id"])
	try:
		chatThreads.append(
			{
				"@id":uuid_object,
				"thread:length": thread_len,
				"thread:messages":thread_messages,
				"thread:participants": thread_participants
			})
	except Exception as e:
		print("ERROR: in appending dictionary to chatThreads, @id=" + uuid_object)
		print (e)


def processAccount(uuid_object=None, facet=None, kind=None):
	accountFound = False
	accountPhoneNumber = ""
	accountIdentifier = ""
	accountApplication = ""
	accountName = ""

	if kind == "AccountFacet":
		accountIdentifier = get_optional_string_attribute(facet, "uco-observable:accountIdentifier", "")
		for a in accounts:
			if a["@id"] == uuid_object:
				a["uco-observable:accountIdentifier"] = accountIdentifier
				accountFound = True
				break
	elif kind == "ApplicationAccountFacet":
		idApp = get_optional_dict_attribute(facet, "uco-observable:application", {})
		if idApp:
			idApp = facet["uco-observable:application"]["@id"]
		accountApplication = '?'
		for app in applications:
			if app["@id"] == idApp:
				accountApplication = app["uco-core:name"]
				break
		for a in accounts:
			if a["@id"] == uuid_object:
				a["uco-observable:application"] = accountApplication
				accountFound = True
				break
	elif kind == "PhoneAccountFacet":
		accountPhoneNumber = get_optional_string_attribute(facet, "uco-observable:phoneNumber", "")
		accountName = get_optional_string_attribute(facet, "uco-observable:accountIdentifier", "")
		for a in accounts:
			if a["@id"] == uuid_object:
				a["uco-observable:phoneAccount"] = accountPhoneNumber
				a["uco-observable:displayName"] = accountName
				accountFound = True
				break
	elif kind == "DigitalAccountFacet":
		accountName = get_optional_string_attribute(facet, "uco-observable:displayName", "")
		for a in accounts:
			if a["@id"] == uuid_object:
				a["uco-observable:displayName"] = accountName
				accountFound = True
				break

	if not accountFound:
		try:
			accounts.append(
				{
					"@id":uuid_object,
					"uco-observable:accountIdentifier": accountIdentifier,
					"uco-observable:phoneAccount":accountPhoneNumber,
					"uco-observable:application":accountApplication,
					"uco-observable:displayName": accountName
				}
			)
		except Exception as e:
			print("ERROR: in appending dictionary to accounts")
			print (e)


def processEmailAddress(uuid_object=None, facet=None):
	accountEmail = get_optional_string_attribute(facet, "uco-observable:addressValue", "")
	try:
		emailAddresses.append(
			{
				"@id":uuid_object,
				"uco-observable:addressValue": accountEmail
			})
	except Exception as e:
		print("ERROR: in appending dictionary to emailAddresses")
		print (e)


def processEmailAccount(uuid_object=None, facet=None):
	accountEmailId = facet["uco-observable:emailAddress"]["@id"]
	addressEmail = "-"
	
	try:
		emailAccounts.append(
			{
				"@id":uuid_object,
				"uco-observable:addressId": accountEmailId,
				"uco-observable:addressValue": addressEmail,
			})
	except Exception as e:
		print("ERROR: in appending dictionary to emailAddresses")
		print (e)


def processBluetooth(uuid_object=None, facet=None):
	bt_address = get_optional_string_attribute(facet, "uco-observable:addressValue", "")
	try:
		bluetooths.append(
			{
				"@id":uuid_object,
				"uco-observable:addressValue": bt_address,
				#"uco-core:name": btName
			})
	except Exception as e:
		print("ERROR: in appending dictionary to Bluetooth Connecitons")
		print (e)


def processCellSite(uuid_object=None, facet=None):
	cellMcc = get_optional_string_attribute(facet, "uco-observable:cellSiteCountryCode", "")
	cellCid = get_optional_string_attribute(facet, "uco-observable:cellSiteIdentifier", "")
	cellLac = get_optional_string_attribute(facet, "uco-observable:cellSiteLocationAreaCode", "")
	cellMnc = get_optional_string_attribute(facet, "uco-observable:cellSiteNetworkCode", "")
	cellType = get_optional_string_attribute(facet, "uco-observable:cellSiteType", "")
	try:
		cell_sites.append(
			{
				"@id":uuid_object,
				"uco-observable:cellSiteCountryCode": cellMcc,
				"uco-observable:cellSiteIdentifier": cellCid,
				"uco-observable:cellSiteNetworkCode": cellMnc,
				"uco-observable:cellSiteLocationAreaCode": cellLac,
				"uco-observable:cellSiteType": cellType,
			})
	except Exception as e:
		print("ERROR: in appending dictionary to Cell Site")
		print (e)


def processEvents(jsonObj, facet):
	eventId = jsonObj["@id"]
	eventCreated = get_optional_dict_attribute(facet, "uco-observable:observableCreatedTime", {})
	if eventCreated:
		eventCreated = facet["uco-observable:observableCreatedTime"]["@value"]
	eventType = get_optional_string_attribute(facet, "uco-observable:eventType", "")
	eventText = get_optional_string_attribute(facet, "uco-observable:eventText", "")
	try:
		events.append(
			{
				"@id":eventId,
				"uco-observable:observableCreatedTime": eventCreated,
				"uco-observable:eventType": eventType,
				"uco-observable:eventText": eventText
			})
	except Exception as e:
		print("ERROR: in appending dictionary to Event Record")
		print (e)


def processSearchedItems(jsonObj, facet):
	searchId = jsonObj["@id"]
	searchApp = get_optional_dict_attribute(facet, "uco-observable:application", {})
	if searchApp:
		searchAppId = facet["uco-observable:application"]["@id"]
		for a in applications:
			if a["@id"] == searchAppId:
				searchApp = a["uco-core:name"]
				break
	searchLaunchTime = get_optional_string_attribute(facet, "drafting:searchLaunchedTime", '')
	if searchLaunchTime:
		searchLaunchTime = facet["drafting:searchLaunchedTime"]["@value"]
	searchValue = get_optional_string_attribute(facet, "drafting:searchValue", "")
	try:
		searched_items.append(
			{
				"@id":searchId,
				"drafting:searchSource": searchApp,
				"drafting:searchLaunchedTime": searchLaunchTime,
				"drafting:searchValue": searchValue
			})
	except Exception as e:
		print("ERROR: in appending dictionary to SearchedItems")
		print (e)


def processSocialMediaActivities(jsonObj, facet):
	socialId = jsonObj["@id"]
	socialBody = get_optional_string_attribute(facet, "uco-observable:body", "")
	socialTitle = get_optional_string_attribute(facet, "uco-observable:pageTitle", "")
	socialDate = get_optional_dict_attribute(facet, "uco-observable:observableCreatedTime", {})
	if socialDate:
		socialDate = facet["uco-observable:observableCreatedTime"]["@value"]
	socialAppId = get_optional_dict_attribute(facet, "uco-observable:application", {})
	socialApp = ''
	if socialAppId:
		socialAppId = facet["uco-observable:application"]["@id"]
		for a in applications:
			if a["@id"] == socialAppId:
				socialApp = a["uco-core:name"]
				break
	socialAuthorId = get_optional_string_attribute(facet, "drafting:authorIdentifier", "")
	socialAccountId = get_optional_string_attribute(facet, "uco-observable:accountIdentifier", "")
	socialName = get_optional_string_attribute(facet, "drafting:authorName", "")
	socialType = get_optional_list_attribute(facet, "@type", [])
	if socialType:
		socialType = facet["@type"][0]
	try:
		social_media_activities.append(
			{
				"@id":socialId,
				"uco-observable:body":socialBody,
				"uco-observable:pageTitle":socialTitle,
				"uco-observable:observableCreatedTime": socialDate,
				"uco-observable:application": socialApp,
			"drafting:authorIdentifier": socialAuthorId,
		"uco-observable:accountIdentifier": socialAccountId,
		"drafting:authorName": socialName,
		"drafting:activityType": socialType
			})
	except Exception as e:
		print("ERROR: in appending dictionary to Social Media Activity")
		print (e)


def processWirelessNetwork(jsonObj, facet) -> None:
	assert isinstance(jsonObj["@id"], str), "Anonymous object found in CASE JSON-LD data."
	wId = jsonObj["@id"]
	wSsid = get_optional_string_attribute(facet, "uco-observable:ssid", '')
	wBssid = get_optional_string_attribute(facet, "uco-observable:baseStation", '')
	try:
		wireless_net.append(
			{
				"@id":wId,
				"uco-observable:ssid": wSsid,
				"uco-observable:baseStation": wBssid,
			})
	except Exception as e:
		print("ERROR: in appending dictionary to Wireless Network")
		print (e)


def processCookie(uuid_object=None, facet=None):
	cookieAppId = get_optional_dict_attribute(facet, "uco-observable:application", {})
	if cookieAppId:
		cookieAppId = facet["uco-observable:application"]["@id"]
	cookieApp = "-"
	cookieName = get_optional_string_attribute(facet, "uco-observable:cookieName", '')
	cookiePath = get_optional_string_attribute(facet, "uco-observable:cookiePath", '')
	
	cookieCreatedTime = get_optional_dict_attribute(facet, "uco-observable:observableCreatedTime", {})
	if cookieCreatedTime:
		cookieCreatedTime = facet["uco-observable:observableCreatedTime"]["@value"]

	cookieLastAccessedTime = get_optional_dict_attribute(facet, "uco-observable:accessedTime", {})
	if cookieLastAccessedTime:
		cookieLastAccessedTime = facet["uco-observable:accessedTime"]["@value"]
	
	cookieExpirationTime = get_optional_dict_attribute(facet, "uco-observable:expirationTime", {})
	if cookieExpirationTime:
		cookieExpirationTime = facet["uco-observable:expirationTime"]["@value"]
	
		
	try:
		cookies.append(
			{
				"@id":uuid_object,
				"uco-observable:cookieAppId": cookieAppId,
				"uco-observable:cookieApp": cookieApp,
				"uco-observable:cookieName": cookieName,
				"uco-observable:cookiePath": cookiePath,
				"uco-observable:observableCreatedTime": cookieCreatedTime,
				"uco-observable:accessedTime": cookieLastAccessedTime,
				"uco-observable:expirationTime": cookieExpirationTime
			})
	except Exception as e:
		print("ERROR: in appending dictionary to cookies")
		print (e)


def processCoordinate(uuid_object=None, facet=None):
	coordinateLat = get_optional_dict_attribute(facet, "uco-location:latitude", {})
	if coordinateLat:
		coordinateLat = facet["uco-location:latitude"]["@value"]
	coordinateLong = get_optional_dict_attribute(facet, "uco-location:longitude", {})
	if coordinateLong:
		coordinateLong = facet["uco-location:longitude"]["@value"]
	coordinateAlt = get_optional_dict_attribute(facet, "uco-location:altitude", {})
	if coordinateAlt:
		coordinateAlt = facet["uco-location:altitude"]["@value"]
	try:
		geo_coordinates.append(
			{
				"@id":uuid_object,
				"uco-location:latitude": coordinateLat,
				"uco-location:longitude": coordinateLong,
				"uco-location:altitude": coordinateAlt
			})
	except Exception as e:
		print("ERROR: in appending dictionary to geo coordinate")
		print (e)


def processApplication(uuid_object=None, facet=None):
	applicationName = get_optional_string_attribute(facet, "uco-core:name", "")
	if applicationName:
		applicationName = get_optional_string_attribute(facet, "uco-observable:applicationIdentifier", "yyy")
	try:
		applications.append(
			{
				"@id":uuid_object,
				"uco-core:name": applicationName
			})
	except Exception as e:
		print("ERROR: in appending dictionary to applications")
		print (e)


def processCall(uuid_object=None, facet=None):
	#callId = jsonObj["@id"]
	callFromId = get_optional_dict_attribute(facet, "uco-observable:from", {})
	callFrom = "-"
	if callFromId:
		callFromId = callFromId["@id"]
		for a in accounts:
			if a["@id"] == callFromId:
				callFrom = a["uco-observable:phoneAccount"] + " / " + \
					a["uco-observable:accountIdentifier"]
				break
	callToId = get_optional_dict_attribute(facet, "uco-observable:to", {})
	if callToId:
		callToId = facet["uco-observable:to"]["@id"]
		callTo = "-"
		if isinstance(callToId, dict):
			for a in accounts:
				if a["@id"] == callToId["@id"]:
					callTo = a["uco-observable:phoneAccount"] + " / " + \
						a["uco-observable:accountIdentifier"]
					break
		elif isinstance(callToId, list):
			for to_item in callToId:
				for a in accounts:
					if a["@id"] == to_item["@id"]:
						callTo = a["uco-observable:phoneAccount"] + " / " + \
							a["uco-observable:accountIdentifier"]
						break

	callApplication = "-"
	callApplicationId = get_optional_dict_attribute(facet, "uco-observable:application", {})
	if callApplicationId:
		callApplicationId = facet["uco-observable:application"]["@id"]
		for a in applications:
			if a["@id"] == callApplicationId:
				callApplication = a["uco-core:name"]
	callStartTime = get_optional_dict_attribute(facet, "uco-observable:startTime", {})
	if callStartTime:
		callStartTime = facet["uco-observable:startTime"]["@value"]
	callDuration = get_optional_integer_attribute(facet, "uco-observable:duration", "-")
	try:
		phoneCalls.append(
			{
				"@id":uuid_object,
				"uco-observable:from":callFrom,
				"uco-observable:to":callTo,
				"uco-core:name":callApplication,
				"uco-observable:startTime":callStartTime,
			  "uco-observable:duration":callDuration,
			})
	except Exception as e:
		print("ERROR: in appending dictionary to Call")
		print (e)


def processCalendar(uuid_object=None, facet=None):
	calendarSubject = get_optional_string_attribute(facet, "uco-observable:subject", "")
	calendarRepeatInterval = get_optional_string_attribute(facet, "uco-observable:recurrence", "")
	calendarStatus = get_optional_string_attribute(facet, "uco-observable:eventStatus", "")
	calendarStartTime = get_optional_dict_attribute(facet, "uco-observable:startTime", {})
	if calendarStartTime:
		calendarStartTime = facet["uco-observable:startTime"]["@value"]
	calendarEndTime = get_optional_dict_attribute(facet, "uco-observable:endTime", {})
	if calendarEndTime:
		calendarEndTime = facet["uco-observable:endTime"]["@value"]
	try:
		calendars.append(
			{
				"@id":uuid_object,
				"uco-observable:subject":calendarSubject,
				"uco-observable:startTime":calendarStartTime,
			  "uco-observable:endTime":calendarEndTime,
			  "uco-observable:recurrence":calendarRepeatInterval,
			  "uco-observable:eventStatus":calendarStatus
			})
	except Exception as e:
		print("ERROR: in appending dictionary to Calendar")
		print (e)


def processEmailMessage(jsonObj, facet):
	emailId = jsonObj["@id"]
	emailSentTime = get_optional_dict_attribute(facet, "uco-observable:sentTime", {})
	if emailSentTime:
		emailSentTime = facet["uco-observable:sentTime"]["@value"]
	
	emailFromId = get_optional_dict_attribute(facet, "uco-observable:from", {})
	if emailFromId:
		emailFromId = facet["uco-observable:from"]["@id"]
	
	emailFrom = ""
	emailToId = get_optional_list_attribute(facet, "uco-observable:to", [])
	if emailToId:
		emailToId = facet["uco-observable:to"]
	emailTo = ""
	emailCcId = get_optional_list_attribute(facet, "uco-observable:cc", [])
	if emailCcId:
		emailCcId = facet["uco-observable:cc"]
	emailCc = ""
	emailBccId = get_optional_list_attribute(facet, "uco-observable:bcc", [])
	if emailBccId:
		emailBccId = facet["uco-observable:bcc"]
	emailBcc = ""
	emailBody = get_optional_string_attribute(facet, "uco-observable:body", "")
	emailSubject = get_optional_string_attribute(facet, "uco-observable:subject", "")
	
	try:
		emailMessages.append(
			{
				"@id":emailId,
				"uco-observable:fromId":emailFromId,
				"uco-observable:from":emailFrom,
				"uco-observable:toId":emailToId,
				"uco-observable:to":emailTo,
				"uco-observable:ccId":emailCcId,
				"uco-observable:cc":emailCc,
				"uco-observable:bccId":emailBccId,
				"uco-observable:bcc":emailBcc,
				"uco-observable:sentTime":emailSentTime,
				"uco-observable:body":emailBody,
				"uco-observable:subject":emailSubject,
			})
	except Exception as e:
		print("ERROR: in appending dictionary to emailMessage")
		print (e)


def processFile(jsonObj, facet):
	fileId = jsonObj["@id"]
	fileTag = get_optional_string_attribute(facet, "uco-observable:mimeType", "")
	fileName = get_optional_string_attribute(facet, "uco-observable:fileName", "")
	filePath = get_optional_string_attribute(facet, "uco-observable:filePath", "")
	fileSize = get_optional_integer_attribute(facet, "uco-observable:sizeInBytes", "-")
	tagProcessed = False;
	try:
		fileTagNorm = fileTag.lower()
		if fileTagNorm in ('image', 'pictures', 'live photos'):
			filesImage.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True
		if fileTagNorm == 'audio':
			filesAudio.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True
		if fileTagNorm.find('text') > -1:
			filesText.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True
		if fileTagNorm.find('pdf') > -1:
			filesPDF.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True
		if fileTagNorm.find('rtf') > -1:
			filesRTF.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True
		if fileTagNorm.find('word') > -1:
			filesWord.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True
		if fileTagNorm.find('video') > -1:
			filesVideo.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True
		if fileTagNorm == 'archives':
			filesArchive.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True
		if fileTagNorm.find('database') > -1:
			filesDatabase.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True
		if fileTagNorm == 'application':
			filesApplication.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True
		if not tagProcessed:
			filesUncategorized.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
	except Exception as e:
		print("ERROR: in appending dictionary to file")
		print (e)


def processURL(jsonObj, facet):
	webId = jsonObj["@id"]
	webUrl = facet["uco-observable:fullValue"]
	try:
		webURLs.append(
			{
				"@id":webId,
				"uco-observable:url":webUrl
			})
	except Exception as e:
		print("ERROR: in appending dictionary to webURL")
		print (e)


def processWebBookmark(jsonObj, facet):
	webId = jsonObj["@id"]
	webCreatedTime = ''
	webApp = ""
	webUrl = ""
	webPath = ""
	browserId = get_optional_dict_attribute(facet, "uco-observable:application", {})
	if browserId:
		browserId = facet["uco-observable:application"]["@id"]
		for a in applications:
			if a["@id"] == browserId:
				webApp = a["uco-core:name"]
	webCreatedTime = get_optional_string_attribute(facet, "uco-observable:observableCreatedTime", '')
	if webCreatedTime:
		webCreatedTime = facet["uco-observable:observableCreatedTime"]["@value"]
	webUrlId = get_optional_dict_attribute(facet, "uco-observable:urlTargeted", {})
	if webUrlId:
		webUrlId = facet["uco-observable:urlTargeted"]["@id"]
		for u in webURLs:
			if u["@id"] == webUrlId:
				webUrl = u["uco-observable:url"]
				break
	else:
		webUrl = "-"
	webPath = get_optional_string_attribute(facet, "uco-observable:bookmarkPath", "")
	try:
		webBookmark.append(
			{
				"@id":webId,
				"uco-observable:application":webApp,
				"uco-observable:urlTargeted": webUrl,
				"uco-observable:bookmarkPath":webPath,
				"uco-observable:observableCreatedTime":webCreatedTime
			})
	except Exception as e:
		print("ERROR: in appending dictionary to Web Bookmark")
		print (e)


def processURLHistory(jsonObj, facet):
	webId = jsonObj["@id"]
	webLastVisited = ''
	webTitle = ""
	webUrl = ""
	webApp = ""
	search_term = get_optional_string_attribute(facet["uco-observable:urlHistoryEntry"][0], "uco-observable:keywordSearchTerm", '')
	if search_term:
		search_term = search_term.replace('\n','').replace('\r', '').replace('\t', ' ')
		try:
			webSearchTerm.append(
				{
					"@id":webId,
					"uco-observable:searchTerm":search_term,
				})
		except Exception as e:
			print("ERROR: in appending dictionary to webSearchTerm")
			print (e)
			return
		return
	browserId = get_optional_dict_attribute(facet, "uco-observable:browserInformation", {})
	if browserId:
		browserId = facet["uco-observable:browserInformation"]["@id"]
		for a in applications:
			if a["@id"] == browserId:
				webApp = a["uco-core:name"]
	else:
		webApp = "-"
	firstVisit = get_optional_string_attribute(facet["uco-observable:urlHistoryEntry"][0], "uco-observable:firstVisit", '')
	if firstVisit:
		firstVisit = facet["uco-observable:urlHistoryEntry"][0]["uco-observable:firstVisit"]["@value"]
	lastVisit = get_optional_string_attribute(facet["uco-observable:urlHistoryEntry"][0], "uco-observable:lastVisit", '')
	if lastVisit:
		lastVisit = facet["uco-observable:urlHistoryEntry"][0]["uco-observable:lastVisit"]["@value"]
	webUrlId = get_optional_dict_attribute(facet["uco-observable:urlHistoryEntry"][0], "uco-observable:url", {})
	webUrl = "-"
	if webUrlId:
		webUrlId = webUrlId["@id"]
		for w in webURLs:
			if w["@id"] == webUrlId:
				webUrl = w["uco-observable:url"]
	webTitle = get_optional_string_attribute(facet["uco-observable:urlHistoryEntry"][0], "uco-observable:pageTitle", "")
	try:
		webURLHistory.append(
			{
				"@id":webId,
				"uco-observable:browserInformation":webApp,
				"uco-observable:url": webUrl,
				"uco-observable:title":webTitle,
				"uco-observable:lastVisited":webLastVisited,
			})
	except Exception as e:
		print("ERROR: in appending dictionary to URLHistory")
		print (e)


def number_with_dots(n: Union[int, str]) -> str:
	if isinstance(n, int) or isinstance(n, str):
		n = str(n)
		num_dots = n[-3:]
		n = n[:-3]
		while n:
			num_dots = n[-3:] + "." + num_dots
			n = n[:-3]
		return(num_dots)
	else:
		raise TypeError('Parameter must be either integer or string')

#--- Gobal variables
chatMessages: list[dict[str, str]] = []
chatThreads: list[dict[str, str]] = []
#chatMessageAttachments = []
cookies: list[dict[str, str]] = []
geo_coordinates: list[dict[str, str]] = []
cell_sites: list[dict[str, str]] = []
bluetooths: list[dict[str, str]] = []
searched_items: list[dict[str, str]] = []
social_media_activities: list[dict[str, str]] = []
events: list[dict[str, str]] = []
relationAttachmentsTo: list[dict[str, str]] = []
relationMappedBy: list[dict[str, str]] = []
relationConnectedTo: list[dict[str, str]] = []
smsMessages: list[dict[str, str]] = []
accounts: list[dict[str, str]] = []
emailAddresses: list[dict[str, str]] = []
emailAccounts: list[dict[str, str]] = []
applications: list[dict[str, str]] = []
phoneCalls: list[dict[str, str]] = []
calendars: list[dict[str, str]] = []
emailMessages: list[dict[str, str]] = []
filesUncategorized: list[dict[str, str]] = []
filesImage: list[dict[str, str]] = []
filesAudio: list[dict[str, str]] = []
filesText: list[dict[str, str]] = []
filesPDF: list[dict[str, str]] = []
filesWord: list[dict[str, str]] = []
filesRTF: list[dict[str, str]] = []
filesVideo: list[dict[str, str]] = []
filesArchive: list[dict[str, str]] = []
filesDatabase: list[dict[str, str]] = []
filesApplication: list[dict[str, str]] = []
webURLs: list[dict[str, str]] = []
webURLHistory: list[dict[str, str]] = []
webSearchTerm: list[dict[str, str]] = []
webBookmark: list[dict[str, str]] = []
wireless_net: list[dict[str, str]] = []

tableData: list[list[str]] = [[]]
treeData: list[dict[str,str]] = []

def main():
	C_GREEN = '\033[32m'
	C_RED = '\033[31m'
	C_BLACK = '\033[0m'
	C_CYAN = '\033[36m'
	EMPTY_DATA = "1900-01-01T00:00:00"

	parser = argparse.ArgumentParser()
	parser.add_argument("--debug", action="store_true")
	parser.add_argument("--dry-run", action="store_true", help="Run application, exiting without initiating GUI.")
	parser.add_argument("input_jsonld")
	args = parser.parse_args()

	logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

#--- Read input file in CASE-JSON format
	try:
		f = codecs.open(args.input_jsonld, 'r', encoding='utf-8')
	except Exception as e:
		print(C_RED + '\n' + "ERROR in trying to open the file " + args.input_jsonld)
		print (e)
		sys.exit('Open file failed.')
	try:
		print(C_CYAN + "Load JSON structure, it might take some time, please wait ...\n")
		json_obj = json.load(f)
		if args.dry_run:
			logging.info("Exiting dry run.")
			sys.exit(0)
		app = QApplication([])
		_widget=QWidget()
		msgBox = QMessageBox()
		reply = msgBox.question(_widget, "CASE syntax check result",
								"Syntax check went well! Do you want to continue?",
								QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

		if reply == QMessageBox.No:
			sys.exit('Terminate by user.')

#--- Loop over all Observables of the array "uco-core:object"
		if 'uco-core:object' in json_obj.keys():
			json_data = json_obj['uco-core:object']
		elif '@graph' in json_obj.keys():
			json_data = json_obj['@graph']
		else:
			sys.exit(C_RED + "\n Neither key uco-core:object nor @graph have been found. \
				\n" + C_BLACK)

		nObjects = 0
		for jsonObj in json_data:
			nObjects +=1
			uuid_object = jsonObj['@id']
			print(f"{C_GREEN} Observable n. {str(nObjects)} - uuid={uuid_object}", end='\r')
			dataFacets = get_optional_list_attribute(jsonObj, "uco-core:hasFacet", [])
			if not dataFacets:
				observableType = get_optional_string_attribute(jsonObj, "@type", "")
				# Only the ObservableRelationship is considered.
				# Others (i.e. uco-identity:Identity, case-investigation:InvestigativeAction,
				# uco-tool:Tool, uco-identity:Organization, uco-role:Role,
				# case-investigation:ProvenanceRecord, case-investigation:InvestigativeAction)
				# are ignored.
				if observableType == "uco-observable:ObservableRelationship":
					if jsonObj["uco-core:kindOfRelationship"] == "Attached_To":
						processRelationAttachments(jsonObj)
					elif jsonObj["uco-core:kindOfRelationship"] == "Mapped_By":
						processRelationMappedBy(jsonObj)
					elif jsonObj["uco-core:kindOfRelationship"] == "Connected_To":
						processRelationConnectedTo(jsonObj)
			else:
				if isinstance(dataFacets, dict):
					dataFacets = [dataFacets]

				for facet in dataFacets:
					assert isinstance(facet, dict)
					facet_type = facet["@type"]
					objectType: str
					if isinstance(facet_type, str):
						objectType = facet_type
					elif isinstance(facet_type, list):
						assert isinstance(facet_type[0], str)
						objectType = facet_type[0] # SocialMediaActivityFacet
					else:
						raise TypeError("Unexpected type for property %r: %r." % (facet_type, type(facet_type)))
					# print(f"objectType={objectType}")
					if objectType == "uco-observable:MessageFacet":
						processMessage(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-observable:SMSMessageFacet":
						processMessage(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-observable:BluetoothAddressFacet":
						processBluetooth(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-observable:CellSiteFacet":
						processCellSite(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-observable:BrowserCookieFacet":
						processCookie(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-location:LatLongCoordinatesFacet":
						processCoordinate(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-observable:MessageThreadFacet":
						processThread(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-observable:AccountFacet":
						processAccount(uuid_object=uuid_object, facet=facet, kind="AccountFacet")
					elif objectType == "uco-observable:ApplicationAccountFacet":
						processAccount(uuid_object=uuid_object, facet=facet, kind="ApplicationAccountFacet")
					elif objectType == "uco-observable:DigitalAccountFacet" :
						processAccount(uuid_object=uuid_object, facet=facet, kind="DigitalAccountFacet")
					elif objectType == "uco-observable:PhoneAccountFacet":
						processAccount(uuid_object=uuid_object, facet=facet, kind="PhoneAccountFacet")
					elif objectType == "uco-observable:EmailAccountFacet":
						processEmailAccount(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-observable:ApplicationFacet":
						processApplication(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-observable:EmailAddressFacet":
						processEmailAddress(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-observable:CalendarEntryFacet":
						processCalendar(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-observable:CallFacet":
						processCall(uuid_object=uuid_object, facet=facet)
					elif objectType == "uco-observable:EmailMessageFacet":
						processEmailMessage(jsonObj, facet)
					elif objectType == "uco-observable:FileFacet":
						processFile(jsonObj, facet)
					elif objectType == "uco-observable:URLFacet":
						processURL(jsonObj, facet)
					elif objectType == "uco-observable:URLHistoryFacet":
						processURLHistory(jsonObj, facet)
					elif objectType == "uco-observable:BrowserBookmarkFacet":
						processWebBookmark(jsonObj, facet)
					elif objectType == "uco-observable:WirelessNetworkConnectionFacet":
						processWirelessNetwork(jsonObj, facet)
					elif objectType == "drafting:SocialMediaActivityFacet":
						processSocialMediaActivities(jsonObj, facet)
					elif objectType == "uco-observable:EventRecordFacet":
						processEvents(jsonObj, facet)
		process_id_messages()
		process_id_cookies()
		process_id_email_accounts()
		process_id_email_messages()
		process_attachments()
	except Exception as e:
		print(C_CYAN + "ERROR: in Loading the JSON structure! \n\n" + C_BLACK + "\n\n")
		print (e)
		sys.exit('Load JSON file failed. \n')

	f.close()
	print(C_CYAN + "\n\nEnd Observables processing!" + C_BLACK + "\n\n")

	i = 1
	totMessages = 0

	# for w in webURLs:
	# 	print(f"@id= {w['@id']}")
	# 	print(f"URL= {w['uco-observable:url']}")
	
	treeData.insert(0, {'unique_id': ':00000000', 'parent_id': '0', 'short_name': 'Cyber items' })

	totAccounts = len(accounts)
	if totAccounts > 0:
		accountText = 'Accounts ' + '(' + number_with_dots(totAccounts) + ')'
		treeData.append({'unique_id': ':Accounts', 'parent_id': ':00000000', 'short_name': accountText })

	totCalendars = len(calendars)
	if totCalendars > 0:
		calendarText = 'Calendars ' + '(' + number_with_dots(totCalendars) + ')'
		treeData.append({'unique_id': ':Calendars', 'parent_id': ':00000000', 'short_name': calendarText })

	totCalls = len(phoneCalls)
	if totCalls > 0:
		callText = 'Calls ' + '(' + number_with_dots(totCalls) + ')'
		treeData.append({'unique_id': ':Calls', 'parent_id': ':00000000', 'short_name': callText })

	totCellSites = len(cell_sites)
	if totCellSites > 0:
		cellSiteText = 'CellSite ' + '(' + number_with_dots(totCellSites) + ')'
		treeData.append({'unique_id': ':CellSites', 'parent_id': ':00000000', 'short_name': cellSiteText })

	for t in chatThreads:
		id = t['@id']
		text = 'chat N. ' + str(i) + ' (' + number_with_dots(t["thread:length"]) + ')'
		totMessages += int(t["thread:length"])
		treeData.append({'unique_id': id, 'parent_id': ':ChatMessages', 'short_name': text})
		i = i + 1

	totChats = len(chatThreads)
	if totChats > 0:
		chatText = 'Chats ' + '(' + number_with_dots(totChats) + '/' + number_with_dots(totMessages) + ')'
		treeData.append({'unique_id': ':ChatMessages', 'parent_id': ':00000000', 'short_name': chatText})

	totCookies = len(cookies)
	if totCookies > 0:
		cookieText = 'Cookies ' + '(' + number_with_dots(totCookies) + ')'
		treeData.append({'unique_id': ':Cookies', 'parent_id': ':00000000', 'short_name': cookieText })

	totBluetooths = len(bluetooths)
	if totBluetooths > 0:
		btText = 'Device connection (Bluetooth) ' + '(' + number_with_dots(totBluetooths) + ')'
		treeData.append({'unique_id': ':Bluetooths', 'parent_id': ':00000000', 'short_name': btText })

	totEmails = len(emailMessages)
	if totEmails > 0:
		emailText = 'Emails ' + '(' + number_with_dots(totEmails) + ')'
		treeData.append({'unique_id': ':EmailMessages', 'parent_id': ':00000000', 'short_name': emailText })

	totEvents = len(events)
	if totEvents > 0:
		eventText = 'Events ' + '(' + number_with_dots(totEvents) + ')'
		treeData.append({'unique_id': ':Events', 'parent_id': ':00000000', 'short_name': eventText })

	totFiles = (len(filesUncategorized) + len(filesImage) + len(filesArchive) +
				len(filesVideo) + len(filesAudio) + + len(filesText) + len(filesDatabase) +
				len(filesApplication) + len(filesPDF) + len(filesWord) + len(filesRTF))
	fileText = 'Files ' + '(' + number_with_dots(totFiles) + ')'
	treeData.append({'unique_id': ':Files', 'parent_id': ':00000000', 'short_name': fileText })

	totImages = len(filesImage)
	if totImages > 0:
		imageText = 'Images ' + '(' + number_with_dots(totImages) + ')'
		treeData.append({'unique_id': ':Images', 'parent_id': ':Files', 'short_name': imageText })

	totAudios = len(filesAudio)
	if totAudios > 0:
		audioText = 'Audios ' + '(' + number_with_dots(totAudios) + ')'
		treeData.append({'unique_id': ':Audios', 'parent_id': ':Files', 'short_name': audioText })

	totTexts = len(filesText)
	if totTexts > 0:
		textText = 'Texts ' + '(' + number_with_dots(totTexts) + ')'
		treeData.append({'unique_id': ':Texts', 'parent_id': ':Files', 'short_name': textText })

	totPDF = len(filesPDF)
	if totPDF > 0:
		pdfText = 'PDFs ' + '(' + number_with_dots(totPDF) + ')'
		treeData.append({'unique_id': ':PDFs', 'parent_id': ':Files', 'short_name': pdfText })

	totWord = len(filesWord)
	if totWord > 0:
		wordText = 'Words ' + '(' + number_with_dots(totWord) + ')'
		treeData.append({'unique_id': ':Words', 'parent_id': ':Files', 'short_name': wordText })

	totWord = len(filesRTF)
	if totWord > 0:
		rtfText = 'RTFs ' + '(' + number_with_dots(totWord) + ')'
		treeData.append({'unique_id': ':RTFs', 'parent_id': ':Files', 'short_name': rtfText })

	totVideos = len(filesVideo)
	if totVideos > 0:
		videoText = 'Videos ' + '(' + number_with_dots(totVideos) + ')'
		treeData.append({'unique_id': ':Videos', 'parent_id': ':Files', 'short_name': videoText })

	totArchives = len(filesArchive)
	if totArchives > 0:
		archiveText = 'Archives ' + '(' + number_with_dots(totArchives) + ')'
		treeData.append({'unique_id': ':Archives', 'parent_id': ':Files', 'short_name': archiveText })

	totDatabases = len(filesDatabase)
	if totDatabases > 0:
		databaseText = 'Databases ' + '(' + number_with_dots(totDatabases) + ')'
		treeData.append({'unique_id': ':Databases', 'parent_id': ':Files', 'short_name': databaseText })

	totApplications = len(filesApplication)
	if totApplications > 0:
		applicationText = 'Applications ' + '(' + number_with_dots(totApplications) + ')'
		treeData.append({'unique_id': ':Applications', 'parent_id': ':Files', 'short_name': applicationText })

	totUncategorized = len(filesUncategorized)
	if totUncategorized > 0:
		uncategorizedText = 'Uncategorized ' + '(' + number_with_dots(totUncategorized) + ')'
		treeData.append({'unique_id': ':Uncategorized', 'parent_id': ':Files', 'short_name': uncategorizedText })

	totLocationDevice = len(relationMappedBy)
	if totLocationDevice > 0:
		locationText = 'Location device ' + '(' + number_with_dots(totLocationDevice) + ')'
		treeData.append({'unique_id': ':LocationDevice', 'parent_id': ':00000000', 'short_name': locationText })

	totSearchedItems = len(searched_items)
	if totSearchedItems > 0:
		searchedItemsText = 'Searched items ' + '(' + number_with_dots(totSearchedItems) + ')'
		treeData.append({'unique_id': ':SearchedItems', 'parent_id': ':00000000', 'short_name': searchedItemsText })

	totSocialMediaActivities = len(social_media_activities)
	if totSocialMediaActivities > 0:
		socialMediaActivitiesText = 'Social media activities ' + '(' + number_with_dots(totSocialMediaActivities) + ')'
		treeData.append({'unique_id': ':SocialMediaActivities', 'parent_id': ':00000000', 'short_name': socialMediaActivitiesText })

	totSMSs = len(smsMessages)
	if totSMSs > 0:
		smsText = 'SMSs ' + '(' + number_with_dots(totSMSs) + ')'
		treeData.append({'unique_id': ':Sms', 'parent_id': ':00000000', 'short_name': smsText })

	totWebBookmarks = len(webBookmark)
	if totWebBookmarks > 0:
		webBookmarkText = 'Web Bookmarks ' + '(' + number_with_dots(totWebBookmarks) + ')'
		treeData.append({'unique_id': ':WebBookmarks', 'parent_id': ':00000000', 'short_name': webBookmarkText })

	totWebs = len(webURLHistory)
	if totWebs > 0:
		webText = 'Web Histories ' + '(' + number_with_dots(totWebs) + ')'
		treeData.append({'unique_id': ':WebHistories', 'parent_id': ':00000000', 'short_name': webText })

	totWirelessNet = len(wireless_net)
	if totWirelessNet > 0:
		wirelessNetText = 'Wireless Net ' + '(' + number_with_dots(totWirelessNet) + ')'
		treeData.append({'unique_id': ':WirelessNet', 'parent_id': ':00000000', 'short_name': wirelessNetText })

	totSearch = len(webSearchTerm)
	if totSearch > 0:
		webSearchText = 'Web Search Terms ' + '(' + number_with_dots(totSearch) + ')'
		treeData.append({'unique_id': ':WebSearchTerms', 'parent_id': ':00000000', 'short_name': webSearchText })

#--- Set the UI layout
	_view = view(treeData, tableData)
	_view.setGeometry(50, 50, 1400, 800)
	_view.setWindowTitle('Cyber items view - ' + args.input_jsonld + ' (n. Observables: ' + number_with_dots(nObjects) + ')')
	_view.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
