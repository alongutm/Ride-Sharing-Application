from azureDatabase import AzureDatabase


class Backend:

    def __init__(self):
        self.db = AzureDatabase()

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
            return True, True

        else:
            return True, False

    def register(self, username, first_name, last_name, password, email, phone_number) -> bool:

        terms_dict = {'username': username}

        results = self.db.select_query('Users', terms_dict)

        if len(results) == 1:
            return False

        values_dict = {'username': username,
                       'firstName': first_name,
                       'lastName': last_name,
                       'password': password,
                       'email': email,
                       'phoneNumber': phone_number}

        if not self.db.insert_query('Users', values_dict):
            return False

        return True

    def add_new_ride(self, user_id: int, location: str, exit_time: str, exit_date: str, num_of_riders_capacity: list, cost: int, ride_kind: list, pick_up_places: list) -> bool:

        values_dict = {'uid': user_id,
                       'location': location,
                       'exitTime': exit_time,
                       'exitDate': exit_date,
                       'numOfRiders': 0,
                       'numOfRidersCapacity': num_of_riders_capacity,
                       'cost': cost,
                       'rideKind': ride_kind,
                        'pickUpPlaces': pick_up_places}

        if not self.db.insert_query('Rides', values_dict):
            return False

        return True

    def join_ride(self, user_id_passenger: int, ride_id: int) -> tuple:
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
            return False,  "Failed adding you to the ride. Please try again later."

        return True, "You have been successfully joined the ride!"






