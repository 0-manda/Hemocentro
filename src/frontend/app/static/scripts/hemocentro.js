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
    window.location.href = "#";
  });
}

const loginHemocentro = document.getElementById("login_hemocentro");

if (loginHemocentro) {
  const hemoTokenFalse =
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30";
  //const safe = "a-string-secret-at-least-256-bits-long"

  loginBtn.addEventListener("click", () => {
    const email = email.value;
    const senha = senha.value;
    if (email && senha) {
      localStorage.setItem("hemotoken", hemoTokenFalse);
      mensagem.textContent = "Login bem-sucedido!";
    } else {
      // ver depois com o bd
      mensagem.textContent = "Preencha e-mail e senha.";
    }
  });
  acessarBtn.addEventListener("click", () => {
    const token = localStorage.getItem("hemotoken");
    mensagem.textContent = token
      ? "Acesso permitido! Token encontrado."
      : "Acesso negado. Faça login.";
  });
}

const hemodados = document.getElementById("lista-view");
if (hemodados) {
  // Dados FALSOS de hemocentros (serão substituídos pelo banco de dados)

  function dadosAleatorios(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  const hemocentrosData = [
    {
      nome: "HOSPITAL VERA CRUZ",
      localizacao:
        "Avenida Guilherme Campos, 500, Jd. Sta. Genebra, Campinas, SP, Brasil",
      estoque: {
        "O+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "O-": { bolsas: dadosAleatorios(0, 50), meta: 80 },
        "A+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "A-": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "AB+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "AB-": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "B+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "B-": { bolsas: dadosAleatorios(0, 80), meta: 100 },
      },
    },
    {
      nome: "HOSPITAL UNICAMP",
      localizacao:
        "Rua Vital Brasil, 251 - Cidade Universitária, Campinas, SP, Brasil",
      estoque: {
        "O+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "O-": { bolsas: dadosAleatorios(0, 50), meta: 80 },
        "A+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "A-": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "AB+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "AB-": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "B+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "B-": { bolsas: dadosAleatorios(0, 80), meta: 100 },
      },
    },
    {
      nome: "HOSPITAL PAULÍNIA",
      localizacao: "Avenida José Paulino, 100, Paulínia, SP",
      estoque: {
        "O+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "O-": { bolsas: dadosAleatorios(0, 50), meta: 80 },
        "A+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "A-": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "AB+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "AB-": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "B+": { bolsas: dadosAleatorios(0, 80), meta: 100 },
        "B-": { bolsas: dadosAleatorios(0, 80), meta: 100 },
      },
    },
  ];

  // Função para calcular o status do estoque
  function calcularStatus(bolsas, meta) {
    const porcentagem = (bolsas / meta) * 100;
    let statusTexto, statusClasse;

    // Define o limite como 70% para 'satisfatório'
    if (porcentagem >= 70) {
      statusTexto = "ADEQUADO - Estoque satisfatório";
      statusClasse = "status-adequado";
    } else {
      statusTexto = "BAIXO - Necessário reposição";
      statusClasse = "status-baixo";
    }

    return { porcentagem, statusTexto, statusClasse };
  }

  // Função para renderizar os cartões de estoque
  function renderizarEstoque(estoqueData) {
    const grid = document.getElementById("estoque-grid");
    grid.innerHTML = ""; // Limpa o conteúdo anterior

    for (const tipo in estoqueData) {
      const data = estoqueData[tipo];
      const { bolsas, meta } = data;
      const { porcentagem, statusTexto, statusClasse } = calcularStatus(
        bolsas,
        meta
      );

      const cardHTML = `
      <div class="card-sangue">
          <span class="tipo-sanguineo">${tipo}</span>
          <div class="estoque-info">
              <span>Estoque: <strong>${bolsas} bolsas</strong></span>
              <span>Meta: <strong>${meta}</strong></span>
          </div>
          <div class="barra-container">
              <div class="barra-nivel" style="width: ${porcentagem}%;"></div>
          </div>
          <span class="status-estoque ${statusClasse}">${statusTexto}</span>
      </div>
    `;
      grid.innerHTML += cardHTML;
    }
  }

  // Função para mostrar a tela de detalhes
  function mostrarDetalhes(index) {
    const hemocentro = hemocentrosData[index];

    // 1. Atualiza as informações do hemocentro na coluna esquerda
    document.getElementById("detalhe-nome").textContent = hemocentro.nome;
    document.getElementById("detalhe-localizacao").textContent =
      hemocentro.localizacao;

    // 2. Renderiza os cartões de estoque na coluna direita
    renderizarEstoque(hemocentro.estoque);

    // 3. Altera a visibilidade das telas
    document.getElementById("lista-view").style.display = "none";
    document.getElementById("detalhe-view").classList.add("ativo");

    // Rola para o topo da página
    window.scrollTo(0, 0);
  }

  // Função para mostrar a lista (Botão "Voltar")
  function mostrarLista() {
    document.getElementById("lista-view").style.display = "flex";
    document.getElementById("detalhe-view").classList.remove("ativo");
    window.scrollTo(0, 0);
  }
}
