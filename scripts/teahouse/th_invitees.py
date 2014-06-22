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
import hb_queries
import hb_templates
import hostbot_settings
import MySQLdb
from warnings import filterwarnings
import wikitools

report_title = hostbot_settings.rootpage + '/Hosts/Database_reports#Daily_Report'

report_template = #fixme

wiki = wikitools.Wiki(hostbot_settings.apiurl)
wiki.login(hostbot_settings.username, hostbot_settings.password)
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()
filterwarnings('ignore', category = MySQLdb.Warning)

# insert 10-edit newbies
cursor.execute("th 10 edit newbies") #call queries
conn.commit()

#insert autoconfirmed editors
cursor.execute("th autoconfirmed newbies")
conn.commit()

#adds in talkpage ids for later link checks
cursor.execute("th sample talkpages")
conn.commit()


#updates the sample type. Used to divide users into experimental and control groups. Now its all experimental, baby.
cursor.execute("update th sample type")
conn.commit()


#builds output list for 10-edit newbies
cursor.execute("get 10 edit newbie list")

output1 = []
fields = cursor.fetchall()
for field in fields:
	number = field[0]
	user_name = unicode(field[1], 'utf-8')
	user_editcount = field[2]
	talk_page = '[[User_talk:%s|%s]]' % (user_name, user_name)
	user_contribs = '[[Special:Contributions/%s|contribs]]' % user_name
	table_row = u'''| %d
| %s
| %d
| %s
|
|-''' % (number, talk_page, user_editcount, user_contribs)
	output1.append(table_row)


#builds output list for autoconfirmed users
cursor.execute("get autoconfirmed newbie list")

output2 = []
fields = cursor.fetchall()
for field in fields:
	number = field[0]
	user_name = unicode(field[1], 'utf-8')
	user_editcount = field[2]
	talk_page = '[[User_talk:%s|%s]]' % (user_name, user_name)
	user_contribs = '[[Special:Contributions/%s|contribs]]' % user_name
	table_row = u'''| %d
| %s
| %d
| %s
|
|-''' % (number, talk_page, user_editcount, user_contribs)
	output2.append(table_row)


#prints reports
queries = hb_queries.Query()
templates = hb_queries.Query()

report = wikitools.Page(wiki, report_title)
report_text = report_template % ('\n'.join(output1), '\n'.join(output2))
report_text = report_text.encode('utf-8')
report.edit(report_text, section=1, summary="Automatic daily invitee report generated by [[User:HostBot|HostBot]].", bot=1)

cursor.close()
conn.close()


