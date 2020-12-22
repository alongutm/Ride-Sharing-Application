import sys
from backend import Backend
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox, \
    QVBoxLayout, QDateTimeEdit, QCalendarWidget
from PyQt5.QtGui import QImage, QPalette, QBrush, QIcon, QPixmap, QIntValidator, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp, QDateTime, QDate, pyqtSignal, pyqtSlot
from pyqtlet import L, MapWidget
from math import radians, cos, sin, asin, sqrt
from datetime import datetime


def generate_button(button_text):
    button = QPushButton(button_text)
    font_size = button.font()
    font_size.setPointSize(14)
    button.setFont(font_size)
    button.setFixedWidth(380)
    button.setStyleSheet("QPushButton { background-color: rgba(0,0,255,25%); border-style: outset; border-width: 4px; border-radius: 10px; border-color: beige; opacity: 0.5; }"
                         "QPushButton:hover { background-color: rgba(0,0,255,70%)}")
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

    first_signal = pyqtSignal()
    second_signal = pyqtSignal()

    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)

        self.first_signal.connect(self.signal_enable_select_destination)
        self.second_signal.connect(self.signal_enable_select_date)
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
        self.setFixedHeight(850)

        # set logo
        self.set_logo()

        # set footer
        self.set_footer()

        self.layout.setSpacing(8)

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

        # set user selected date
        self.selected_date = None
        self.calendar = None
        self.map = MapWindow(self)

    def signal_enable_select_destination(self):
        self.location_button.setText('1. Select Start Location  √')
        self.button_destination.setDisabled(False)

    def signal_enable_select_date(self):
        self.button_destination.setText('2. Select Destination  √')
        self.button_set_calender_window.setDisabled(False)

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
        footer = QLabel('<font size="5">This application developed by Alon Gutman & Aviv Amsellem.</font>', self)
        footer.setFixedWidth(900)
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("QLabel { background-color : black; color : white; }")

        footer.move(0, 820)

    def check_credentials(self):
        self.set_after_login_window() # TODO: delete later
        msg = QMessageBox()
        msg.setWindowIcon(QIcon("assets/icon.png"))

        if self.lineEdit_username.text() == '' or self.lineEdit_password.text() == '':
            pass

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
                self.set_after_login_window()

        # login_res = self.backend.login(self.lineEdit_username, self.lineEdit_password)

    def set_background_image(self):
        # set background
        oImage = QImage("assets/background3.jpg")
        # sImage = oImage.scaled(QSize(900, 800))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(oImage))
        self.setPalette(palette)

    def set_after_login_window(self):
        self.clean_layout()

        # set buttons
        self.add_new_ride_button = generate_button("Add New Ride")
        self.add_new_ride_button.clicked.connect(self.set_add_ride_window)
        self.layout.addWidget(self.add_new_ride_button, 0, 0)


        # set buttons
        self.search_ride_button = generate_button("Search Ride")
        # self.search_ride_button.clicked.connect(self.set_search_window_first_step) # TODO:
        self.layout.addWidget(self.search_ride_button, 1, 0)


        self.back_to_login_button = generate_button("logout")
        self.back_to_login_button.clicked.connect(self.set_login_window)
        self.layout.addWidget(self.back_to_login_button, 2, 0)
        self.setLayout(self.layout)

    def set_add_ride_window(self):
        self.clean_layout()
        self.selected_date = None
        self.map.locations = {}

        # location button
        self.location_button = generate_button('1. Select Start Location')
        self.location_button.clicked.connect(self.set_map_loc_selector)
        self.layout.addWidget(self.location_button, 0, 0)

        # destination button
        self.button_destination = generate_button('2. Select Destination')
        self.button_destination.clicked.connect(self.set_map_dest_selector)
        self.button_destination.setDisabled(True)
        self.layout.addWidget(self.button_destination, 1, 0)

        # select date button
        self.button_set_calender_window = generate_button('3. Select Exit Date')
        self.button_set_calender_window.clicked.connect(self.show_calender)
        self.button_set_calender_window.setDisabled(False) # TODO: change back later to True
        self.layout.addWidget(self.button_set_calender_window, 2, 0)

        # set calender at row 3 at the layout
        self.calendar = self.set_calender()
        self.layout.addWidget(self.calendar, 3, 0)
        self.calendar.hide()

        # search step button
        self.next_button = generate_button('Choose Date')
        self.next_button.clicked.connect(self.close_calender)
        self.layout.addWidget(self.next_button, 4, 0)
        self.next_button.hide()

        # select time button
        self.button_set_time_window = generate_button('4. Select Exit Time')
        self.button_set_time_window.clicked.connect(self.set_time_fields)
        self.button_set_time_window.setDisabled(True)
        self.layout.addWidget(self.button_set_time_window, 5, 0)

        # set hours and minutes fields fields row 6,1 and 6,1 in the layout
        self.text_field_hours, self.text_field_minutes = self.set_hours_times_fields()

        # 'set time' button
        self.button_set_time = generate_button('Set Time')
        self.button_set_time.clicked.connect(self.close_time_fields_and_button)
        self.layout.addWidget(self.button_set_time, 7, 0)
        self.button_set_time.hide()

        # select cost button
        self.button_select_cost = generate_button('5. Select Cost Per Person')
        self.button_select_cost.clicked.connect(self.show_cost_field_and_button)
        self.layout.addWidget(self.button_select_cost, 8, 0)
        self.button_select_cost.setDisabled(True)

        # set cost field
        self.text_field_cost = self.set_cost_field()
        self.layout.addWidget(self.text_field_cost, 9, 0)

        # set cost button
        self.button_set_cost = generate_button('Set Cost')
        self.button_set_cost.clicked.connect(self.close_cost_field_and_button)
        self.layout.addWidget(self.button_set_cost, 10, 0)
        self.button_set_cost.hide()

        # add new ride button
        self.button_add_new_ride = generate_button('Add New Ride')
        self.button_add_new_ride.clicked.connect(self.add_new_ride)
        self.layout.addWidget(self.button_add_new_ride, 11, 0)
        self.button_add_new_ride.setDisabled(True)

        # back to after login window
        self.button_back_to_after_login_window = generate_button('back')
        self.button_back_to_after_login_window.clicked.connect(self.set_after_login_window)
        self.layout.addWidget(self.button_back_to_after_login_window, 12, 0)



        # # next step button
        # self.next_button = generate_button('Next')
        # self.next_button.clicked.connect(self.set_search_window_second_step)
        # self.layout.addWidget(self.next_button, 5, 0)

        # # destination button
        # self.button_destination = generate_button('Select destination')
        # self.button_destination.clicked.connect(self.set_map_dest_selector)
        # self.layout.addWidget(self.button_destination, 2, 0)

        # # radius
        # self.label_radius = generate_label('Max distance from destination')
        # self.lineEdit_radius = generate_input_text_filed("Please enter your max distance (in KM)")
        # self.layout.addWidget(self.label_radius, 0, 0)
        # self.layout.addWidget(self.lineEdit_radius, 0, 1)

        # date time
        # self.label_password = generate_label('Password')
        # self.lineEdit_password = generate_input_text_filed("Please enter your password")
        # self.lineEdit_password.setEchoMode(QLineEdit.Password)
        # self.layout.addWidget(self.label_password, 1, 0)
        # self.layout.addWidget(self.lineEdit_password, 1, 1)

        self.setLayout(self.layout)

    def add_new_ride(self):
        
        # dictionary of start location and destination key: 'start_location', 'end_location'
        print(f"selected start_location: {self.map.locations['start_location'].latLng[0]}, {self.map.locations['start_location'].latLng[1]}")
        print(f"selected end_location: {self.map.locations['end_location'].latLng[0]}, {self.map.locations['end_location'].latLng[1]}") # dictionary of start location and destination key: 'start_location', 'end_location'

        print(f'selected_date {self.selected_date}') # tuple of 3 for day month year
        print(f'selected time: {self.text_field_hours.text()} : {self.text_field_minutes.text()}')
        print(f'selected cost: {self.text_field_cost.text()}')

    def close_cost_field_and_button(self):
        if self.text_field_cost.text() != '':
            self.button_set_calender_window.show()  # 2
            self.calendar.hide()  # 3
            self.next_button.hide()  # 4
            self.button_set_time_window.show()  # 5
            self.text_field_hours.hide()  # 6.1
            self.text_field_minutes.hide()  # 6.2
            self.button_set_time.hide()  # 7
            self.button_select_cost.show()    # 8
            self.text_field_cost.hide()   # 9
            self.button_set_cost.hide()   # 10

            self.button_select_cost.setText('5. Select Cost Per Person  √')
            self.button_add_new_ride.setDisabled(False)

    def show_cost_field_and_button(self):
        self.button_set_calender_window.show()  # 2
        self.calendar.hide()  # 3
        self.next_button.hide()  # 4
        self.button_set_time_window.show()  # 5
        self.text_field_hours.hide()  # 6.1
        self.text_field_minutes.hide()  # 6.2
        self.button_set_time.hide()  # 7
        self.button_select_cost.hide()    # 8
        self.text_field_cost.show()   # 9
        self.button_set_cost.show()   # 10

    def set_cost_field(self):

        cost_validator = QIntValidator(0, 999, self)

        # create hours field
        text_field = QLineEdit()
        font_size = text_field.font()
        font_size.setPointSize(12)
        text_field.setFont(font_size)
        text_field.setFixedWidth(380)
        text_field.setValidator(cost_validator)
        text_field.setMaxLength(9)
        text_field.setPlaceholderText('Cost per person in Shekels ₪')
        self.layout.addWidget(text_field, 6, 0)
        text_field.hide()

        return text_field

    def set_hours_times_fields(self) -> tuple:

        # set validators to the hour and minute fields
        hours_validator = QIntValidator(0, 24, self)
        minutes_validator = QIntValidator(0, 60, self)

        # create hours field
        text_field_hours = QLineEdit()
        font_size = text_field_hours.font()
        font_size.setPointSize(12)
        text_field_hours.setFont(font_size)
        text_field_hours.setFixedWidth(185)
        text_field_hours.setValidator(hours_validator)
        text_field_hours.setMaxLength(2)
        text_field_hours.setPlaceholderText('Hours 00 - 24')
        self.layout.addWidget(text_field_hours, 6, 0)
        text_field_hours.hide()

        # create minutes fields
        text_field_minutes = input_text_field = QLineEdit()
        font_size = text_field_minutes.font()
        font_size.setPointSize(12)
        text_field_minutes.setFont(font_size)
        text_field_minutes.setValidator(minutes_validator)
        text_field_minutes.setMaxLength(2)
        text_field_minutes.setFixedWidth(185)
        text_field_minutes.setPlaceholderText('Minutes 00 - 60')
        self.layout.addWidget(text_field_minutes, 6, 1)
        text_field_minutes.hide()

        return text_field_hours, text_field_minutes

    def set_time_fields(self):
        self.button_set_calender_window.show()  # 2
        self.calendar.hide()  # 3
        self.next_button.hide()  # 4
        self.button_set_time_window.hide()  # 5
        self.text_field_hours.show()  # 6.1
        self.text_field_minutes.show()  # 6.2
        self.button_set_time.show()  # 7
        self.button_select_cost.show()    # 8
        self.text_field_cost.hide()   # 9
        self.button_set_cost.hide()   # 10

    def close_time_fields_and_button(self):
        if self.text_field_hours.text() != '' and self.text_field_minutes.text() != '':
            self.button_set_calender_window.show()  # 2
            self.calendar.hide()  # 3
            self.next_button.hide()  # 4
            self.button_set_time_window.show()  # 5
            self.text_field_hours.hide()  # 6.1
            self.text_field_minutes.hide()  # 6.2
            self.button_set_time.hide()  # 7
            self.button_select_cost.show()    # 8
            self.text_field_cost.hide()   # 9
            self.button_set_cost.hide()   # 10

            self.button_set_time_window.setText('4. Select Exit Time  √')
            self.button_select_cost.setDisabled(False)

    def set_map_loc_selector(self):
        self.map.is_chose_start_location = False
        self.map.show_map()

    def set_map_dest_selector(self):
        self.map.is_chose_start_location = True
        self.map.show_map()

    def show_calender(self):
        self.button_set_calender_window.hide()  # 2
        self.calendar.show()    # 3
        self.next_button.show() # 4
        self.button_set_time_window.show()  # 5
        self.text_field_hours.hide()    # 6.1
        self.text_field_minutes.hide()  # 6.2
        self.button_set_time.hide()     # 7
        self.button_select_cost.show()    # 8
        self.text_field_cost.hide()   # 9
        self.button_set_cost.hide()   # 10

    def set_calender(self):
        # set calendar
        my_calendar = QCalendarWidget(self)
        # self.calendar.move(112, 112)
        my_calendar.setGridVisible(True)
        # self.calendar.setGeometry(100, 180, 200, 150)
        # self.calendar.setGeometry(50, 50, 50, 50)
        my_calendar.setFixedWidth(380)
        my_calendar.setFixedHeight(200)
        currentMonth = datetime.now().month
        currentYear = datetime.now().year
        currentDay = datetime.now().day
        my_calendar.setMinimumDate(QDate(currentYear, currentMonth, currentDay))
        my_calendar.clicked.connect(self.save_date)

        print(f"current month is {currentMonth} and curr year is {currentYear} and curr ay is {currentDay} ")

        return my_calendar

    def close_calender(self):
        if self.selected_date != None:

            self.button_set_calender_window.show()  # 2
            self.calendar.hide()  # 3
            self.next_button.hide()  # 4
            self.button_set_time_window.show()  # 5
            self.text_field_hours.hide()  # 6.1
            self.text_field_minutes.hide()  # 6.2
            self.button_set_time.hide()  # 7
            self.button_select_cost.show()    # 8
            self.text_field_cost.hide()   # 9
            self.button_set_cost.hide()   # 10

            self.button_set_calender_window.setText('3. Select Exit Date  √')
            self.button_set_time_window.setDisabled(False)

            self.setLayout(self.layout)

    def save_date(self):
        self.selected_date = self.calendar.selectedDate().getDate()
        print(f'{self.selected_date[2]}-{self.selected_date[1]}-{self.selected_date[0]}')

    # def set_search_window_first_step(self):
    #     self.clean_layout()
    #
    #     # location button
    #     self.location_button = generate_button('Select start location')
    #     self.location_button.clicked.connect(self.set_map_loc_selector)
    #     self.layout.addWidget(self.location_button, 2, 1)
    #
    #     # # destination button
    #     # self.button_destination = generate_button('Select destination')
    #     # self.button_destination.clicked.connect(self.set_map_dest_selector)
    #     # self.layout.addWidget(self.button_destination, 2, 0)
    #
    #     # # radius
    #     # self.label_radius = generate_label('Max distance from destination')
    #     # self.lineEdit_radius = generate_input_text_filed("Please enter your max distance (in KM)")
    #     # self.layout.addWidget(self.label_radius, 0, 0)
    #     # self.layout.addWidget(self.lineEdit_radius, 0, 1)
    #
    #     # date time
    #     # self.label_password = generate_label('Password')
    #     # self.lineEdit_password = generate_input_text_filed("Please enter your password")
    #     # self.lineEdit_password.setEchoMode(QLineEdit.Password)
    #     # self.layout.addWidget(self.label_password, 1, 0)
    #     # self.layout.addWidget(self.lineEdit_password, 1, 1)
    #
    #     self.setLayout(self.layout)


class MapWindow(QWidget):

    first_signal = pyqtSignal()
    second_signal = pyqtSignal()

    def __init__(self, parent, *args):
        # Setting up the widgets and layout
        super(MapWindow, self).__init__(*args)

        self.first_signal.connect(parent.first_signal.emit)
        self.second_signal.connect(parent.second_signal.emit)

        self.mapWidget = MapWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.mapWidget)
        self.setWindowTitle('BGRide Map')
        self.setLayout(self.layout)

        self.current_lat = None
        self.current_lang = None

        self.locations = {}

        self.places = []

        self.is_chose_start_location = False

        # Working with the maps with pyqtlet
        self.map = L.map(self.mapWidget)
        self.map.setView([31.256974278389507, 34.79832234475968], 14)

        self.set_new_ride_on_click()

        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
        self.marker = L.marker([75.262070, 34.798280], {'opacity': 0})
        self.marker.bindPopup('Sharmuta in this place')
        self.map.addLayer(self.marker)

    def show_map(self):
        self.mapWidget.show()
        self.show()

    def get_lat_and_lng(self):
        if self.current_lat is not None:
            return self.current_lat, self.current_lang

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

    def set_lng_and_lat(self, location_pressed):

        # get current x,y of user's mouse press
        lat = location_pressed['latlng']['lat']
        lang = location_pressed['latlng']['lng']

        print(f"lat is {lat} and lang is {lang}")

        # a select start location has chosen
        if not self.is_chose_start_location:
            if 'start_location' in self.locations:
                # a start location as already chosen and we need to delete the old one
                self.map.removeLayer(self.locations['start_location'])

            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)

            # get the new location
            self.locations['start_location'] = L.marker([lat, lang], {'opacity': 0.5})
            self.map.addLayer(self.locations['start_location'])
            self.first_signal.emit()

        # a select destination has chosen
        else:
            if 'end_location' in self.locations:
                # a destination as already chosen and we need to delete the old one
                self.map.removeLayer(self.locations['end_location'])

            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)

            # get the new location
            self.locations['end_location'] = L.marker([lat, lang], {'opacity': 0.5})
            self.map.addLayer(self.locations['end_location'])
            self.second_signal.emit()







        #
        # if self.current_lang is not None:
        #     # remove previous point
        #     self.map.removeLayer(self.marker)
        #
        # self.current_lat = lat
        # self.current_lang = lang
        # L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
        # self.marker = L.marker([self.current_lat, self.current_lang], {'opacity': 0.5})
        # self.marker.bindPopup('New Ride')
        # self.map.addLayer(self.marker)
        #
        # if not self.is_chose_start_location:
        #     self.locations['start_location'] = lat, lang



        button_reply = QMessageBox.question(self, 'Message', "Is it your desired location?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if button_reply == QMessageBox.Yes:
            print('Yes clicked.')
            # if self.map.user_map == "location":
            #     print("selected location lang is", lang)
            # else:
            #     self.parent.set_selected_destination(lat, lang)
            #     print("selected destination lang is", lang)
            self.mapWidget.hide()
            self.hide()

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
