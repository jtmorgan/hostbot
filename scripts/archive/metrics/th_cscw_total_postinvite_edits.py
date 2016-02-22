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

import datetime
import MySQLdb

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf' )
cursor = conn.cursor()

def getRows(cursor):
	
	cursor.execute('''select guest_userid, invite_date, user_talkpage, invite_week from th_yr_1_ret_sample''')

	rows = cursor.fetchall()
	return rows

#get cumulative post_invite edits
def getCumEdits(cursor, rows):

	for row in rows:
		user = row[0]
		date = row[1]
		cursor.execute ('''UPDATE th_yr_1_ret_sample AS th, (SELECT rev_user, count(rev_id) AS cum_revs FROM enwiki.revision WHERE rev_user = %s AND DATE(DATE_FORMAT(rev_timestamp,'%s')) > '%s' AND rev_page NOT IN (SELECT page_id FROM th_pages)) AS tmp SET th.postinv_edits = tmp.cum_revs WHERE th.guest_userid = tmp.rev_user''' % (user, '%Y%m%d%H%i%s', date))
		conn.commit()
		
#gets ns0 edits
def getNs0Edits(cursor, rows):

	for row in rows:
		user = row[0]
		date = row[1]
		cursor.execute ('''UPDATE th_yr_1_ret_sample AS th, (SELECT rev_user, count(rev_id) AS cum_revs FROM enwiki.revision as r, enwiki.page as p WHERE rev_user = %s AND p.page_namespace = 0 AND r.rev_page = p.page_id AND DATE(DATE_FORMAT(rev_timestamp,'%s')) > '%s') AS tmp SET th.pi_ns0_edits = tmp.cum_revs WHERE th.guest_userid = tmp.rev_user''' % (user, '%Y%m%d%H%i%s', date))
		conn.commit()

#gets talk ns edits, to other people's talk pages
def getTalkNsEdits(cursor, rows):

	for row in rows:
		user = row[0]
		date = row[1]
		talkpage = row[2]
		cursor.execute ('''UPDATE th_yr_1_ret_sample AS th, (SELECT rev_user, count(rev_id) AS cum_revs FROM enwiki.revision as r, enwiki.page as p WHERE rev_user = %s AND p.page_namespace IN (1, 3, 5) AND p.page_id != %s AND r.rev_page = p.page_id AND DATE(DATE_FORMAT(rev_timestamp,'%s')) > '%s') AS tmp SET th.pi_talk_edits = tmp.cum_revs WHERE th.guest_userid = tmp.rev_user''' % (user, talkpage, '%Y%m%d%H%i%s', date))
		conn.commit()

#gets weeks with edits
def getWeeksWithEdits(cursor, rows):

	for row in rows:
		user = row[0]
		proj_week = row[3]
		cursor.execute ('''update th_yr_1_ret_sample as th, (select rev_user, count(weeks) AS weeks_with_edits FROM (SELECT rev_user, weekofyear(DATE_FORMAT(rev_timestamp,'%s')) AS weeks, count(rev_id) FROM enwiki.revision WHERE weekofyear(DATE_FORMAT(rev_timestamp,'%s')) >= %s and rev_user = %s and rev_page not in (select page_id from th_pages) GROUP BY weeks) AS tmp1) AS tmp set th.pi_weeks_editing = tmp.weeks_with_edits where th.guest_userid = tmp.rev_user''' % ('%Y%m%d%H%i%s', '%Y%m%d%H%i%s', proj_week, user))
		conn.commit()

#gets num articles edited
def getArEdited(cursor, rows):

	for row in rows:
		user = row[0]
		date = row[1]
		cursor.execute ('''UPDATE th_yr_1_ret_sample AS th, (SELECT rev_user, count(distinct rev_page) AS cum_revs FROM enwiki.revision as r, enwiki.page as p WHERE rev_user = %s AND p.page_namespace = 0 AND r.rev_page = p.page_id AND DATE(DATE_FORMAT(rev_timestamp,'%s')) > '%s') AS tmp SET th.pi_ar_edited = tmp.cum_revs WHERE th.guest_userid = tmp.rev_user''' % (user, '%Y%m%d%H%i%s', date))
		conn.commit()
		
##main##
editor_rows = getRows(cursor)
getCumEdits(cursor, editor_rows)
getNs0Edits(cursor, editor_rows)
getTalkNsEdits(cursor, editor_rows)
getWeeksWithEdits(cursor, editor_rows)
getArEdited(cursor, editor_rows)

cursor.close()
conn.close()				
		