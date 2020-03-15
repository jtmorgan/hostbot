#! /usr/bin/env python

from datetime import datetime, timedelta
import hb_config
import json
import pandas as pd
import requests
from requests_oauthlib import OAuth1

rt_header = """== Top ~1000 most viewed English Wikipedia articles on {year}-{month}-{day} ==
Excludes the main page, and all pages outside the article namespace.

Last updated on ~~~~~

{{| class="wikitable sortable"
!Rank
!Article
!Page views
"""

rt_row = """|-
|{rank}
|[[w:{title}|{title}]]
|{views}
"""

def get_top_daily(sample_date):
    """
    Accepts a dictionary with string values for %Y %m and %d
    Returns a list of dictionaries of article traffic metadata
    """

    q_template= "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/all-access/{year}/{month}/{day}"
    q_string = q_template.format(**sample_date)
#     print(q_string)
    response = requests.get(q_string).json()
#     print(response)
    top_articles = response['items'][0]['articles']

    return top_articles

def get_token(auth1):
    """
    Accepts an auth object for a user
    Returns an edit token for the specified wiki
    """

    result = requests.get(
        url="https://en.wikipedia.org/w/api.php", #TODO add to config
        params={
            'action': "query",
            'meta': "tokens",
            'type': "csrf",
            'format': "json"
            },
        headers={'User-Agent': "jonnymorgan.esq@gmail.com"}, #TODO add to config
        auth=auth1,
        ).json()

    print(result)

    edit_token = result['query']['tokens']['csrftoken']

    return(edit_token)

def publish_report(output, auth1, edit_token):
    """
    Accepts the page text, credentials and edit token
    Publishes the formatted page text to the specified wiki
    """
    response = requests.post(
    url = "https://en.wikipedia.org/w/api.php", #TODO add to config
    data={
        'action': "edit",
        'title': "User:HostBot/Top_1000_report", #TODO add to config
#         'section': "new",
        'summary': "testing new top 1000 reports", #TODO add to config
        'text': output,
        'bot': 0,
        'token': edit_token,
        'format': "json"
        },
    headers={'User-Agent': "jonnymorgan.esq@gmail.com"}, #TODO add to config
    auth=auth1
        )

if __name__ == "__main__":

    auth1 = OAuth1(dtr_config.client_key,
               hb_config.client_secret,
               hb_config.resource_owner_key,
               hb_config.resource_owner_secret)

    sample_date = {'year': datetime.strftime(datetime.now() - timedelta(1), '%Y'),
           'month' : datetime.strftime(datetime.now() - timedelta(1), '%m'),
           'day': datetime.strftime(datetime.now() - timedelta(1), '%d'),
                }

    top_1k_daily = get_top_daily(sample_date)

    df_topk = pd.DataFrame(top_1k_daily)

    blacklist = ["Main_Page", "Special:", "Portal:", "Wikipedia:", "Talk:", "User:", "_talk:"]

    df_topk = df_topk[~df_topk['article'].str.contains('|'.join(blacklist))]

    ## fix the ranking, now that we've deleted some pages from the list
    new_rank = range(1, len(df_topk)+1)

    df_topk['rank'] = list(new_rank)

    header = rt_header.format(**sample_date)

    report_rows = [format_row(x, y, z, rt_row)
          for x, y, z
          in zip(df_topk['rank'],
                 df_topk['article'],
                 df_topk['views'],
                    )]

    rows_wiki = ''.join(report_rows)

    output = header + rows_wiki + "|}"

    edit_token = get_token(auth1)

    publish_report(output, auth1, edit_token)


