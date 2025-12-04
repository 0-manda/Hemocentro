document.addEventListener("DOMContentLoaded", () => {
  // --- Variáveis de Referência do Formulário ---
  const cadastroUser = document.getElementById("cadastro-usuario");

  if (cadastroUser) {
    // Campos Comuns
    const nome = document.getElementById("nome");
    const hintNome = document.getElementById("hintNome");
    const email = document.getElementById("email");
    const hintEmail = document.getElementById("hintEmail");
    const senha = document.getElementById("senha");
    const hintSenha = document.getElementById("hintSenha");
    const senha2 = document.getElementById("senha2");
    const hintSenha2 = document.getElementById("hintSenha2");
    const telefone = document.getElementById("telefone");
    const tipoUser = document.getElementById("tipoUser");
    const termos = document.getElementById("termos");
    const hintTermos = document.getElementById("hintTermos");
    const bar = document.getElementById("bar");
    const send = document.getElementById("btnEnviar");

    // Seções de Conteúdo Variável
    const secaoDoador = document.getElementById("secao-doador");
    const secaoColaborador = document.getElementById("secao-colaborador");
    const secaoDadosDoador = document.getElementById("secao-dados-doador");

    // Elementos da Seção Doador
    const cpfDoc = document.getElementById("cpf_doc");
    const hintCpfDoc = document.getElementById("hint_cpf_doc");
    const dataNascimento = document.getElementById("dataNascimento");
    const tipoSangue = document.getElementById("tipoSangue");

    // Elementos da Seção Colaborador
    const cpfColaborador = document.getElementById("cpf_colaborador");
    const hintCpfColaborador = document.getElementById("hint_cpf_colaborador");
    const cnpjColaborador = document.getElementById("cnpj_colaborador"); // Obrigatório para Colaborador
    const hintCnpjColaborador = document.getElementById(
      "hint_cnpj_colaborador"
    );

    // Expressões Regulares e Funções de Validação
    const reMail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    // RegEx que aceita tanto CPF (11) quanto CNPJ (14), formatado ou não.
    const reCpfCnpj =
      /^(\d{3}\.?\d{3}\.?\d{3}-?\d{2}|\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2})$/;

    const vNome = (v) => v.trim().length >= 3;
    const vMail = (v) => reMail.test(v.trim());
    const vTerm = (v) => v === true;

    // vDocumento:
    // - 'cpf' obriga 11 dígitos.
    // - 'cnpj' obriga 14 dígitos.
    // - 'opcional_cpf' valida apenas se estiver preenchido, mas se preenchido, deve ser 11 dígitos.
    const vDocumento = (docValue, docType) => {
      const docNumeros = docValue.trim().replace(/\D/g, "");

      // 1. Opcional (CPF do Colaborador)
      if (docType === "opcional_cpf") {
        if (docNumeros.length === 0) return true; // Vazio é OK
        if (docNumeros.length !== 11) return false;
        return reCpfCnpj.test(docValue.trim());
      }

      // 2. Obrigatório (CPF Doador, CNPJ Colaborador)
      if (docNumeros.length === 0) return false; // Não pode estar vazio

      if (docType === "cpf" && docNumeros.length !== 11) return false;
      if (docType === "cnpj" && docNumeros.length !== 14) return false;

      return reCpfCnpj.test(docValue.trim());
    };

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
      if (campo && campo.classList) {
        campo.classList.toggle("ok", ok);
        campo.classList.toggle("erro", !ok);
        campo.setAttribute("aria-invalid", String(!ok));
      }
      if (hintElemento) {
        hintElemento.textContent = ok ? msgOK : msgERRO;
      }
    }

    function setBarra(pct) {
      bar.style.width = pct + "%";
      bar.className = "";
      if (pct < 40) bar.style.backgroundColor = "red";
      else if (pct < 80) bar.style.backgroundColor = "yellow";
      else bar.style.backgroundColor = "green";
    }

    // --- Lógica de Alternância de Campos ---

    function alternarCamposUsuario() {
      const tipoSelecionado = tipoUser.value;

      // Limpa e desabilita todos os campos de documento cruzados
      cpfDoc.disabled = true;
      cpfColaborador.disabled = true;
      cnpjColaborador.disabled = true;

      if (tipoSelecionado === "doador") {
        // Doador: Exibe CPF e Dados do Doador. Oculta Colaborador.
        secaoDoador.style.display = "block";
        secaoDadosDoador.style.display = "block";
        secaoColaborador.style.display = "none";
        cpfDoc.disabled = false;
      } else if (tipoSelecionado === "hemocentro") {
        // Colaborador: Oculta CPF Doador e Dados Doador. Exibe Colaborador (CPF e CNPJ).
        secaoDoador.style.display = "none";
        secaoDadosDoador.style.display = "none";
        secaoColaborador.style.display = "block";
        cpfColaborador.disabled = false;
        cnpjColaborador.disabled = false;
      }

      revalidar();
    }

    // revalidação

    function revalidar() {
      const tipoSelecionado = tipoUser.value;
      let okDocumento = true; // Começa como true, pois o documento pode ser opcionalmente o CNPJ

      // 1. Validação de Documento
      if (tipoSelecionado === "doador") {
        const okCpfDoador = vDocumento(cpfDoc.value, "cpf");
        setEstado(
          cpfDoc,
          hintCpfDoc,
          okCpfDoador,
          "",
          "CPF inválido ou incompleto (11 dígitos numéricos)."
        );
        okDocumento = okCpfDoador;
      } else {
        // hemocentro (Colaborador)
        // CNPJ é obrigatório para Colaborador
        const okCnpjColab = vDocumento(cnpjColaborador.value, "cnpj");
        setEstado(
          cnpjColaborador,
          hintCnpjColaborador,
          okCnpjColab,
          "",
          "CNPJ inválido ou incompleto (14 dígitos numéricos)."
        );

        // CPF é opcional para Colaborador (mas se digitado, deve ser válido)
        const okCpfColab = vDocumento(cpfColaborador.value, "opcional_cpf");
        setEstado(
          cpfColaborador,
          hintCpfColaborador,
          okCpfColab,
          "",
          "CPF inválido ou incompleto (11 dígitos numéricos)."
        );

        // O documento geral é OK se o CNPJ for válido E o CPF (se preenchido) for válido
        okDocumento = okCnpjColab && okCpfColab;
      }

      // valida as variaveis (vê se tá tudo certo)
      const okNome = vNome(nome.value);
      const okEmail = vMail(email.value);
      const pts = scoreSenha(senha.value);
      const okSenha = pts >= 40;
      const okTermos = vTerm(termos.checked);

      // mede a força de senha
      let strengthLabel = "";
      let strengthColor = "";
      if (pts < 40) {
        strengthLabel = "Senha fraca";
        strengthColor = "#d32f2f"; // vermelho
      } else if (pts < 80) {
        strengthLabel = "Senha média";
        strengthColor = "#ffa726"; // amarelo
      } else {
        strengthLabel = "Senha forte";
        strengthColor = "#2e7d32"; // verde
      }
      if (hintSenha) {
        hintSenha.textContent = strengthLabel;
        hintSenha.style.color = strengthColor;
        hintSenha.style.display = "block";
      }

      // Checagem de repetição de senha (se o campo existir)
      let okSenhaMatch = true;
      if (senha2) {
        const s2 = senha2.value || "";
        if (s2.trim().length === 0) {
          okSenhaMatch = false;
          if (hintSenha2) {
            hintSenha2.textContent = "Repita a senha";
            hintSenha2.style.color = "#d32f2f";
            hintSenha2.style.display = "block";
          }
        } else if (senha.value !== s2) {
          okSenhaMatch = false;
          if (hintSenha2) {
            hintSenha2.textContent = "Senhas não coincidem";
            hintSenha2.style.color = "#d32f2f";
            hintSenha2.style.display = "block";
          }
        } else {
          okSenhaMatch = true;
          if (hintSenha2) {
            hintSenha2.textContent = "Senhas conferem";
            hintSenha2.style.color = "#2e7d32";
            hintSenha2.style.display = "block";
          }
        }
        // Atualiza classes do campo repetir-senha
        if (senha2 && senha2.classList) {
          senha2.classList.toggle("ok", okSenhaMatch);
          senha2.classList.toggle("erro", !okSenhaMatch);
          senha2.setAttribute("aria-invalid", String(!okSenhaMatch));
        }
      }

      // Atualiza classes do campo senha de acordo com força mínima
      if (senha && senha.classList) {
        senha.classList.toggle("ok", okSenha);
        senha.classList.toggle("erro", !okSenha);
        senha.setAttribute("aria-invalid", String(!okSenha));
      }

      // Aplica estados (termos)
      setEstado(termos, hintTermos, okTermos, "", "Marque para continuar.");

      const tudoOK =
        okNome && okDocumento && okEmail && okSenha && okTermos && okSenhaMatch;
      send.disabled = !tudoOK;
      return tudoOK;
    }

    // --- Listeners ---

    // 1. Ouve a mudança no tipo de usuário (Doador/Colaborador)
    tipoUser.addEventListener("change", alternarCamposUsuario);

    // 2. Inicializa os campos na primeira carga da página
    alternarCamposUsuario();

    // Revalidação ao digitar
    cadastroUser.addEventListener("input", revalidar);

    // Envio do formulário
    cadastroUser.addEventListener("submit", async (event) => {
      event.preventDefault();

      if (!revalidar()) return;

      const tipoSelecionado = tipoUser.value;

      let dados, endpoint;

      if (tipoSelecionado === "hemocentro") {
        // Colaborador: CNPJ é obrigatório; CPF é opcional.
        const cnpjValor = cnpjColaborador.value.trim().replace(/\D/g, "");
        const cpfValor = cpfColaborador.value.trim().replace(/\D/g, "");

        // Colaborador (CNPJ e/ou CPF)
        endpoint = "/api/cadastrar-colaborador";
        dados = {
          nome: nome.value.trim(),
          email: email.value.trim(),
          senha: senha.value,
          telefone: telefone.value.trim(),
          cnpj: cnpjValor,
          // Inclui CPF apenas se tiver sido preenchido
          ...(cpfValor.length === 11 && { cpf: cpfValor }),
        };
      } else {
        // Doador (CPF)
        const cpfValor = cpfDoc.value.trim().replace(/\D/g, "");

        endpoint = "/api/cadastrar";
        dados = {
          nome: nome.value.trim(),
          email: email.value.trim(),
          senha: senha.value,
          telefone: telefone.value.trim(),
          cpf: cpfValor,
          data_nascimento: dataNascimento.value,
          tipo_sanguineo: tipoSangue.value,
        };
      }

      //desabilita botão durante envio
      send.disabled = true;
      send.value = "ENVIANDO...";

      //envia dados para o backend
      try {
        const resp = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(dados),
        });

        const res = await resp.json();
        if (res.success) {
          alert(res.message || "Cadastro realizado com sucesso!");

          if (res.token) {
            localStorage.setItem("token", res.token);
          }

          cadastroUser.reset();

          if (tipoSelecionado === "hemocentro") {
            window.location.href = "/login";
          } else {
            window.location.href = "/";
          }
        } else {
          alert("Erro: " + (res.message || "Erro ao cadastrar"));
          send.disabled = false;
          send.value = "CRIAR";
        }
      } catch (err) {
        console.error("Erro de cadastro:", err);
        alert("Erro de conexão com o servidor.");
        send.disabled = false;
        send.value = "CRIAR";
      }
    });
  }

  const loginUser = document.getElementById("login-usuario");

  if (loginUser) {
    const email = document.getElementById("email");
    const senha = document.getElementById("senha");
    const avisoEmail = document.getElementById("aviso-email");
    const avisoSenha = document.getElementById("aviso-senha");
    const avisoGeral = document.getElementById("aviso-geral");

    loginUser.addEventListener("submit", async function (e) {
      e.preventDefault();

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

      try {
        const resp = await fetch("/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            identificador: emailTeste,
            senha: senhaTeste,
          }),
        });

        const res = await resp.json();
        if (res.success) {
          localStorage.setItem("token", res.token);
          alert("Login realizado com sucesso!");
          window.location.href = "/perfil";
        } else {
          avisoGeral.style.color = "red";
          avisoGeral.textContent = res.message || "Email ou senha inválido.";
        }
      } catch (err) {
        console.error("Erro de login:", err);
        avisoGeral.style.color = "red";
        avisoGeral.textContent = "Erro de conexão com o servidor.";
      }
    });
  }
});
