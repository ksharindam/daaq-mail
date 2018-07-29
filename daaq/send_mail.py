
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog, QFileDialog, QMessageBox, QHeaderView, QTableWidgetItem
from ui_send_mail import Ui_SendMailDialog

import os, email, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

GMAIL = {'server':'smtp.gmail.com', 'port':587}


class SendMailDialog(QDialog, Ui_SendMailDialog):
    def __init__(self, email_id, passwd, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.tableWidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.setHidden(True)
        self.tableWidget.cellClicked.connect(self.onAttachmentClick)
        self.attachFileButton.clicked.connect(self.addAttachment)
        self.sendButton.clicked.connect(self.sendMail)
        self.cancelButton.clicked.connect(self.reject)
        self.email_id = email_id
        self.passwd = passwd
        self.attachments = []
        self.reply_to = False

    def replyTo(self, reply_to, msg_id, subject):
        self.reply_to = reply_to
        self.reference_msg = msg_id
        self.recipientEdit.setText(reply_to)
        if subject[:4].lower() not in ['re: ', 're :'] : subject = 'Re: ' + subject
        self.subjectEdit.setText(subject)

    def attachFile(self, filename):
        # check if filename exists and it is not directory
        # check if filesize exceeds 25MB
        filename = unicode(filename)
        if filename not in self.attachments:
            self.attachments.append(filename)
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(os.path.basename(filename)))
            self.tableWidget.setItem(row, 1, QTableWidgetItem('Remove'))
        self.tableWidget.setHidden(False)

    def onAttachmentClick(self, row, col):
        ''' remove attachment if remove is clicked '''
        if col == 1:
            self.tableWidget.removeRow(row)
            self.attachments.pop(row)

    def addAttachment(self):
        # Open a file dialog a add files
        filefilters = 'All Files (*);;Image Files (*.jpg *jpeg *.png);;Document Files (*.pdf *.docx *.odt)'
        filenames = QFileDialog.getOpenFileNames(self, 'Attach Files', '', filefilters)
        for each in filenames:
            self.attachFile(each)

    def sendMail(self):
        # Check if sender is empty or invalid
        # Check if msg text and attachments both are empty
        sendServer = smtplib.SMTP(GMAIL['server'], GMAIL['port'])
        try:
            sendServer.ehlo()
            sendServer.starttls()
            sendServer.ehlo()
            sendServer.login(self.email_id, self.passwd)
            print("Login Successful")
        except smtplib.SMTPException:
            QMessageBox.warning(self, "Login Failed !", "Failed to Login to Mail Server")
            return

        msg = MIMEMultipart()
        # Email Info
        msg['Subject'] = unicode(self.subjectEdit.text())
        msg['To'] =    unicode(self.recipientEdit.text())
        msg['From'] = self.email_id
        if self.reply_to:
            msg['In-Reply-To'] = self.reference_msg
            msg['References'] = self.reference_msg
        # Attach text and images
        textPart = MIMEText(unicode(self.mailText.toHtml()), 'html')
        msg.attach(textPart)
        # Attach files
        for filename in self.attachments:
            attachment = MIMEBase('application','octet-stream')
            with open(filename, 'rb') as fd:
                data = fd.read()
            attachment.set_payload(data)
            email.encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(filename))
            msg.attach(attachment)

        sendServer.sendmail(self.email_id, [unicode(self.recipientEdit.text())], msg.as_string())
        sendServer.quit()
        # Show success/failure msg here
        self.accept()

