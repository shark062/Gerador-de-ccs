// ... dentro do seu try/catch no JavaScript ...

const data = await response.json();

// O seu Python retorna um objeto que contém 'valid' e 'invalid'
// Se você quer mostrar as CCs que foram geradas:
const cardsParaMostrar = data.valid.length > 0 ? data.valid : data.invalid;

if (cardsParaMostrar.length === 0) {
    logContainer.innerHTML = "<p style='color: #ff003c;'>[!] Nenhuma CC gerada.</p>";
    return;
}

// Agora percorre a lista correta
cardsParaMostrar.forEach((item, index) => {
    setTimeout(() => {
        const div = document.createElement('div');
        div.className = 'cc-item';
        div.innerHTML = `
            <span style="color: #00ff41;">[+]</span> 
            <span>${item.cc}</span> | 
            <span>${item.expiry}</span> | 
            <span style="color: #ff003c;">CVV: ${item.cvv}</span>
        `;
        logContainer.appendChild(div);
        logContainer.scrollTop = logContainer.scrollHeight;
    }, index * 100);
});
