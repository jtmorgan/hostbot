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

report_title = settings.rootpage + '/Hosts/Database_reports#Daily_Report'

report_template = u'''==Daily Report==

===Highly active new editors===
Below is a list of editors who joined within the last 24 hours, have since made more than 10 edits, and were not blocked at the time the report was generated.
 
{| class="wikitable sortable plainlinks"
|-
! Guest #
! Guest Name
! Edit Count
! Email enabled?
! Contribs
! Already Invited?
|-
%s
|}


===New Autoconfirmed Editors===
Below is a list of editors who gained [[Wikipedia:User_access_levels#Autoconfirmed_users|autoconfirmed status]] today, who were not previously invited to Teahouse after their first day, and were not blocked at the time the report was generated.
 
{| class="wikitable sortable plainlinks"
|-
! Guest #
! Guest Name
! Edit Count
! Email enabled?
! Contribs
! Already Invited?
|-
%s
|}

{{Wikipedia:Teahouse/Layout-end}}
{{Wikipedia:Teahouse/Host navigation}}
'''

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf' )
cursor = conn.cursor()


#adding talkpage ids for users whose talkpage was created by the invitation
cursor.execute('''
UPDATE jmorgan.th_up_invitees as i, enwiki.page as p
SET i.user_talkpage = p.page_id, i.ut_is_redirect = p.page_is_redirect
WHERE date(i.sample_date) = date(NOW())
AND i.user_talkpage is null
AND p.page_namespace = 3
AND REPLACE(i.user_name, " ", "_") = p.page_title;
''')
conn.commit()


cursor.execute('''
SELECT user_talkpage 
FROM th_up_invitees 
WHERE user_talkpage is not null
AND invite_status = 0
AND date(sample_date) = (select * from (select date(MAX(sample_date)) from th_up_invitees) as tmp); 
''')

#check for links to Teahouse rather than templates and updates accordingly
rows = cursor.fetchall()
for row in rows:
	user_talkpage = row[0]
	cursor2 = conn.cursor()
	cursor2.execute('''
SELECT pl_from 
FROM enwiki.pagelinks 
WHERE pl_namespace = 4 
AND pl_from = %s 
AND pl_title = "Teahouse"
LIMIT 1;
''' % user_talkpage)
	invite_link_check = cursor2.fetchall()
	if not invite_link_check:
		pass
	else:
		teahouse_link = str(invite_link_check[0])
		if len(teahouse_link) > 0:
			cursor2.execute('''
	update th_up_invitees set invite_status = 1 where invite_status = 0 and user_talkpage = %s;
	''' % user_talkpage)
			conn.commit()
	cursor2.close()		


#brand new editors report
cursor.execute('''
SELECT
id,
user_name,
user_editcount,
email_status,
invite_status,
hostbot_skipped
FROM th_up_invitees
WHERE sample_type = 1
AND ut_is_redirect != 1
AND date(sample_date) = (select * from (select date(MAX(sample_date)) from th_up_invitees) as tmp);
''')

output1 = []
fields = cursor.fetchall()
for field in fields:
	number = field[0]
	user_name = unicode(field[1], 'utf-8')	
	user_editcount = field[2]
	email_status = field[3]
	email_string = "No"
	if email_status is not None:
		email_string = '[[Special:EmailUser/%s|Yes]]' % user_name
	invite_status = field[4]	
	skipped_status = field[5]
	invite_string = ""
	if invite_status == 1:
		invite_string = "invited"
	elif skipped_status == 1:
		invite_string = "skipped"
	talk_page = '[[User_talk:%s|%s]]' % (user_name, user_name)
	user_contribs = '[[Special:Contributions/%s|contribs]]' % user_name
	email_user = '[[Special:EmailUser/%s|Yes]]' % user_name
	table_row = u'''| %d
| %s
| %d
| %s
| %s
| %s
|-''' % (number, talk_page, user_editcount, email_string, user_contribs, invite_string)
	output1.append(table_row)


# newish editors report
cursor.execute('''
	SELECT 
	id, 
	user_name,
	user_editcount,	
	email_status,
	invite_status,
	hostbot_skipped
	FROM th_up_invitees
	WHERE sample_type = 2
	AND ut_is_redirect != 1	
	AND date(sample_date) = (select * from (select date(MAX(sample_date)) from th_up_invitees) as tmp);	
''')

output2 = []
fields = cursor.fetchall()
for field in fields:
	number = field[0]
	user_name = unicode(field[1], 'utf-8')	
	user_editcount = field[2]
	email_status = field[3]
	email_string = "No"
	if email_status is not None:
		email_string = '[[Special:EmailUser/%s|Yes]]' % user_name
	invite_status = field[4]
	skipped_status = field[5]
	invite_string = ""
	if invite_status == 1:
		invite_string = "invited"
	elif skipped_status == 1:
		invite_string = "skipped"			
	talk_page = '[[User_talk:%s|%s]]' % (user_name, user_name)
	user_contribs = '[[Special:Contributions/%s|contribs]]' % user_name
	table_row = u'''| %d
| %s
| %d
| %s
| %s
| %s
|-''' % (number, talk_page, user_editcount, email_string, user_contribs, invite_string)
	output2.append(table_row)


report = wikitools.Page(wiki, report_title)
report_text = report_template % ('\n'.join(output1), '\n'.join(output2))
report_text = report_text.encode('utf-8')
report.edit(report_text, section=1, summary="automatic update of invitee status by [[User:HostBot|HostBot]]", bot=1)

cursor.close()

conn.close()
	

