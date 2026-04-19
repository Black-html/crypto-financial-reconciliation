#  Crypto Financial Reconciliation Pipeline

🔗 **Live Interactive Dashboard:** [View on Dune Analytics](https://dune.com/dybg/crypto-financial-reconciliation)

##  Project Overview
Automated reconciliation system comparing **real blockchain data** (Etherscan API) against **simulated internal records** to identify financial discrepancies.

**Key Finding:** Identified **267 discrepancies** totaling **~823 ETH ($1.6M)** in financial impact.

##  Results Summary
| Discrepancy Type | Count | Impact (ETH) | Business Risk |
|-----------------|-------|--------------|---------------|
| Missing Transactions | 198 | 68.96 ETH | Revenue leakage |
| Amount Mismatches | 37 | 151.56 ETH | Accounting errors |
| Extra/Orphan Records | 2 | 602.50 ETH | Potential fraud |
| Fee Mismatches | 30 | ~0 ETH | Minor issue |
| **TOTAL** | **267** | **823 ETH** | **$1.6M** |

## Tech Stack
- **Data Ingestion:** Python + Etherscan API V2
- **Database:** Microsoft SQL Server
- **Analytics:** T-SQL (stored procedures, complex joins)
- **Automation:** Python export script

##  Repository Structure
├── outputs/ # All CSV results

├── pull_eth_data.py # ETL pipeline

├── export_all_results.py # Automated exports

├── reconciliation_queries.sql # All T-SQL queries

└── README.md


##  How to Reproduce
1. Run `pull_eth_data.py` to ingest blockchain data
2. Execute SQL scripts to create the `internal_records` table
3. Run reconciliation queries
4. Run `export_all_results.py` to generate CSVs

##  Skills Demonstrated
-  Financial Reconciliation (blockchain vs internal)
-  ETL Pipeline Development
-  Advanced SQL (FULL OUTER JOIN, CASE, stored procedures)
-  Blockchain Analytics (Ethereum, gas fees)
- Automation & Reporting

##  For Recruiters
This project simulates exactly what The Open Platform (Tonkeeper) requires:
- "Automate financial reconciliations between blockchain vs internal records."
- "Build ETL processes for financial reporting."
- "Present findings to CFO."

##  Project Details
- **Date:** April 2026
- **Data:** 2,387 Ethereum transactions (2015-2026)
- **Discrepancies Found:** 267 totaling 823 ETH

---
Created by [Akpan Daniel]
