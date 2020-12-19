import sys
from backend import Backend
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox, QSizePolicy, QHBoxLayout
from PyQt5.QtGui import QImage, QPalette, QBrush, QIcon, QPixmap, QFont
from PyQt5.QtCore import QSize, Qt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.backend = Backend()
        # set window title
        self.setWindowTitle('BGRide')

        # set icon
        self.setWindowIcon(QIcon("assets/icon.png"))

        # set layout
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        # set login window
        self.set_login_window()

        # set background
        self.set_background_image()

        # set fixed window size
        self.setFixedWidth(900)
        self.setFixedHeight(800)

        # set logo
        self.set_logo()

        # set footer
        self.set_footer()

        self.layout.setSpacing(30)

    def set_login_window(self):
        self.clean_layout()

        # username
        self.label_username = QLabel('<font size="14"><b>Username</b></font>')
        self.label_username.setAlignment(Qt.AlignCenter)
        self.lineEdit_username = QLineEdit()
        font_size = self.lineEdit_username.font()
        font_size.setPointSize(14)
        self.lineEdit_username.setFont(font_size)
        self.lineEdit_username.setPlaceholderText("Please enter your username")
        self.lineEdit_username.setFixedWidth(380)
        self.layout.addWidget(self.label_username, 0, 0)
        self.layout.addWidget(self.lineEdit_username, 0, 1)

        # password
        self.label_password = QLabel('<font size="14"><b>    Password </b></font>')
        self.label_password.setAlignment(Qt.AlignCenter)
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        self.lineEdit_password.setFont(font_size)
        self.lineEdit_password.setPlaceholderText("Please enter your password")
        self.lineEdit_password.setFixedWidth(380)
        self.layout.addWidget(self.label_password, 1, 0)
        self.layout.addWidget(self.lineEdit_password, 1, 1)

        # login button
        self.button_login = QPushButton('Login')
        self.button_login.setFont(font_size)
        self.button_login.clicked.connect(self.check_credentials)
        self.button_login.setFixedWidth(380)
        self.layout.addWidget(self.button_login, 2, 0)

        # register_login = QPushButton('Not a member yet? register now!')
        self.register_button = QPushButton('Register')
        self.register_button.setFont(font_size)
        self.register_button.clicked.connect(self.set_register_window)
        self.register_button.setFixedWidth(380)
        self.layout.addWidget(self.register_button, 2, 1)

        self.setLayout(self.layout)

    def set_register_window(self):
        self.clean_layout()

        # first name
        self.label_username = QLabel('<font size="14"><b>Username</b></font>')
        self.label_username.setAlignment(Qt.AlignCenter)
        self.lineEdit_username_register = QLineEdit()
        font_size = self.lineEdit_username.font()
        font_size.setPointSize(14)
        self.lineEdit_username_register.setFont(font_size)
        self.lineEdit_username_register.setPlaceholderText("Please enter username")
        self.lineEdit_username_register.setFixedWidth(380)
        self.layout.addWidget(self.label_username, 0, 0)
        self.layout.addWidget(self.lineEdit_username_register, 0, 1)

        # first name
        self.label_first_namne = QLabel('<font size="14"><b>First Name</b></font>')
        self.label_first_namne.setAlignment(Qt.AlignCenter)
        self.lineEdit_first_name_register = QLineEdit()
        font_size = self.lineEdit_first_name_register.font()
        font_size.setPointSize(14)
        self.lineEdit_first_name_register.setFont(font_size)
        self.lineEdit_first_name_register.setPlaceholderText("Please enter your first name")
        self.lineEdit_first_name_register.setFixedWidth(380)
        self.layout.addWidget(self.label_first_namne, 1, 0)
        self.layout.addWidget(self.lineEdit_first_name_register, 1, 1)




    def clean_layout(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def set_logo(self):
        labelImage = QLabel(self)
        labelImage.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("assets/logo2.png")
        labelImage.setPixmap(pixmap)
        labelImage.setAlignment(Qt.AlignCenter)
        labelImage.resize(231, 161)
        labelImage.move(355, 3)

    def set_footer(self):
        footer = QLabel('<font size="6">This application developed by Alon Gutman & Aviv Amsellem.</font>', self)
        footer.setFixedWidth(900)
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("QLabel { background-color : black; color : white; }")

        footer.move(0, 770)

    def check_credentials(self):
        msg = QMessageBox()
        msg.setWindowIcon(QIcon("assets/icon.png"))

        if self.lineEdit_username.text() == '' or self.lineEdit_password.text() == '':
            msg.setWindowTitle('loginError')
            msg.setText('Username or Password is missing.\n'
                        'Please try again.')

        else:
            res_log = self.backend.login(self.lineEdit_username.text(), self.lineEdit_password.text())
            if not res_log[0]:
                msg.setWindowTitle('loginError')
                msg.setText('Incorrect Username or Password.\n'
                            'Please try again.')
            else:
                msg.setWindowTitle('Success')
                msg.setText('Succeeded login in.')
        msg.exec_()

        # login_res = self.backend.login(self.lineEdit_username, self.lineEdit_password)

    def set_background_image(self):
        # set background
        oImage = QImage("assets/background3.jpg")
        # sImage = oImage.scaled(QSize(900, 800))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(oImage))
        self.setPalette(palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    form = MainWindow()

    form.show()

    sys.exit(app.exec_())
