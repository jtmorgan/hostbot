#! /usr/bin/env python

import hb_toolkit
import hb_output_settings
import hb_profiles
import random
import sys

def getEligibleInviters(elig_check, potential_inviters):
    eligible_inviters = [x for x in potential_inviters if elig_check.determineInviterEligibility(x, 21)]
    print(eligible_inviters)
    return eligible_inviters

def getEligibleInvitees(elig_check, potential_invitees, skip_templates):
    """
    Takes an eligibility checker object, a list of keywords, and
    a list of invite candidates (user_name, user_id, talkpage_id).
    Returns a dictionary with lists of eligible and ineligible invitees.
    """
    eligible_invitees = [x for x in potential_invitees if elig_check.determineInviteeEligibility(x)]
    return eligible_invitees

def runSample(c, inviter, message, params):
    prof = hb_profiles.Profiles(params['output namespace'] + c[0], user_name = c[0], user_id = c[1], page_id = c[2],  settings = params)
    prof.inviter = inviter
    prof.message = message
    prof.invited = False
    prof.skip = False
    prof = inviteGuests(prof, prof.message[1], prof.inviter)
    return prof

def inviteGuests(prof, message_text, inviter):
    """
    Invites todays newcomers.
    """
    prof.invite = prof.formatProfile({'inviter' : inviter, 'message' : message_text})
    prof.edit_summ = prof.user_name + params["edit summary"]
    try:
        prof.getToken()
        prof.publishProfile()
    except:
        print "something went wrong trying to invite " + page_path
    return prof

if __name__ == "__main__":
    param = hb_output_settings.Params()
    params = param.getParams(sys.argv[1])
    elig_check = hb_toolkit.Eligible()

    daily_sample = hb_profiles.Samples()
    daily_sample.insertInvitees("teahouse test")#parameterize
    daily_sample.updateTalkPages("th add talkpage test")#parameterize
    candidates = daily_sample.selectSample(params['select query'], sub_sample=False)
    #make this a function
#     user_name = sys.argv[2]
#     user_id = int(sys.argv[3]) #int so it will be committed to the db
#     page_id = sys.argv[4]
#     candidates = [(user_name, user_id, page_id)]
    if sys.argv[1] in ('th_invites', 'test_invites'):
        if len(candidates) > 300:
            candidates = random.sample(candidates, 300) #pull 300 users out randomly
    else:
        pass
    inviters = getEligibleInviters(elig_check, params['inviters'])
    invitees = getEligibleInvitees(elig_check, candidates, params['skip templates'])
    skipped_editors = [x for x in candidates if x not in invitees]
#     print skipped_editors
    for i in invitees:
        profile = runSample(i, random.choice(inviters), random.choice(params['messages']), params)
        daily_sample.updateOneRow("update test invite status", [profile.message[0], int(profile.invited), int(profile.skip), profile.user_id])
    for s in skipped_editors:
        daily_sample.updateOneRow("update test invite status", [profile.message[0], 0, 1, s[1]])

    daily_sample.updateTalkPages("th add talkpage test")
