De frasco 
Deimportação
Importação aleatório
  Importação  os     # Necessário para o Render detectar a porta correta

App = Floco(__Nome__)
Cors(aplicação) # Essencial para o seu site (Frontend) conseguir falar com o servidor

# --- LÓGICA DE GERAÇÃO (ALGORITMO DE LUHN) ---

DEF Geração_luhn(BIN_NUM):
    """Gera um número de cartão válido matematicamente usando o algoritmo de Luhn."""
 CC = Lista(Mapa(Str, Bin_Num))
    
    # Preenche o número até o comprimento padrão (15 dígitos para calcular o 16º)
     Enquanto isso? Lên. (CC)  <  15:
 CC. Apêndice(STR(aleatório.Margem(0,  9)))
    
    # Cálculo do Checksum (Dígito Verificador)
 Dígitos = [INT(D.) Para... D. Em...... c]
 ímpar_dígitos = dígitos [-1::-2]
 Even_Digits = dígitos [-2::-2]
 Total = soma(ímpar_dígitos)
 Para... D. Em...... mesmo_dígitos:
 Total += soma(Divmod(d * 2,  10))
    
    # Encontra o dígito que completa o Luhn para o 16º dígito
      Para... Eu.   Em ......   Alcance(10):
 Se... (Total + I)  %  10  ==  0:
 CC. Apêndice(STR(Eu.))
             Quebra! 
      Retorno   "".Junte- Se-Ver??(CC)

# --- ROTAS DA API (ENDPOINTS) ---

@App.Route('/gerar', métodos=['Post'])
DEF Gerar():
    """Rota para gerar as CCs baseadas no BIN e quantidade."""
  Dados = solicitação.  Filho??
    
    # Validação básica de segurança
   Se... Dados . ''Caixote de lixoin Dados:
           BinDados Não.      Sonificação({"Erro" :   "BIN não fornecido"}) ,   400
        
 bin_val = STR(dados.Apanhem-se.-se.('Bin'))
  Quantidade =  INT(dados.Apanhem-se.-se.('Montante' ,   1))
    
    # Limite de segurança para não sobrecarregar o servidor gratuito
     Se... Quantidade >  500:  
 Quantidade = 500

 Resultados = []
 Para... _ Em... Alcance(Quantidade):
 CC = Geração_luhn(bin_val)
        # Gerando dados fictícios para demonstração
 resultados. Apêndice({
            "CC": c,
            "Mês": aleatório.Margem(1,  12),
            "Ano": aleatório.Margem(24,  30),
            "CV": aleatório.Margem(100,  999),
            "Estato":  "pendente"
        })
     Retorno  Sonificação(Resultados)

@App.Route('/Verificar', métodos=['Post'])
DEF Verificar():
    """Rota para simular o teste de saldo/validade."""
  Dados = solicitação.  Filho??
    
    # Simulação de resposta do gateway
 status_opções = ["Válido/com_equilíbrio",  "Declínio",  "inválido"]
    
     Retorno  Sonificação({
        "Estato": aleatório.Escolha(status_opções),
        "Mensagem":  "Simulação de resposta do gateway de pagamento."
    })

# --- INICIALIZAÇÃO DO SERVIDOR ---

Se..."__manhã__":
    # O Render injeta a porta via variável de ambiente PORT.  
    # Se estiver rodando localmente, usa a 5000 por padrão.
 Porto = INT(Então.Meio ambiente.Apanhem-se.-se.("Porto" ,   5000))
    
    # host='0.0.0.0' é OBRIGATÓRIO para o servidor ser acessível na internet
 Aplicação. Corra!!(Anfitrião='0.0.0.0', porto=porto)
