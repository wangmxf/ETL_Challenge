#!/usr/bin/python
from urllib2 import urlopen
import json
import MySQLdb as mdb
import jsonpath

#list of companies provided by FindTheBest
#stored in an array so that I could easily query the CrunchBase api
companies = ['clearwire', 'facebook', 'dena', 'solyndra', 'fisker', 'twitter', 'groupon', 'sirius', 'wave-broadband', 
'livingsocial', 'surveymonkey', 'zynga', 'better-place', 'brightsource-energy', 'tesla-motors', 'enel-ogk-5', 'vertex-pharmaceuticals', 
'vivint', 'greatpoint-energy', 'friendfinder-networks', 'bloom-energy', 'm-setek', 'first-wind', 'unitedmobile', 'solarcity', 
'abound-solar', 'homeaway', 'a123systems', 'nanosolar', 'oak-pacific-interactive', 'miasole', 'gree', 'invenergy', 'crucell', 'solopower', 
'bigpoint', 'nextg-networks', 'brash-entertainment', 'nook-media', 'demandmedia', 'reardencommerce', 'vmware', 'i-o-data-centers', 
'bostonpower', 'stormfisher-biogas', 'square', 'xiaomi-tech', 'bonesupport', 'pinterest', 'sunrun', 'qunar-com', 'palo-alto-networks', 
'zenimax', 'kosmos-biotherapeutics', 'horizon-wind-energy', 'sungard', 'oxthera', 'amyris-biotechnologies', 'palantir-technologies', 
'thegenerationsnetwork', 'tower-vision', 'whale-shark-media', 'box', 'chegg']

#declare array to put the api responses in
company_data = []

#loop through the companies array and append responses to company_data array
for x in range(0, len(companies)):
	print 'Getting data for company ' + str(x + 1) + ': ' + companies[x]
	response = json.load(urlopen('http://api.crunchbase.com/v/1/company/' + companies[x] + '.js?api_key=b6erucspnpp9pghb2xxtthn4'))
	company_data.append(response)

#make database connection to mysql
try:
	con = mdb.connect('localhost', 'ftb', 'ftbpw', 'findthebest');

except mdb.Error, e:
	print "Error %d: %s" % (e.args[0],e.args[1])
	sys.exit(1)


#use connection to run sql commands
with con:
	cur = con.cursor()

	for y in range(0, len(company_data)):
		#columns for company_data table
		permalink = json.dumps(jsonpath.jsonpath(company_data[y], "$.permalink"))
		name = json.dumps(jsonpath.jsonpath(company_data[y], "$.name"))
		homepage_url = json.dumps(jsonpath.jsonpath(company_data[y], "$.homepage_url"))
		blog_url = json.dumps(jsonpath.jsonpath(company_data[y], "$.blog_url"))
		description = json.dumps(jsonpath.jsonpath(company_data[y], "$.description"))
		number_of_employees = json.dumps(jsonpath.jsonpath(company_data[y], "$.number_of_employees"))
		founded_day = json.dumps(jsonpath.jsonpath(company_data[y], "$.founded_day"))
		founded_year = json.dumps(jsonpath.jsonpath(company_data[y], "$.founded_year"))
		founded_month = json.dumps(jsonpath.jsonpath(company_data[y], "$.founded_month"))
		total_money_raised = json.dumps(jsonpath.jsonpath(company_data[y], "$.total_money_raised"))
	
		print 'Insert data for ' + companies[y] + ' in to company_data table.'

		#insert in to company_data table
		cur.execute("insert into company_data(permalink, company_name, homepage_url, blog_url, description, number_of_employees, founded_day, founded_year, founded_month, total_money_raised) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (permalink, name, homepage_url, blog_url, description, number_of_employees, founded_day, founded_year, founded_month, total_money_raised))

		print 'Inserting data for ' + companies[y] + ' in to company_funding table.'

		#columns for company_funding table
		funding_rounds = len(jsonpath.jsonpath(company_data[y], "$.funding_rounds[*]"))
		for z in range(0, funding_rounds):
			raised_amount = json.dumps(jsonpath.jsonpath(company_data[y], "$.funding_rounds[" + str(z) + "].raised_amount"))
			funded_year = json.dumps(jsonpath.jsonpath(company_data[y], "$.funding_rounds[" + str(z) + "].funded_year"))

			investments_list = jsonpath.jsonpath(company_data[y], "$.funding_rounds[" + str(z) + "].investments[*]")
			if investments_list:
				investments = len(jsonpath.jsonpath(company_data[y], "$.funding_rounds[" + str(z) + "].investments[*]"))	
				for a in range(0, investments):
					person_permalink = json.dumps(jsonpath.jsonpath(company_data[y], "$.funding_rounds[" + str(z) + "].investments[" + str(a) + "].person.permalink"))
					comp_permalink = json.dumps(jsonpath.jsonpath(company_data[y], "$.funding_rounds[" + str(z) + "].investments[" + str(a) + "].company.permalink"))
					fin_permalink = json.dumps(jsonpath.jsonpath(company_data[y], "$.funding_rounds[" + str(z) + "].investments[" + str(a) + "].financial_org.permalink"))
				
					#insert into company_funding table
					cur.execute("insert into company_funding(permalink, raised_amount, funded_year, person_permalink, comp_permalink, fin_permalink) values(%s, %s, %s, %s, %s, %s)", (permalink, raised_amount, funded_year, person_permalink, comp_permalink, fin_permalink))

#close the database connection
con.close()
