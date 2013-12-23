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
def updateBlockStatus(cursor):
	"""
	Excludes recently blocked users from invitation to TWA, 
	in the event that any newcomers have been blocked since 
	the Snuggle data was downloaded and processed.
	"""
	update_query = query.getQuery("twa blocked")
	cursor.execute(update_query)
	conn.commit()	
	
def updateTalkpageStatus(cursor):
	"""
	Inserts the id of the user's talkpage into the database, 
	in the event that any newcomers have had their talkpage created since 
	the Snuggle data was downloaded and processed.
	"""
	update_query = query.getQuery("twa talkpage")
	cursor.execute(update_query)
	conn.commit()		

def getUsernames(cursor):
	"""
	Returns a list of usernames of candidates for invitation:
	newcomers who joined in the past two days and who have not been blocked.
	"""
	select_query = query.getQuery("twa invites")
	cursor.execute(select_query)
	rows = cursor.fetchall()
	candidates = [(row[0],row[1]) for row in rows]
	return candidates

# 
def talkpageCheck(c, header):
	"""
	Skips invitation if the user's talkpage has any of the following strings.
	These include keywords embedded in templates for level 4 user warnings, 
	other serious warnings, and Teahouse invitations:
	
	'uw-vandalism4', 'uw-socksuspect', 'Socksuspectnotice', 'Uw-socksuspect', 
	'sockpuppetry', 'Teahouse', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4'
	"""
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

def allow_bots(text, user):
	"""
	Assures exclusion compliance, 
	per http://en.wikipedia.org/wiki/Template:Bots
	"""
	return not re.search(r'\{\{(nobots|bots\|(allow=none|deny=.*?' + user + r'.*?|optout=all|deny=all))\}\}', text, flags=re.IGNORECASE)

def inviteGuests(cursor, invites):
	"""
	Invites todays invitees.
	"""
	invite_errs = []
	for i in invites:
		try:
			output = hb_profiles.Profiles(params['output namespace'] + i, settings = params)	
			try:	
				quargs = ["invited", MySQLdb.escape_string(i)] #puts it back in the wonky db format to match user_name
			except: #escape string sometimes triggers an encoding error
				quargs = ["invited", i] 
# 				traceback.print_exc()	
			invite = output.formatProfile({'user' : i})					
			edit_summ = "{{subst:PAGENAME}}, you are invited on a Wikipedia Adventure!"
			output.publishProfile(invite, params['output namespace'] + i, edit_summ, edit_sec = "new")		
			updateDB(cursor, "update invite status", quargs)
		except:
			invite_errs.append(i)
# 			traceback.print_exc()
	return invite_errs	

def recordSkips(cursor, skips):	
	"""
	Records users who were skipped because of talkpage templates, or
	because there was an error sending or recording their invitation.
	"""	
	for s in skips:	
		try:
			quargs = ["skipped", MySQLdb.escape_string(s)]			
			updateDB(cursor, "update invite status", quargs)
		except:
# 			traceback.print_exc()
			pass			

def updateDB(cursor, query_name, quargs):
	"""
	Updates the database: was the user invited, or skipped?
	"""	
	try:
		update_query = query.getQuery(query_name, query_vars = quargs)
		cursor.execute(update_query)
		conn.commit()		
	except:
# 		traceback.print_exc()
		pass

##MAIN##
wiki = wikitools.Wiki(hostbot_settings.apiurl)
wiki.login(hostbot_settings.username, hostbot_settings.password)
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()
tools = hb_profiles.Toolkit()
query = hb_queries.Query()
param = hb_output_settings.Params()
params = param.getParams('twa invites')

updateBlockStatus(cursor)
updateTalkpageStatus(cursor)
invites, skips = [], []
candidates = getUsernames(cursor)
for c in candidates:
	skip = talkpageCheck(c, params['headers'])
	if skip:
		skips.append(c[0])
	else:
		invites.append(c[0])
invite_errs = inviteGuests(cursor, invites)
skips.extend(invite_errs) #if I couldn't invite for some reason, add to skip list
recordSkips(cursor, skips)

cursor.close()
conn.close()