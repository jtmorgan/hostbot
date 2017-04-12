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

import datetime
import MySQLdb
import hb_config

conn = MySQLdb.connect(host = hb_config.host, db = hb_config.dbname, read_default_file = hb_config.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()

#gets all questions within past 2 weeks
cursor.execute('''
SELECT rev_id, rev_user_text, rev_timestamp, rev_comment, post_date
	from th_up_questions AS q
	where q.post_date BETWEEN DATE_SUB(NOW(), INTERVAL 14 DAY) AND DATE_SUB(NOW(), INTERVAL 1 DAY)
''')

#get all questions with previous "New question: " edit comment prefix
# cursor.execute('''
# SELECT rev_id, rev_user_text, rev_timestamp, rev_comment, post_date
# 	from th_up_questions AS q
# 	where q.post_date < "2013-09-07 17:22:59"
# ''')

#update questioner responses, host answers, and first answer date columns
rows = cursor.fetchall()
for row in rows:
	rev = row[0]
	user = row[1]
	user = MySQLdb.escape_string(user)
	time = row[2]
	comment = row[3]
	datetime = row[4]
	comment = MySQLdb.escape_string(comment)
	com_substr = comment[:-12] #removes " new section" from comment string
# 	com_substr = comment[14:] #removes "New question: " from comment string
# 	com_substr = "/* " + com_substr + " */"

	cursor.execute ('''
			update th_up_questions as q, (select count(rev_id) as reps, rev_timestamp from th_up_answers where rev_comment like "%s" and rev_user_text = '%s' and str_to_date(rev_timestamp, '%s') > DATE_FORMAT(DATE_ADD('%s', INTERVAL 5 MINUTE), '%s')) as tmp set q.questioner_replies = tmp.reps where q.rev_id = %d
		''' % (com_substr + "%", user, "%Y%m%d%H%i%s", time, "%Y%m%d%H%i%s", rev))
	conn.commit()
	cursor.execute ('''update th_up_questions as q,
					(select MIN(q_date) as first_resp, count(rev_id)
							as asrs
						from th_up_answers
							where rev_comment like "%s"
								and rev_user_text != '%s'and q_date between '%s' and DATE_ADD('%s', INTERVAL 7 DAY))
						as tmp set q.answers = tmp.asrs, q.first_answer_date = tmp.first_resp where q.rev_id = %s;
	''' % (com_substr + "%", user, datetime, datetime, rev))
	conn.commit()

cursor.close()
conn.close()