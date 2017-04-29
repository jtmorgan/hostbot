#! /usr/bin/env python

class Params:
	"""
	output parameters for running the invite script under different conditions.
	"""

	def __init__(self):
		self.output_params = {
			'th_invites' : {
			    'insert query' : 'teahouse experiment newbies',
			    'select query' : 'th experiment invitees',
			    'status update query' : 'update th invite status',
			    'talkpage update query' : 'th add talkpage',
				'type' : 'th invite templates',
				'output namespace' : 'User_talk:',
				'output section' : 'new',
				'sample size' : 300,
				'edit summary' : ', you are invited to the Teahouse!',
				'output section title' : '== {{subst:PAGENAME}}, you are invited to the Teahouse ==',
				'inviters' : ['Rosiestep','Jtmorgan','Missvain','Liz','Naypta','AmaryllisGardener','Doctree','Osarius','I JethroBT', 'Dathus', 'Cordless Larry', '78.26', 'Worm That Turned', 'ChamithN', 'Samwalton9',],
				'conditions' : ['th-invite'],
				'skip templates' : ['uw-vandalism4', 'final warning', '{{sock|', 'uw-unsourced4', 'uw-socksuspect', 'Socksuspectnotice', 'only warning','without further warning', 'Uw-socksuspect', 'sockpuppetry', 'Teahouse', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4'],
				},
			'test_invites' : { #when using the test db th_invite_test
			    'insert query' : 'teahouse test',
			    'select query' : 'th test invitees',
			    'status update query' : 'update test invite status',
			    'talkpage update query' : 'th add talkpage test',
				'type' : 'test invite templates',
				'output namespace' : 'User_talk:',
				'output section' : 'new',
				'sample size' : 10,
				'edit summary' : ', you are invited to the Teahouse!',
				'output section title' : '== {{subst:PAGENAME}}, you are invited to the Teahouse ==',
				'inviters' : ['Rosiestep','Jtmorgan','Missvain','Liz','Naypta','AmaryllisGardener','Doctree','Osarius','Soni', 'I JethroBT', 'Dathus', '78.26', 'Worm That Turned', 'ChamithN', 'Samwalton9',],
				'conditions' : ['th-invite'],
				'skip templates' : ['uw-vandalism4', 'final warning', '{{sock|', 'uw-unsourced4', 'uw-socksuspect', 'Socksuspectnotice', 'only warning','without further warning', 'Uw-socksuspect', 'sockpuppetry', 'Teahouse', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4'],
				},
			'training_module_invites' : {
			    'insert query' : 'tm insert records',
			    'select query' : 'tm select records',
			    'status update query' : 'tm update invite status',
			    'talkpage update query' : 'tm add talkpage',
				'type' : 'tm invite template',
				'output namespace' : 'User_talk:',
				'output section' : 'new',
				'sample size' : 500,
				'edit summary' : ', FIXME',
				'output section title' : '== {{subst:PAGENAME}}, you are invited to the FIXME ==',
				'inviters' : ['NULL'], #make sure this is ignored when formatting template
				'conditions' : ['tm-invite', 'control'],
				'skip templates' : ['uw-vandalism4', 'final warning', '{{sock|', 'uw-unsourced4', 'uw-socksuspect', 'Socksuspectnotice', 'only warning','without further warning', 'Uw-socksuspect', 'sockpuppetry', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4'],
				},
			}

	def getParams(self, profile_type):
		tp = self.output_params[profile_type]
		return tp