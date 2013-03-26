#! /usr/bin/python

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

cursor.execute('''
insert ignore into jmorgan.th_up_answers
	(rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, q_date)
	select rev_id, rev_user, rev_user_text, rev_timestamp, rev_comment, str_to_date(rev_timestamp, '%s')
	from enwiki.revision
	where rev_page = 34745517
	and rev_comment not like '%s' and rev_user_text not like '%s' and rev_minor_edit = 0;
''' % ("%Y%m%d%H%i%s", "New question:%", "%Bot"))
conn.commit()

cursor.execute('''
update th_up_answers
	set week = week(q_date,7)
	where week is null;
''')
conn.commit()

cursor.close()
conn.close()


