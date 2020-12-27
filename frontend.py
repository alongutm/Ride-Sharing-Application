import sys
import datetime

from PyQt5 import QtCore

from backend import Backend
from operator import itemgetter
from pyqtlet import L, MapWidget
from PyQt5.QtCore import Qt, QRegExp, QDate, pyqtSignal
from PyQt5.QtGui import QImage, QPalette, QBrush, QIcon, QPixmap, QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox, \
    QVBoxLayout, QCalendarWidget, QCheckBox, QComboBox

"""
This class represent the User Interface of the app.
all functionalities the app is capable off will be presented through the GUI system.
"""


def generate_button(button_text: str, size=14):
    """
    the function generates a button with a given text to set to the button
    and a given font_size.
    :param button_text: String. a text to set to the button.
    :param size: int. the size of the text.
    :return: button object.
    """
    button = QPushButton(button_text)
    font_size = button.font()
    font_size.setPointSize(size)
    button.setFont(font_size)
    button.setFixedWidth(380)
    button.setStyleSheet(
        "QPushButton { background-color: rgba(0,0,255,25%); border-style: outset; border-width: 4px; border-radius: 10px; border-color: beige; opacity: 0.5; }"
        "QPushButton:hover { background-color: rgba(0,0,255,70%)}")
    return button


def generate_label(label_text: str):
    """
    the function generates a label with a given text.
    :param label_text: String. a text to set to the label.
    :return: label object.
    """
    label = QLabel(f'<font size="14"><b>{label_text}</b></font>')
    label.setAlignment(Qt.AlignCenter)
    return label


def generate_input_text_filed(placeholder_text):
    """
    the function generates an input text field.
    :param placeholder_text: String. a text to set as a placeholder.
    :return: text input object.
    """
    input_text_field = QLineEdit()
    font_size = input_text_field.font()
    font_size.setPointSize(14)
    input_text_field.setFont(font_size)
    input_text_field.setFixedWidth(380)
    input_text_field.setPlaceholderText(placeholder_text)
    return input_text_field


def set_date_from_user(day: int, month: int, year: str) -> str:
    """
    the function receive 2 int and 1 String representing a date and
    return the date as a string of 'dd-mm-yyyy'
    :param day: int. represent the day of the date.
    :param month: int. represent the month of the date.
    :param year: String. represent the year of the date.
    :return: String. return a date is String of 'dd-mm-yyyy'.
    """
    if len(str(day)) == 1:
        day = f'0{day}'
    if len(str(month)) == 1:
        month = f'0{month}'

    return f'{day}-{month}-{year}'


def set_time_from_user(hours: str, minutes: str) -> str:
    """
    the function receive 2 Strings representing a time and
    return the time as a string of 'hh-mm'
    :param hours: String. represent the hours of the time.
    :param minutes: String. represent the minutes of the time.
    :return: String. return a time is String of 'hh-mm'.
    """
    if len(hours) == 1:
        hours = f'0{hours}'

    if len(minutes) == 1:
        minutes = f'0{minutes}'

    return f'{hours}-{minutes}'


def pop_message_box(window_title: str, error_text_message: str):
    """
    the function generate a popup message to the user with a given text
    to show and a given window title.
    :param window_title: String. represent the window title text.
    :param error_text_message: String. represent the window text.
    """
    msg = QMessageBox()
    msg.setWindowIcon(QIcon("assets/icon.png"))
    msg.setWindowTitle(window_title)
    msg.setText(error_text_message)
    msg.exec_()


class MainWindow(QWidget):
    """
    Main Window class of the GIU application.
    """
    # map signals
    first_signal = pyqtSignal()
    second_signal = pyqtSignal()
    third_signal = pyqtSignal()

    # checkbox signals
    checkbox_signal = pyqtSignal()
    select_ride_signal = pyqtSignal()

    def __init__(self, *args):
        """
        constructor
        """
        super(MainWindow, self).__init__(*args)

        self.first_signal.connect(self.signal_enable_select_destination)
        self.second_signal.connect(self.signal_enable_select_date)
        self.third_signal.connect(self.signal_enable_select_date_search)

        self.checkbox_signal.connect(self.add_new_ride)
        self.select_ride_signal.connect(self.join_ride)

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
        self.checkbox = CheckBox(self)

        # id of logged in user
        self.current_user_id = 0
        self.is_user_admin = False

        self.is_unset_click_map = False

        self.users_statistics_df = None
        self.full_username_dict = {}

        self.text_field_preferences = None

    def signal_enable_select_destination(self):
        """
        signal method. the function triggers when the user choose a start location and signal it
        to the Main Window application.
        """
        self.location_button.setText('1. Select Start Location  √')
        self.button_destination.setDisabled(False)

    def signal_enable_select_date(self):
        """
        signal method. the function triggers when the user choose a destination location and signal it
        to the Main Window application.
        """
        self.button_destination.setText('2. Select Destination  √')
        self.button_set_calender_window.setDisabled(False)

    def set_login_window(self):
        """
        first GUI window the user see. a window containing options to login
        or to move to registration window
        """
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
        """
        GUI window. a window containing the registration process for new users
        in the application.
        """
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
        self.button_signup.clicked.connect(self.check_new_user_details)
        self.layout.addWidget(self.button_signup, 7, 1)

    def check_new_user_details(self) -> bool:
        """
        the method checks if the new user registration fits all the condition
        for creating a new user.
        if it does - the method will pop a suuccess message.
        else - the method will pop an error message with an explanation.
        """
        if len(self.lineEdit_password_register.text()) < 8 or len(self.lineEdit_re_password_register.text()) < 8:
            error_message = "Password too small.\n" \
                            "At list 8 characters."
            pop_message_box('Signup Error', error_message)
            return False
        elif self.lineEdit_password_register.text() != self.lineEdit_re_password_register.text():
            error_message = "passwords doesn't match.\n" \
                            "Please try again."
            pop_message_box('Signup Error', error_message)
            return False
        elif len(self.lineEdit_phone_register.text()) != 10 or int(self.lineEdit_phone_register.text()) < 0 or \
                str(self.lineEdit_phone_register.text()[0:2]) != '05':
            error_message = "Illegal phone number.\n" \
                            "Please try again."
            pop_message_box('Signup Error', error_message)
            return False
        elif self.lineEdit_first_name_register.text() == '':
            error_message = "You forgot to enter your first name.\n" \
                            "Please try again."
            pop_message_box('Signup Error', error_message)
            return False
        elif self.lineEdit_last_name_register.text() == '':
            error_message = "You forgot to enter your last name.\n" \
                            "Please try again."
            pop_message_box('Signup Error', error_message)
            return False

        elif len(self.lineEdit_email_register.text()) < 16 or self.lineEdit_email_register.text()[
                                                              -15:] != '@post.bgu.ac.il':
            error_message = "Invalid email address.\n" \
                            "only BGU email address - @post.bgu.ac.il suffix.\n" \
                            "Please try again."
            pop_message_box('Signup Error', error_message)
            return False
        elif self.lineEdit_username_register.text() == '':
            error_message = "Please pick a username.\n"
            pop_message_box('Signup Error', error_message)
            return False
        elif len(self.lineEdit_username_register.text()) < 3:
            error_message = "Username is too short.\n" \
                            "Please try again."
            pop_message_box('Signup Error', error_message)
            return False

        elif not self.backend.check_if_username_taken(self.lineEdit_username_register.text()):
            error_message = "Username is already taken.\n" \
                            "Please choose another username."
            pop_message_box('Signup Error', error_message)
            return False

        if self.backend.register(self.lineEdit_username_register.text(), self.lineEdit_first_name_register.text(),
                                 self.lineEdit_last_name_register.text(), self.lineEdit_password_register.text(),
                                 self.lineEdit_email_register.text(), self.lineEdit_phone_register.text()):
            self.set_login_window()
            success_message = "Succeeded creating a new account!.\n"
            pop_message_box('Signup Succeeded', success_message)
            self.set_register_window()
            return True
        else:
            error_message = "Something went wrong.\n" \
                            "Please try again later."
            pop_message_box('Signup Error', error_message)
            return False

    def clean_layout(self):
        """
        the method cleans all the widgets in the layout.
        the method used for transitions between screens in the main window app.
        """
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def set_logo(self):
        """
        the method sets the application logo.
        """
        label_image = QLabel(self)
        label_image.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("assets/logo.png")
        label_image.setPixmap(pixmap)
        label_image.setAlignment(Qt.AlignCenter)
        label_image.resize(231, 161)
        label_image.move(355, 3)

    def set_footer(self):
        """
        the method sets a footer in the bottom of the application window.
        """
        footer = QLabel('<font size="5">This application developed by Alon Gutman & Aviv Amsellem.</font>', self)
        footer.setFixedWidth(900)
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("QLabel { background-color : black; color : white; }")

        footer.move(0, 820)

    def check_credentials(self):
        """
        the mehtod checks if the credentials inserted by the user is legal
        and exist in the application database.
        """
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
                self.current_user_id = res_log[2]
                self.is_user_admin = res_log[1]
                self.set_after_login_window()

        # login_res = self.backend.login(self.lineEdit_username, self.lineEdit_password)

    def set_background_image(self):
        """
        the method sets the image background in the main window application.
        """
        # set background
        oImage = QImage("assets/background.jpg")
        # sImage = oImage.scaled(QSize(900, 800))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(oImage))
        self.setPalette(palette)

    def set_after_login_window(self):
        """
        after login window. the window will contain all the features available to the user/admin.
        """
        self.clean_layout()
        self.map.is_search = False

        self.map.clean_selected_locations()
        self.map.locations = {}

        # set buttons
        self.add_new_ride_button = generate_button("Add New Ride")
        self.add_new_ride_button.clicked.connect(self.set_add_ride_window)
        self.layout.addWidget(self.add_new_ride_button, 0, 0)

        # set buttons
        self.search_ride_button = generate_button("Search Ride")
        self.search_ride_button.clicked.connect(self.open_search_window)
        self.layout.addWidget(self.search_ride_button, 1, 0)

        if self.is_user_admin:
            self.button_statistics = generate_button("Users Statistics")
            self.button_statistics.clicked.connect(self.open_statistics_window)
            self.button_statistics.setStyleSheet(
                "QPushButton { background-color: rgba(11,94,46,40%); border-style: outset; border-width: 5px; border-radius: 10px; border-color: beige; opacity: 1; }"
                "QPushButton:hover { background-color: rgba(11,94,46,80%)}")
            self.layout.addWidget(self.button_statistics, 2, 0)

        self.back_to_login_button = generate_button("logout")
        self.back_to_login_button.clicked.connect(self.set_login_window)
        self.layout.addWidget(self.back_to_login_button, 3, 0)
        self.setLayout(self.layout)

    def open_statistics_window(self):
        """
        a window only the application admin can see and have permissions to use.
        the window will contain seeing information about the users in the app.
        """
        self.clean_layout()

        self.users_statistics_df = self.backend.get_all_users()
        self.users_statistics_df = self.users_statistics_df.T.drop_duplicates().T

        # heat map button
        self.button_show_all_heat_map = generate_button("All Rides Destinations - Heat Map")
        self.button_show_all_heat_map.clicked.connect(self.show_all_users_heat_map)
        self.layout.addWidget(self.button_show_all_heat_map, 0, 0)

        # creating a combo box widget
        self.users_drop_list = QComboBox(self)
        self.users_drop_list.setFixedWidth(380)
        self.users_drop_list.setFixedHeight(30)
        self.users_drop_list.setEditable(True)

        self.full_username_dict = {}
        for index, row in self.users_statistics_df.iterrows():
            self.full_username_dict[f"{row['firstName']} {row['lastName']}"] = row['uid']

        del self.full_username_dict['admin admin']
        del self.full_username_dict['Aviv Amsellem']
        del self.full_username_dict['Alon Gutman']

        self.users_drop_list.addItems(self.full_username_dict.keys())
        line_edit = self.users_drop_list.lineEdit()
        line_edit.setAlignment(Qt.AlignCenter)
        line_edit.setReadOnly(True)
        font_size = line_edit.font()
        font_size.setPointSize(14)
        line_edit.setFont(font_size)
        self.users_drop_list.setFont(font_size)

        self.users_drop_list.setStyleSheet(
            "QComboBox { background-color: rgba(0,0,255,25%); border-style: outset; border-width: 4px; border-radius: "
            "10px; border-color: beige; opacity: 0.5; }")
        self.layout.addWidget(self.users_drop_list, 1, 0)

        # heat map button
        self.button_show_heat_map = generate_button("Show User Heat Map")
        self.button_show_heat_map.clicked.connect(self.show_user_heat_map)
        self.layout.addWidget(self.button_show_heat_map, 2, 0)

        # Show user preferences
        self.button_show_user_heat_map = generate_button("Show User Preferences")
        self.button_show_user_heat_map.clicked.connect(self.get_user_preferences)
        self.layout.addWidget(self.button_show_user_heat_map, 3, 0)

        # back to after login window
        self.button_back_to_after_login_window = generate_button('back')
        self.button_back_to_after_login_window.clicked.connect(self.set_after_login_window)
        self.layout.addWidget(self.button_back_to_after_login_window, 5, 0)

    def show_all_users_heat_map(self):
        """
        the method shows to the admin the heat map of all the users in the system
        together.
        """
        self.backend.all_rides_heat_maps_folium()

    def show_user_heat_map(self):
        """
        the method shows to the admin the heat map of a specific user.
        """
        self.backend.all_rides_by_user_heat_maps_folium(self.full_username_dict[self.users_drop_list.currentText()])

    def get_user_preferences(self):
        """
        the method shows to the admin the 3 most types of rides the user is taking.
        """
        if self.text_field_preferences is not None:
            self.text_field_preferences.setText('')

        user_id = self.full_username_dict[self.users_drop_list.currentText()]

        row = self.users_statistics_df.loc[self.users_statistics_df['uid'] == user_id]

        user_preferences = row[row.columns[-21:]].to_dict()

        user_preferences_dict = {}
        for key in user_preferences.keys():
            user_preferences_dict[key] = user_preferences[key][user_id - 1]

        top_preferences_dict = dict(sorted(user_preferences_dict.items(), key=itemgetter(1), reverse=True)[:3])
        top_preferences_list = list(top_preferences_dict)
        self.text_field_preferences = QLabel(f"<font size=12><b>User's most visited amenities:</b><br>" \
                                             f"1. {top_preferences_list[0]}<br>" \
                                             f"2. {top_preferences_list[1]}<br>"
                                             f"3. {top_preferences_list[2]}</font>")
        self.layout.addWidget(self.text_field_preferences, 4, 0)

    def set_add_ride_window(self):
        """
        add new ride window. a window contaning all the field required from the
        user to enter a new ride he want to do.
        """
        self.clean_layout()
        self.selected_date = None

        self.map.clean_selected_locations()
        self.map.locations = {}

        # location button
        self.map.set_new_ride_on_click()

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
        self.button_set_calender_window.setDisabled(True)
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
        self.text_field_hours, self.text_field_minutes = self.set_hours_times_fields(row=6)

        # 'set time' button
        self.button_set_time = generate_button('Set Time')
        self.button_set_time.clicked.connect(self.close_time_fields_and_button)
        self.layout.addWidget(self.button_set_time, 7, 0)
        self.button_set_time.hide()

        # select cost button
        self.button_select_cost = generate_button('5. Select Cost Per Person')
        self.button_select_cost.clicked.connect(self.show_cost_field_and_button)
        self.button_select_cost.setDisabled(True)
        self.layout.addWidget(self.button_select_cost, 8, 0)

        # set cost field
        self.text_field_cost = self.set_cost_field()
        cost_validator = QIntValidator(0, 999, self)
        self.text_field_cost.setValidator(cost_validator)
        self.text_field_cost.setMaxLength(3)
        self.text_field_cost.setPlaceholderText('Cost per person in Shekels ₪')
        self.layout.addWidget(self.text_field_cost, 9, 0)

        # 'set cost' button
        self.button_set_cost = generate_button('Set Cost')
        self.button_set_cost.clicked.connect(self.close_cost_field_and_button)
        self.layout.addWidget(self.button_set_cost, 10, 0)
        self.button_set_cost.hide()

        # select how many passengers button
        self.button_select_riders_amount = generate_button('6. Select Passengers Amount')
        self.button_select_riders_amount.clicked.connect(self.open_passengers_field_and_set_button)
        self.layout.addWidget(self.button_select_riders_amount, 11, 0)
        self.button_select_riders_amount.setDisabled(True)

        # set passengers amounts
        self.text_field_passengers = self.set_cost_field()
        passenges_validator = QIntValidator(1, 4, self)
        self.text_field_passengers.setValidator(passenges_validator)
        self.text_field_passengers.setMaxLength(1)
        self.text_field_passengers.setPlaceholderText('1 - 4 Passengers')
        self.layout.addWidget(self.text_field_passengers, 12, 0)

        # 'set passengers amount' button
        self.button_set_riders_amount = generate_button('Set Passengers Amount')
        self.button_set_riders_amount.clicked.connect(self.close_passengers_field_and_set_button)
        self.layout.addWidget(self.button_set_riders_amount, 13, 0)
        self.button_set_riders_amount.hide()

        # add new ride button
        self.button_add_new_ride = generate_button('Add New Ride')
        self.button_add_new_ride.clicked.connect(self.choose_ride_purposes)
        self.layout.addWidget(self.button_add_new_ride, 14, 0)
        self.button_add_new_ride.setDisabled(True)

        # back to after login window
        self.button_back_to_after_login_window = generate_button('back')
        self.button_back_to_after_login_window.clicked.connect(self.set_after_login_window)
        self.layout.addWidget(self.button_back_to_after_login_window, 15, 0)

        self.setLayout(self.layout)

    def choose_ride_purposes(self):
        """
        the method get all amenities that exist in a radius of 300 meters that exists
        from the location the user chose and pops a message checkbox for the user to check
        what is the purpose of the ride.
        """
        res = self.backend.get_ride_purposes_from_google_maps(self.map.locations['end_location'].latLng[0],
                                                              self.map.locations['end_location'].latLng[1])
        destination_address = self.backend.get_address_by_lan_lng(self.map.locations['end_location'].latLng[0],
                                                                  self.map.locations['end_location'].latLng[1])

        self.checkbox.open_checkbox_purposes(res, destination_address)

    def add_new_ride(self):
        """
        the method add a new ride to the database and pops a success message to
        the user if it succeeded.
        else - pops an error message.
        """
        uid = self.current_user_id
        start_location_lat = self.map.locations['start_location'].latLng[0]
        start_location_lng = self.map.locations['start_location'].latLng[1]
        end_location_lat = self.map.locations['end_location'].latLng[0]
        end_location_lng = self.map.locations['end_location'].latLng[1]
        exit_date = set_date_from_user(day=self.selected_date[2], month=self.selected_date[1],
                                       year=self.selected_date[0])
        exit_time = set_time_from_user(self.text_field_hours.text(), self.text_field_minutes.text())
        num_of_riders_capacity = self.text_field_passengers.text()
        cost = self.text_field_cost.text()
        ride_kind = self.checkbox.chosen_purposes

        self.backend.add_new_ride(user_id=uid, start_location_lat=start_location_lat,
                                  start_location_lng=start_location_lng, end_location_lat=end_location_lat,
                                  end_location_lng=end_location_lng,
                                  exit_time=exit_time, exit_date=exit_date,
                                  num_of_riders_capacity=num_of_riders_capacity, cost=cost, ride_kind=ride_kind)

        success_message = "Succeeded creating a new ride!.\n"
        pop_message_box('Signup Succeeded', success_message)
        self.set_after_login_window()

    def close_passengers_field_and_set_button(self):
        """
        the method close and open the necessary fields inthe layout.
        """
        if self.text_field_passengers.text() != '':
            self.button_set_calender_window.show()
            self.calendar.hide()
            self.next_button.hide()
            self.button_set_time_window.show()
            self.text_field_hours.hide()
            self.text_field_minutes.hide()
            self.button_set_time.hide()
            self.button_select_cost.show()
            self.text_field_cost.hide()
            self.button_set_cost.hide()
            self.button_select_riders_amount.show()
            self.text_field_passengers.hide()
            self.button_set_riders_amount.hide()

            self.button_select_riders_amount.setText('6. Select Passengers Amount  √')
            self.button_add_new_ride.setDisabled(False)

    def open_passengers_field_and_set_button(self):
        """
        the method close and open the necessary fields inthe layout.
        """
        self.button_set_calender_window.show()
        self.calendar.hide()
        self.next_button.hide()
        self.button_set_time_window.show()
        self.text_field_hours.hide()
        self.text_field_minutes.hide()
        self.button_set_time.hide()
        self.button_select_cost.show()
        self.text_field_cost.hide()
        self.button_set_cost.hide()
        self.button_select_riders_amount.hide()
        self.text_field_passengers.show()
        self.button_set_riders_amount.show()

    def close_cost_field_and_button(self):
        """
        the method close and open the necessary fields inthe layout.
        """
        if self.text_field_cost.text() != '':
            self.button_set_calender_window.show()
            self.calendar.hide()
            self.next_button.hide()
            self.button_set_time_window.show()
            self.text_field_hours.hide()
            self.text_field_minutes.hide()
            self.button_set_time.hide()
            self.button_select_cost.show()
            self.text_field_cost.hide()
            self.button_set_cost.hide()
            self.button_select_riders_amount.show()
            self.text_field_passengers.hide()
            self.button_set_riders_amount.hide()

            self.button_select_cost.setText('5. Select Cost Per Person  √')
            self.button_select_riders_amount.setDisabled(False)

    def show_cost_field_and_button(self):
        """
        the method close and open the necessary fields inthe layout.
        """
        self.button_set_calender_window.show()
        self.calendar.hide()
        self.next_button.hide()
        self.button_set_time_window.show()
        self.text_field_hours.hide()
        self.text_field_minutes.hide()
        self.button_set_time.hide()
        self.button_select_cost.hide()
        self.text_field_cost.show()
        self.button_set_cost.show()
        self.button_select_riders_amount.show()
        self.text_field_passengers.hide()
        self.button_set_riders_amount.hide()

    def set_cost_field(self):
        """
        the generates a an input text field for the cost.
        :return: text field object.
        """
        # create hours field
        text_field = QLineEdit()
        font_size = text_field.font()
        font_size.setPointSize(12)
        text_field.setFont(font_size)
        text_field.setFixedWidth(380)
        text_field.hide()

        return text_field

    def set_hours_times_fields(self, row: int) -> tuple:
        """
        the function generates a text input of hours and minutes and add it
        to the layout for a given row.
        :param row: int. the row to insert the widgets.
        :return: tuple. text field objects.
        """
        # set validators to the hour and minute fields
        hours_validator = QIntValidator(0, 23, self)
        minutes_validator = QIntValidator(0, 60, self)

        # create hours field
        text_field_hours = QLineEdit()
        font_size = text_field_hours.font()
        font_size.setPointSize(12)
        text_field_hours.setFont(font_size)
        text_field_hours.setFixedWidth(185)
        text_field_hours.setValidator(hours_validator)
        text_field_hours.setMaxLength(2)
        text_field_hours.setPlaceholderText('Hours 00 - 23')
        self.layout.addWidget(text_field_hours, row, 0)
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
        self.layout.addWidget(text_field_minutes, row, 1)
        text_field_minutes.hide()

        return text_field_hours, text_field_minutes

    def set_time_fields(self):
        """
        the method close and open the necessary fields inthe layout.
        """
        self.button_set_calender_window.show()
        self.calendar.hide()
        self.next_button.hide()
        self.button_set_time_window.hide()
        self.text_field_hours.show()
        self.text_field_minutes.show()
        self.button_set_time.show()
        self.button_select_cost.show()
        self.text_field_cost.hide()
        self.button_set_cost.hide()
        self.button_select_riders_amount.show()
        self.text_field_passengers.hide()
        self.button_set_riders_amount.hide()

    def close_time_fields_and_button(self):
        """
        the method close and open the necessary fields in the layout.
        """
        if self.text_field_hours.text() != '' and self.text_field_minutes.text() != '':
            self.button_set_calender_window.show()
            self.calendar.hide()
            self.next_button.hide()
            self.button_set_time_window.show()
            self.text_field_hours.hide()
            self.text_field_minutes.hide()
            self.button_set_time.hide()
            self.button_select_cost.show()
            self.text_field_cost.hide()
            self.button_set_cost.hide()
            self.button_select_riders_amount.show()
            self.text_field_passengers.hide()
            self.button_set_riders_amount.hide()

            self.button_set_time_window.setText('4. Select Exit Time  √')
            self.button_select_cost.setDisabled(False)

    def set_map_loc_selector(self):
        """
        the method assign in the Map Window a new start location
        is not selected yet or reselected and opn the map window.
        """
        self.map.is_chose_start_location = False
        self.map.show_map()

    def set_map_dest_selector(self):
        """
        the method assign in the Map Window a new destination
        is not selected yet or reselected and opn the map window.
        """
        self.map.is_chose_start_location = True
        self.map.show_map()

    def show_calender(self):
        """
        the method close and open the necessary fields in the layout.
        """
        self.button_set_calender_window.hide()
        self.calendar.show()  # 3
        self.next_button.show()  # 4
        self.button_set_time_window.show()  # 5
        self.text_field_hours.hide()  # 6.1
        self.text_field_minutes.hide()  # 6.2
        self.button_set_time.hide()  # 7
        self.button_select_cost.show()  # 8
        self.text_field_cost.hide()  # 9
        self.button_set_cost.hide()  # 10
        self.button_select_riders_amount.show()  # 11
        self.text_field_passengers.hide()  # 12
        self.button_set_riders_amount.hide()  # 13

    def set_calender(self):
        """
        the method generates the calender widget to show to the user
        when it necessary to him insert a certain date
        """
        # set calendar
        my_calendar = QCalendarWidget(self)
        # self.calendar.move(112, 112)
        my_calendar.setGridVisible(True)
        # self.calendar.setGeometry(100, 180, 200, 150)
        # self.calendar.setGeometry(50, 50, 50, 50)
        my_calendar.setFixedWidth(380)
        my_calendar.setFixedHeight(200)
        now = datetime.datetime.today()
        currentMonth = now.month
        currentYear = now.year
        currentDay = now.day
        my_calendar.setMinimumDate(QDate(currentYear, currentMonth, currentDay))
        my_calendar.clicked.connect(self.save_date)

        return my_calendar

    def close_calender(self):
        """
        the method close and open the necessary fields in the layout.
        """
        if self.selected_date != None:
            self.button_set_calender_window.show()  # 2
            self.calendar.hide()  # 3
            self.next_button.hide()  # 4
            self.button_set_time_window.show()  # 5
            self.text_field_hours.hide()  # 6.1
            self.text_field_minutes.hide()  # 6.2
            self.button_set_time.hide()  # 7
            self.button_select_cost.show()  # 8
            self.text_field_cost.hide()  # 9
            self.button_set_cost.hide()  # 10
            self.button_select_riders_amount.show()  # 11
            self.text_field_passengers.hide()  # 12
            self.button_set_riders_amount.hide()  # 13

            self.button_set_calender_window.setText('3. Select Exit Date  √')
            self.button_set_time_window.setDisabled(False)

            self.setLayout(self.layout)

    def open_search_window(self):
        """
        search window. the method show to the user what the search window with all the required
        fields he need to fill for finding a ride that fits his needs.
        """
        self.clean_layout()
        self.map.is_search = True

        # destination button
        self.button_destination_search = generate_button('1. Select Destination')
        self.button_destination_search.clicked.connect(self.set_map_dest_selector)

        self.map.set_new_ride_on_click()

        self.map.clean_selected_locations()
        self.layout.addWidget(self.button_destination_search, 0, 0)

        # select date button
        self.button_set_calender_window_search = generate_button('2. Select Date')
        self.button_set_calender_window_search.clicked.connect(self.show_calender_search)
        self.button_set_calender_window_search.setDisabled(True)
        self.layout.addWidget(self.button_set_calender_window_search, 1, 0)

        # set calender at row 3 at the layout
        self.calendar = self.set_calender()
        self.layout.addWidget(self.calendar, 2, 0)
        self.calendar.hide()

        # 'set date' button
        self.button_set_date_search = generate_button('Choose Date')
        self.button_set_date_search.clicked.connect(self.close_calender_search)
        self.layout.addWidget(self.button_set_date_search, 3, 0)
        self.button_set_date_search.hide()

        self.button_select_exit_time = generate_button('3. Select Exit Time')
        self.button_select_exit_time.clicked.connect(self.open_time_fields_search)
        self.button_select_exit_time.setDisabled(True)
        self.layout.addWidget(self.button_select_exit_time, 4, 0)

        # set hours and minutes fields fields row 5,1 and 5,1 in the layout
        self.text_field_hours_search, self.text_field_minutes_search = self.set_hours_times_fields(row=5)

        # 'set time' button
        self.button_set_time_search = generate_button('Set Time')
        self.button_set_time_search.clicked.connect(self.close_time_fields_search)
        self.layout.addWidget(self.button_set_time_search, 6, 0)
        self.button_set_time_search.hide()

        # select radius button
        self.button_select_radius = generate_button('4. Set Maximal Radius From Destination')
        self.button_select_radius.clicked.connect(self.open_radius_field_search)
        self.button_select_radius.setDisabled(True)
        self.layout.addWidget(self.button_select_radius, 7, 0)

        # radius field
        self.text_field_radius = self.set_cost_field()
        distance_validator = QIntValidator(0, 1000, self)
        self.text_field_radius.setValidator(distance_validator)
        self.text_field_radius.setMaxLength(4)
        self.text_field_radius.setPlaceholderText('0 - 1000 meters')
        self.layout.addWidget(self.text_field_radius, 8, 0)
        self.text_field_radius.hide()

        # 'set radius' button
        self.button_set_radius = generate_button('Set')
        self.button_set_radius.clicked.connect(self.close_radius_field_search)
        self.layout.addWidget(self.button_set_radius, 9, 0)
        self.button_set_radius.hide()

        # search button
        self.button_search = generate_button('Search')
        self.button_search.clicked.connect(self.search_rides)
        self.button_search.setDisabled(True)
        self.layout.addWidget(self.button_search, 10, 0)

        # back to after login window
        self.button_back_to_after_login_window = generate_button('back')
        self.button_back_to_after_login_window.clicked.connect(self.set_after_login_window)
        self.layout.addWidget(self.button_back_to_after_login_window, 11, 0)

        self.setLayout(self.layout)

    def signal_enable_select_date_search(self):
        """
        signal method. the method triggers once a destination if filled by the user.
        """
        self.button_destination_search.setText('1. Select Destination  √')
        self.button_set_calender_window_search.setDisabled(False)

    def show_calender_search(self):
        """
        the method close and open the necessary fields in the layout.
        """
        self.button_set_calender_window_search.hide()  # 1
        self.calendar.show()  # 2
        self.button_set_date_search.show()  # 3
        self.button_select_exit_time.show()  # 4
        self.text_field_hours_search.hide()  # 5.1
        self.text_field_minutes_search.hide()  # 5.1
        self.button_set_time_search.hide()  # 6
        self.button_select_radius.show()  # 7
        self.text_field_radius.hide()  # 8
        self.button_set_radius.hide()  # 9

    def close_calender_search(self):
        """
        the method close and open the necessary fields in the layout.
        """
        if self.selected_date is not None:
            self.button_set_calender_window_search.show()  # 1
            self.calendar.hide()  # 2
            self.button_set_date_search.hide()  # 3
            self.button_select_exit_time.show()  # 4
            self.text_field_hours_search.hide()  # 5.1
            self.text_field_minutes_search.hide()  # 5.1
            self.button_set_time_search.hide()  # 6
            self.button_select_radius.show()  # 7
            self.text_field_radius.hide()  # 8
            self.button_set_radius.hide()  # 9

            self.button_set_calender_window_search.setText('2. Select Date  √')
            self.button_select_exit_time.setDisabled(False)

    def open_time_fields_search(self):
        """
        the method close and open the necessary fields in the layout.
        """
        self.button_set_calender_window_search.show()  # 1
        self.calendar.hide()  # 2
        self.button_set_date_search.hide()  # 3
        self.button_select_exit_time.hide()  # 4
        self.text_field_hours_search.show()  # 5.1
        self.text_field_minutes_search.show()  # 5.1
        self.button_set_time_search.show()  # 6
        self.button_select_radius.show()  # 7
        self.text_field_radius.hide()  # 8
        self.button_set_radius.hide()  # 9

    def close_time_fields_search(self):
        """
        the method close and open the necessary fields in the layout.
        """
        if self.text_field_hours_search.text() != '' and self.text_field_minutes_search.text() != '':
            self.button_set_calender_window_search.show()  # 1
            self.calendar.hide()  # 2
            self.button_set_date_search.hide()  # 3
            self.button_select_exit_time.show()  # 4
            self.text_field_hours_search.hide()  # 5.1
            self.text_field_minutes_search.hide()  # 5.1
            self.button_set_time_search.hide()  # 6
            self.button_select_radius.show()  # 7
            self.text_field_radius.hide()  # 8
            self.button_set_radius.hide()  # 9

            self.button_select_exit_time.setText('3. Select Exit Time  √')
            self.button_select_radius.setDisabled(False)

    def open_radius_field_search(self):
        """
        the method close and open the necessary fields in the layout.
        """
        self.button_set_calender_window_search.show()  # 1
        self.calendar.hide()  # 2
        self.button_set_date_search.hide()  # 3
        self.button_select_exit_time.show()  # 4
        self.text_field_hours_search.hide()  # 5.1
        self.text_field_minutes_search.hide()  # 5.1
        self.button_set_time_search.hide()  # 6
        self.button_select_radius.hide()  # 7
        self.text_field_radius.show()  # 8
        self.button_set_radius.show()  # 9

    def close_radius_field_search(self):
        """
        the method close and open the necessary fields in the layout.
        """
        if self.text_field_radius.text() != '':
            self.button_set_calender_window_search.show()  # 1
            self.calendar.hide()  # 2
            self.button_set_date_search.hide()  # 3
            self.button_select_exit_time.show()  # 4
            self.text_field_hours_search.hide()  # 5.1
            self.text_field_minutes_search.hide()  # 5.1
            self.button_set_time_search.hide()  # 6
            self.button_select_radius.show()  # 7
            self.text_field_radius.hide()  # 8
            self.button_set_radius.hide()  # 9

            self.button_search.setDisabled(False)
            self.button_select_radius.setText('4. Set Maximal Radius From Destination  √')

    def search_rides(self):
        """
        the function search a relevant rides that fits the user need by the inmformation
        he filled.
        """
        uid = self.current_user_id
        end_location_lat = self.map.search_location.latLng[0]
        end_location_lng = self.map.search_location.latLng[1]
        exit_time = set_time_from_user(self.text_field_hours_search.text(), self.text_field_minutes_search.text())
        exit_date = set_date_from_user(day=self.selected_date[2], month=self.selected_date[1],
                                       year=self.selected_date[0])
        radius = self.text_field_radius.text()

        res = self.backend.search_ride(user_id=uid, end_location_lat=end_location_lat,
                                       end_location_lng=end_location_lng, exit_time=exit_time, exit_date=exit_date,
                                       radius=radius)
        if len(res) > 0:
            self.set_after_login_window()
            self.map.show_rides_on_map(res)
            self.checkbox.open_checkbox_join_ride()
        else:
            self.set_after_login_window()
            no_rides_found_message = "No Results Found!\n"
            pop_message_box('Search Results', no_rides_found_message)

    def join_ride(self):
        """
        the method add the user to an existing ride.
        """
        self.map.mapWidget.hide()
        self.map.hide()

        is_succeeded, error = self.backend.join_ride(self.current_user_id, self.checkbox.text_field.text())
        if is_succeeded:
            pop_message_box('Join Ride', 'You successfully joined the ride!')
        else:
            pop_message_box('Join Ride', error)

    def save_date(self):
        """
        the method saves the chosen date by the user.
        """
        self.selected_date = self.calendar.selectedDate().getDate()


class MapWindow(QWidget):
    """
    the class shows the map to search and add rides.
    """
    first_signal = pyqtSignal()
    second_signal = pyqtSignal()
    third_signal = pyqtSignal()

    def __init__(self, parent, *args):
        """
        constructor.
        """
        # Setting up the widgets and layout
        super(MapWindow, self).__init__(*args)

        self.first_signal.connect(parent.first_signal.emit)
        self.second_signal.connect(parent.second_signal.emit)
        self.third_signal.connect(parent.third_signal.emit)

        self.mapWidget = MapWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.mapWidget)
        self.setWindowTitle('BGRide Map')
        self.setWindowIcon(QIcon("assets/icon.png"))

        self.setLayout(self.layout)
        self.current_lat = None
        self.current_lang = None

        self.search_location = None
        self.is_search = False

        self.locations = {}

        self.places = []

        self.is_chose_start_location = False

        # Working with the maps with pyqtlet
        self.map = L.map(self.mapWidget)
        self.map.setView([31.256974278389507, 34.79832234475968], 14)

        self.is_unset_click_map = True
        self.set_new_ride_on_click()

        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
        self.marker = L.marker([75.262070, 34.798280], {'opacity': 0})
        self.map.addLayer(self.marker)

    def show_map(self):
        """
        the method shows to the user the map
        :return:
        """
        self.mapWidget.show()
        self.show()

    def get_lat_and_lng(self) -> tuple:
        """
        the method return the coordinates of the chosen spot in the map.
        :return tuple (int, int): the land and lat coordinates.
        """
        if self.current_lat is not None:
            return self.current_lat, self.current_lang

    def check_selected_location(self) -> bool:
        """
        the method checks if the user already selected a start location.
        :return: boolean. True if he does. else - False.
        """
        if self.current_lang is None:
            return False
        self.hide()
        self.parent.set_selected_location(self.current_lat, self.current_lang)
        self.current_lang = None
        self.current_lat = None
        return True

    def check_selected_destination(self) -> bool:
        """
        the method checks if the user already selected a destionation.
        :return: boolean. True if he does. else - False.
        """
        if self.current_lang is None:
            return False
        self.hide()
        self.parent.set_selected_destination(self.current_lat, self.current_lang)
        self.current_lang = None
        self.current_lat = None
        return True

    def set_new_ride_on_click(self):
        """
        listener method. the method triggers once a clicked as been made on the map.
        """
        if self.is_unset_click_map:
            self.map.clicked.connect(lambda x: self.set_lng_and_lat(x))
            self.is_unset_click_map = False

    def unset_new_ride_on_click(self):
        """
        the method unbind the clicker listener from the map.
        """
        if not self.is_unset_click_map:
            self.map.clicked.disconnect()
            self.is_unset_click_map = True

    def set_lng_and_lat(self, location_pressed):
        """
        the method triggers once has been made on the map.
        """
        # get current x,y of user's mouse press
        lat = location_pressed['latlng']['lat']
        lang = location_pressed['latlng']['lng']

        if self.is_search is True:
            if self.search_location is not None:
                self.map.removeLayer(self.search_location)
                self.search_location = None

            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
            self.search_location = L.marker([lat, lang], {'opacity': 0.7})
            self.map.addLayer(self.search_location)
            self.third_signal.emit()

        # a select start location has chosen
        elif not self.is_chose_start_location:
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

        button_reply = QMessageBox.question(self, 'Message', "Is it your desired location?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if button_reply == QMessageBox.Yes:
            self.mapWidget.hide()
            self.hide()

    def show_rides_on_map(self, places_list):
        """
        the method receives a list of coordinates by lat and lang and mark the map with the data of the rides.
        :param places_list: list. a list of the rides and their info.
        """
        self.clean_selected_locations()

        for place in places_list:
            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)  # .on('onClick', self.onClick)
            marker = L.marker([place[4], place[5]], {'opacity': 1})
            self.places.append(marker)

            ride_purpose = '<b>Ride Purpose:</b> '

            if place[11] == '':
                pass
            elif ',' in place[11]:
                for purpose in place[11].split(','):
                    ride_purpose = f'{ride_purpose} {purpose},'
                ride_purpose = f'{ride_purpose[:-1]}<br>'
            else:
                ride_purpose = f'{ride_purpose} {place[11]}<br>'
            time = list(place[6])
            time[2] = ':'

            string_info = f"<b>Ride id: {place[0]}</b><br>" \
                          f"<b>Ride from: </b> {place[12]}<br>" \
                          f"<b>to: </b> {place[13]}<br>" \
                          f"<b>Exit Date: </b>{place[7]}<br>" \
                          f"<b>Exit Time: </b> {''.join(time)}<br>" \
                          f"<b>Cost: </b>{place[10]}₪<br>" \
                          f"<b>{place[9] - place[8]}</b> available seats left<br>" \
                          f"{ride_purpose}" \
                          f"<b>Contact Name:</b> {place[14]}<br>" \
                          f"<b>Phone Number:</b> {place[15]}<br>"
            marker.bindPopup(string_info)
            self.map.addLayer(marker)

        self.unset_new_ride_on_click()
        self.show_map()

    def clean_selected_locations(self):
        """
        the method removes from the map all the locations on the map.
        """
        for key in self.locations.keys():
            self.map.removeLayer(self.locations[key])

        if self.search_location is not None:
            self.map.removeLayer(self.search_location)
            self.search_location = None

        for marker in self.places:
            self.map.removeLayer(marker)

        self.places = []


class CheckBox(QWidget):
    """
    checkbox class. the class is used to show/receive data to/from the user.
    """
    checkbox_signal = pyqtSignal()
    select_ride_signal = pyqtSignal()

    def __init__(self, parent, *args):
        super(CheckBox, self).__init__(*args)
        """
        constructor.
        """

        # set background and icon to the checkbox window
        self.set_background_image()
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.setWindowTitle('Ride Purposes')

        # set signal to MainWindow
        self.checkbox_signal.connect(parent.checkbox_signal)
        self.select_ride_signal.connect(parent.select_ride_signal)

        # set lists
        self.chosen_purposes = []
        self.check_box_list = []
        self.checkbox_layout = QVBoxLayout()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.button_ok = None
        self.label = None
        self.text_field = None

    def open_checkbox_purposes(self, potential_ride_purpose_list: list, destination_address: str):
        """
        the method open a checkbox to ask the user what is the purpose of his ride.
        :param potential_ride_purpose_list: list. list of all the amenities in the area of his destination.
        :param destination_address: String. containg the lat and lang of the user destination.
        """
        self.setWindowTitle('Ride Purposes')

        self.clearLayout(self.checkbox_layout)

        self.chosen_purposes = []
        self.check_box_list = []

        for potential_ride_purpose in potential_ride_purpose_list:
            check_box = QCheckBox(f' {potential_ride_purpose}')
            check_box.setStyleSheet('QCheckBox{'
                                    'spacing:px;'
                                    'font-size:15px;}')
            self.check_box_list.append(check_box)

        self.label = QLabel(f'<font size="4">What is your Ride Purpose:<br>'
                            f'in {destination_address} ?</font>')
        self.checkbox_layout.addWidget(self.label)

        for check_box in self.check_box_list:
            self.checkbox_layout.addWidget(check_box)

        # create 'OK' button
        self.button_ok = generate_button('Ok')
        self.button_ok.setFixedWidth(100)
        self.button_ok.clicked.connect(self.get_selected_purposes)

        self.checkbox_layout.addWidget(self.button_ok)

        self.setLayout(self.checkbox_layout)
        self.show()

    def open_checkbox_join_ride(self):
        """
        the message opens a checkbox to receive from the user a ride id that the user would like to join.
        """
        self.clearLayout(self.checkbox_layout)
        self.setWindowTitle('Join Ride')

        self.label = QLabel(f'<font size="4">Please Insert the <b>ride id</b> to join:<br>'
                            f'the ride you interested in</font>')

        self.text_field = QLineEdit()
        font_size = self.text_field.font()
        font_size.setPointSize(10)
        self.text_field.setFont(font_size)
        self.text_field.setFixedWidth(185)
        self.text_field.setMaxLength(4)
        self.text_field.setPlaceholderText('ride id')
        only_int = QIntValidator()
        self.text_field.setValidator(only_int)

        self.button_ok = generate_button('Ok')
        self.button_ok.setFixedWidth(100)
        self.button_ok.clicked.connect(self.get_selected_ride)

        self.checkbox_layout.addWidget(self.label)
        self.checkbox_layout.addWidget(self.text_field)
        self.checkbox_layout.addWidget(self.button_ok)

        self.setLayout(self.checkbox_layout)
        self.show()

    def get_selected_ride(self):
        """
        the method close and signal the main window once the user chose a
        ride to join to.
        """
        if self.text_field.text() != '':
            # close window
            self.hide()
            # signal MainWindow
            self.select_ride_signal.emit()

    def clearLayout(self, layout):
        """
        the method cleans the checkbox from all the widgets in it.
        :param layout: the checkbox layout.
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def get_selected_purposes(self):
        """
        the method triggers once the user chose his ride purposes and signal about it to
        the main window of the app.
        """
        if len(self.check_box_list) == 0:
            # close checkbox
            self.hide()

            # signal MainWindow
            self.checkbox_signal.emit()

        else:
            for check_box in self.check_box_list:
                if check_box.isChecked():
                    self.chosen_purposes.append(check_box.text())

            if len(self.chosen_purposes) != 0:
                # close checkbox
                self.hide()

                # signal MainWindow
                self.checkbox_signal.emit()

    def set_background_image(self):
        """
        the method sets the image background of the checkbox.
        """
        # set background
        oImage = QImage("assets/background.jpg")
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(oImage))
        self.setPalette(palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec_())
