#! /usr/bin/env python

from datetime import datetime, timedelta
import hb_config
import json
import pandas as pd
import requests
from requests_oauthlib import OAuth1
from urllib import parse

rt_header = """== Popular articles {date7} to {date1} ==
Last updated on ~~~~~

{{| class="wikitable sortable"
!Rank
!Article
!Total weekly views
!Days in top 1k this week
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

        date_parts['display_date'] = date_parts['year'] + "-" + date_parts['month'] + "-" + date_parts['day']

        date_parts['api_date'] = date_parts['year'] + date_parts['month'] + date_parts['day'] + "00"

        date_range.append(date_parts)

    return date_range

def get_all_topk_articles(day_range):
    """
    Accepts a list of dicts with year, month, and day values
    Returns a dictionary (article titles as keys)
        with all articles that were in the topk list during those dates
        and the pageview counts for each of the dates the article appeared in the topk

    Example query: https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/all-access/2020/03/31
    """

    q_template= "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/all-access/{year}/{month}/{day}"

    all_articles = {}

    for day_val in day_range:
        q_string = q_template.format(**day_val)
        response = requests.get(q_string).json()
        top_articles_list = response['items'][0]['articles']

        for ar in top_articles_list:
            if ar['article'] in all_articles.keys():
                all_articles[ar['article']].update({day_val['api_date'] : ar['views']})

            else:
                all_articles.update({ar['article'] : {day_val['api_date'] : ar['views']}})

    return all_articles

def ar_days_in_topk(day_range, ar_dict):
    """
    Accepts a day range dictionary
        And a nested dict with articles as keys
        And as values varying numbers of k,v pairs
    Returns the article dictionary with a new k,v pair value
        that counts the number of existing k,v pairs in that article dict
    """

    for k,v in ar_dict.items():
        v['topk_days'] = len(ar_dict[k])

    return ar_dict

def get_daily_non_topk_counts(day_range, ar_dict):
    """
    Accepts a list of dicts with year, month, and day values
        And a dict with article titles as keys dicts with different numbers of k,v pairs as values
    Returns a dict that contains for each article the difference between the length of the day range
        And the number of keys in each dict
    Example query:         https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user/2009_swine_flu_pandemic/daily/2020032500/2020033100
    """

    q_template= "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user/{article}/daily/{day7}/{day1}"

    for k,v in ar_dict.items():
        if len(v) < 8: #if this article didn't spend all week among the top 1000

            safe_title = parse.quote(k, safe='') #in case there are weird chars in title
            q_string = q_template.format(article = safe_title, day7 = day_range[6]['api_date'], day1 = day_range[0]['api_date'])
#             print(q_string)
            response = requests.get(q_string).json()

            ar_views = response['items']
    #         print(ar_views)

            for d in ar_views:
                if d['timestamp'] not in v.keys():
                    v.update({d['timestamp'] : d['views']})
        else:
            pass

    return ar_dict

def fill_null_date_vals(day_range, ar_dict):
    """
    Accepts a list of dicts with year, month, and day values
        And a dict with article titles as keys and gaps in the date keys
    Returns the article dictionary with each sub-dict fully populated
        With pageview values for all dates in range, even if val is 0
    """
    #https://www.geeksforgeeks.org/dictionary-methods-in-python-set-2-update-has_key-fromkeys/
    for day_val in week_of_days:
        for v in ar_dict.values():
            if len(v) < 8: #if we still don't have any pageviews for some days
                v.setdefault(day_val['api_date'], 0) #adds a key with val of 0 if no key present
            else:
                pass

    return ar_dict

def format_row(rank, title, week_total, days_in_topk, row_template):

    table_row = {'rank': rank,
           'title' : title.replace("_"," "),
            'week_total' : week_total,
            'days_in_topk' : days_in_topk
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

    #get previous week's date info for query and reporting
    week_of_days = get_yesterdates(lookback=7)

    #get all of the articles that appeared on the topk list that week
    all_articles = get_all_topk_articles(week_of_days)

    #get counts for all days each article was in the top 1000
#     all_articles = get_daily_topk_counts(week_of_days, all_articles)

    #add number of days each article appears in the topk list. could do this in first function too
    all_articles = ar_days_in_topk(len(week_of_days), all_articles)

    #add page counts for days the article was not in the topk list
    all_articles = get_daily_non_topk_counts(week_of_days, all_articles)

    all_articles = fill_null_date_vals(week_of_days, all_articles)

    #now we're ready to make a dataframe!
    df_aa = pd.DataFrame.from_dict(all_articles, orient="index")

    #sum across the daily counts
    #https://stackoverflow.com/questions/25748683/pandas-sum-dataframe-rows-for-given-columns
    df_aa['week_total'] = df_aa.sum(axis=1)

    #make the title NOT the index. Should do this when creating the frame, instead
    df_aa.reset_index(inplace=True)

    #rename title column. Should do this when creating the frame, instead
    df_aa.rename(columns = {'index' : 'title'}, inplace=True)

    #remove blacklisted titles--pages we don't care about, for these purposes. Although... we could keep them I guess.
    blacklist = ["Main_Page", "Special:", "Category:", "Portal:", "Template:", "Wikipedia:", "Talk:", "User:", "_talk:", "Help:", "File:"]
    df_aa = df_aa[~df_aa['title'].str.contains('|'.join(blacklist))]

    #sort by weekly views
    df_aa.sort_values('week_total', ascending=False, inplace=True)

    #add rank column based on weekly views
    new_rank = range(1, len(df_aa)+1)
    df_aa['rank'] = list(new_rank)

    #reset the index to reflect the final ranking, dropping the existing index this time
    df_aa.reset_index(drop=True, inplace=True)

    #start and end dates for header and edit comment
    header_dates = {'date1' : week_of_days[0]['display_date'],
                    'date7' : week_of_days[6]['display_date']
                        }

    #format the header template
    header = rt_header.format(**header_dates)

    report_rows = [format_row(a, b, c, d, rt_row) #this is messy
      for a, b, c, d
      in zip(df_aa['rank'],
             df_aa['title'],
             df_aa['week_total'],
             df_aa['topk_days'],
                )]

    rows_wiki = ''.join(report_rows)

    output = header + rows_wiki + footer
#     print(output)

    edit_token = get_token(auth1)

    edit_sum = "Popular articles from {date7} to {date1}".format(**header_dates)

    publish_report(output, edit_sum, auth1, edit_token)


