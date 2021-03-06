#! /usr/bin/env python

from datetime import date
import hb_toolkit
import hb_output_settings
import hb_profiles
import random
from time import sleep
import sys

def get_eligible_users(elig_check, usernames, elig_type):
    """
    Takes an eligibility checker object, and a list of usernames.
    Returns a dictionary with lists of eligible and ineligible invitees.
    """
    eligible = [x for x in usernames if elig_check.determine_user_eligibility(x, elig_type)]

    return eligible


def send_invites(invitee, inviter, condition, params):
    """
    Send talkpage invitations.
    """
    prof = hb_profiles.Profiles(params['output namespace'] + invitee[0],
                                user_name = invitee[0],
                                user_id = invitee[1],
                                page_id = invitee[2],
                                settings = params
                                )
    prof.inviter = inviter
    prof.condition = condition
    prof.invited = False
    prof.skip = False

    if prof.condition == "control":
#         pass #record but don't invite
        prof.skip = True

    else:
        prof.invite = prof.formatProfile({'inviter' : inviter})
        prof.edit_summ = prof.user_name + params["edit summary"]

        try:
            prof.getToken()
            prof.publishProfile()
        except:
            print("something went wrong trying to invite " + prof.page_path) #should log, not print

    return prof


if __name__ == "__main__":
    param = hb_output_settings.Params()
    params = param.getParams(sys.argv[1])
    elig_check = hb_toolkit.Eligible(params)

    daily_sample = hb_profiles.Samples()
    all_records = daily_sample.select_rows(params['select sample query'], 'enwiki', convert_bytestrings = True) #list of lists

    if len(all_records) == 0: #if we can't retrieve any records at all. Currently implemented because of ongoing replag on the replica dbs.
        message = "{}: nobody to invite today".format(date.today()) #not sure if you can use .format in the sys.exit message directly
        sys.exit(message)
    else:
        print("{0}: There were {1} users found in today's candidate group.".format(date.today(), len(all_records)))
#     print(all_records)


    daily_sample.insert_rows(params['insert sample query'], all_records)
#     all_records.append([0,"\"Sadlyme\"", 0, 0]) #testing escape chars
#     all_records.append([0,"abc'd", 0, 0])

    sample_pagenames = [x[1].replace(" ","_") for x in all_records]
#     print(sample_pagenames)

    all_talkpages = daily_sample.select_rows_formatted(params['talkpage select query'], sample_pagenames, 'enwiki', convert_bytestrings = True)#should I add this to 'all records' instead?

    daily_sample.update_rows(params['talkpage update query'], all_talkpages)

    candidates = daily_sample.select_rows(params['select candidates query'], 'hostbot', convert_bytestrings = True)
#     print(candidates)

    candidate_usernames = [x[0] for x in candidates]
    eligible_usernames = get_eligible_users(elig_check, [x[0] for x in candidates], elig_type='invitee')
    eligible = [x for x in candidates if x[0] in eligible_usernames]
#     print(eligible)
    ineligible = [x for x in candidates if x[0] not in eligible_usernames]
#     print(ineligible)

    inviters = get_eligible_users(elig_check, params['inviters'], elig_type = 'inviter')
#     print(inviters)
#     print(params)

    for e in eligible:
        profile = send_invites(e, random.choice(inviters), "th-invite", params) #use when inviting everyone who is eligible
        daily_sample.update_rows(params['status update query'], [profile.condition, int(profile.invited), int(profile.skip), profile.user_id], single_row = True)

    for i in ineligible:
        daily_sample.update_rows(params['status update query'], ['invalid', 0, 1, i[1]], single_row = True) #should it always be single rows?

    eligible_new_talkpage = [x for x in eligible if x[2] is None]
#     print(eligible_new_talkpage)

    sleep(30) #sleep to let the replicas catch up with prod

    for e in eligible_new_talkpage:
        #try to grab the ID of the newly-created talkpage
        page_id = elig_check.get_page_id(params['output namespace'] + e[0])
#         print(page_id)
#         print(e[0])
        if page_id:
            updates = [page_id,0,e[0]]
            #wrap this in try/except...
            try:
                daily_sample.update_rows(params['talkpage update query'], updates, single_row=True)
            except:
                print("something went wrong trying to save new talkpage for " + e[0])
        else:
            pass
