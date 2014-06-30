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

from datetime import datetime
import hb_output_settings
import hb_profiles
import hb_queries
import hostbot_settings
import MySQLdb
from random import choice
import re
import traceback
import wikitools

###FUNCTIONS###
def updateTalkpageStatus(cursor, qstring):
	"""
	Inserts the id of the user's talkpage into the database,
	in the event that any newcomers have had their talkpage created since
	the Snuggle data was downloaded and processed.
	"""
	cursor.execute(qstring)
	conn.commit()

def getUsernames(cursor, qstring):
	"""
	Returns a list of usernames of candidates for invitation:
	newcomers who joined in the past two days and who have not been blocked.
	"""
	cursor.execute(qstring)
	rows = cursor.fetchall()
	candidates = [(row[0],row[1]) for row in rows]
# 	candidates = candidates[:50]
# 	candidates.append(('Bgkavinga', 34905179))
	return candidates


def inviteGuests(c, params):
	"""
	Invites todays invitees.
	"""
	invited = False
	skip = False
# 	try:
	output = hb_profiles.Profiles(params['output namespace'] + c[0], id = c[1], settings = params)
	if c[1] is not None:
		print c[1]
		talkpage_text = output.getPageText()
		for template in params['skip templates']:
			if template in talkpage_text:
				skip = True
		allowed = allowBots(talkpage_text, "HostBot")
		if not allowed:
			skip = True
	if not skip:							
		invite = output.formatProfile({'user' : c[0], 'inviter' : choice(params['inviters']),}, True)
		edit_summ = c[0] + params["edit summary"]
		output.publishProfile(invite, params['output namespace'] + c[0], edit_summ, edit_sec = "new")
		invited = True
# 	except:
# 		print "something went wrong in InviteGuests"	
	return invited
	
def allowBots(text, user):
	"""
	Assures exclusion compliance,
	per http://en.wikipedia.org/wiki/Template:Bots
	"""
	return not re.search(r'\{\{(nobots|bots\|(allow=none|deny=.*?' + user + r'.*?|optout=all|deny=all))\}\}', text, flags=re.IGNORECASE)	

def updateInviteStatus(cursor, qname, invited, c):
	"""
	Updates the database: was the user invited, or skipped?
	"""
	if invited:
		try:
			qvars = [1, 1, 0, MySQLdb.escape_string(c[0])] #puts it back in the wonky db format to match user_name
		except: #escape string sometimes triggers an encoding error
			qvars = [1, 1, 0, c[0]]
# 				traceback.print_exc()	
	else:
		try:
			qvars = [0, 0, 1, MySQLdb.escape_string(c[0])] #puts it back in the wonky db format to match user_name
		except: #escape string sometimes triggers an encoding error
			qvars = [0, 0, 1, c[0]]
# 				traceback.print_exc()
	query = queries.getQuery(qname, qvars)
	cursor.execute(query)
	conn.commit()

##MAIN##
wiki = wikitools.Wiki(hostbot_settings.apiurl)
wiki.login(hostbot_settings.username, hostbot_settings.password)
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()
tools = hb_profiles.Toolkit()
queries = hb_queries.Query()
param = hb_output_settings.Params()
params = param.getParams('th invites')
invitees = []

updateTalkpageStatus(cursor, queries.getQuery("th add talkpage"))
candidates = getUsernames(cursor, queries.getQuery("th invitees"))
for c in candidates:
# 	try:
	invited = inviteGuests(c, params)
	updateInviteStatus(cursor, "update th invite status", invited, c)
# 	except:
# 		print "something went wrong with " + c[0]					

cursor.close()
conn.close()