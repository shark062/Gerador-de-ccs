import os
import random
import stripe
from flask import Flask, request, jsonify
from flask_cors import CORS  # IMPORTANTE: Para resolver o "Failed to fetch"

app = Flask(__name__)
CORS(app)  # IMPORTANTE: Permite que seu frontend chame o backend

# CONFIGURAÇÃO - No Render, adicione STRIPE_SECRET_KEY nas Environment Variables
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# --- FUNÇÕES DE SUPORTE ---

def generate_real_card(bin_val):
    """
    Simula a geração de dados de cartão.
    """
    # Gerando um número que parece real (exemplo simples)
    card_number = f"{bin_val}{random.randint(10000000, 99999999)}"
    return {
        "cc": card_number,
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
        # O ID do método de pagamento DEVE vir do frontend via Stripe Elements
        payment_method_id = card_data.get('payment_method_id')
        
        if not payment_method_id:
            return {
                "is_valid": False, 
                "balance": 0.0, 
                "error": "Erro: Falta o Payment Method ID (token do Stripe)"
            }

        # Valor de teste: 99 centavos (0.99)
        amount_in_cents = 99 

        # Criando uma intenção de pagamento para validar o cartão
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="usd",
            payment_method=payment_method_id,
            confirm=True,
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            description="Verificação de validade de cartão"
        )

        return {
            "is_valid": True,
            "balance": amount_in_cents / 100,
            "error": None,
            "transaction_id": intent.id
        }

    except stripe.error.CardError as e:
        # Captura recusa do banco (Saldo, CVV, Expirado, etc)
        return {
            "is_valid": False, 
            "balance": 0.0, 
            "error": e.user_message  
        }
    except stripe.error.StripeError as e:
        # Erros de configuração da API (Chave errada, etc)
        return {"is_valid": False, "balance": 0.0, "error": "Erro na API Stripe"}
    except Exception as e:
        print(f"Erro interno: {str(e)}")
        return {"is_valid": False, "balance": 0.0, "error": "Erro interno no servidor"}

# --- ROTAS DA API ---

@app.route('/process_batch', methods=['POST'])
def process_batch():
    """
    Rota principal para processar uma lista de verificações.
    """
    data = request.json
    if not data:
        return jsonify({"error": "Dados não fornecidos"}), 400

    # Pegando os dados enviados pelo seu frontend
    bin_val = str(data.get('bin', '411111'))
    amount = int(data.get('amount', 1))
    payment_method_id = data.get('payment_method_id') # IMPORTANTE: Receber o ID aqui

    if amount > 200: amount = 200 # Limite de segurança para testes
    
    valid_cards = []
    invalid_cards = []

    for _ in range(amount):
        # 1. Gerar dados simulados
        card_info = generate_real_card(bin_val)
        
        # Adiciona o payment_method_id para a validação
        card_info['payment_method_id'] = payment_method_id
        
        # 2. Validar via Stripe (Transação Real de $0.99)
        check_res = validate_with_stripe(card_info)
        
        # 3. Montar objeto final para o Frontend
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

# --- INICIALIZAÇÃO DO SERVIDOR ---

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
