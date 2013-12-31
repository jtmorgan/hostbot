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

import shelve
import query

"""
this script will load queries into the db. It performs a kind of 'on duplicate key update' functionality too, I believe
"""
db = shelve.open('/home/jmorgan/hostbot/data/metrics/queries.db', writeback=True)
query_list = query.Queries()
query = query_list.queries
for k, v in query.iteritems():
	db[k] = v
db.close()	
