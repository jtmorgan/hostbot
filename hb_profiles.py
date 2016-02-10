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
import invite_config
import MySQLdb
import hb_output_settings as output_settings
import hb_templates as templates
import requests
from requests_oauthlib import OAuth1
# import operator
import hb_queries
# import re
# import time

class Profiles:
    """Create, parse, and post formatted messages to wiki."""

    def __init__(self, path, id = False, settings = False):
        """
        Instantiate your editing session.
        """
        self.page_path = path
#       print self.page_path
        if id:
            self.page_id = str(id)
#           print self.page_id
        if settings:
            self.profile_settings = settings
        self.api_url = invite_config.oauth_api_url
        self.user_agent = invite_config.oauth_user_agent
        self.auth1 = OAuth1(unicode("b5d87cbe96174f9435689a666110159c"),
                client_secret=unicode(invite_config.client_secret),
                resource_owner_key=unicode("ca1b222d687be9ac33cfb49676f5bfd2"),
                resource_owner_secret=unicode(invite_config.resource_owner_secret))      
                
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
                                    
    def getPageText(self, page_path, page_id):
        """
        Gets the raw text of a page or page section.
        Sample: http://meta.wikimedia.org/w/api.php?action=query&prop=revisions&titles=Grants:IdeaLab/Introductions&rvprop=content&rvsection=21&format=jsonfm
        """
#       if section:
#           params['rvsection'] = section
        response = requests.get(
            self.api_url,   
            params={
            'action': 'query',
            'prop': 'revisions',
            'titles': page_path,
            'rvprop' : 'content',
                },
#             headers={'User-Agent': self.user_agent},
#             auth=self.auth1,        
            )                   
        doc = response.json()
        text = response['query']['pages'][page_id]['revisions'][0]['*']
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
        
    def publishProfile(self, val, path, edit_summ):
        """
        Publishes one or more formatted messages on a wiki.
        """
        print path
        print edit_summ
        print val
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




