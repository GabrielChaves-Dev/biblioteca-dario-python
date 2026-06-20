async function login() {
    let matricula = document.querySelector("input[name='matricula']").value;
    let senha = document.querySelector("input[name='senha']").value;

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matricula, senha })
        });
        const data = await res.json();

        if (data.success) {
            sessionStorage.setItem('usuario', JSON.stringify(data.user));
            window.location.href = "tela%20inicial.html";
        } else {
            alert("Login invalido");
        }
    } catch (err) {
        alert("Erro ao conectar com o servidor");
    }
}
