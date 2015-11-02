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

def getSample(cursor, qstring):
	"""
	Returns a list of usernames and ids of candidates for invitation
	"""
	cursor.execute(qstring)
	rows = cursor.fetchall()
	sample_set = [(row[0],row[1], row[2]) for row in rows]
# 	sample_set = sample_set[:10]
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
			message = ("th control","")
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


if __name__ == "__main__":
    wiki = wikitools.Wiki(hostbot_settings.apiurl)
    wiki.login(hostbot_settings.username, hostbot_settings.password)
    conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
    cursor = conn.cursor()
    queries = hb_queries.Query()
    param = hb_output_settings.Params()
    params = param.getParams(sys.argv[1])

    cursor.execute(queries.getQuery("th add talkpage")) #Inserts the id of the user's talkpage into the database
    conn.commit()

    candidates = getSample(cursor, queries.getQuery(params['select query']))
    if sys.argv[1] in ('th_invites', 'twa_invites'):
    #START experiment 11/2
        candidate_count = len(candidates)
        invitee_count = int(candidate_count/2)
        invitees = random.sample(candidates, invitee_count)
        controls = [x for x in candidates if x not in invitees]
    #END BLOCK experiment 11/2    
#         if len(candidates) > 100:
#             candidates = random.sample(candidates, 100) #pull 100 users out randomly
#     elif sys.argv[1] == 'coop_invites':
#         if len(candidates) > 15: #should be parameterized
#             candidates = random.sample(candidates, 15)
    else:
        pass
    runSample(controls, False)
    runSample(invitees, True)

    cursor.execute(queries.getQuery("th add talkpage")) #Inserts the id of the user's talkpage into the database
    conn.commit()

    cursor.close()
    conn.close()