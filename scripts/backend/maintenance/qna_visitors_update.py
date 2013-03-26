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

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf' )

cursor = conn.cursor()

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

cursor.execute('''
update th_up_all_visitors_qna
	set week = week(fv_datetime,7)
	where week is null;
''')
conn.commit()

cursor.close()
conn.close()


