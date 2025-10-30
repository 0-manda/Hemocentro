// registro de cadastro do Usuario
const cadastroUser = document.getElementById("cadastro-usuario");
// verifica se formUser existe na atual pagina
if (cadastroUser) {
  const nome = document.getElementById("nome");
  const hintNome = document.getElementById("hintNome"); // se houver a opcao de dica
  const cpfCnpj = document.getElementById("cpf_cnpj");
  const hintCpfCnpj = document.getElementById("hint_cpf_cnpj");
  const email = document.getElementById("email");
  const hintEmail = document.getElementById("hintEmail");
  const sexo = document.getElementById("sexo");
  const senha = document.getElementById("senha");
  const hintSenha = document.getElementById("hintSenha");
  const telefone = document.getElementById("telefone");
  const tipoUser = document.getElementById("tipoUser");
  const dataNascimento = document.getElementById("dataNascimento");
  const tipoSangue = document.getElementById("tipoSangue");
  const termos = document.getElementById("termos");
  const hintTermos = document.getElementById("hintTermos");
  const bar = document.getElementById("bar");
  const send = document.getElementById("btnEnviar");
  let ativo = true; // por padrao eh true

  const reMail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const reCpfCnpj =
    /^(\d{3}\.?\d{3}\.?\d{3}-?\d{2}|\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2})$/; // aceita ou cpf ou cnpj

  const vNome = (v) => v.trim().length >= 3;
  const vMail = (v) => reMail.test(v.trim());
  const vTerm = (v) => v === true;
  const vCpfCnjpj = (v) => reCpfCnpj.test(v.trim());

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
    const okCpfCnpj = vCpfCnjpj(cpfCnpj.value);
    const okEmail = vMail(email.value);
    const pts = scoreSenha(senha.value);
    const okSenha = pts >= 40;
    const okTermos = vTerm(termos.checked);

    setEstado(nome, hintNome, okNome, "", "Mínimo 3 caracteres.");
    setEstado(
      cpfCnpj,
      hintCpfCnpj,
      okCpfCnpj,
      "",
      "Cpf ou cnpj recebem somente número."
    );
    setEstado(email, hintEmail, okEmail, "", "Ex.: exemplo@dominio.com");
    setBarra(pts);
    setEstado(senha, hintSenha, okSenha, "", "Use 8+ chars, nº e símbolos.");
    setEstado(termos, hintTermos, okTermos, "", "Marque para continuar.");

    const tudoOK = okNome && okCpfCnpj && okEmail && okSenha && okTermos;
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
      cpf: cpfCnpj.value.trim(),
      data_nascimento: dataNascimento.value,
      sexo: sexo.value,
      tipo_sanguineo: tipoSangue.value,
    };

    // aqui eh pra lancar pro python/flask
    try {
      const resp = await fetch("/cadastrar_usuario", {
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
    window.location.href = "index.html"; // esse direcionamento eh temporario
  });
}

const loginUser = document.getElementById("login-usuario");

if (loginUser) {
  const tokenFake =
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30";

  const email = document.getElementById("email");
  const senha = document.getElementById("senha");
  const avisoEmail = document.getElementById("aviso-email");
  const avisoSenha = document.getElementById("aviso-senha");

  loginUser.addEventListener("submit", function (event) {
    event.preventDefault();
    const emailTeste = email.value.trim();
    const senhaTeste = senha.value.trim();
    if (emailTeste === "") {
      avisoEmail.style.color = "red";
      avisoEmail.textContent = "Email vazio.";
      return;
    } else if (senhaTeste === "") {
      avisoSenha.style.color = "red";
      avisoSenha.textContent = "Senha vazia.";
      return;
    }
    localStorage.setItem("token", tokenFake);
    window.location.href = "../templates/index.html";
  });

  // essa parte tem que ficar ligada ao logout do usuario
  // logoutBtn.addEventListener("click", () => {
  //   localStorage.removeItem("token");
  //   mensagem.textContent = "Logout realizado.";
  // });
}
