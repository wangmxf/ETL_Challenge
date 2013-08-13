#1. create the company_data table for python insert
create table company_data(
	permalink varchar (50),
	company_name varchar(50),
	homepage_url varchar(100),
	blog_url varchar(100),
	description varchar(50),
	number_of_employees varchar(10),
	founded_day varchar(10),
	founded_year varchar(10),
	founded_month varchar(10),
	total_money_raised varchar(20),
	top10 tinyint
);

#2. create company_funding table for python insert
create table company_funding(
	permalink varchar(50),
	raised_amount varchar(20),
	funded_year varchar(10),
	person_permalink varchar(50),
	comp_permalink varchar(50),
	fin_permalink varchar(50)
);

#3. run crunchBase_companies.py

#4. update company_data to clean up json brackets and null values
update company_data
set permalink = replace(replace(permalink, left(permalink, 2), ''), right(permalink, 2), ''),
	company_name = replace(replace(company_name, left(company_name, 2), ''), right(company_name, 2), ''),
	homepage_url = replace(replace(homepage_url, left(homepage_url, 2), ''), right(homepage_url, 2), ''),
	blog_url = replace(replace(blog_url, left(blog_url, 2), ''), right(blog_url, 2), ''),
	description = replace(replace(description, left(description, 2), ''), right(description, 2), ''),
	number_of_employees = case when number_of_employees = '[null]' then '' else replace(replace(number_of_employees, left(number_of_employees, 1), ''), right(number_of_employees, 1), '') end,
	founded_day = case when founded_day = '[null]' then '' else replace(replace(founded_day, left(founded_day, 1), ''), right(founded_day, 1), '') end,
	founded_year = case when founded_year = '[null]' then '' else replace(replace(founded_year, left(founded_year, 1), ''), right(founded_year, 1), '') end ,
	founded_month = case when founded_month = '[null]' then '' else replace(replace(founded_month, left(founded_month, 1), ''), right(founded_month, 1), '') end,
	total_money_raised = replace(replace(total_money_raised, left(total_money_raised, 2), ''), right(total_money_raised, 2), '');

#5. flag the top 10
update company_data
set top10 = 1
where right(total_money_raised, 1) = 'b'
or permalink = 'livingsocial';

#6. create answer1 table to insert data in to
create table answer1(
	Company_Name varchar(50),
	Homepage_URL varchar(100),
	Blog_URL varchar(100),
	Founded_Date varchar(10),
	Number_of_Employees varchar(10),
	Total_Money_Raised varchar(15)
);

#7. insert top 10 company data
insert into answer1
select Company_Name, Homepage_URL, Blog_URL, concat(
	case when founded_month = '' then '' else founded_month end,
	case when founded_month = '' then '' else '-' end,
	case when founded_day = '' then '' else founded_day + '-' end,
	case when founded_day = '' then '' else '-' end,
	case when founded_year = '' then '' else founded_year end) as Founded_Date, Number_of_Employees, Total_Money_Raised
from company_data
where top10 = 1;

#8. update company_funding to clean up json brackets and false results
update company_funding
set permalink = replace(replace(permalink, left(permalink, 2), ''), right(permalink, 2), ''),
	raised_amount = replace(replace(raised_amount, left(raised_amount, 1), ''), right(raised_amount, 1), ''),
	funded_year = replace(replace(funded_year, left(funded_year, 1), ''), right(funded_year, 1), ''),
	person_permalink = case when person_permalink = 'false' then '' else replace(replace(person_permalink, left(person_permalink, 2), ''), right(person_permalink, 2), '') end,
	comp_permalink = case when comp_permalink = 'false' then '' else replace(replace(comp_permalink, left(comp_permalink, 2), ''), right(comp_permalink, 2), '') end,
	fin_permalink = case when fin_permalink = 'false' then '' else replace(replace(fin_permalink, left(fin_permalink, 2), ''), right(fin_permalink, 2), '') end;

#9. create list of distinct investors (used later for retrieving investor data)
#investor_type: 1 = person, 2 = company, 3 = financial-organization
create table investors(
	investors varchar(50),
	investor_type tinyint
);

#10. insert list of distinct investors
insert into investors
select distinct person_permalink, '1'
from company_funding
where person_permalink <> ''
union
select distinct comp_permalink, '2'
from company_funding
where comp_permalink <> ''
union
select distinct fin_permalink, '3'
from company_funding
where fin_permalink <> ''
order by 1;

#11. funding amounts are given per round of funding
# get distinct list of funding round and year
update company_funding
set raised_amount = convert(raised_amount, unsigned integer);

create table funding_by_year(
	permalink varchar(50),
	raised_amount int,
	funded_year int
);

insert into funding_by_year
select distinct permalink, convert(raised_amount, unsigned integer), funded_year
from company_funding
order by 1, 3;

#12. find the cumulative funding for 2011 and 2012
create table answer2_step1(
	permalink varchar(50),
	funding_2011 int,
	funding_2012 int,
	funding_change int
);

insert into answer2_step1(permalink, funding_2011, funding_2012)
select permalink, sum(case when funded_year <= 2011 then raised_amount end) as funding_2011,
	sum(case when funded_year <= 2012 then raised_amount end) as funding_2012
from funding_by_year
where funded_year <= 2012
group by permalink
order by 1;


#13. calculate the difference and rank the results in to a new table
update answer2_step1
set funding_change = case when funding_2011 is null then funding_2012 else funding_2012 - funding_2011 end;

create table answer2_step2(
	permalink varchar(50),
	funding_2011 int,
	funding_2012 int,
	funding_change int,
	rank smallint
);

set @rank := 0;

insert into answer2_step2
select permalink, funding_2011, funding_2012, funding_change, @rank := @rank + 1
from answer2_step1
order by funding_change desc;

#14. finalize answer 2 results
create table answer2(
	Company_Name varchar(50),
	Description varchar(50),
	Homepage_URL varchar(100),
	Number_of_Employees varchar(10),
	Funding_2011 varchar(20),
	Funding_2012 varchar(20),
	Funding_Change varchar(20),
	Rank smallint
);


insert into answer2
select a.Company_Name, a.Description, a.Homepage_URL, a.Number_of_Employees, concat('$', format(b.Funding_2011, 2)), 
	concat('$', format(b.Funding_2012, 2)), concat('$', format(b.Funding_Change, 2)), b.Rank
from company_data a inner join answer2_step2 b
on a.permalink = b.permalink
and b.rank <= 10
order by b.rank;