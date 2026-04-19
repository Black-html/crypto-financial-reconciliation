import requests
import pandas as pd
from sqlalchemy import create_engine

# Use the test placeholder (or your real key)
API_KEY = "YourApiKeyToken"

# Active wallet address
WALLET = "0xab5801a7d398351b8be11c439e05c5b3259aec9b"

# UPDATED V2 URL
url = f"https://api.etherscan.io/v2/api?chainid=1&module=account&action=txlist&address={WALLET}&startblock=0&endblock=99999999&sort=asc&apikey={API_KEY}"

print("Pulling data from Etherscan V2...")
response = requests.get(url)
data = response.json()

if data['status'] == '1':
    df = pd.DataFrame(data['result'])
    print(f"Pulled {len(df)} transactions")
    
    # Clean and calculate financial metrics
    df['value_eth'] = df['value'].astype(float) / 1e18
    df['timestamp'] = pd.to_datetime(df['timeStamp'].astype(int), unit='s')
    df['gas_price_gwei'] = df['gasPrice'].astype(float) / 1e9
    df['fee_eth'] = df['gasUsed'].astype(float) * df['gasPrice'].astype(float) / 1e18
    
    # Select columns for finance
    df_clean = df[['hash', 'from', 'to', 'value_eth', 'fee_eth', 'timestamp']].copy()
    df_clean['transaction_type'] = 'transfer'
    df_clean['status'] = 'success'
    
    print(df_clean.head())
    
    # Connect to SQL Server
    conn_str = "mssql+pyodbc://DYBG\\SQLEXPRESS/CryptoAnalytics?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    engine = create_engine(conn_str)
    
    # Send to database
    df_clean.to_sql('eth_transactions', engine, if_exists='replace', index=False)
    print("Data loaded to SQL Server!")
    
else:
    print(f"Error: {data['message']}")