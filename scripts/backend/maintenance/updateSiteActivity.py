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

import datetime
import MySQLdb
conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()

##FUNCTIONS##
def updateQuestions(cursor):
	cursor.execute('''
	insert ignore into th_up_questions
		(rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, post_date)
		select rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, str_to_date(rev_timestamp, '%Y%m%d%H%i%s')
		from enwiki.revision
		where rev_page = 34745517
		and rev_comment like "New question:%";
	''')
	conn.commit()

def updateAnswers(cursor):
	cursor.execute('''
	insert ignore into jmorgan.th_up_answers
		(rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, q_date)
		select rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, str_to_date(rev_timestamp, '%s')
		from enwiki.revision
		where rev_page = 34745517
		and rev_comment not like '%s' and rev_user_text not like '%s' and rev_minor_edit = 0;
	''' % ("%Y%m%d%H%i%s", "New question:%", "%Bot"))
	conn.commit()

def updateResponses(cursor):
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

def updateProfiles(cursor):
	cursor.execute('''
	insert ignore into th_up_profiles
		(rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, post_date)
		select rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, str_to_date(rev_timestamp, '%Y%m%d%H%i%s')
		from enwiki.revision
		where rev_page in (35844019, 35844104)
		and rev_comment like "/* {{subst:REVISIONUSER}} */ new section";
	''')
	conn.commit()

def updateQnaVisitors(cursor):
	cursor.execute('''
	insert ignore into jmorgan.th_up_all_visitors_qna
		(user_id, user_name, user_registration, user_editcount, user_email, rev_count, first_visit_rev, first_visit_date)
	select user_id, user_name, user_registration, user_editcount, user_email, count(rev_id), min(rev_id), min(rev_timestamp)
	from enwiki.user
	inner join enwiki.revision
	on user_id = rev_user
	where rev_page = 34745517
	group by user_id;
	''')
	conn.commit()

	cursor.execute('''
	update jmorgan.th_up_all_visitors_qna as t,
		(select rev_user, count(rev_id) as teahouse_revs
		from enwiki.revision
		where rev_page = 34745517
		group by rev_user) as tmp
	set t.rev_count = tmp.teahouse_revs
	where tmp.rev_user = t.user_id;
	''')
	conn.commit()

	cursor.execute('''
	update th_up_all_visitors_qna
		set fv_datetime = str_to_date(first_visit_date, '%Y%m%d%H%i%s')
		where fv_datetime is null;
	''')
	conn.commit()

def updateGuestbookVisitors(cursor):
	cursor.execute('''
	insert ignore into jmorgan.th_up_all_visitors_intro
		(user_id, user_name, user_registration, user_editcount, user_email, rev_count, first_visit_rev, first_visit_date)
	select user_id, user_name, user_registration, user_editcount, user_email, count(rev_id), min(rev_id), min(rev_timestamp)
	from enwiki.user
	inner join enwiki.revision
	on user_id = rev_user
	where (rev_page = 35844019 or rev_page = 35844104)
	group by user_id;
	''')
	conn.commit()

	cursor.execute('''
	update jmorgan.th_up_all_visitors_intro as t,
		(select rev_user, count(rev_id) as teahouse_revs
		from enwiki.revision
		where (rev_page = 35844019 or rev_page = 35844104)
		group by rev_user) as tmp
	set t.rev_count = tmp.teahouse_revs
	where tmp.rev_user = t.user_id;
	''')
	conn.commit()

	cursor.execute('''
	update th_up_all_visitors_intro
		set fv_datetime = str_to_date(first_visit_date, '%Y%m%d%H%i%s')
		where fv_datetime is null;
	''')
	conn.commit()

def updatePagelist(cursor):
	cursor.execute('''
	insert ignore into th_pages (page_id, page_namespace, page_title, page_touched) select page_id, page_namespace, page_title, page_touched from enwiki.page where page_namespace in (4,5) and page_title like "Teahouse/%";
	''')
	conn.commit()

##MAIN##
updateQuestions(cursor)
updateAnswers(cursor)
updateResponses(cursor)
updateProfiles(cursor)
updateQnaVisitors(cursor)
updateGuestbookVisitors(cursor)
updatePagelist(cursor)

cursor.close()
conn.close()


