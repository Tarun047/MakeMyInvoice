import sqlite3
conn = sqlite3.connect('inv.db')
def checkState():
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM INVTAB")
    except:
        c.execute("CREATE TABLE INVTAB(invNo int,cAddr TEXT)")
        conn.commit()
checkState()
def getAddressLines():
    c = conn.cursor()
    l=list(c.execute("SELECT cAddr from INVTAB WHERE invNo=0"))
    if len(l)==0:
        return l
    else:
        return l[0][0].split("$")


def putAddressLines(address):
    address="$".join(address)
    c=conn.cursor()
    c.execute("INSERT INTO INVTAB VALUES(0,'{}')".format(address))
    c.execute("INSERT INTO INVTAB VALUES(1,'Empty')")
    conn.commit()

def getInvoiceNumber():
    c = conn.cursor()
    return list(c.execute("SELECT invNo from INVTAB WHERE cAddr='Empty'"))[0][0]

def updateInvoiceNumber(curr_no):
    c = conn.cursor()
    c.execute("update INVTAB SET invNo={} WHERE cAddr='Empty'".format(curr_no))
    conn.commit()
