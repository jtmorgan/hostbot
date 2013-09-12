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

####settings#####
import moves
import MySQLdb
import urllib2
import wikitools
import hostbot_settings
from BeautifulSoup import BeautifulStoneSoup as bss
from BeautifulSoup import BeautifulSoup as bs
from datetime import datetime
import logging
import time

wiki = wikitools.Wiki(hostbot_settings.apiurl)
wiki.login(hostbot_settings.username, hostbot_settings.password)
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()
logging.basicConfig(filename='/data/project/hostbot/bot/logs/moves.log',level=logging.INFO)
curtime = str(datetime.utcnow())
params = moves.Params()

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
users_to_mv = findUsersToMove(1)
if users_to_mv:
	hb_profiles = getSectionData(1)
# 	print hb_profiles
	users_to_move = getSectionsToMove(hb_profiles, users_to_mv)
# 	print users_to_move
	users_to_keep = [item for item in hb_profiles if item not in users_to_move]
# 	print users_to_keep
	profiles_move = getProfileText(users_to_move, 1, True)
# 	for profile in profiles_move:
# 		print(profile + '\n\n')
	profiles_keep = getProfileText(users_to_keep, 1, False)
# 	for profile in profiles_keep:
# 		print(profile + '\n\n')
	moveProfiles(profiles_move, 1, True)
	moveProfiles(profiles_keep, 1, False)
	updateStatus(users_to_mv, 1)
else:
	pass

cursor.close()
conn.close()
