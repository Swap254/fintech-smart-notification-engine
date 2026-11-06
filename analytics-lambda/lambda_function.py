import os
import io
import json
import urllib.parse
import boto3
import pandas as pd

# Initialize AWS SDK Clients outside the handler for container reuse execution efficiency
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')

QUEUE_URL = os.environ.get('SQS_QUEUE_URL')
HIGH_AMOUNT_LIMIT = 200000.00

def lambda_handler(event, context):
    """
    AWS Lambda trigger handler listening to Amazon S3 ObjectCreated events.
    Streams CSV contents, executes rapid VECTORIZED Pandas risk evaluations, and alerts SQS.
    """
    # 1. Parse incoming S3 Event notification structures
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        print(f"🕵️‍♂️ Python Risk Engine triggered for bucket: {bucket_name}, key: {file_key}")
    except (KeyError, IndexException) as e:
        print(f"❌ Malformed S3 event execution block: {str(e)}")
        return {'statusCode': 400, 'body': 'Invalid event record layout.'}

    # 2. Stream payload directly from S3 to memory via Boto3
    try:
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        csv_bytes = s3_response['Body'].read()
        df = pd.read_csv(io.BytesIO(csv_bytes))
    except Exception as e:
        print(f"❌ Error downloading/parsing file from S3: {str(e)}")
        return {'statusCode': 500, 'body': f"S3 Stream failure: {str(e)}"}

    # ------------------------------------------------------------------------
    # 3. HIGH-SPEED VECTORIZED EVALUATION ENGINE (No Row Loops!)
    # ------------------------------------------------------------------------
    # Calculate column-wide score metrics instantly using boolean arrays
    df['risk_score'] = 0
    df['reasons'] = ""

    # Rule A condition mask: High-value transfers
    high_value_mask = df['amount'] > HIGH_AMOUNT_LIMIT
    df.loc[high_value_mask, 'risk_score'] += 50
    df.loc[high_value_mask, 'reasons'] += "High-value transfer exceeding limit (Amount: " + df['amount'].astype(str) + ")"

    # Rule B condition mask: Cross-border foreign transfers
    cross_border_mask = df['location_country'].str.strip().str.upper() != 'IN'

    # Handle separating multiple reasons cleanly where both rules hit
    delimiter_mask = high_value_mask & cross_border_mask
    df.loc[delimiter_mask, 'reasons'] += " | "

    df.loc[cross_border_mask, 'risk_score'] += 35
    df.loc[cross_border_mask, 'reasons'] += "Cross-border transaction source detected (" + df['location_country'].astype(str) + ")"

    # Cap max risk metrics limit threshold boundary to 100
    df['risk_score'] = df['risk_score'].clip(upper=100)

    # Filter out records that met or exceeded the alerting threshold limit (>= 50)
    flagged_df = df[df['risk_score'] >= 50]
    # ------------------------------------------------------------------------

    print(f"📊 Vectorized Evaluation Complete. Identified {len(flagged_df)} high-risk anomalies.")

    # 4. Asynchronously route individual alerts to SQS Buffers
    success_count = 0
    for _, row in flagged_df.iterrows():
        try:
            alert_payload = {
                "transaction_id": str(row['transaction_id']),
                "calculated_risk_score": int(row['risk_score']),
                "flag_reason": str(row['reasons'])
            }
            sqs_client.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=json.dumps(alert_payload)
            )
            success_count += 1
        except Exception as sqs_error:
            print(f"⚠️ SQS Enqueue drop failure for TxID {row['transaction_id']}: {str(sqs_error)}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Vectorized risk execution pipeline processed successfully.',
            'total_analyzed': len(df),
            'total_flagged': len(flagged_df),
            'successfully_buffered': success_count
        })
    }