import os
import random
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)

# CONFIGURAÇÃO - Use variáveis de ambiente para segurança
# No Render, adicione STRIPE_SECRET_KEY nas Environment Variables
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# --- FUNÇÕES DE SUPORTE ---

def generate_real_card(bin_val):
    """
    Simula a geração de dados de cartão. 
    Em um cenário real, isso viria de um algoritmo de geração.
    """
    return {
        "cc": f"{bin_val}{random.randint(10000000, 99999999)}", # Exemplo simplificado
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
        # Valor de teste: 99 centavos (0.99)
        amount_in_cents = 99 

        # Criando uma intenção de pagamento para validar o cartão
        # Nota: Para transação real, o payment_method deve vir do frontend
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="usd",
            payment_method=card_data.get('payment_method_id'), # ID do Stripe Elements
            confirm=True,
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            description="Verificação de validade"
        )

        return {
            "is_valid": True,
            "balance": amount_in_cents / 100, # Retorna o valor testado
            "error": None,
            "transaction_id": intent.id
        }

    except stripe.error.CardError as e:
        # Aqui captura: Saldo insuficiente, CVV errado, cartão recusado, etc.
        return {
            "is_valid": False, 
            "balance": 0.0, 
            "error": e.user_message  # Mensagem real do banco/Stripe
        }
    except stripe.error.StripeError as e:
        # Erros de API do Stripe (Chave inválida, rede, etc)
        return {"is_valid": False, "balance": 0.0, "error": "Erro na API Stripe"}
    except Exception as e:
        # Erros genéricos de código
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

    bin_val = str(data.get('bin'))
    amount = int(data.get('amount', 1))
    
    # Limite de segurança para não estourar o processamento
    if amount > 50: amount = 50 

    valid_cards = []
    invalid_cards = []

    for _ in range(amount):
        # 1. Gerar dados (Simulação)
        card_info = generate_real_card(bin_val)
        
        # 2. Validar via Stripe (Transação Real de $0.99)
        # Nota: Para funcionar, o objeto card_info precisaria ter o payment_method_id
        check_res = validate_with_stripe(card_info)
        
        # 3. Montar objeto de resposta para o Frontend
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
    # O Render define a porta automaticamente via variável de ambiente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
