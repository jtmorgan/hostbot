#! /usr/bin/env python

import hb_utils as utils
# import hb_output_settings as output_settings
import re
# import hb_templates as templates

# params = output_settings.retrieve('recent questions')
# output_template = templates.retrieve('recent questions')

parameters = {
        'recent questions' : {
            'output path' : 'Wikipedia:Teahouse/Questions-recent/',
            'output section' : 1,
            'num questions' : 5,                
            'min words' : 20,
            'max words' : 150,
            'edit summary' : 'Updating [[WP:Teahouse/Questions-recent|recent questions gallery]]',
            }
        }

templates = {
        'recent questions' : """{text}\n\n<!-- Fill in the "section" parameter with the question title from the Q&A page -->\n{{{{Wikipedia:Teahouse/Questions-answer|section={title}}}}}\n\n<noinclude>[[Category:Wikipedia Teahouse]]</noinclude>""",
        }
        	        	 
params = parameters['recent questions']
output_template = templates['recent questions']

api_session = utils.API()
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
    questions = recent_question_text("Wikipedia:Teahouse/Questions", "new section", "(UTC)", params['min words'], params['max words'], params['num questions'])
#     print(len(questions))
    output_counter = 1
    for i,q in enumerate(questions):
        if i < params['num questions']:
            subpage_path = params['output path'] + str(i + 1)
            output = output_template.format(**q)
#             print(subpage_path)
#             print(output)

            status = api_session.publish_to_wiki(subpage_path, params['edit summary'], output)
#             print(status)
        else:
            break
#TODO        
# what do I need to log for this one?