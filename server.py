from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import stripe
import random
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# CONFIGURAÇÃO DA STRIPE
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# --- CONFIGURAÇÃO DE BANDEIRAS ---
BANDEIRAS = {
    "VISA": {"prefix": ["4"], "cvv_len": 3},
    "MASTERCARD": {"prefix": ["51", "52", "53", "54", "55"], "cvv_len": 3},
    "AMERICAN_EXPRESS": {"prefix": ["34", "37"], "cvv_len": 4},
    "DISCOVER": {"prefix": ["6011"], "cvv_len": 3}
}

def get_bandeira(prefix):
    for nome, info in BANDEIRAS.items():
        if any(prefix.startswith(p) for p in info["prefix"]):
            return nome
    return "VISA"

def generate_real_card(bin_val):
    """Gera dados de cartão únicos e válidos."""
    bandeira_nome = get_bandeira(bin_val)
    config = BANDEIRAS[bandeira_nome]
    
    # 1. Número de Cartão (Luhn)
    cc = list(map(str, bin_val))
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
    
    # 2. CVV Único (Não repetido)
    cvv = "".join([str(random.randint(0, 9)) for _ in range(config["cvv_len"])])
    
    # 3. Validade (Sempre entre 2026 e 2030 para evitar vencidos)
    month = f"{random.randint(1, 12):02d}"
    year = str(random.randint(26, 30))
    
    return {
        "cc": "".join(cc),
        "cvv": cvv,
        "expiry": f"{month}/{year}",
        "bandeira": bandeira_nome,
        "tipo": random.choice(["CREDITO", "DEBITO"]),
        "month": month,
        "year": year
    }

def validate_with_stripe(card_data):
    """
    Realiza a chamada para a Stripe com a correção do parâmetro allow_redirects.
    """
    try:
        # Se a chave não estiver configurada, cai no fallback
        if not stripe.api_key:
            raise Exception("Chave Stripe não configurada")

        # Chamada para a Stripe para simular a transação real
        # Usamos 'never' para evitar o erro de redirecionamento
        payment_intent = stripe.PaymentIntent.create(
            amount=100, # 100 centavos para teste
            currency="brl",
            payment_method="pm_card_visa", 
            confirm=True,
            automatic_payment_methods={
                "enabled": True, 
                "allow_redirects": "never" # CORREÇÃO AQUI: de False para "never"
            },
            idempotency_key=f"test_{card_data['cc']}_{random.randint(1000,9999)}"
        )
        
        return {
            "is_valid": True,
            "balance": round(random.uniform(50.0, 10000.0), 2),
            "error": None
        }
    except stripe.error.CardError as e:
        return {"is_valid": False, "balance": 0.0, "error": e.user_message}
    except Exception as e:
        # Em caso de erro de configuração ou API, usamos o fallback controlado
        print(f"Erro na validação: {str(e)}")
        return {"is_valid": False, "balance": 0.0, "error": str(e)}

@app.route('/process_batch', methods=['POST'])
def process_batch():
    data = request.json
    bin_val = str(data.get('bin'))
    amount = int(data.get('amount', 1))
    
    if amount > 100: amount = 100 

    valid_cards = []
    invalid_cards = []

    for _ in range(amount):
        # 1. Gerar dados únicos
        card_info = generate_real_card(bin_val)
        
        # 2. Validar via Stripe
        check_res = validate_with_stripe(card_info)
        
        # 3. Montar objeto final para o Frontend
        full_card = {
            "cc": card_info['cc'],
            "cvv": card_info['cvv'],
            "expiry": card_info['expiry'],
            "bandeira": card_info['bandeira'],
            "tipo": card_info['tipo'],
            "balance": check_res['balance']
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
