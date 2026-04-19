-- Reconciliation Summary Query
SELECT 
    discrepancy_type,
    COUNT(*) as count,
    SUM(ABS(ISNULL(blockchain_amount, 0) - ISNULL(internal_amount, 0))) as amount_impact_eth,
    SUM(ABS(ISNULL(blockchain_fee, 0) - ISNULL(internal_fee, 0))) as fee_impact_eth
FROM (
    SELECT 
        CASE 
            WHEN b.hash IS NULL THEN 'EXTRA_IN_INTERNAL'
            WHEN i.transaction_hash IS NULL THEN 'MISSING_FROM_INTERNAL'
            WHEN b.value_eth != i.internal_amount_eth THEN 'AMOUNT_MISMATCH'
            WHEN b.fee_eth != i.internal_fee_eth THEN 'FEE_MISMATCH'
            ELSE 'MATCH'
        END as discrepancy_type,
        b.value_eth as blockchain_amount,
        i.internal_amount_eth as internal_amount,
        b.fee_eth as blockchain_fee,
        i.internal_fee_eth as internal_fee
    FROM eth_transactions b
    FULL OUTER JOIN internal_records i ON b.hash = i.transaction_hash
) t
GROUP BY discrepancy_type;

-- Daily Reconciliation Stored Procedure
CREATE OR ALTER PROCEDURE sp_daily_reconciliation
    @report_date DATE = NULL
AS
BEGIN
    IF @report_date IS NULL
        SET @report_date = DATEADD(day, -1, GETDATE())
    
    SELECT 
        CASE 
            WHEN b.hash IS NULL THEN 'EXTRA_IN_INTERNAL'
            WHEN i.transaction_hash IS NULL THEN 'MISSING_FROM_INTERNAL'
            WHEN b.value_eth != i.internal_amount_eth THEN 'AMOUNT_MISMATCH'
            WHEN b.fee_eth != i.internal_fee_eth THEN 'FEE_MISMATCH'
            ELSE 'MATCH'
        END as discrepancy_type,
        COUNT(*) as count
    FROM eth_transactions b
    FULL OUTER JOIN internal_records i ON b.hash = i.transaction_hash
    WHERE CAST(ISNULL(b.timestamp, i.processed_date) AS DATE) = @report_date
    GROUP BY 
        CASE 
            WHEN b.hash IS NULL THEN 'EXTRA_IN_INTERNAL'
            WHEN i.transaction_hash IS NULL THEN 'MISSING_FROM_INTERNAL'
            WHEN b.value_eth != i.internal_amount_eth THEN 'AMOUNT_MISMATCH'
            WHEN b.fee_eth != i.internal_fee_eth THEN 'FEE_MISMATCH'
            ELSE 'MATCH'
        END
END;