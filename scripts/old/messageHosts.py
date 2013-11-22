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
import wikitools
import hostbot_settings
from datetime import datetime
import re
import logging

wiki = wikitools.Wiki(hostbot_settings.apiurl)
wiki.login(hostbot_settings.username, hostbot_settings.password)
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()

logging.basicConfig(filename='/data/project/hostbot/bot/logs/reminders.log',level=logging.INFO)

##GLOBAL VARIABLES##
curtime = str(datetime.utcnow())
page_namespace = 'User_talk:'

# lists to track who needs a reminder
recipients = []

# the reminder template
message_template = u'{{subst:Wikipedia:Teahouse/Host_reminder|sign=~~~~}}'

##FUNCTIONS##
#gets a list of today's editors to invite
def getUsernames(cursor):
	cursor.execute('''
	SELECT
	user_name
	FROM th_up_hosts
	WHERE date(last_move_date) = DATE(NOW())
	AND in_breakroom = 1
	AND has_profile = 1
	AND num_edits_2wk = 0
	AND colleague = 0
	AND no_spam = 0;
	''')
	rows = cursor.fetchall()
	if rows:
		return rows
	else:
		pass

# checks to see if the user's talkpage has any nobots templates
def talkpageCheck():
	global recipients
	for name in recipients:
		try:
			tp = wikitools.Page(wiki, 'User talk:' + name)
			contents = unicode(tp.getWikiText(), 'utf8')
			allowed = allow_bots(contents, hostbot_settings.username)
			if not allowed:
				logging.info('REMIND: Nobots! Reminder to User:' + name + ' not delivered ' + curtime)
				recipients.remove(name)
		except:
			logging.info('REMIND: Reminder to User:' + name + ' failed on talkpageCheck at ' + curtime)

##checks for exclusion compliance, per http://en.wikipedia.org/wiki/Template:Bots
def allow_bots(text, user):
	return not re.search(r'\{\{(nobots|bots\|(allow=none|deny=.*?' + user + r'.*?|optout=all|deny=all))\}\}', text, flags=re.IGNORECASE)

#invites guests
def messageUsers():
	for name in recipients:
		page_title = page_namespace + name
		page = wikitools.Page(wiki, page_title)
		try:
			page.edit(message_template, section="new", sectiontitle="== {{ {{{|safesubst:}}}ROOTPAGENAME}}, we moved your Teahouse host profile ==", summary="Automatic host notification from [[WP:Teahouse]] sent by [[User:HostBot|HostBot]]", bot=1)
		except:
			logging.info('REMIND: Reminder to User:' + name + ' failed at to send at ' + curtime)
			continue

##MAIN##
rows = getUsernames(cursor)
if rows:
	for row in rows:
		name = row[0]
		recipients.append(name)
	talkpageCheck()
	messageUsers()
# 	print recipients
	logging.info('REMIND: Sent reminders to ' + ' '.join(recipients) + ' ' + curtime)

else:
	logging.info('REMIND: No reminders today ' + curtime)

cursor.close()
conn.close()






