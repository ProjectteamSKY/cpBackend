from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from typing import Optional
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173","http://citizenprints-erp.s3-website-ap-southeast-2.amazonaws.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "CPMagesh@2025"),
    "database": os.getenv("DB_NAME", "cp_test_db"),
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.get("/api/customers/search")
def search_customers(q: str = Query(default="", min_length=0)):
    """
    Search customers by name (partial match).
    Returns: list of { customer_code, customer_name, mobile_no }
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    like_q = f"%{q}%"
    cursor.execute(
        """
        SELECT customer_code, customer_name, mobile_no
        FROM customer_master
        WHERE customer_name LIKE %s
        ORDER BY customer_name
        LIMIT 20
        """,
        (like_q,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


@app.get("/api/customers/{customer_code}")
def get_customer(customer_code: str):
    """
    Get full customer details by customer_code.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT customer_code, customer_name, customer_type,
               customer_addr1, customer_addr2, customer_city,
               customer_state_code, customer_state, customer_pin_code,
               gst_no, mobile_no, customer_email_id
        FROM customer_master
        WHERE customer_code = %s
        LIMIT 1
        """,
        (customer_code,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Customer not found")
    return row


@app.get("/api/customers/{customer_code}/history")
def get_customer_history(customer_code: str):
    """
    Get job card history for a customer.
    Returns list of recent job cards.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT jm.jobcard_no, jm.jobcard_date, jm.approximate_amount,
               jm.advance_amount, jm.delivery_txt, jm.remarks_txt,
               jm.customer_type
        FROM jobcard_master jm
        WHERE jm.credit_customer_code = %s
           OR (jm.customer_mobile_no = (
                   SELECT mobile_no FROM customer_master WHERE customer_code = %s LIMIT 1
               ) AND jm.customer_type != 'Credit')
        ORDER BY jm.jobcard_date DESC, jm.jobcard_no DESC
        LIMIT 20
        """,
        (customer_code, customer_code),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    # Convert dates to string for JSON serialisation
    for r in rows:
        if r.get("jobcard_date"):
            r["jobcard_date"] = str(r["jobcard_date"])
    return rows
