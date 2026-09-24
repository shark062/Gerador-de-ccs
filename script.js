async function gerarCCs() {
    const bin = document.getElementById('binInput').value;
    const amount = document.getElementById('amountInput').value;
    const statusText = document.getElementById('status');
    const logContainer = document.getElementById('logContainer');

    if(!bin || !amount) {
        alert("Preencha o BIN e a Quantidade!");
        return;
    }

    statusText.innerText = "Gerando...";
    logContainer.innerHTML = ""; // Limpa o log

    try {
        const response = await fetch('http://127.0.0.1:5000/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bin: bin, amount: amount })
        });

        if (!response.ok) throw new Error("Erro no servidor");

        const data = await response.json();
        statusText.innerText = "Sucesso!";

        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'cc-item';
            div.innerText = `[+] ${item.cc} | ${item.month}/${item.year} | CVV: ${item.cvv}`;
            logContainer.appendChild(div);
        });

    } catch (error) {
        console.error(error);
        statusText.innerText = "Erro na conexão!";
    }
}

document.getElementById('generateBtn').addEventListener('click', gerarCCs);