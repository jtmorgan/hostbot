#! /usr/bin/env python

import hb_config as config
from operator import itemgetter
import pymysql
import requests
from requests_oauthlib import OAuth1

#TODO: add in logging again, more try statements

class API:
    """Interactions with the API"""

    def __init__(self, alt_url_get=False):
        """
        Set up the API session.
        :alt_get_url: if you want to query a different wiki than you post to (for testing)
        """

#         self.api_url_get = config.api_url_get
        if alt_url_get:
            self.api_url_get = alt_url_get
        else:
            self.api_url_get = config.api_url_get     
        self.api_url_post = config.oauth_api_url
        self.user_agent = config.oauth_user_agent
        self.auth1 = OAuth1(config.client_key.encode('utf-8'),
                client_secret=config.client_secret.encode('utf-8'),
                resource_owner_key=config.resource_owner_key.encode('utf-8'),
                resource_owner_secret=config.resource_owner_secret.encode('utf-8')
                ) 


    def get_token(self): #should be self-token?
        """
        Request an edit token.
        """
        response = requests.get(
            self.api_url_post,
            params={
                'action': "query",
                'meta': "tokens",
                'type': "csrf",
                'format': "json"
                },
            headers={'User-Agent': self.user_agent},
            auth=self.auth1       
            )
        doc = response.json()
        try:
            self.token = doc['query']['tokens']['csrftoken'] 
        except:
            self.token = None
#         return token  # raise error instead, log it!!!


    def publish_to_wiki(self, page_path, edit_summ, text, sec_str = False): #should just be 'publish'? sec_str should be sec? 
        """
        Publishes text to a wikipage, as a bot. 
    
        Specify the edit comment, and (optionally) the output section.
        """
        api_params={
            'action': "edit",
            'title': page_path,
            'summary': edit_summ,
            'text': text,
            'bot': 1,
            'token': self.token,
            'format': "json"
            }
        if sec_str:
            api_params['section'] = sec_str
        else:
            pass
           
        try:
            response = requests.post(self.api_url_post, api_params, headers={'User-Agent': self.user_agent}, auth=self.auth1)
#             print(response.status_code)
#             print(response.json())
            #if the edit was failure, log it            
        except:
            print("post failed.")   #should be logged, not printed
        result = response.json()
#         print(result)
        return response.status_code, result['edit']['result']

    def get_page_text(self, page_path, sec_index=False, limit=False):
        """
        Get the raw text of a page or page section.

        Sample: https://test.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Wikipedia:Teahouse/Host_landing&rvprop=content&rvsection=5&format=jsonfm
        """
        parameters = {
            'action': 'query',
            'prop': 'revisions',
            'titles': page_path,
            'rvprop' : 'comment|content', #check that this still works for host profiles
            'format': "json",
            'continue' : ''            
        }
        if sec_index:
            parameters['rvsection'] = sec_index
        if limit:
            parameters['rvlimit'] = limit
    #     try:
        response = requests.get(self.api_url_get, headers={'User-Agent': self.user_agent}, params=parameters)                   
        doc = response.json()
#         revs = []
        for page_id in doc['query']['pages'].keys():
            revs = doc['query']['pages'][page_id]['revisions']
        return revs
#         for v in doc['query']['pages'].values(): #avoids need for page_id
#             text = v['revisions'][0]['*']
    #     except:#if there's an error, text is an empty string. Should log instead.
    #         text = ""
#         return text 


    def get_page_section_data(self, page_path, level = False): #just get_page_sections
        """
        Returns the section titles and numbers for a given page.
    
        Level arg can be used to return only sections of a given indentation level.
        Sample request: https://test.wikipedia.org/w/api.php?action=parse&page=Wikipedia:Teahouse/Host_landing&prop=sections&format=jsonfm
        """
        response = requests.get(
            self.api_url_get,
            params={
                'action': "parse",
                'page': page_path,
                'prop': 'sections',
                'format': "json"
                },
            headers={'User-Agent': self.user_agent},
        )
        doc = response.json()
#         print(doc)
    #     try:
        if level:
            secs_list = [{'title' : x['line'], 'index' : x['index']} for x in doc['parse']['sections'] if x['toclevel'] == level]
        else:
            secs_list = [{'title' : x['line'], 'index' : x['index']} for x in doc['parse']['sections']]
    #     except:
    #         secs_list = None
        return secs_list


class DB:
    """Database queries"""

    def __init__(self):
        """
        Set up the DB conn.
        """    
        self.conn = pymysql.connect(
            host = config.host,
            read_default_file = config.testcnf,
            database = config.testdb,
            charset='utf8',
            )
#     return conn

    def select_query(self, db_to_use, q_string, q_params): #renamed from query_db
        """
        Specify database and run a select query.
        q_params: a list of one or more strings to pass into the query string. 
        """ 
        with self.conn.cursor() as cur:
            cur.execute('use {};'.format(db_to_use))
            cur.execute(q_string.format(*q_params))
            res = cur.fetchall()
            data = tuple(map(lambda x: x.decode('utf-8') if type(x) == bytes else x, res[0])) #convert bytes to strings
        return data[0] #db query should always return a tuple of len 1


def dedupe_one(list1, dupe_key):
    """
    Remove all but the first instances (chronologically) of items 
    in a list of dicts that have the same value for a specified key.
    """
    list2 = []
    seen = set()
    for x in list1:
        if x[dupe_key] not in seen:
            list2.append(x)
            seen.add(x[dupe_key])
    #log duplicates found        
    return list2
    
def dedupe_two(list1, list2, dupe_key):
    """
    Remove all items from a list of dicts (list2) that match
    values for a specified key in another list of dicts (list1)
    """
    #log duplicates found
    return [x for x in list2 if x[dupe_key] not in [y[dupe_key] for y in list1]]

def combine_and_sort(list1, list2, sort_key, reverse=True):
    """
    Combine two lists of dicts and sort the resulting list
    by the specified key. 
    
    Default sort is last-first (strings)and greatest-least (ints)
    """
    list3 = list1 + list2
    list3.sort(key=itemgetter(sort_key), reverse=reverse)
    return list3     

def split_binary(list1, split_key, split_val):
    """
    Split a list of dicts by the value of a specified key and return two lists
    """
    list_no_val = [x for x in list1 if x[split_key] != split_val] 
    list_has_val = [x for x in list1 if x[split_key] == split_val]
    return list_no_val, list_has_val