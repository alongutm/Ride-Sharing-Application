import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
from pyqtlet import L, MapWidget
from math import radians, cos, sin, asin, sqrt


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

def generate_button(button_text):
    button = QPushButton(button_text)
    font_size = button.font()
    font_size.setPointSize(14)
    button.setFont(font_size)
    button.setFixedWidth(380)
    return button


class MapWindow(QWidget):
    def __init__(self, parent_window):
        # Setting up the widgets and layout
        super().__init__()
        self.mapWidget = MapWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.mapWidget)
        self.setWindowTitle('BGRide Map')
        self.setLayout(self.layout)
        # self.button = generate_button('Confirm Location')
        # self.button.clicked.connect(self.check_selected_location)
        self.parent = parent_window
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
        # self.map.show()


    def show_map(self):
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


if __name__ == '__main__':
    a = 3
    # app = QApplication(sys.argv)
    # parent = MainWindow()
    # widget = MapWindow(parent)
    # places = [[2, 3, "Big Beer Sheva", 31.242817, 34.8108412, "16:30", "20/12/20", 1, 3, 20, "Pleasure", "places pick up"],
    #           [3, 1, "Baraka", 31.23931426638609, 34.79268091645712, "22:30", "22/12/20", 1, 3, 25, "Pleasure", "places pick up"]]
    # widget.show_rides_on_map(places)
    #
    # # check_if_close_enough(31.23877283432704, 34.790932878768515, 31.23931426638609, 34.79268091645712, 0.5)
    # sys.exit(app.exec_())
