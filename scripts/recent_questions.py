#! /usr/bin/env python

# Copyright 2012, 2016 Jtmorgan

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

import test_config as config
import hb_utils as utils
import test_output_settings as output_settings
import requests
import re
from random import shuffle
import test_templates as templates

#capitalize these globals?
param = output_settings.Params()
params = param.getParams('recent questions')
tmplt = templates.Template()
t = tmplt.getTemplate('recent questions')
#     print(t)
api_session = utils.API(alt_url_get = 'https://en.wikipedia.org/w/api.php')
token = api_session.get_token() #do this in the class instead

def recent_question_text(page_path, comment_sub, text_sub, min_words, max_words, num_questions):
    """
    title: the title of the page
    substring: what to look for in the edit comment
    min_max: tuple of (minimum words, maximum words) in the question
    num_questions: get this many questions
    """

    questions = []

    rev_data = api_session.get_page_text(page_path, sec_index=1, limit=100)
    for r in rev_data:
        word_count = len(r["*"].split())
        if (
            r["comment"].endswith(comment_sub) and 
            r["*"].endswith(text_sub) and
            word_count >= min_words and 
            word_count <= max_words
            ):
            q_text = re.sub("\=\=(.*?)\=\=\\n", "", r["*"])
            q_title = re.match("\=\=(.*?)\=\=", r["*"]).group(1)
            questions.append({'text' : q_text, 'title' : q_title})            
    
    return questions

if __name__ == "__main__":
    questions = recent_question_text("Wikipedia:Teahouse/Questions", "new section", "(UTC)", 20, 150, 2)
    print(len(questions))
    output_counter = 1
    for i,q in enumerate(questions):
        if i < params['num questions']:
            subpage_path = params['output path'] + str(i + 1)
            output = t.format(**q)
            print(subpage_path)
            print(output)

            status = api_session.publish_to_wiki(subpage_path, params['edit summary'], output)
            print(status)
        else:
            break
        
# do I need to log anything for this one?