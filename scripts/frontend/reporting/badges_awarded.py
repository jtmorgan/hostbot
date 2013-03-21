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
import wikitools
import settings
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

report_title = settings.rootpage + '/Badge/Awarded'

report_template = u'''== Badges awarded ==
Please do not edit this table manually. It is updated daily by [[User:HostBot|HostBot]] and your edits will be overwritten. The page was last updated on {{subst:REVISIONMONTH}}/{{subst:REVISIONDAY}}/{{subst:REVISIONYEAR}} by {{subst:REVISIONUSER}}.
<onlyinclude>
%s badges have been given out so far.

{| class="wikitable sortable plainlinks"
|-
! Badge
! Number of recipients
|-
%s
|}
</onlyinclude>

=== Recently awarded badges ===
{| class="wikitable sortable plainlinks"
|-
! Username
! Badge
! Award date
|-
%s
|}
'''

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()

#adds pages to the badge page list
def updatePageList():
	cursor.execute('INSERT IGNORE INTO th_badges (bpage_title, bpage_id) SELECT page_title, page_id FROM enwiki.page WHERE page_namespace = 4 AND page_title LIKE "Teahouse/Badge/%"')
	conn.commit()

#gets badge pages and titles
def getPages(cursor):
	list = []
	cursor.execute('SELECT bpage_id, bpage_title, b_id FROM th_badges WHERE b_id IS NOT NULL')
	rows = cursor.fetchall()
	for row in rows:
		page = str(row[0])
		page_title = row[1]
		page_title = MySQLdb.escape_string(page_title)
		some_id = str(row[2])
# 		print page_title
		list.append([page, page_title, some_id])
	return list


#finds new links to badges.
def findLinks(cursor, list):
	badges_inserted = 0
	for l in list:
		cursor.execute('''INSERT IGNORE INTO th_up_badges_awarded (b_id, ba_date, ba_page, bap_ns, bap_title) SELECT %s, DATE(NOW()), page_id, page_namespace, page_title FROM enwiki.page AS p, enwiki.pagelinks AS pl WHERE pl.pl_namespace = 4 AND pl.pl_title = "%s" AND p.page_namespace IN (2,3) AND p.page_id = pl.pl_from AND p.page_title NOT LIKE "%s"
	''' % (l[2], l[1], "%/%"))
		conn.commit()
		badges_inserted += cursor.rowcount
# 		print badges_inserted
	return badges_inserted
# 		print cursor._executed


#gets recipient user data
def getUserData(cursor):
		cursor.execute('UPDATE th_up_badges_awarded as t, enwiki.user AS u SET t.user_id = u.user_id, t.user_name = u.user_name, t.user_registration = u.user_registration, t.not_badge = 0 WHERE REPLACE(t.bap_title,"_"," ") = u.user_name AND t.user_id IS NULL')
		conn.commit()


def updateBadgeTable(cursor):
	cursor.execute('UPDATE th_badges AS p, (SELECT b_id, COUNT(ba_id) as num FROM th_up_badges_awarded WHERE bap_ns = 3 AND not_badge = 0 GROUP BY b_id) AS tmp SET p.b_awarded = tmp.num WHERE p.b_id = tmp.b_id')


#print a summary table of badges to Teahouse/Badge/Awarded
def outputBadgeTable(cursor):
	output = [] #list that contains each row for the summary table
	#gets total badge counts for output
	cursor.execute('SELECT SUM(b_awarded) AS sum FROM th_badges WHERE b_id IS NOT NULL AND b_id != 9 AND b_awarded IS NOT NULL')
	row = cursor.fetchone()
	total = row[0] #total badges awarded. all types
	output.append(total)
	#gets individual badge counts for output
	cursor.execute('SELECT b_name, bpage_title, b_awarded FROM th_badges WHERE b_id IS NOT NULL AND b_id != 9 AND b_awarded IS NOT NULL ORDER BY b_awarded DESC')
	rows = cursor.fetchall()
	for row in rows:
		name = row[0]
		title = row[1]
		count = row[2]
		link = '[[Wikipedia:%s|%s]]' % (title, name)
		table_row = u'''| %s
| %s
|-''' % (link, count)
		output.append(table_row)

	output2 = [] #the recent by-user badge table
	cursor.execute('SELECT user_name, b_name, bpage_title, ba_date FROM th_badges as b, th_up_badges_awarded as ba WHERE b.b_id = ba.b_id AND ba.bap_ns = 3 AND ba.b_id != 9 AND ba.user_id IS NOT NULL ORDER BY ba_date DESC LIMIT 100')
	rows = cursor.fetchall()
	for row in rows:
		uname = row[0]
		bname = row[1]
		bpage = row[2]
		bdate = row[3]
		table_row = u'''|[[User_talk:%s|%s]]
| [[WP:%s|%s]]
| %s
|-''' % (uname, uname, bpage, bname, bdate)
		output2.append(table_row)

	#prints the report to WP:Teahouse/Badge/Awarded
	report = wikitools.Page(wiki, report_title)
	report_text = report_template % (output[0], '\n'.join(output[1:]), '\n'.join(output2))
	report_text = report_text.encode('utf-8')
# 	print report_text
	report.edit(report_text, section=1, summary="[[User:HostBot|HostBot]] is updating [[WP:Teahouse/Badge|Badge]] counts", bot=1)


##MAIN##
updatePageList()
badge_list = getPages(cursor)
badges_inserted = findLinks(cursor, badge_list)
if badges_inserted > 0:
	getUserData(cursor)
	updateBadgeTable(cursor)
	outputBadgeTable(cursor)

cursor.close()
conn.close()