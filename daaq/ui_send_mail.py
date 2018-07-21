# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'files/send-mail-dialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SendMailDialog(object):
    def setupUi(self, SendMailDialog):
        SendMailDialog.setObjectName(_fromUtf8("SendMailDialog"))
        SendMailDialog.resize(480, 600)
        self.gridLayout = QtGui.QGridLayout(SendMailDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(SendMailDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.recipientEdit = QtGui.QLineEdit(SendMailDialog)
        self.recipientEdit.setObjectName(_fromUtf8("recipientEdit"))
        self.gridLayout.addWidget(self.recipientEdit, 0, 1, 1, 1)
        self.label = QtGui.QLabel(SendMailDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.subjectEdit = QtGui.QLineEdit(SendMailDialog)
        self.subjectEdit.setObjectName(_fromUtf8("subjectEdit"))
        self.gridLayout.addWidget(self.subjectEdit, 1, 1, 1, 1)
        self.widget = QtGui.QWidget(SendMailDialog)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.attachFileButton = QtGui.QPushButton(self.widget)
        self.attachFileButton.setObjectName(_fromUtf8("attachFileButton"))
        self.horizontalLayout.addWidget(self.attachFileButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QtGui.QPushButton(self.widget)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)
        self.sendButton = QtGui.QPushButton(self.widget)
        self.sendButton.setObjectName(_fromUtf8("sendButton"))
        self.horizontalLayout.addWidget(self.sendButton)
        self.gridLayout.addWidget(self.widget, 4, 0, 1, 2)
        self.mailText = QtGui.QTextEdit(SendMailDialog)
        self.mailText.setObjectName(_fromUtf8("mailText"))
        self.gridLayout.addWidget(self.mailText, 2, 0, 1, 2)
        self.tableWidget = QtGui.QTableWidget(SendMailDialog)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tableWidget, 3, 0, 1, 2)
        self.gridLayout.setRowStretch(2, 1)

        self.retranslateUi(SendMailDialog)
        QtCore.QMetaObject.connectSlotsByName(SendMailDialog)

    def retranslateUi(self, SendMailDialog):
        SendMailDialog.setWindowTitle(_translate("SendMailDialog", "Send Mail", None))
        self.label_2.setText(_translate("SendMailDialog", "Subject :", None))
        self.label.setText(_translate("SendMailDialog", "Send To :", None))
        self.attachFileButton.setText(_translate("SendMailDialog", "Attach", None))
        self.cancelButton.setText(_translate("SendMailDialog", "Cancel", None))
        self.sendButton.setText(_translate("SendMailDialog", "Send", None))

