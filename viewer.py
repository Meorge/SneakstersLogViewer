from PyQt5 import QtWidgets, QtGui
import sys, re, traceback

from PyQt5 import QtGui
logfile_parser = r'^(?:UnloadTime:.*?\n+|\n)(.*?\(Filename: (.*?)\))'

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		self.initUI()
		self.setupMenuBar()

	def initUI(self):
		self.list = QtWidgets.QListWidget()
		self.list.currentRowChanged.connect(self.updateCurrentRow)
		self.textField = QtWidgets.QTextEdit()
		self.textField.setReadOnly(True)

		self.mainLayout = QtWidgets.QSplitter()
		self.mainLayout.addWidget(self.list)
		self.mainLayout.addWidget(self.textField)

		self.setCentralWidget(self.mainLayout)

	def updateCurrentRow(self, newRow):
		self.textField.setText(self.logfile.matches[newRow].message)

	def setupMenuBar(self):
		self.menuBar = QtWidgets.QMenuBar()
		self.fileMenu = self.menuBar.addMenu("&File")

		self.openAction = QtWidgets.QAction("&Open", self)
		self.openAction.setShortcut(QtGui.QKeySequence.Open)
		self.openAction.triggered.connect(self.openFile)

		self.fileMenu.addAction(self.openAction)
		self.setMenuBar(self.menuBar)

	def openFile(self):
		openFrom = QtWidgets.QFileDialog.getOpenFileName(self, "Open Log File")
		print(openFrom)
		if openFrom[0] == "": return
		file = open(openFrom[0], 'r')

		try:
			data = file.read()
			file.close()

			self.list.clear()

			self.logfile = LogFile(data)
			for i in self.logfile.matches:
				new_list_item = QtWidgets.QListWidgetItem()
				if i.type != "message": new_list_item.setForeground(getColorForMessageType(i))
				new_list_item.setText(i.getFirstLines())
				self.list.addItem(new_list_item)

		except Exception as ex:
			traceback.print_exc()
			return



class LogFile:
	def __init__(self, text=""):
		self.raw_text = text
		self.parse_text()

	def parse_text(self):
		raw_matches = re.findall(logfile_parser, self.raw_text, re.S | re.M)

		self.matches = []
		for i in raw_matches:
			self.matches.append(LogItem(i))


class LogItem:
	def __init__(self, tup):
		self.__message = tup[0]
		self.__line = tup[1]

		# this is an exception
		if self.__message.split('\n')[0] == "Uploading Crash Report":
			self.__type = "exception"
			self.__message = self.__message.split('\n',1)[1]

		elif "LogError" in self.__message or "LogFormatError" in self.__message:
			self.__type = "error"

		elif "LogWarning" in self.__message or "LogFormatWarning" in self.__message:
			self.__type = "warning"

		else:
			self.__type = "message"

	@property
	def message(self):
		return self.__message

	def getFirstLines(self, lines=1):
		return "[" + self.type + "] " + '\n'.join(self.message.split('\n')[:lines])

	@property
	def line(self):
		return self.__line

	@property
	def type(self):
		return self.__type


def getColorForMessageType(message):
	if message.type == "exception": return QtGui.QColor(255,40,40)
	elif message.type == "error": return QtGui.QColor(255, 80, 80)
	elif message.type == "warning": return QtGui.QColor(250, 180, 0)
	else: return QtGui.QColor(255,255,255)
		
if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())