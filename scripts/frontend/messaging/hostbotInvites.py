#! /usr/bin/python

# Copyright 2012 Jtmorgan

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

import MySQLdb
import wikitools
import settings
# import os
from random import choice
from datetime import datetime
import urllib2 as u2
import urllib
import re
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()

logging.basicConfig(filename='/home/jmorgan/hostbot/logs/invites.log',level=logging.INFO)

##GLOBAL VARIABLES##
curtime = str(datetime.utcnow())
page_namespace = 'User_talk:'
headers = { 'User-Agent' : 'HostBot (http://github.com/jtmorgan/hostbot; jtmorgan25@gmail.com)' }

# lists to track who received a hostbot invite
invite_list = []
skip_list = []

# the basic invite template
invite_template = u'{{subst:Wikipedia:Teahouse/HostBot_Invitation|personal=I hope to see you there! [[User:%s|%s]] ([[w:en:WP:Teahouse/Hosts|I\'m a Teahouse host]])%s}}'

# list of hosts who have volunteered to have their usernames associated with HostBot invites
curHosts = ['Rosiestep','Jtmorgan','SarahStierch','Ryan Vesey','Writ Keeper','Doctree','Osarius','Hajatvrc','Nathan2055','Benzband','Theopolisme','TheOriginalSoni','Ushau97']


# strings associated with substituted templates that mean I should skip this guest
skip_templates = ['uw-vandalism4', 'uw-socksuspect', 'Socksuspectnotice', 'Uw-socksuspect', 'sockpuppetry', 'Teahouse', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4']


##FUNCTIONS##

#gets a list of today's editors to invite
def getUsernames(cursor):
	cursor.execute('''
	SELECT
	user_name, user_talkpage
	FROM th_up_invitees
	WHERE date(sample_date) = date(NOW())
	AND invite_status = 0
	AND ut_is_redirect != 1
	''')
	rows = cursor.fetchall()

	return rows


# selects a host to personalize the invite from curHosts[]
def select_host(curHosts):
	host = choice(curHosts)

	return host


# checks to see if the user's talkpage has any templates that would necessitate skipping
def talkpageCheck(guest, header):
	skip_test = False
	try:
		tp = wikitools.Page(wiki, 'User_talk:' + guest)
		contents = unicode(tp.getWikiText(), 'utf8')
		for template in skip_templates:
			if template in contents:
				skip_test = True
		allowed = allow_bots(contents, settings.username)
		if not allowed:
			skip_test = True
	except:
		logging.info('Guest ' + guest + ' failed on talkpageCheck ' + curtime)

	return skip_test


##checks for exclusion compliance, per http://en.wikipedia.org/wiki/Template:Bots
def allow_bots(text, user):
	return not re.search(r'\{\{(nobots|bots\|(allow=none|deny=.*?' + user + r'.*?|optout=all|deny=all))\}\}', text, flags=re.IGNORECASE)

#invites guests
def inviteGuests(cursor):
	for invitee in invite_list:
		host = select_host(curHosts)
		invite_title = page_namespace + invitee
		invite_page = wikitools.Page(wiki, invite_title)
		invite_text = invite_template % (host, host, '|signature=~~~~')
		invite_text = invite_text.encode('utf-8')
		try:
			invite_page.edit(invite_text, section="new", sectiontitle="== {{subst:PAGENAME}}, you are invited to the Teahouse ==", summary="Automatic invitation to visit [[WP:Teahouse]] sent by [[User:HostBot|HostBot]]", bot=1)
		except:
			logging.info('Guest ' + invitee + ' failed on invitation ' + curtime)
			continue
		try:
# 			invitee = MySQLdb.escape_string(invitee)
			cursor.execute('''update jmorgan.th_up_invitees set invite_status = 1, hostbot_invite = 1, hostbot_personal = 1 where user_name = %s ''', (invitee,))
			conn.commit()
		except UnicodeDecodeError:
			logging.info('Guest ' + invitee + ' failed on invite db update due to UnicodeDecodeError ' + curtime)
			continue

#records the users who were skipped
def recordSkips(cursor):
	for skipped in skip_list:
		try:
# 			skipped = MySQLdb.escape_string(skipped)
			cursor.execute('''update jmorgan.th_up_invitees set hostbot_skipped = 1 where user_name = %s ''', (skipped,))
			conn.commit()
		except:
			logging.info('Guest ' + skipped + ' failed on skip db update ' + curtime)
			continue


##MAIN##
rows = getUsernames(cursor)
for row in rows:
	has_template = False
	guest = row[0]
	if row[1] is not None: # and not bad_encoding
		has_template = talkpageCheck(guest, headers)
	else:
		pass
	if has_template:
		skip_list.append(guest)
	else:
		invite_list.append(guest)
inviteGuests(cursor)
invited = len(invite_list)
skipped = len(skip_list)
logging.info('HostBot invited ' + str(invited) + ' guests on ' + curtime)
recordSkips(cursor)
logging.info('HostBot skipped ' + str(skipped) + ' guests on ' + curtime)


# print ("invited: ", invite_list)
# print ("skipped: ", skip_list)
# 
# #updates Wikipedia:Teahouse/Hosts/Database_reports
# os.system("/usr/bin/python $HOME/hostbot/scripts/frontend/reporting/invitecheck.py")

cursor.close()
conn.close()