#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
matchbot
~~~~~~~~

MatchBot is a MediaWiki bot that perfoms category-based matching among
pages in a given on-wiki space. In the en.wp Co-op program, it leaves
a message on a Co-op member's profile talk page when it detects a
change in certain categories. This message mentions an appropriately
matched mentor.

To run:
    $ python matchbot <path-to-config-dir>

MatchBot expects to find two files in its containing directory:
time.log, a text file containing a MediaWiki-formatted timestamp that
denotes the last time the bot ran, and config.json, a configuration
file containing settings such as login information, category names, the
mentor who will be the default match if no category-based match can be
made, and the text of the greeting messages to be posted.

MatchBot logs information when a run is complete, when a match is made,
and when an error occurs. Logs are stored in <path-to-config-dir>/log .
"""

import argparse
import datetime
import os
import random
import sys

import mwclient
import sqlalchemy

import mbapi
import mblog
from load_config import filepath, config


requestcats = config['categories']['requestcategories']
mentorcats = config['categories']['mentorcategories']
skillslist = config['categories']['skillslist']
prefix = config['pages']['main']
talkprefix = config['pages']['talk']
optout = config['categories']['optout']
general = config['categories']['general']
defaultmentor = config['defaultmentorprofile']
mentorcat_dict = {k: v for (k, v) in zip(requestcats, mentorcats)}
skills_dict = {k: v for (k, v) in zip(requestcats, skillslist)}


def main():
    # Variables to log
    run_time = datetime.datetime.utcnow()
    edited_pages = False
    wrote_db = False
    logged_errors = False

    try:
        prevruntimestamp = timelog(run_time)
    except Exception as e:
        mblog.logerror(u'Could not get time of previous run', exc_info=True)
        logged_errors = True
        sys.exit()

    # Initializing site + logging in
    login = config['login']
    try:
        site = mwclient.Site((login['protocol'], login['site']),
                             clients_useragent=login['useragent'])
        site.login(login['username'], login['password'])
    except mwclient.LoginError as e:
        mblog.logerror(u'Login failed for {}'.format(login['username']),
                       exc_info=True)
        logged_errors = True
        sys.exit()

    # create a list of learners who have joined since the previous run
    learners = getlearnerinfo(getlearners(prevruntimestamp, site), site)
    mentors, genmentors = getmentors(site)

    for learner in learners:
        try:
            mentorcat = mentorcat_dict[learner['category']]
            mentor = match(mentors[mentorcat], genmentors)
        except Exception as e:
            mblog.logerror(u'Matching failed for {}'.format(
                learner['learner']), exc_info=True)
            logged_errors = True
            continue

        try:
            mname, muid, matchmade = get_match_info(mentor, site)
            print((mname, muid, matchmade))
        except Exception as e:
            mblog.logerror(u'Could not get information for profile {}'.format(
                mentor['profile']), exc_info=True)
            logged_errors = True
            continue

        try:
            invite_info = get_invite_info(learner, mname,
                                                  matchmade, site)
            response = postinvite(invite_info)
            edited_pages = True
        except Exception as e:
            mblog.logerror(u'Could not post match on {}\'s page'.format(
                learner['learner']), exc_info=True)
            logged_errors = True
            continue

        try:
            flowenabled = invite_info[3]
            revid, postid = getrevid(response, flowenabled)
            matchtime = gettimeposted(response, flowenabled)
            cataddtime = parse_timestamp(learner['cattime'])

            mblog.logmatch(luid=learner['luid'],
                           lprofileid=learner['profileid'],
                           muid=muid, category=learner['category'],
                           cataddtime=cataddtime,
                           matchtime=matchtime, matchmade=matchmade,
                           revid=revid, postid=postid, run_time=run_time)
            wrote_db = True
        except Exception as e:
            mblog.logerror(u'Could not write to DB for {}'.format(
                learner['learner']), exc_info=True)
            logged_errors = True
            continue

    try:
        mblog.logrun(run_time, edited_pages, wrote_db, logged_errors)
    except Exception as e:
        mblog.logerror(u'Could not log run at {}'.format(run_time),
                       exc_info=True)


def parse_timestamp(t):
    """Parse MediaWiki-style timestamps and return a datetime."""
    if t == '0000-00-00T00:00:00Z':
        return None
    else:
        return datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')


def getprofiletalkpage(profile):
    """Get the talk page for a profile (a sub-page of the Co-op)."""
    talkpage = talkprefix + profile.lstrip(prefix)
    return talkpage


def timelog(run_time):
    """Get the timestamp from the last run, then log the current time
    (UTC).
    """
    timelogfile = os.path.join(filepath, 'time.log')
    with open(timelogfile, 'r+b') as timelog:
        prevruntimestamp = timelog.read()
        timelog.seek(0)
        timelog.write(datetime.datetime.strftime(run_time,
                                                 '%Y-%m-%dT%H:%M:%SZ'))
        timelog.truncate()
    return prevruntimestamp


def getlearners(prevruntimestamp, site):
    """Get a list of learners who have created profiles since the last
    time this script started running.

    Returns a list of dictionaries, each containing the learner's
    profile pageid, the profile page title, the category, and the
    timestamp corresponding to when the category was added.

    If it is not possible to retrieve the new profiles in a given
    category, it skips that category and logs an error.
    """
    learners = []
    for category in requestcats:
        try:
            newlearners = mbapi.getnewmembers(category, site,
                                              prevruntimestamp)
            for userdict in newlearners:
                # Check that the page is actually in the Co-op
                if userdict['profile'].startswith(prefix):
                    learners.append(userdict)
                else:
                    pass
        except Exception as e:
            mblog.logerror('Could not fetch new profiles in {}'.format(
                category), exc_info=True)
            logged_errors = True
    return learners


def getlearnerinfo(learners, site):
    """Given a list of dicts containing information on learners, add
    the learner's username and userid to the corresponding dict. Return
    the changed list of dicts.

    Assumes that the owner of the profile created the profile.
    """
    for userdict in learners:
        try:
            learner, luid = mbapi.getpagecreator(userdict['profile'], site)
            userdict['learner'] = learner
            userdict['luid'] = luid
        except Exception as e:
            mblog.logerror('Could not get information for {}'.format(
                userdict['profile']), exc_info=True)
            logged_errors = True
            continue
    return learners


def getmentors(site):
    """Using the config data, get lists of available mentors for each
    category, filtering out mentors who have opted out of new matches.

    Return:
        mentors     : dict of lists of mentor names, keyed by mentor
                        category
        genmentors  : list of mentor names for mentors who will mentor
                        on any topic

    Assumes that the owner of the profile created the profile.
    """
    mentors = {}

    nomore = mbapi.getallcatmembers(optout, site)
    allgenmentors = mbapi.getallcatmembers(general, site)
    genmentors = [x for x in allgenmentors if x not in nomore and
                  x['profile'].startswith(prefix)]
    for category in mentorcats:
        try:
            catmentors = mbapi.getallcatmembers(category, site)
            mentors[category] = [x for x in catmentors if x not in nomore and
                                 x['profile'].startswith(prefix)]
        except Exception as e:
            mblog.logerror('Could not fetch list of mentors for {}'.format(
                category), exc_info=True)
            logged_errors = True
            continue
    return (mentors, genmentors)


def match(catmentors, genmentors):
    """Given two lists, return a random choice from the first, or if there
    are no elements in the first return a random choice from the second.
    If there are no elements in either return None.
    """
    if catmentors:
        mentor = random.choice(catmentors)
        return mentor
    elif genmentors:
        mentor = random.choice(genmentors)
        return mentor
    else:
        return None

def get_match_info(mentor, site):
    # if there is no match, leave a message with the default mentor
    # but do not record a true match
    if mentor is None:
        mname, muid = mbapi.getpagecreator(defaultmentor, site)
        matchmade = False
    else:
        mname, muid = mbapi.getpagecreator(mentor['profile'], site)
        matchmade = True
    return (mname, muid, matchmade)


def buildgreeting(learner, mname, skill, matchmade):
    """Create a customized greeting string to be posted to a talk page
    or Flow board to introduce a potential mentor to a learner.

    Return the greeting and a topic string for the greeting post.
    """
    greetings = config['greetings']
    if matchmade:
        greeting = greetings['matchgreeting'].format(mname, skill)
        topic = greetings['matchtopic']
    else:
        greeting = greetings['nomatchgreeting'].format(mname)
        topic = greetings['nomatchtopic']
    return (greeting, topic)


def get_invite_info(learner, mname, matchmade, site):
    """ Docstring placeholder FIXME """
    talkpage = getprofiletalkpage(learner['profile'])
    flowenabled = mbapi.flowenabled(talkpage, site)
    skill = skills_dict[learner['category']]
    greeting, topic = buildgreeting(learner['learner'], mname,
                                    skill, matchmade)
    lname = learner['learner']
    return (talkpage, greeting, topic, flowenabled, lname, site)


def postinvite(invite_info):
    """Post a greeting, with topic, to a page. If Flow is enabled or
    the page does not already exist, post a new topic on a the page's
    Flow board; otherwise, appends the greeting to the page's existing
    text.

    Return the result of the API POST call as a dict.
    """
    pagetitle, greeting, topic, flowenabled, lname, site = invite_info
    if flowenabled or flowenabled is None:
        result = mbapi.postflow(pagetitle, topic, greeting, site)
        return result
    else:
        profile = site.Pages[pagetitle]
        addedtext = config['greetings']['noflowtemplate'].format(
            topic, lname, greeting)
        newpagecontents = '{0} {1}'.format(profile.text(), addedtext)
        result = profile.save(newpagecontents, summary=topic)
        return result


def getrevid(result, isflow):
    """ Get the revid (for a non-Flow page) or the post-revision-id
    (for a Flow page), given the API result for the POST request.

    Return a tuple (revid, post-revision-id). Either revid or
    post-revision-id will be None.
    """
    if 'nochange' in result:
        raise mwclient.APIError  #FIXME (maybe unneeded?)
    elif isflow or isflow is None:
        return (None, result['flow']['new-topic']['committed'][
                'topiclist']['post-revision-id'])
    else:
        return (result['newrevid'], None)


def gettimeposted(result, isflow):
    """Get the time a revision was posted from the API POST result, if
    possible.

    If the page has Flow enabled, the time posted will be approximate.

    If the page does not have Flow enabled, the time will match the
    time in the wiki database for that revision.
    """
    if 'nochange' in result:
        raise mwclient.APIError #FIXME (maybe unneeded?)
    elif isflow or isflow is None:
        return datetime.datetime.utcnow()
    else:
        return parse_timestamp(result['newtimestamp'])


if __name__ == '__main__':
#    parser = argparse.ArgumentParser(description='Generate data for the mobile dashboard.')
#    parser.add_argument('folder', help='folder with config.yaml and *.sql files')
#    parser.set_defaults(folder='./matchbot')
#    args = parser.parse_args()
    # something about load_config here; FIXME
    main()
