#! /usr/bin/python2.7

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

import moves
import MySQLdb
import urllib2
import wikitools
import settings
from BeautifulSoup import BeautifulStoneSoup as bss
from BeautifulSoup import BeautifulSoup as bs
from datetime import datetime
import logging
import time

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()
logging.basicConfig(filename='/home/jmorgan/hostbot/logs/moves.log',level=logging.INFO)
curtime = str(datetime.utcnow())
params = moves.Params()

def clearStatus():
	"""clears edit counts, profile, breakroom and featured status.
	Makes sure that new and active hosts are featured.
	"""
	cursor.execute('UPDATE th_up_hosts SET num_edits_2wk = 0, in_breakroom = 0, has_profile = 0, featured = 0')
	conn.commit()


def addNewHosts():
	"""add metadata of newly-joined hosts to db, if there are any
	"""
	cursor.execute('''
	INSERT IGNORE INTO th_up_hosts
		(user_name, user_id, join_date, in_breakroom, featured, colleague, no_spam)
		SELECT rev_user_text, rev_user, STR_TO_DATE(rev_timestamp, '%s'), 0, 1, 0, 0
		FROM enwiki.revision
		WHERE rev_page = 36794919
		AND rev_user != 0
		AND rev_comment = "/* {{subst:REVISIONUSER}} */ new section";
	''' % ("%Y%m%d%H%i%s",))
	conn.commit()
	rowsaffected = cursor.rowcount
	if rowsaffected > 0:
		#adding in talkpage id for new hosts
		cursor.execute('''
		UPDATE th_up_hosts AS t, enwiki.page AS p SET t.user_talkpage = p.page_id WHERE p.page_namespace = 3 AND REPLACE(t.user_name," ","_") = p.page_title AND t.user_talkpage IS NULL''')
		conn.commit()


def urlEncode(url):
	"""encode characters in the url
	"""
	reps = {'_':'+', '/':'%2F', ' ':'+'}
	for j, k in reps.iteritems():
		url = url.replace(j, k)
	return url

def getSectionData(mv_to):
	"""get the section number and name for each profile
	"""
	sec_list = []
	page = urlEncode(params.frpg[mv_to])
# 	for i, j in reps.iteritems():
# 		page = page.replace(i, j)
	url = params.api_url % (page)
# 	print url
	usock = urllib2.urlopen(url)
	sections = usock.read()
	usock.close()
	soup = bss(sections, selfClosingTags = ['s'])
	for x in soup.findAll('s',toclevel="2"):
		profile = (x['index'], x['line'])
# 		print profile
		sec_list.append(profile)
	return sec_list


def dupe_check(list1, list2):
	"""check whether any hosts have profiles in both the host landing and breakroom
	"""
	dupe_profiles = []
	for item in list1:
		name = item[1]
		if name in(x[1] for x in list2):
			dupe_profiles.append(name)
	if len(dupe_profiles) > 0:
		logging.info('DUPLICATES: duplicate profiles for ' + ' '.join(dupe_profiles) + ' ' + curtime)	# would be nice to do this within-lists, too.


def updateHostTable(list1, list2, list3):
	"""update the host table indicating whether each host has a profile,
	and indicates whether that profile is on the landing page or breakroom page
	"""

	cursor.execute('UPDATE th_up_hosts SET has_profile = 0 WHERE user_name NOT IN (%s)' % ('"' + '", "'.join(item[1] for item in list1) + '"'))
	conn.commit()
	cursor.execute('UPDATE th_up_hosts SET has_profile = 1, in_breakroom = 1 WHERE user_name in (%s)' % ('"' + '", "'.join(item[1] for item in list2) + '"'))
	conn.commit()
	cursor.execute('UPDATE th_up_hosts SET has_profile = 1, in_breakroom = 0 WHERE user_name in (%s)' % ('"' + '", "'.join(item[1] for item in list3) + '"'))
	conn.commit()

def updateLastEdit():
	"""get timestamp of latest edit for all hosts
	"""
	cursor.execute('''
	UPDATE th_up_hosts AS h,
	(SELECT h.user_id, MAX(r.rev_timestamp) AS latest_rev
		FROM enwiki.revision AS r, th_up_hosts AS h, th_pages AS p
			WHERE STR_TO_DATE(r.rev_timestamp, '%s') > h.join_date
			AND r.rev_user = h.user_id
			AND r.rev_page = p.page_id
			GROUP BY h.user_id ORDER BY latest_rev DESC) AS tmp
		SET h.latest_edit = STR_TO_DATE(latest_rev, '%s')
			WHERE h.user_id = tmp.user_id;
	''' % ("%Y%m%d%H%i%s", "%Y%m%d%H%i%s"))
	conn.commit()


def updateHostEditCounts():
	"""update the rev counts for all hosts. features the top-contributing hosts.
	"""
	cursor.execute('''UPDATE th_up_hosts AS h, (SELECT rev_user, COUNT(rev_id) AS recent_edits FROM enwiki.revision AS r, th_pages AS p WHERE rev_user IN (SELECT user_id FROM th_up_hosts) AND r.rev_page = p.page_id AND r.rev_timestamp > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 14 DAY),'%s') GROUP BY rev_user) AS tmp
	SET h.num_edits_2wk = tmp.recent_edits WHERE h.user_id = tmp.rev_user;
	''' % ("%Y%m%d%H%i%s",))
	conn.commit()
	cursor.execute('UPDATE th_up_hosts AS h, (SELECT user_id FROM th_up_hosts WHERE has_profile = 1 ORDER BY num_edits_2wk DESC LIMIT 20) AS tmp SET h.featured = 1 WHERE h.featured = 0 AND h.user_id = tmp.user_id')
	conn.commit()


def findUsersToMove(mv_to): #whether this is a move to or from the breakroom
	"""gets a list of profiles to move between pages
	"""
	move_list = []
	cursor.execute(params.mv_queries[mv_to])
	rows = cursor.fetchall()
	if rows:
		for row in rows:
			user = unicode(row[0],'utf-8')
			move_list.append(user)
	else:
		logging.info(params.nomv_log[mv_to] + curtime)
	return move_list


def getSectionsToMove(profile_list, user_list):
	"""combine profile metadata with list of users to move
	"""
	move_list = []
	for item in profile_list:
		if item[1] in user_list:
			move_list.append(item)
	return move_list


def getProfileText(mv_lst, mv_to, mv_add):
	"""get the content of profiles. first, gets text for the profiles to be moved. then, 	appends the first profile off the target page, if this is edit is adding profiles
	"""
	page_from = urlEncode(params.frpg[mv_to])
	page_to = urlEncode(params.topg[mv_to])
	i = 0
	prof_text_list = []
	while i < len(mv_lst):
		sec = mv_lst[i][0]
		url = params.index_url % (page_from, sec)
# 		print url
		usock = urllib2.urlopen(url)
		text = usock.read()
		usock.close()
		text = unicode(text, 'utf8')
		text = text.strip()
		prof_text_list.append(text + '\n\n')
		i += 1
	if mv_add:
		sec = 2	#assumes first profile is always in section 2
		url = params.index_url % (page_to, sec)
		usock = urllib2.urlopen(url)
		text = usock.read()
		usock.close()
		text = unicode(text, 'utf8')
		text = text.strip()
		prof_text_list.append(text + '\n')
	return prof_text_list


def moveProfiles(profiles, mv_to, mv_add):
	"""edit the profile page
	"""
	if mv_add:
		sec = 2
		template = params.topg_tem
		comment = params.topg_cmt[mv_to]
		path = params.ns + params.topg[mv_to]

	else:
		sec = 1
		template = params.frpg_tem[mv_to]
		comment = params.frpg_cmt[mv_to]
		path = params.ns + params.frpg[mv_to]
	wikipage = wikitools.Page(wiki, path)
	edit_profiles = template % '\n'.join(profiles)
	edit_profiles = edit_profiles.encode('utf-8')
# 	print path
# 	print sec
# 	print comment
# 	print edit_profiles
	wikipage.edit(edit_profiles, section=sec, summary=comment, bot=1)


def updateStatus(sub_list, mv_to):
	"""record the move to the host table
	"""
	breakroom = params.db_up[mv_to]
	for user in sub_list:
		cursor.execute('''UPDATE th_up_hosts SET in_breakroom = %s, last_move_date = NOW() WHERE user_name = "%s"''' % (breakroom, user))
		conn.commit()
	log = params.mv_log[mv_to]
	logging.info(log % ' '.join(sub_list) + curtime)


###MAIN###
clearStatus()
addNewHosts()
hl_profiles = getSectionData(0)
hb_profiles = getSectionData(1)
all_profiles = hb_profiles + list(set(hl_profiles) - set(hb_profiles))
dupe_check(hl_profiles, hb_profiles)
updateHostTable(all_profiles, hb_profiles, hl_profiles)
updateLastEdit()
updateHostEditCounts()
users_to_mv = findUsersToMove(0)
if users_to_mv:
	users_to_move = getSectionsToMove(hl_profiles, users_to_mv)
	users_to_keep = [item for item in hl_profiles if item not in users_to_move]
	profiles_move = getProfileText(users_to_move, 0, True)
	profiles_keep = getProfileText(users_to_keep, 0, False)
	moveProfiles(profiles_move, 0, True)
	moveProfiles(profiles_keep, 0, False)
	updateStatus(users_to_mv, 0)
else:
	pass

cursor.close()
conn.close()
