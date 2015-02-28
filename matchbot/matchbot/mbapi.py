#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
mbapi
~~~~~

This module contains customized API calls and associated helper methods
for MatchBot.
"""

import json
import time


def flowenabled(title, site):
    """Find whether Flow is enabled on a given page.
    Parameters:
        title   :   a string containing the page title
        site    :   a mwclient Site object associated with the page

    Returns:
        True    if Flow is enabled on the page
        False   if Flow is not enabled on the page
        None    if the page does not exist
    """
    query = site.api(action='query',
                     titles=title,
                     prop='flowinfo')
    pagedict = query['query']['pages']
    for page in pagedict:
        if page == '-1':
            return None
        else:
            return (u'enabled' in pagedict[page]['flowinfo']['flow'])


def getpagecreator(title, site):
    """ Retrieve user information for the user who made the first edit
    to a page.
    Parameters:
        title   :   a string containing the page title
        site    :   a mwclient Site object associated with the page

    Returns:
        user    :   a string containing the page creator's user name
        userid  :   a string containing the page creator's userid
    """
    query = site.api(action='query',
                     prop='revisions',
                     rvprop='user|userid',
                     rvdir='newer',
                     titles=title,
                     rvlimit=1,
                     indexpageids="")
    pagedict = query['query']['pages']
    for page in pagedict:
        user = pagedict[page]['revisions'][0]['user']
        userid = pagedict[page]['revisions'][0]['userid']
    return (user, userid)


def getnewmembers(categoryname, site, timelastchecked):
    """Get information on all pages in a given category that have been
    added since a given time.

    Parameters:
        category        :   a string containing the category name,
                            including the 'Category:' prefix
        site            :   mwclient Site object corresponding to the
                            desired category
        timelastchecked :   a MediaWiki-formatted timestamp

    Returns:
        a list of dicts containing information on the category members.

    Handles query continuations automatically.
    """
    recentkwargs = {'action': 'query',
                    'list': 'categorymembers',
                    'cmtitle': categoryname,
                    'cmprop': 'ids|title|timestamp',
                    'cmlimit': 'max',
                    'cmsort': 'timestamp',
                    'cmdir': 'older',
                    'cmend': timelastchecked}
    result = site.api(**recentkwargs)
    newcatmembers = makelearnerlist(result, categoryname)

    while True:
        if 'continue' in result:
            newkwargs = recentkwargs.copy()
            for arg in result['continue']:
                newkwargs[arg] = result['continue'][arg]
            result = site.api(**newkwargs)
            newcatmembers = makelearnerlist(result, categoryname,
                                            newcatmembers)
        else:
            break
    return newcatmembers



def makelearnerlist(result, categoryname, catusers=None):
    """Create a list of dicts containing information on each user from
    the getnewmembers API result.

    Parameters:
        result      :   a dict containing the results of the
                        getnewmembers API query
        catusers    :   a list of dicts with information on category
                        members from earlier queries. Optional,
                        defaults to None.

    Returns:
        a list of dicts containing information on the category members
        in the provided query.
    """
    if catusers is None:
        catusers = []
    else:
        pass

    for page in result['query']['categorymembers']:
        userdict = {'profileid': page['pageid'],
                    'profile': page['title'],
                    'cattime': page['timestamp'],
                    'category': categoryname}
        catusers.append(userdict)
    return catusers


def getallcatmembers(category, site):
    """Get information on all members of a given category

    Parameters:
        category:   a string containing the category name, including
                    the 'Category:' prefix
        site    :   mwclient Site object corresponding to the desired
                    category

    Returns:
        a list of dicts containing information on the category members.

    Handles query continuations automatically.
    """
    kwargs = {'action': 'query',
              'list': 'categorymembers',
              'cmtitle': category,
              'cmprop': 'ids|title',
              'cmlimit': 'max'}
    result = site.api(**kwargs)
    catmembers = addmentorinfo(result)

    while True:
        if 'continue' in result:
            newkwargs = kwargs.copy()
            for arg in result['continue']:
                newkwargs[arg] = result['continue'][arg]
            result = site.api(**newkwargs)
            newcatmembers = addmentorinfo(result, catmembers)
        else:
            break
    return catmembers


def addmentorinfo(result, catmembers=None):
    """Create a list of dicts containing information on each user from
    the getallcatmembers API result.

    Parameters:
        result      :   a dict containing the results of the
                        getallmembers API query
        catusers    :   a list of dicts with information on category
                        members from earlier queries. Optional,
                        defaults to [].
    Returns:
        a list of dicts containing information on the category members
        in the provided query.
    """
    if catmembers is None:
        catmembers = []
    else:
        pass

    for page in result['query']['categorymembers']:
        userdict = {'profileid': page['pageid'], 'profile': page['title']}
        catmembers.append(userdict)
    return catmembers


def postflow(page, topic, message, site):
    """Post a new topic to a Flow board.
    Parameters:
        page    :   string containing the title of the page to post to
        topic   :   string containing the new Flow topic
        message :   string containing the message to post in the topic
        site    :   logged-in mwclient Site object corresponding to
                    the page

    Returns the API POST result as a dictionary containing the post's
    metadata.

    If the bot has the appropriate permissions, this will create Flow
    boards on empty pages.
    """
    token = site.get_token('csrf')
    kwargs = {'action': 'flow',
              'page': page,
              'submodule': 'new-topic',
              'token': token,
              'nttopic': topic,
              'ntcontent': message,
              'ntmetadataonly': 'true'}
    query = site.api(**kwargs)
    return query
