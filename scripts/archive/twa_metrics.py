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

from datetime import datetime
from datetime import timedelta
import calendar
import hb_profiles
import hb_queries
import hostbot_settings
import json
import MySQLdb
import random
import sys
from warnings import filterwarnings
import wikitools

###FUNCTIONS###
def getSample(recent_newcomers):
	sample_set = []
	date_since = datetime.utcnow()-timedelta(days=1)
	ds_unix = calendar.timegm(date_since.timetuple())
	recent_gf_newcomers = [x for x in recent_newcomers if x['registration'] > ds_unix and x['desirability']['ratio'] >= 4]
	for x in recent_gf_newcomers:
		invite = True
		if x['talk']['threads']:
			for y in x['talk']['threads']:
				if y['trace']:
					trace = y['trace']
					if 'name' in trace and trace['name'] == "teahouse invitation":
						invite = False
		else:
			pass
		if invite:
			sample_set.append(x)
# 	print str(len(sample_set)) + " recent good faith newcomers without teahouse invites" 		
# 	print str(len(recent_gf_newcomers)) + " recent good faith newcomers total"

	return sample_set
		
def updateDB(sample_set):
	group1 = random.sample(sample_set, 50) #first, hold back invites from 100 users as control			
# 	print str(len(group1)) + " control"
	insertSubSample(group1, "con")
	group2 = [x for x in sample_set if x not in group1]
# 	print str(len(group2)) + " experimental"
	insertSubSample(group2, "exp")

def insertSubSample(group, condition):
	sample_data = []
	for user in group:
		try:
			user['name'] = MySQLdb.escape_string(user['name'])
		except: #this sometimes triggers an encoding/decoding error
			pass
		reg = datetime.utcfromtimestamp(int(user['registration'])).strftime('%Y%m%d%H%M%S')
		x = [user['id'], user['name'], reg, user['activity']['counts']['all'], condition, sample_datestring, sample_unixdate]
		sample_data.append(x)
		insert_query = query.getQuery("twa sample", query_vars = x) #needs to be a list
		cursor.execute(insert_query)
		conn.commit()	
	

def dumpSample(sample_set):
	filename = str(sample_unixdate) + ".json"
	path = "/data/project/hostbot/bot/data/twa/"
	with open(path + filename, 'w') as outfile:
		json.dump(sample_set, outfile)	
	
##MAIN##
wiki = wikitools.Wiki(hostbot_settings.apiurl)
wiki.login(hostbot_settings.username, hostbot_settings.password)
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()
filterwarnings('ignore', category = MySQLdb.Warning)

tools = hb_profiles.Toolkit()
query = hb_queries.Query()

f = open('/data/project/hostbot/bot/data/twa/snuggle.json')
data = json.load(f)
f.close()

recent_newcomers = data['success']
sample_datetime = datetime.utcfromtimestamp(data['meta']['time'])
# print sample_datetime
sample_datestring = tools.getSubDate(0)
# print sample_datestring
sample_unixdate = data['meta']['time']
# print sample_unixdate
sample_set = getSample(recent_newcomers)
if len(sample_set) > 50:
	updateDB(sample_set)
	dumpSample(sample_set)	
else:
# 	print "not enough" #need to make this a log instead
	sys.exit("not enough people to invite")
cursor.close()
conn.close()	