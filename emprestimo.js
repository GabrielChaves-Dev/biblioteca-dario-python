const usuario = JSON.parse(sessionStorage.getItem('usuario') || '{}');
const livros = document.querySelectorAll(".livro");

async function carregarLivros() {
    try {
        const res = await fetch('/api/livros');
        const livrosAPI = await res.json();
        const container = document.querySelector(".container");
        if (!container) return;

        livrosAPI.forEach(livro => {
            const div = document.createElement("div");
            div.className = "livro";
            div.dataset.id = livro.id;

            const btnLabel = livro.status === "disponivel" ? "Emprestar"
                : livro.status === "emprestado" ? "Devolver"
                : "Ver Reserva";

            const imgSrc = livro.imagem && livro.imagem.startsWith('http')
                ? livro.imagem
                : livro.imagem || 'livros.svg';

            div.innerHTML = `
                <div class="status ${livro.status}">${capitalizar(livro.status)}</div>
                <img src="${imgSrc}" alt="${livro.titulo}" onerror="this.src='livros.svg'">
                <h3>${livro.titulo}</h3>
                <p>${livro.autor}</p>
                <div class="acoes">
                    <button class="btn-acao">${btnLabel}</button>
                </div>
            `;
            container.appendChild(div);
        });

        document.querySelectorAll(".btn-acao").forEach(btn => {
            btn.addEventListener("click", handleAcao);
        });
    } catch (err) {
        console.error("Erro ao carregar livros:", err);
    }
}

function capitalizar(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

async function handleAcao(e) {
    const btn = e.target;
    const livroDiv = btn.closest(".livro");
    const livroId = livroDiv.dataset.id;
    const statusDiv = livroDiv.querySelector(".status");
    const acao = btn.textContent;

    if (acao === "Emprestar") {
        if (!usuario.id) {
            alert("Faca login primeiro!");
            window.location.href = "bibliotecaa.html";
            return;
        }
        try {
            const res = await fetch('/api/emprestar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ livro_id: parseInt(livroId), usuario_id: usuario.id })
            });
            const data = await res.json();
            if (data.success) {
                statusDiv.textContent = "Emprestado";
                statusDiv.className = "status emprestado";
                btn.textContent = "Devolver";
                alert(data.message);
            } else {
                alert(data.message);
            }
        } catch (err) {
            alert("Erro ao emprestar livro");
        }
    } else if (acao === "Devolver") {
        try {
            const res = await fetch('/api/devolver', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ livro_id: parseInt(livroId) })
            });
            const data = await res.json();
            if (data.success) {
                statusDiv.textContent = "Disponivel";
                statusDiv.className = "status disponivel";
                btn.textContent = "Emprestar";
                alert(data.message);
            } else {
                alert(data.message);
            }
        } catch (err) {
            alert("Erro ao devolver livro");
        }
    } else if (acao === "Ver Reserva") {
        alert("Este livro esta reservado.");
    }
}

if (document.querySelector(".container")) {
    carregarLivros();
}

document.querySelectorAll(".livro").forEach(livro => {
    const botao = livro.querySelector("button");
    const status = livro.querySelector(".status");

    if (botao) {
        botao.addEventListener("click", () => {
            if (botao.textContent === "Emprestar" && !usuario.id) {
                alert("Faca login primeiro!");
                window.location.href = "bibliotecaa.html";
                return;
            }

            if (botao.textContent === "Emprestar") {
                status.textContent = "Emprestado";
                status.classList.remove("disponivel");
                status.classList.add("emprestado");
                botao.textContent = "Devolver";
                alert("Livro emprestado com sucesso!");
            } else if (botao.textContent === "Devolver") {
                status.textContent = "Disponivel";
                status.classList.remove("emprestado");
                status.classList.add("disponivel");
                botao.textContent = "Emprestar";
                alert("Livro devolvido com sucesso!");
            } else if (botao.textContent === "Ver Reserva") {
                alert("Este livro esta reservado.");
            }
        });
    }
});
