#! /usr/bin/env python2.7

# Copyright 2013 Jtmorgan

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# from datetime import datetime, timedelta
# import dateutil.parser
# import wikitools
import hostbot_settings
import MySQLdb
import hb_output_settings as output_settings
import hb_queries
import hb_templates as templates
import requests
from requests_oauthlib import OAuth1
import wikitools


class Samples:
    """Create, parse, and post formatted messages to wiki."""

    def __init__(self):
        """
        Set up the db connection.
        """
#         self.wiki = wikitools.Wiki(hostbot_settings.apiurl)
#         self.wiki.login(hostbot_settings.username, hostbot_settings.password)
        self.conn = MySQLdb.connect(
        host = hostbot_settings.host, 
        db = hostbot_settings.dbname, 
        read_default_file = hostbot_settings.defaultcnf, 
        use_unicode=1, 
        charset="utf8"
            )
        self.cursor = self.conn.cursor()        
        self.queries = hb_queries.Query()        
        
    def getSample(self, query_key, sub_sample=False):
        """
        Returns a list of usernames and ids of candidates for invitation
        """
#         sample_query = self.queries.getQuery(query_key)
        sample_query = "SELECT user_name, user_id, user_talkpage FROM th_invite_test WHERE date(sample_date) = date(NOW()) AND sample_type = 4 AND invite_status IS NULL AND (ut_is_redirect = 0 OR ut_is_redirect IS NULL);"
        self.cursor.execute(sample_query)
        rows = self.cursor.fetchall()
        sample_set = [(row[0],row[1], row[2]) for row in rows]
        if sub_sample:
        	sample_set = sample_set[:5]
        return sample_set 
        
#         self.cursor.close()
#         self.conn.close()    

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
#         print self.page_path
        if user_id:
            self.user_id = user_id
#           print self.page_id
        if page_id:
            self.page_id = str(page_id)
        if settings:
            self.profile_settings = settings
        self.api_url = hostbot_settings.oauth_api_url
        self.user_agent = hostbot_settings.oauth_user_agent
        self.auth1 = OAuth1(unicode("b5d87cbe96174f9435689a666110159c"),
                client_secret=unicode(hostbot_settings.client_secret),
                resource_owner_key=unicode("ca1b222d687be9ac33cfb49676f5bfd2"),
                resource_owner_secret=unicode(hostbot_settings.resource_owner_secret))      
                
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
            token = doc['query']['tokens']['csrftoken'] 
        except:
            token = None
        
        return token
                                    
    def getPageText(self, section=False):
        """
        Gets the raw text of a page or page section.
        Sample: http://meta.wikimedia.org/w/api.php?action=query&prop=revisions&titles=Grants:IdeaLab/Introductions&rvprop=content&rvsection=21&format=jsonfm
        """
        api_params={
            'action': 'query',
            'prop': 'revisions',
            'titles': self.page_path,
            'rvprop' : 'content',
            'format': "json"            
        }        
        if section:
			api_params['rvsection'] = section
        response = requests.get(self.api_url, params=api_params)                   
        doc = response.json()
        text = doc['query']['pages'][self.page_id]['revisions'][0]['*']
        return text
        
    def formatProfile(self, val):
        """
        takes in a dictionary of parameter values and plugs them into the specified template
        """
        page_templates = templates.Template()
        tmplt = page_templates.getTemplate(self.profile_settings['type'])
        tmplt = tmplt.format(**val).encode('utf-8')
#       print tmplt
        return tmplt
        
    def publishProfile(self):
        """
        Publishes one or more formatted messages on a wiki.
        """
        try:
            print self.page_path
            print self.edit_summ
            print self.invite
            self.invited = True
        except:
            print "unable to invite " + self.user_name + " at this time."    
        
        return self.invited
#         response = requests.post(
#             self.api_url,
#             data={
#                 'action': "edit",
#                 'title': path,
#                 'section': "new",
#                 'summary': edit_summ,
#                 'text': val,
#                 'bot': 1,
#                 'token': doc['query']['tokens']['csrftoken'],
#                 'format': "json"
#             },
#             headers={'User-Agent': self.user_agent},
#             auth=auth1  # This is the new thing
#         )     

    def updateDB(self):
        """
        Updates the database: was the user invited, or skipped?
        """
        self.conn = MySQLdb.connect(
        host = hostbot_settings.host, 
        db = hostbot_settings.dbname, 
        read_default_file = hostbot_settings.defaultcnf, 
        use_unicode=1, 
        charset="utf8"
            )
        self.cursor = self.conn.cursor()        
        self.queries = hb_queries.Query() 


