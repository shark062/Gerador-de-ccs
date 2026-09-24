from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import os

app = Flask(__name__)
# Permite que o seu frontend acesse o backend sem erros de segurança (CORS)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- LÓGICA DE GERAÇÃO (ALGORITMO DE LUHN) ---

def generate_luhn(bin_num):
    """Gera um número de cartão válido matematicamente usando o algoritmo de Luhn."""
    cc = list(map(str, bin_num))
    
    # Preenche o número até o comprimento padrão (15 dígitos)
    while len(cc) < 15:
        cc.append(str(random.randint(0, 9)))
    
    # Cálculo do Checksum (Dígito Verificador)
    digits = [int(d) for d in cc]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    
    # Encontra o dígito que completa o Luhn para o 16º dígito
    for i in range(10):
        if (total + i) % 10 == 0:
            cc.append(str(i))
            break
    return "".join(cc)

# --- ROTAS DA API (ENDPOINTS) ---

@app.route('/generate', methods=['POST'])
def generate():
    """Rota para gerar as CCs baseadas no BIN e quantidade."""
    data = request.json
    
    if not data or 'bin' not in data:
        return jsonify({"error": "BIN não fornecido"}), 400
        
    bin_val = str(data.get('bin'))
    amount = int(data.get('amount', 1))
    
    # Limite de segurança para evitar sobrecarga no servidor
    if amount > 500: 
        amount = 500

    results = []
    for _ in range(amount):
        cc = generate_luhn(bin_val)
        results.append({
            "cc": cc,
            "month": random.randint(1, 12),
            "year": random.randint(24, 30),
            "cvv": random.randint(100, 999),
            "status": "PENDING"
        })
    return jsonify(results)

@app.route('/check', methods=['POST'])
def check():
    """Rota para simular o teste de saldo/validade."""
    data = request.json
    
    if not data or 'cc' not in data:
        return jsonify({"error": "Número do cartão não fornecido"}), 400

    # Lista de status possíveis para a simulação
    status_options = ["VALID/WITH_BALANCE", "DECLINED", "INVALID"]
    resultado_status = random.choice(status_options)
    
    # Se for válido, gera um saldo aleatório, se não, saldo é zero
    saldo = 0.0
    if resultado_status == "VALID/WITH_BALANCE":
        saldo = round(random.uniform(10.0, 4999.99), 2)

    return jsonify({
        "status": resultado_status,
        "balance": saldo,
        "message": "Simulação de resposta do gateway de pagamento realizada com sucesso."
    })

# --- INICIALIZAÇÃO DO SERVIDOR ---

if __name__ == '__main__':
    # O Render injeta a porta via variável de ambiente PORT.
    port = int(os.environ.get("PORT", 5000))
    
    # host='0.0.0.0' é OBRIGATÓRIO para o servidor ser acessível na internet
    app.run(host='0.0.0.0', port=port)
