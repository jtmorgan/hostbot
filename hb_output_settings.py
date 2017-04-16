#! /usr/bin/env python

class Params:
	"""
	output parameters for building various kinds of profiles and their values and settings.
	"""

	def __init__(self):
		self.output_params = {
			'th_invites' : {
			    'select query' : 'th experiment invitees',
				'type' : 'th invite templates',
				'output namespace' : 'User_talk:',
				'output section' : 'new',
				'edit summary' : ', you are invited to the Teahouse!',
				'output section title' : '== {{subst:PAGENAME}}, you are invited to the Teahouse ==',
				'inviters' : ['Rosiestep','Jtmorgan','Missvain','Liz','Naypta','AmaryllisGardener','Doctree','Osarius','I JethroBT', 'Dathus', 'Cordless Larry', '78.26', 'Worm That Turned', 'ChamithN', 'Samwalton9',],
				'messages' : [('th exp', ""),], #not currently using the message text
				'skip templates' : ['uw-vandalism4', 'final warning', '{{sock|', 'uw-unsourced4', 'uw-socksuspect', 'Socksuspectnotice', 'only warning','without further warning', 'Uw-socksuspect', 'sockpuppetry', 'Teahouse', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4'],
				},
			'test_invites' : { #when using the test db th_invite_test
			    'select query' : 'th test invitees',
				'type' : 'th invite templates',
				'output namespace' : 'User_talk:',
				'output section' : 'new',
				'edit summary' : ', you are invited to the Teahouse!',
				'output section title' : '== {{subst:PAGENAME}}, you are invited to the Teahouse ==',
				'inviters' : ['Rosiestep','Jtmorgan','Missvain','Liz','Naypta','AmaryllisGardener','Doctree','Osarius','Soni', 'I JethroBT', 'Dathus', '78.26', 'Worm That Turned', 'ChamithN', 'Samwalton9',],
				'messages' : [('th exp', ""),], #not currently using the message text
				'skip templates' : ['uw-vandalism4', 'final warning', '{{sock|', 'uw-unsourced4', 'uw-socksuspect', 'Socksuspectnotice', 'only warning','without further warning', 'Uw-socksuspect', 'sockpuppetry', 'Teahouse', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4'],
				},
			'profile defaults' : [],
			}

	def getParams(self, profile_type):
		tp = self.output_params[profile_type]
		return tp