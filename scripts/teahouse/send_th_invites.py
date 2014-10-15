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
import random
import traceback
import wikitools

###FUNCTIONS###


def getSample(cursor, qstring):
	"""
	Returns a list of usernames and ids of candidates for invitation:
	newcomers who joined in the past two days, 
	who have made at least 5 edits, and who have not been blocked.
	"""
	cursor.execute(qstring)
	rows = cursor.fetchall()
	sample_set = [(row[0],row[1], row[2]) for row in rows]
# 	candidates = candidates[:10]
	return sample_set

def runSample(user_list, message, send_invite = True):
	for c in user_list:
		invited = False
		output = hb_profiles.Profiles(params['output namespace'] + c[0], id = c[2], settings = params)
		invitable = talkpageCheck(c[2], output)
		if send_invite:
			invited = inviteGuests(c, output, message[1])
		updateDB(c[1], "update th invite status", message[0], int(invited), int(invitable))	
				
def inviteGuests(c, output, message_text):
	"""
	Invites todays newcomers.
	"""
	invited = False
	invite = output.formatProfile({'inviter' : random.choice(params['inviters']), 'message' : message_text})
	edit_summ = c[0] + params["edit summary"]
	try:
		output.publishProfile(invite, params['output namespace'] + c[0], edit_summ, edit_sec = "new")
		invited = True
	except:
		print "something went wrong trying to invite " + c[0]	
	return invited

def talkpageCheck(talkpage_id, output):
	"""checks talk pages"""
	invitable = True
	if talkpage_id is not None:
		talkpage_text = output.getPageText()
		for template in params['skip templates']:
			if template in talkpage_text:
				invitable = False		
	return invitable	

def updateDB(user_id, qstring, sample_group, invited, invitable):
	"""
	Updates the database: was the user invited, or skipped?
	"""
	try:
		qvars = [sample_group, invited, invitable, user_id]
		query = queries.getQuery(qstring, qvars)
		cursor.execute(query)
		conn.commit()	
	except:
		print "something went wrong with " + str(user_id)	


##MAIN##
wiki = wikitools.Wiki(hostbot_settings.apiurl)
wiki.login(hostbot_settings.username, hostbot_settings.password)
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()
# tools = hb_profiles.Toolkit()
queries = hb_queries.Query()
param = hb_output_settings.Params()
params = param.getParams('th invites')

cursor.execute(queries.getQuery("th add talkpage")) #Inserts the id of the user's talkpage into the database
conn.commit()

sample_set = getSample(cursor, queries.getQuery("th invitees"))
controls = random.sample(sample_set, 50) #hold back invites from 50 users
candidates = [x for x in sample_set if x not in controls]
runSample(controls, ("control",""), send_invite = False)
runSample(candidates, random.choice(params['messages']))

# for c in control:
# 	invited = False
# 	output = hb_profiles.Profiles(params['output namespace'] + c[0], id = c[2], settings = params)
# 	invitable = talkpageCheck(c[2], output)
# 	updateDB(c[1], "update th invite status", "control", int(invited), int(invitable))
# 
# for c in candidates:
# 	invited = False
# 	output = hb_profiles.Profiles(params['output namespace'] + c[0], id = c[2], settings = params)
# 	message = random.choice(params['messages'])	
# 	invitable = talkpageCheck(c[2], output)
# 		if invitable:
# 			invited = inviteGuests(c, output, message[1])
# 			updateDB(c[1], "update th invite status", message[0], int(invited), int(invitable))		

cursor.execute(queries.getQuery("th add talkpage")) #Inserts the id of the user's talkpage into the database
conn.commit()

cursor.close()
conn.close()