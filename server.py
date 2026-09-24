from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import stripe
import random

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

def generate_luhn(bin_num):
    cc = list(map(str, bin_num))
    while len(cc) < 15:
        cc.append(str(random.randint(0, 9)))
    digits = [int(d) for d in cc]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    for i in range(10):
        if (total + i) % 10 == 0:
            cc.append(str(i))
            break
    return "".join(cc)

def check_card_real(cc_number):
    # Simulação da lógica Stripe
    if not stripe.api_key:
        return {"is_valid": False, "error": "API Key missing"}

    # Simulando resposta de gateway
    is_valid = random.choice([True, False]) 
    balance = round(random.uniform(10.0, 4999.0), 2) if is_valid else 0.0
    
    return {
        "is_valid": is_valid,
        "balance": balance,
        "cvv": random.randint(100, 999),
        "expiry": f"{random.randint(1,12):02d}/{random.randint(25,30)}"
    }

@app.route('/process_batch', methods=['POST'])
def process_batch():
    data = request.json
    bin_val = str(data.get('bin'))
    amount = int(data.get('amount', 1))
    
    if amount > 100: amount = 100 

    valid_cards = []
    invalid_cards = []

    for _ in range(amount):
        cc_num = generate_luhn(bin_val)
        check_res = check_card_real(cc_num)
        
        card_data = {
            "cc": cc_num,
            "cvv": check_res['cvv'],
            "expiry": check_res['expiry'],
            "balance": check_res['balance']
        }

        if check_res['is_valid']:
            valid_cards.append(card_data)
        else:
            invalid_cards.append(card_data)

    return jsonify({
        "valid": valid_cards,
        "invalid": invalid_cards,
        "summary": {
            "total": amount,
            "valid_count": len(valid_cards),
            "invalid_count": len(invalid_cards)
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
