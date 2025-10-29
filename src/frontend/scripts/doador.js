// registro de cadastro do Usuario
const cadastroUser = document.getElementById("formUser");
// verifica se formUser existe na atual pagina
if (cadastroUser) {
  const nome = document.getElementById("nome");
  const hintNome = document.getElementById("hintNome"); // se houver a opcao de dica
  const email = document.getElementById("email");
  const hintEmail = document.getElementById("hintEmail");
  const senha = document.getElementById("senha");
  const hintSenha = document.getElementById("hintSenha");
  const telefone = document.getElementById("telefone");
  const tipoUser = document.getElementById("tipoUser");
  const dataNascimento = document.getElementById("dataNascimento");
  const tipoSangue = document.getElementById("tipoSangue");
  const termos = document.getElementById("termos");
  const hintTermos = document.getElementById("hintTermos");
  const bar = document.getElementById("bar");
  const sumarioErros = document.getElementById("sumarioErros");
  const send = document.getElementById("btnEnviar");
  let ativo = true;

  // data atual do cadastro
  const hoje = new Date();
  const dia = String(hoje.getDate()).padStart(2, "0");
  const mes = String(hoje.getMonth() + 1).padStart(2, "0");
  const ano = hoje.getFullYear();
  const dCadastro = `${ano}-${mes}-${dia}`; // formato ISO pra facilitar backend

  const reMail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const vNome = (v) => v.trim().length >= 3;
  const vMail = (v) => reMail.test(v.trim());
  const vTerm = (v) => v === true;

  function scoreSenha(v) {
    let p = 0;
    if (v.length >= 8) p += 30;
    if (/[A-Z]/.test(v)) p += 20;
    if (/[a-z]/.test(v)) p += 20;
    if (/\d/.test(v)) p += 15;
    if (/[^A-Za-z0-9]/.test(v)) p += 15;
    return Math.min(p, 100);
  }

  function setEstado(campo, hintElemento, ok, msgOK, msgERRO) {
    campo.classList.toggle("ok", ok);
    campo.classList.toggle("erro", !ok);
    campo.setAttribute("aria-invalid", String(!ok));
    hintElemento.textContent = ok ? msgOK : msgERRO;
  }

  function setBarra(pct) {
    bar.style.width = pct + "%";
    bar.className = "";
    if (pct < 40) bar.classList.add("fraca");
    else if (pct < 80) bar.classList.add("media");
    else bar.classList.add("forte");
  }

  function revalidar() {
    const okNome = vNome(nome.value);
    const okEmail = vMail(email.value);
    const pts = scoreSenha(senha.value);
    const okSenha = pts >= 40;
    const okTermos = vTerm(termos.checked);

    setEstado(nome, hintNome, okNome, "Nome ok.", "Mínimo 3 caracteres.");
    setEstado(email, hintEmail, okEmail, "E-mail ok.", "Ex.: nome@dominio.com");
    setBarra(pts);
    setEstado(
      senha,
      hintSenha,
      okSenha,
      "Senha adequada.",
      "Use 8+ chars, nº e símbolos."
    );
    setEstado(
      termos,
      hintTermos,
      okTermos,
      "Termos aceitos.",
      "Marque para continuar."
    );

    const erros = [];
    if (!okNome) erros.push("Nome curto.");
    if (!okEmail) erros.push("E-mail inválido.");
    if (!okSenha) erros.push("Senha fraca.");
    if (!okTermos) erros.push("Termos não aceitos.");
    sumarioErros.textContent = erros.join(" ");

    const tudoOK = okNome && okEmail && okSenha && okTermos;
    send.disabled = !tudoOK;
    return tudoOK;
  }

  // Revalidação ao digitar
  cadastroUser.addEventListener("input", revalidar);

  // Envio do formulário
  cadastroUser.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!revalidar()) return;

    const dados = {
      nome: nome.value.trim(),
      email: email.value.trim(),
      senha: senha.value,
      telefone: telefone.value.trim(),
      tipoUser: tipoUser.value,
      dataNascimento: dataNascimento.value,
      tipoSangue: tipoSangue.value,
      dCadastro: dCadastro,
      ativo: ativo, // por padrao, o ativo eh "true"
    };

    // aqui eh pra lancar pro python/flask
    try {
      const resp = await fetch("/cadastroUser", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
      });

      const res = await resp.json();
      if (res.ok) {
        alert("Usuário cadastrado com sucesso!");
        cadastroUser.reset();
      } else {
        alert("Erro: " + res.msg);
      }
    } catch (err) {
      console.error(err);
      alert("Erro de conexão com o servidor.");
    }
  });
}

const loginUser = document.getElementById("login");
