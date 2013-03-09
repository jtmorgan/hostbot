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

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )

cursor = conn.cursor()

#gets all questions from between 1 and 2 weeks ago
cursor.execute('''
SELECT rev_id, rev_user_text, rev_timestamp, rev_comment
	from jmorgan.th_up_questions AS q
	where q.post_date BETWEEN DATE_SUB(NOW(), INTERVAL 14 DAY) AND DATE_SUB(NOW(), INTERVAL 7 DAY)
''')

#gets all questioner responses, host answers, and first answer date
rows = cursor.fetchall()
for row in rows:
	rev = row[0]
	user = row[1]
	user = MySQLdb.escape_string(user)		
	time = row[2]
	comment = row[3]
	comment = MySQLdb.escape_string(comment)
	com_substr = comment[14:]
# 	user_str = unicode(row[1], 'utf-8')
	user = MySQLdb.escape_string(user)
	cursor2 = conn.cursor()
	cursor2.execute ('''
			update th_up_questions as q, (select count(rev_id) as reps, rev_timestamp from th_up_answers where rev_comment like '%s' and rev_user_text = '%s' and str_to_date(rev_timestamp, '%s') > DATE_FORMAT(DATE_ADD('%s', INTERVAL 5 MINUTE), '%s')) as tmp set q.questioner_replies = tmp.reps where q.rev_id = %d 
		''' % ("/* " + com_substr + " */%", user, "%Y%m%d%H%i%s", time, "%Y%m%d%H%i%s", rev))
	conn.commit()
	cursor2.execute ('''update th_up_questions as q, 
					(select MIN(rev_timestamp) as first_resp, count(rev_id) 
							as asrs 
						from th_up_answers
							where rev_comment like '%s' 
								and rev_user_text != '%s')
						as tmp set q.answers = tmp.asrs, q.first_answer_date = str_to_date(tmp.first_resp, '%s') where q.rev_id = %s;
	''' % ("/* " + com_substr + " */%", user, "%Y%m%d%H%i%s", rev))
	conn.commit()	
	cursor2.close()

cursor.close()
conn.close()
	

