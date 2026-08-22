import os
import hmac
import hashlib
import json
import logging
from datetime import datetime
import httpx
from fastapi import FastAPI, Header, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPBasic, HTTPBasicCredentials
from fastapi.responses import Response
from src.config import settings

logger = logging.getLogger("mocks")

app = FastAPI(title="Legacy Customer Systems Mocks")

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
basic_scheme = HTTPBasic(auto_error=False)

# Mock databases in-memory (to allow dynamic changes/resets if needed)
MOCK_REST_DATA = [
    {"id": "r_101", "name": "Rajesh Kumar", "email": "rajesh@crm-example.com", "balance": 45000.50, "active": True},
    {"id": "r_102", "name": "Priya Sharma", "email": "priya@crm-example.com", "balance": 12000.00, "active": False},
    {"id": "r_103", "name": "Sanjay Mehta", "email": "sanjay@crm-example.com", "balance": 89000.00, "active": True}
]

MOCK_XML_DATA = """<?xml version="1.0" encoding="UTF-8"?>
<accounts>
    <account>
        <id>x_201</id>
        <name>Amit Patel</name>
        <email>amit@billing-legacy.com</email>
        <balance>75000.00</balance>
        <status>active</status>
    </account>
    <account>
        <id>x_202</id>
        <name>Anjali Gupta</name>
        <email>anjali@billing-legacy.com</email>
        <balance>0.00</balance>
        <status>suspended</status>
    </account>
    <account>
        <id>x_203</id>
        <name>Rohan Das</name>
        <email>rohan@billing-legacy.com</email>
        <balance>54300.25</balance>
        <status>active</status>
    </account>
</accounts>
"""

# 1. REST JSON Source Endpoint
@app.get("/rest/customers")
async def get_rest_customers(authorization: str = Header(None)):
    """Simulates a legacy CRM REST endpoint. Requires API Key bearer token."""
    expected_token = f"Bearer {settings.REST_SOURCE_API_KEY}"
    if not authorization or authorization != expected_token:
        logger.warning("Unauthenticated attempt to access REST mock.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing REST API Key."
        )
    return MOCK_REST_DATA

# 2. SOAP/XML Source Endpoint
@app.get("/xml/accounts")
async def get_xml_accounts(credentials: HTTPBasicCredentials = Depends(basic_scheme)):
    """Simulates a billing system SOAP/XML endpoint. Requires Basic Auth."""
    if not credentials or credentials.username != settings.XML_SOURCE_USERNAME or credentials.password != settings.XML_SOURCE_PASSWORD:
        logger.warning("Unauthenticated attempt to access XML mock.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password for Basic Auth."
        )
    return Response(content=MOCK_XML_DATA, media_type="application/xml")

# 3. CSV Drop Simulator
@app.post("/trigger-csv-drop")
async def trigger_csv_drop():
    """Generates a CSV file in the configured directory to simulate a legacy mainframe dump."""
    os.makedirs(settings.CSV_DROP_DIR, exist_ok=True)
    filename = f"customer_drop_{int(datetime.utcnow().timestamp())}.csv"
    filepath = os.path.join(settings.CSV_DROP_DIR, filename)
    
    csv_content = """customer_id,name,email,balance,status
c_401,Vikram Singh,vikram@mainframe-legacy.com,125000.00,active
c_402,Neha Verma,neha@mainframe-legacy.com,3200.50,suspended
c_403,Karan Malhotra,karan@mainframe-legacy.com,41000.90,active
"""
    try:
        with open(filepath, "w") as f:
            f.write(csv_content)
        logger.info(f"Mock CSV file dropped successfully: {filepath}")
        return {"status": "success", "file": filepath}
    except Exception as e:
        logger.error(f"Failed to drop mock CSV file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to drop CSV: {str(e)}")

# 4. Webhook Event Publisher
@app.post("/trigger-webhook")
async def trigger_webhook():
    """Simulates an external gateway triggering a signed webhook to our integration engine."""
    webhook_url = f"http://127.0.0.1:{settings.FASTAPI_PORT}/api/webhook"
    
    payload = {
        "event": "customer.created",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "id": f"w_{int(datetime.utcnow().timestamp())}",
            "name": "Sunita Rao",
            "email": "sunita@orders-webhook.com",
            "amount": 25000.00,
            "status": "completed"
        }
    }
    
    payload_str = json.dumps(payload)
    # Calculate signature
    signature = hmac.new(
        settings.WEBHOOK_SIGNATURE_KEY.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(webhook_url, content=payload_str, headers=headers, timeout=5.0)
            logger.info(f"Mock webhook fired. Receiver responded with status: {response.status_code}")
            return {
                "status": "success",
                "receiver_response_code": response.status_code,
                "receiver_body": response.text,
                "sent_payload": payload
            }
        except Exception as e:
            logger.error(f"Failed to publish mock webhook: {e}")
            raise HTTPException(status_code=502, detail=f"Webhook receiver unreachable: {str(e)}")
