import sys
from os.path import (dirname, join)
from PyQt5 import uic,QtCore,QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import *
#from ruamel.yaml import YAML
import yaml
import re
import os
from enum import Enum
from config import MobSkillDbConfigDialog,MobSkillDbConfig

class HashListModel(QAbstractTableModel):
	def __init__(self, hash_list, key_list, return_key, parent = None):
		QAbstractTableModel.__init__(self, parent)
		self.list = hash_list
		self.key_list = key_list
		self.return_key = return_key

	def rowCount(self, parent = None):
		return len(self.list)

	def columnCount(self, parent = None):
		return len(self.key_list)

	def flags(self, index):
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable

	def data(self, index, role = Qt.DisplayRole):
		if role == Qt.EditRole:
			return None

		if role == Qt.DisplayRole:
			row = index.row()
			column = index.column()
			if row >= 0 and column >= 0 and self.key_list[column] in self.list[row]:
				value = self.list[row][self.key_list[column]]
			else:
				value = ''
			return value
	
	def selectedReturnValue(self,index,role):
		if role == Qt.EditRole:
			return None
		if role == Qt.DisplayRole:
			row = index.row()
			if row >= 0 and self.return_key in self.list[row]:
				value = self.list[row][self.return_key]
			else:
				value = None
			return value

	def setData(self, index, value, role = Qt.EditRole):
		return False

	def headerData(self, section, orientation, role):

		if role == Qt.DisplayRole:

			if orientation == Qt.Horizontal:

				if section < len(self.key_list):
					return self.key_list[section]
				else:
					return ''
			else:
				return section

class SelectorDialog(QDialog):
	def __init__(self,hash_list,key_list,return_key):
		QDialog.__init__(self)
		uic.loadUi(join(os.getcwd(), 'selector.ui'),self)
		self.contents = hash_list
		
		self.table = self.tableView
		self.model = HashListModel(hash_list,key_list,return_key)
		self.table.setModel(self.model)
		self.filter = self.lineEdit_Filter
		self.filter.textChanged.connect(self.onFilterChanged)
		
	
	def onFilterChanged(self):
		filter = self.filter.text().lower()
		if filter == '':
			for row in range(self.model.rowCount()):
				self.table.setRowHidden(row, False)
		else:
			for row in range(self.model.rowCount()):
				hide = True
				for col in range(self.model.columnCount()):
					if filter in str(self.model.data(self.model.index(row,col,QModelIndex()),Qt.DisplayRole)).lower():
						hide = False
						break
				self.table.setRowHidden(row, hide)
	def clearFilter(self):
		self.filter.setText('')
		self.onFilterChanged()
	def show(self):
		ok = self.exec()
		if ok:
			return self.model.selectedReturnValue(self.table.selectionModel().currentIndex(),Qt.DisplayRole)
		else:
			return None
	
	def findByKeyValue(self,findKey,findValue,returnKey):
		for _dic in self.contents:
			if findKey in _dic and _dic[findKey] == findValue:
				if returnKey in _dic:
					return _dic[returnKey]
				else:
					return None
		return None

class SkillDbItem(Enum):
	MobId = 0
	DummyValue = 1
	State = 2
	SkillID = 3
	SkillLv = 4
	Rate = 5
	CastTime = 6
	Delay = 7
	Cancelable = 8
	Target = 9
	ConditionType = 10
	ConditionValue = 11
	Val1 = 12
	Val2 = 13
	Val3 = 14
	Val4 = 15
	Val5 = 16
	Emotion = 17
	Chat = 18

class SkillListMode(QStringListModel):
	re_mobid = re.compile(r'^(\d*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?),([^,]*?)\n?$')

	def __init__(self, parent = None):
		QStringListModel.__init__(self, parent)
	def dbItem(self,index : QModelIndex, dbitem : SkillDbItem, role = Qt.DisplayRole):
		if role == Qt.EditRole:
			return None

		if role == Qt.DisplayRole:
			_str = self.data(index,role)
			_m = __class__.re_mobid.search(_str)
			if _m:
				item = _m.groups()[dbitem.value]
				if dbitem == SkillDbItem.Cancelable:
					item = True if item == 'yes' else False
				return item
			else:
				return None
	def dbItems(self,index : QModelIndex, role = Qt.DisplayRole):
		if role == Qt.EditRole:
			return None

		if role == Qt.DisplayRole:
			_str = self.data(index,role)
			if _str is None:
				return None
			_m = __class__.re_mobid.search(_str)
			if _m:
				items = list(_m.groups())
				items[SkillDbItem.Cancelable.value] = True if items[SkillDbItem.Cancelable.value] == 'yes' else False
				return items
			else:
				return None
	def setDbItems(self,index : QModelIndex, itemList : list, role = Qt.DisplayRole):
		if role == Qt.EditRole:
			itemList[SkillDbItem.Cancelable.value] = 'yes' if itemList[SkillDbItem.Cancelable.value] == True else 'no'
			self.setData(index,','.join(itemList),role)
			

class MobSkillDbEditorWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		uic.loadUi(join(os.getcwd(), 'mobskill.ui'),self)

		self.setWindowTitle(self.windowTitle() + ' v0.1')

		self._dbItemObjects = (
			[self.lineEdit_MobId,self.toolButton_MobId],
			[self.lineEdit_DummyValue,self.toolButton_DummyValue],
			[self.comboBox_State],
			[self.lineEdit_SkillId,self.toolButton_SkillId],
			[self.lineEdit_SkillLv],
			[self.lineEdit_Rate],
			[self.lineEdit_CastTime],
			[self.lineEdit_Delay],
			[self.checkBox_Cancelable],
			[self.comboBox_Target],
			[self.comboBox_ConditionType],
			[self.lineEdit_ContitionValue],
			[self.lineEdit_Val1],
			[self.lineEdit_Val2],
			[self.lineEdit_Val3],
			[self.lineEdit_Val4],
			[self.lineEdit_Val5],
			[self.lineEdit_Emotion],
			[self.lineEdit_Chat],
		)

		# set button icon
		_pixmapi = getattr(QStyle, 'SP_BrowserReload')
		_icon = self.style().standardIcon(_pixmapi)
		self.toolButton_DummyValue.setIcon(_icon)
		_pixmapi = getattr(QStyle, 'SP_FileDialogContentsView')
		_icon = self.style().standardIcon(_pixmapi)
		self.toolButton_MobId.setIcon(_icon)
		self.toolButton_SkillId.setIcon(_icon)

		# setup combobox menu
		self.comboBox_State.addItems(['any','idle','walk','dead','loot','attack','angry','chase','follow','without','anytarget'])
		self.comboBox_Target.addItems(['target','self','friend','master','randomtarget'])
		self.comboBox_ConditionType.addItems(['always','onspawn','myhpltmaxrate','myhpinrate','mystatuson','mystatusoff','friendhpltmaxrate','friendhpinrate','friendstatuson','friendstatusoff','attackpcgt','attackpcge','slavelt','slavele','closedattacked','longrangeattacked','skillused','afterskill','casttargeted','rudeattacked'])

		# setup db file contents view
		self._list = self.listView_Lines
		self._model = SkillListMode(self._list)
		self._list.setModel(self._model)
		self._list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self._list.customContextMenuRequested.connect(self.onListRightClick)

		# setup signal connection
		# -menu
		self.actionSave.triggered.connect(self.onSave)
		self.actionExit.triggered.connect(self.close)
		self.actionFilePath.triggered.connect(self.onConfig)
		# -listview
		self.comboBox_Files.currentIndexChanged.connect(self.onMonbSkillDbFileChanged)
		self.lineEdit_Filter.textChanged.connect(self.onFilterChanged)
		# -db items
		self.afterRefleshItems()
		self.toolButton_MobId.clicked.connect(self.invokeMobIdInputHelper)
		self.toolButton_DummyValue.clicked.connect(self.invokeDummyValueInputHelper)
		self.toolButton_SkillId.clicked.connect(self.invokeSkillIdInputHelper)
		# -line text
		self.afterRefleshLineText()
		
		# setup helper dialog
		
		self._cfg = MobSkillDbConfig()
		self.onUpdateConfig()

		#dirty check
		self._fileIsDirty = False
	
	def closeEvent(self, event):
		if self.saveCheck() == True:
			event.accept()
		else:
			event.ignore()
	
	def onConfig(self):
		if self.saveCheck() == False:
			return
		_gui = MobSkillDbConfigDialog()
		_ok,_mobDbFiles,_skillDbFiles,_mobSkillDbFiles = _gui.show(self._cfg.mobDbFiles,self._cfg.skillDbFiles,self._cfg.mobSkillDbFiles)
		if _ok:
			self._cfg.mobDbFiles = _mobDbFiles
			self._cfg.skillDbFiles = _skillDbFiles
			self._cfg.mobSkillDbFiles = _mobSkillDbFiles
			self._cfg.save()
			self.onUpdateConfig()
	
	def saveCheck(self):
		if self._fileIsDirty == False:
			return True
		
		_msgBox = QMessageBox(self)
		_msgBox.setWindowTitle('Save file ?')
		_msgBox.setText('Your changes will be discarded if proceed\nDo you want to save your changes?')
		_msgBox.setStandardButtons(QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
		_ret = _msgBox.exec_()
		
		if _ret == QMessageBox.Yes:
			self.onSave()
			return True
		elif _ret == QMessageBox.No:
			self._fileIsDirty = False
			return True
		else:
			return False
		
	def onSave(self):
		for _path,_model in self._mobSkillDbDic.items():
			with open(_path, 'w') as f:
				f.write('\n'.join(_model.stringList())+'\n')
		self._fileIsDirty = False
	
	def dbFileRead(self,curDict,filePath):
		if os.path.isfile(filePath):
			with open(filePath, 'r') as f:
				_addDict = yaml.load(f.read(),Loader=yaml.CBaseLoader)
				if 'Body' in _addDict:
					for _addItem in _addDict['Body']:
						if 'Id' in _addItem:
							_id = _addItem['Id']
							if _id in curDict:
								curDict[_id].update(_addItem)
							else:
								curDict[_id] = _addItem
	def onUpdateConfig(self):
		_skillDb = {}
		for _path in self._cfg.skillDbFiles:
			self.dbFileRead(_skillDb,_path)
		self._skillSelector = SelectorDialog(list(_skillDb.values()),['Id','Name','Description','MaxLevel'],'Id')
		
		_mobDb = {}
		for _path in self._cfg.mobDbFiles:
			self.dbFileRead(_mobDb,_path)
		self._mobSelector = SelectorDialog(list(_mobDb.values()),['Id','Name','JapaneseName'],'Id')

		self._mobSkillDbDic={}
		for _path in self._cfg.mobSkillDbFiles:
			if os.path.isfile(_path):
				with open(_path,'r') as f:
					_lines = map(lambda s: s.strip(), f.readlines())
				_model = SkillListMode(self._list)
				_model.setStringList(_lines)
				self._mobSkillDbDic[_path]=_model
		self.comboBox_Files.clear()
		self.comboBox_Files.addItems(self._mobSkillDbDic.keys())

	def onMonbSkillDbFileChanged(self):
		_file = self.comboBox_Files.currentText()
		if _file in self._mobSkillDbDic:
			self._model = self._mobSkillDbDic[_file]
			self._list.setModel(self._model)#model.setStringList(self._mobSkillDbDic[self.comboBox_Files.currentText()])
			self.listView_Lines.selectionModel().selectionChanged.connect(self.selectionChanged)
			self._list.setCurrentIndex(self._model.createIndex(0,0))
	
	def onFilterChanged(self):
		filter = self.lineEdit_Filter.text()
		if filter == '':
			for row in range(self._model.rowCount()):
				self._list.setRowHidden(row, False)
		else:
			for row in range(self._model.rowCount()):
				if filter in self._model.data(self._model.index(row,0),Qt.DisplayRole).lower():
					self._list.setRowHidden(row, False)
				else:
					self._list.setRowHidden(row, True)
	def onListRightClick(self,pos):
		_menu = QMenu(self)
		_addTemplate = QAction('add template line after', self, triggered=self.addTemplateItem)
		_menu.addAction(_addTemplate)
		_addBlank = QAction('add blank line after', self, triggered=self.addBlankItem)
		_menu.addAction(_addBlank)
		_delete = QAction('delete', self, triggered=self.deleteItem)
		_menu.addAction(_delete)
		_menu.exec_(self._list.mapToGlobal(pos))
	
	def addTemplateItem(self):
		_idx = self._list.currentIndex()
		_row = min(_idx.row()+1,len(self._model.stringList()))
		self._model.insertRow(_row)
		_idx = self._model.createIndex(_row,0)
		self._model.setDbItems(_idx,['1002','Poring@dummy','any','197','1','2000','0','0',False,'target','always','','','','','','','',''],Qt.EditRole)
		self._list.setCurrentIndex(_idx)
		self._fileIsDirty = True

	def addBlankItem(self):
		_idx = self._list.currentIndex()
		_row = min(_idx.row()+1,len(self._model.stringList()))
		self._model.insertRow(_row)
		_idx = self._model.createIndex(_row,0)
		self._list.setCurrentIndex(_idx)
		self._fileIsDirty = True
	
	def deleteItem(self):
		_idx = self._list.currentIndex()
		if _idx.row() >= 0:
			self._model.removeRow(_idx.row())
			self._fileIsDirty = True
	
	def selectionChanged(self,index):
		_listIdx = self.listView_Lines.currentIndex()
		self.refleshLineText(_listIdx)
		self.refleshItems(_listIdx)


	def beforeRefleshLineText(self):
		self.lineEdit_LineText.textChanged.disconnect(self.onLineTextChanged)
	def afterRefleshLineText(self):
		self.lineEdit_LineText.textChanged.connect(self.onLineTextChanged)
	
	def refleshLineText(self,index : QModelIndex):
		_str = index.data()#selectionModel().selection().indexes()[0]
		self.beforeRefleshLineText()
		if _str is not None:
			self.lineEdit_LineText.setText(_str)
		else:
			self.lineEdit_LineText.setText('')
		self.afterRefleshLineText()
		
	def beforeRefleshItems(self):
		for _item in self._dbItemObjects:
			_obj = _item[0]	#head object ontains skill db value
			if type(_obj) is QLineEdit:
				_obj.textChanged.disconnect(self.onItemsChanged)
			elif type(_obj) is QComboBox:
				_obj.currentIndexChanged.disconnect(self.onItemsChanged)
			elif type(_obj) is QCheckBox:
				_obj.stateChanged.disconnect(self.onItemsChanged)
	def afterRefleshItems(self):
		for _item in self._dbItemObjects:
			_obj = _item[0]	#head object ontains skill db value
			if type(_obj) is QLineEdit:
				_obj.textChanged.connect(self.onItemsChanged)
			elif type(_obj) is QComboBox:
				_obj.currentIndexChanged.connect(self.onItemsChanged)
			elif type(_obj) is QCheckBox:
				_obj.stateChanged.connect(self.onItemsChanged)
	def refleshItems(self,index : QModelIndex):
		_items = self._model.dbItems(index)
		self.beforeRefleshItems()
		if _items:
			for _itemIdx,_item in enumerate(self._dbItemObjects):
				for _objIdx,_obj in enumerate(_item):
					_obj.setEnabled(True)
					if _objIdx == 0:	#head object ontains skill db value
						if type(_obj) is QLineEdit:
							_obj.setText(_items[_itemIdx])
						elif type(_obj) is QComboBox:
							_obj.setCurrentIndex(_obj.findText(_items[_itemIdx]))
						elif type(_obj) is QCheckBox:
							_obj.setChecked(_items[_itemIdx])
		else:
			for _item in self._dbItemObjects:
				for _obj in _item:
					_obj.setEnabled(False)
		self.afterRefleshItems()
	
	def onItemsChanged(self):
		_values = []
		for _itemIdx,_item in enumerate(self._dbItemObjects):
			_obj = _item[0]	#head object ontains skill db value
			if type(_obj) is QLineEdit:
				_values.append(_obj.text())
			elif type(_obj) is QComboBox:
				_values.append(_obj.currentText())
			elif type(_obj) is QCheckBox:
				_values.append(_obj.isChecked())
		_listIdx = self.listView_Lines.currentIndex()
		self._model.setDbItems(_listIdx,_values,Qt.EditRole)
		self.refleshLineText(_listIdx)
		self._fileIsDirty = True
		
	
	def onLineTextChanged(self):
		_listIdx = self.listView_Lines.currentIndex()
		self._model.setData(_listIdx,self.lineEdit_LineText.text(),Qt.EditRole)
		self.refleshItems(_listIdx)
		self._fileIsDirty = True

	def invokeMobIdInputHelper(self):
		_input = self._mobSelector.show()
		if _input is not None:
			self.lineEdit_MobId.setText(_input)
	
	def invokeDummyValueInputHelper(self):
		_mobName = self._mobSelector.findByKeyValue('Id',self.lineEdit_MobId.text(),'JapaneseName')
		if _mobName is None:
			_mobName = self._mobSelector.findByKeyValue('Id',self.lineEdit_MobId.text(),'Name')
		if _mobName is not None:
			_skillName = self._skillSelector.findByKeyValue('Id',self.lineEdit_SkillId.text(),'Name')
			if _skillName is not None:
				self.lineEdit_DummyValue.setText('{}@{}'.format(_mobName,_skillName))
				

	def invokeSkillIdInputHelper(self):
		_input = self._skillSelector.show()
		if _input is not None:
			self.lineEdit_SkillId.setText(_input)

if __name__ == '__main__':	
	app = QApplication(sys.argv)
	app.setStyle('Fusion')

	skill_editor_ui = MobSkillDbEditorWindow()
	skill_editor_ui.show()

	sys.exit(app.exec_())