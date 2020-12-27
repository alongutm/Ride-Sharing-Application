import pyodbc
from abc import ABC
from Idatabase import Database


class AzureDatabase(Database, ABC):
    """
    the class implements the Idatabase interface.
    the class responsible to communicate with the database located in the microsoft azure cloud.
    """
    def __init__(self):
        """
        constructor
        """
        self.server = 'tcp:bgride-db.database.windows.net'
        self.database = 'BGRIde'
        self.username = 'aviv_alon'
        self.password = 'Arnuyv123'
        self.cursor = None
        self.connection = None

    def open_connection(self):
        """
        the method open a connection with the azure database.
        """
        self.connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.server + ';DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        """
        the method close the connection with the azure database.
        """
        self.cursor.close()
        self.connection.close()

    def select_query(self, table: str, terms_dict=None, is_string=False) -> list:
        """
        the method gather date from the database.
        :param table: String. the table/tables to select date from.
        :param terms_dict: dict. a dictionary containg all the terms to constrain on the query.
        :param is_string: boolean. a boolean to flag if the the term are String type.
        :return: list. a list of all the results from committing the query.
        """
        query = f"SELECT * FROM {table}"

        if terms_dict is not None:
            terms_query = ' '
            for term in terms_dict.keys():
                if not is_string:
                    terms_query = terms_query + f"{term}='{terms_dict[term]}' AND "
                else:
                    terms_query = terms_query + f"{term}={terms_dict[term]} AND "
            terms_query = terms_query[:-5]
            query = f"{query} WHERE {terms_query}"

        self.open_connection()

        self.cursor.execute(query)

        results = self.cursor.fetchall()

        self.close_connection()

        return results

    def insert_query(self, table: str, values_dict: dict) -> bool:
        """
        the method insert a date from the database.
        :param table: String. the table name to insert data to.
        :param values_dict: dict. the data values to insert to the table.
        :return: boolean. return True if the insertion succeeded. else - return False.
        """
        fields_query = "("
        values_query = "("
        for field in values_dict.keys():
            fields_query = f"{fields_query}{field}, "
            values_query = f"{values_query}'{values_dict[field]}', "

        fields_query = f"{fields_query[:-2]}) "
        values_query = f"{values_query[:-2]})"

        query = f"INSERT INTO {table}{fields_query} VALUES{values_query}"

        self.open_connection()

        try:
            self.cursor.execute(query)
            self.cursor.commit()
        except:
            self.close_connection()
            return False

        if not self.cursor.rowcount != 0:
            self.close_connection()
            return False

        self.close_connection()
        return True

    def update_query(self, table: str, values_update_dict: dict, terms_dict: dict) -> bool:
        """
        the method updated an existing data in the database.
        :param table: String. the table name to update data in.
        :param values_update_dict: dict. the values to update the data.
        :param terms_dict: dict. the terms to aim the specific row in the database that need to be updated.
        :return:  boolean. return True if the update succeeded. else - return False.
        """
        set_query = ''
        terms_query = ''

        for value in values_update_dict.keys():
            set_query = f"{set_query}{value}='{values_update_dict[value]}', "

        set_query = set_query[:-2]

        for value in terms_dict.keys():
            terms_query = f"{terms_query}{value}='{terms_dict[value]}' AND "

        terms_query = terms_query[:-4]
        query = f"UPDATE {table} SET {set_query} WHERE {terms_query}"
        self.open_connection()

        try:
            self.cursor.execute(query)
            self.cursor.commit()
        except:
            self.close_connection()
            return False

        self.close_connection()
        return True

    def update_query_increment(self, table: str, values_update_list: list, terms_dict: dict) -> bool:
        """
        the method updated an existing integer data in the database by incrementing the value in 1.
        :param table: String. the table name to update data in.
        :param values_update_list: dict. the values to update the data.
        :param terms_dict: dict. the terms to aim the specific row in the database that need to be updated.
        :return: boolean. return True if the update succeeded. else - return False.
        :param table:
        :param values_update_list:
        :param terms_dict:
        :return:
        """

        set_query = ''
        terms_query = ''

        for value in values_update_list:
            set_query = f"{set_query}{value}={value} + 1, "

        set_query = set_query[:-2]

        for value in terms_dict.keys():
            terms_query = f"{terms_query}{value}='{terms_dict[value]}' AND "

        terms_query = terms_query[:-4]
        query = f"UPDATE {table} SET {set_query} WHERE {terms_query}"
        self.open_connection()

        try:
            self.cursor.execute(query)
            self.cursor.commit()
        except:
            self.close_connection()
            return False

        self.close_connection()
        return True
