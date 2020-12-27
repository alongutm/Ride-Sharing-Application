import os
import folium
import datetime
import googlemaps
import pandas as pd
from folium.plugins import HeatMap
from azureDatabase import AzureDatabase
from math import radians, cos, sin, asin, sqrt


class Backend:
    """
    this class is responsible for all the application logic.
    """
    def __init__(self):
        """
        constructor
        """
        self.db = AzureDatabase()

        self.g_maps_api_key = 'AIzaSyD2mZwWRBcD3vbRFmvtJzcQCyCpNpzkrws'

        self.g_maps = googlemaps.Client(key=self.g_maps_api_key)

        self.rise_purposes_list = ['bakery', 'restaurant', 'pharmacy', 'bank', 'atm', 'park', 'pet_store',
                                   'police', 'doctor', 'supermarket', 'gym', 'hospital', 'university', 'synagogue',
                                   'stadium', 'night_club', 'library', 'home_goods_store', 'movie_theater', 'bar',
                                   'train_station']

    def login(self, username: str, password: str) -> tuple:
        """
        the method check in the database if the user exist and if the user the password fits the the given user.
        the method also checks if the given user have admin privileges and signal about it if it does.
        :param username: String. the inserted username.
        :param password: String. the isnerted password.
        :return: tuple (bool, bool, int). first boolean - if the user and the password are correct.
        second boolean - if the user is admin user.
        third value - the user id of the user.
        """

        terms_dict = {'username': username, 'password': password}
        results = self.db.select_query('Users', terms_dict)

        if len(results) == 0:
            return False, False

        user_id = results[0][0]
        # check if the user is an administrator
        # query = f"SELECT * FROM Administrators WHERE uid='{user_id}'"

        terms_dict_2 = {'uid': user_id}

        results = self.db.select_query('Administrators', terms_dict_2)
        is_admin = True if len(results) == 1 else False

        if is_admin:
            return True, True, user_id

        else:
            return True, False, user_id

    def check_if_username_taken(self, username) -> bool:
        """
        the method chceks in the database if the given username is already taken by another user.
        :param username: String. the inserted username.
        :return: boolean. True - of the user already taken. else - False.
        """
        terms_dict = {'username': username}

        results = self.db.select_query('Users', terms_dict)

        if len(results) == 1:
            return False

        return True

    def register(self, username: str, first_name: str, last_name: str, password: str, email: str, phone_number: str) -> bool:
        """
        the method register the new user to the database and return True if it does.
        :param username: String. the inserted username.
        :param first_name: String. the inserted first name.
        :param last_name: String. the inserted last name.
        :param password: String. the inserted password.
        :param email: String. the inserted rmail.
        :param phone_number: String. the inserted phone number.
        :return: boolean. True - if succeeded. else - return False.
        """

        values_dict = {'username': username,
                       'firstName': first_name,
                       'lastName': last_name,
                       'password': password,
                       'email': email,
                       'phoneNumber': phone_number}

        if not self.db.insert_query('Users', values_dict):
            return False

        res = self.db.select_query('Users', {'username': username})

        user_id = res[0][0]

        if not self.db.insert_query('Preferences', {'uid': user_id}):
            return False

        return True

    def add_new_ride(self, user_id: int, start_location_lat: str, start_location_lng: str, end_location_lat: str,
                     end_location_lng: str, exit_time: str, exit_date: str, num_of_riders_capacity: list,
                     cost: int, ride_kind: list) -> bool:
        """
        the method add a new ride to the database and return True if succeeded.
        :param user_id: int. the user id who inserted the new ride.
        :param start_location_lat: String. the start location lat the user chose.
        :param start_location_lng: String. the start location lang the user chose.
        :param end_location_lat: String. the destination lat the user chose.
        :param end_location_lng: String. the destination lang the user chose.
        :param exit_time: String. the exit time the user chose.
        :param exit_date: String. the exit Date the user chose.
        :param num_of_riders_capacity: String. the amount of riders the user want take with.
        :param cost: String. the cost of the ride the user ask for for every passenger.
        :param ride_kind: list. a list of all the amenities the user want to visit.
        :return: boolean. True - if succeeded. else - return False.
        """

        ride_kind_str = ','.join(ride_kind)

        values_dict = {'uid': user_id,
                       'start_location_lat': start_location_lat,
                       'start_location_lng': start_location_lng,
                       'end_location_lat': end_location_lat,
                       'end_location_lng': end_location_lng,
                       'exitTime': exit_time,
                       'exitDate': exit_date,
                       'numOfRiders': 0,
                       'numOfRidersCapacity': num_of_riders_capacity,
                       'cost': cost,
                       'rideKind': ride_kind_str
                       }

        if not self.db.insert_query('Rides', values_dict):
            return False

        if not self.db.update_query_increment('Preferences', ride_kind, {'uid': user_id}):
            return False

        return True

    def search_ride(self, user_id: int, end_location_lat: float, end_location_lng: float, exit_time: str, exit_date: str,
                    radius: str) -> list:
        """
        the method search for potential rides in the database for the user.
        :param user_id: the id if the user that search for rides to join.
        :param end_location_lat: String. the destination lat the user want to reach.
        :param end_location_lng: String. the destination lang the user want to reach.
        :param exit_time: String. the exit date the user need the ride.
        :param exit_date: String. the exit time the user need the ride.
        :param radius: String. the maximal radius the user will agree to "settle"
        :return: list. a list of all the potential rides that fits the user need for a ride.
        """

        # select rides with the user's date
        results = self.db.select_query('Rides', {'exitDate': exit_date})

        # filtering rides by 2 hours before and after the time the user entered
        results_after_date_check = filter_by_time(results, exit_date, exit_time)

        # filtering rides by the maximal accepted radius away from the user's destination
        results_after_radius_check = filter_by_radius(
            results_after_date_check,
            end_location_lat,
            end_location_lng,
            radius
        )

        results_list = [list(res) for res in results_after_radius_check]

        # get rider name and phone number and name address
        for res in results_list:
            start_location_address = self.get_address_by_lan_lng(res[2], res[3])
            end_location_address = self.get_address_by_lan_lng(res[4], res[5])

            res.append(start_location_address)
            res.append(end_location_address)

            select_query_res = self.db.select_query('Users', {'uid': res[1]})

            res.append(f'{select_query_res[0][2]} {select_query_res[0][3]}')
            res.append(f'{select_query_res[0][6]}')

        return results_list

    def join_ride(self, user_id_passenger: int, ride_id: int) -> tuple:
        """
        the method add a user to a an existing ride.
        the method return True or False if it succeeded to join the ride or not
        with a suitable message.
        :param user_id_passenger: int. the user id that want to join the ride.
        :param ride_id: int. the ride id the user want to join to.
        :return: tuple (bool, String). first value - True of the succeeded joining the ride - else False.
        second value - a suitable message the pop to the user.
        """
        terms_dict = {'rid': ride_id}

        rides_results = self.db.select_query('Rides', terms_dict)

        if len(rides_results) != 1:
            return False, "Couldn't find the requested ride. Please try again."

        ride = rides_results[0]

        riders_results = self.db.select_query('Riders', terms_dict)

        for current_passenger in riders_results:
            if current_passenger[1] == user_id_passenger:
                return False, "You already assigned to this ride."

        current_passengers_amount = ride[8]
        passengers_capacity = ride[9]
        if current_passengers_amount >= passengers_capacity:
            return False, "This ride is already full. Please try another ride."

        values_update_dict = {'numOfRiders': current_passengers_amount + 1}

        if not self.db.update_query('Rides', values_update_dict, terms_dict):
            return False, "Failed adding you to the ride. Please try again later."

        terms_dict['uid'] = user_id_passenger

        if not self.db.insert_query('Riders', terms_dict):
            return False, "Failed adding you to the ride. Please try again later."

        preferences_ride = []
        if ride[11] != '':
            if ',' in ride[11]:
                preferences_ride = list(ride[11].split(','))
            else:
                preferences_ride.append(ride[11])

            if not self.db.update_query_increment('Preferences', preferences_ride, {'uid': user_id_passenger}):
                return False, "Failed adding you to the ride. Please try again later."

        return True, "You have been successfully joined the ride!"

    def get_all_users(self) -> pd.DataFrame:
        """
        the method returns in a data frame all the users that exist in the database.
        :return: data frame. a data frame of all the users in the database.
        """
        results = self.db.select_query('Users, Preferences', terms_dict={'Users.uid': 'Preferences.uid'},
                                       is_string=True)

        columns_list = ['uid', 'username', 'firstName', 'lastName', 'password', 'email', 'phoneNumber', 'uid']
        columns_list = columns_list + self.rise_purposes_list

        results_df = pd.DataFrame([list(list1) for list1 in results], columns=columns_list)

        return results_df

    def get_ride_purposes_from_google_maps(self, lat, lng) -> list:
        potential_ride_purpose_list = []
        for potential_purpose in self.rise_purposes_list:
            res = self.g_maps.places_nearby(location=f'{lat},{lng}', radius=300, open_now=False,
                                            type=potential_purpose)
            if res['status'] == 'OK':
                potential_ride_purpose_list.append(potential_purpose)

        return potential_ride_purpose_list

    def get_address_by_lan_lng(self, lat, lng) -> str:
        results = self.g_maps.reverse_geocode(f'{lat},{lng}')
        for current_res in results:
            if any(char.isdigit() for char in current_res['formatted_address']) and any(
                    c.isalpha() for c in current_res['formatted_address']):
                return current_res['formatted_address']

    def all_rides_heat_maps_folium(self):
        """
        the method creates a heat map of all the users rides they took.
        """
        results = self.db.select_query('Rides, Riders', {'Riders.rid': 'Rides.rid'}, True)
        locations = []
        for res in results:
            locations.append([float(res[4]), float(res[5])])

        base_map = generate_base_map()
        HeatMap(data=locations, radius=22).add_to(base_map)
        # gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
        date = datetime.datetime.now().date()

        if not os.path.isdir('./assets/all_rides_heat_map'):
            os.mkdir('./assets/all_rides_heat_map')

        filepath = f'assets/all_rides_heat_map/{date}.html'
        base_map.save(filepath)
        os.system(f"start chrome {filepath}")
        # webbrowser.open('file://' + filepath)

    def all_rides_by_user_heat_maps_folium(self, user_id: int):
        """
        the method creates a heat map of all the rides a specific user took.
        :param user_id: int. the user id of a specific user the show his heat map.
        """
        terms_dict = {'Riders.rid': 'Rides.rid',
                      'Riders.uid': user_id}
        results = self.db.select_query('Riders, Rides', terms_dict, True)
        locations = []
        for res in results:
            locations.append([float(res[6]), float(res[7])])

        base_map = generate_base_map()
        HeatMap(data=locations, radius=15).add_to(base_map)
        # gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
        date = datetime.datetime.now().date()

        if not os.path.isdir('./assets/users_heat_maps'):
            os.mkdir('./assets/users_heat_maps')

        filepath = f'assets/users_heat_maps/{user_id}_{date}.html'
        base_map.save(filepath)
        os.system(f"start chrome {filepath}")
        # webbrowser.open('file://' + filepath)


def check_if_close_enough(x_loc_main: float, y_loc_main: float, x_loc: float, y_loc: float, max_dist: int):
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
    return c * r * 1000 < int(max_dist)


def filter_by_time(results: list, date_user: str, hour_user: str) -> list:
    """
    the method filters all the results by the date inserted by the user,
    and also filters the time inserted by the user and the rides in a gap of 2 hours between.
    :param results: list. a list of all the results from the database.
    :param date_user: String. the inserted date from the user.
    :param hour_user: String. the inserted time from the user.
    :return: list. a list of all the filtered results.
    """
    filtered_res = []
    for res in results:
        time_user_earlier = datetime.time(int(hour_user[:2]) + 2, int(hour_user[3:]), 00)
        time_user_later = datetime.time(int(hour_user[:2]) - 2, int(hour_user[3:]), 00)
        res_time = datetime.time(int(res[6][:2]), int(res[6][3:]), 00)
        # check if the time is in range of +-2 hours from the user time
        if is_time_between(time_user_later, time_user_earlier, res_time):
            filtered_res.append(res)

    return filtered_res


def is_time_between(begin_time: int, end_time: int, check_time: int) -> bool:
    """
    the methodchecks if a ride time is in the inserted time by the user in a gap of 2 hours between.
    :param begin_time: the earliest time in the 2 hours gap from the time the user inserted.
    :param end_time:the latest time in the 2 hours gap from the time the user inserted
    :param check_time: the exit time of the ride.
    :return: boolean. True - if the the exit time is in the 2 hours gap.
    """
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def filter_by_radius(results_after_date_check: list, x_user: str, y_user: str, radius: str) -> list:
    """
    the method checks if the rides in the list are in the radius the user inserted
    and return a list of the rides that passed the term above.
    :param results_after_date_check: list. a list of rides.
    :param x_user: String. the destination lat the user chose.
    :param y_user: String. the destination lang the user chose.
    :param radius: String. the radius the user agreed to "settle".
    :return: list. a list of filtered rides.
    """
    results = []
    for res in results_after_date_check:
        x = float(res[4])
        y = float(res[5])
        if check_if_close_enough(x, y, x_user, y_user, radius):
            results.append(res)
    return results


def generate_base_map(default_location=[31.26176079969529, 34.7982650268944], default_zoom_start=15):
    """
    the function generates a basic heat map.
    :param default_location: list. a list containing a lat and lang to where to focus on the globe.
    :param default_zoom_start: int. the level of the zoom in the map.
    :return: base map object.
    """
    base_map = folium.Map(location=default_location, control_scale=True, zoom_start=default_zoom_start)
    return base_map
