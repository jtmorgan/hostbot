#! /usr/bin/env python

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
from random import shuffle

###FUNCTIONS####
def updateActiveStatus(cursor):
	cursor.execute('''SELECT user_id, sample_date from twa_invitees''')
	rows = cursor.fetchall()
	for row in rows:
		('''UPDATE twa_invitees t, (SELECT rev_user, MAX(rev_timestamp) ts FROM enwiki.revision WHERE rev_user = %d) tmp SET t.has_subsequent_edit = CASE
		WHEN tmp.ts > %s THEN 1
		ELSE 0
		END
		WHERE t.user_id = tmp.rev_user''' % (row[0], row[1],))
		conn.commit()

def getVisitors(cursor):
	visitors = []
	cursor.execute('''select user_id, sample_date, from twa_invitees where sample_group = "exp" and invited = 1 and twa_played = 1''')
	rows = cursor.fetchall()
	for row in rows:
		user = (row[0], row[1])
		visitors.append(user)
	return visitors

def getControls(cursor, visitors, group, invited):
	control = []
	control
	for v in visitors:
		cursor.execute ('''SELECT user_id, sample_date from twa_invitees where sample_group = "%s" and invited = %d and twa_played is null and sample_date = %s order by rand() limit 1''' % (group, v[1], invited))
		r = cursor.fetchone()
		user = (r[0], r[1])
		control.append(user)
	return control	

def makeSample(cursor, visitors, control_a, control_b):
	all_sample = []
	all_sample.extend(visitors, control_a, control_b)
	all_sample_ids = [u[0] for u in all_sample]	
	shuffle(all_sample_ids)
	for i in all_sample_ids:
		cursor.execute ('''INSERT IGNORE INTO twa_editors_reverts (user_id) VALUES (%d)''' % (i),)
		conn.commit()
		
###MAIN###
conn = MySQLdb.connect(host = 'db1047.eqiad.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf' )
cursor = conn.cursor()
updateActiveStatus(cursor)
# visitors = getVisitors(cursor)
# control_a = getControls(cursor, visitors, "con", 0)
# control_b = getControls(cursor, visitors, "exp", 1)
# makeSample(cursor, visitors, control_a, control_b)
cursor.close()
conn.close()				
		