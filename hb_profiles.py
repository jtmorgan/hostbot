#! /usr/bin/env python

import hb_config
# import MySQLdb
import pymysql.cursors
import pymysql.converters as conv
# import pymysql.constants as const
from pymysql.constants import FIELD_TYPE
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
        self.conn_hostbot = pymysql.connect(
            host = hb_config.hostbot_host,
            db = hb_config.hostbot_db,
            read_default_file = hb_config.defaultcnf,
            charset="utf8",
        )

        self.cursor_hostbot = self.conn_hostbot.cursor()

        self.conn_wiki = pymysql.connect(
            host = hb_config.wiki_host,
            db = hb_config.wiki_db,
            read_default_file = hb_config.defaultcnf,
            charset="utf8",
        )

        self.cursor_wiki = self.conn_wiki.cursor()

        self.queries = hb_queries.Query()

    def convert_bytes_in_db_rows(self, rows):
        """
        Takes a list of tupes from a db query
        Convert all varbinary fields to unicode strings
        Return a list of lists.
        """
        return [[x.decode() if type(x) == bytes else x for x in row] for row in rows]


    def select_from_wiki_db(self, query_key, convert_bytestrings = False):
        """
        Select one or more rows from the wiki db
        Return a list of tuples
        """
        query = self.queries.getQuery(query_key)
        rows = self.cursor_wiki.execute(query)
        if convert_bytestrings:
            rows = self.convert_bytes_in_db_rows(self.cursor_wiki.fetchall())
        else:
            rows = list(self.cursor_wiki.fetchall())

        return rows

    def insert_rows(self, query_key, rows):
        """
        Insert one or more rows into the hostbot db
        Takes a list of lists
        Converts datetime values to strings - is this necessary?
        currently, datetime is hardcoded as field 4
        """
        query = self.queries.getQuery(query_key)
        for row in rows:
            row[4] = '{:%Y-%m-%d %H:%M:%S}'.format(row[4])
            x = tuple(row)
            self.cursor_hostbot.execute(query.format(*x))
            self.conn_hostbot.commit()


 #    def insertInvitees(self, query_key):
#         """
#         Insert today's potential invitees into the database
#         """
#         query = self.queries.getQuery(query_key)
#         self.cursor.execute(query)
#         self.conn.commit()
#
#     def updateTalkPages(self, query_key):
#         """
#         Updates the database with user talkpage ids (if they have one)
#         """
#         query = self.queries.getQuery(query_key)
#         self.cursor.execute(query)
#         self.conn.commit()
#
#     def selectSample(self, query_key, sub_sample=False):
#         """
#         Returns a list of usernames and ids of candidates for invitation
#         """
#         sample_query = self.queries.getQuery(query_key)
#         self.cursor.execute(sample_query)
#         rows = self.cursor.fetchall()
#         sample_set = [[row[0],row[1], row[2]] for row in rows]
#         if sub_sample:
#             sample_set = sample_set[:5]
#         return sample_set
#
#     def updateOneRow(self, query_key, qvars):
#         """
#         Updates the database: was the user invited, or skipped?
#         """
# #         try:
#         query = self.queries.getQuery(query_key, qvars)
#         self.cursor.execute(query)
#         self.conn.commit()
# #         except:
# #             print "something went wrong with this one"

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
#         tmplt = tmplt.format(**val).encode('utf-8')
        tmplt = tmplt.format(**val)

        return tmplt

    def publishProfile(self):
        """
        Publishes one or more formatted messages on a wiki.
        """
        try:
            print(self.page_path)
#             print(self.edit_summ)
            print(self.invite)
#             response = requests.post(
#                 self.api_url,
#                 data={
#                     'action': "edit",
#                     'title': self.page_path,
#                     'section': "new",
#                     'summary': self.edit_summ,
#                     'text': self.invite,
#                     'bot': 1,
#                     'token': self.token,
#                     'format': "json"
#                     },
#                 headers={'User-Agent': self.user_agent},
#                 auth=self.auth1
#                 )
#             self.invited = True
        except:
            print("unable to invite " + self.user_name + " at this time.")   #should be logged, not printed

