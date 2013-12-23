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
import hb_profiles
import hostbot_settings
import hb_output_settings
import sys

###FUNCTIONS###
def rankProfiles():
	"""
	rank Eval portal profiles by number of recent edits.
	"""
	profile_page = hb_profiles.Profiles(params['output path'], params['output page id'], params)
	profile_list = profile_page.getPageSectionData("2")
	profile_list = tools.dedupeMemberList(profile_list, "index", "title")
	quote1 = "'"
	quote2 = "'"
	profile_names = [x['title'] for x in profile_list]	
	query_list = quote1 + "','".join(name for name in profile_names) + quote2	
	query = "SELECT user_name, num_edits_2wk FROM th_up_hosts WHERE user_name IN (%s);" % query_list	
# 	print query
# 	print type(query)
	cursor.execute(query)
	rows = cursor.fetchall()
	output = [{'edits' : row[1], 'title' : row[0].decode("utf8")} for row in rows]
	for p in profile_list:
		p['text'] = profile_page.getPageText(p['index'])
		p['edits'] = [o['edits'] for o in output if o['title'] == p['title']]
	for p in profile_list:
		if 'edits' not in p:
			p['edits'] = 0
		else:
			pass
	missing_profiles = [o['title'] for o in output if o not in profile_names]			
# 	print missing_profiles
	plist_sorted = sorted(profile_list, key=lambda item: item['edits'], reverse = True)
	plist_text = {'profiles' : '\n'.join([x['text'] for x in plist_sorted])} 
	formatted_profiles = profile_page.formatProfile(plist_text)
	edit_summ = params['edit summary'] % (params['type'],)
	profile_page.publishProfile(formatted_profiles, params['output path'], edit_summ, edit_sec = 1)


###MAIN###
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=True, charset="utf8")
cursor = conn.cursor()
param = hb_output_settings.Params()
params = param.getParams(sys.argv[1])
params['type'] = sys.argv[1]
tools = hb_profiles.Toolkit()
rankProfiles()
cursor.close()
conn.close()
