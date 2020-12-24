from azureDatabase import AzureDatabase
import googlemaps
from math import radians, cos, sin, asin, sqrt
import datetime


class Backend:

    def __init__(self):
        self.db = AzureDatabase()

        self.g_maps_api_key = 'AIzaSyD2mZwWRBcD3vbRFmvtJzcQCyCpNpzkrws'

        self.g_maps = googlemaps.Client(key=self.g_maps_api_key)

        self.rise_purposes_list = ['bakery', 'restaurant', 'pharmacy', 'bank', 'atm', 'park', 'pet_store',
                                   'police', 'doctor', 'supermarket', 'gym', 'hospital', 'university', 'synagogue',
                                   'stadium', 'night_club', 'library', 'home_goods_store', 'movie_theater']

    def login(self, username, password) -> tuple:

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

    def check_if_username_taken(self, username):
        terms_dict = {'username': username}

        results = self.db.select_query('Users', terms_dict)

        if len(results) == 1:
            return False

        return True

    def register(self, username, first_name, last_name, password, email, phone_number) -> bool:

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
                    radius: str) -> bool:

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
        return results_after_radius_check

    def join_ride(self, user_id_passenger: int, ride_id: int,
                  ride_kind: list) -> tuple:  # TODO: the ride kind comes in list or string??
        terms_dict = {'rid': ride_id}

        rides_results = self.db.select_query('Rides', terms_dict)

        if len(rides_results) != 1:
            return False, "Couldn't find the requested ride. Please try again."

        ride = rides_results[0]

        riders_results = self.db.select_query('Riders', terms_dict)

        for current_passenger in riders_results:
            if current_passenger[1] == user_id_passenger:
                return False, "You already assigned to this ride."

        current_passengers_amount = ride[5]
        passengers_capacity = ride[6]
        if current_passengers_amount >= passengers_capacity:
            return False, "This ride is already full. Please try another ride."

        values_update_dict = {'numOfRiders': current_passengers_amount + 1}

        if not self.db.update_query('Rides', values_update_dict, terms_dict):
            return False, "Failed adding you to the ride. Please try again later."

        terms_dict['uid'] = user_id_passenger

        if not self.db.insert_query('Riders', terms_dict):
            return False, "Failed adding you to the ride. Please try again later."

        return True, "You have been successfully joined the ride!"

    def get_ride_purposes(self, lat, lng) -> list:
        potential_ride_purpose_list = []
        for potential_purpose in self.rise_purposes_list:
            res = self.g_maps.places_nearby(location=f'{lat},{lng}', radius=200, open_now=False,
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
    return c * r * 1000 < int(max_dist)


def filter_by_time(results, date_user, hour_user):
    filtered_res = []
    for res in results:
        time_user_earlier = datetime.time(int(hour_user[:2]) + 2, int(hour_user[3:]), 00)
        time_user_later = datetime.time(int(hour_user[:2]) - 2, int(hour_user[3:]), 00)
        res_time = datetime.time(int(res[6][:2]), int(res[6][3:]), 00)
        # check if the time is in range of +-2 hours from the user time
        if is_time_between(time_user_later, time_user_earlier, res_time):
            filtered_res.append(res)

    return filtered_res


def is_time_between(begin_time, end_time, check_time):
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def filter_by_radius(results_after_date_check, x_user, y_user, radius):
    results = []
    for res in results_after_date_check:
        x = float(res[4])
        y = float(res[5])
        if check_if_close_enough(x, y, x_user, y_user, radius):
            results.append(res)
    return results
