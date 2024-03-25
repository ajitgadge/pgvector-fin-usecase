This exploratory use case is to find the similarity search customer profiles with similar characteristics based on the transactional data stored in RDBMS. In this use case, I have assumed that the customer profile data is generated from their original source of truth data from RDBMS and form the customer profile data that get ingested. Parameters like customer id, age, income ( this is the customer monthly/daily/weekly income-based transactional table ( CR-DR) that gets updated here), spending (DR ), target saving goal (based on customer profile survey ), risk tolerance ( 1-5, 1 is lowest while five is highest based on customer data survey ). Based on this data populated in RDBMS ( PostgreSQL here) from the original data source, I embeded (Use PCA for embedding. https://en.wikipedia.org/wiki/Principal_component_analysis ) this data in vector (pgvector) with K mean as a reference. One can create a multiple reference embedding vector depending on the profile, which is desired). These vectors are now ready for similarity search. We can search with cosine <=>, Euclidean <->, inner product <#> distance depends upon the search profile. Ex: If you find the particular profile that fits your use case and would like to find which other profiles are similar in my database, then you can use the above and limit that similarity. Without vector, you can find exact with =, <> etc. with numeric value but similarity, which you might be interested in some cases like this. I have also provided a ranking programme based on this similarity search so that one can rank the customer profile based on the search criteria.

The above use cases are helpful in similarity searches, recommendations, etc., in financial, retail, and telco domains when someone likes to do simility searches like customer profile similarity searches or product similarity searches, etc. Below are the steps and Python programs that help you to build these demos. 

=========================================================================================================================================================================================================================================================
# pgvector-fin-usecase


**Prepare for the environment.**

I assume you already have Postgres version 13 and above.
**Now let’s install pgvector.**

Install postgres or use Biganimal https://www.enterprisedb.com/products/biganimal-cloud-postgresql or any Postgres variant that you can use with pgvector.

**Install Build Dependencies**

You'll need to make and a C compiler (typically gcc) to compile pgvector, as well as git to clone the repository:

sudo dnf -y install make gcc git

Clone the pgvector GitHub repository:

git clone https://github.com/pgvector/pgvector.git

Navigate to the pgvector directory:

cd pgvector

Compile and install pgvector:

make
sudo make install

login to postgres into your choice of database where you want to enabled the EXTENSION.

CREATE EXTENSION pgvector;


Verify it

SELECT * FROM pg_extension WHERE extname='pgvector';

For more details , 

https://github.com/pgvector/pgvector

**Create your database and then create table**

I am using blog_data as database .

Below is my table script.

CREATE TABLE IF NOT EXISTS public.customer_profiles_fin
(
    customer_id integer NOT NULL DEFAULT nextval('customer_profiles_fin_customer_id_seq'::regclass),
    age integer,
    income integer,
    spending integer,
    target_savings_goal integer,
    risk_tolerance integer,
    embeddings vector(5),
    customer_rank integer,
    CONSTRAINT customer_profiles_fin_pkey PRIMARY KEY (customer_id)
)

Create Index script.


CREATE INDEX IF NOT EXISTS embedding_idx
    ON public.customer_profiles_fin USING ivfflat
    (embeddings)
    TABLESPACE pg_default;

**Now lets prepare python setup.**

Install python lib

brew install python

Check with your Python setup.

python3 --version

Navigate your Python project.

python -m venv venv  # or "python3 -m venv venv" depending on your system

**Install required python packages.**

pip install psycopg2-binary pandas scikit-learn SQLAlchemy numpy Flask matplotlib

Check all these packages you installed correctly or not. If i am missing anything , please go ahead and import.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine
import psycopg2
from flask import Flask


==============================================================

**Generate data**

generate_customer_profile_data.py

**Embedding Data**

customer_profile_embeddings_fin.py

**Reference dimension ( optional)**

calculate_reference_embedding.py

**Ranking **

customer_profile_ranking.py

**You can also do a similarity search by query  to find the customer ID with similar embedding vectors.**

SELECT c1.customer_id, c2.customer_id AS similar_id, 
       c2.embeddings <-> c1.embeddings AS distance
FROM customer_profiles_fin c1, customer_profiles_fin c2
ORDER BY distance limit 10;

You can also add some conditions to find your appropriate customers, like finding customer IDs with more than 15000 income and similar embeddings.

WITH reference_profiles AS (
  SELECT customer_id, embeddings
  FROM customer_profiles_fin
  WHERE customer_id IN (select customer_id from customer_profiles_fin where income > 15000 )
)
SELECT rp.customer_id AS reference_id, cp.customer_id, 
       cp.embeddings <-> rp.embeddings AS distance, age,income, spending,target_savings_goal,risk_tolerance
FROM customer_profiles_fin cp, reference_profiles rp
ORDER BY rp.customer_id, distance
LIMIT 10;

**Plot Graph**

plot_flask_3d.py

plot_flask_5d.py


**Advanced Analytical queries**
**1: Let's calculate a running total of spending to see how cumulative spending grows as we move through the dataset ordered by income**

SELECT
  customer_id,
  age,
  income,
  spending,
  risk_tolerance,
  SUM(spending) OVER (ORDER BY income) AS running_total_spending
FROM customer_profiles_fin order by spending limit 10;

**2: Ranking Customers by Income**
We can use the RANK() function to rank customers based on their income, showing the highest earners first.

SELECT
  customer_id,
  age,
  income,
  spending,
  risk_tolerance,
  RANK() OVER (ORDER BY income DESC) AS income_rank
FROM customer_profiles_fin order by income desc limit 10;

**3. Calculating Averages Partitioned by Age Group**
To analyze how income and spending vary across different age groups, we can partition the data by age and calculate average income and spending for each group. Assuming age groups are divided as follows: 18-25, 26-35, 36-45, 46-55, 56+.

WITH age_grouped AS (
    SELECT
        CASE
            WHEN age BETWEEN 18 AND 25 THEN '18-25'
            WHEN age BETWEEN 26 AND 35 THEN '26-35'
            WHEN age BETWEEN 36 AND 45 THEN '36-45'
            WHEN age BETWEEN 46 AND 55 THEN '46-55'
            ELSE '56+' END AS age_group,
        AVG(income) AS avg_income,
        AVG(spending) AS avg_spending
    FROM customer_profiles_fin
    GROUP BY CASE
            WHEN age BETWEEN 18 AND 25 THEN '18-25'
            WHEN age BETWEEN 26 AND 35 THEN '26-35'
            WHEN age BETWEEN 36 AND 45 THEN '36-45'
            WHEN age BETWEEN 46 AND 55 THEN '46-55'
            ELSE '56+' END
)
SELECT
    age_group,
    round(avg_income,2) as avg_income,
    round(avg_spending,2) as avg_spendings
FROM age_grouped
ORDER BY age_group;

**4:Percentile Analysis of Risk Tolerance**
We might also be interested in understanding the distribution of risk_tolerance scores across our customer base. The PERCENTILE_CONT function can help us find the median risk tolerance score.
sql

SELECT
  risk_tolerance,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY target_savings_goal) AS median_target_saving
FROM customer_profiles_fin
GROUP BY risk_tolerance
ORDER BY risk_tolerance;

**5:Cumulative Distribution of Target Saving by Risk Tolerance**
This query aims to show how accumulated target savings are distributed across different levels of risk tolerance. For each level of risk tolerance, we calculate the cumulative sum of target savings and compare these sums across the groups.

SELECT
  risk_tolerance,
  target_savings_goal,
  SUM(target_savings_goal) OVER (PARTITION BY risk_tolerance ORDER BY target_savings_goal) AS cumulative_target_saving,
  SUM(target_savings_goal) OVER (PARTITION BY risk_tolerance) AS total_target_saving_by_risk,
  (SUM(target_savings_goal) OVER (PARTITION BY risk_tolerance ORDER BY target_savings_goal) /
  SUM(target_savings_goal) OVER (PARTITION BY risk_tolerance)) * 100 AS perc_of_total_target_saving
FROM customer_profiles_fin
ORDER BY risk_tolerance, target_savings_goal desc  limit 10;


5D- Graph.

![image](https://github.com/ajitgadge/pgvector-fin-usecase/assets/35986148/e576192f-ffc0-4584-ace4-97bb917f0bfd)


