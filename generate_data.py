import pandas as pd
import random
from datetime import datetime, timedelta

def generate_fintech_dataset(filename="large_transactions.csv", num_rows=10500):
    print(f"🚀 Generating {num_rows} diverse transaction rows...")

    countries = ['IN', 'IN', 'IN', 'IN', 'US', 'UK', 'AE', 'SG', 'CA'] # Heavy bias to domestic 'IN'
    currencies = ['INR', 'INR', 'INR', 'INR', 'USD', 'GBP', 'AED', 'SGD', 'CAD']
    statuses = ['PENDING']

    data = []
    start_time = datetime(2026, 11, 5, 10, 0, 0)

    for i in range(1, num_rows + 1):
        txn_id = f"TXN-{100000 + i}"
        user_id = random.randint(1001, 1500) # 500 distinct mock users

        # Scenario Generation Strategy
        roll = random.random()
        if roll < 0.85:
            # 1. Normal clean transactions (85% of data)
            amount = round(random.uniform(50.00, 45000.00), 2)
            country = 'IN'
            currency = 'INR'
        elif roll < 0.93:
            # 2. Anomaly Rule A: High-value transfers (> 2,00,000 INR)
            amount = round(random.uniform(205000.00, 1500000.00), 2)
            country = 'IN'
            currency = 'INR'
        else:
            # 3. Anomaly Rule B: Cross-border foreign transfers
            amount = round(random.uniform(500.00, 85000.00), 2)
            country = random.choice(['US', 'UK', 'AE', 'SG'])
            currency = currencies[countries.index(country)]

        receiver_acc = f"ACC-{random.randint(550000, 999999)}"
        timestamp = (start_time + timedelta(seconds=i * random.randint(1, 5))).strftime('%Y-%m-%dT%H:%M:%S')
        status = random.choice(statuses)

        data.append([txn_id, user_id, amount, currency, receiver_acc, country, timestamp, status])

    columns = ['transaction_id', 'user_id', 'amount', 'currency', 'receiver_account', 'location_country', 'timestamp', 'status']
    df = pd.DataFrame(data, columns=columns)

    df.to_csv(filename, index=False)
    print(f"✅ Dataset saved successfully as: '{filename}'!")

if __name__ == "__main__":
    generate_fintech_dataset()
