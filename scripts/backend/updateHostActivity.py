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

import MySQLdb
import hostbot_settings
from warnings import filterwarnings

###FUNCTIONS###
def updateProfiles():
	"""
	Adds new profiles in, if there are any. Logs any new profiles.
	"""
	cursor.execute('''
	INSERT IGNORE INTO th_up_hosts
		(user_name, user_id, join_date, in_breakroom, featured, colleague, no_spam)
		SELECT rev_user_text, rev_user, STR_TO_DATE(rev_timestamp, '%s'), 0, 1, 0, 0
		FROM enwiki_p.revision
		WHERE rev_page = 36794919
		AND rev_user != 0
		AND rev_comment = "/* {{subst:REVISIONUSER}} */ new section";
	''' % ("%Y%m%d%H%i%s",))
	conn.commit()
	rowsaffected = cursor.rowcount
	if rowsaffected > 0:
		#adding in talkpage id for new hosts
		cursor.execute('''
		UPDATE th_up_hosts AS t, enwiki_p.page AS p SET t.user_talkpage = p.page_id WHERE p.page_namespace = 3 AND REPLACE(t.user_name," ","_") = p.page_title AND t.user_talkpage IS NULL;''')
		conn.commit()	
#add in edits in past 2 weeks
	cursor.execute('''
UPDATE  th_up_hosts a
        LEFT JOIN 
        (
            SELECT  rev_user_text, COUNT(*) RecentRevs 
            FROM    enwiki_p.revision
            WHERE   rev_timestamp > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 14 DAY), '%s')
            AND rev_page IN (SELECT page_id FROM th_pages)
            GROUP   BY rev_user_text
        ) b ON a.user_name = b.rev_user_text
SET     a.num_edits_2wk = COALESCE(b.RecentRevs, 0);
	''' % ("%Y%m%d%H%i%s",))
	conn.commit()	

###MAIN###
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=True, charset="utf8")
cursor = conn.cursor()
filterwarnings('ignore', category = MySQLdb.Warning)
updateProfiles()
cursor.close()
conn.close()
