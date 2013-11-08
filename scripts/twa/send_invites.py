#! /usr/bin/python2.7

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
import re
import wikitools
import hostbot_settings
from random import choice
from datetime import datetime

###FUNCTIONS###
def updateBlockStatus(cursor):
	update_query = query.getQuery("twa blocked")#query not currently working
	print update_query
	cursor.execute(update_query)
	conn.commit()	
	
def updateBlockStatus(cursor):
	update_query = query.getQuery("twa talkpage")#query not currently working
	print update_query
	cursor.execute(update_query)
	conn.commit()		

def getUsernames(cursor):
	select_query = query.getQuery("twa invites")
	print select_query
	cursor.execute(select_query)
	rows = cursor.fetchall()
	candidates = [(row[0],row[1]) for row in rows]
	return invitees

# checks to see if the user's talkpage has any templates that would necessitate skipping
def talkpageCheck(c, header):#not using header right now... why?
	skip_test = False
	if c[1] is not None:
		try:
			profile = hb_profiles.Profiles(params['output namespace'] + c[0], id = c[1])
			text = profile.getPageText()
			for template in params['skip templates']:
				if template in text:
					skip_test = True
			allowed = allow_bots(text, hostbot_settings.username)
			if not allowed:
				skip_test = True
		except:
			print "error on talkpage check"
	else:
		pass		
	return skip_test

##checks for exclusion compliance, per http://en.wikipedia.org/wiki/Template:Bots
def allow_bots(text, user):
	return not re.search(r'\{\{(nobots|bots\|(allow=none|deny=.*?' + user + r'.*?|optout=all|deny=all))\}\}', text, flags=re.IGNORECASE)

#invites guests
def inviteGuests(cursor, invite_list, skip_list):
	for i in invite_list:
		#construct profile object (again?!?) with params
		#format invite
		#format output
		#send to outputter

		try:
			output.publishProfile(invite, params['output path'] + i, edit_summ, edit_sec_title = params['section title'], edit_sec = "new")		
			invite_page.edit(invite_text, section="new", sectiontitle="== {{subst:PAGENAME}}, you are invited to PLAY TWA ==", summary="Automatic invitation to visit [[WP:TWA]] sent by [[User:HostBot|HostBot]]", bot=1)
		except:
			skip_list.append[i]
			continue
		try:
# 			invitee = MySQLdb.escape_string(invitee)
			cursor.execute('''update th_up_invitees set invite_status = 1, hostbot_invite = 1, hostbot_personal = 1 where user_name = %s ''', (invitee,))
			conn.commit()
		except UnicodeDecodeError:
			logging.info('Guest ' + invitee + ' failed on invite db update due to UnicodeDecodeError ' + curtime)
			continue

#records the users who were skipped
def updateDB(cursor, invite_list, skip_list):
	for skipped in skip_list:
		try:
# 			skipped = MySQLdb.escape_string(skipped)
			cursor.execute('''update th_up_invitees set hostbot_skipped = 1 where user_name = %s ''', (skipped,))
			conn.commit()
		except:
			logging.info('Guest ' + skipped + ' failed on skip db update ' + curtime)
			continue


##MAIN##
wiki = wikitools.Wiki(hostbot_settings.apiurl)
wiki.login(hostbot_settings.username, hostbot_settings.password)
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()
tools = hb_profiles.Toolkit()
query = hb_queries.Query()
param = hb_output_settings.Params()
params = param.getParams('twa invites')

invite_list = []
skip_list = []

updateBlockStatus(cursor)
updateTalkpage(cursor)
candidates = getUsernames(cursor)
for c in candidates:
	skip = talkpageCheck(c, params['headers'])
	if skip:
		skip_list.append(c[0])
	else:
		invite_list.append(c[0])
inviteGuests(cursor, invite_list)
updateDB(cursor, invite_list, skip_list)

cursor.close()
conn.close()