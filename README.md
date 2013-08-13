ETL_Challenge
=============

This was an ETL challenge completed via the [CrunchBase API](http://developer.crunchbase.com). I leveraged Python in order to pull the data and then load it to a MySQL database.

There were 4 objectives:
- Present the top 10 companies in terms of cumulative funding 
- Present the top 10 companies in terms of change in funding from 2011 to 2012 (who is hot now?)
- Present the top 10 investors in terms of cumulative funding
- Present the top 10 investors in terms of change in funding from 2011 to 2012 (who is ramping up?)

A list of companies were provided. These are already loaded to the __crunchBase_companies.py__ script.

Start here: _SQLQueries_Companies.sql_
The comments in the document will step you through how the work was completed and indicate when the Python scripts should be executed.

NOTE: The scripts have had the DB connections and API key generalized, so these will all need to be changed in order to actually run any of this on your own.

I have some edits I'd like to make in the future, based on feedback that was given already. Feel free to reach out with any suggestions of your own though on how this could be improved.