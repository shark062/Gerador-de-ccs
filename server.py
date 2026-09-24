import os
import random
import stripe
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# CONFIGURAÇÃO - Coloque sua chave real aqui no Render
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# --- FUNÇÕES MATEMÁTICAS ---

def luhn_checksum(number):
    """Calcula o dígito verificador para o número ser matematicamente válido."""
    digits = [int(d) for d in str(number)]
    odd_digits = digits[-1]
    even_digits = digits[:-1]
    even_digits.reverse()
    for i in range(len(even_digits)):
        even_digits[i] *= 2
        if even_digits[i] > 9:
            even_digits[i] -= 9
    total = sum(even_digits) + odd_digits
    return (10 - (total % 10)) % 10

def generate_real_card(bin_val):
    """Gera um número que passa no teste de Luhn e tem validade aleatória."""
    # 1. Gera a base (15 dígitos)
    base_number = f"{bin_val}{random.randint(10000000, 99999999)}"[:15]
    # 2. Calcula o 16º dígito real
    check_digit = luhn_checksum(base_number)
    full_number = f"{base_number}{check_digit}"
    
    # 3. Gera validade aleatória (para não ficar tudo 12/26)
    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(25, 29)) # Ano entre 2025 e 2029
    
    return {
        "cc": full_number,
        "cvv": str(random.randint(100, 999)),
        "expiry": f"{month}/{year}",
        "bandeira": "Visa",
        "tipo": "Credit"
    }

# --- VALIDAÇÃO REAL ---

def validate_with_stripe(card_data):
    """Tenta realizar uma transação de $0.99 para checar o crédito."""
    try:
        # O ID do método de pagamento deve vir do seu Frontend (Stripe Elements)
        payment_method_id = card_data.get('payment_method_id')
        
        if not payment_method_id:
            return {"is_valid": False, "error": "Falta o token de pagamento"}

        # Tenta cobrar o valor mínimo
        intent = stripe.PaymentIntent.create(
            amount=99, # 99 centavos
            currency="usd",
            payment_method=payment_method_id,
            confirm=True,
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            description="Check Credit"
        )

        return {
            "is_valid": True,
            "balance": 0.99,
            "error": None,
            "transaction_id": intent.id
        }

    except stripe.error.CardError as e:
        # Se o banco recusar (falta de saldo, etc)
        return {
            "is_valid": False, 
            "balance": 0.0, 
            "error": e.user_message  # "Insufficient funds", etc.
        }
    except Exception as e:
        return {"is_valid": False, "balance": 0.0, "error": str(e)}

# --- ROTAS ---

@app.route('/process_batch', methods=['POST'])
def process_batch():
    data = request.json
    if not data:
        return jsonify({"error": "Sem dados"}), 400

    bin_val = str(data.get('bin'))
    amount = int(data.get('amount', 1))
    payment_method_id = data.get('payment_method_id')

    # Limite para não travar o servidor
    if amount > 50: amount = 50 

    results = []

    for _ in range(amount):
        # 1. Gera o número que "parece" real
        card_info = generate_real_card(bin_val)
        card_info['payment_method_id'] = payment_method_id
        
        # 2. Valida o crédito real no Stripe
        check_res = validate_with_stripe(card_info)
        
        results.append({
            "cc": card_info['cc'],
            "cvv": card_info['cvv'],
            "expiry": card_info['expiry'],
            "bandeira": card_info['bandeira'],
            "tipo": card_info['tipo'],
            "balance": check_res['balance'],
            "status_msg": check_res['error'] if not check_res['is_valid'] else "Aprovado"
        })

    return jsonify({"results": results})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
