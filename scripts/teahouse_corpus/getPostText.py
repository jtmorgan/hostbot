import csv
import urllib2 as u2
import json
import re
import sys



def readCSVdata(inputfile):
	posts = []
	with open(inputfile,'rb') as csvfile:
		sreader = csv.reader(csvfile)
		for row in sreader:
			if row[0] != "rev_id":
				try:
					post = {'revision' : row[0],}
# 					print question
					posts.append(post)
				except:
					print "something went wrong here" + row[0]
			else:
				pass
	return posts

def getRevisions(posts):
	for post in posts:
		post_url = difftext_url % (post['revision'], post['revision'],)
# 		print question_url
		usock = u2.urlopen(post_url)
		sock_data = usock.read()
		usock.close()
		p_data = json.loads(sock_data)
# 		print q_data
		try:
			p_text = p_data['query']['pages'][qpage_id]['revisions'][0]['*']
			post['text'] = p_text
# 			print question['text']
		except:
			pass
	posts = [post for post in posts if "text" in post]
	return posts

#separates the title from the text of the question
def getTitle(post):
# 	print question['text']
	try:
		ttl = re.match("\=\=(.*?)\=\=", post['text'])
		post['title'] = ttl.group(1)
	# 		print ttl.group(1)
		post['text'] = re.sub("\=\=(.*?)\=\=\\n", "", post['text']).strip()
# 		print question['title']
	except:
		pass
	return post

#writes a new line of data to the csv
def writeline(post, writer, i):
	try:
		writer.writerow( (i, post['revision'], post['title'], post['text'],) )
	except ValueError:
		pass
# 		writer.writerow( (i, "error!") )

##MAIN##
difftext_url = u'http://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Wikipedia:Teahouse/Questions&rvprop=content&rvstartid=%s&rvendid=%s&rvlimit=1&rvsection=1&format=json'
qpage_id = "34745517" #the page you're pulling questions and answers from
inputfile = sys.argv[1] #path to file you are reading revids from
outputfile = sys.argv[2] #path to file you want to create
texttype = sys.argv[3] #currently 'questions' or 'answers'
posts = readCSVdata(inputfile)
posts = getRevisions(posts)
i = 1
f = open(outputfile, 'wt')
writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
writer.writerow( ('serial_id','rev_id', 'title', 'text',) )
for post in posts:
	post = getTitle(post)
	if 'title' in post:
		try:
			writeline(post, writer, i)
			i+=1
		except:
			pass
	else:
		pass
f.close()