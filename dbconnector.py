import psycopg2
from config import config

class Dbconnetor ():


    def __init__(self):
        self.config = config()

    def connect(self):
        try:
            params = self.config
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            return conn, cur
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


    def execute_select_query (self, query):
        conn, cur = self.connect()
        with conn:
            cur.execute(query)
            result = cur.fetchone()
            return result

    def execute_select_many_query (self, query):
        conn, cur = self.connect()
        with conn:
            cur.execute(query)
            result = cur.fetchall()
            return result

    def execute_insert_query (self, query):
        conn, cur = self.connect()
        with conn:
            cur.execute(query)
            conn.commit()


    def get_config_parameter (self, conf_name, conf_group):
        result = self.execute_select_query(
            "SELECT conf_value FROM core.configuration WHERE conf_name = '{}' AND conf_group = '{}'".format (conf_name, conf_group))
        if result:
            return result[0]


    def count_questions (self) -> int:
        result = self.execute_select_query("""
                SELECT COUNT(DISTINCT num) 
                FROM test_bot.test_questions
                WHERE test_type = 'MAIN_TEST'
            """)
        return int(result[0])

    def count_additional_questions(self) -> int:
        result = self.execute_select_query("""
                SELECT COUNT(DISTINCT num) 
                FROM test_bot.test_questions
                WHERE test_type = 'ADD_TEST'
            """)
        return int(result[0])


if __name__ == '__main__':
    connector=Dbconnetor()
    result = connector.count_questions()
    print (result[0])