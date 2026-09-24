// 1. CONFIGURAÇÃO DE URL (O SEGREDO PARA O APP FUNCIONAR ONLINE)
// Se o site estiver rodando no seu celular/computador local, usa localhost.
// Se estiver no site do Render, usa a sua URL oficial.
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://127.0.0.1:5000' 
    : 'https://gerador-de-ccs.onrender.com'; // <--- COLOQUE A SUA URL DO RENDER AQUI

async function gerarCCs() {
    const bin = document.getElementById('binInput').value;
    const amount = document.getElementById('amountInput').value;
    const statusText = document.getElementById('status');
    const logContainer = document.getElementById('logContainer');

    // Validação básica de entrada
    if(!bin || !amount) {
        alert("⚠️ Preencha o BIN e a Quantidade!");
        return;
    }

    // Feedback visual para o usuário
    statusText.innerText = "PROCESSANDO...";
    statusText.style.color = "#00ff41"; // Verde
    logContainer.innerHTML = "<p style='color: #888;'>[!] Iniciando requisição ao servidor...</p>";

    try {
        // Chamada para o seu servidor real no Render
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify({ 
                bin: bin, 
                amount: parseInt(amount) // Garante que o número seja enviado como inteiro
            })
        });

        if (!response.ok) {
            throw new Error(`Erro no servidor:  ${response.status}`);
        }

        const data = await response.json();
        
        // Atualiza o status na interface
        statusText.innerText = "SUCESSO!";
        statusText.style.color = "#00ff41";

        // Limpa o log anterior e renderiza as novas CCs
        logContainer.innerHTML = ""; 
        
        if (data.length === 0) {
 logContainer.innerHTML = "<p style='color: #ff003c;'>[!] Nenhuma CC gerada.p>"; logContainer.innerHTML = "<p style='color: #ff003c;'>[!] Nenhuma CC gerada.</p>";
            return;
        }

         // Renderiza a lista de CCs com um efeito de delay para parecer "hacker" // Renderiza a lista de CCs com um efeito de delay para parecer "hacker"
        data.forEach((item, index) => {
            setTimeout(() => {
                const div = document.createElement('div');
                div.className = 'cc-item';
                div.innerHTML = `
                    <span style="color: #00ff41;">[+]</span> 
                    <span>${item.cc}</span> | 
                    <span>${item.month}/${item.year}</span> | 
                    <span style="color: #ff003c;">CVV: ${item.cvv}</span>
                `;
                logContainer.appendChild(div);
                
                 // Auto-scroll para baixo no log // Auto-scroll para baixo no log
                logContainer.scrollTop = logContainer.scrollHeight;
             }, index * 100); // Delay de 100ms entre cada CC para efeito visual }, index * 100); // Delay de 100ms entre cada CC para efeito visual
        });

    } catch (error) {
         console.error("Erro detalhado:", error); console.error("Erro detalhado:", error);
        statusText.innerText = "ERRO DE CONEXÃO!";
        statusText.style.color = "#ff003c";
         logContainer.innerHTML = `<p style="color: #ff003c;">[!] Erro ao conectar com o servidor.<br>Verifique se o backend está online.</p>`; logContainer.innerHTML = `<p style="color: #ff003c;">[!] Erro ao conectar com o servidor.<br>Verifique se o backend está online.</p>`;
    }
}

// Event Listener para o botão
document.getElementById('generateBtn').addEventListener('click', gerarCCs);
