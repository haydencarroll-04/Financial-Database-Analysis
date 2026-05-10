# Financial Database - SQL Practice Project

A PostgreSQL database modeled for a financial institution. With ~11 million rows of realistic and intentionally messy synthetic data, I built a self-contained sandbox for practicing data modeling, ETL, SQL, and data analytics.

> **Status: in progress.** Schema, data generation, and load pipeline are complete. Analytics queries, data-cleaning workflows, and dashboards to come.

---

## Part 1: Setting Up the Database

This project started as a way for me to get hands-on practice with an SQL environment that actually feels like something I might see at a real company, instead of the clean, tiny datasets you typically get from tutorials. I designed the 13-table schema myself to model a real financial institution - customers, branches, employees, seven different account products, beneficiaries, cards, and transactions — and wired up the primary keys, foreign keys, and indexes to keep it relationally sound. To populate it, I wrote a Python generator (with the help of Claude Code) that produces 100,000 customers and 10.6 million transactions across a 25-year span, and outputs the data into CSVs. I deliberately made the data messy with inconsistent casing and whitespace, half a dozen phone-number formats, email typos, NULLs, duplicate customers, future-dated records, the occasional negative balance. I wanted to simulate some of the things I might find in a real database that I would need to clean before analysis. From there I built a single-command psql load script that handles all 13 CSVs in FK-dependency order, defers constraint checks for speed, and resets the BIGSERIAL sequences so the database is ready to use afterward. This was all done locally. The next iteration of this project will happen in the cloud.

## Part 2: Data Cleaning

## Part 3: Data Analysis
Q/A's, queries, and results here

## Part 4: Dashboard | PowerBI and Tableau
Show a PowerBI dashboard and a Tableau dashboard here

---

## Tech stack (thus far)

- **PostgreSQL**
- **Python** 
- **psql**
- **PowerShell**
- **Claude Code**

---

## Data model

A retail bank with the following tables:

| Domain | Tables |
|---|---|
| Core | `branch`, `customer`, `employee` |
| Deposit accounts | `checking_account`, `savings_account` |
| Credit / debt | `credit_account`, `loan_account` |
| Investment | `brokerage_account`, `four_oh_one_k_account`, `roth_ira` |
| Supporting | `beneficiary`, `card`, `transaction` |

The `transaction` table fans out to all seven account types via nullable foreign keys.

See 'FinancialDBSchemaMap.pdf' for a more visual representation

---

## Quickstart

```powershell
# 1. Create the schema
psql -U postgres -d financialdb -f schema.sql

# 2. Generate the synthetic data
python synthetic_data/generate.py

# 3. Load it into Postgres
psql -U postgres -d financialdb -f synthetic_data/load.sql

---

## Notes

- Generated CSVs are excluded from version control because of their size. Run `generate.py` to reproduce them; output is deterministic via a fixed random seed.
- Tested on Windows 11 with PostgreSQL 18.
