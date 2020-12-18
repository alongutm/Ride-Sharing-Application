import abc


class Database(abc.ABC):

    @abc.abstractmethod
    def open_connection(self):
        pass

    @abc.abstractmethod
    def close_connection(self):
        pass

    @abc.abstractmethod
    def select_query(self, table: str, terms_dict: dict):
        pass

    @abc.abstractmethod
    def insert_query(self, table: str, values_dict: dict) -> bool:
        pass

    @abc.abstractmethod
    def update_query(self, table, values_update_dict: dict, terms_dict: dict) -> bool:
        pass
