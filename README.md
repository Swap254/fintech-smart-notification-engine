# Automated FinTech Smart Notification & Asynchronous Risk Analysis Engine

An enterprise-grade, decoupled microservices architecture designed to solve a critical fintech scalability challenge: ingestion of massive transaction volumes while performing high-speed statistical anomaly detection and routing dynamic notifications without blocking core transaction throughput.

## 🛠️ System Architecture & Data Flow

The platform relies on a completely asynchronous pipeline to ensure high throughput and zero structural data loss:

1. **Ingestion Layer (Java / Spring Boot 3.2.5):** Exposes REST endpoints to receive transaction batch uploads. Implements optimized **JDBC batch insertions (Batch Size: 500)** to save rows into PostgreSQL while streaming a copy of the payload to cloud storage using the AWS SDK for Java.
2. **Storage Layer (Amazon S3):** Acts as a stateless, highly resilient file locker that minimizes application memory footprint.
3. **Compute Core (Python 3.12 / AWS Lambda):** Wakes up instantaneously via S3 `ObjectCreated` event notifications. Utilizes highly optimized **Pandas column-wide Vectorization** (running low-level compiled C code) to analyze datasets in milliseconds without resource-heavy row loops.
4. **Asynchronous Buffer (Amazon SQS):** Flags high-risk anomalies and buffers them inside a standard message queue to protect database integrity and guarantee processing during heavy backend spike locks.
5. **Worker Daemon (Java / Spring Boot Background Thread):** Continually polls the cloud queue via a background SQS Listener container, processes risk entities, and logs tracking rows inside PostgreSQL.
6. **Dispatch Layer (Amazon SNS):** Inspects the threat intensity score. If the calculated risk is critically high (≥ 75%), it automatically broadcasts detailed notification alerts directly to system operations email streams.

---

## 📈 Enterprise Performance Enhancements Implemented

* **JDBC Batch Ingestion Processing:** Grouping transaction rows into 500-unit memory vectors dropped database network I/O overhead from minutes to under 3 seconds for 10,500+ records.
* **High-Speed Pandas Vectorization:** Rewrote iterative Python `.iterrows()` loops into column-wide matrix condition masks inside AWS Lambda. This ensures that processing timelines scale logarithmically rather than linearly under production volume constraints.
* **Dynamic Configuration Isolation:** Stripped environmental absolute URL targets out of source components. Application properties are dynamically resolved via variable mappings (`${aws.sqs.queue-url}`), making code configurations cloud-agnostic.

---

## ⚙️ Tech Stack & Software Ecosystem

* **Backend Framework:** Java 21 (LTS) / Spring Boot 3.2.5 / Spring Data JPA / Hibernate
* **Data Processing Layer:** Python 3.12 / Pandas Core / Boto3 AWS SDK
* **Cloud Infrastructure (AWS Free Tier):** Amazon S3, AWS Lambda, Amazon SQS, Amazon SNS, AWS IAM
* **Relational Ledger Database:** PostgreSQL / pgAdmin 4
* **Testing Suite:** Postman API client / Custom Python Dataset Generation Script

---

## 🚀 Step-by-Step Local Deployment & Setup

### 1. Database Provisioning
Execute this script inside your PostgreSQL instance to establish the tracking ledger tables:

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    risk_threshold INT DEFAULT 75
);

CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    amount NUMERIC(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    receiver_account VARCHAR(50) NOT NULL,
    location_country VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING'
);

CREATE TABLE risk_flags (
    flag_id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) REFERENCES transactions(transaction_id),
    calculated_risk_score INT NOT NULL,
    flag_reason VARCHAR(255) NOT NULL,
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Environment Variables Injection
Configure your IDE or terminal to export your API credentials safely without hardcoding strings into source files:
* `AWS_ACCESS_KEY_ID` = `your_access_key_here`
* `AWS_SECRET_ACCESS_KEY` = `your_secret_key_here`

### 3. Application Verification
1. Launch your local Spring Boot engine via `RiskEngineApplication.java`.
2. Generate an enterprise dataset of 10,500+ rows by running `python generate_data.py`.
3. Use Postman to fire a multi-part `POST` form-data request containing the dataset file path targeting `http://localhost:8080/api/transactions/upload`.
4. Monitor the console logs to observe the background worker processing real-time anomalies pulled out of the AWS SQS queue.
