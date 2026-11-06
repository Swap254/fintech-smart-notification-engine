import os
import io
import json
import pandas as pd

def analyze_transaction_risk(csv_file_path):
    print(f"🕵️‍♂️ Python Risk Engine triggered for file: {csv_file_path}")

    # 1. Ingest data into a high-speed Pandas Dataframe
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # 2. Define our Statistical Anomaly Limits
    HIGH_AMOUNT_LIMIT = 200000.00  # Flag any transfer above ₹2 Lakhs

    flagged_alerts = []

    # 3. Analyze the transactions line-by-line using Pandas logic
    for index, row in df.iterrows():
        risk_score = 0
        reasons = []

        # Rule A: High Velocity / Large Transaction Limit Check
        if row['amount'] > HIGH_AMOUNT_LIMIT:
            risk_score += 50
            reasons.append(f"High-value transfer exceeding limit (Amount: {row['amount']})")

        # Rule B: International Footprint Exposure Check
        # If the country tag is outside the domestic operational footprint (not 'IN')
        if str(row['location_country']).strip().upper() != 'IN':
            risk_score += 35
            reasons.append(f"Cross-border transaction source detected ({row['location_country']})")

        # 4. If the total risk score crosses our threshold level, generate a structured flag
        if risk_score >= 50:
            alert_payload = {
                "transaction_id": row['transaction_id'],
                "calculated_risk_score": min(risk_score, 100),
                "flag_reason": " | ".join(reasons)
            }
            flagged_alerts.append(alert_payload)

    # 5. Output results (This layout mimics what Python will drop into the AWS SQS queue)
    print(f"\n📊 Risk Evaluation Complete. Found {len(flagged_alerts)} high-risk anomalies:")
    print(json.dumps(flagged_alerts, indent=4))

    return flagged_alerts

# This allows us to instantly test the script locally on our desktop CSV file
if __name__ == "__main__":
    desktop_file = r"C:\Users\L460\Desktop\transactions.csv"
    if os.path.exists(desktop_file):
        analyze_transaction_risk(desktop_file)
    else:
        print(f"⚠️ Mock file not found at {desktop_file}. Please check the path.")