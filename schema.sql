-- Step 1: Run this (schema.sql) against an empty database
-- Step 2: Run the generate.py script to generate synthetic data
-- Step 3: Run the load.sql script to load the data into the database

CREATE TABLE branch (
    branch_id BIGSERIAL PRIMARY KEY,
    branch_name VARCHAR(150) NOT NULL,
    routing_number VARCHAR(20) NOT NULL,
    address TEXT
);

CREATE TABLE customer (
    customer_id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dob DATE,
    email VARCHAR(255),
    phone VARCHAR(30),
    address TEXT
);

CREATE TABLE employee (
    employee_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(100),
    hire_date DATE,
    CONSTRAINT fk_employee_branch
        FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

CREATE TABLE checking_account (
    checking_account_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    branch_id BIGINT NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    open_date DATE,
    status VARCHAR(50),
    balance NUMERIC(15,2) DEFAULT 0,
    CONSTRAINT fk_checking_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT fk_checking_branch
        FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

CREATE TABLE savings_account (
    savings_account_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    branch_id BIGINT NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    interest_rate NUMERIC(5,2),
    open_date DATE,
    status VARCHAR(50),
    balance NUMERIC(15,2) DEFAULT 0,
    CONSTRAINT fk_savings_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT fk_savings_branch
        FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

CREATE TABLE credit_account (
    credit_account_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    branch_id BIGINT NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    credit_limit NUMERIC(15,2),
    apr NUMERIC(5,2),
    open_date DATE,
    status VARCHAR(50),
    current_balance NUMERIC(15,2) DEFAULT 0,
    CONSTRAINT fk_credit_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT fk_credit_branch
        FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

CREATE TABLE loan_account (
    loan_account_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    branch_id BIGINT NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    loan_type VARCHAR(100),
    principal_amount NUMERIC(15,2),
    interest_rate NUMERIC(5,2),
    open_date DATE,
    maturity_date DATE,
    status VARCHAR(50),
    CONSTRAINT fk_loan_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT fk_loan_branch
        FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

CREATE TABLE brokerage_account (
    brokerage_account_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    branch_id BIGINT NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    account_type VARCHAR(100),
    open_date DATE,
    status VARCHAR(50),
    balance NUMERIC(15,2) DEFAULT 0,
    CONSTRAINT fk_brokerage_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT fk_brokerage_branch
        FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

CREATE TABLE four_oh_one_k_account (
    four_oh_one_k_account_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    branch_id BIGINT NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    company_match NUMERIC(5,2),
    account_type VARCHAR(100),
    open_date DATE,
    status VARCHAR(50),
    balance NUMERIC(15,2) DEFAULT 0,
    CONSTRAINT fk_401k_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT fk_401k_branch
        FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

CREATE TABLE roth_ira (
    roth_ira_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    branch_id BIGINT NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    account_type VARCHAR(100),
    open_date DATE,
    status VARCHAR(50),
    balance NUMERIC(15,2) DEFAULT 0,
    CONSTRAINT fk_roth_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT fk_roth_branch
        FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

CREATE TABLE beneficiary (
    beneficiary_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    name VARCHAR(150) NOT NULL,
    bank_name VARCHAR(150),
    beneficiary_account_number VARCHAR(50),
    relationship VARCHAR(100),
    CONSTRAINT fk_beneficiary_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

CREATE TABLE card (
    card_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    checking_account_id BIGINT,
    credit_account_id BIGINT,
    brokerage_account_id BIGINT,
    four_oh_one_k_account_id BIGINT,
    card_type VARCHAR(50),
    card_number VARCHAR(50) NOT NULL,
    expiration_date DATE,
    status VARCHAR(50),
    CONSTRAINT fk_card_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT fk_card_checking
        FOREIGN KEY (checking_account_id) REFERENCES checking_account(checking_account_id),
    CONSTRAINT fk_card_credit
        FOREIGN KEY (credit_account_id) REFERENCES credit_account(credit_account_id),
    CONSTRAINT fk_card_brokerage
        FOREIGN KEY (brokerage_account_id) REFERENCES brokerage_account(brokerage_account_id),
    CONSTRAINT fk_card_401k
        FOREIGN KEY (four_oh_one_k_account_id) REFERENCES four_oh_one_k_account(four_oh_one_k_account_id)
);

CREATE TABLE transaction (
    transaction_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    employee_id BIGINT NOT NULL,
    checking_account_id BIGINT,
    savings_account_id BIGINT,
    credit_account_id BIGINT,
    loan_account_id BIGINT,
    brokerage_account_id BIGINT,
    four_oh_one_k_account_id BIGINT,
    roth_ira_id BIGINT,
    transaction_type VARCHAR(100) NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    description TEXT,
    CONSTRAINT fk_transaction_customer
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT fk_transaction_employee
        FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
    CONSTRAINT fk_transaction_checking
        FOREIGN KEY (checking_account_id) REFERENCES checking_account(checking_account_id),
    CONSTRAINT fk_transaction_savings
        FOREIGN KEY (savings_account_id) REFERENCES savings_account(savings_account_id),
    CONSTRAINT fk_transaction_credit
        FOREIGN KEY (credit_account_id) REFERENCES credit_account(credit_account_id),
    CONSTRAINT fk_transaction_loan
        FOREIGN KEY (loan_account_id) REFERENCES loan_account(loan_account_id),
    CONSTRAINT fk_transaction_brokerage
        FOREIGN KEY (brokerage_account_id) REFERENCES brokerage_account(brokerage_account_id),
    CONSTRAINT fk_transaction_401k
        FOREIGN KEY (four_oh_one_k_account_id) REFERENCES four_oh_one_k_account(four_oh_one_k_account_id),
    CONSTRAINT fk_transaction_roth
        FOREIGN KEY (roth_ira_id) REFERENCES roth_ira(roth_ira_id)
);

-- Indexes on foreign keys and the transaction date.
-- Reminder: Postgres auto-indexes primary keys, but FK columns and any column you frequently filter or sort on need explicit indexes.
CREATE INDEX idx_employee_branch_id
ON employee(branch_id);

CREATE INDEX idx_checking_customer_id
ON checking_account(customer_id);

CREATE INDEX idx_checking_branch_id
ON checking_account(branch_id);

CREATE INDEX idx_savings_customer_id
ON savings_account(customer_id);

CREATE INDEX idx_savings_branch_id
ON savings_account(branch_id);

CREATE INDEX idx_credit_customer_id
ON credit_account(customer_id);

CREATE INDEX idx_credit_branch_id
ON credit_account(branch_id);

CREATE INDEX idx_loan_customer_id
ON loan_account(customer_id);

CREATE INDEX idx_loan_branch_id
ON loan_account(branch_id);

CREATE INDEX idx_brokerage_customer_id
ON brokerage_account(customer_id);

CREATE INDEX idx_brokerage_branch_id
ON brokerage_account(branch_id);

CREATE INDEX idx_401k_customer_id
ON four_oh_one_k_account(customer_id);

CREATE INDEX idx_401k_branch_id
ON four_oh_one_k_account(branch_id);

CREATE INDEX idx_roth_customer_id
ON roth_ira(customer_id);

CREATE INDEX idx_roth_branch_id
ON roth_ira(branch_id);

CREATE INDEX idx_beneficiary_customer_id
ON beneficiary(customer_id);

CREATE INDEX idx_card_customer_id
ON card(customer_id);

CREATE INDEX idx_transaction_customer_id
ON transaction(customer_id);

CREATE INDEX idx_transaction_employee_id
ON transaction(employee_id);

CREATE INDEX idx_transaction_date
ON transaction(transaction_date);
