# -*- coding: utf-8 -*-

# QtCore se usa para coordenadas, tamaños y traducción de textos.
# QtWidgets se usa para crear botones, ventanas, cajas de texto y demás elementos visuales.
from PyQt5 import QtCore, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        """
        Define la estructura visual de la ventana principal.

        Este archivo contiene el diseño:
        - botones
        - caja de texto
        - estilos
        - posiciones
        - tamaño de ventana

        La lógica de los botones no está aquí; está en main.py.
        """

        # Nombre interno de la ventana.
        MainWindow.setObjectName("MainWindow")

        # Tamaño general de la ventana.
        MainWindow.resize(900, 650)

        # Estilo base: fondo oscuro y texto blanco.
        MainWindow.setStyleSheet(
            "background-color: #2b2b2b;\n"
            "color: white;"
        )

        # Widget central donde se colocan todos los elementos.
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Estilo general para los botones.
        # Se usa el mismo estilo en todos para que la interfaz se vea uniforme.
        button_style = """
        QPushButton {
            background-color: #4a4a4a;
            color: white;
            border: 1px solid #222222;
            border-radius: 8px;
            font: 12pt "Helvetica";
            padding: 6px;
        }
        QPushButton:hover {
            background-color: #5a5a5a;
        }
        """

        # Estilo de la caja donde el usuario escribe el mensaje.
        input_style = """
        QPlainTextEdit {
            border: 2px solid #3498db;
            border-radius: 6px;
            background-color: #1e1e1e;
            color: white;
            padding: 5px;
            font: 11pt "Helvetica";
        }
        """

        # Estilo de un cuadro informativo.
        # En la versión final main.py lo oculta, pero se dejó como parte del diseño.
        info_style = """
        QTextBrowser {
            border: 2px solid #3498db;
            border-radius: 6px;
            background-color: #1e1e1e;
            color: white;
            padding: 5px;
            font: 10pt "Helvetica";
        }
        """

        # Botón Logo.
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(70, 150, 140, 42))
        self.pushButton.setStyleSheet(button_style)
        self.pushButton.setObjectName("pushButton")

        # Botón Tec.
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(70, 205, 140, 42))
        self.pushButton_2.setStyleSheet(button_style)
        self.pushButton_2.setObjectName("pushButton_2")

        # Botón 3 Tec.
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(70, 260, 140, 42))
        self.pushButton_3.setStyleSheet(button_style)
        self.pushButton_3.setObjectName("pushButton_3")

        # Botón Nombres.
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(70, 315, 140, 42))
        self.pushButton_4.setStyleSheet(button_style)
        self.pushButton_4.setObjectName("pushButton_4")

        # Caja de texto para escribir un mensaje personalizado.
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(260, 120, 340, 70))
        self.plainTextEdit.setStyleSheet(input_style)
        self.plainTextEdit.setObjectName("plainTextEdit")

        # Botón Enviar Mensaje.
        # Es más ancho porque el texto es más largo que el de los otros botones.
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(260, 210, 180, 42))
        self.pushButton_5.setStyleSheet(button_style)
        self.pushButton_5.setObjectName("pushButton_5")

        # Cuadro de información del equipo.
        # Se conserva, pero main.py lo oculta para no duplicar la visualización.
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(620, 120, 220, 160))
        self.textBrowser.setStyleSheet(info_style)
        self.textBrowser.setObjectName("textBrowser")

        # Línea horizontal decorativa.
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(0, 90, 900, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        # Se asigna el widget central a la ventana.
        MainWindow.setCentralWidget(self.centralwidget)

        # Barra de menú superior.
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        # Barra inferior de estado.
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # Se colocan los textos visibles en la interfaz.
        self.retranslateUi(MainWindow)

        # Conecta automáticamente señales internas de Qt si existieran.
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """
        Define los textos que aparecen en la ventana.

        Se separa esta parte porque PyQt acostumbra manejar los textos visibles
        en una función aparte.
        """
        _translate = QtCore.QCoreApplication.translate

        MainWindow.setWindowTitle(_translate("MainWindow", "I2C e interfaz gráfica"))

        self.pushButton.setText(_translate("MainWindow", "Logo"))
        self.pushButton_2.setText(_translate("MainWindow", "Tec"))
        self.pushButton_3.setText(_translate("MainWindow", "3 Tec"))
        self.pushButton_4.setText(_translate("MainWindow", "Nombres"))
        self.pushButton_5.setText(_translate("MainWindow", "Enviar Mensaje"))

        self.textBrowser.setHtml(_translate(
            "MainWindow",
            "<html><body>"
            "<p><b>Equipo:</b></p>"
            "<p>Luis Fernando Salazar Hernández</p>"
            "<p>Magdaleno Pérez Olmos</p>"
            "<p>Fatima Valeria Huerta Cabrera</p>"
            "</body></html>"
        ))