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

class Params:
	"""
	output parameters for building various kinds of profiles and their values and settings.
	"""

	def __init__(self):
		self.output_params = {
		  'teahouse_gallery' : {
				'edit summary' : 'Updating featured host and guest galleries',
				'header template' : '<noinclude>[[Category:Wikipedia Teahouse]]</noinclude>',
				'featured_hosts' : {
					'output path' : 'Wikipedia:Teahouse/Host/Featured/',
					'input page path' : 'Wikipedia:Teahouse/Host_landing',
					'input page id' : 36794919,
					'first subpage' : 1,
					'number featured' : 10,
					'profile toclevel' : 2,
					'infobox params' : {
						'image' : '^\|\s*image\s*=',
						},
					},
				'featured_guests_right' : {
					'output path' : 'Wikipedia:Teahouse/Guest/Featured/',
					'input page path' : 'Wikipedia:Teahouse/Guests/Right_column',
					'input page id' : 35844104,
					'first subpage' : 1,
					'number featured' : 5,
					'profile toclevel' : 2,
					'infobox params' : {
						'image' : '^\|\s*image\s*=',
						'quote' : '^\|\s*quote\s*=',
						},
					},
				'featured_guests_left' : {
					'output path' : 'Wikipedia:Teahouse/Guest/Featured/',
					'input page path' : 'Wikipedia:Teahouse/Guests/Left_column',
					'input page id' : 35844019,
					'first subpage' : 6,
					'number featured' : 5,
					'profile toclevel' : 2,
					'infobox params' : {
						'image' : '^\|\s*image\s*=',
						'quote' : '^\|\s*quote\s*=',
						},
					},
				},
			'intro' : {
				'output path' : 'Wikipedia:Teahouse/Host_landing',
				'output page id' : 36794919,
				'output section' : 1,
				'edit summary' : 'Reordering %ss, putting recently active participants at the top',
				},
			'th_invites' : {
			    'select query' : 'th experiment invitees',
				'type' : 'th invite templates',
				'output namespace' : 'User_talk:',
				'output section' : 'new',
				'edit summary' : ', you are invited to the Teahouse!',
				'output section title' : '== {{subst:PAGENAME}}, you are invited to the Teahouse ==',
				'inviters' : ['Rosiestep','Jtmorgan','Missvain','Naypta','AmaryllisGardener','Doctree','Osarius','Soni', 'I JethroBT', 'Dathus', '78.26', 'Worm That Turned', 'ChamithN', 'Samwalton9',],
				'messages' : [('th exp', ""),], #not currently using the message text
				'skip templates' : ['uw-vandalism4', 'final warning', '{{sock|', 'uw-unsourced4', 'uw-socksuspect', 'Socksuspectnotice', 'only warning','without further warning', 'Uw-socksuspect', 'sockpuppetry', 'Teahouse', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4'],
				'headers' : { 'User-Agent' : 'HostBot (http://github.com/jtmorgan/hostbot; jmorgan@wikimedia.org)', },
				},
			'twa_invites' : {
			    'select query' : 'twa invitees',
				'type' : 'twa invite templates',
				'output namespace' : 'User_talk:',
				'output section' : 'new',
				'edit summary' : ', you are invited on a [[WP:TWA|Wikipedia Adventure]]!',
				'output section title' : '== {{subst:PAGENAME}}, you are invited on a Wikipedia Adventure ==',
				'inviters' : ['Ocaasi',],
				'messages' : [('twa', ""),],
				'skip templates' : ['uw-vandalism4', 'final warning', '{{sock|', 'uw-unsourced4', 'uw-socksuspect', 'Socksuspectnotice', 'only warning','without further warning', 'Uw-socksuspect', 'sockpuppetry', 'Teahouse', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4'],
				'headers' : { 'User-Agent' : 'HostBot (http://github.com/jtmorgan/hostbot; jmorgan@wikimedia.org)', },
				},
			'profile defaults' : [],
			}

	def getParams(self, profile_type):
		tp = self.output_params[profile_type]
		return tp


