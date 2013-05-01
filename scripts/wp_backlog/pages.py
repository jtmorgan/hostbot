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

import wikitools
import settings
import json

class CategoryCheck:
	"""Requests pages and subcategories in categories from the MediaWiki API."""

	def __init__(self):
		"""
		catmems['cmtitle'] - the title of the category you want info about
		catmems['cmtype'] = the kind of members you want data about: page, subcat, file
		"""
		self.wiki = wikitools.Wiki(settings.apiurl)
		self.wiki.login(settings.username, settings.password)
		self.catmems = {'action':'query','list':'categorymembers','cmtitle':'', 'cmtype':'','cmnamespace':''}


	def getPages(self, rtype, rtitle, rns=None):
		self.catmems['cmtype'] = rtype
		self.catmems['cmtitle'] = rtitle
		if rns is not None:
			self.catmems['cmnamespace'] = rns
		request = wikitools.APIRequest(self.wiki, self.catmems)
		subcats = request.query()
		pages = subcats['query']['categorymembers']

		return pages
