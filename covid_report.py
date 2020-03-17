#! /usr/bin/env python

from datetime import datetime, timedelta
import hb_config
import mwapi
from mwapi.errors import APIError
import requests
from requests_oauthlib import OAuth1
import pandas as pd
import json

#code from https://.com/mediawiki-utilities/python-mwapi
def get_template_mems(template):
# If passed a `continuation` parameter, returns an iterable over a continued query.
# On each iteration, a new request is made for the next portion of the results.
    continued = session.get(
        formatversion=2,
        action='query',
        generator='transcludedin',
        gtinamespace = "0",
        gtiprop= "title",
        gtishow = "!redirect",
        titles= template,
        gtilimit=500,  # 100 results per request
        continuation=True)

    pages = []
    try:
        for portion in continued:
            if 'query' in portion:
                for page in portion['query']['pages']:
                    pages.append(page['title'])
            else:
                print("MediaWiki returned empty result batch.")
    except APIError as error:
        raise ValueError(
            "MediaWiki returned an error:", str(error)
        )

    return pages

def api_call(endpoint, parameters): #I don't need this
    try:
        call = requests.get(endpoint, params=parameters)
        response = call.json()
    except:
        response = None
    return response

def get_latest_rev(page_title):
                #https://en.wikipedia.org/w/api.php?action=parse&prop=sections&format=json&formatversion=2&page=Whidbey_Island
    ENDPOINT = 'https://en.wikipedia.org/w/api.php'

    params = {'action' : 'query',
                'prop' : 'revisions',
                'titles' : page_title,
                'format' : 'json',
                'formatversion' : 2,
                }

    page_data = api_call(ENDPOINT, params)
#     pprint(page_data)

    try:
        latest_rev = page_data['query']['pages'][0]['revisions'][0]['revid']
    except:
        print("unable to retrieve latest revision for " + page_title)
        latest_rev = None

    return latest_rev

def get_quality_score(revision):
    #https://ores.wikimedia.org/v3/scores/enwiki/866126465/wp10?features=true
    ENDPOINT = 'https://ores.wikimedia.org/v3/scores/enwiki/'

    params = {'models' : 'wp10',
                'revids' : revision,
                }

    page_data = api_call(ENDPOINT, params)
#     pprint(page_data)

    try:
        prediction = page_data['enwiki']['scores'][str(revision)]['wp10']['score']['prediction']
#     print(prediction)

    except:
        print("unable to retrieve ORES score for " + str(revision))
        prediction = None

    return prediction

def get_pageviews(article_params):
#sample https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user/Zeng_Guang/daily/20200314/20200314
    q_template= "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user/{title}/daily/{startdate}/{enddate}"
    q_string = q_template.format(**article_params)
#     print(q_string)
    response = requests.get(q_string).json()
#     print(response)
    try:
        views = response['items'][0]['views']
    except:
        views = None

    return views

def format_row(rank, title, views, prediction, row_template):

    table_row = {'view rank': rank,
           'title' : title.replace("_"," "),
            'views' : views,
            'prediction' : prediction,
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

def publish_report(output, auth1, edit_token):
    """
    Accepts the page text, credentials and edit token
    Publishes the formatted page text to the specified wiki
    """
    response = requests.post(
    url = "https://en.wikipedia.org/w/api.php", #TODO add to config
    data={
        'action': "edit",
        'title': "User:HostBot/COVID-19_article_report", #TODO add to config
        'section': "1",
        'summary': "testing automated COVID-19 reports", #TODO add to config
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

    session = mwapi.Session('https://en.wikipedia.org/')

    cat = 'Template:2019–20 coronavirus pandemic'

    mems = get_template_mems(cat)
#     print(mems)

    #put these in a dataframe
    df_pandemic = pd.DataFrame(mems)

    df_pandemic.rename(columns = {0 : 'page title'}, inplace=True) #should do this when we create the df

    latest_revs = []
    scores = []

    for row in df_pandemic['page title']:
    #     print(dfd_test['event_pageTitle'])
    #     print(get_latest_rev(row))

        latest = get_latest_rev(row)
        latest_revs.append(latest)
        scores.append(get_quality_score(latest))

    # Add the scores and revs into the dataframe
    lrs = pd.Series(latest_revs)
    ss = pd.Series(scores)

    df_pandemic.insert(loc=1, column = 'latest revision', value = lrs)
    df_pandemic.insert(loc=2, column = 'quality prediction', value = ss)

    #get recent pageviews
    sample_date = {'startdate': datetime.strftime(datetime.now() - timedelta(1), '%Y')
               + datetime.strftime(datetime.now() - timedelta(1), '%m')
               + datetime.strftime(datetime.now() - timedelta(1), '%d'),
               'enddate' : datetime.strftime(datetime.now() - timedelta(1), '%Y')
               + datetime.strftime(datetime.now() - timedelta(1), '%m')
               + datetime.strftime(datetime.now() - timedelta(1), '%d'),
            }

    views = []

    for row in df_pandemic['page title']:
    #     print(dfd_test['event_pageTitle'])
    #     print(get_latest_rev(row))

        q_params = sample_date
        q_params.update(title = row)
        v = get_pageviews(q_params)
        views.append(v)

    vs = pd.Series(views)

    df_pandemic.insert(loc=3, column = 'views', value = vs)

    df_pandemic.sort_values('views', ascending=False, inplace=True)

    rank = range(1, len(df_pandemic)+1)

    df_pandemic['rank'] = list(rank)

    rt_header = """== COVID-19 article status on {year}-{month}-{day} ==
All articles that transclude the [[:Template:2019–20_coronavirus_pandemic|COVID-19 template]].

Last updated on ~~~~~

{{| class="wikitable sortable"
!Pageview rank
!Article
!Page views
!Predicted quality class
"""

    rt_row = """|-
    |{view rank}
    |[[{title}|{title}]]
    |{views}
    |{prediction}
    """

    report_rows = [format_row(x, y, z, a, rt_row)
              for x, y, z, a
              in zip(df_pandemic['rank'],
                     df_pandemic['page title'],
                     df_pandemic['views'],
                     df_pandemic['quality prediction'],
                        )]

    rows_wiki = ''.join(report_rows)

    sd_components = {'year': datetime.strftime(datetime.now() - timedelta(1), '%Y'),
       'month' : datetime.strftime(datetime.now() - timedelta(1), '%m'),
       'day': datetime.strftime(datetime.now() - timedelta(1), '%d'),
            }

    header = rt_header.format(**sd_components)

    output = header + rows_wiki + "|}"

    edit_token = get_token(auth1)

    publish_report(output, auth1, edit_token)

