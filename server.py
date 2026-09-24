from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app) # Permite que o seu HTML converse com o servidor

def generate_luhn(bin_num):
    # Lógica de geração baseada no algoritmo de Luhn
    cc = list(map(str, bin_num))
    while len(cc) < 15:
        cc.append(str(random.randint(0, 9)))
    
    # Cálculo do Checksum (Dígito Verificador)
    digits = [int(d) for d in cc]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    
    # Encontrar o dígito que completa o Luhn
    for i in range(10):
        if (total + i) % 10 == 0:
            cc.append(str(i))
            break
    return "".join(cc)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    bin_val = data.get('bin')
    amount = int(data.get('amount', 1))
    
    results = []
    for _ in range(amount):
        cc = generate_luhn(bin_val)
        # Gerando dados fictícios para o exemplo
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
    # Simulação de teste de saldo real
    data = request.json
    # Aqui você faria a requisição real para uma API de Gateway
    # Ex: response = requests.post(GATEWAY_URL, data=data)
    
    status_options = ["VALID/WITH_BALANCE", "DECLINED", "INVALID"]
    return jsonify({"status": random.choice(status_options)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)