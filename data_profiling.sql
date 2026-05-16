-- missing contact info
SELECT
    'customer_missing_fields' AS check_name,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER 
        (WHERE email IS NULL OR TRIM(email) = '') AS missing_email,
    COUNT(*) FILTER 
        (WHERE phone IS NULL OR TRIM(phone) = '') AS missing_phone,
    COUNT(*) FILTER 
        (WHERE dob IS NULL) AS missing_dob,
    COUNT(*) FILTER 
        (WHERE address IS NULL OR TRIM(address) = '') AS missing_address
FROM customer;


-- name hygiene
SELECT
    'customer_name_hygiene' AS check_name,
    COUNT(*) 
        FILTER (WHERE first_name <> TRIM(first_name)
        OR last_name  <> TRIM(last_name)) AS whitespace_padded,
    COUNT(*)
        FILTER (WHERE first_name = UPPER(first_name)
        AND first_name <> LOWER(first_name)) AS all_caps_first,
    COUNT(*) 
        FILTER (WHERE first_name = LOWER(first_name)
        AND first_name <> UPPER(first_name)) AS all_lower_first
FROM customer;


-- customer email format problems
SELECT
    'customer_email_problems' AS check_name,
    COUNT(*) FILTER 
        (WHERE email NOT LIKE '%@%') AS no_AT_sign,
    COUNT(*) FILTER 
        (WHERE email LIKE '%@%@%') AS multiple_AT_signs,
    COUNT(*) FILTER 
        (WHERE email LIKE '%..%') AS double_dot,
    COUNT(*) FILTER 
        (WHERE email <> TRIM(email)) AS whitespace_padded,
    COUNT(*) FILTER 
        (WHERE email ~ '(gmial|gmai|yaho|hotnail|outloook|\.con)') AS likely_domain_typo
FROM customer
WHERE email IS NOT NULL AND TRIM(email) <> '';


-- customer phone format distribution
SELECT
    'customer_phone_formats' AS check_name,
    CASE
        WHEN phone IS NULL OR TRIM(phone) = '' THEN '(missing)'
        WHEN phone ~ '^\(\d{3}\) \d{3}-\d{4}$' THEN 'US_parens'
        WHEN phone ~ '^\d{3}-\d{3}-\d{4}$' THEN 'US_dashes'
        WHEN phone ~ '^\d{3}\.\d{3}\.\d{4}$' THEN 'US_dots'
        WHEN phone ~ '^\d{10}$' THEN 'digits_only'
        WHEN phone ~ '^\+1' THEN 'country_code'
        WHEN phone ~ '^\d{3} \d{3} \d{4}$' THEN 'US_spaces'
        ELSE 'OTHER_OR_INVALID'
    END AS phone_format,
    COUNT(*) AS rows
FROM customer
GROUP BY 2
ORDER BY rows DESC;


-- customer implausible date of birth
SELECT
    'customer_bad_dob' AS check_name,
    COUNT(*) FILTER 
        (WHERE dob > CURRENT_DATE - INTERVAL '18 years') AS under_18,
    COUNT(*) FILTER 
        (WHERE dob < CURRENT_DATE - INTERVAL '120 years') AS over_120,
    COUNT(*) FILTER 
        (WHERE dob > CURRENT_DATE) AS born_in_future
FROM customer
WHERE dob IS NOT NULL;


-- customer likely duplicates (same name + dob)
SELECT
    'customer_duplicates' AS check_name,
    COUNT(*) AS duplicate_groups,
    COALESCE(SUM(grp - 1), 0) AS extra_rows_to_resolve
FROM (
    SELECT COUNT(*) AS grp
    FROM customer
    WHERE dob IS NOT NULL
    GROUP BY LOWER(TRIM(first_name)), LOWER(TRIM(last_name)), dob
    HAVING COUNT(*) > 1
) d;


-- acccount status distribution (looking for impossible or suspicious values)
SELECT 'checking' AS tbl, status, COUNT(*) AS rows FROM checking_account 
    GROUP BY status
    UNION ALL
SELECT 'savings', status, COUNT(*) AS rows FROM savings_account
    GROUP BY status
    UNION ALL
SELECT 'credit', status, COUNT(*) AS rows FROM credit_account
    GROUP BY status
ORDER BY 1, 3 DESC;


-- Negative balances on deposit accounts
SELECT 'checking'  AS tbl, 
    COUNT(*) AS negative_balances 
    FROM checking_account
    WHERE balance < 0
UNION ALL SELECT 'savings',
    COUNT(*) AS negative_balances
    FROM savings_account
    WHERE balance < 0
UNION ALL SELECT 'brokerage',
    COUNT(*) AS negative_balances
    FROM brokerage_account
    WHERE balance < 0
UNION ALL SELECT 'roth_ira',
    COUNT(*) AS negative_balances
    FROM roth_ira
    WHERE balance < 0;


-- Future-dated open_date
SELECT 'checking' AS tbl, 
    COUNT(*) AS future_open_dates 
    FROM checking_account 
    WHERE open_date > CURRENT_DATE
UNION ALL SELECT 'savings', 
    COUNT(*) AS future_open_dates 
    FROM savings_account 
    WHERE open_date > CURRENT_DATE
UNION ALL SELECT 'credit',  
    COUNT(*) AS future_open_dates 
    FROM credit_account  
    WHERE open_date > CURRENT_DATE
UNION ALL SELECT 'loan',    
    COUNT(*) AS future_open_dates 
    FROM loan_account    
    WHERE open_date > CURRENT_DATE;


-- Other impossible / suspicious values
SELECT 'loans_maturity_before_open' AS check_name,
    COUNT(*) AS amount 
    FROM loan_account 
    WHERE maturity_date < open_date
UNION ALL SELECT 'credit_over_limit',
    COUNT(*) AS amount 
    FROM credit_account 
    WHERE current_balance > credit_limit
UNION ALL SELECT 'transactions_in_future',
    COUNT(*) AS amount 
    FROM "transaction" 
    WHERE transaction_date > NOW();


-- Beneficiary relationship typos
SELECT
    'beneficiary_relationships' AS check_name,
    relationship,
    COUNT(*) AS amount
FROM beneficiary
GROUP BY relationship
ORDER BY amount DESC;

