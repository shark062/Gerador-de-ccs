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
