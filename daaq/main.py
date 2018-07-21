#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import standard python modules
import os, sys
import imaplib, email

# Import PyQt modules
from PyQt4 import QtCore
from PyQt4.QtGui import ( QApplication, QMainWindow, QIcon, QTableWidgetItem, QHeaderView,
        QWidget, QLineEdit, QInputDialog, QMessageBox, QPrinter, QPrintPreviewDialog )
from PyQt4.QtXml import QDomDocument

# Import created modules
from ui_window import Ui_Window
from widgets import TextViewer, MailItem, MailInfoFrame, splitEmailAddr
import bodystructure, send_mail
from keyring import Keyring

SMTP_SERVER = {'server':'smtp.gmail.com', 'port':587}
IMAP_SERVER = {'server':'imap.gmail.com', 'port':993}

DOC_DIR = os.path.expanduser('~/Documents') + '/'
ACNT_DIR = os.path.expanduser('~/.config/daaq-mail/accounts/')


class Window(QMainWindow, Ui_Window):
    def __init__(self):
        QMainWindow.__init__(self)
        QIcon.setThemeName('Adwaita')
        self.setupUi(self)
        self.initUi()
        self.settings = QtCore.QSettings(1, 0, "daaq-mail","daaq", self)
        self.resize(1024, 714)
        self.show()
        # init variables
        self.mailbox = ''
        QtCore.QTimer.singleShot(30, self.setupClient)

    def initUi(self):
        spacer = QWidget(self)
        spacer.setSizePolicy(1|2|4,1|4)
        self.toolBar.insertWidget(self.quitAction, spacer)
        # Create text browser
        self.textViewer = TextViewer(self)
        self.verticalLayout.insertWidget(0, self.textViewer, 1)
        # mailboxTable shows list of Mailboxes
        self.mailboxTable.setFixedWidth(150)
        self.mailboxTable.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.mailboxTable.itemClicked.connect(self.onMailboxClick)
        # mailsTable is list of mails for a mailbox
        self.mailsTable.setFixedWidth(500)
        self.mailsTable.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.mailsTable.cellClicked.connect(self.loadMail)
        # Attachments table
        self.tableWidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.hide()
        # Insert Mail Info Frame
        self.mailInfoFrame = MailInfoFrame(self.widget_2)
        self.verticalLayout.insertWidget(0, self.mailInfoFrame)
        # Create actions
        self.replyAction.triggered.connect(self.replyMail)
        self.deleteAction.triggered.connect(self.deleteMail)
        self.printAction.triggered.connect(self.printMail)
        self.quitAction.triggered.connect(self.close)
        self.newMailAction.triggered.connect(self.newMail)


    def setupClient(self):
        """ Login to email server (IMAP) """
        passwords = Keyring('Daaq Mail', 'imap.gmail.com')
        self.email_id = str(self.settings.value('EmailId', '').toString())
        if self.email_id == '':
            self.email_id, ok = QInputDialog.getText(self, 'Email Address', 'Enter Email Address :')
            if not ok: return
        if passwords.hasPassword(self.email_id):
            self.passwd = passwords.getPassword(self.email_id)
        else:
            self.passwd, ok = QInputDialog.getText(self, 'Password',
                        'Enter Password for email\n'+self.email_id, QLineEdit.Password)
            if ok:
                self.settings.setValue('EmailId', self.email_id)
                passwords.setPassword(self.email_id, self.passwd)
            else:
                return
        self.imapServer = imaplib.IMAP4_SSL(IMAP_SERVER['server'], IMAP_SERVER['port']) # port is 143 for non-ssl servers
        try:
            self.imapServer.login(self.email_id, self.passwd)
            print "Logged in to %s" % self.email_id
            if not os.path.exists(ACNT_DIR + self.email_id + '/mails'):
                os.makedirs(str(ACNT_DIR + self.email_id + '/mails'))
            self.getMailboxes()
        except imaplib.IMAP4.error:
            print "Login Failed"
            sys.exit(1)

    def getMailboxes(self):
        response, mailbox_list = self.imapServer.list()
        #print mailbox_list
        if response == 'OK':
            row = 0
            for mailbox in mailbox_list:
                #print mailbox
                if 'HasChildren' in mailbox: continue
                mailbox_path = mailbox.split('"/"')[-1].replace('"', '').strip()
                mailbox_name = mailbox_path.split('/')[-1]
                #print mailbox_name
                self.mailboxTable.insertRow(row)
                item = QTableWidgetItem(mailbox_name)
                item.mailbox_path = mailbox_path
                self.mailboxTable.setItem(row, 0, item)
                row += 1
        response, total = self.imapServer.select('INBOX')
        self.mailbox = 'INBOX'
        self.total_mails = int(total[0])
        QtCore.QTimer.singleShot(30, self.getMails)

    def onMailboxClick(self, item):
        mailbox = item.mailbox_path
        if self.mailbox == mailbox : return     # Already selected
        response, total = self.imapServer.select(mailbox)
        if response == 'OK':
            print 'Selected Mailbox :', mailbox
            self.mailbox = mailbox
            self.total_mails = int(total[0])
            self.getMails()

    def getMails(self):
        """ fetch list of mails (with headers) in a mailbox """
        last_uid = None
        self.mailsTable.clear()
        self.mailsTable.setRowCount(0)
        mailbox_file = ACNT_DIR + self.email_id + '/%s.xml'%self.mailbox.replace('/', '_')
        if os.path.exists(mailbox_file):
            # load cached mails
            doc = QDomDocument()
            doc_file = QtCore.QFile(mailbox_file)
            if doc_file.open(QtCore.QIODevice.ReadOnly):
                doc.setContent(doc_file)
                doc_file.close()
            mails = doc.firstChild().toElement()
            mail = mails.firstChild()
            last_uid = mail.toElement().attribute('UID')
            i = 0
            while not mail.isNull():
                e = mail.toElement()
                self.mailsTable.insertRow(i)
                item = MailItem()
                item.setData(e.attribute('Sender'), e.attribute('Subject'), e.attribute('UID'),
                         e.attribute('Message-ID'), e.attribute('Date'), e.attribute('Cached'))
                self.mailsTable.setCellWidget(i, 0, item)
                self.mailsTable.resizeRowsToContents()
                wait(30)
                mail = mail.nextSibling()
                i += 1
            oldest_uid = mails.lastChild().toElement().attribute('UID')
        #print 'mails loaded'
        # remove deleted mails here
        last_index = 0
        if last_uid:
            ok, data = self.imapServer.search(None, '(UID %s:%s)'%(oldest_uid,last_uid)) # check if last uid is valid
            indexes = data[0].split()
            uids = []
            if len(indexes)!=0:
                last_index = int(indexes[-1])
                #print 'Last index', last_index
                oldest_index = int(indexes[0])
                ok, data = self.imapServer.fetch('%i:%i'%(oldest_index, last_index), '(UID FLAGS)')
                for each in data:
                    uids.append(each.split()[2])
            deleted = 0
            for i in range(self.mailsTable.rowCount()):
                item = self.mailsTable.cellWidget(i-deleted,0)
                if item.uid not in uids:
                    if item.cached : # delete cached files
                        msg_struct = ACNT_DIR + self.email_id + '/mails/' + item.msg_id.replace('/', '_') + '.struc'
                        msg_file = ACNT_DIR + self.email_id + '/mails/' + item.msg_id.replace('/', '_') + '.txt'
                        if os.path.exists(msg_struct) : os.remove(msg_struct)
                        if os.path.exists(msg_file) : os.remove(msg_file)
                    self.mailsTable.removeRow(i-deleted)
                    deleted += 1
                    wait(30)
        #print 'mails deleted'
        #print last_index, self.total_mails
        # check here if next index is not greater than total emails
        if last_index < self.total_mails:   # it fetches even when last_index+1 does not exist
            ok, data = self.imapServer.fetch('%i:*'%(last_index+1), '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE MESSAGE-ID)])')
            #total = len(data)/2
            # create mail itemm for each mail
            for i, mail_data in enumerate(data):
                if i%2==1 : continue    # item of odd index does not contain data
                self.mailsTable.insertRow(0)
                item = MailItem()
                item.setDataFromHeader(mail_data)
                self.mailsTable.setCellWidget(0, 0, item)
                self.mailsTable.resizeRowsToContents()
                wait(30)

    def loadMail(self, row, column):
        """ Fetch body of mail and show them in viewer widget"""
        rows = self.mailsTable.selectionModel().selectedRows()
        if len(rows)>1 : return     # return when multiple is selected
        self.mailInfoFrame.setData(self.mailsTable.cellWidget(row, column))
        msg_id = self.mailInfoFrame.msg_id
        self.textViewer.clear()
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.hide()
        wait(30)
        #ok, data = self.imapServer.fetch(self.total_mails-row, '(UID BODY.PEEK[HEADER])')
        #print data[0][1] # print header
        # Some msg_id contains / character
        msg_struct = ACNT_DIR + self.email_id + '/mails/' + msg_id.replace('/', '_') + '.struc'
        if os.path.exists(msg_struct):
            doc = QDomDocument()
            doc_file = QtCore.QFile(msg_struct)
            if doc_file.open(QtCore.QIODevice.ReadOnly):
                doc.setContent(doc_file)
                doc_file.close()
        else:
            ok, structure = self.imapServer.fetch(self.total_mails-row, '(BODYSTRUCTURE)')
            doc = bodystructure.bodystructureToXml(structure[0])
            with open(msg_struct, 'w') as fd:
                fd.write(doc.toString())
        text_part_num, enc, attachments = getAttachments(doc)
        for [part_num, filename, file_size] in attachments:
            ro = self.tableWidget.rowCount()
            self.tableWidget.insertRow(ro)
            item = QTableWidgetItem(QIcon(':/download.png'), filename)
            item.part_num = part_num
            self.tableWidget.setItem(ro, 0, item)
            self.tableWidget.setItem(ro, 1, QTableWidgetItem(file_size))
        if self.tableWidget.rowCount() > 0:
            self.tableWidget.show()
        # load html body
        msg_file = ACNT_DIR + self.email_id + '/mails/' + msg_id.replace('/', '_') + '.txt'
        if os.path.exists(msg_file):
            with open(msg_file, 'rb') as fd:
                html = fd.read()
        else:
            ok, data = self.imapServer.fetch(self.total_mails-row, '(BODY[%s])'%text_part_num)#RFC822
            msg_data = data[0][1]
            #print msg_data
            msg = email.message_from_string(msg_data)
            msg.add_header('Content-Transfer-Encoding', str(enc)) # encoding is obtained from bodystructure
            html = msg.get_payload(decode=True)
            with open(msg_file, 'wb') as fd:
                fd.write(html)
            self.mailsTable.cellWidget(row, column).cached = True
        self.textViewer.setText(unicode(html, 'utf8'))#QtCore.QString.fromUtf8(html)

    def replyMail(self):
        name, reply_to = splitEmailAddr(self.mailInfoFrame.sender)
        if reply_to == '' : reply_to = name
        dialog = send_mail.SendMailDialog(self.email_id, self.passwd, self)
        dialog.replyTo(reply_to, self.mailInfoFrame.msg_id, self.mailInfoFrame.subject)
        dialog.exec_()

    def deleteMail(self):
        rows = self.mailsTable.selectionModel().selectedRows()
        for row in rows:
            uid = self.mailsTable.cellWidget(row.row(), 0).uid
            self.imapServer.uid('STORE', uid, '+X-GM-LABELS', '\\Trash')  # For gmail only

        response, total = self.imapServer.select(self.mailbox)
        if response == 'OK':
            self.total_mails = int(total[0])
        self.getMails()


    def printMail(self):
        printer = QPrinter(mode=QPrinter.HighResolution)
        printer.setCreator("Daaq Mail")
        title = 'Daaq Mail'
        #title = validateFileName(title)
        printer.setDocName(title)
        printer.setOutputFileName(DOC_DIR + title + ".pdf")
        print_dialog = QPrintPreviewDialog(printer, self)
        print_dialog.paintRequested.connect(self.textViewer.print_)
        print_dialog.exec_()

    def newMail(self):
        dialog = send_mail.SendMailDialog(self.email_id, self.passwd, self)
        dialog.exec_()

    def saveMailInfo(self):
        # Cache mails in xml file
        doc = QDomDocument()
        root = doc.createElement('mails')
        doc.appendChild(root)
        for i in range(self.mailsTable.rowCount()):
            item = self.mailsTable.cellWidget(i,0)
            mail = doc.createElement('mail')
            mail.setAttribute('UID', item.uid)
            mail.setAttribute('Message-ID', item.msg_id)
            mail.setAttribute('Sender', item.sender)
            mail.setAttribute('Subject', unicode(item.subject).encode('utf8'))
            mail.setAttribute('Date', item.date)
            mail.setAttribute('Cached', item.cached)
            root.appendChild(mail)

        mailbox_file = ACNT_DIR + self.email_id + '/%s.xml'%self.mailbox.replace('/', '_')
        with open(mailbox_file, 'w') as doc_file:
            doc_file.write(doc.toString())

    def closeEvent(self, ev):
        self.saveMailInfo()
        self.imapServer.close()
        self.imapServer.logout()
        QMainWindow.closeEvent(self, ev)




def getAttachments(doc):
    # Get text part and attachments
    root = doc.firstChild().toElement()
    alt_part = root.elementsByTagName('alternative').item(0)
    parts = root.childNodes()
    attachments = []
    i = 0
    while i < parts.length():
        i += 1
        e = parts.item(i-1).toElement()
        if e.tagName() != 'part' : continue
        if 'text/' in e.attribute('type') and alt_part.isNull() :
            text_part_num, enc = e.attribute('PartNum'), e.attribute('encoding')
        else:
            attachments.append([e.attribute('PartNum'), e.attribute('filename'), formatFileSize(e.attribute('size'))])
    # preferably select text/html in multipart/alternative
    if not alt_part.isNull():
        part = alt_part.firstChild()
        while not part.isNull():
            e = part.toElement()
            text_part_num, enc = e.attribute('PartNum'), e.attribute('encoding')
            if e.attribute('type') == 'text/html':
                break
            part = part.nextSibling()
    return text_part_num, enc, attachments


def wait(msec):
    loop = QtCore.QEventLoop()
    QtCore.QTimer.singleShot(msec, loop.quit)
    loop.exec_()

def formatFileSize(byte):
    try:
        size = int(byte)
        if size >= 1048576:
            return '%s MB' % round(size/1048576.0, 2)
        elif size >= 1024:
            return '%s KB' % round(size/1024.0, 1)
        else:
            return '%s B' % byte
    except:
        return byte

def main():
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
