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
!Days among top 1000 this week
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

def fill_null_date_vals(day_range, ar_dict):
    """
    Accepts a list of dicts with year, month, and day values
        And a dict with article titles as keys and gaps in the date keys
    Returns the article dictionary with each sub-dict fully populated
        With pageview values for all dates in range, even if val is 0
    """

    #https://www.geeksforgeeks.org/dictionary-methods-in-python-set-2-update-has_key-fromkeys/
    for day_val in day_range:
#         dstr = day_val['year'] + "-" + day_val['month'] + "-" + day_val['day'] #need to stop converting this on the fly
        for v in ar_dict.values():
            v.setdefault(day_val['date'], 0)

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
    all_articles = get_daily_counts(week_of_days, all_articles)

    #fill in missing dict keys with 0 vals
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
    blacklist = ["Main_Page", "Special:", "Category:", "Portal:", "Wikipedia:", "Talk:", "User:", "_talk:", "Help:", "File:"]
    df_aa = df_aa[~df_aa['title'].str.contains('|'.join(blacklist))]

    #sort by weekly views
    df_aa.sort_values('week_total', ascending=False, inplace=True)

    #add rank column based on weekly views
    new_rank = range(1, len(df_aa)+1)
    df_aa['rank'] = list(new_rank)

    #reset the index to reflect the final ranking, dropping the existing index this time
    df_aa.reset_index(drop=True, inplace=True)

    #add a column of days when each article was NOT in the topk, so that we can report the inverse of this
    df_aa['days_not_topk'] = (df_aa == 0).astype(int).sum(axis=1)

    #count days appearing in topk list, from col that reports the inverse
    df_aa['days_in_topk'] = 7 - df_aa['days_not_topk']

    #start and end dates for header and edit comment
    header_dates = {'date1' : week_of_days[0]['date'],
                    'date7' : week_of_days[6]['date']
                        }

    #format the header template
    header = rt_header.format(**header_dates)

    report_rows = [format_row(a, b, c, d, rt_row) #this is messy
      for a, b, c, d
      in zip(df_aa['rank'],
             df_aa['title'],
             df_aa['week_total'],
             df_aa['days_in_topk'],
                )]

    rows_wiki = ''.join(report_rows)

    output = header + rows_wiki + footer
    print(output)

    edit_token = get_token(auth1)

    edit_sum = "Popular articles from {date7} to {date1}".format(**header_dates)

    publish_report(output, edit_sum, auth1, edit_token)


