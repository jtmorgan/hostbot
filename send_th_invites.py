#! /usr/bin/env python

import hb_toolkit
import hb_output_settings
import hb_profiles
import random
from time import sleep
import sys

def convertBytestrings(all_records):
    """Db returns byte strings, but we want normal strings"""
    for a in all_records:
        a[0] = a[0].decode('utf-8')
    return all_records

def getEligibleInviters(elig_check, potential_inviters):
    eligible_inviters = [x for x in potential_inviters if elig_check.determineInviterEligibility(x, 21)]
    return eligible_inviters

def getEligibleInvitees(elig_check, potential_invitees, skip_templates):
    """
    Takes an eligibility checker object, a list of keywords, and
    a list of invite candidates (user_name, user_id, talkpage_id).
    Returns a dictionary with lists of eligible and ineligible invitees.
    """
    eligible_invitees = [x for x in potential_invitees if elig_check.determineInviteeEligibility(x)]
    return eligible_invitees

def runSample(c, inviter, condition, params):
    prof = hb_profiles.Profiles(params['output namespace'] + c[0],
                                user_name = c[0],
                                user_id = c[1],
                                page_id = c[2],
                                settings = params
                                )
    prof.inviter = inviter
    prof.condition = condition
    prof.invited = False
    prof.skip = False

    if prof.condition != "control":
        prof = inviteGuests(prof, prof.inviter)
    else:
        pass #record but don't invite

    return prof

def inviteGuests(prof, inviter):
    """
    Send talkpage invitations.
    """
    prof.invite = prof.formatProfile({'inviter' : inviter})
    prof.edit_summ = prof.user_name + params["edit summary"]

    try:
        prof.getToken()
        prof.publishProfile()
    except:
        print("something went wrong trying to invite " + page_path) #should log, not print
    return prof

if __name__ == "__main__":
    param = hb_output_settings.Params()
    params = param.getParams(sys.argv[1])
#     elig_check = hb_toolkit.Eligible(params)

    daily_sample = hb_profiles.Samples()
    all_records = daily_sample.select_rows(params['select query'], 'enwiki', convert_bytestrings = True) #list of lists
    print(all_records)
    daily_sample.insert_rows(params['insert query'], all_records)
    sample_userpages = ["'" + "','".join(x[1].replace(" ","_") for x in all_records) + "'"]
    print(sample_userpages)
    all_talkpages = daily_sample.select_rows_formatted(params['talkpage select query'], sample_userpages, 'enwiki', convert_bytestrings = True)
    print(all_talkpages)
    daily_sample.update_rows(params['talkpage update query'], all_talkpages)

#     daily_sample.update_rows(params[''])
#     daily_sample.updateTalkPages(params['talkpage update query'])
#     all_records = daily_sample.selectSample(params['select query'], sub_sample=True)
#     all_records = convertBytestrings(all_records)
#     candidates = getEligibleInvitees(elig_check, all_records, params['skip templates'])
#     print("Found " + str(len(candidates)) + " candidates for invitation")
#     skipped_editors = [x for x in all_records if x not in candidates]
#     print("Skipped " + str(len(skipped_editors)) + " editors for invitation")
#
#     if len(candidates) > params['sample size']:
#         candidates = random.sample(candidates, params['sample size'])
#         print("Ready to invite " + str(len(candidates)) + " of the candidates for invitation")
#
#     if sys.argv[1] == 'th_invites':
#         inviters = getEligibleInviters(elig_check, params['inviters'])
#     else: #only Teahouse invites have an inviters param
#         inviters = params['inviters']
#
#     for c in candidates:
#         profile = runSample(c, random.choice(inviters), random.choice(params['conditions']), params)
#         daily_sample.updateOneRow(params['status update query'], {'group':profile.condition, 'status':int(profile.invited), 'skipped':int(profile.skip), 'user_id':profile.user_id})
#         if sys.argv[1] == 'training_module_invites':
#             sleep(5)
#
#     for s in skipped_editors:
# #         daily_sample.updateOneRow(params['status update query'], ["invalid", 0, 1, s[1]])
#         daily_sample.updateOneRow(params['status update query'], {'group':'invalid', 'status':0, 'skipped':1, 'user_id':profile.user_id})
#
#     daily_sample.updateTalkPages(params['talkpage update query'])
