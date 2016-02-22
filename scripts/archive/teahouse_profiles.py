#! /usr/bin/python2.7


import moves
import pprint as pp

landing = moves.Profiles('/Host_landing') #not really ideal
landing_list = landing.getPageSectionData()
# print [x['username'] + "\n" for x in landing_list]
l_list = [x['username'] for x in landing_list]
l_list = sorted(l_list)
pp.pprint(l_list)
breakroom = moves.Profiles('/Host_breakroom') #not really ideal
breakroom_list = breakroom.getPageSectionData()
b_list = [x['username'] for x in breakroom_list]

b_list = sorted(b_list)
pp.pprint(b_list)

print "cross dupes \n"
c_list = [x for x in l_list if x in b_list]
pp.pprint(c_list)
##############
# print "breakroom \n"
# print [x['username'] + "\n" for x in breakroom_list]

# print sorted(b_list)
# print [x for x in l_list if x in b_list]

# canonical = moves.Toolkit()
# landing_dupes = canonical.dedupeMemberList(landing_list, 'username', 'profile index')
# print "these duplicates exist in the landing page: \n"
# print landing_dupes
# 
# breakroom_dupes = canonical.dedupeMemberList(breakroom_list, 'username', 'profile index')
# print "these duplicates exist in the breakroom page: \n"
# print breakroom_dupes
# 
# 
# # all_profiles = landing_list + breakroom_list
# # all_dupes = canonical.dedupeMemberList(all_profiles, 'username', 'profile index')
# # print "these duplicates exist between the landing and breakroom pages: \n"
# # print all_dupes
# 
# print [x['username'] for x in landing_list if x['username'] in [x['username'] for x in breakroom_list]]