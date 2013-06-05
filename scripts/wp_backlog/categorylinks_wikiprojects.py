
import os, sys, MySQLdb, re

conn = MySQLdb.connect(
host='db42',
db='shawn',
read_default_file=os.path.expanduser("~/.my.cnf")
)

conn2 = MySQLdb.connect(
host='db42',
db='shawn',
read_default_file=os.path.expanduser("~/.my.cnf")
)


def getWikiProjectPage(conn,  page_title):
	# sys.stdout.write("Searching WikiProject Page for %s\n" % (page_title))
	cursor = conn.cursor(MySQLdb.cursors.SSCursor)
	#cursor.execute("""SELECT page_id FROM enwiki.page WHERE CONVERT(page_title USING latin1) like %(page_title)s AND page_namespace = 4
	cursor.execute("""SELECT page_id FROM enwiki.page WHERE page_title = %(page_title)s AND page_namespace = 4
	""",
	{
	'page_title': page_title
	}
	)
	edits = cursor.fetchone()
	#sys.stdout.write(".")
	if edits:
		# sys.stdout.write("Found WikiProject Page for %s - %s\n" % (page_title, edits[0]))
		return edits[0]
	else:
		# sys.stdout.write("NOT Found WikiProject Page for %s\n" % page_title)
		return None

# Given a categorylink, returnt the WikiProject name by removing anything after _article, _page, _member, or _participant
def parseWikiProject(conn, page_title):
	# sys.stdout.write("Parsing WikiProject Page for %s\n" % (page_title))
	if re.search('_article.*$', page_title):
		wp = re.sub(r'_article.*$','', page_title)
	
	elif re.search('_page.*$', page_title):
		wp = re.sub(r'_page.*$','', page_title)
	
	elif re.search('_member.*$', page_title):
		wp = re.sub(r'_member.*$','', page_title)
	
	elif re.search('_participant.*$', page_title):
		wp = re.sub(r'_participant.*$','', page_title)
	
	else:
		# sys.stdout.write("NO PARSING for %s\n" % (page_title))
		return None
	
	# sys.stdout.write("PARSED as %s\n" % (wp))
	return wp



ucursor = conn.cursor(MySQLdb.cursors.SSCursor)
ucursor.execute("""
                SELECT DISTINCT
					cl_to
				FROM categorylinks
				"""
)



for cat_link in ucursor:
	wp_page_name = cat_link[0]
	# sys.stdout.write("Working With WikiProject Category: %s\n" % cat_link[0])
	wikiproject = parseWikiProject(conn2, cat_link[0])
	# sys.stdout.write("-- Working With WikiProject After Parsing: %s\n" % wikiproject)
	if wikiproject:
		# sys.stdout.write("WikiProject parsed, setting to %s - %s\n" % (cat_link[0], wp_page_name))
		wp_page_nume = wikiproject
		
	wp_page_id = getWikiProjectPage(conn2, wp_page_name)
	
	# didn't find a match for the wikiproject name
	while not wp_page_id:
		#wp_page_name = trimWikiProjectName(wp_page_name)
		
		wp_page_name = wp_page_name[0:wp_page_name.rfind('_')]
		# sys.stdout.write("-- Trimming WikiProject name to: %s\n" % wp_page_name)
		wp_page_id = getWikiProjectPage(conn2, wp_page_name)
		# sys.stdout.write("-- Searching for page id: %s\n" % wp_page_id)

	if wp_page_id == 33631:
		sys.stdout.write("-- NOT found after trimming: %s - %s - %s\n\n" % (wp_page_name, cat_link[0], wp_page_id))
		
	if wp_page_id != 33631:
		sys.stdout.write("++ FOUND after trimming: %s - %s - %s\n\n" % (wp_page_name, cat_link[0], wp_page_id))
		sys.stdout.write("+")
		cursor3 = conn2.cursor(MySQLdb.cursors.SSCursor)
		cursor3.execute("""INSERT INTO categorylinks_wp values (%(wp_id)s, %(category)s)
						""",
			{
			'wp_id': wp_page_id,
			'category': cat_link[0]
			}
		)
	else:
		sys.stdout.write("-")