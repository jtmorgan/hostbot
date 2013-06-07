#! /usr/bin/env python2.7

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

import sys
import shelve
import query

db = shelve.open('/home/jmorgan/hostbot/data/metrics/queries.db')


query_lib = query.Queries()
query = query_lib.queries
for k, v in query.iteritems():
	db[k] = [v]
		
db.close()	
# try:
#     db[sys.argv[1]] = sys.argv[2]
# finally:
#     db.close()