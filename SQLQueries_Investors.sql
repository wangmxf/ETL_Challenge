#1. create investor_data table
create table investor_data(
	permalink varchar(50),
	first_name varchar(25),
	last_name varchar(25),
	company_name varchar(50),
	homepage_url varchar(100),
	blog_url varchar(150),
	description varchar(50),
	degree_type varchar(25),
	degree_subject varchar(100),
	institution varchar(100),
	number_of_employees varchar(10)
);

#2. create investor_funding table
create table investor_funding(
	permalink varchar(50),
	investment_amt varchar(20),
	investment_year varchar(10),
	investment_company varchar(150)
);

#3. run crunchBase_investors.py
#4. run cb_investordata.py

#5. update investor_data to clean up json brackets
update investor_data
set permalink = replace(replace(permalink, '["', ''), '"]', ''),
	first_name = case when first_name is null then first_name else replace(replace(first_name, '["', ''), '"]', '') end,
	last_name = case when last_name is null then last_name else replace(replace(last_name, '["', ''), '"]', '') end,
	company_name = case when company_name is null then company_name else replace(replace(company_name, '["', ''), '"]', '') end,
	homepage_url = case when homepage_url = '[null]' then null else replace(replace(homepage_url, '["', ''), '"]', '') end,
	blog_url = case when blog_url = '[null]' then null else replace(replace(blog_url, '["', ''), '"]', '') end,
	description = case when description = '[null]' then null else replace(replace(description, '["', ''), '"]', '') end,
	degree_type = case when degree_type is null then degree_type else replace(replace(degree_type, '["', ''), '"]', '') end,
	degree_subject = case when degree_subject is null then degree_subject else replace(replace(degree_subject, '["', ''), '"]', '') end,
	institution = case when institution is null then institution else replace(replace(institution, '["', ''), '"]', '') end,
	number_of_employees = case when number_of_employees = '[null]' then null else replace(replace(number_of_employees, '[', ''), ']', '') end;

#6. update investor_funding to clean up json brackets
update investor_funding
set permalink = replace(replace(permalink, '["', ''), '"]', ''),
	investment_amt = case when investment_amt = '[null]' then null else replace(replace(investment_amt, '[', ''), ']', '') end,
	investment_year = replace(replace(investment_year, '[', ''), ']', ''),
	investment_company = replace(replace(investment_company, '["', ''), '"]', '');
	
#7. create table and derive companies cumulative funding
update investor_funding
set investment_amt = convert(investment_amt, unsigned integer);

create table answer3_step1(
	permalink varchar(50),
	funding varchar(20)
);

insert into answer3_step1
select permalink, sum(investment_amt)
from investor_funding
group by permalink
order by 2 desc;

#8. answer 3
create table answer3(
	Investor_Name varchar(50),
	Description varchar(50),
	Homepage_URL varchar(100),
	Degree_Type varchar(25),
	Degree_Subject varchar(100),
	Institution varchar(100), 
	Number_of_Employees varchar(10),
	Funding varchar(20)
);

insert into answer3
select case when b.company_name is null then concat(b.first_name, ' ', b.last_name) else b.company_name end as Investor_Name,
	b.Description, b.Homepage_URL, b.Degree_Type, b.Degree_Subject, b.Institution, b.Number_of_Employees, 
	concat('$', format(a.Funding, 2)) as Funding
from answer3_step1 a inner join investor_data b
on a.permalink = b.permalink
order by convert(a.funding, unsigned integer) desc
limit 10;

#9. find the cumulative funding for 2011 and 2012
create table answer4_step1(
	permalink varchar(50),
	funding_2011 int,
	funding_2012 int,
	funding_change int
);

insert into answer4_step1(permalink, funding_2011, funding_2012)
select permalink, sum(case when investment_year <= 2011 then investment_amt end) as funding_2011,
	sum(case when investment_year <= 2012 then investment_amt end) as funding_2012
from investor_funding
where investment_year <= 2012
group by permalink
order by 1;

#10. calculate the difference and rankt he results in to a new table
update answer4_step1
set funding_change = case when funding_2011 is null then funding_2012 else funding_2012 - funding_2011 end;

create table answer4_step2(
	permalink varchar(50),
	funding_2011 int,
	funding_2012 int,
	funding_change int,
	rank int
);

set @rank := 0;

insert into answer4_step2
select permalink, funding_2011, funding_2012, funding_change, @rank := @rank + 1
from answer4_step1
order by funding_change desc;

#11. finalize answer 4 results
create table answer4(
	Investor_Name varchar(50),
	Description varchar(50),
	Homepage_URL varchar(100),
	Funding_2011 varchar(20),
	Funding_2012 varchar(20),
	Funding_Change varchar(20),
	Rank smallint
);

insert into answer4
select distinct case when a.company_name is null then concat(a.first_name, ' ', a.last_name) else a.company_name end,
	a.description, a.homepage_url, concat('$', format(b.funding_2011, 2)), concat('$', format(b.funding_2012, 2)), 
	concat('$', format(b.funding_change, 2)), b.rank
from investor_data a inner join answer4_step2 b
on a.permalink = b.permalink
and b.rank <= 10
order by b.rank;