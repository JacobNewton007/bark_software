import sqlite3

class DatabaseManager:
    def __init__(self, database_filename):
        self.connection = sqlite3.connect(database_filename) #create and store database for later use

    def __del__(self):
        self.connection.close()# cleans up connnection when done, to be safe 

    #transaction
    def _execute(self, statement, values=None):
        with self.connection:  # this create a database transaction context
            cursor = self.connection.cursor()
            cursor.execute(statement, values or [])# uses the cursor to execute the sql statement
            return cursor            # has stored the result 

    def create_table(self, table_name, columns):
        columns_with_types = [ #Constructs the columns definitions, with their data data type and constraints
            f'{column_name} {data_type}'
            for column_name, data_type in columns.items()
        ]
        self._execute(# Constructs the full create table statement and execute it.

            f''' CREATE TABLE IF NOT EXISTS {table_name}
            ({', '.join(columns_with_types)});
            '''
        )

    def add(self, table_name, data):
        palceholders = ', '.join('?' * len(data))
        column_names  = ', '.join(data.keys())# the keys of the data are the names of thr columns
        column_values = tuple(data.values())#.values() retur a dict_values object, but execute needs a list or tuple


        self._execute(
            f'''
            INSERT INTO {table_name}
            ({column_names})
            VALUES ({palceholders});
            ''',
            column_values, # passes the optional values  argument to _execute method
        )

    def delete(self, table_name, criteria):# the criteria argument isn't optional here; all the records would be deleted without any criteria.
        palceholders = [f'{column} = ?' for column in criteria.keys()]
        delete_criteria = ' AND '.join(palceholders)
        
        self._execute(
            f'''
            DELETE FROM {table_name}
            WHERE {delete_criteria};
            ''',
            tuple(criteria.values()),
        )

    def select(self, table_name, criteria =None, order_by=None):
        criteria = criteria or {}# criteria can be empty by default, because selecting all records in the table is all right
        query  = f'SELECT * FROM {table_name}'

        if criteria:#constructs the WHERE clause to limit the result
            palceholders = [f'{column} = ?' for column in criteria.keys()]
            select_criteria = ' AND '.join(palceholders)
            query += f'WHERE {select_criteria}'

        if order_by:# construct the ORDER BY clause to sort the results
            query += f' ORDER BY {order_by}'

        return self._execute(# this time, you want the return value from _execute to iterate over the results.
            query, 
            tuple(criteria.values())
        )

    def update(self, table_name, criteria, data):
        update_placeholders = [f'{column} = ?' for column in criteria.keys()]
        update_criteria = ' AND '.join(update_placeholders)

        data_placeholders = ', '.join(f'{key} = ?' for key in data.keys())

        values = tuple(data.values()) + tuple(criteria.values())

        self._execute(
            f'''
            UPDATE {table_name}
            SET {data_placeholders}
            WHERE {update_criteria};
            ''',
            values,
        )