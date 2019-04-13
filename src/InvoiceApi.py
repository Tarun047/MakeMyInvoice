from datetime import datetime, date
from invutils.models import InvoiceInfo, ServiceProviderInfo, ClientInfo, Item, Transaction,AddressInfo
from invutils.templates import SimpleInvoice
class API:
    def __init__(self,dialog):
        self.dlg = dialog
    def makeInvoice(self):
        self.doc = doc = SimpleInvoice('invoice - {}.pdf'.format(self.dlg.bName.text().replace("\\","").replace("/","")),discount=self.dlg.discount.value())
        self.doc.is_paid = self.dlg.paidBox.isChecked()
        if len(self.dlg.invNo.text())!=0:
            self.dlg.DB_NO=int(self.dlg.invNo.text())
        self.doc.invoice_info = InvoiceInfo(self.dlg.DB_NO,self.dlg.dateEdit.dateTime().toPyDateTime())
        self.doc.service_provider_info = ServiceProviderInfo(name=self.dlg.addr_list[0],street=self.dlg.addr_list[1],city=self.dlg.addr_list[2],state=self.dlg.addr_list[3],post_code=self.dlg.addr_list[4],vat_tax_number=self.dlg.addr_list[5])
        self.doc.client_info = ClientInfo(name=self.dlg.bName.text(),street=self.dlg.bAddr.toPlainText(),vat_tax_number=self.dlg.bGST.text())
        numRows = self.dlg.itmtbl.rowCount()
        for i in range(0,numRows):
            name = self.dlg.itmtbl.item(i,0).text()
            price = float(self.dlg.itmtbl.item(i,1).text())
            qty = int(self.dlg.itmtbl.item(i,2).text())
            hsn = self.dlg.itmtbl.item(i,3).text()
            gst = int(self.dlg.itmtbl.item(i,4).text())
            self.doc.add_item(Item(name,hsn,qty,price,gst))
        self.doc.finish()
