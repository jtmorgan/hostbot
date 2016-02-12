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

import hb_queries
import hostbot_settings
import MySQLdb
from warnings import filterwarnings


def getInvitees(q_string, cursor):
	"""insert today's potential invitees into the database"""
	cursor.execute(q_string)
	conn.commit()
	
def addTalkPages(q_string, cursor):
	"""adds their talkpage id (if they have one)"""
	cursor.execute(q_string)
	conn.commit()	

if __name__ == "__main__":
    conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
    cursor = conn.cursor()
    filterwarnings('ignore', category = MySQLdb.Warning)
    queries = hb_queries.Query()

#     getInvitees(queries.getQuery("five edit newbies"), cursor)
#     getInvitees(queries.getQuery("ten edit newbies"), cursor)
#     getInvitees(queries.getQuery("teahouse experiment newbies"), cursor) 
    getInvitees(queries.getQuery("teahouse experiment newbies"), cursor) 
    addTalkPages(queries.getQuery("th add talkpage"), cursor)    
    
    
#     addTalkPages(queries.getQuery("th add talkpage"), cursor)    
       
#     getInvitees(queries.getQuery("autoconfirmed newbies"), cursor)

    cursor.close()
    conn.close()


