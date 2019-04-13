from PyQt5 import QtWidgets,uic,QtCore
import os
from InvoiceApi import API
import Database
def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
	# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)
base2,form2=uic.loadUiType(resource_path('cust.ui'))
class InputPopup(base2,form2):
	def __init__(self):
		super(base2,self).__init__()
		self.setupUi(self)
	def getResults(self):
		if self.exec_():
			name = self.name.text()
			street=self.street.toPlainText()
			city=self.city.text()
			state=self.state.text()
			postcode=self.postcode.text()
			gst=self.gst.text()
			l = [name,street,city,state,postcode,gst]
			if all(l):
				return l
			else:
				return None




class Invoice:
	def __init__(self):
		self.app = QtWidgets.QApplication([])
		self.dlg = uic.loadUi(resource_path("test.ui"))
		self.dlg.addBtn.clicked.connect(self.addRow)
		self.dlg.finalBtn.clicked.connect(self.finalize)
		self.dlg.setFixedSize(807,616)
		self.dlg.dateEdit.setDateTime(QtCore.QDateTime.currentDateTime())
		self.dlg.itmtbl.itemChanged.connect(self.updateTotal)
		self.dlg.totalCost.setText("0.0")
		self.dlg.remBtn.clicked.connect(self.removeRow)
		self.dlg.discount.valueChanged.connect(self.offerDiscount)
		self.dlg.show()
		self.app.exec_()

	def offerDiscount(self):
		price=float(self.dlg.totalCost.text())
		if(price!=0):
			price = round(((100-float(self.dlg.discount.value()))/100)*self.start_price,2)
			self.dlg.totalCost.setText(str(price))

	def showInfo(self,title,inf,inf_tip):
		self.msg = QtWidgets.QMessageBox()
		self.msg.setIcon(QtWidgets.QMessageBox.Information)
		self.msg.setText(inf)
		self.msg.setInformativeText(inf_tip)
		self.msg.setWindowTitle(title)
		self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
		return self.msg.show()

	def addRow(self):
		numRows = self.dlg.itmtbl.rowCount()
		if numRows!=0 and (self.dlg.itmtbl.item(numRows-1,0).text()==""):
			self.showInfo("Empty Name field","Error: Name field can't be empty","Please update the Name field and then add new row")
			return
		#print(numRows)
		self.dlg.itmtbl.insertRow(numRows)
		self.dlg.itmtbl.setItem(numRows,0,QtWidgets.QTableWidgetItem(""))

		itm = QtWidgets.QTableWidgetItem("0.00")
		itm.setData(QtCore.Qt.EditRole, 0.00)
		self.dlg.itmtbl.setItem(numRows,1,itm)


		itm2 = QtWidgets.QTableWidgetItem("2")
		itm2.setData(QtCore.Qt.EditRole, 1)
		self.dlg.itmtbl.setItem(numRows,2,itm2)


		self.dlg.itmtbl.setItem(numRows,3,QtWidgets.QTableWidgetItem(""))

		self.dlg.itmtbl.setItem(numRows,4,QtWidgets.QTableWidgetItem("9"))

		itm = QtWidgets.QTableWidgetItem("0")
		itm.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
		self.dlg.itmtbl.setItem(numRows,5,itm)

	def updateTotal(self,no):
		if no.column()==1 or no.column()==2 or no.column()==4:
			try:
				previousPrice=round(float(self.dlg.itmtbl.item(no.row(),5).text()),2)
				price = float(self.dlg.itmtbl.item(no.row(),1).text())
				qty = int(float(self.dlg.itmtbl.item(no.row(),2).text()))
				gst = int(self.dlg.itmtbl.item(no.row(),4).text())
				new_total = round((price*qty)*(100+gst)/100,2)
				self.dlg.itmtbl.item(no.row(),5).setText(str(new_total))
				if not hasattr(self,"start_price"):
					self.start_price=float(self.dlg.totalCost.text())
				self.start_price=round(self.start_price-previousPrice+new_total,2)
				self.dlg.totalCost.setText(str(self.start_price))
			except AttributeError as e:
				pass
			except TypeError:
				self.dlg.itmtbl.item(no.row(),5).setText("0")
	def removeRow(self):
		selection = self.dlg.itmtbl.selectedIndexes()
		total_cost = float(self.dlg.totalCost.text())
		for item in selection:
			self.start_price-=float(self.dlg.itmtbl.item(item.row(),5).text())
			self.dlg.itmtbl.removeRow(item.row())
		self.offerDiscount()

	def finalize(self):
		if len(self.dlg.bName.text())==0 or len(self.dlg.bAddr.toPlainText())==0 or len(self.dlg.bGST.text())==0:
			self.showInfo("Empty Client Fields","Error: Client Fields Can't be empty","Please verify if all client fields are correctly filled")
			return
		self.dlg.addr_list=Database.getAddressLines()
		if len(self.dlg.addr_list)==0:
			w=InputPopup()
			values = w.getResults()
			if values:
				self.dlg.addr_list = values
				Database.putAddressLines(values)
			else:
				self.showInfo("Empty Bussiness Provider Info","Error: Empty Bussiness information","Please ensure you enter your business information correctly")
				return
		if QtWidgets.QMessageBox.question(self.dlg,'Prompt for Invoice Generation', "Are you sure to generate invoice ?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)==QtWidgets.QMessageBox.Yes:
				self.dlg.DB_NO = Database.getInvoiceNumber()
				self.invGen = API(self.dlg)
				self.invGen.makeInvoice()
				Database.updateInvoiceNumber(self.dlg.DB_NO+1)

Invoice()
