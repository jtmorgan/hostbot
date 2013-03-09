#! /usr/bin/env python

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

####settings#####
import MySQLdb
import urllib2
import wikitools
import settings
from BeautifulSoup import BeautifulStoneSoup as bss
from BeautifulSoup import BeautifulSoup as bs
from datetime import datetime
import logging
import time


wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()

logging.basicConfig(filename='/home/jmorgan/logs/moves.log',level=logging.INFO)

##global variables and output templates
curtime = str(datetime.utcnow())
api_url = u'http://en.wikipedia.org/w/api.php?action=parse&page=Wikipedia%%3A%s&prop=sections&format=xml'
index_url = u'http://en.wikipedia.org/w/index.php?title=Wikipedia%%3A%s&action=raw&section=%s'

###CLASSES###
#assigns the variables, based on what kind of move it is
class Params:
	def __init__(self):
			self.ns = u'Wikipedia:'
			self.frpg = ('Teahouse/Host_landing', 'Teahouse/Host_breakroom')
			self.topg = ('Teahouse/Host_breakroom', 'Teahouse/Host_landing')
			self.frpg_tem = ('=Hosts=\n{{TOC hidden}}\n\n<br/>\n</noinclude>\n%s', '= Hosts on Sabbatical =\n{{TOC left}}\n</div>\n<br/>\n%s')
			self.topg_tem = '%s\n'
			self.frpg_cmt = (u'HostBot is automatically moving profiles for currently inactive hosts to [[WP:Teahouse/Host_breakroom]]', u'HostBot is automatically moving profiles of recently active hosts to [[WP:Teahouse/Host_landing]]')
			self.topg_cmt = (u'HostBot is automatically moving profiles for currently inactive hosts from [[WP:Teahouse/Host_landing]]', u'HostBot is automatically moving profiles of recently active hosts from [[WP:Teahouse/Host_breakroom]]')
			self.db_up = ((0,1), (1,0))	


###NOTES
 # mv_to is whether this is a deactivate or a reactivate. 0 = deactivate (move to breakroom), 1 = reactivate (move to host_landing). mv_add is whether this edit action is adding content to a page (True) or effectively removing it (False) by only adding back what was NOT moved.

###FUNCTIONS###
def urlEncode(url):
	reps = {'_':'+', '/':'%2F', ' ':'+'}
	for j, k in reps.iteritems():
		url = url.replace(j, k)	
	return url	


##UPDATE HOST ACTIVITY
#clears edit counts, profile status and in breakroom status. Makes sure that new and newly-moved hosts are featured
def clearStatus():
	cursor.execute('UPDATE th_up_hosts SET num_edits_2wk = 0, in_breakroom = 0, has_profile = 0')
	conn.commit()
	cursor.execute('UPDATE th_up_hosts SET featured = 0 WHERE featured = 1 AND join_date < DATE_SUB(NOW(),INTERVAL 14 DAY) AND (last_move_date < DATE_SUB(NOW(),INTERVAL 14 DAY) OR last_move_date IS NULL)')
	conn.commit()
	

#adds metadata of newly-joined hosts to db, if there are any
def addNewHosts():
	cursor.execute('''
	INSERT IGNORE INTO th_up_hosts
		(user_name, user_id, join_date, in_breakroom, featured, colleague) 
		SELECT rev_user_text, rev_user, STR_TO_DATE(rev_timestamp, '%s'), 0, 1, 0
		FROM enwiki.revision 
		WHERE rev_page = 36794919
		AND rev_user != 0
		AND rev_comment = "/* {{subst:REVISIONUSER}} */ new section";
	''' % "%Y%m%d%H%i%s")
	conn.commit()	
	rowsaffected = cursor.rowcount
	if rowsaffected > 0:
		#adding in talkpage id for new hosts
		cursor.execute('''
		UPDATE th_up_hosts AS t, enwiki.page AS p SET t.user_talkpage = p.page_id WHERE p.page_namespace = 3 AND REPLACE(t.user_name," ","_") = p.page_title AND t.user_talkpage IS NULL
		''')
		conn.commit()

#gets latest edit for all hosts
def updateLastEdit():
	cursor.execute('''
	UPDATE th_up_hosts AS h,
	(SELECT h.user_id, MAX(r.rev_timestamp) AS latest_rev
		FROM enwiki.revision AS r, th_up_hosts AS h, th_pages AS p
			WHERE STR_TO_DATE(r.rev_timestamp, '%s') > h.join_date
			AND r.rev_user = h.user_id
			AND r.rev_page = p.page_id
			GROUP BY h.user_id ORDER BY latest_rev DESC) AS tmp
		SET h.latest_edit = STR_TO_DATE(latest_rev, '%s')
			WHERE h.user_id = tmp.user_id;
	''' % ("%Y%m%d%H%i%s", "%Y%m%d%H%i%s"))
	conn.commit()	
	
#updates the revision_counts for all hosts. features the top hosts.
def updateHostEditCounts():	
	cursor.execute('''UPDATE th_up_hosts AS h, (SELECT rev_user, COUNT(rev_id) AS recent_edits FROM enwiki.revision AS r, th_pages AS p WHERE rev_user IN (SELECT user_id FROM th_up_hosts) AND r.rev_page = p.page_id AND r.rev_timestamp > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 14 DAY),'%s') GROUP BY rev_user) AS tmp 
	SET h.num_edits_2wk = tmp.recent_edits WHERE h.user_id = tmp.rev_user;
	''' % "%Y%m%d%H%i%s")
	conn.commit()
	cursor.execute('UPDATE th_up_hosts AS h, (SELECT user_id FROM th_up_hosts ORDER BY num_edits_2wk DESC LIMIT 10) AS tmp SET h.featured = 1 WHERE h.featured = 0 AND h.user_id = tmp.user_id')
	conn.commit()	#marks the most active hosts as featured		

##FIND HOST PROFILES
#gets the host profile metadata
def getSectionData(api_url, mv_to):
	sec_list = []
	page = urlEncode(Params().frpg[mv_to])
# 	for i, j in reps.iteritems():
# 		page = page.replace(i, j)
	url = api_url % (page)		
# 	print url
	usock = urllib2.urlopen(url)
	sections = usock.read()
	usock.close()
	soup = bss(sections, selfClosingTags = ['s'])
	for x in soup.findAll('s',toclevel="2"):
		profile = (x['index'], x['line'])
# 		print profile
		sec_list.append(profile)	
	return sec_list

#checks for duplicate profiles
def dupe_check(list1, list2):
	dupe_profiles = []
	for item in list1:
		name = item[1]
		if name in(x[1] for x in list2):
			dupe_profiles.append(name)
	if len(dupe_profiles) > 0:
		logging.info('DUPLICATES: duplicate profiles for ' + ' '.join(dupe_profiles) + ' ' + curtime)	# would be nice to do this within-lists, too.
		
#writes these operations to the database
#clears the slate
def updateHostTable(list1, list2, list3):
	cursor.execute('''
UPDATE th_up_hosts
	SET has_profile = 0 WHERE user_name NOT IN (%s)
''' % ('"' + '", "'.join(item[1] for item in list1) + '"'))
	conn.commit()
#updates the 'in_breakroom' status, based on profile
	cursor.execute('''
UPDATE th_up_hosts SET has_profile = 1, in_breakroom = 1 WHERE user_name in (%s)
''' % ('"' + '", "'.join(item[1] for item in list2) + '"'))
	conn.commit()
	cursor.execute('''
UPDATE th_up_hosts SET has_profile = 1, in_breakroom = 0 WHERE user_name in (%s)
''' % ('"' + '", "'.join(item[1] for item in list3) + '"'))
	conn.commit()			

##DEACTIVATE HOSTS
# gets the hosts who should have their profiles moved from the database
def findUsersToMove(mv_to): #whether this is a move to or from the breakroom
	move_list = []
	if mv_to == 0:
		cursor.execute('''
			SELECT
			user_name
			FROM th_up_hosts
			WHERE num_edits_2wk = 0
			AND in_breakroom = 0
			AND has_profile = 1
			AND join_date IS NOT NULL;
			''')
	elif mv_to == 1:
		cursor.execute('''
			SELECT
			user_name
			FROM th_up_hosts
			WHERE num_edits_2wk > 0
			AND in_breakroom = 1
			AND has_profile = 1
			AND join_date IS NOT NULL;
			''')
	else:
		pass				
	rows = cursor.fetchall()
	if rows:
		for row in rows:
			user = unicode(row[0],'utf-8')
			move_list.append(user)
	else: 
		if mv_to == 0:
			logging.info('No moves to breakroom today' + curtime)	
		elif mv_to == 1:
			logging.info('No moves to host landing today' + curtime)
		else:
			pass						
	return move_list

#identifies those sections that need to be moved (either way)	
##VALIDATE
def getSectionsToMove(profile_list, user_list): #gets our list of profiles that exist from above, and our lists of people to be moved from findUsersToMove
	move_list = []
	for item in profile_list:
		if item[1] in user_list:
			move_list.append(item)
	return move_list

#collects the profile text based on lists
def getProfileText(mv_lst, mv_to, mv_add):
	page_from = urlEncode(Params().frpg[mv_to])
	page_to = urlEncode(Params().topg[mv_to])	
# 	#first, gets text for the profiles to be moved
	i = 0
	prof_text_list = []
	while i < len(mv_lst):
		sec = mv_lst[i][0]
		url = index_url % (page_from, sec)
# 		print url
		usock = urllib2.urlopen(url)
		text = usock.read()
		usock.close()
		text = unicode(text, 'utf8')
		text = text.strip()
		prof_text_list.append(text + '\n\n')
		i += 1
	#then, appends the first profile off the move to page
	if mv_add:
		sec = 2	#assumes first profile is always in section 2
		url = index_url % (page_to, sec)
		usock = urllib2.urlopen(url)
		text = usock.read()
		usock.close()
		text = unicode(text, 'utf8')
		text = text.strip()
		prof_text_list.append(text + '\n')		
	return prof_text_list

#moves profiles
def moveProfiles(profiles, mv_to, mv_add):
	if mv_add:
		sec = 2
		template = Params().topg_tem
		comment = Params().topg_cmt[mv_to]
		path = Params().ns + Params().topg[mv_to]
			
	else:
		sec = 1	
		template = Params().frpg_tem[mv_to]
		comment = Params().frpg_cmt[mv_to]
		path = Params().ns + Params().frpg[mv_to]
	wikipage = wikitools.Page(wiki, path)
	edit_profiles = template % '\n'.join(profiles)
	edit_profiles = edit_profiles.encode('utf-8')
# 	print path
# 	print sec
# 	print comment
# 	print edit_profiles
	wikipage.edit(edit_profiles, section=sec, summary=comment, bot=1)
		
#writes this operation to the database
def updateStatus(sub_list, mv_to):	
	featured = Params().db_up[mv_to][0]
	breakroom = Params().db_up[mv_to][1]	
	for user in sub_list:
		cursor.execute('''UPDATE th_up_hosts
		set featured = %s, in_breakroom = %s, last_move_date = NOW()
		where user_name = "%s";
	''' % (featured, breakroom, user))
		conn.commit()

###MAIN###
##UPDATE HOST ACTIVITY
clearStatus() #checked
addNewHosts() #checked
updateLastEdit() #checked
updateHostEditCounts() #checked

##FIND HOST PROFILES
hl_profiles = getSectionData(api_url, 0)
hb_profiles = getSectionData(api_url, 1)
all_profiles = hb_profiles + list(set(hl_profiles) - set(hb_profiles))
dupe_check(hl_profiles, hb_profiles)
updateHostTable(all_profiles, hb_profiles, hl_profiles)

##DEACTIVATE HOSTS
users_to_mv = findUsersToMove(0)
if users_to_mv:
	hl_profiles = getSectionData(api_url, 0)
	users_to_move = getSectionsToMove(hl_profiles, users_to_mv)
	users_to_keep = [item for item in hl_profiles if item not in users_to_move]	
	profiles_move = getProfileText(users_to_move, 0, True)
	profiles_keep = getProfileText(users_to_keep, 0, False)	
	moveProfiles(profiles_move, 0, True)	
	moveProfiles(profiles_keep, 0, False)		
	updateStatus(users_to_mv, 0) 
else:
	pass

# time.sleep(60) #delay to let api and db catch up
# 
# ##REACTIVATE HOSTS
# users_to_mv = findUsersToMove(1)
# if users_to_mv:
# 	hb_profiles = getSectionData(api_url, 1)
# 	users_to_move = getSectionsToMove(hb_profiles, users_to_mv)
# 	users_to_keep = [item for item in hb_profiles if item not in users_to_move]
# 	profiles_move = getProfileText(users_to_move, 1, True)
# 	profiles_keep = getProfileText(users_to_keep, 1, False)
# 	moveProfiles(profiles_move, 1, True)
# 	time.sleep(60) #delay to let api and db catch up
# 	moveProfiles(profiles_keep, 1, False)
# 	updateStatus(users_to_mv, 1) 
# else:
# 	pass

cursor.close()
conn.close()
