#! /usr/bin/python2.7

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

import hb_hosts
import hb_output_settings
import hb_profiles
import random
import sys

def getSample(cursor, qstring):
    """
    Returns a list of usernames and ids of candidates for invitation
    """
    cursor.execute(qstring)
    rows = cursor.fetchall()
    sample_set = [(row[0],row[1], row[2]) for row in rows]
#   sample_set = sample_set[:5]
    sample_set = [(user_name, user_id, page_id)]
    return sample_set

def getEligibleInviters(elig_check, potential_inviters):
    eligible_inviters = [x for x in potential_inviters if elig_check.determineInviterEligibility(x, 21)]
    return eligible_inviters
    
def runSample(c, inviter, message, params):
#     invited = False
#     skip = False
#     message = random.choice(params['messages'])     
    prof = hb_profiles.Profiles(params['output namespace'] + c[0], user_name = c[0], user_id = c[1], page_id = c[2],  settings = params)
    prof.inviter = inviter
    prof.message = message
    prof.invited = False
    prof.skip = False
    if c[2] is not None:
        prof.skip = checkTalkPage(prof.skip, prof, params['skip templates'])
    if not prof.skip:
        prof = inviteGuests(prof, prof.message[1], prof.inviter) #return invited, don't declare it
#         prof.invited = True
#         print "invited? " + str(invited)
    else:
#         print "skipped? " + str(skip) + prof.user_name
        message = ("th control","")
    return prof #add invite status, etc here    
#       updateDB(s[1], "update th invite status", message[0], int(invited), int(skip))


def checkTalkPage(skip, prof, skip_templates): #only works if you already have the talkpage
    """checks talk pages"""
    tp_text = prof.getPageText()
    for t in skip_templates:
        if t in tp_text:
            skip = True
    return skip
    
def inviteGuests(prof, message_text, inviter):
    """
    Invites todays newcomers.
    """
    prof.invite = prof.formatProfile({'inviter' : inviter, 'message' : message_text})
    prof.edit_summ = prof.user_name + params["edit summary"]
#     try:
    prof.publishProfile()
#     except:
#         print "something went wrong trying to invite " + page_path
    return prof
    #need to return success
# def updateDB(profile)


if __name__ == "__main__":
    param = hb_output_settings.Params()
    params = param.getParams(sys.argv[1])
    elig_check = hb_hosts.Eligible()
    daily_sample = hb_profiles.Samples()
    candidates = daily_sample.getSample(params['select query'], sub_sample=True)    
#     user_name = sys.argv[2]
#     user_id = sys.argv[3]
#     page_id = sys.argv[4]
#     candidates = [(user_name, user_id, page_id)]
    if sys.argv[1] in ('th_invites', 'twa_invites', 'test_invites'):
        if len(candidates) > 150:
            candidates = random.sample(candidates, 150) #pull 150 users out randomly
    else:
        pass
    inviters = getEligibleInviters(elig_check, params['inviters'])
#     inviters = ["J-Mo", "Fred", "Subbu"]
    for c in candidates:
        print c
        profile = runSample(c, random.choice(inviters), random.choice(params['messages']), params)
        daily_sample.updateOneRow("update test invite status", [profile.message[0], int(profile.invited), int(profile.skip), profile.user_id])
#         updateDB('update th invite status', profile) #update query should be parameterized       
