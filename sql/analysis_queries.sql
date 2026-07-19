-- =====================================================================
-- SOUKIQ (WAFR) EXECUTIVE C-SUITE SQL ANALYTICS LAYER
-- Target: PostgreSQL | Focus: Business Insights & Decision Making
-- =====================================================================

-- =====================================================================
-- 1. MoM FINANCIAL PULSE (GMV, Net Revenue, and Blended Take-Rate)
-- Business Value: Tells the CEO/CFO if we are growing profitably or just moving volume.
-- =====================================================================
WITH MonthlyMetrics AS (
    SELECT 
        DATE_TRUNC('month', transaction_datetime) AS billing_month,
        SUM(amount_mad) AS total_gmv,
        SUM(amount_mad * commission_rate) AS net_revenue,
        COUNT(transaction_id) AS total_txns
    FROM fact_transaction
    WHERE status = 'Success'
    GROUP BY 1
)
SELECT 
    TO_CHAR(billing_month, 'YYYY-MM') AS month,
    ROUND(total_gmv, 2) AS total_gmv_mad,
    ROUND(net_revenue, 2) AS net_revenue_mad,
    total_txns,
    ROUND((net_revenue / total_gmv) * 100, 3) AS blended_take_rate_pct,
    ROUND(((net_revenue - LAG(net_revenue) OVER (ORDER BY billing_month)) / 
           NULLIF(LAG(net_revenue) OVER (ORDER BY billing_month), 0)) * 100, 2) AS mom_net_revenue_growth_pct
FROM MonthlyMetrics
ORDER BY billing_month DESC;


-- =====================================================================
-- 2. REGIONAL PROFIT ENGINES (City Margin Analysis)
-- Business Value: Identifies where we should focus our expansion budget (Agadir vs Fes vs Casa).
-- =====================================================================
SELECT 
    m.city,
    COUNT(t.transaction_id) AS total_success_txns,
    ROUND(SUM(t.amount_mad), 2) AS total_gmv_mad,
    ROUND(SUM(t.amount_mad * t.commission_rate), 2) AS net_revenue_mad,
    ROUND((SUM(t.amount_mad * t.commission_rate) / SUM(t.amount_mad)) * 100, 3) AS city_take_rate_pct
FROM fact_transaction t
JOIN dim_merchant m ON t.merchant_id = m.merchant_id
WHERE t.status = 'Success'
GROUP BY m.city
ORDER BY net_revenue_mad DESC;


-- =====================================================================
-- 3. PRODUCT ECONOMICS (Service & Provider Matrix)
-- Business Value: Tells us which product vertical keeps our lights on (Gaming vs Telecom).
-- =====================================================================
SELECT 
    service,
    provider,
    COUNT(transaction_id) AS transaction_count,
    ROUND(SUM(amount_mad), 2) AS total_gmv_mad,
    ROUND(SUM(amount_mad * commission_rate), 2) AS net_revenue_mad,
    ROUND(AVG(commission_rate) * 100, 2) AS avg_commission_rate_pct
FROM fact_transaction
WHERE status = 'Success'
GROUP BY service, provider
ORDER BY net_revenue_mad DESC;


-- =====================================================================
-- 4. DIGITAL ADOPTION (MoM Wallet Penetration)
-- Business Value: Tracks our shift towards digital payments (eliminating cash logistics).
-- =====================================================================
SELECT 
    TO_CHAR(DATE_TRUNC('month', transaction_datetime), 'YYYY-MM') AS month,
    COUNT(transaction_id) AS total_transactions,
    SUM(CASE WHEN payment_method = 'Wallet' THEN 1 ELSE 0 END) AS wallet_transactions,
    ROUND((SUM(CASE WHEN payment_method = 'Wallet' THEN 1 ELSE 0 END)::NUMERIC / COUNT(transaction_id)) * 100, 2) AS wallet_penetration_rate_pct
FROM fact_transaction
WHERE status = 'Success'
GROUP BY 1
ORDER BY 1;


-- =====================================================================
-- 5. SEGMENT-SPECIFIC WALLET ADOPTION
-- Business Value: Proves if high-value Premium merchants are adopting Wallet faster than Standard.
-- =====================================================================
SELECT 
    m.segment,
    COUNT(t.transaction_id) AS total_txns,
    SUM(CASE WHEN t.payment_method = 'Wallet' THEN 1 ELSE 0 END) AS wallet_txns,
    ROUND((SUM(CASE WHEN t.payment_method = 'Wallet' THEN 1 ELSE 0 END)::NUMERIC / COUNT(t.transaction_id)) * 100, 2) AS wallet_adoption_pct
FROM fact_transaction t
JOIN dim_merchant m ON t.merchant_id = m.merchant_id
WHERE t.status = 'Success'
GROUP BY m.segment;


-- =====================================================================
-- 6. AVERAGE TICKET VALUE (Cash vs. Wallet)
-- Business Value: Do digital wallet transactions lead to larger average basket sizes?
-- =====================================================================
SELECT 
    payment_method,
    service,
    COUNT(transaction_id) AS txns,
    ROUND(AVG(amount_mad), 2) AS avg_ticket_size_mad
FROM fact_transaction
WHERE status = 'Success'
GROUP BY payment_method, service
ORDER BY service, payment_method;


-- =====================================================================
-- 7. SILENT MERCHANT CHURN (Inactivity Rule)
-- Business Value: Generates a list of dormant merchants (>30 days inactive) to trigger retention alerts.
-- =====================================================================
WITH MerchantLastTxn AS (
    SELECT 
        m.merchant_id,
        m.store_name,
        m.city,
        m.join_date,
        MAX(t.transaction_datetime) AS last_active_datetime,
        -- Reference date is 2026-06-30 (End of our H1 data)
        ('2026-06-30 23:59:59'::TIMESTAMP - MAX(t.transaction_datetime)) AS inactive_interval
    FROM dim_merchant m
    LEFT JOIN fact_transaction t ON m.merchant_id = t.merchant_id AND t.status = 'Success'
    GROUP BY m.merchant_id, m.store_name, m.city, m.join_date
)
SELECT 
    merchant_id,
    store_name,
    city,
    join_date,
    COALESCE(last_active_datetime::TEXT, 'NEVER TRANSACTED') AS last_active,
    EXTRACT(DAY FROM inactive_interval) AS days_inactive,
    CASE 
        WHEN EXTRACT(DAY FROM inactive_interval) > 30 OR last_active_datetime IS NULL THEN 'Churned'
        WHEN EXTRACT(DAY FROM inactive_interval) BETWEEN 15 AND 30 THEN 'At Risk'
        ELSE 'Active'
    END AS churn_segmentation
FROM MerchantLastTxn
ORDER BY days_inactive DESC NULLS FIRST;


-- =====================================================================
-- 8. MONTHLY COHORT RETENTION HEATMAP
-- Business Value: The ultimate metric for commercial health. Are merchants acquired in Jan still active in Jun?
-- =====================================================================
WITH MerchantCohorts AS (
    -- Define Cohort as the Join Month
    SELECT 
        merchant_id,
        DATE_TRUNC('month', join_date) AS cohort_month
    FROM dim_merchant
),
MerchantActivity AS (
    -- Extract months where the merchant actually transacted successfully
    SELECT DISTINCT
        merchant_id,
        DATE_TRUNC('month', transaction_datetime) AS activity_month
    FROM fact_transaction
    WHERE status = 'Success'
),
CohortTenure AS (
    -- Calculate months active since joining
    SELECT 
        c.cohort_month,
        a.activity_month,
        ROUND(EXTRACT(DAY FROM (a.activity_month - c.cohort_month)) / 30.4) AS month_number,
        COUNT(DISTINCT c.merchant_id) AS active_merchants
    FROM MerchantCohorts c
    JOIN MerchantActivity a ON c.merchant_id = a.merchant_id
    GROUP BY 1, 2, 3
),
CohortSizes AS (
    -- Size of each cohort at Month 0
    SELECT 
        cohort_month,
        COUNT(DISTINCT merchant_id) AS cohort_size
    FROM dim_merchant
    GROUP BY 1
)
SELECT 
    TO_CHAR(t.cohort_month, 'YYYY-MM') AS cohort_month,
    t.month_number AS tenure_month,
    s.cohort_size,
    t.active_merchants,
    ROUND((t.active_merchants::NUMERIC / s.cohort_size) * 100, 2) AS retention_rate_pct
FROM CohortTenure t
JOIN CohortSizes s ON t.cohort_month = s.cohort_month
WHERE t.month_number <= 5
ORDER BY t.cohort_month, t.month_number;


-- =====================================================================
-- 9. PARETO REVENUE CONTRIBUTION (The 80/20 Rule)
-- Business Value: Proves if we depend on a tiny elite of merchants, making us vulnerable.
-- =====================================================================
WITH MerchantRevenue AS (
    SELECT 
        merchant_id,
        SUM(amount_mad * commission_rate) AS merchant_net_revenue
    FROM fact_transaction
    WHERE status = 'Success'
    GROUP BY merchant_id
),
RunningRevenue AS (
    SELECT 
        merchant_id,
        merchant_net_revenue,
        SUM(merchant_net_revenue) OVER (ORDER BY merchant_net_revenue DESC) AS cumulative_revenue,
        SUM(merchant_net_revenue) OVER () AS total_revenue,
        ROW_NUMBER() OVER (ORDER BY merchant_net_revenue DESC) AS merchant_rank,
        COUNT(*) OVER () AS total_merchants
    FROM MerchantRevenue
)
SELECT 
    merchant_rank,
    merchant_id,
    ROUND(merchant_net_revenue, 2) AS net_revenue_mad,
    ROUND((merchant_net_revenue / total_revenue) * 100, 3) AS rev_percentage,
    ROUND((cumulative_revenue / total_revenue) * 100, 2) AS cumulative_rev_percentage,
    ROUND((merchant_rank::NUMERIC / total_merchants) * 100, 2) AS cumulative_merchant_percentage
FROM RunningRevenue
ORDER BY merchant_rank;


-- =====================================================================
-- 10. COST OF OPERATIONS FAILURE (Outages & Lost Commissions)
-- Business Value: Re-frames IT glitches as lost money. COO/CFO can use this to hold telecom SLA.
-- =====================================================================
SELECT 
    o.outage_id,
    o.provider,
    o.reason,
    COUNT(t.transaction_id) AS failed_txns_during_outage,
    ROUND(SUM(t.amount_mad), 2) AS lost_gmv_mad,
    ROUND(SUM(t.amount_mad * t.commission_rate), 2) AS lost_commission_revenue_mad
FROM fact_transaction t
JOIN dim_outage o ON t.provider = o.provider 
    AND t.transaction_datetime BETWEEN o.start_datetime AND o.end_datetime
WHERE t.status = 'Failed'
GROUP BY 1, 2, 3
ORDER BY lost_commission_revenue_mad DESC;


-- =====================================================================
-- 11. PLATFORM TRANSACTION SUCCESS RATE (TSR)
-- Business Value: Core Ops KPI tracking platform transaction reliability.
-- =====================================================================
SELECT 
    service,
    provider,
    COUNT(transaction_id) AS total_attempts,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS successful_txns,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_txns,
    ROUND((SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END)::NUMERIC / COUNT(transaction_id)) * 100, 2) AS success_rate_pct
FROM fact_transaction
GROUP BY service, provider
ORDER BY success_rate_pct ASC;


-- =====================================================================
-- 12. MARKETING CAMPAIGN ROI (ROMI)
-- Business Value: Proves if marketing campaigns actually drive profit or waste cash.
-- =====================================================================
SELECT 
    c.campaign_name,
    c.budget AS campaign_budget,
    COUNT(t.transaction_id) AS promo_txns,
    ROUND(SUM(t.amount_mad), 2) AS promo_gmv,
    ROUND(SUM(t.amount_mad * t.commission_rate), 2) AS promo_net_revenue,
    -- ROMI = (Net Revenue / Budget)
    ROUND((SUM(t.amount_mad * t.commission_rate) / c.budget), 2) AS return_on_marketing_investment_romi
FROM fact_transaction t
JOIN dim_campaign c ON t.campaign_id = c.campaign_id
WHERE t.status = 'Success'
GROUP BY c.campaign_name, c.budget;