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

class Template:
	"""templates of profiles for wiki pages"""
	def __init__(self):
		self.profile_templates = {#do I need to make the formatTemplates method pull from subtype instead, so I can feature both hosts and guests?
		'teahouse_gallery' : u"""
{{{{Wikipedia:Teahouse/Host_featured
| username = {username}
| image = {image}
}}}}""",		
	'intro' : u"""=Hosts=\n{{{{TOC hidden}}}}\n<br/>\n</noinclude>
{profiles}""",
	'twa invites' : u"""{{{{subst:Wikipedia:TWA/Invite|signature=~~~~}}}}""",
}

	def getTemplate(self, member):
		tmplt = self.profile_templates[member]
		return tmplt

