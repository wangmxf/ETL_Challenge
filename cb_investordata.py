#!/usr/bin/python
from urllib2 import urlopen
import json
import MySQLdb as mdb
import jsonpath

#make database connection
try:
	con = mdb.connect('localhost', 'user', 'password', 'database');
except mdb.Error, e:
	print "Error %d, %s" % (e.args[0],e.args[1])
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
	#insert data in to investor_funding table
	for a in range(0, len(personal_data)):
		permalink = json.dumps(jsonpath.jsonpath(personal_data[a], "$.permalink"))
		
		investments = len(jsonpath.jsonpath(personal_data[a], "$.investments[*]"))
		for b in range(0, investments):
			investment_amt = json.dumps(jsonpath.jsonpath(personal_data[a], "$.investments[" + str(b) + "].funding_round.raised_amount"))
			investment_year = json.dumps(jsonpath.jsonpath(personal_data[a], "$.investments[" + str(b) + "].funding_round.funded_year"))
			investment_company = json.dumps(jsonpath.jsonpath(personal_data[a], "$.investments[" + str(b) + "].funding_round.company.name"))
			
			#insert
			print 'Loading ' + permalink + ' investment in ' + investment_company
			cur.execute("insert into investor_funding(permalink, investment_amt, investment_year, investment_company) values(%s, %s, %s, %s)", (permalink, investment_amt, investment_year, investment_company))

	for c in range(0, len(company_data)):
		permalink = json.dumps(jsonpath.jsonpath(company_data[c], "$.permalink"))

		investments = len(jsonpath.jsonpath(company_data[c], "$.investments[*]"))
		for d in range(0, investments):
			investment_amt = json.dumps(jsonpath.jsonpath(company_data[c], "$.investments[" + str(d) + "].funding_round.raised_amount"))
			investment_year = json.dumps(jsonpath.jsonpath(company_data[c], "$.investments[" + str(d) + "].funding_round.funded_year"))
			investment_company = json.dumps(jsonpath.jsonpath(company_data[c], "$.investments[" + str(d) + "].funding_round.company.name"))

			#insert
			print 'Loading ' + permalink + ' investment in ' + investment_company
			cur.execute("insert into investor_funding(permalink, investment_amt, investment_year, investment_company) values(%s, %s, %s, %s)", (permalink, investment_amt, investment_year, investment_company))

	for e in range(0, len(fin_data)):
		permalink = json.dumps(jsonpath.jsonpath(fin_data[e], "$.permalink"))

		investments = len(jsonpath.jsonpath(fin_data[e], "$.investments[*]"))
		for f in range(0, investments):
			investment_amt = json.dumps(jsonpath.jsonpath(fin_data[e], "$.investments[" + str(f) + "].funding_round.raised_amount"))
			investment_year = json.dumps(jsonpath.jsonpath(fin_data[e], "$.investments[" + str(f) + "].funding_round.funded_year"))
			investment_company = json.dumps(jsonpath.jsonpath(fin_data[e], "$.investments[" + str(f) + "].funding_round.company.name"))

			#insert
			print 'Loading ' + permalink + ' investment in ' + investment_company
			cur.execute("insert into investor_funding(permalink, investment_amt, investment_year, investment_company) values(%s, %s, %s, %s)", (permalink, investment_amt, investment_year, investment_company))

#close the database connection
con.close()
