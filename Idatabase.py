import abc


class Database(abc.ABC):
    """
    Interface class representing the needed functionalities to the app tp
    communicate with the chosen database that will implement this interface.
    """

    @abc.abstractmethod
    def open_connection(self):
        """
        open connection.
        """
        pass

    @abc.abstractmethod
    def close_connection(self):
        """
        close connection.
        :return:
        """
        pass

    @abc.abstractmethod
    def select_query(self, table: str, terms_dict: dict):
        """
        get data from the database.
        """
        pass

    @abc.abstractmethod
    def insert_query(self, table: str, values_dict: dict) -> bool:
        """
        insert data to the database.
        """
        pass

    @abc.abstractmethod
    def update_query(self, table: str, values_update_dict: dict, terms_dict: dict) -> bool:
        """
        update data in the database.
        """
        pass

    @abc.abstractmethod
    def update_query_increment(self, table: str, values_update_list: list, terms_dict: dict) -> bool:
        """
        update numeric data in the database by incrementing it by 1.
        """
        pass
