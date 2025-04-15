from flask import Flask, jsonify, request
from flask_cors import CORS
from config import get_db_connection
from groq_ai import get_ai_response
from datetime import datetime

app = Flask(__name__)
CORS(app)  

@app.route('/tickets', methods=['GET'])
def get_tickets():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.*, c.name, c.email 
        FROM tickets t
        JOIN customers c ON t.customer_id = c.customer_id
    """)
    tickets = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(tickets)

@app.route('/create_ticket', methods=['POST'])
def create_ticket():

    data = request.json

    required_fields = ['name', 'email', 'subject', 'description', 'priority']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT customer_id FROM customers 
            WHERE email = %s
        """, (data['email'],))
        customer = cursor.fetchone()

        if not customer:
            insert_customer_query = """
            INSERT INTO customers (name, email) 
            VALUES (%s, %s)
            """
            cursor.execute(insert_customer_query, (data['name'], data['email']))
            customer_id = cursor.lastrowid
        else:
            customer_id = customer['customer_id']

        insert_ticket_query = """
        INSERT INTO tickets 
        (customer_id, subject, description, priority, status) 
        VALUES (%s, %s, %s, %s, %s)
        """

        status = data.get('status', 'open')
        
        cursor.execute(insert_ticket_query, (
            customer_id, 
            data['subject'], 
            data['description'], 
            data['priority'], 
            status
        ))

        ticket_id = cursor.lastrowid

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Ticket created successfully",
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "ticket_details": {
                "name": data['name'],
                "email": data['email'],
                "subject": data['subject'],
                "description": data['description'],
                "priority": data['priority'],
                "status": status
            }
        }), 201
    
    except Exception as e:

        if conn:
            conn.rollback()

        print(f"Error creating ticket: {str(e)}")
        
        return jsonify({
            "error": "Failed to create ticket",
            "details": str(e)
        }), 500
    finally:
        if conn:
            conn.close()

@app.route('/ask', methods=['POST'])
def ask_ai():
    data = request.json
    question = data.get("question")
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    response = get_ai_response(question)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)