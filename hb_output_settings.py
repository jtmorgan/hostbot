#! /usr/bin/env python

class Params:
    """
    output parameters for running the invite script under different conditions.
    """

    def __init__(self):
        self.output_params = {
            'th_invites' : {
                'db_table' : 'th_up_invitees_current',
                'select sample query' : 'select th sample',
                'insert sample query' : 'insert th sample',
                'talkpage select query' : 'find th talkpage',
                'talkpage update query' : 'add th talkpage',
                'select candidates query' : 'select th candidates',
                'status update query' : 'update th invite status',
                'type' : 'th invite templates',
                'output namespace' : 'User_talk:',
                'output section' : 'new',
                'sample size' : 300,
                'edit summary' : ', you are invited to the Teahouse!',
#                 'output section title' : '== {{subst:PAGENAME}}, you are invited to the Teahouse ==',
                'inviters' : ['Rosiestep', 'Missvain', 'Naypta', 'AmaryllisGardener', 'Doctree', 'I JethroBT', 'Dathus', 'Cordless Larry', 'Gestrid', 'Cullen328', 'Lectonar', '78.26', 'Worm That Turned', 'ChamithN', 'Nick Moyes', 'John from Idegon', 'GreenMeansGo', 'Abelmoschus Esculentus', 'Masumrezarock100', 'MrClog'],
                'inviter edit threshold' : 21,
                'conditions' : ['th-invite', 'control'],
                'skip templates' : ['uw-vandalism4', 'final warning', '{{sock|', 'uw-unsourced4', 'uw-socksuspect', 'Socksuspectnotice', 'only warning','without further warning', 'Uw-socksuspect', 'sockpuppetry', 'Teahouse', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4', '{{bots|deny=HostBot','{{Bots|deny=HostBot','{{nobots','{{Nobots'],
                },
            'test_invites' : { #when using the test db th_invite_test
                'test_invites' : True, #a little hack for line 195 in profiles.py
                'db_table' : 'th_invite_test',
                'select sample query' : 'select sample test',
                'insert sample query' : 'insert sample test',
                'talkpage select query' : 'find talkpage test',
                'talkpage update query' : 'add talkpage test',
                'select candidates query' : 'select candidates test',
                'status update query' : 'update invite status test',
                'type' : 'test invite templates',
                'output namespace' : 'User_talk:',
                'output section' : 'new',
                'sample size' : 300,
                'edit summary' : ', you are invited to the Teahouse!',
#                 'output section title' : '== {{subst:PAGENAME}}, you are invited to the Teahouse ==',
                'inviters' : ['Rosiestep','Jtmorgan','Missvain','Liz','Naypta','AmaryllisGardener','Doctree','I JethroBT', 'Dathus', 'Cordless Larry', 'Gestrid', 'Cullen328', 'Lectonar', 'Mz7', '78.26', 'Worm That Turned', 'ChamithN', 'Samwalton9',],
                'inviter edit threshold' : 21,
                'conditions' : ['th-invite', 'control'],
                'skip templates' : ['uw-vandalism4', 'final warning', '{{sock|', 'uw-unsourced4', 'uw-socksuspect', 'Socksuspectnotice', 'only warning','without further warning', 'Uw-socksuspect', 'sockpuppetry', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4', '{{bots|deny=HostBot','{{Bots|deny=HostBot','{{nobots','{{Nobots'],  #skip templates don't include 'teahouse' for testing purposes
                },
            }

    def getParams(self, profile_type):
        tp = self.output_params[profile_type]
        return tp
