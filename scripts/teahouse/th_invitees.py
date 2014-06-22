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

import datetime #necessary?
import hb_queries
import hostbot_settings
import MySQLdb
from warnings import filterwarnings

def updateInviteeTable(#query):
# cursor.execute("th 10 edit newbies") #call queries
# conn.commit()
# cursor.execute("th autoconfirmed newbies")
# conn.commit()
# cursor.execute("th sample talkpages")
# conn.commit()
# cursor.execute("update th sample type")
# conn.commit()

##MAIN##
queries = hb_queries.Query()
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()
filterwarnings('ignore', category = MySQLdb.Warning)
updateInviteeTable(#query) # insert 10-edit newbies
updateInviteeTable(#query) #insert autoconfirmed editors
updateInviteeTable(#query) #adds in talkpage ids for later link checks
updateInviteeTable(#query) #updates the sample type. for a/b tests

cursor.close()
conn.close()


