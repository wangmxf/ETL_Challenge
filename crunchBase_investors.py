#!/usr/bin/python
from urllib2 import urlopen
import json
import MySQLdb as mdb
import jsonpath

#make database connection
try:
	con = mdb.connect('localhost', 'user', 'password', 'database');
except mdb.Error, e:
	print "Error %d: %s" % (e.args[0],e.args[1])
	sys.exit(1)
with con:
	cur = con.cursor()
	
	#get personal investors
	cur.execute("select investors from investors where investor_type = 1")
	personal_investors = [element[0] for element in cur.fetchall()]
	
	#get company investors
	cur.execute("select investors from investors where investor_type = 2")
	company_investors = [element[0] for element in cur.fetchall()]

	#get financial organization investors
	cur.execute("select investors from investors where investor_type = 3")
	fin_investors = [element[0] for element in cur.fetchall()]

#call person api
personal_data = []
for x in range(0, len(personal_investors)):
	print 'Getting data for: ' + personal_investors[x]
	p_response = json.load(urlopen('http://api.crunchbase.com/v/1/person/' + personal_investors[x] + '.js?api_key=000000000000000000000000'))
	personal_data.append(p_response)

#call company api
company_data = []
for y in range(0, len(company_investors)):
	print 'Getting data for: ' + company_investors[y]
	c_response = json.load(urlopen('http://api.crunchbase.com/v/1/company/' + company_investors[y] + '.js?api_key=000000000000000000000000'))
	company_data.append(c_response)

#call financial-organization api
fin_data = []
for z in range(0, len(fin_investors)):
	print 'Getting data for: ' + fin_investors[z]
	f_response = json.load(urlopen('http://api.crunchbase.com/v/1/financial-organization/' + fin_investors[z] + '.js?api_key=000000000000000000000000'))
	fin_data.append(f_response)

with con:
	#insert data in to investor_data table
	for a in range(0, len(personal_data)):
		permalink = json.dumps(jsonpath.jsonpath(personal_data[a], "$.permalink"))
		first_name = json.dumps(jsonpath.jsonpath(personal_data[a], "$.first_name"))
		last_name = json.dumps(jsonpath.jsonpath(personal_data[a], "$.last_name"))
		homepage_url = json.dumps(jsonpath.jsonpath(personal_data[a], "$.homepage_url"))
		blog_url = json.dumps(jsonpath.jsonpath(personal_data[a], "$.blog_url"))
		description = json.dumps(jsonpath.jsonpath(personal_data[a], "$.affiliation_name"))

		degree_list = jsonpath.jsonpath(personal_data[a], "$.degrees[*]")
		if degree_list:
			degrees = len(jsonpath.jsonpath(personal_data[a], "$.degrees[*]"))
			for b in range(0, degrees):
				degree_type = json.dumps(jsonpath.jsonpath(personal_data[a], "$.degrees[" + str(b) + "].degree_type"))
				subject = json.dumps(jsonpath.jsonpath(personal_data[a], "$.degrees[" + str(b) + "].subject"))
				institution = json.dumps(jsonpath.jsonpath(personal_data[a], "$.degrees[" + str(b) + "].institution"))
				#insert
				cur.execute("insert into investor_data(permalink, first_name, last_name, homepage_url, blog_url, description, degree_type, degree_subject, institution) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (permalink, first_name, last_name, homepage_url, blog_url, description, degree_type, subject, institution))
		else:	#insert
			cur.execute("insert into investor_data(permalink, first_name, last_name, homepage_url, blog_url, description) values(%s, %s, %s, %s, %s, %s)", (permalink, first_name, last_name, homepage_url, blog_url, description))


	for c in range(0, len(company_data)):
		permalink = json.dumps(jsonpath.jsonpath(company_data[c], "$.permalink"))
		name = json.dumps(jsonpath.jsonpath(company_data[c], "$.name"))
		homepage_url = json.dumps(jsonpath.jsonpath(company_data[c], "$.homepage_url"))
		blog_url = json.dumps(jsonpath.jsonpath(company_data[c], "$.blog_url"))
		description = json.dumps(jsonpath.jsonpath(company_data[c], "$.description"))
		number_of_employees = json.dumps(jsonpath.jsonpath(company_data[c], "$.number_of_employees"))

		#insert
		cur.execute("insert into investor_data(permalink, company_name, homepage_url, blog_url, description, number_of_employees) values(%s, %s, %s, %s, %s, %s)", (permalink, name, homepage_url, blog_url, description, number_of_employees))

	for d in range(0, len(fin_data)):
		permalink = json.dumps(jsonpath.jsonpath(fin_data[d], "$.permalink"))
		name = json.dumps(jsonpath.jsonpath(fin_data[d], "$.name"))
		homepage_url = json.dumps(jsonpath.jsonpath(fin_data[d], "$.homepage_url"))
		blog_url = json.dumps(jsonpath.jsonpath(fin_data[d], "$.blog_url"))
		description = json.dumps(jsonpath.jsonpath(fin_data[d], "$.description"))
		number_of_employees = json.dumps(jsonpath.jsonpath(fin_data[d], "$.number_of_employees"))

		#insert
		cur.execute("insert into investor_data(permalink, company_name, homepage_url, blog_url, description, number_of_employees) values(%s, %s, %s, %s, %s, %s)", (permalink, name, homepage_url, blog_url, description, number_of_employees))

#close database connection
con.close()
