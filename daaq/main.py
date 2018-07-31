#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import standard python modules
import os, sys
import imaplib, email
from email.header import decode_header

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



DOC_DIR = os.path.expanduser('~/Documents') + '/'
ACNT_DIR = os.path.expanduser('~/.config/daaq-mail/accounts/')


class Window(QMainWindow, Ui_Window):
    loginRequested = QtCore.pyqtSignal(str, str)
    selectMailboxRequested = QtCore.pyqtSignal(str)
    uidListRequested = QtCore.pyqtSignal(str, str)
    newMailsRequested = QtCore.pyqtSignal(int)
    bodystructureRequested = QtCore.pyqtSignal(int)
    mailTextRequested = QtCore.pyqtSignal(int, str, str)
    deleteRequested = QtCore.pyqtSignal(list)
    saveAttachmentRequested = QtCore.pyqtSignal(int, str, str, unicode)
    def __init__(self):
        QMainWindow.__init__(self)
        QIcon.setThemeName('Adwaita')
        self.setupUi(self)
        self.initUi()
        self.settings = QtCore.QSettings(1, 0, "daaq-mail","daaq", self)
        self.resize(1024, 714)
        self.show()
        # create imap client
        self.thread = QtCore.QThread(self)
        self.imapClient = GmailImap()
        self.thread.finished.connect(self.imapClient.deleteLater)
        self.imapClient.moveToThread(self.thread)
        self.imapClient.loggedIn.connect(           self.onLogin)
        self.imapClient.mailboxListLoaded.connect(  self.setMailboxes)
        self.imapClient.mailboxSelected.connect(    self.onMailboxSelect)
        self.imapClient.uidsListed.connect(         self.removeDeleted)
        self.imapClient.insertMailRequested.connect(self.insertNewMail)
        self.imapClient.bodystructureLoaded.connect(self.setAttachments)
        self.imapClient.mailTextLoaded.connect(     self.setMailText)
        self.loginRequested.connect(                self.imapClient.login)
        self.selectMailboxRequested.connect(        self.imapClient.selectMailbox)
        self.uidListRequested.connect(              self.imapClient.listUids)
        self.newMailsRequested.connect(             self.imapClient.getNewMails)
        self.bodystructureRequested.connect(        self.imapClient.loadBodystructure)
        self.mailTextRequested.connect(             self.imapClient.loadMailText)
        self.saveAttachmentRequested.connect(        self.imapClient.saveAttachment)
        self.deleteRequested.connect(               self.imapClient.deleteMails)
        self.thread.start()
        # init variables
        self.email_id = ''
        self.passwd = ''
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
        self.tableWidget.cellClicked.connect(self.onAttachmentClick)
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
        email_id = str(self.settings.value('EmailId', '').toString())
        if email_id == '':
            email_id, ok = QInputDialog.getText(self, 'Email Address', 'Enter Email Address :')
            if not ok: return
        if passwords.hasPassword(email_id):
            passwd = passwords.getPassword(email_id)
        else:
            passwd, ok = QInputDialog.getText(self, 'Password',
                        'Enter Password for email\n'+email_id, QLineEdit.Password)
            if ok:
                self.settings.setValue('EmailId', email_id)
                passwords.setPassword(email_id, passwd)
            else:
                return
        print 'login requested'
        self.loginRequested.emit(email_id, passwd)

    def onLogin(self, email_id, passwd):
        self.email_id = email_id
        self.passwd = passwd
        if not os.path.exists(ACNT_DIR + email_id + '/mails'):
            os.makedirs(str(ACNT_DIR + email_id + '/mails'))

    def setMailboxes(self, mailboxes):
        #print mailboxes
        row = 0
        for mailbox in mailboxes:
            #print mailbox
            mailbox_name = mailbox.split('/')[-1]
            #print mailbox_name
            self.mailboxTable.insertRow(row)
            item = QTableWidgetItem(mailbox_name)
            item.mailbox_path = mailbox
            self.mailboxTable.setItem(row, 0, item)
            row += 1

    def onMailboxClick(self, item):
        mailbox = item.mailbox_path
        if self.mailbox == mailbox : return     # Already selected
        self.selectMailboxRequested.emit(mailbox)

    def onMailboxSelect(self, mailbox, total_mails):
        if self.mailbox != '' : self.saveMailInfo()
        self.mailbox = mailbox
        self.total_mails = total_mails
        self.clearMailViewer()
        self.mailsTable.clear()
        self.mailsTable.setRowCount(0)
        QtCore.QTimer.singleShot(30, self.loadCachedMails)

    def loadCachedMails(self):
        """ fetch list of mails (with headers) in a mailbox """
        oldest_uid, latest_uid = None, None
        mailbox_file = ACNT_DIR + self.email_id + '/%s.xml'%self.mailbox[:].replace('/', '_')
        if os.path.exists(mailbox_file):
            # load cached mails
            doc = QDomDocument()
            doc_file = QtCore.QFile(mailbox_file)
            if doc_file.open(QtCore.QIODevice.ReadOnly):
                doc.setContent(doc_file)
                doc_file.close()
            mails = doc.firstChild().toElement()
            mail = mails.firstChild()
            latest_uid = mail.toElement().attribute('UID')
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
        print 'uids', oldest_uid, latest_uid
        if latest_uid:
            self.uidListRequested.emit(oldest_uid, latest_uid)
        else:
            self.newMailsRequested.emit(0)

    def removeDeleted(self, uids, last_index):
        print 'removing deleted mails'
        deleted = 0
        for i in range(self.mailsTable.rowCount()):
            item = self.mailsTable.cellWidget(i-deleted,0)
            if item.uid not in uids:
                if item.cached : # delete cached files
                    msg_struct = ACNT_DIR + self.email_id + '/mails/' + item.msg_id[:].replace('/', '_') + '.xml'
                    msg_file = ACNT_DIR + self.email_id + '/mails/' + item.msg_id[:].replace('/', '_') + '.txt'
                    if os.path.exists(msg_struct) : os.remove(msg_struct)
                    if os.path.exists(msg_file) : os.remove(msg_file)
                self.mailsTable.removeRow(i-deleted)
                deleted += 1
                wait(30)
        self.newMailsRequested.emit(last_index)
        #print 'mails deleted'

    def insertNewMail(self, sender, subject, uid, msg_id, date, cached, seen):
        #print 'insert new mail', uid
        self.mailsTable.insertRow(0)
        item = MailItem()
        item.setData(sender, subject, uid, msg_id, date, cached, seen)
        self.mailsTable.setCellWidget(0, 0, item)
        self.mailsTable.resizeRowsToContents()
        wait(30)

    def loadMail(self, row, column):
        """ Fetch body of mail and show them in viewer widget"""
        rows = self.mailsTable.selectionModel().selectedRows()
        if len(rows)>1 : return     # return when multiple is selected
        self.clearMailViewer()
        self.mailInfoFrame.setData(self.mailsTable.cellWidget(row, column))
        wait(30)
        msg_id = self.mailInfoFrame.msg_id[:].replace('/', '_')
        # Some msg_id contains / character
        msg_struct = ACNT_DIR + self.email_id + '/mails/' + msg_id + '.xml'
        if os.path.exists(msg_struct):
            with open(msg_struct, 'r') as doc_file:
                xml_doc = doc_file.read()
            self.setAttachments(xml_doc)
        else:
            self.bodystructureRequested.emit(self.total_mails-row)

    def setAttachments(self, xml_doc): # bodystructure dom
        msg_id = self.mailInfoFrame.msg_id[:].replace('/', '_')
        # save bodystructure
        msg_struct = ACNT_DIR + self.email_id + '/mails/' + msg_id + '.xml'
        if not os.path.exists(msg_struct):
            with open(msg_struct, 'w') as fd:
                fd.write(unicode(xml_doc))
        # get attachments
        text_part_num, txt_enc, attachments = getAttachments(xml_doc)
        for [part_num, enc, filename, file_size] in attachments:
            ro = self.tableWidget.rowCount()
            self.tableWidget.insertRow(ro)
            item = QTableWidgetItem(QIcon(':/download.png'), filename)
            item.part_num = part_num
            item.encoding = enc
            self.tableWidget.setItem(ro, 0, item)
            self.tableWidget.setItem(ro, 1, QTableWidgetItem(file_size))
        if self.tableWidget.rowCount() > 0:
            self.tableWidget.show()
        # load html body
        msg_file = ACNT_DIR + self.email_id + '/mails/' + msg_id + '.txt'
        if os.path.exists(msg_file):
            with open(msg_file, 'rb') as fd:
                html = fd.read()
            self.setMailText(unicode(html, 'utf8')) # convert byte string to unicode
        else:
            row = self.mailsTable.selectionModel().selectedRows()[0].row()
            self.mailTextRequested.emit(self.total_mails-row, text_part_num, txt_enc)
            self.mailsTable.cellWidget(row, 0).cached = True

    def setMailText(self, html):
        msg_id = self.mailInfoFrame.msg_id[:].replace('/', '_')
        msg_file = ACNT_DIR + self.email_id + '/mails/' + msg_id + '.txt'
        if not os.path.exists(msg_file):
            with open(msg_file, 'wb') as fd:
                fd.write(unicode(html).encode('utf8')) # save text file in byte string
        self.textViewer.setText(html)

    def onAttachmentClick(self, row, col):
        if col != 0 : return
        part_num = self.tableWidget.item(row, col).part_num
        enc = self.tableWidget.item(row, col).encoding
        filename = self.tableWidget.item(row, col).text()
        msg_row = self.mailsTable.selectionModel().selectedRows()[0].row()
        self.saveAttachmentRequested.emit(self.total_mails-msg_row, part_num, enc, filename)

    def replyMail(self):
        name, reply_to = splitEmailAddr(self.mailInfoFrame.sender)
        if reply_to == '' : reply_to = name
        dialog = send_mail.SendMailDialog(self.email_id, self.passwd, self)
        dialog.replyTo(reply_to, self.mailInfoFrame.msg_id, self.mailInfoFrame.subject)
        dialog.exec_()

    def deleteMail(self):
        rows = self.mailsTable.selectionModel().selectedRows()
        uid_list = [self.mailsTable.cellWidget(row.row(), 0).uid for row in rows]
        self.deleteRequested.emit(uid_list)

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

    def clearMailViewer(self):
        self.mailInfoFrame.clear()
        self.textViewer.clear()
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.hide()

    def saveMailInfo(self):
        if self.total_mails != self.mailsTable.rowCount(): return
        if self.total_mails == 0 : return
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

        mailbox_file = ACNT_DIR + self.email_id + '/%s.xml'%self.mailbox[:].replace('/', '_')
        with open(mailbox_file, 'w') as doc_file:
            doc_file.write(doc.toString())

    def closeEvent(self, ev):
        self.saveMailInfo()
        loop = QtCore.QEventLoop()
        self.thread.finished.connect(loop.quit)
        self.thread.quit()
        loop.exec_()
        QMainWindow.closeEvent(self, ev)


class GmailImap(QtCore.QObject):
    loggedIn = QtCore.pyqtSignal(str, str)
    mailboxListLoaded = QtCore.pyqtSignal(list)
    mailboxSelected = QtCore.pyqtSignal(str, int)
    uidsListed = QtCore.pyqtSignal(list, int)
    insertMailRequested = QtCore.pyqtSignal(unicode, unicode, str, str, str, bool, bool)
    bodystructureLoaded = QtCore.pyqtSignal(unicode)
    mailTextLoaded = QtCore.pyqtSignal(unicode)
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.conn = None
        self.email_id, self.passwd = '', ''
        self.mailbox = ''
        self.total_mails = 0

    def login(self, email_id, passwd):
        print 'try login'
        try:
            self.conn = imaplib.IMAP4_SSL('imap.gmail.com', 993)
            self.conn.login(email_id, passwd)
            self.email_id = email_id
            self.passwd = passwd
            self.loggedIn.emit(email_id, passwd)
            print 'logged in as', email_id
            self.getMailboxes()
            self.selectMailbox('INBOX')
        except:
            print "Login Failed"

    def getMailboxes(self):
        print 'get mailboxes'
        status, mailbox_list = self.conn.list()
        if status != 'OK': return
        mailboxes = []
        for mailbox in mailbox_list:
            if 'HasChildren' in mailbox: continue
            mailbox_path = mailbox.split('"/"')[-1].replace('"', '').strip()
            mailboxes.append(mailbox_path)
        self.mailboxListLoaded.emit(mailboxes)

    def selectMailbox(self, mailbox):
        print 'mailbox selected :', mailbox
        status, total = self.conn.select(str(mailbox))
        if status == 'OK':
            self.mailbox = mailbox
            self.total_mails = int(total[0])
            self.mailboxSelected.emit(mailbox, self.total_mails)

    def listUids(self, oldest_uid, latest_uid):
        print 'list uids from', oldest_uid, 'to', latest_uid
        # remove deleted mails here
        if not latest_uid: return
        status, data = self.conn.search(None, '(UID %s:%s)'%(oldest_uid,latest_uid)) # check if last uid is valid
        indexes = data[0].split()
        last_index = 0
        uids = []
        if len(indexes)!=0:
            last_index = int(indexes[-1])
            #print 'Last index', last_index
            oldest_index = int(indexes[0])
            status, data = self.conn.fetch('%i:%i'%(oldest_index, last_index), '(UID FLAGS)')
            for each in data:
                uids.append(each.split()[2])
        self.uidsListed.emit(uids, last_index)

    def getNewMails(self, last_index):
        print 'get new mails'
        if last_index >= self.total_mails: return # return when last_index+1 does not exist
        status, mail_data = self.conn.fetch('%i:*'%(last_index+1),
                      '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE MESSAGE-ID)])')
        #total = len(data)/2
        # create mail itemm for each mail
        for i, data in enumerate(mail_data):
            if i%2==1 : continue    # item of odd index does not contain data
            # data[0][0] contains flags, uid and data[0][1] contains header
            header = email.message_from_string(data[1])
            sender, enc = decode_header(header['from'])[0]
            subject, enc = decode_header(header['subject'])[0]
            if enc:
                subject = subject.decode(enc)
            subject = subject.split('\n')[0]
            uid = data[0].split()[2]    # Have to use regex later
            msg_id = header['message-id']
            date = header['date']
            cached = False
            seen = True if '\Seen' in data[0] else False
            self.insertMailRequested.emit(sender, subject, uid, msg_id, date, cached, seen)

    def loadBodystructure(self, index):
        status, structure = self.conn.fetch(index, '(BODYSTRUCTURE)')
        doc = bodystructure.bodystructureToXml(structure[0])
        #print structure[0]
        self.bodystructureLoaded.emit(doc.toString())

    def loadMailText(self, index, text_part_num, enc):
        #status, data = self.conn.fetch(index, '(UID BODY.PEEK[HEADER])')
        #print data[0][1] # print header
        status, data = self.conn.fetch(index, '(BODY[%s])'%text_part_num)#RFC822
        msg_data = data[0][1]
        #print msg_data
        msg = email.message_from_string(msg_data)
        msg.add_header('Content-Transfer-Encoding', str(enc)) # encoding is obtained from bodystructure
        html = msg.get_payload(decode=True)
        self.mailTextLoaded.emit(unicode(html, 'utf8'))

    def saveAttachment(self, msg_num, part_num, enc, filename):
        #print 'saving attachment', msg_num, part_num, enc
        status, data = self.conn.fetch(msg_num, '(BODY[%s])'%part_num)
        msg = email.message_from_string(data[0][1])
        msg.add_header('Content-Transfer-Encoding', str(enc))
        attach = msg.get_payload(decode=True)
        filename = os.path.expanduser('~/Downloads')+ '/' + filename 
        with open(filename, 'wb') as fd:
            fd.write(attach)

    def deleteMails(self, uids):
        for uid in uids:
            self.conn.uid('STORE', uid, '+X-GM-LABELS', '\\Trash')
        self.selectMailbox(self.mailbox)

    def keepAlive(self):
        pass

    def close(self):
        # TODO : use this to logout when closing window
        self.conn.close()

def getAttachments(xml_doc):
    # Get text part and attachments
    doc = QDomDocument()
    doc.setContent(xml_doc)
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
            attachments.append([e.attribute('PartNum'), e.attribute('encoding'),
                            e.attribute('filename'), formatFileSize(e.attribute('size'))])
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
