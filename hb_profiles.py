#! /usr/bin/env python

import hb_config
import MySQLdb
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
        Set up the db connection.
        """
        self.conn = MySQLdb.connect(
        host = hb_config.host,
        db = hb_config.dbname,
        read_default_file = hb_config.defaultcnf,
        use_unicode=1,
        charset="utf8"
            )
        self.cursor = self.conn.cursor()
        self.queries = hb_queries.Query()

    def insertInvitees(self, query_key):
        """
        Insert today's potential invitees into the database
        """
        query = self.queries.getQuery(query_key)
        self.cursor.execute(query)
        self.conn.commit()

    def updateTalkPages(self, query_key):
        """
        Updates the database with user talkpage ids (if they have one)
        """
        query = self.queries.getQuery(query_key)
        self.cursor.execute(query)
        self.conn.commit()

    def selectSample(self, query_key, sub_sample=False):
        """
        Returns a list of usernames and ids of candidates for invitation
        """
        sample_query = self.queries.getQuery(query_key)
        self.cursor.execute(sample_query)
        rows = self.cursor.fetchall()
        sample_set = [(row[0],row[1], row[2]) for row in rows]
        if sub_sample: #this may not be necessary
        	sample_set = sample_set[:5]
        return sample_set

    def updateOneRow(self, query_key, qvars):
        """
        Updates the database: was the user invited, or skipped?
        """
#         try:
        query = self.queries.getQuery(query_key, qvars)
        self.cursor.execute(query)
        self.conn.commit()
#         except:
#             print "something went wrong with this one"

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
        self.auth1 = OAuth1(unicode("b5d87cbe96174f9435689a666110159c"),
                client_secret=unicode(hb_config.client_secret),
                resource_owner_key=unicode("ca1b222d687be9ac33cfb49676f5bfd2"),
                resource_owner_secret=unicode(hb_config.resource_owner_secret))

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
        tmplt = tmplt.format(**val).encode('utf-8')
        return tmplt

    def publishProfile(self):
        """
        Publishes one or more formatted messages on a wiki.
        """
        try:
#             print self.page_path
#             print self.edit_summ
#             print self.invite
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
            print "unable to invite " + self.user_name + " at this time."   #should be logged, not printed

