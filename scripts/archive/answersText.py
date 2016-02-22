import csv
import urllib2 as u2
import json
import re
import sys

difftext_url = u'http://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Wikipedia:Teahouse/Questions&rvprop=content&rvstartid=%s&rvendid=%s&rvlimit=1&rvsection=1&format=json'

def readCSVdata(inputfile):
	questions = []
	with open(inputfile,'rb') as csvfile:
		sreader = csv.reader(csvfile)
		for row in sreader:
			if row[0] != "rev_id":
				try:
					question = {'revision' : row[0],}
# 					print question
					questions.append(question)
				except:
					print "something went wrong here" + row[0]
			else:
				pass		
	return questions

def getRevisions(questions):
	qpage_id = "34745517"
	for question in questions:
		question_url = difftext_url % (question['revision'], question['revision'],)
# 		print question_url
		usock = u2.urlopen(question_url)
		sock_data = usock.read()
		usock.close()
		q_data = json.loads(sock_data)
# 		print q_data
		try:
			q_text = q_data['query']['pages'][qpage_id]['revisions'][0]['*']
			question['text'] = q_text
# 			print question['text']		
		except:
			pass
	questions = [question for question in questions if "text" in question]			
	return questions

#separates the title from the text of the question
def getTitle(question):
# 	print question['text']
	try:
		ttl = re.match("\=\=(.*?)\=\=", question['text'])
		question['title'] = ttl.group(1)
	# 		print ttl.group(1)
		question['text'] = re.sub("\=\=(.*?)\=\=\\n", "", question['text']).strip()
# 		print question['title']
	except:
		pass
	return question
	
#writes a new line of data to the csv
def writeline(question, writer, i):
	try:
		writer.writerow( (i, question['revision'], question['title'], question['text'],) )
	except ValueError:
		pass
# 		writer.writerow( (i, "error!") )
		
##MAIN##
inputfile = '/data/project/hostbot/bot/data/teahouse_questions_revs20140215.csv'
outputfile = '/data/project/hostbot/bot/data/teahouse_questions_text20140215.csv'
questions = readCSVdata(inputfile)
questions = getRevisions(questions)
i = 1
f = open(outputfile, 'wt')
writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
writer.writerow( ('serial_id','rev_id', 'title', 'text',) )
for question in questions:
	question = getTitle(question)
	if 'title' in question:
		try:
			writeline(question, writer, i)
			i+=1			
		except:
			pass
	else:
		pass			
f.close()