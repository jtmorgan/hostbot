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
import sys
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
# 	sample_set = sample_set[:5]
	return sample_set

def runSample(sub_sample, send_invite):
	for s in sub_sample:
		output = hb_profiles.Profiles(params['output namespace'] + s[0], id = s[2], settings = params)
		invited = False
		skip = talkpageCheck(s[2], output)
		if send_invite:
			message = random.choice(params['messages'])
			if not skip:
				inviteGuests(s, output, message[1])
				invited = True
		else:
			message = ("control","")
		updateDB(s[1], "update th invite status", message[0], int(invited), int(skip))

def inviteGuests(s, output, message_text):
	"""
	Invites todays newcomers.
	"""
	invite = output.formatProfile({'inviter' : random.choice(params['inviters']), 'message' : message_text})
	edit_summ = s[0] + params["edit summary"]
	try:
		output.publishProfile(invite, params['output namespace'] + s[0], edit_summ, edit_sec = "new")
	except:
		print "something went wrong trying to invite " + s[0]

def talkpageCheck(talkpage_id, output):
	"""checks talk pages"""
	skip = False
	if talkpage_id is not None:
		talkpage_text = output.getPageText()
		for template in params['skip templates']:
			if template in talkpage_text:
				skip = True
	return skip

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
params = param.getParams(sys.argv[1]) #now passing in 'which' invites so I can run it for both TH and Co-op

# cursor.execute(queries.getQuery("generate TH invitee list"))
cursor.execute(queries.getQuery("th add talkpage")) #Inserts the id of the user's talkpage into the database
conn.commit()

candidates = getSample(cursor, queries.getQuery("th invitees"))
if sys.argv[1] == 'coop_invites': #args passed in via jsub and cron need to be a single string
    candidates = random.sample(candidates, 25) #pull 50 users out randomly
# candidates = [x for x in sample_set]
# candidates = [x for x in sample_set if x not in controls]
# runSample(controls, False)
runSample(candidates, True)

cursor.execute(queries.getQuery("th add talkpage")) #Inserts the id of the user's talkpage into the database
conn.commit()

cursor.close()
conn.close()