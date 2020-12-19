import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QPushButton
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


class MapWindow(QWidget):
    def __init__(self):
        # Setting up the widgets and layout
        super().__init__()
        self.mapWidget = MapWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.mapWidget)
        self.setLayout(self.layout)
        self.current_lat = None
        self.current_lang = None
        self.places = []

        # Working with the maps with pyqtlet
        self.map = L.map(self.mapWidget)
        self.map.setView([31.256974278389507, 34.79832234475968], 14)

        # self.set_new_ride_on_click()

        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
        self.marker = L.marker([31.262070, 34.798280], {'opacity': 1})
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
    app = QApplication(sys.argv)
    widget = MapWindow()
    places = [[2, 3, "Big Beer Sheva", 31.242817, 34.8108412, "16:30", "20/12/20", 1, 3, 20, "Pleasure", "places pick up"],
              [3, 1, "Baraka", 31.23931426638609, 34.79268091645712, "22:30", "22/12/20", 1, 3, 25, "Pleasure", "places pick up"]]
    widget.show_rides_on_map(places)
    # check_if_close_enough(31.23877283432704, 34.790932878768515, 31.23931426638609, 34.79268091645712, 0.5)
    sys.exit(app.exec_())
