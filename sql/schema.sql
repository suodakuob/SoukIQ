-- SOUKIQ RETAIL ANALYTICS SCHEMA
-- Target Database: PostgreSQL

-- Drop tables if they exist to ensure clean slate (Cascade handles constraints)
DROP TABLE IF EXISTS fact_transaction CASCADE;
DROP TABLE IF EXISTS dim_outage CASCADE;
DROP TABLE IF EXISTS dim_campaign CASCADE;
DROP TABLE IF EXISTS dim_merchant CASCADE;

-- 1. Dim Merchant (5 Columns matching merchants.csv)
CREATE TABLE dim_merchant (
    merchant_id VARCHAR(50) PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    join_date DATE NOT NULL,
    segment VARCHAR(50) NOT NULL
);

-- 2. Dim Campaign
CREATE TABLE dim_campaign (
    campaign_id INT PRIMARY KEY,
    campaign_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    target_service VARCHAR(50) NOT NULL,
    budget DECIMAL(12,2) NOT NULL
);

-- 3. Dim Outage
CREATE TABLE dim_outage (
    outage_id INT PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    reason VARCHAR(255) NOT NULL
);

-- 4. Fact Transaction
CREATE TABLE fact_transaction (
    transaction_id VARCHAR(50) PRIMARY KEY,
    merchant_id VARCHAR(50) REFERENCES dim_merchant(merchant_id),
    transaction_datetime TIMESTAMP NOT NULL,
    service VARCHAR(50) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    amount_mad DECIMAL(10,2) NOT NULL,
    commission_rate DECIMAL(5,4) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    campaign_id INT -- Handled as nullable FK (Null means organic transaction)
);

-- PERFORMANCE OPTIMIZATION INDEXES
CREATE INDEX idx_txn_datetime ON fact_transaction(transaction_datetime);
CREATE INDEX idx_txn_merchant ON fact_transaction(merchant_id);
CREATE INDEX idx_txn_status ON fact_transaction(status);
CREATE INDEX idx_txn_service_provider ON fact_transaction(service, provider);