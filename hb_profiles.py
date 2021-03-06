#! /usr/bin/env python

import hb_config
# import MySQLdb
import pymysql.cursors
# import pymysql.converters as conv
# import pymysql.constants as const
# from pymysql.constants import FIELD_TYPE
import hb_output_settings as output_settings
import hb_queries
import hb_templates as templates
import requests
from requests_oauthlib import OAuth1

#TODO: add in logging again, more try statements
#hb_config to config
#get DB class out of profiles.py, rename

class Samples:
    """Create, parse, and post formatted messages to wiki."""

    def __init__(self):
        """
        Set up connections to hostbot db and enwiki db
        Load query library
        """
#         self.conn_hostbot = pymysql.connect(
#             host = hb_config.hostbot_host,
#             db = hb_config.hostbot_db,
#             read_default_file = hb_config.defaultcnf,
#             charset="utf8",
#         )
#
#         self.cursor_hostbot = self.conn_hostbot.cursor()
#
#         self.conn_wiki = pymysql.connect(
#             host = hb_config.wiki_host,
#             db = hb_config.wiki_db,
#             read_default_file = hb_config.defaultcnf,
#             charset="utf8",
#         )
#
#         self.cursor_wiki = self.conn_wiki.cursor()

        self.queries = hb_queries.Query()

    def connect_to_db(self, db_name):
        """
        Takes a string corresponding to a database name (a key in the config)
        Returns a connection to that database
        """

        if db_name == 'hostbot':
#             cursor = self.cursor_wiki
            sql_host = hb_config.hostbot_host
            query_db = hb_config.hostbot_db

        elif db_name == 'enwiki':
            sql_host = hb_config.wiki_host
            query_db = hb_config.wiki_db

        else:
            print("unrecognized database")

        conn = pymysql.connect(
            host = sql_host,
            db = query_db,
            read_default_file = hb_config.defaultcnf,
            charset="utf8",
        )

#         if conn.open:
#             print("conn is open")
#
#         else:
#             print("conn NOT open")
#         cursor = conn.cursor()
        return conn


    def convert_bytes_in_db_rows(self, rows): #should be in toolkit?
        """
        Takes a list of tupes from a db query
        Convert all varbinary fields to unicode strings
        Return a list of lists.
        """
        return [[x.decode() if type(x) == bytes else x for x in row] for row in rows]


    def select_rows(self, query_key, db_name, convert_bytestrings = False):
        """
        Select one or more rows from the wiki db
        Return a list of tuples
        """
#         if query_db == 'enwiki_db':
# #             cursor = self.cursor_wiki
#             cursor = self.conn_wiki.cursor() #attempt to solve the pymysql.err.InterfaceError: (0, '')
#
#         elif query_db == 'hostbot_db':
# #             cursor = self.cursor_hostbot
#             cursor = self.conn_hostbot.cursor() #attempt to solve the pymysql.err.InterfaceError: (0, '')
#
# #         else:
# #             print("unrecognized database: " + query_db)

        conn = self.connect_to_db(db_name)
        query = self.queries.getQuery(query_key)
#         print(query )
        cursor = conn.cursor()
        rows = cursor.execute(query)

        if convert_bytestrings:
            rows = self.convert_bytes_in_db_rows(cursor.fetchall())
        else:
            rows = list(cursor.fetchall())

        cursor.close() #attempt to solve the pymysql.err.InterfaceError: (0, ''), see https://stackoverflow.com/questions/6650940/interfaceerror-0
        conn.close() #can I do this without closing the cursor first?

        return rows


    def insert_rows(self, query_key, rows):
        """
        Insert one or more rows into the hostbot db
        Takes a list of lists or tuples
        Converts datetime values to strings - is this necessary?
        currently, datetime is hardcoded as field 4
        """

        conn = self.connect_to_db("hostbot") #hardcoded because I don't ever want to commit anywhere else
        cursor = conn.cursor()
        query = self.queries.getQuery(query_key)

        for row in rows:
            try:
                row[4] = "{:%Y-%m-%d %H:%M:%S}".format(row[4])
                cursor.execute(query.format(*row))
                conn.commit()
            except:
                print("couldn't insert record for " + str(row[0]))
                continue

        cursor.close() #attempt to solve the pymysql.err.InterfaceError: (0, ''), see https://stackoverflow.com/questions/6650940/interfaceerror-0
        conn.close() #can I do this without closing the cursor first?


    def select_rows_formatted(self, query_key, query_vals, db_name, convert_bytestrings = False):
        """
        Select one or more rows from the wiki db, based on a formatted query
        Return a list of tuples
        """
#         if query_db == 'enwiki_db':
#             qv_escaped = [pymysql.escape_string(x) for x in query_vals] #escape any apostrophes or quotes in the username. per https://www.reddit.com/r/learnpython/comments/ajcp5i/pymysql_and_escaping_input/
#             q_format = "'" + "', '".join(qv_escaped) + "'" #make it a single string
#             cursor = self.cursor_wiki
#
#         elif query_db == 'hostbot_db':
#             cursor = self.cursor_hostbot
#
#         else:
#             print("unrecognized database: " + query_db)
        conn = self.connect_to_db(db_name)
        cursor = conn.cursor()
        qstring = self.queries.getQuery(query_key)
        qv_escaped = [pymysql.escape_string(x) for x in query_vals] #escape any apostrophes or quotes in the username. per https://www.reddit.com/r/learnpython/comments/ajcp5i/pymysql_and_escaping_input/
        q_format = "'" + "', '".join(qv_escaped) + "'" #make it a single string
        query = qstring.format(q_format) #can't seem to do this without the SQL injection no-no
#         print(query)

        rows = cursor.execute(query)

        if convert_bytestrings:
            rows = self.convert_bytes_in_db_rows(cursor.fetchall())
        else:
            rows = list(cursor.fetchall())
#         print(rows)

        cursor.close() #attempt to solve the pymysql.err.InterfaceError: (0, ''), see https://stackoverflow.com/questions/6650940/interfaceerror-0
        conn.close() #can I do this without closing the cursor first?

        return rows


    def update_rows(self,query_key, rows, single_row = False):
        """
        Update values in existing rows on the hostbot db
        """
        conn = self.connect_to_db("hostbot") #hardcoded because I don't ever want to commit anywhere else
        cursor = conn.cursor()
        query = self.queries.getQuery(query_key)

        if single_row:
            cursor.execute(query.format(*rows)) #works if it's a list?
            conn.commit()
        else:
            for row in rows:
                try:
                    cursor.execute(query.format(*rows)) #works if it's a list?
                    conn.commit()
                except:
                    continue #this was leading to a traceback and possibly halting the script

        cursor.close() #attempt to solve the pymysql.err.InterfaceError: (0, ''), see https://stackoverflow.com/questions/6650940/interfaceerror-0
        conn.close() #can I do this without closing the cursor first?


class Profiles:
    """Create, parse, and post formatted messages to wiki."""

    def __init__(self, path, user_name = False, user_id = False, page_id = False, settings = False):
        """
        Instantiate your editing session.
        """
        self.page_path = path
        if user_name:
            self.user_name = user_name
        if user_id:
            self.user_id = user_id
        if page_id:
            self.page_id = str(page_id)
        if settings:
            self.profile_settings = settings #why are settings optional?
        self.api_url = hb_config.oauth_api_url
        self.user_agent = hb_config.oauth_user_agent
        self.auth1 = OAuth1("b5d87cbe96174f9435689a666110159c",
                client_secret=hb_config.client_secret,
                resource_owner_key="ca1b222d687be9ac33cfb49676f5bfd2",
                resource_owner_secret=hb_config.resource_owner_secret)

    def getToken(self):
        """
        Request a token for your request
        """
        response = requests.get(
            self.api_url,
            params={
                'action': "query",
                'meta': "tokens",
                'type': "csrf",
                'format': "json"
                },
            headers={'User-Agent': self.user_agent},
            auth=self.auth1,
            )
        doc = response.json() #why name this variable doc?
        try:
            self.token = doc['query']['tokens']['csrftoken']
        except:
            self.token = None

    def formatProfile(self, val):
        """
        takes in a dictionary of parameter values and plugs them into the specified template
        """
        page_templates = templates.Template()
        tmplt = page_templates.getTemplate(self.profile_settings['type'])
        tmplt = tmplt.format(**val)

        return tmplt

    def publishProfile(self):
        """
        Publishes one or more formatted messages on a wiki.
        """

        if 'test_invites' in self.profile_settings.keys(): #what if profile_settings not set?
            print(self.page_path)
            print(self.edit_summ)
            print(self.invite)
            self.invited = True

        else:
#             print(self.page_path)
            try:
                response = requests.post(
                    self.api_url,
                    data={
                        'action': "edit",
                        'title': self.page_path,
                        'section': "new",
                        'summary': self.edit_summ,
                        'text': self.invite,
                        'bot': 1,
                        'token': self.token,
                        'format': "json"
                        },
                    headers={'User-Agent': self.user_agent},
                    auth=self.auth1
                    )
                self.invited = True

            except:
                print("unable to invite " + self.user_name + " at this time.")   #should be logged, not printed

