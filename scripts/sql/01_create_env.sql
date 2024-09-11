use role accountadmin;
grant usage on warehouse compute_wh to role public;

use role sysadmin;
use warehouse compute_wh;
create database swtt_test;
use schema swtt_test.public;


use role sysadmin;
create or replace TABLE SWTT_TEST.PUBLIC.SUBMIT2 (
	TEAM_ID VARCHAR(16777216),
	PROBLEM_ID VARCHAR(16777216),
	TIMESTAMP TIMESTAMP_NTZ(9),
	IS_CLEAR BOOLEAN,
	KEY VARCHAR(16777216),
	MAX_ATTEMPTS NUMBER(38,0)
);


use role sysadmin;
create or replace TABLE SWTT_TEST.PUBLIC.HAND_DATA (
	ID NUMBER(38,0) autoincrement start 1 increment 1 noorder,
	TEAM_ID VARCHAR(16777216),
	HAND VARCHAR(1)
);


use role accountadmin;
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
select snowflake.cortex.complete('snowflake-arctic', 'こんにちは。あなたは誰ですか？');