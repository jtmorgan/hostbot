#! /usr/bin/env python

import hb_utils as utils
import re

parameters = {
        'archive guests' : {
            'input path 1' : 'Wikipedia:Teahouse/Guests/Left_column',
            'input path 2' : 'Wikipedia:Teahouse/Guests/Right_column',
            'output path' : 'Wikipedia:Teahouse/Guest_book',
            'output section' : 1,
            'lines to keep' : ['==','{{','|username','^\|\s*image\s*='],
            'edit summary 1' : 'Archiving {} guest profiles from {}',
            'edit summary 2' : 'Archiving {} guest profiles to [[WP:Teahouse/Guest_book]]',
            }
        }

templates = {
        'archive guests' : """{{Wikipedia:Teahouse/Guest\n{profile}""",
        }

api_session = utils.API()
params = parameters['archive guests']
output_template = templates['archive guests']

if __name__ == "__main__":
    p_to_archive = []
    p_left = api_session.get_page_section_data(params['input path 1'], level = 2)
#     print(p_left)
    p_to_archive.extend(p_left[:len(p_left) - 14])
#     print(p_to_archive)
    for p in p_to_archive:
        text = api_session.get_page_text(params['input path 1'], sec_index=p['index'])[0]['*']
        x = text.split('\n')
        print(x)
        #get title, image, quote, realname, 
#         for t in text:
#             print(t.split('\n'))
#             print(t)
#     print(p_to_archive)
    #get profile list from both pages
    #get profile text from both pages
    #if there are more than 10 per page, take the N oldest ones (top)
#     api_session.get_token()
    #do I need to remove the noincludes?
    #update comment strings
    #add the newest ones back to the page
    #add the oldest one to guest book