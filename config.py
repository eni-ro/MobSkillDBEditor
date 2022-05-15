import os
from PyQt5 import uic,QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import *
import yaml

class MobSkillDbConfigDialog(QDialog):
	def __init__(self):
		QDialog.__init__(self)
		uic.loadUi(os.path.join(os.getcwd(), 'settings.ui'),self)
		# setup db file contents view
		self.listMobDB = self.listView_MobDB
		self.modelMobDB = QStringListModel(self.listMobDB)
		self.listMobDB.setModel(self.modelMobDB)
		self.listMobDB.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.listMobDB.customContextMenuRequested.connect(self.onListRightClickMobDB)
		
		self.listSkillDB = self.listView_SkillDB
		self.modelSkillDB = QStringListModel(self.listSkillDB)
		self.listSkillDB.setModel(self.modelSkillDB)
		self.listSkillDB.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.listSkillDB.customContextMenuRequested.connect(self.onListRightClickSkillDB)
		
		self.listMobSkillDB = self.listView_MobSkillDB
		self.modelMobSkillDB = QStringListModel(self.listMobSkillDB)
		self.listMobSkillDB.setModel(self.modelMobSkillDB)
		self.listMobSkillDB.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.listMobSkillDB.customContextMenuRequested.connect(self.onListRightClickMobSkillDB)
		

	def show(self, currentMobDb : list, currentSkillDB : list, currentMobSkillDB : list):
		self.modelMobDB.setStringList(currentMobDb.copy())
		self.modelSkillDB.setStringList(currentSkillDB.copy())
		self.modelMobSkillDB.setStringList(currentMobSkillDB.copy())
		ok = self.exec()
		if ok:
			return True,self.modelMobDB.stringList(),self.modelSkillDB.stringList(),self.modelMobSkillDB.stringList()
		else:
			return False,None,None,None
	
	def onListRightClickMobDB(self,pos):
		self.onListRightClick(pos,self.listMobDB,self.modelMobDB)
	def onListRightClickSkillDB(self,pos):
		self.onListRightClick(pos,self.listSkillDB,self.modelSkillDB)
	def onListRightClickMobSkillDB(self,pos):
		self.onListRightClick(pos,self.listMobSkillDB,self.modelMobSkillDB)
	
	def onListRightClick(self,pos,clickedList,clickedModel):
		self._clickedList = clickedList
		self._clickedModel = clickedModel
		_menu = QMenu(self)
		_addTemplate = QAction('add file before', self, triggered=self.addItemBefore)
		_menu.addAction(_addTemplate)
		_addBlank = QAction('add file after', self, triggered=self.addItemAfter)
		_menu.addAction(_addBlank)
		_delete = QAction('delete', self, triggered=self.deleteItem)
		_menu.addAction(_delete)
		_menu.exec_(clickedList.mapToGlobal(pos))
	
	def addItemBefore(self):
		_fname = QFileDialog.getOpenFileName(self, 'Select DB file')
		if _fname[0]:
			_idx = self._clickedList.currentIndex()
			_row = _idx.row()
			if _row < 0:
				_row = 0
			self._clickedModel.insertRow(_row)
			_idx = self._clickedModel.createIndex(_row,0)
			self._clickedList.setCurrentIndex(_idx)
			self._clickedModel.setData(_idx,_fname[0],Qt.EditRole)

	def addItemAfter(self):
		_fname = QFileDialog.getOpenFileName(self, 'Select DB file')
		if _fname[0]:
			_idx = self._clickedList.currentIndex()
			_row = min(_idx.row()+1,len(self._clickedModel.stringList()))
			self._clickedModel.insertRow(_row)
			_idx = self._clickedModel.createIndex(_row,0)
			self._clickedList.setCurrentIndex(_idx)
			self._clickedModel.setData(_idx,_fname[0],Qt.EditRole)
	
	def deleteItem(self):
		_idx = self._clickedList.currentIndex()
		if _idx.row() >= 0:
			self._clickedModel.removeRow(_idx.row())

class MobSkillDbConfig:
	settingFile = os.path.join(os.getcwd(), 'config.yml')
	def __init__(self) -> None:
		self.mobDbFiles=list()
		self.skillDbFiles=list()
		self.mobSkillDbFiles=list()
		if os.path.isfile(__class__.settingFile):
			with open(__class__.settingFile, 'r') as f:
				_cnf = yaml.load(f.read(),Loader=yaml.CBaseLoader)
			if _cnf:
				if 'MobDB' in _cnf:
					self.mobDbFiles = list(_cnf['MobDB'])
				if 'SkillDB' in _cnf:
					self.skillDbFiles = list(_cnf['SkillDB'])
				if 'MobSkillDB' in _cnf:
					self.mobSkillDbFiles = list(_cnf['MobSkillDB'])
	def save(self):
		_db = {}
		if len(self.mobDbFiles):
			_db['MobDB']=self.mobDbFiles
		if len(self.skillDbFiles):
			_db['SkillDB']=self.skillDbFiles
		if len(self.mobSkillDbFiles):
			_db['MobSkillDB']=self.mobSkillDbFiles
		with open(__class__.settingFile,'w') as f:
			yaml.dump(_db,f)

