const form = document.getElementById("f");

if (form) {
  const nome = document.getElementById("nome");
  const email = document.getElementById("email");
  const senha = document.getElementById("senha");
  const termos = document.getElementById("termos");
  const bar = document.getElementById("bar"); // mostra se a senha estah boa ou n
  const hintNome = document.getElementById("hintNome");
  const hintEmail = document.getElementById("hintEmail");
  const hintSenha = document.getElementById("hintSenha");
  const hintTermos = document.getElementById("hintTermos");
  const sumarioErros = document.getElementById("sumarioErros");
  const send = document.getElementById("send"); // botao
  const ok = document.getElementById("ok"); // eh um check

  // --------------------------
  // [2] Validadores (lógica pura)
  // --------------------------
  const reMail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const vNome = (v) => v.trim().length >= 3;
  const vMail = (v) => reMail.test(v.trim());
  const vTerm = (v) => v === true;
  // Força de senha (pontuação simples)
  function scoreSenha(v) {
    let p = 0;
    if (v.length >= 8) p += 30;
    if (/[A-Z]/.test(v)) p += 20;
    if (/[a-z]/.test(v)) p += 20;
    if (/\d/.test(v)) p += 15;
    if (/[^A-Za-z0-9]/.test(v)) p += 15;
    return Math.min(p, 100);
  }
  // --------------------------
  // [3] UI helpers (apenas interface)
  // --------------------------
  function setEstado(campo, hintElemento, ok, msgOK, msgERRO) {
    campo.classList.toggle("ok", ok);
    campo.classList.toggle("erro", !ok);
    campo.setAttribute("aria-invalid", String(!ok));
    hintElemento.textContent = ok ? msgOK : msgERRO;
  }
  function setBarra(pct) {
    bar.style.width = pct + "%";
    bar.className = ""; // reset classes
    if (pct < 40) bar.classList.add("fraca");
    else if (pct < 80) bar.classList.add("media");
    else bar.classList.add("forte");
  }

  // --------------------------
  // [4] Revalidação geral
  // --------------------------
  function revalidar() {
    const okNome = vNome(nome.value);
    const okEmail = vMail(email.value);
    const pts = scoreSenha(senha.value);
    const okSenha = pts >= 40; // exige pelo menos "média"
    const okTermos = vTerm(termos.checked);

    // dicas ou sugestoes dos inputs
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
      "Termos .",
      "Marque para continuar."
    );

    // Sumário de erros para acessibilidade (screen readers)
    const erros = [];
    if (!okNome) erros.push("Nome curto.");
    if (!okEmail) erros.push("E-mail inválido.");
    if (!okSenha) erros.push("Senha fraca.");
    if (!okTermos) erros.push("Termos não aceitos.");
    sumarioErros.textContent = erros.join(" ");
    // Habilita envio apenas se tudo ok
    const tudoOK = okNome && okEmail && okSenha && okTermos;
    send.disabled = !tudoOK;
    return tudoOK;
  }

  // --------------------------
  // [5] Ouvintes por campo
  // --------------------------
  nome.addEventListener("input", revalidar);
  email.addEventListener("input", revalidar);
  senha.addEventListener("input", revalidar);
  termos.addEventListener("change", revalidar);
  // --------------------------
  // [6] Envio
  // --------------------------
  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    if (!revalidar()) return;
    // Aqui caberia um fetch(...) real (é o início da API Fetch em JavaScript)
    ok.textContent = "Cadastro enviado com sucesso! ";
    form.reset();
    setBarra(0);
    revalidar(); // recalcula estados após reset
  });
}

// registro de cadastro do Usuario

const cadastroUser = document.getElementById("formUser");
// verifica se formUser existe na atual pagina
if (cadastroUser) {
  const nome = document.getElementById("nome"); // tem q <------
  const hintNome = document.getElementById("hintNome");
  const email = document.getElementById("email"); // tem q <------
  const hintEmail = document.getElementById("hintEmail");
  const senha = document.getElementById("senha"); // tem q <------
  const hintSenha = document.getElementById("hintSenha");
  const telefone = document.getElementById("telefone");
  const tipoUser = document.getElementById("tipoUser"); // tem q <-----
  const dataNascimento = document.getElementById("dataNascimento"); // tem q <------
  const hintData = document.getElementById("hintData");
  const tipoSangue = document.getElementById("tipoSangue"); // tem q <------
  let ativo = true;

  // pega a data do atual cadastro
  const hoje = new Date();
  const mes = hoje.getMonth() + 1; // 0-11, então somamos 1
  const dia = hoje.getDate(); // 1-31
  const ano = hoje.getFullYear(); // 4 dígitos
  const dCadastro = `${dia}/${mes}/${ano}`;

  const reMail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const vNome = (v) => v.trim().length >= 3;
  const vMail = (v) => reMail.test(v.trim());
  const vTerm = (v) => v === true;

  // verificar pra proxima <--
  // const idade = function (data) { // verifica se o usuario esta apto ou nao para doar
  //   const seAno = ano - dataNascimento.getFullYear();
  //   const seMes = mes - dataNascimento.getMonth() + 1;
  //   if (seMes < 0 || seAno < 18) {
  //     // aviso que tem de ser maior de 16
  //     return;
  //   } else if (seAnos >= 60) { // tem que ter um check pra
  //     return;
  //   }
  // };

  // Força de senha (pontuação simples)
  function scoreSenha(v) {
    let p = 0;
    if (v.length >= 8) p += 30;
    if (/[A-Z]/.test(v)) p += 20;
    if (/[a-z]/.test(v)) p += 20;
    if (/\d/.test(v)) p += 15;
    if (/[^A-Za-z0-9]/.test(v)) p += 15;
    return Math.min(p, 100);
  }
  // --------------------------
  // [3] UI helpers (apenas interface)
  // --------------------------
  function setEstado(campo, hintElemento, ok, msgOK, msgERRO) {
    campo.classList.toggle("ok", ok);
    campo.classList.toggle("erro", !ok);
    campo.setAttribute("aria-invalid", String(!ok));
    hintElemento.textContent = ok ? msgOK : msgERRO;
  }
  function setBarra(pct) {
    bar.style.width = pct + "%";
    bar.className = ""; // reset classes
    if (pct < 40) bar.classList.add("fraca");
    else if (pct < 80) bar.classList.add("media");
    else bar.classList.add("forte");
  }

  // --------------------------
  // [4] Revalidação geral
  // --------------------------
  function revalidar() {
    const okNome = vNome(nome.value);
    const okEmail = vMail(email.value);
    const pts = scoreSenha(senha.value);
    const okSenha = pts >= 40; // exige pelo menos "média"
    const okTermos = vTerm(termos.checked);

    // dicas ou sugestoes dos inputs
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
      "Termos .",
      "Marque para continuar."
    );

    // Sumário de erros para acessibilidade (screen readers)
    const erros = [];
    if (!okNome) erros.push("Nome curto.");
    if (!okEmail) erros.push("E-mail inválido.");
    if (!okSenha) erros.push("Senha fraca.");
    if (!okTermos) erros.push("Termos não aceitos.");
    sumarioErros.textContent = erros.join(" ");
    // Habilita envio apenas se tudo ok
    const tudoOK = okNome && okEmail && okSenha && okTermos;
    send.disabled = !tudoOK;
    return tudoOK;

    //aqui tem que ter a conexao com o python
  }

  // --------------------------
  // [5] Ouvintes por campo
  // --------------------------
  nome.addEventListener("input", revalidar);
  email.addEventListener("input", revalidar);
  senha.addEventListener("input", revalidar);
  termos.addEventListener("change", revalidar);
  // --------------------------
  // [6] Envio
  // --------------------------
  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    if (!revalidar()) return;
    // Aqui caberia um fetch(...) real (é o início da API Fetch em JavaScript)
    ok.textContent = "Cadastro enviado com sucesso! ";
    form.reset();
    setBarra(0);
    revalidar(); // recalcula estados após reset
  });
}

// registro de cadastro do Hemocentro
const cadastroHemocentro = document.getElementById("cadastroHemocentro");

if (cadastroHemocentro) {
  const nomeHemocentro = document.getElementById("nomeHemocentro"); // ver o jeito que foi posto nos htmls  // tem q <------
  const email = documento.getelementById("emailInstituicional"); // tem q <------
  const tel = document.getElementById("telefone"); // tem q <------
  const end = document.getElementById("endereco"); // tem q <------
  //const cidade = document.getElementById("cidade"); // não sei se deixo, pq por padrao vai ficar soh campinas - sp
  //const estado = document.getElementById("estado");
  const cep = document.getElementById("cep"); // tem q <------
  const site = document.getElementById("site");

  // pega a data do atual cadastro
  const hoje = new Date();
  const mes = hoje.getMonth() + 1; // 0-11, então somamos 1
  const dia = hoje.getDate(); // 1-31
  const ano = hoje.getFullYear(); // 4 dígitos
  const dCadastro = `${dia}/${mes}/${ano}`;

  let ativo = true; // ativo por padrao por ser primeiro cadastro
}

// registro de horario de funcionamento
const horarioFuncionamento = document.getElementById("horarioFuncionamento");
if (horarioFuncionamento) {
  const dFuncionamento = document.getElementById("diaFuncionamento"); // tem q <------
  const hAbertura = document.getElementById("horaAbertura"); // tem q <------
  const hFechado = document.getElementById("horaFechamento"); // tem q <------
  const observacao = document.getElementById("observacao");
}

// registro de campanha
const campanha = document.getElementById("campanha");
if (campanha) {
  const descricao = document.getElementById("descricao");
  const dInic = document.getElementById("diaInicio"); // tem q <------
  const dFim = document.getElementById("diaFim"); // tem q <------
  const tipoSangueRequerido = document.getElementById("tipoSangueRequerido"); // tem q <------
  const qtdMetaLitros = document.getElementById("qtdMetaLitros"); // tem q <------
  const qtdAtual = document.getElementById("qtdAtual"); // tem q <------
  const objetivo = document.getElementById("objetivo");
  let ativo = true; // cmc cm true enqt a campanha durar
  const destaque = document.getElementById("destaque");

  // pega a data do atual cadastro
  const hoje = new Date();
  const mes = hoje.getMonth() + 1; // 0-11, então somamos 1
  const dia = hoje.getDate(); // 1-31
  const ano = hoje.getFullYear(); // 4 dígitos
  const dCriacao = `${dia}/${mes}/${ano}`;
}
