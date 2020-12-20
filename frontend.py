import sys
from backend import Backend
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox, QVBoxLayout
from PyQt5.QtGui import QImage, QPalette, QBrush, QIcon, QPixmap, QIntValidator, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp
from pyqtlet import L, MapWidget
from math import radians, cos, sin, asin, sqrt


def generate_button(button_text):
    button = QPushButton(button_text)
    font_size = button.font()
    font_size.setPointSize(14)
    button.setFont(font_size)
    button.setFixedWidth(380)
    return button


def generate_label(label_text: str):
    label = QLabel(f'<font size="14"><b>{label_text}</b></font>')
    label.setAlignment(Qt.AlignCenter)
    return label


def generate_input_text_filed(placeholder_text):
    input_text_field = QLineEdit()
    font_size = input_text_field.font()
    font_size.setPointSize(14)
    input_text_field.setFont(font_size)
    input_text_field.setFixedWidth(380)
    input_text_field.setPlaceholderText(placeholder_text)
    return input_text_field


def pop_error_message_box(window_title, error_text_message):
    msg = QMessageBox()
    msg.setWindowIcon(QIcon("assets/icon.png"))
    msg.setWindowTitle(window_title)
    msg.setText(error_text_message)
    msg.exec_()

def check_if_close_enough(x_loc_main, y_loc_main, x_loc, y_loc, max_dist):
    """
       Calculate the great circle distance between two points
       on the earth (specified in decimal degrees)
       """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [y_loc_main, x_loc_main, y_loc, x_loc])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r < max_dist



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

        self.layout.setSpacing(20)

        # set locations by user
        self.selected_loc_x = None
        self.selected_loc_y = None
        self.selected_destination_x = None
        self.selected_destination_y = None
        # set map window
        self.map_locations = None
        self.map_destinations = None
        # set current user map select
        self.user_map = None

        self.map = None


    def set_login_window(self):
        self.clean_layout()

        # username
        self.label_username = generate_label('Username')
        self.lineEdit_username = generate_input_text_filed("Please enter your username")
        self.layout.addWidget(self.label_username, 0, 0)
        self.layout.addWidget(self.lineEdit_username, 0, 1)

        # password
        self.label_password = generate_label('Password')
        self.lineEdit_password = generate_input_text_filed("Please enter your password")
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.label_password, 1, 0)
        self.layout.addWidget(self.lineEdit_password, 1, 1)

        # register button
        self.register_button = generate_button('Register')
        self.register_button.clicked.connect(self.set_register_window)
        self.layout.addWidget(self.register_button, 2, 0)

        # login button
        self.button_login = generate_button('Login')
        self.button_login.clicked.connect(self.check_credentials)
        self.layout.addWidget(self.button_login, 2, 1)

        self.setLayout(self.layout)

    def set_register_window(self):
        self.clean_layout()

        # username
        self.label_username = generate_label('Username')
        self.lineEdit_username_register = generate_input_text_filed("At list 3 latin characters")
        regex = QRegExp("[a-z-A-Z_]+")
        validator = QRegExpValidator(regex)
        self.lineEdit_username_register.setValidator(validator)
        self.layout.addWidget(self.label_username, 0, 0)
        self.layout.addWidget(self.lineEdit_username_register, 0, 1)

        # first name
        self.label_first_name = generate_label('First Name')
        self.lineEdit_first_name_register = generate_input_text_filed("Your first name")
        self.layout.addWidget(self.label_first_name, 1, 0)
        self.layout.addWidget(self.lineEdit_first_name_register, 1, 1)

        # last name
        self.label_last_name = generate_label("Last Name")
        self.lineEdit_last_name_register = generate_input_text_filed("Your last name")
        self.layout.addWidget(self.label_last_name, 2, 0)
        self.layout.addWidget(self.lineEdit_last_name_register, 2, 1)

        # email name
        self.label_email = generate_label('Email Address')
        self.lineEdit_email_register = generate_input_text_filed("Your *BGU* email address")
        self.layout.addWidget(self.label_email, 3, 0)
        self.layout.addWidget(self.lineEdit_email_register, 3, 1)

        # phone number
        self.label_phone = generate_label('Phone Number')
        self.lineEdit_phone_register = generate_input_text_filed("Your phone number")
        only_int = QIntValidator()
        self.lineEdit_phone_register.setValidator(only_int)
        self.layout.addWidget(self.label_phone, 4, 0)
        self.layout.addWidget(self.lineEdit_phone_register, 4, 1)

        # password
        self.label_password = generate_label('Password')
        self.lineEdit_password_register = generate_input_text_filed("At list 8 characters")
        self.lineEdit_password_register.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.label_password, 5, 0)
        self.layout.addWidget(self.lineEdit_password_register, 5, 1)

        # re-password
        self.label_re_password = generate_label('re-Password')
        self.lineEdit_re_password_register = generate_input_text_filed("Please re-enter the password")
        self.lineEdit_re_password_register.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.label_re_password, 6, 0)
        self.layout.addWidget(self.lineEdit_re_password_register, 6, 1)

        # register button
        self.login_window_button = generate_button('Already have account')
        self.login_window_button.clicked.connect(self.set_login_window)
        self.layout.addWidget(self.login_window_button, 7, 0)

        # register
        self.button_signup = generate_button('Sign up')
        self.button_signup.clicked.connect(self.sign_up_new_user)
        self.layout.addWidget(self.button_signup, 7, 1)

    def sign_up_new_user(self):
        if self.check_new_user_details():
            pass

    def check_new_user_details(self):
        if len(self.lineEdit_password_register.text()) < 8 or len(self.lineEdit_re_password_register.text()) < 8:
            error_message = "Password too small.\n" \
                            "At list 8 characters."
            pop_error_message_box('Signup Error', error_message)
            return False
        elif self.lineEdit_password_register.text() != self.lineEdit_re_password_register.text():
            error_message = "passwords doesn't match.\n" \
                            "Please try again."
            pop_error_message_box('Signup Error', error_message)
            return False
        elif len(self.lineEdit_phone_register.text()) != 10 or int(self.lineEdit_phone_register.text()) < 0 or \
                str(self.lineEdit_phone_register.text()[0:2]) != '05':
            error_message = "Illegal phone number.\n" \
                            "Please try again."
            pop_error_message_box('Signup Error', error_message)
            return False
        elif self.lineEdit_first_name_register.text() == '':
            error_message = "You forgot to enter your first name.\n" \
                            "Please try again."
            pop_error_message_box('Signup Error', error_message)
            return False
        elif self.lineEdit_last_name_register.text() == '':
            error_message = "You forgot to enter your last name.\n" \
                            "Please try again."
            pop_error_message_box('Signup Error', error_message)
            return False

        elif len(self.lineEdit_email_register.text()) < 16 or self.lineEdit_email_register.text()[
                                                              -15:] != '@post.bgu.ac.il':
            error_message = "Invalid email address.\n" \
                            "only BGU email address - @post.bgu.ac.il suffix.\n" \
                            "Please try again."
            pop_error_message_box('Signup Error', error_message)
            return False
        elif self.lineEdit_username_register.text() == '':
            error_message = "Please pick a username.\n"
            pop_error_message_box('Signup Error', error_message)
            return False
        elif len(self.lineEdit_username_register.text()) < 3:
            error_message = "Username is too short.\n" \
                            "Please try again."
            pop_error_message_box('Signup Error', error_message)
            return False

        elif not self.backend.check_if_username_taken(self.lineEdit_username_register.text()):
            error_message = "Username is already taken.\n" \
                            "Please choose another username."
            pop_error_message_box('Signup Error', error_message)
            return False

        if self.backend.register(self.lineEdit_username_register.text(), self.lineEdit_first_name_register.text(),
                                 self.lineEdit_last_name_register.text(), self.lineEdit_password_register.text(),
                                 self.lineEdit_email_register.text(), self.lineEdit_phone_register.text()):
            self.set_login_window()
            success_message = "Succeeded creating a new account!.\n"
            pop_error_message_box('Signup Succeeded', success_message)
            return True
        else:
            error_message = "Something went wrong.\n" \
                            "Please try again later."
            pop_error_message_box('Signup Error', error_message)
            return False

    def clean_layout(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def set_logo(self):
        label_image = QLabel(self)
        label_image.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("assets/logo2.png")
        label_image.setPixmap(pixmap)
        label_image.setAlignment(Qt.AlignCenter)
        label_image.resize(231, 161)
        label_image.move(355, 3)

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
                msg.exec_()
            else:
                msg.setWindowTitle('Success')
                msg.setText('Succeeded login in.')
                msg.exec_()
                self.navigate_after_login()

        # login_res = self.backend.login(self.lineEdit_username, self.lineEdit_password)

    def set_background_image(self):
        # set background
        oImage = QImage("assets/background3.jpg")
        # sImage = oImage.scaled(QSize(900, 800))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(oImage))
        self.setPalette(palette)

    def navigate_after_login(self):
        self.clean_layout()

        # set buttons
        self.search_ride_button = generate_button("Search For A Ride")
        self.search_ride_button.clicked.connect(self.set_search_window)
        self.layout.addWidget(self.search_ride_button, 0, 0)
        self.setLayout(self.layout)

    def set_map_loc_selector(self):
        # print("set map location selector, the map is", self.map_locations)
        # self.set_map()

        if self.map is None:
            self.map = MapWindow()
        else:
            self.map.show_map()
        # self.map_locations.show()
        # print(self.map_locations)

    def set_map_dest_selector(self):
        # print("set map destination selector, the map is", self.map_destinations)
        if self.map is None:
            self.map = MapWindow()
        else:
            self.map.show_map()
        # self.map_destinations.mapWidget.show()
        # print(self.map_destinations)

    def set_search_window(self):
        self.clean_layout()

        # location button
        self.location_button = generate_button('Select location')
        self.location_button.clicked.connect(self.set_map_loc_selector)
        self.layout.addWidget(self.location_button, 2, 1)

        # destination button
        self.button_destination = generate_button('Select destination')
        self.button_destination.clicked.connect(self.set_map_dest_selector)
        self.layout.addWidget(self.button_destination, 2, 0)

        # radius
        self.label_radius = generate_label('Max distance from destination')
        self.lineEdit_radius = generate_input_text_filed("Please enter your max distance (in KM)")
        self.layout.addWidget(self.label_radius, 0, 0)
        self.layout.addWidget(self.lineEdit_radius, 0, 1)

        # date time
        # self.label_password = generate_label('Password')
        # self.lineEdit_password = generate_input_text_filed("Please enter your password")
        # self.lineEdit_password.setEchoMode(QLineEdit.Password)
        # self.layout.addWidget(self.label_password, 1, 0)
        # self.layout.addWidget(self.lineEdit_password, 1, 1)

        self.setLayout(self.layout)

    def set_selected_destination(self, x, y):
        self.selected_destination_x = x
        self.selected_destination_y = y

    def set_selected_location(self, x, y):
        self.selected_loc_x = x
        self.selected_loc_y = y


class MapWindow(QWidget):
    def __init__(self):
        # Setting up the widgets and layout
        super().__init__()
        self.mapWidget = MapWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.mapWidget)
        self.setWindowTitle('BGRide Map')
        self.setLayout(self.layout)
        # self.button = generate_button('Confirm Location')
        # self.button.clicked.connect(self.check_selected_location)
        self.current_lat = None
        self.current_lang = None
        self.places = []


        # Working with the maps with pyqtlet
        self.map = L.map(self.mapWidget)
        self.map.setView([31.256974278389507, 34.79832234475968], 14)

        self.set_new_ride_on_click()

        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
        self.marker = L.marker([75.262070, 34.798280], {'opacity': 1})
        self.marker.bindPopup('Sharmuta in this place')
        self.map.addLayer(self.marker)

        # L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
        # self.marker = L.marker([31.242811866862326, 34.81084127358059])
        # self.marker.bindPopup('Sharmuta here too')
        # self.map.addLayer(self.marker)
        #
        # # Create a icon called markerIcon in the js runtime.
        # self.map.runJavaScript(
        #     'var markerIcon = L.icon({iconUrl: "C:/photo.png"});')
        # # Edit the existing python object by accessing it's jsName property
        # self.map.runJavaScript(f'{self.marker.jsName}.setIcon(markerIcon);')
        # self.map
        self.show()

    def show_map(self):
        self.mapWidget.show()
        self.show()

    def check_selected_location(self):
        if self.current_lang is None:
            return False
        self.hide()
        self.parent.set_selected_location(self.current_lat, self.current_lang)
        self.current_lang = None
        self.current_lat = None
        return True

    def check_selected_destination(self):
        if self.current_lang is None:
            return False
        self.hide()
        self.parent.set_selected_destination(self.current_lat, self.current_lang)
        self.current_lang = None
        self.current_lat = None
        return True

    def set_new_ride_on_click(self):
        self.map.clicked.connect(lambda x: self.set_lng_and_lat(x))

    def set_lng_and_lat(self, x):
        # get current x,y of user's mouse press
        lat = x['latlng']['lat']
        lang = x['latlng']['lng']
        # print(f"lat is {lat} and lang is {lang}")
        if self.current_lang is not None:
            # remove previous point
            self.map.removeLayer(self.marker)

        self.current_lat = lat
        self.current_lang = lang
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
        self.marker = L.marker([self.current_lat, self.current_lang], {'opacity': 0.5})
        self.marker.bindPopup('New Ride')
        self.map.addLayer(self.marker)

        # self.check_selected_destination(lat, lang)
        # self.check_selected_location(lat, lang)
        print("lang is", lang)

        buttonReply = QMessageBox.question(self, 'Message', "Is it your desired location?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            print('Yes clicked.')
            if self.parent.user_map == "location":
                self.parent.set_selected_location(lat, lang)
                print("selected location lang is", lang)
            else:
                self.parent.set_selected_destination(lat, lang)
                print("selected destination lang is", lang)
            self.close()
            # self.hide()

        else:
            print('No clicked.')

    def show_rides_on_map(self, places_list):
        self.places = places_list
        for place in self.places:
            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
            self.marker = L.marker([place[3], place[4]], {'opacity': 1})
            string_info = f"Ride to {place[2]} On {place[5]} {place[6]} Cost is:{place[9]}-NIS"
            self.marker.bindPopup(string_info)
            self.map.addLayer(self.marker)
            self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec_())
