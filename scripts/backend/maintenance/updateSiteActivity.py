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

conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()

##FUNCTIONS##
def updateQuestions(cursor):
	cursor.execute('''
	insert ignore into th_up_questions
		(rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, post_date)
		select rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, str_to_date(rev_timestamp, '%Y%m%d%H%i%s')
		from enwiki_p.revision
		where rev_page = 34745517
		and rev_comment like "New question:%";
	''')
	conn.commit()

def updateAnswers(cursor):
	cursor.execute('''
	insert ignore into th_up_answers
		(rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, q_date)
		select rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, str_to_date(rev_timestamp, '%s')
		from enwiki_p.revision
		where rev_page = 34745517
		and rev_comment not like '%s' and rev_user_text not like '%s' and rev_minor_edit = 0;
	''' % ("%Y%m%d%H%i%s", "New question:%", "%Bot"))
	conn.commit()

def updateProfiles(cursor):
	cursor.execute('''
	insert ignore into th_up_profiles
		(rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, post_date)
		select rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, str_to_date(rev_timestamp, '%Y%m%d%H%i%s')
		from enwiki_p.revision
		where rev_page in (35844019, 35844104)
		and rev_comment like "/* {{subst:REVISIONUSER}} */ new section";
	''')
	conn.commit()

def updateQnaVisitors(cursor):
	cursor.execute('''
	insert ignore into th_up_all_visitors_qna
		(user_id, user_name, user_registration, user_editcount, user_email, rev_count, first_visit_rev, first_visit_date)
	select user_id, user_name, user_registration, user_editcount, user_email, count(rev_id), min(rev_id), min(rev_timestamp)
	from enwiki_p.user
	inner join enwiki_p.revision
	on user_id = rev_user
	where rev_page = 34745517
	group by user_id;
	''')
	conn.commit()

	cursor.execute('''
	update jmorgan.th_up_all_visitors_qna as t,
		(select rev_user, count(rev_id) as teahouse_revs
		from enwiki_p.revision
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
	insert ignore into th_up_all_visitors_intro
		(user_id, user_name, user_registration, user_editcount, user_email, rev_count, first_visit_rev, first_visit_date)
	select user_id, user_name, user_registration, user_editcount, user_email, count(rev_id), min(rev_id), min(rev_timestamp)
	from enwiki_p.user
	inner join enwiki_p.revision
	on user_id = rev_user
	where (rev_page = 35844019 or rev_page = 35844104)
	group by user_id;
	''')
	conn.commit()

	cursor.execute('''
	update th_up_all_visitors_intro as t,
		(select rev_user, count(rev_id) as teahouse_revs
		from enwiki_p.revision
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
	insert ignore into th_pages (page_id, page_namespace, page_title, page_touched) select page_id, page_namespace, page_title, page_touched from enwiki_p.page where page_namespace in (4,5) and page_title like "Teahouse/%";
	''')
	conn.commit()

##MAIN##
updateQuestions(cursor)
updateAnswers(cursor)
updateProfiles(cursor)
updateQnaVisitors(cursor)
updateGuestbookVisitors(cursor)
updatePagelist(cursor)

cursor.close()
conn.close()


