#! /usr/bin/env python

from datetime import datetime, timedelta
import hb_config
import json
import pandas as pd
import requests
from requests_oauthlib import OAuth1

rt_header = """== Popular articles {date7} to {date1} ==
Excludes the main page, and all pages outside the article namespace.

Last updated on ~~~~~

{{| class="wikitable sortable"
!Rank
!Article
!Total weekly views
!Days among top 1000
"""

footer = """|}

<!--IMPORTANT add all categories to the top section of the page, not here. Otherwise, they will get removed when the bot runs tomorrow! -->

"""

rt_row = """|-
|{rank}
|[[w:{title}|{title}]]
|{week_total}
|{days_in_topk}
"""

def get_yesterdates(lookback=7):
    """
    Accepts a lookback parameter of how many days ago to gather data for (not including the current day per UTC time)
    Defaults to seven days lookback (val must be at least 1)
    Returns a list of dictionaries with the previous n dates (exclusive), in reverse chronological order
    """

    date_range = []

    for d in range(1, lookback + 1):
        date_parts = {'year': datetime.strftime(datetime.now() - timedelta(d), '%Y'),
           'month' : datetime.strftime(datetime.now() - timedelta(d), '%m'),
           'day': datetime.strftime(datetime.now() - timedelta(d), '%d'),
            }

        date_parts['date'] = "-".join(date_parts['year'] + date_parts['month'] + date_parts['day']) #untested, may work better with string formatting

        date_range.append(date_parts)

    return date_range

def get_all_topk_articles(day_range):
    """
    Accepts a list of dicts with year, month, and day values
    Returns a dictionary (article titles as keys) with all articles that were in the topk list during those dates
    """

    q_template= "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/all-access/{year}/{month}/{day}"

    all_articles = {}

    for day_val in day_range:
        q_string = q_template.format(**day_val) #will this fail if there are extra keys in the dict, like 'date'?
        response = requests.get(q_string).json()
        top_articles_list = response['items'][0]['articles']

        top_articles = {item['article']: {} for item in top_articles_list}

        all_articles.update(top_articles)

    return all_articles

def get_daily_counts(day_range, ar_dict):
    """
    Accepts a list of dicts with year, month, and day values
        And a dict with article titles as keys and empty dicts as values
    Returns the article dictionary with each sub-dict populated
        With pageview values for each date where pageviews were available
    """

    q_template= "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/all-access/{year}/{month}/{day}"

    for day_val in day_range:

        dstr = day_val['year'] + "-" + day_val['month'] + "-" + day_val['day']
#         print(dstr)

        q_string = q_template.format(**day_val)
        print(q_string)
        response = requests.get(q_string).json()
        top_articles_list = response['items'][0]['articles']

        for ar in top_articles_list:
#             print(ar)
            if ar['article'] in ar_dict.keys():
#                 print(ar['article'])
                ar_dict[ar['article']].update({day_val['date'] : ar['views']}) #untested
#                 print(ar_dict[ar['article']])

    return ar_dict

# def get_top_daily(date_parts):
#     """
#     Accepts a dictionary with string values for %Y %m and %d
#     Returns a list of dictionaries of article traffic metadata
#     """
#
#     q_template= "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/all-access/{year}/{month}/{day}"
#     q_string = q_template.format(**date_parts)
# #     print(q_string)
#     response = requests.get(q_string).json()
# #     print(response)
#     top_articles = response['items'][0]['articles']
#
#     return top_articles

def format_row(rank, title, views, row_template):

    table_row = {'rank': rank,
           'title' : title.replace("_"," "),
            'views' : views,
                }

    row = row_template.format(**table_row)
#     print(row)
    return(row)


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

#     print(result)
    edit_token = result['query']['tokens']['csrftoken']
#     print(edit_token)

    return(edit_token)

def publish_report(output, edit_sum, auth1, edit_token):
    """
    Accepts the page text, credentials and edit token
    Publishes the formatted page text to the specified wiki
    """
    response = requests.post(
    url = "https://en.wikipedia.org/w/api.php", #TODO add to config
    data={
        'action': "edit",
        'title': "User:HostBot/Top_1000_report", #TODO add to config
        'section': "1",
        'summary': edit_sum, #TODO add to config
        'text': output,
        'bot': 1,
        'token': edit_token,
        'format': "json"
        },
    headers={'User-Agent': "jonnymorgan.esq@gmail.com"}, #TODO add to config
    auth=auth1
        )

if __name__ == "__main__":

    auth1 = OAuth1("b5d87cbe96174f9435689a666110159c",
               hb_config.client_secret,
               "ca1b222d687be9ac33cfb49676f5bfd2",
               hb_config.resource_owner_secret)

    #get yesterday's date info for queries and reporting
    date_parts = get_yesterdates()

    top_1k_daily = get_top_daily(date_parts)

    df_topk = pd.DataFrame(top_1k_daily)

    blacklist = ["Main_Page", "Special:", "Portal:", "Wikipedia:", "Talk:", "User:", "_talk:", "Help:", "File:"]

    df_topk = df_topk[~df_topk['article'].str.contains('|'.join(blacklist))]

    ## fix the ranking, now that we've deleted some pages from the list
    new_rank = range(1, len(df_topk)+1)

    df_topk['rank'] = list(new_rank)

    header = rt_header.format(**date_parts)

    report_rows = [format_row(x, y, z, rt_row)
          for x, y, z
          in zip(df_topk['rank'],
                 df_topk['article'],
                 df_topk['views'],
                    )]

    rows_wiki = ''.join(report_rows)

    output = header + rows_wiki + footer

    edit_token = get_token(auth1)

    edit_sum = "Top 1k articles report for {year}-{month}-{day}".format(**date_parts)

    publish_report(output, edit_sum, auth1, edit_token)


