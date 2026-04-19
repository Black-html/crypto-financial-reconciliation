import pyodbc
import pandas as pd
from datetime import datetime
import os

# Create outputs folder if it doesn't exist
output_folder = 'outputs'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# SQL Server connection
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DYBG\\SQLEXPRESS;'
    'DATABASE=CryptoAnalytics;'
    'Trusted_Connection=yes;'
)

# Dictionary of all queries to export
queries = {
    '01_reconciliation_summary': """
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
        GROUP BY discrepancy_type
    """,
    
    '02_daily_discrepancy_trend': """
        SELECT 
            CAST(ISNULL(b.timestamp, i.processed_date) AS DATE) as date,
            COUNT(*) as total_transactions,
            SUM(CASE WHEN b.hash IS NULL THEN 1 ELSE 0 END) as extra_in_internal,
            SUM(CASE WHEN i.transaction_hash IS NULL THEN 1 ELSE 0 END) as missing_from_internal,
            SUM(CASE WHEN b.value_eth != i.internal_amount_eth THEN 1 ELSE 0 END) as amount_mismatch,
            SUM(CASE WHEN b.fee_eth != i.internal_fee_eth THEN 1 ELSE 0 END) as fee_mismatch
        FROM eth_transactions b
        FULL OUTER JOIN internal_records i ON b.hash = i.transaction_hash
        GROUP BY CAST(ISNULL(b.timestamp, i.processed_date) AS DATE)
        ORDER BY date
    """,
    
    '03_sample_transactions': """
        SELECT TOP 100
            hash,
            CAST(timestamp AS DATE) as date,
            value_eth,
            fee_eth,
            [from],
            [to]
        FROM eth_transactions
        ORDER BY timestamp DESC
    """,
    
    '04_financial_impact_by_date': """
        SELECT 
            CAST(b.timestamp AS DATE) as date,
            COUNT(*) as mismatch_count,
            SUM(ABS(b.value_eth - ISNULL(i.internal_amount_eth, 0))) as total_amount_impact_eth,
            SUM(ABS(b.fee_eth - ISNULL(i.internal_fee_eth, 0))) as total_fee_impact_eth
        FROM eth_transactions b
        LEFT JOIN internal_records i ON b.hash = i.transaction_hash
        WHERE b.value_eth != ISNULL(i.internal_amount_eth, -1)
           OR b.fee_eth != ISNULL(i.internal_fee_eth, -1)
        GROUP BY CAST(b.timestamp AS DATE)
        ORDER BY date
    """,
    
    '05_blockchain_summary_stats': """
        SELECT 
            COUNT(*) as total_transactions,
            SUM(value_eth) as total_volume_eth,
            SUM(fee_eth) as total_fees_eth,
            AVG(value_eth) as avg_tx_value_eth,
            MIN(timestamp) as earliest_tx,
            MAX(timestamp) as latest_tx
        FROM eth_transactions
    """,
    
    '06_internal_records_summary': """
        SELECT 
            status,
            COUNT(*) as count,
            SUM(internal_amount_eth) as total_amount_eth,
            SUM(internal_fee_eth) as total_fees_eth
        FROM internal_records
        GROUP BY status
    """
}

# Export each query to CSV
print("Starting export...")
print("-" * 50)

for name, query in queries.items():
    try:
        print(f"Exporting {name}...", end=" ")
        df = pd.read_sql(query, conn)
        filename = f"{output_folder}/{name}.csv"
        df.to_csv(filename, index=False)
        print(f"✅ {len(df)} rows exported to {filename}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Create metadata file
metadata = {
    "project": "Crypto Financial Reconciliation",
    "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "database": "CryptoAnalytics",
    "total_queries": len(queries),
    "files_exported": list(queries.keys())
}

import json
with open(f"{output_folder}/metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("-" * 50)
print(f"✅ All exports complete! Check the '{output_folder}' folder")
print(f"📁 Location: {os.path.abspath(output_folder)}")

conn.close()