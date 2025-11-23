# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QLabel, QListWidget, QListWidgetItem, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(980, 712)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.leftColumn = QVBoxLayout()
        self.leftColumn.setObjectName(u"leftColumn")
        self.srcCode_lbl = QLabel(self.centralwidget)
        self.srcCode_lbl.setObjectName(u"srcCode_lbl")

        self.leftColumn.addWidget(self.srcCode_lbl)

        self.srcCode = QTextEdit(self.centralwidget)
        self.srcCode.setObjectName(u"srcCode")
        font = QFont()
        font.setFamilies([u"Consolas"])
        self.srcCode.setFont(font)

        self.leftColumn.addWidget(self.srcCode)

        self.codeTable_lbl = QLabel(self.centralwidget)
        self.codeTable_lbl.setObjectName(u"codeTable_lbl")

        self.leftColumn.addWidget(self.codeTable_lbl)

        self.codeTable = QTableWidget(self.centralwidget)
        if (self.codeTable.columnCount() < 3):
            self.codeTable.setColumnCount(3)
        if (self.codeTable.rowCount() < 9):
            self.codeTable.setRowCount(9)
        __qtablewidgetitem = QTableWidgetItem()
        self.codeTable.setItem(0, 0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.codeTable.setItem(0, 1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.codeTable.setItem(0, 2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.codeTable.setItem(1, 0, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.codeTable.setItem(1, 1, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.codeTable.setItem(1, 2, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.codeTable.setItem(2, 0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.codeTable.setItem(2, 1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.codeTable.setItem(2, 2, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.codeTable.setItem(3, 0, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.codeTable.setItem(3, 1, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.codeTable.setItem(3, 2, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.codeTable.setItem(4, 0, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.codeTable.setItem(4, 1, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.codeTable.setItem(4, 2, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.codeTable.setItem(5, 0, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.codeTable.setItem(5, 1, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.codeTable.setItem(5, 2, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.codeTable.setItem(6, 0, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.codeTable.setItem(6, 1, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.codeTable.setItem(6, 2, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.codeTable.setItem(7, 0, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.codeTable.setItem(7, 1, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.codeTable.setItem(7, 2, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        self.codeTable.setItem(8, 0, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        self.codeTable.setItem(8, 1, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        self.codeTable.setItem(8, 2, __qtablewidgetitem26)
        self.codeTable.setObjectName(u"codeTable")
        self.codeTable.viewport().setProperty(u"cursor", QCursor(Qt.CursorShape.CrossCursor))
        self.codeTable.setProperty(u"showDropIndicator", True)
        self.codeTable.setRowCount(9)
        self.codeTable.setColumnCount(3)

        self.leftColumn.addWidget(self.codeTable)


        self.horizontalLayout.addLayout(self.leftColumn)

        self.middleColumn = QVBoxLayout()
        self.middleColumn.setObjectName(u"middleColumn")
        self.helpTable_lbl = QLabel(self.centralwidget)
        self.helpTable_lbl.setObjectName(u"helpTable_lbl")

        self.middleColumn.addWidget(self.helpTable_lbl)

        self.helpTable = QTableWidget(self.centralwidget)
        self.helpTable.setObjectName(u"helpTable")
        self.helpTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.middleColumn.addWidget(self.helpTable)

        self.symbolicNameTable_lbl = QLabel(self.centralwidget)
        self.symbolicNameTable_lbl.setObjectName(u"symbolicNameTable_lbl")

        self.middleColumn.addWidget(self.symbolicNameTable_lbl)

        self.symbolicNameTable = QTableWidget(self.centralwidget)
        self.symbolicNameTable.setObjectName(u"symbolicNameTable")
        self.symbolicNameTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.middleColumn.addWidget(self.symbolicNameTable)

        self.firstPassErr_lbl = QLabel(self.centralwidget)
        self.firstPassErr_lbl.setObjectName(u"firstPassErr_lbl")

        self.middleColumn.addWidget(self.firstPassErr_lbl)

        self.firstPassErr = QListWidget(self.centralwidget)
        self.firstPassErr.setObjectName(u"firstPassErr")

        self.middleColumn.addWidget(self.firstPassErr)

        self.clearFirst = QPushButton(self.centralwidget)
        self.clearFirst.setObjectName(u"clearFirst")

        self.middleColumn.addWidget(self.clearFirst)


        self.horizontalLayout.addLayout(self.middleColumn)

        self.rightColumn = QVBoxLayout()
        self.rightColumn.setObjectName(u"rightColumn")
        self.binaryCode_lbl = QLabel(self.centralwidget)
        self.binaryCode_lbl.setObjectName(u"binaryCode_lbl")

        self.rightColumn.addWidget(self.binaryCode_lbl)

        self.binaryCode = QListWidget(self.centralwidget)
        self.binaryCode.setObjectName(u"binaryCode")

        self.rightColumn.addWidget(self.binaryCode)

        self.secondPassErr_lbl = QLabel(self.centralwidget)
        self.secondPassErr_lbl.setObjectName(u"secondPassErr_lbl")

        self.rightColumn.addWidget(self.secondPassErr_lbl)

        self.secondPassErr = QListWidget(self.centralwidget)
        self.secondPassErr.setObjectName(u"secondPassErr")

        self.rightColumn.addWidget(self.secondPassErr)

        self.clearSecond = QPushButton(self.centralwidget)
        self.clearSecond.setObjectName(u"clearSecond")

        self.rightColumn.addWidget(self.clearSecond)


        self.horizontalLayout.addLayout(self.rightColumn)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")

        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.firstPass = QPushButton(self.centralwidget)
        self.firstPass.setObjectName(u"firstPass")

        self.horizontalLayout_2.addWidget(self.firstPass)

        self.secondPass = QPushButton(self.centralwidget)
        self.secondPass.setObjectName(u"secondPass")

        self.horizontalLayout_2.addWidget(self.secondPass)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 980, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.srcCode_lbl.setText(QCoreApplication.translate("MainWindow", u"\u0418\u0441\u0445\u043e\u0434\u043d\u044b\u0439 \u0442\u0435\u043a\u0441\u0442", None))
        self.codeTable_lbl.setText(QCoreApplication.translate("MainWindow", u"\u0422\u0430\u0431\u043b\u0438\u0446\u0430 \u043a\u043e\u0434\u043e\u0432 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0439", None))

        __sortingEnabled = self.codeTable.isSortingEnabled()
        self.codeTable.setSortingEnabled(False)
        ___qtablewidgetitem = self.codeTable.item(0, 0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"LOAD", None));
        ___qtablewidgetitem1 = self.codeTable.item(0, 1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"1", None));
        ___qtablewidgetitem2 = self.codeTable.item(0, 2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"2", None));
        ___qtablewidgetitem3 = self.codeTable.item(1, 0)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"LOADI", None));
        ___qtablewidgetitem4 = self.codeTable.item(1, 1)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"2", None));
        ___qtablewidgetitem5 = self.codeTable.item(1, 2)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"4", None));
        ___qtablewidgetitem6 = self.codeTable.item(2, 0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"STORE", None));
        ___qtablewidgetitem7 = self.codeTable.item(2, 1)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"3", None));
        ___qtablewidgetitem8 = self.codeTable.item(2, 2)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"4", None));
        ___qtablewidgetitem9 = self.codeTable.item(3, 0)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"ADD", None));
        ___qtablewidgetitem10 = self.codeTable.item(3, 1)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"4", None));
        ___qtablewidgetitem11 = self.codeTable.item(3, 2)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"2", None));
        ___qtablewidgetitem12 = self.codeTable.item(4, 0)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"SUB", None));
        ___qtablewidgetitem13 = self.codeTable.item(4, 1)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"5", None));
        ___qtablewidgetitem14 = self.codeTable.item(4, 2)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"2", None));
        ___qtablewidgetitem15 = self.codeTable.item(5, 0)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainWindow", u"JMP", None));
        ___qtablewidgetitem16 = self.codeTable.item(5, 1)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainWindow", u"6", None));
        ___qtablewidgetitem17 = self.codeTable.item(5, 2)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MainWindow", u"4", None));
        ___qtablewidgetitem18 = self.codeTable.item(6, 0)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("MainWindow", u"JZ", None));
        ___qtablewidgetitem19 = self.codeTable.item(6, 1)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("MainWindow", u"7", None));
        ___qtablewidgetitem20 = self.codeTable.item(6, 2)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("MainWindow", u"4", None));
        ___qtablewidgetitem21 = self.codeTable.item(7, 0)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("MainWindow", u"HALT", None));
        ___qtablewidgetitem22 = self.codeTable.item(7, 1)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("MainWindow", u"8", None));
        ___qtablewidgetitem23 = self.codeTable.item(7, 2)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("MainWindow", u"1", None));
        ___qtablewidgetitem24 = self.codeTable.item(8, 0)
        ___qtablewidgetitem24.setText(QCoreApplication.translate("MainWindow", u"NOP", None));
        ___qtablewidgetitem25 = self.codeTable.item(8, 1)
        ___qtablewidgetitem25.setText(QCoreApplication.translate("MainWindow", u"9", None));
        ___qtablewidgetitem26 = self.codeTable.item(8, 2)
        ___qtablewidgetitem26.setText(QCoreApplication.translate("MainWindow", u"1", None));
        self.codeTable.setSortingEnabled(__sortingEnabled)

        self.helpTable_lbl.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0441\u043f\u043e\u043c\u043e\u0433\u0430\u0442\u0435\u043b\u044c\u043d\u0430\u044f \u0442\u0430\u0431\u043b\u0438\u0446\u0430", None))
        self.symbolicNameTable_lbl.setText(QCoreApplication.translate("MainWindow", u"\u0422\u0430\u0431\u043b\u0438\u0446\u0430 \u0441\u0438\u043c\u0432\u043e\u043b\u0438\u0447\u0435\u0441\u043a\u0438\u0445 \u0438\u043c\u0435\u043d", None))
        self.firstPassErr_lbl.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0448\u0438\u0431\u043a\u0438 \u043f\u0435\u0440\u0432\u043e\u0433\u043e \u043f\u0440\u043e\u0445\u043e\u0434\u0430", None))
        self.clearFirst.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0447\u0438\u0441\u0442\u043a\u0430 \u043e\u0448\u0438\u0431\u043e\u043a \u043f\u0435\u0440\u0432\u043e\u0433\u043e \u043f\u0440\u043e\u0445\u043e\u0434\u0430", None))
        self.binaryCode_lbl.setText(QCoreApplication.translate("MainWindow", u"\u0414\u0432\u043e\u0438\u0447\u043d\u044b\u0439 \u043a\u043e\u0434", None))
        self.secondPassErr_lbl.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0448\u0438\u0431\u043a\u0438 \u0432\u0442\u043e\u0440\u043e\u0433\u043e \u043f\u0440\u043e\u0445\u043e\u0434\u0430", None))
        self.clearSecond.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0447\u0438\u0441\u0442\u043a\u0430 \u043e\u0448\u0438\u0431\u043e\u043a \u0432\u0442\u043e\u0440\u043e\u0433\u043e \u043f\u0440\u043e\u0445\u043e\u0434\u0430", None))
        self.firstPass.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0435\u0440\u0432\u044b\u0439 \u043f\u0440\u043e\u0445\u043e\u0434", None))
        self.secondPass.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0442\u043e\u0440\u043e\u0439 \u043f\u0440\u043e\u0445\u043e\u0434", None))
    # retranslateUi

