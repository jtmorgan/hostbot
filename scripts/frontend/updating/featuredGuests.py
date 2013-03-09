#! /usr/bin/env python

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

from BeautifulSoup import BeautifulStoneSoup as bss
import urllib2
import wikitools
import re
import settings

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

##global variables and output templates

guest_profiles = []

profileurl = u'http://en.wikipedia.org/w/index.php?title=Wikipedia%%3ATeahouse%%2FGuests%%2F%s&action=raw&section=%s'

securl = u'http://en.wikipedia.org/w/api.php?action=parse&page=Wikipedia%%3ATeahouse%%2FGuests%%2F%s&prop=sections&format=xml'

left = "Left_column"
right = "Right_column"

page_namespace = u'Wikipedia:'

page_section = u'Teahouse/Guest/Featured/%i' 

report_template = '%s'

###FUNCTIONS###

def getSectionData(securl, string):
	usock = urllib2.urlopen(securl % string)
	print usock
	sections = usock.read()
	usock.close()
	soup = bss(sections, selfClosingTags = ['s'])
	
	return soup
	
	
def getAllSections(soup):
	all_sec = []
	for x in soup.findAll('s',toclevel="2"):
		all_sec.append(x['index'])
	
	return all_sec
	
	
def copySectionText(sections, url, string):
	global guest_profiles
	for sec in sections:
		usock = urllib2.urlopen(url % (string, sec))
		txt = usock.readlines()
		usock.close()
		del txt[0]
		feature = True
		for index, line in enumerate(txt):
			if line.startswith('|image='):
				if len(txt[index]) < 9:
					feature = False	
			if line.startswith('}}'):
				txt[index] = '}}<br/>'
		txt = ''.join(txt)
		if feature:
			guest_profiles.append(txt)

	
def updateFeatured(guest_profiles):	
	i = 1
	for profile in guest_profiles:
		report_title = page_namespace + page_section % i
		report = wikitools.Page(wiki, report_title)
		report_text = report_template % profile
		i += 1
		report.edit(report_text, summary="Automatic update of [[Wikipedia:Teahouse/Host/Featured|featured guest gallery]] by [[User:HostBot|HostBot]]", bot=1)	

			

##MAIN##
soup = getSectionData(securl, left)
sections = getAllSections(soup)
copySectionText(sections, profileurl, left)

soup = getSectionData(securl, right)
sections = getAllSections(soup)
copySectionText(sections, profileurl, right)

updateFeatured(guest_profiles)

             