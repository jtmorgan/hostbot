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
	'teahouse_invitee_report' : u'''==Daily Report==
This list was last updated on {{subst:REVISIONMONTH}}/{{subst:REVISIONDAY}}/{{subst:REVISIONYEAR}} by {{subst:REVISIONUSER}}.

===Highly active new editors===
Below is a list of editors who joined within the last 24 hours, have since made more than 10 edits, and were not blocked at the time the report was generated.

{| class="wikitable sortable plainlinks"
|-
! Guest #
! Guest Name
! Edit Count
! Contribs
! Already Invited?
|-
%s
|}


===New Autoconfirmed Editors===
Below is a list of editors who gained [[Wikipedia:User_access_levels#Autoconfirmed_users|autoconfirmed status]] today, who were not previously invited to Teahouse after their first day, and were not blocked at the time the report was generated.

{| class="wikitable sortable plainlinks"
|-
! Guest #
! Guest Name
! Edit Count
! Contribs
! Already Invited?
|-
%s
|}

{{Wikipedia:Teahouse/Layout-end}}
{{Wikipedia:Teahouse/Host navigation}}
''',
}

	def getTemplate(self, member):
		tmplt = self.profile_templates[member]
		return tmplt

