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

import MySQLdb
from datetime import datetime
import logging

conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()

logging.basicConfig(filename='/data/project/hostbot/bot/logs/reminders.log',level=logging.INFO)

 ##GLOBAL VARIABLES AND TEMPLATES
curtime = str(datetime.utcnow())

#determines if anyone has signed up to stop receiving reminders. If so, adds them to "do not spam" list
signup_list = []
cursor.execute('''select rev_user, rev_user_text from enwiki_p.revision WHERE rev_page = 38190470 AND rev_timestamp > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 3 DAY),'%Y%m%d%H%i%s') AND rev_user NOT IN (SELECT user_id FROM th_up_hosts WHERE colleague = 1);
''')
rows = cursor.fetchall()
if rows:
	cursor2 = conn.cursor()
	for row in rows:
		signup = row[0]
		name = row[1]
		signup_list.append(name)
		cursor2.execute('''UPDATE th_up_hosts SET no_spam = 1 WHERE no_spam = 0 AND user_id = %s''' % (signup,))
		conn.commit()
	cursor2.close()
	logging.info('SIGNUP: Signed up ' + ' '.join(signup_list) + ' ' + curtime)
else:
	logging.info('SIGNUP: No signups today ' + curtime)


cursor.close()
conn.close()