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

# from wikitools import category as wtcat
from datetime import datetime, timedelta
import dateutil.parser
import wikitools
import hostbot_settings
import MySQLdb
import hb_output_settings as output_settings
import hb_templates as templates
import operator
# import queries
import re
import time

class Profiles:
	"""A grab-bag of operations you might want to perform on and with profiles."""

	def __init__(self, path, id = False, settings = False):
		"""
		Instantiates page-level variables for building a set of profiles.
		"""
		self.page_path = path
# 		print self.page_path
		if id:
			self.page_id = str(id)
# 			print self.page_id
		if settings:
			self.profile_settings = settings
		self.tools = Toolkit()
		self.wiki = wikitools.Wiki(hostbot_settings.apiurl)
		self.wiki.login(hostbot_settings.username, hostbot_settings.password)

	def getPageSectionData(self, level = False):
		"""
		Returns the section titles and numbers for a given page.
		Sample request: http://meta.wikimedia.org/w/api.php?action=parse&page=Grants:IdeaLab/Introductions&prop=sections&format=jsonfm
		"""
		params = {
			'action': 'parse',
			'page': self.page_path,
			'prop': 'sections',
		}
		req = wikitools.APIRequest(self.wiki, params)
		response = req.query()
		if level:
			secs_list = [{'title' : unicode(x['line']), 'index' : x['index']} for x in response['parse']['sections'] if x['toclevel'] == level]
# 			print secs_list
		else:
			secs_list = [{'title' : unicode(x['line']), 'index' : x['index']} for x in response['parse']['sections']]
		return secs_list

	def getPageText(self, section = False):
		"""
		Gets the raw text of a page or page section.
		Sample: http://meta.wikimedia.org/w/api.php?action=query&prop=revisions&titles=Grants:IdeaLab/Introductions&rvprop=content&rvsection=21&format=jsonfm
		"""
		params = {
			'action': 'query',
			'prop': 'revisions',
			'titles': self.page_path,
			'rvprop' : 'content',
			'rvsection' : section,
		}
		req = wikitools.APIRequest(self.wiki, params)
		response = req.query()
		text = response['query']['pages'][self.page_id]['revisions'][0]['*']
		return text

	def scrapeInfobox(self, member, infobox, redict = False): #gets the relevant param values from text of an infobox
		if redict:
			re_types = redict #this is now very inconsistent, because of the away I'm storing these regexes. Fix!
		else:
			re_types = self.profile_settings[self.profile_settings['subtype']]['infobox params']
		for line in infobox.split('\n'):
			for k,v in re_types.iteritems():	#params are loaded when the profile object is created
				if re.search(v, line): #can I just search for the key?
					try:
						member[k] = re.search('(?<=\=)(.*?)(?=<|\||$)',line).group(1) #am I ignoring HTML comments?
					except:
						print "can't find this param in the infobox"
				else:
					continue #should I ignore profiles that don't have, say summaries?
		return member

	def formatProfile(self, val):
		"""
		takes in a dictionary of parameter values and plugs them into the specified template
		"""
		page_templates = templates.Template()
		tmplt = page_templates.getTemplate(self.profile_settings['type'])
		tmplt = tmplt.format(**val).encode('utf-8')
		return tmplt

	def publishProfile(self, val, path, edit_summ, sb_page = False, edit_sec = False):
		"""
		Publishes a profile or set of concatenated profiles to a page on a wiki.
		"""
		if sb_page:
			path += str(sb_page)
# 		print path
# 		print val
# 		print edit_summ
# 		print edit_sec
		output = wikitools.Page(self.wiki, path)
		if edit_sec:
			output.edit(val, section=edit_sec, summary=edit_summ, bot=1)
		else:
			output.edit(val, summary=edit_summ, bot=1)



class Toolkit:
	"""
	Handy ready-to-use methods that you don't need to create a complex object for.
	"""

	def addDefaults(self, member_list):
		"""
		Adds pre-specified set of default (null) fields to a dictionary.
		"""
		params = output_settings.Params()
		mem_defaults = dict.fromkeys(params.getParams('profile defaults'), "")
		for m in member_list:
			for k,v in mem_defaults.iteritems():
				if k not in m.keys():
					m[k] = v
		return member_list

	def setTimeValues(self, member_list):
		"""
		Adds a python date object and a pretty formatted date string
		to each dict in a list of dicts that contains a 'timestamp' key that contains a
		a 12-digit date string (like rev_timestamp) or an ISO 8601 date string
		(like API timestamp)
		"""
		for m in member_list:
			try:
				m['datetime'] = dateutil.parser.parse(m['timestamp'])
				m['time'] = datetime.strftime(m['datetime'], '%d %B %Y')
			except:
				print "no timestamp available for " + m['title']
		return member_list


	def getSubDate(self, day_interval):
		"""
		Returns the date a specified number of days before the current date as an API and database-friendly 14-digit timestamp string. Also handy for getting a date formatted for pretty output.
		"""
		date_since = datetime.utcnow()-timedelta(days=day_interval)
		date_since = date_since.strftime('%Y%m%d%H%M%S')
		return date_since

	def titleFromPath(self, path): #making this less abstract, unfortunately
		title = re.search('([^/]+$)', path).group(1).replace("_", " ")
		return title

	def titleFromComment(self, comment):
		title = re.search('\*(.*?)\*', comment).group(1)
		for sub in ['* ', ' *']:
			if sub in title:
				title.replace(sub,"")
		return title

	def formatSummaries(self, text):
		"""
		Cleans markup from strings of profile summary text and trims them to 140 chars.
		"""
		text = text.strip()
		text = re.sub("(\[\[)(.*?)(\|)","",text)
		text = re.sub("\]","",text)
		text = re.sub("\[","",text)
		text = (text[:140] + '...') if len(text) > 140 else text
		return text

	def dedupeMemberList(self, mem_list, sort_val, dict_val):
		"""
		Sort and remove duplicates from a list of dicts based on a specified key/value pair. Also removes things that should be ignored.
		"""
		mem_list.sort(key=operator.itemgetter(sort_val), reverse=True)
		seen_list = []
		unique_list = []
		for mem in mem_list:
			t = mem[dict_val]
			if t not in seen_list:
				seen_list.append(t)
				unique_list.append(mem)
			else:
				pass
		return unique_list

	def compareDates(self, date_one, date_two):
		"""
		Compares two date objects and returns the most recent one.
		"""
		if date_one >= date_two:
			return date_one
		else:
			return date_two

	def queryDB(self, query_type):
		"""
		MySQL queries for the evaluation portal.
		"""
		conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=True, charset="utf8")
		cursor = conn.cursor()
		q = queries.Query()
		query = q.getQuery(query_type)
		cursor.execute(query)
		rows = cursor.fetchall()
		for row in rows:
			print row[0]
		return rows





