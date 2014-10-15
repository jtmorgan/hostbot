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

import hostbot_settings
import MySQLdb
from warnings import filterwarnings


def getInvitees():
	"""insert today's potential invitees into the database"""
	q_string = """insert ignore into th_up_invitees_experiment_2
	(user_id, user_name, user_registration, user_editcount, sample_date, sample_type)
	SELECT user_id, user_name, user_registration, user_editcount, NOW(), 1
	FROM enwiki_p.user
	WHERE user_registration > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s')
	AND user_editcount >= 5
	AND user_id NOT IN (SELECT ug_user FROM enwiki_p.user_groups WHERE ug_group = 'bot')
	AND user_name not in (SELECT REPLACE(log_title,"_"," ") from enwiki_p.logging
		where log_type = "block" and log_action = "block"
		and log_timestamp >  DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s'))
	"""

	cursor.execute(q_string)
	conn.commit()

##MAIN##
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()
filterwarnings('ignore', category = MySQLdb.Warning)

getInvitees()

cursor.close()
conn.close()


