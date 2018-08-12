# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'files/window.ui'
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

class Ui_Window(object):
    def setupUi(self, Window):
        Window.setObjectName(_fromUtf8("Window"))
        Window.resize(651, 555)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/mail.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Window.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(Window)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.docLayout = QtGui.QHBoxLayout(self.widget)
        self.docLayout.setContentsMargins(6, 4, 4, 2)
        self.docLayout.setSpacing(2)
        self.docLayout.setObjectName(_fromUtf8("docLayout"))
        self.mailboxTable = QtGui.QTableWidget(self.widget)
        self.mailboxTable.setAlternatingRowColors(True)
        self.mailboxTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.mailboxTable.setColumnCount(1)
        self.mailboxTable.setObjectName(_fromUtf8("mailboxTable"))
        self.mailboxTable.setRowCount(0)
        self.mailboxTable.horizontalHeader().setVisible(False)
        self.mailboxTable.verticalHeader().setVisible(False)
        self.docLayout.addWidget(self.mailboxTable)
        self.mailsTable = QtGui.QTableWidget(self.widget)
        self.mailsTable.setColumnCount(1)
        self.mailsTable.setObjectName(_fromUtf8("mailsTable"))
        self.mailsTable.setRowCount(0)
        self.mailsTable.horizontalHeader().setVisible(False)
        self.mailsTable.verticalHeader().setVisible(False)
        self.docLayout.addWidget(self.mailsTable)
        self.horizontalLayout.addWidget(self.widget)
        self.widget_2 = QtGui.QWidget(self.centralwidget)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget_2)
        self.verticalLayout.setContentsMargins(0, 0, 9, 0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tableWidget = QtGui.QTableWidget(self.widget_2)
        self.tableWidget.setMaximumSize(QtCore.QSize(16777215, 100))
        self.tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tableWidget)
        self.horizontalLayout.addWidget(self.widget_2)
        Window.setCentralWidget(self.centralwidget)
        self.statusBar = QtGui.QStatusBar(Window)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        Window.setStatusBar(self.statusBar)
        self.toolBar = QtGui.QToolBar(Window)
        self.toolBar.setMovable(False)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        Window.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.newMailAction = QtGui.QAction(Window)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/write-mail.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.newMailAction.setIcon(icon1)
        self.newMailAction.setObjectName(_fromUtf8("newMailAction"))
        self.printAction = QtGui.QAction(Window)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-print"))
        self.printAction.setIcon(icon)
        self.printAction.setObjectName(_fromUtf8("printAction"))
        self.deleteAction = QtGui.QAction(Window)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("edit-delete"))
        self.deleteAction.setIcon(icon)
        self.deleteAction.setObjectName(_fromUtf8("deleteAction"))
        self.replyAction = QtGui.QAction(Window)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("mail-reply-sender"))
        self.replyAction.setIcon(icon)
        self.replyAction.setObjectName(_fromUtf8("replyAction"))
        self.quitAction = QtGui.QAction(Window)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/quit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.quitAction.setIcon(icon2)
        self.quitAction.setObjectName(_fromUtf8("quitAction"))
        self.toolBar.addAction(self.newMailAction)
        self.toolBar.addAction(self.printAction)
        self.toolBar.addAction(self.deleteAction)
        self.toolBar.addAction(self.replyAction)
        self.toolBar.addAction(self.quitAction)

        self.retranslateUi(Window)
        QtCore.QMetaObject.connectSlotsByName(Window)

    def retranslateUi(self, Window):
        Window.setWindowTitle(_translate("Window", "Daaq Mail", None))
        self.newMailAction.setText(_translate("Window", "Compose New", None))
        self.newMailAction.setToolTip(_translate("Window", "Write a new Mail", None))
        self.newMailAction.setShortcut(_translate("Window", "Ctrl+N", None))
        self.printAction.setText(_translate("Window", "Print", None))
        self.printAction.setToolTip(_translate("Window", "Print Mail", None))
        self.printAction.setShortcut(_translate("Window", "Ctrl+P", None))
        self.deleteAction.setText(_translate("Window", "Delete", None))
        self.deleteAction.setToolTip(_translate("Window", "Delete Mail", None))
        self.replyAction.setText(_translate("Window", "Reply", None))
        self.replyAction.setToolTip(_translate("Window", "Reply Mail", None))
        self.quitAction.setText(_translate("Window", "Quit", None))
        self.quitAction.setToolTip(_translate("Window", "Quit Program", None))
        self.quitAction.setShortcut(_translate("Window", "Ctrl+Q", None))

import resources_rc
