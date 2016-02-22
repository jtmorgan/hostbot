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
import wikitools

###FUNCTIONS###
def getUsernames(cursor):
	candidates = []
	select_query = query.getQuery("username encoding test select")
	cursor.execute(select_query)
	rows = cursor.fetchall()
	for row in rows:
		can = row[0]
# 		print can
# 		print can.decode('latin-1')
	candidates.append(can)	
# 	print candidates
	return candidates

def inviteGuests(cursor, invites):
	"""
	Invites todays invitees.
	"""
	invite_errs = []
	for i in invites:
		output = hb_profiles.Profiles(params['output namespace'] + i, settings = params)		
		quargs = ["invited", i.decode('latin-1')] #puts it back in the wonky db format to match user_name
		print quargs
		invite = output.formatProfile({'user' : i})					
		edit_summ = "{{subst:PAGENAME}}, you are invited on a Wikipedia Adventure!"
		try:
			print i	
			updateDB(cursor, "update invite status", quargs)
		except:
			invite_errs.append(i)
	return invite_errs				

def updateDB(cursor, query_name, quargs):
	"""
	Updates the database: was the user invited, or skipped?
	"""	
	update_query = query.getQuery(query_name, query_vars = quargs)
# 	print update_query
	cursor.execute(update_query)
	conn.commit()		
# 	except:
# 		print "couldn't update db for " + quargs[0] + " user " + quargs[1]

##MAIN##
wiki = wikitools.Wiki(hostbot_settings.apiurl)
wiki.login(hostbot_settings.username, hostbot_settings.password)
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=True, charset="latin1")
cursor = conn.cursor()
tools = hb_profiles.Toolkit()
query = hb_queries.Query()
param = hb_output_settings.Params()
params = param.getParams('twa invites')

invites, skips = [], []
candidates = getUsernames(cursor)
for c in candidates:
	invites.append(c)
invite_errs = inviteGuests(cursor, invites)
print invite_errs

cursor.close()
conn.close()