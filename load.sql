-- Loads the generated CSVs into financialdb.
-- Run this from PowerShell, not from inside pgAdmin or a VSCode SQL extension (learned that one the hard way):
--     psql -U postgres -d financialdb -f load.sql
-- Using \copy instead of server-side COPY so the file paths are read from my machine, not from wherever the Postgres server thinks its working directory is.

\set ON_ERROR_STOP on
\timing on

BEGIN;

-- Clear out anything left over from previous attempts. RESTART IDENTITY resets the BIGSERIAL counters back to 1 so the ids in the CSV line up cleanly.
TRUNCATE TABLE
    "transaction", card, beneficiary, roth_ira, four_oh_one_k_account, brokerage_account, loan_account, credit_account, savings_account, checking_account, employee, customer, branch
RESTART IDENTITY CASCADE;

-- Turn off FK checks during the load. The data is internally consistent (the generator made sure of that), so this is safe and shaves a lot of time off the transaction load in particular.
-- With data where I don't trust the integrity, I would leave FK checks on and fix the offending rows as needed.
SET session_replication_role = replica;

-- Order matters here, parents before children, otherwise the foreign keys blow up. Took me a debugging session to figure that one out.

-- Top-level tables with no dependencies
\copy branch
FROM 'C:/developer/SQLProject/synthetic_data/out/branch.csv'
WITH (FORMAT csv, HEADER true, NULL '')

\copy customer
FROM 'C:/developer/SQLProject/synthetic_data/out/customer.csv'
WITH (FORMAT csv, HEADER true, NULL '')

-- Employees belong to a branch
\copy employee
FROM 'C:/developer/SQLProject/synthetic_data/out/employee.csv'
WITH (FORMAT csv, HEADER true, NULL '')

-- All seven account types -- each one references a customer and a branch
\copy checking_account
FROM 'C:/developer/SQLProject/synthetic_data/out/checking_account.csv'
WITH (FORMAT csv, HEADER true, NULL '')

\copy savings_account
FROM 'C:/developer/SQLProject/synthetic_data/out/savings_account.csv'
WITH (FORMAT csv, HEADER true, NULL '')

\copy credit_account
FROM 'C:/developer/SQLProject/synthetic_data/out/credit_account.csv'
WITH (FORMAT csv, HEADER true, NULL '')

\copy loan_account
FROM 'C:/developer/SQLProject/synthetic_data/out/loan_account.csv'
WITH (FORMAT csv, HEADER true, NULL '')

\copy brokerage_account
FROM 'C:/developer/SQLProject/synthetic_data/out/brokerage_account.csv'
WITH (FORMAT csv, HEADER true, NULL '')

\copy four_oh_one_k_account
FROM 'C:/developer/SQLProject/synthetic_data/out/four_oh_one_k_account.csv'
WITH (FORMAT csv, HEADER true, NULL '')

\copy roth_ira
FROM 'C:/developer/SQLProject/synthetic_data/out/roth_ira.csv'
WITH (FORMAT csv, HEADER true, NULL '')

-- Beneficiaries and cards both reference customers (and cards reference accounts)
\copy beneficiary
FROM 'C:/developer/SQLProject/synthetic_data/out/beneficiary.csv'
WITH (FORMAT csv, HEADER true, NULL '')

\copy card
FROM 'C:/developer/SQLProject/synthetic_data/out/card.csv'
WITH (FORMAT csv, HEADER true, NULL '')

-- Transactions reference basically everything, so they go last.
\copy "transaction"
FROM 'C:/developer/SQLProject/synthetic_data/out/transaction.csv'
WITH (FORMAT csv, HEADER true, NULL '')

-- Put FK enforcement back the way we found it
SET session_replication_role = DEFAULT;

-- Bump every BIGSERIAL sequence past the highest id we just loaded. Without this, the next manual INSERT would try to use id=1 and immediately conflict.
SELECT setval
    ('branch_branch_id_seq',
    (SELECT MAX(branch_id)
    FROM branch));

SELECT setval
    ('customer_customer_id_seq',
    (SELECT MAX(customer_id)
    FROM customer));

SELECT setval
    ('employee_employee_id_seq',
    (SELECT MAX(employee_id)
    FROM employee));

SELECT setval
    ('checking_account_checking_account_id_seq',
    (SELECT MAX(checking_account_id)
    FROM checking_account));

SELECT setval
    ('savings_account_savings_account_id_seq',
    (SELECT MAX(savings_account_id)
    FROM savings_account));

SELECT setval
    ('credit_account_credit_account_id_seq',
    (SELECT MAX(credit_account_id)
    FROM credit_account));

SELECT setval
    ('loan_account_loan_account_id_seq',
    (SELECT MAX(loan_account_id)
    FROM loan_account));

SELECT setval
    ('brokerage_account_brokerage_account_id_seq',
    (SELECT MAX(brokerage_account_id)
    FROM brokerage_account));

SELECT setval
    ('four_oh_one_k_account_four_oh_one_k_account_id_seq',
    (SELECT MAX(four_oh_one_k_account_id)
    FROM four_oh_one_k_account));

SELECT setval
    ('roth_ira_roth_ira_id_seq',
    (SELECT MAX(roth_ira_id)
    FROM roth_ira));

SELECT setval
    ('beneficiary_beneficiary_id_seq',
    (SELECT MAX(beneficiary_id)
    FROM beneficiary));

SELECT setval
    ('card_card_id_seq',
    (SELECT MAX(card_id)
    FROM card));

SELECT setval
    ('transaction_transaction_id_seq',
    (SELECT MAX(transaction_id)
    FROM "transaction"));

COMMIT;
