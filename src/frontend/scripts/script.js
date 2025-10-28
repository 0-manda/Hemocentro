const form = document.getElementById("form");

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
  const nome = document.getElementById("nome");
  const hintNome = document.getElementById("hintNome");
  const email = document.getElementById("email");
  const hintEmail = document.getElementById("hintEmail");
  const senha = document.getElementById("senha");
  const hintSenha = document.getElementById("hintSenha");
  const telefone = document.getElementById("telefone");
  const tipoUser = document.getElementById("tipoUser");
  const dataNascimento = document.getElementById("dataNascimento");
  const hintData = document.getElementById("hintData");
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
// registro de cadastro do Hemocentro
const cadastroHemocentro = document.getElementById("cadastroHemocentro");

if (cadastroHemocentro) {
  const nomeHemocentro = document.getElementById("nomeHemocentro");
  const email = document.getElementById("emailInstitucional");
  const tel = document.getElementById("telefone");
  const end = document.getElementById("endereco");
  const cep = document.getElementById("cep");
  const site = document.getElementById("site");
  const btnEnviar = document.getElementById("btnEnviar");

  // data atual do cadastro (jah no formato ISO)
  const hoje = new Date();
  const dia = String(hoje.getDate()).padStart(2, "0");
  const mes = String(hoje.getMonth() + 1).padStart(2, "0");
  const ano = hoje.getFullYear();
  const dCadastro = `${ano}-${mes}-${dia}`;

  let ativo = true; // ativo por padrão

  // Regex para e-mail e CEP (simples)
  const reMail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const reCEP = /^\d{5}-?\d{3}$/; // formato ideal pra cep "XXXXX-XXX"

  // Funções de validação
  const vNome = (v) => v.trim().length >= 3;
  const vMail = (v) => reMail.test(v.trim());
  const vTel = (v) => v.trim().length >= 8;
  const vEnd = (v) => v.trim().length >= 5;
  const vCEP = (v) => reCEP.test(v.trim());

  function validar() {
    const okNome = vNome(nomeHemocentro.value);
    const okEmail = vMail(email.value);
    const okTel = vTel(tel.value);
    const okEnd = vEnd(end.value);
    const okCEP = vCEP(cep.value);

    // mostra erro visual simples (borda vermelha)
    [nomeHemocentro, email, tel, end, cep].forEach((elemento, index) => {
      const valids = [okNome, okEmail, okTel, okEnd, okCEP];
      elemento.classList.toggle("erro", !valids[index]);
    });

    return okNome && okEmail && okTel && okEnd && okCEP; // retorna true ou false
  }

  cadastroHemocentro.addEventListener("input", validar);

  cadastroHemocentro.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    if (!validar()) {
      alert("Por favor, preencha corretamente todos os campos obrigatórios.");
      return;
    }

    // dic das variaveis
    const dados = {
      nomeHemocentro: nomeHemocentro.value.trim(),
      emailInstitucional: email.value.trim(),
      telefone: tel.value.trim(),
      endereco: end.value.trim(),
      cep: cep.value.trim(),
      site: site.value.trim(),
      dCadastro: dCadastro,
      ativo: ativo,
    };

    // aqui deve ser a comunicacao com o flask
    try {
      const resp = await fetch("/cadastroHemocentro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
      });

      const res = await resp.json();

      if (res.ok) {
        alert("Hemocentro cadastrado com sucesso!");
        cadastroHemocentro.reset();
      } else {
        alert("Erro: " + res.msg);
      }
    } catch (err) {
      console.error(err);
      alert("Erro de conexão com o servidor.");
    }
  });
}

// registro de horario de funcionamento
const horarioFuncionamento = document.getElementById("horarioFuncionamento");

if (horarioFuncionamento) {
  const dFuncionamento = document.getElementById("diaFuncionamento");
  const hAbertura = document.getElementById("horaAbertura");
  const hFechado = document.getElementById("horaFechamento");
  const observacao = document.getElementById("observacao");

  // Pega a data atual
  const hoje = new Date();
  const dia = String(hoje.getDate()).padStart(2, "0");
  const mes = String(hoje.getMonth() + 1).padStart(2, "0");
  const ano = hoje.getFullYear();
  const dCadastro = `${ano}-${mes}-${dia}`; //jah deixo no formato mysql

  const vDia = (v) => v.trim().length > 0;
  const vHora = (v) => /^\d{2}:\d{2}$/.test(v.trim()); // formato HH:MM
  const compararHoras = (inicio, fim) => {
    const [h1, m1] = inicio.split(":").map(Number);
    const [h2, m2] = fim.split(":").map(Number);
    return h1 < h2 || (h1 === h2 && m1 < m2);
  };

  function validar() {
    const okDia = vDia(dFuncionamento.value);
    const okAbertura = vHora(hAbertura.value);
    const okFechado = vHora(hFechado.value);
    const ordemCerta =
      okAbertura && okFechado && compararHoras(hAbertura.value, hFechado.value);

    // Aplica estilos de erro simples
    dFuncionamento.classList.toggle("erro", !okDia);
    hAbertura.classList.toggle("erro", !okAbertura);
    hFechado.classList.toggle("erro", !okFechado || !ordemCerta);

    return okDia && okAbertura && okFechado && ordemCerta;
  }

  horarioFuncionamento.addEventListener("input", validar);

  // --------------------------
  // Envio do formulário
  // --------------------------
  horarioFuncionamento.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!validar()) {
      alert("Verifique se os campos estão corretos e o horário faz sentido.");
      return;
    }

    const dados = {
      diaFuncionamento: dFuncionamento.value.trim(),
      horaAbertura: hAbertura.value.trim(),
      horaFechamento: hFechado.value.trim(),
      observacao: observacao.value.trim(),
      dCadastro: dCadastro,
    };

    try {
      const resp = await fetch("/horarioFuncionamento", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
      });

      const res = await resp.json();

      if (res.ok) {
        alert("Horário de funcionamento cadastrado com sucesso!");
        horarioFuncionamento.reset();
      } else {
        alert("Erro: " + res.msg);
      }
    } catch (err) {
      console.error(err);
      alert("Erro de conexão com o servidor.");
    }
  });
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
