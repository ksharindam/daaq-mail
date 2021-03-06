import subprocess, re, time
import email
from email.header import decode_header
from email.utils import parsedate_tz, mktime_tz

from PyQt4 import QtCore
from PyQt4.QtGui import ( QWidget, QTextEdit, QMessageBox, QGridLayout, QLabel, QSizePolicy,
    QPixmap, QFontMetrics,
)
from PyQt4.QtGui import ( QDialog, QComboBox, QCheckBox, QLineEdit, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem
)
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
from keyring import Keyring

class ResourceLoader(QtCore.QThread):
    ''' loads images of qtextedit in separate thread '''
    resourceLoaded = QtCore.pyqtSignal(int, QtCore.QUrl, QtCore.QByteArray)
    def __init__(self, parent, res_type, url):
        QtCore.QThread.__init__(self, parent)
        self.res_type = res_type
        self.url = url

    def run(self):
        loop = QtCore.QEventLoop()
        nm = QNetworkAccessManager()
        reply = nm.get(QNetworkRequest(self.url))
        reply.finished.connect(loop.quit)
        loop.exec_()
        data = reply.readAll()
        self.resourceLoaded.emit(self.res_type, self.url, data)
        reply.deleteLater()
        nm.deleteLater()


class TextViewer(QTextEdit):
    def __init__(self, parent):
        QTextEdit.__init__(self, parent)
        self.setReadOnly(True)
        self.viewport().setMouseTracking(True)
        self.urls = []

    def mousePressEvent(self, ev):
        QTextEdit.mousePressEvent(self, ev)
        p = self.anchorAt(ev.pos())
        if p.startsWith("http"):
          confirm = QMessageBox.question(self, "Open Url in Browser", 
                    "Do you want to open browser to open...\n%s"%p, QMessageBox.Yes|QMessageBox.Cancel, QMessageBox.Yes)
          if confirm == 0x00004000:
            subprocess.Popen(["x-www-browser", p])

    def mouseMoveEvent(self, ev):
        if self.anchorAt(ev.pos())!='':
            self.viewport().setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.viewport().setCursor(QtCore.Qt.IBeamCursor)
        QTextEdit.mouseMoveEvent(self, ev)

    def loadResource(self, res_type, url):
        if url.toString() in self.urls: return QtCore.QVariant()
        self.urls.append(url.toString())
        #print res_type, url.toString()
        res_thread = ResourceLoader(self, res_type, url)
        res_thread.resourceLoaded.connect(self.setResource)
        res_thread.start()
        return QTextEdit.loadResource(self, res_type, url)

    def setResource(self, res_type, url, data):
        self.document().addResource(res_type, url, QtCore.QVariant(data))
        self.sender().deleteLater()
        self.viewport().update()    # force repaint to show image

    def clear(self):
        self.urls = []
        QTextEdit.clear(self)


class MailItem(QWidget):
    def __init__(self):
        super(MailItem, self).__init__()
        # Create Widgets
        self.layout = QGridLayout(self)
        self.iconLabel = QLabel(self)
        self.iconLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.iconLabel.setPixmap(QPixmap('mail-message-new.png'))
        self.senderLabel = QLabel(self)
        self.subjectLabel = QLabel(self)
        self.subjectLabel.setStyleSheet("QLabel { color: gray; font-size: 9pt;}")
        self.layout.addWidget(self.iconLabel, 0,0,1,1)
        self.layout.addWidget(self.senderLabel, 0,1,1,1)
        self.layout.addWidget(self.subjectLabel, 1,0,1,2)
        #print 

    def setData(self, sender, subject, uid, msg_id, date, cached, seen=True):
        self.sender = unicode(sender)
        self.subject = unicode(subject)
        self.uid = uid
        self.msg_id = msg_id
        self.date = date
        self.cached = int(cached)
        self.seen = seen
        self.mailSeen(self.seen)
        self.subjectLabel.setText(self.subject)

    def mailSeen(self, seen):
        name, addr = splitEmailAddr(self.sender)
        if seen:
            self.senderLabel.setText(name)
            self.iconLabel.setPixmap(QPixmap(':/mail-opened.png'))
        else:
            self.senderLabel.setText('<b>%s</b>' % name)
            self.iconLabel.setPixmap(QPixmap(':/mail.png'))


class MailInfoFrame(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(10, QtCore.Qt.white)
        self.setPalette(pal)
        fromText = QLabel('<font color=gray>From :</font>', self)
        dateText = QLabel('<font color=gray>Date :</font>', self)
        self.fromLabel = QLabel(self)
        self.subjectLabel = QLabel(self)
        self.dateLabel = QLabel(self)
        fromText.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        dateText.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.fromLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.subjectLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.dateLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        layout = QGridLayout(self)
        layout.addWidget(fromText, 0,0,1,1)
        layout.addWidget(self.fromLabel, 0,1,1,1)
        layout.addWidget(dateText, 1,0,1,1)
        layout.addWidget(self.dateLabel, 1,1,1,1)
        layout.addWidget(self.subjectLabel, 2,0,1,2)

    def setData(self, cellWidget):
        # Set Values
        self.sender = cellWidget.sender
        self.msg_id = cellWidget.msg_id
        self.subject = cellWidget.subject
        name, addr = splitEmailAddr(self.sender)
        if addr == '': addr = name
        setElidedText(self.fromLabel, addr)
        setElidedText(self.dateLabel, fromRfc2822(cellWidget.date))
        setElidedText(self.subjectLabel, '<b>%s</b>' % self.subject)

    def clear(self):
        self.sender, self.msg_id, self.subject = '', '', ''
        self.fromLabel.clear()
        self.dateLabel.clear()
        self.subjectLabel.clear()

re_mail_id = re.compile('(.*) <([^ ]+)>', re.I)

def splitEmailAddr(addr):
    addr = unicode(addr)
    m = re_mail_id.search(addr)
    if m:
        name = m.group(1)
        if name.startswith('"') : name = name[1:-1]
        return name, m.group(2)
    else:
        return addr, ''


def setElidedText(label, text):
    text = QFontMetrics(label.font()).elidedText(text, 1, label.width()-2)
    label.setText(text)

def fromRfc2822(date):
    py_time = mktime_tz(parsedate_tz(str(date)))
    return time.strftime("%d %b  %Y,  %I:%M %P", time.localtime(py_time))


class AccountManagerDialog(QDialog):
    def __init__(self, emails, types, parent):
        self.emails, self.types = emails, types
        QDialog.__init__(self, parent)
        self.resize(560, 350)
        self.gridLayout = QGridLayout(self)
        self.tableWidget = QTableWidget(0,2, self)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionBehavior(1) # Rows
        self.tableWidget.setSelectionMode(1) # Single
        self.tableWidget.horizontalHeader().setResizeMode(0, 1) # 1 = Stretch
        self.tableWidget.setHorizontalHeaderLabels(['Email', 'Type'])
        self.addBtn = QPushButton('+', self)
        self.removeBtn = QPushButton('-', self)
        self.closeBtn = QPushButton('Close', self)
        self.spacer = QWidget(self)
        self.spacer.setSizePolicy(1|2|4,1|4)
        self.gridLayout.addWidget(self.tableWidget, 0,0,1,4)
        self.gridLayout.addWidget(self.addBtn, 1,0,1,1)
        self.gridLayout.addWidget(self.removeBtn, 1,1,1,1)
        self.gridLayout.addWidget(self.spacer, 1,2,1,1)
        self.gridLayout.addWidget(self.closeBtn, 1,3,1,1)
        self.addBtn.clicked.connect(self.addAccount)
        self.removeBtn.clicked.connect(self.removeAccount)
        self.closeBtn.clicked.connect(self.accept)
        for i in range(len(self.emails)):
            self.tableWidget.insertRow(i)
            self.tableWidget.setItem(i,0, QTableWidgetItem(emails[i]))
            self.tableWidget.setItem(i,1, QTableWidgetItem(types[i]))

    def addAccount(self):
        dialog = AddAccountDialog(self)
        if dialog.exec_() != QDialog.Accepted: return
        email = unicode(dialog.emailEdit.text())
        passwd = unicode(dialog.passwordEdit.text())
        ac_type = unicode(dialog.typeCombo.currentText())
        self.tableWidget.insertRow(0)
        self.tableWidget.setItem(0,0, QTableWidgetItem(email))
        self.tableWidget.setItem(0,1, QTableWidgetItem(ac_type))
        self.emails.insert(0, email)
        self.types.insert(0, ac_type)
        kr = Keyring()
        kr.setPassword(email, passwd)

    def removeAccount(self):
        row = self.tableWidget.selectionModel().selectedRows()[0].row()
        email = self.tableWidget.item(row,0).text()
        kr = Keyring()
        kr.deletePassword(email)
        self.tableWidget.removeRow(row)
        self.emails.pop(row)
        self.types.pop(row)


class AddAccountDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle('Add Account')
        self.resize(400, 160)
        self.gridLayout = QGridLayout(self)
        self.typeCombo = QComboBox(self)
        self.typeCombo.addItem('Gmail')
        self.label = QLabel('Type :', self)
        self.label1 = QLabel('Email :', self)
        self.label2 = QLabel('Password :', self)
        self.emailEdit = QLineEdit(self)
        self.passwordEdit = QLineEdit(self)
        self.passwordEdit.setEchoMode(QLineEdit.Password)
        self.showPasswordBtn = QCheckBox('Show', self)
        self.cancelBtn = QPushButton('Cancel', self)
        self.saveBtn = QPushButton('Save', self)
        self.gridLayout.addWidget(self.label, 0,0,1,1)
        self.gridLayout.addWidget(self.typeCombo, 0,1,1,2)
        self.gridLayout.addWidget(self.label1, 1,0,1,1)
        self.gridLayout.addWidget(self.emailEdit, 1,1,1,3)
        self.gridLayout.addWidget(self.label2, 2,0,1,1)
        self.gridLayout.addWidget(self.passwordEdit, 2,1,1,2)
        self.gridLayout.addWidget(self.showPasswordBtn, 2,3,1,1)
        self.gridLayout.addWidget(self.cancelBtn, 3,2,1,1)
        self.gridLayout.addWidget(self.saveBtn, 3,3,1,1)
        #self.gridLayout.setRowStretch(2, 1)
        self.showPasswordBtn.clicked.connect(self.showPassword)
        self.cancelBtn.clicked.connect(self.reject)
        self.saveBtn.clicked.connect(self.accept)

    def showPassword(self, checked):
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.passwordEdit.setEchoMode(mode)
