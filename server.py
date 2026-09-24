import os
import random
import stripe
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# CONFIGURAÇÃO
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# --- FUNÇÕES DE SUPORTE (COLE AQUI A CORREÇÃO) ---

def luhn_checksum(number):
    """Calcula o dígito verificador para passar no algoritmo de Luhn."""
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
    """
    Gera um número de cartão que passa no teste de Luhn (Matematicamente correto).
    """
    # 1. Gera uma base de 15 dígitos (BIN + aleatórios)
    base_number = f"{bin_val}{random.randint(10000000, 99999999)}"[:15]
    
    # 2. Calcula o 16º dígito (o verificador)
    check_digit = luhn_checksum(base_number)
    
    # 3. Monta o número completo
    full_card_number = f"{base_number}{check_digit}"
    
    return {
        "cc": full_card_number,
        "cvv": str(random.randint(100, 999)),
        "expiry": "12/26",
        "bandeira": "Visa",
        "tipo": "Credit"
    }

def validate_with_stripe(card_data):
    """
    Realiza a transação de teste (0.99) para validar o cartão.
    """
    try:
        payment_method_id = card_data.get('payment_method_id')
        
        if not payment_method_id:
            return {
                "is_valid": False, 
                "balance": 0.0, 
                "error": "Erro: Falta o Payment Method ID"
            }

        amount_in_cents = 99 

        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="usd",
            payment_method=payment_method_id,
            confirm=True,
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            description="Verificação de validade"
        )

        return {
            "is_valid": True,
            "balance": amount_in_cents / 100,
            "error": None,
            "transaction_id": intent.id
        }

    except stripe.error.CardError as e:
        return {
            "is_valid": False, 
            "balance": 0.0, 
            "error": e.user_message  
        }
    except stripe.error.StripeError as e:
        return {"is_valid": False, "balance": 0.0, "error": "Erro na API Stripe"}
    except Exception as e:
        print(f"Erro interno: {str(e)}")
        return {"is_valid": False, "balance": 0.0, "error": "Erro interno no servidor"}

# --- RESTO DO SEU CÓDIGO (ROTAS E INICIALIZAÇÃO) CONTINUA IGUAL ---

@app.route('/process_batch', methods=['POST'])
def process_batch():
    data = request.json
    if not data:
        return jsonify({"error": "Dados não fornecidos"}), 400

    bin_val = str(data.get('bin', '53811123'))
    amount = int(data.get('amount', 1))
    payment_method_id = data.get('payment_method_id')

    if amount > 50: amount = 50 
    
    valid_cards = []
    invalid_cards = []

    for _ in range(amount):
        card_info = generate_real_card(bin_val)
        card_info['payment_method_id'] = payment_method_id
        
        check_res = validate_with_stripe(card_info)
        
        full_card = {
            "cc": card_info['cc'],
            "cvv": card_info['cvv'],
            "expiry": card_info['expiry'],
            "bandeira": card_info['bandeira'],
            "tipo": card_info['tipo'],
            "balance": check_res['balance'],
            "status_msg": check_res['error'] if not check_res['is_valid'] else "Aprovado"
        }

        if check_res['is_valid']:
            valid_cards.append(full_card)
        else:
            invalid_cards.append(full_card)

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
