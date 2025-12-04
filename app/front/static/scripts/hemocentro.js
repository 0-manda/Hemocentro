// variável global para armazenar dados
let hemocentrosDataGlobal = [];

// funções auxiliares
function dadosAleatorios(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function obterMapUrl(hemo) {
  const endereco = encodeURIComponent(
    `${hemo.endereco}, ${hemo.cidade}, ${hemo.estado}`
  );
  return `https://www.google.com/maps?q=${endereco}&output=embed`;
}
async function buscarHemocentrosBD() {
  try {
    console.log("=== BUSCANDO HEMOCENTROS DO BD ===");

    const resp = await fetch("/api/hemocentros", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    console.log("Status da resposta:", resp.status);
    const res = await resp.json();
    console.log("Resposta completa:", res);
    if (res.success && res.hemocentros) {
      console.log("Hemocentros encontrados:", res.hemocentros.length);
      return res.hemocentros;
    } else {
      console.error("Erro ao buscar hemocentros:", res.message);
      return [];
    }
  } catch (err) {
    console.error("ERRO ao buscar hemocentros:", err);
    return [];
  }
}

async function buscarEstoquePorHemocentro(idHemocentro) {
  try {
    console.log(`Buscando estoque do hemocentro ID ${idHemocentro}...`);
    const resp = await fetch(`/api/estoque/hemocentro/${idHemocentro}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (!resp.ok) {
      console.error(`Erro ao buscar estoque (${resp.status})`);
      return null;
    }
    const json = await resp.json();
    if (json.success && json.estoque) {
      console.log(
        `Estoque encontrado para hemocentro ${idHemocentro}:`,
        json.estoque
      );
      return json.estoque;
    } else {
      console.log(`Nenhum estoque para hemocentro ${idHemocentro}`);
      return null;
    }
  } catch (err) {
    console.error(`Erro ao buscar estoque do hemocentro ${idHemocentro}:`, err);
    return null;
  }
}

function mapearEstoque(listaEstoque) {
  const buscaEstoque = {};
  if (!listaEstoque) return buscaEstoque;
  listaEstoque.forEach((item) => {
    buscaEstoque[item.tipo_sanguineo] = item.quantidade;
  });
  return buscaEstoque;
}

async function verificarColaborador(idHemocentro) {
  const token = localStorage.getItem("token");
  if (!token) return false;
  try {
    const resp = await fetch("/api/perfil", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    if (!resp.ok) return false;
    const res = await resp.json();
    if (res.success && res.usuario) {
      const usuario = res.usuario;
      return (
        usuario.tipo_usuario === "colaborador" &&
        usuario.hemocentro &&
        usuario.hemocentro.id_hemocentro === idHemocentro
      );
    }
    return false;
  } catch (err) {
    console.error("Erro ao verificar colaborador:", err);
    return false;
  }
}

// renderização
function renderizarCardsHemocentros(hemocentros) {
  console.log("=== RENDERIZANDO CARDS ===");
  const listaView = document.getElementById("lista-view");
  if (!listaView) {
    console.error("Elemento #lista-view não encontrado!");
    return;
  }
  listaView.innerHTML = "";
  if (hemocentros.length === 0) {
    listaView.innerHTML =
      "<p style='text-align: center; padding: 40px;'>Nenhum hemocentro ativo no momento.</p>";
    return;
  }
  hemocentros.forEach((hemo, index) => {
    const article = document.createElement("article");
    article.className = "hemocentro-card";
    let horariosHTML = "";
    if (hemo.horarios && hemo.horarios.length > 0) {
      horariosHTML = `
        <section class="horarios-resumo">
          <h4>⏰ Horários de Funcionamento:</h4>
          <ul class="lista-horarios-card">
            ${hemo.horarios
              .slice(0, 3)
              .map(
                (h) => `
              <li>
                <strong>${h.dia_semana_nome}:</strong> 
                ${h.horario_abertura} - ${h.horario_fechamento}
              </li>
            `
              )
              .join("")}
            ${
              hemo.horarios.length > 3
                ? '<li class="ver-mais">+ Ver todos os horários</li>'
                : ""
            }
          </ul>
          <p class="status-aberto ${hemo.aberto_agora ? "aberto" : "fechado"}">
            ${hemo.aberto_agora ? "🟢 ABERTO AGORA" : "🔴 FECHADO"}
          </p>
        </section>
      `;
    } else {
      horariosHTML = `
        <section class="horarios-resumo">
          <p class="sem-horarios">⚠️ Horários não cadastrados</p>
        </section>
      `;
    }
    article.innerHTML = `
      <section class="info">
        <header>
          <h3>${hemo.nome}</h3>
        </header>
        <p><strong>Email:</strong> ${hemo.email}</p>
        <p><strong>Telefone:</strong> ${hemo.telefone}</p>
        <address>
          <strong>Localização:</strong> ${hemo.endereco}, ${hemo.cidade} - ${
      hemo.estado
    }, CEP: ${hemo.cep}
        </address>
        ${
          hemo.site
            ? `<p><strong>Site:</strong> <a href="${hemo.site}" target="_blank" rel="noopener">${hemo.site}</a></p>`
            : ""
        }
        ${horariosHTML}
        <button class="btn btn-visitar" data-index="${index}" aria-label="Visitar ${
      hemo.nome
    }">Visitar</button>
        <button class="btn btn-agendar" data-index="${index}" data-id="${
      hemo.id_hemocentro
    }" aria-label="Agendar no ${hemo.nome}">Agendar</button>
      </section>
    `;
    listaView.appendChild(article);
  });
  console.log("Cards renderizados com sucesso!");
}

function renderizarHorariosDetalhes(horarios, abertoAgora) {
  let horariosHTML = "";
  if (horarios && horarios.length > 0) {
    horariosHTML = `
      <section class="horarios-completos">
        <h4>⏰ Horários de Funcionamento</h4>
        <ul class="lista-horarios-detalhes">
          ${horarios
            .map(
              (h) => `
            <li class="horario-item">
              <span class="dia">${h.dia_semana_nome}:</span>
              <span class="horario">${h.horario_abertura} - ${h.horario_fechamento}</span>
            </li>
          `
            )
            .join("")}
        </ul>
        <p class="status-aberto-grande ${abertoAgora ? "aberto" : "fechado"}">
          ${abertoAgora ? "🟢 ABERTO AGORA" : "🔴 FECHADO NO MOMENTO"}
        </p>
      </section>
    `;
  } else {
    horariosHTML = `
      <section class="horarios-completos">
        <p class="sem-horarios">⚠️ Horários de funcionamento não cadastrados</p>
      </section>
    `;
  }
  return horariosHTML;
}

function calcularStatus(bolsas, meta) {
  const porcentagem = (bolsas / meta) * 100;
  let statusTexto, statusClasse;
  if (porcentagem >= 70) {
    statusTexto = "ADEQUADO - Estoque satisfatório";
    statusClasse = "status-adequado";
  } else {
    statusTexto = "BAIXO - Necessário reposição";
    statusClasse = "status-baixo";
  }
  return { porcentagem, statusTexto, statusClasse };
}

function renderizarEstoque(estoqueData) {
  const grid = document.getElementById("estoque-grid");
  if (!grid) {
    console.error("Elemento #estoque-grid não encontrado!");
    return;
  }
  grid.innerHTML = "";
  for (const tipo in estoqueData) {
    const data = estoqueData[tipo];
    const { porcentagem, statusTexto, statusClasse } = calcularStatus(
      data.bolsas,
      data.meta
    );
    const cardHTML = `
      <article class="card-sangue">
        <span class="tipo-sanguineo">${tipo}</span>
        <section class="estoque-info">
          <span>Estoque: <strong>${data.bolsas} litros</strong></span>
          <span>Meta: <strong>${data.meta}</strong></span>
        </section>
        <section class="barra-container">
          <span class="barra-nivel" style="width: ${porcentagem}%;"></span>
        </section>
        <span class="status-estoque ${statusClasse}">${statusTexto}</span>
      </article>
    `;
    grid.innerHTML += cardHTML;
  }
}

async function gerenciarEstoque(hemocentro, acao) {
  const tipoSangue = document.getElementById("tipo-sangue-gerenciar").value;
  const quantidade = parseInt(
    document.getElementById("quantidade-gerenciar").value
  );
  const aviso = document.getElementById("modal-aviso");
  if (!tipoSangue) {
    aviso.textContent = "Selecione o tipo sanguíneo";
    aviso.style.color = "red";
    return;
  }
  if (!quantidade || quantidade <= 0) {
    aviso.textContent = "Informe uma quantidade válida";
    aviso.style.color = "red";
    return;
  }
  const token = localStorage.getItem("token");
  if (!token) {
    aviso.textContent = "Você precisa estar logado";
    aviso.style.color = "red";
    return;
  }
  try {
    aviso.textContent = `${
      acao === "adicionar" ? "Adicionando" : "Removendo"
    }...`;
    aviso.style.color = "#666";

    const endpoint =
      acao === "adicionar" ? "/api/estoque/adicionar" : "/api/estoque/remover";

    const resp = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        tipo_sanguineo: tipoSangue,
        quantidade: quantidade,
      }),
    });

    const res = await resp.json();

    if (res.success) {
      aviso.textContent = `! ${res.message}`;
      aviso.style.color = "green";

      document.getElementById("form-gerenciar-estoque").reset();

      setTimeout(async () => {
        await atualizarEstoqueNaTela(hemocentro);
        document.getElementById("modal-gerenciamento").remove();
      }, 1000);
    } else {
      aviso.textContent = `X ${res.message}`;
      aviso.style.color = "red";
    }
  } catch (err) {
    console.error("Erro ao gerenciar estoque:", err);
    aviso.textContent = "X Erro ao conectar com o servidor";
    aviso.style.color = "red";
  }
}

async function atualizarEstoqueNaTela(hemocentro) {
  console.log("Atualizando estoque na tela...");
  const estoqueArray = await buscarEstoquePorHemocentro(hemocentro.id);
  const estoqueMap = mapearEstoque(estoqueArray);
  const index = hemocentrosDataGlobal.findIndex((h) => h.id === hemocentro.id);
  if (index !== -1) {
    hemocentrosDataGlobal[index].estoque = {
      "O+": { bolsas: estoqueMap["O+"] ?? 0, meta: 100 },
      "O-": { bolsas: estoqueMap["O-"] ?? 0, meta: 80 },
      "A+": { bolsas: estoqueMap["A+"] ?? 0, meta: 100 },
      "A-": { bolsas: estoqueMap["A-"] ?? 0, meta: 100 },
      "AB+": { bolsas: estoqueMap["AB+"] ?? 0, meta: 100 },
      "AB-": { bolsas: estoqueMap["AB-"] ?? 0, meta: 100 },
      "B+": { bolsas: estoqueMap["B+"] ?? 0, meta: 100 },
      "B-": { bolsas: estoqueMap["B-"] ?? 0, meta: 100 },
    };
    renderizarEstoque(hemocentrosDataGlobal[index].estoque);
  }
  console.log("Estoque atualizado!");
}

async function adicionarBotoesGerenciamento(hemocentro) {
  // Remove botão antigo se existir
  const btnAntigo = document.querySelector(".btn-gerenciar");
  if (btnAntigo) btnAntigo.remove();

  // Verifica se o usuário é colaborador deste hemocentro
  const eColaborador = await verificarColaborador(hemocentro.id);
  
  if (eColaborador) {
    const botoesAcao = document.querySelector(".botoes-acao");
    if (botoesAcao) {
      const btnGerenciar = document.createElement("button");
      btnGerenciar.className = "btn btn-gerenciar";
      btnGerenciar.textContent = "Gerenciar Estoque";
      btnGerenciar.addEventListener("click", () => {
        abrirModalGerenciamento(hemocentro);
      });
      botoesAcao.appendChild(btnGerenciar);
    }
  }
}

// Gerenciamento de estoque
async function adicionarBotoesGerenciamento(hemocentro) {
  const ehColaborador = await verificarColaborador(hemocentro.id);
  if (!ehColaborador) return;
  console.log(
    `Usuário é colaborador do ${hemocentro.nome}. Adicionando botões de gerenciamento...`
  );
  const botoesAcao = document.querySelector(".botoes-acao");
  if (botoesAcao) {
    // Verifica se o botão já existe para evitar duplicação
    const btnExistente = document.querySelector(".btn-gerenciar");
    if (btnExistente) return;
    const btnGerenciar = document.createElement("button");
    btnGerenciar.className = "btn-detalhe btn-gerenciar";
    btnGerenciar.textContent = "⚙️ Gerenciar Estoque";
    btnGerenciar.setAttribute("aria-label", "Gerenciar estoque do hemocentro");
    btnGerenciar.addEventListener("click", () =>
      abrirModalGerenciamento(hemocentro)
    );
    botoesAcao.insertBefore(btnGerenciar, botoesAcao.firstChild);
  }
}
function abrirModalGerenciamento(hemocentro) {
  console.log("Abrindo modal de gerenciamento para:", hemocentro.nome);
  const modalAntigo = document.getElementById("modal-gerenciamento");
  if (modalAntigo) modalAntigo.remove();
  const modal = document.createElement("section");
  modal.id = "modal-gerenciamento";
  modal.className = "modal-overlay";
  modal.innerHTML = `
    <article class="modal-content">
      <header class="modal-header">
        <h3>⚙️ Gerenciar Estoque - ${hemocentro.nome}</h3>
        <button class="btn-fechar" aria-label="Fechar modal">&times;</button>
      </header>
      
      <form id="form-gerenciar-estoque" class="modal-body">
        <label for="tipo-sangue-gerenciar">
          <strong>Tipo Sanguíneo:</strong>
        </label>
        <select id="tipo-sangue-gerenciar" required>
          <option value="">Selecione o tipo</option>
          <option value="O+">O+</option>
          <option value="O-">O-</option>
          <option value="A+">A+</option>
          <option value="A-">A-</option>
          <option value="B+">B+</option>
          <option value="B-">B-</option>
          <option value="AB+">AB+</option>
          <option value="AB-">AB-</option>
        </select>
        <label for="quantidade-gerenciar">
          <strong>Quantidade (litros):</strong>
        </label>
        <input
          type="number"
          id="quantidade-gerenciar"
          min="1"
          max="1000"
          required
          placeholder="Ex: 10"
        />
        <p class="modal-aviso" id="modal-aviso"></p>
      </form>
    </article>
  `;
  document.body.appendChild(modal);
  modal
    .querySelector(".btn-fechar")
    .addEventListener("click", () => modal.remove());
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.remove();
  });
  document
    .getElementById("btn-adicionar-estoque")
    .addEventListener("click", () => {
      gerenciarEstoque(hemocentro, "adicionar");
    });
  document
    .getElementById("btn-remover-estoque")
    .addEventListener("click", () => {
      gerenciarEstoque(hemocentro, "remover");
    });
}

// navegação entre views
async function mostrarDetalhes(index) {
  console.log("=== MOSTRANDO DETALHES ===");
  console.log("Index clicado:", index);
  console.log("Total de hemocentros:", hemocentrosDataGlobal.length);
  console.log("Hemocentro selecionado:", hemocentrosDataGlobal[index]);
  const hemocentro = hemocentrosDataGlobal[index];
  const detalheMapaIframe = document.getElementById("detalhe_mapa");
  document.getElementById("detalhe-nome").textContent = hemocentro.nome;
  document.getElementById("detalhe-localizacao").textContent =
    hemocentro.localizacao;
  if (hemocentro.map_url && detalheMapaIframe) {
    detalheMapaIframe.src = hemocentro.map_url;
  } else if (detalheMapaIframe) {
    detalheMapaIframe.src = "";
  }
  console.log("Estoque que será renderizado:", hemocentro.estoque);
  renderizarEstoque(hemocentro.estoque);
  const detalhesHemocentro = document.querySelector(".detalhes-hemocentro");
  if (detalhesHemocentro) {
    const horariosAntigos = detalhesHemocentro.querySelector(
      ".horarios-completos"
    );
    if (horariosAntigos) {
      horariosAntigos.remove();
    }
    const horariosHTML = renderizarHorariosDetalhes(
      hemocentro.horarios,
      hemocentro.abertoAgora
    );
    const horariosDiv = document.createElement("div");
    horariosDiv.innerHTML = horariosHTML;
    const botoesAcao = detalhesHemocentro.querySelector(".botoes-acao");
    if (botoesAcao) {
      detalhesHemocentro.insertBefore(
        horariosDiv.firstElementChild,
        botoesAcao
      );
    } else {
      detalhesHemocentro.appendChild(horariosDiv.firstElementChild);
    }
  }
  await adicionarBotoesGerenciamento(hemocentro);
  document.getElementById("lista-view").style.display = "none";
  document.getElementById("detalhe-view").classList.add("ativo");
  window.scrollTo(0, 0);
}

function mostrarLista() {
  document.getElementById("lista-view").style.display = "flex";
  document.getElementById("detalhe-view").classList.remove("ativo");
  const iframe = document.getElementById("detalhe_mapa");
  if (iframe) iframe.src = "";
  const btnGerenciar = document.querySelector(".btn-gerenciar");
  if (btnGerenciar) btnGerenciar.remove();
  const horariosDetalhes = document.querySelector(".horarios-completos");
  if (horariosDetalhes) horariosDetalhes.remove();
  window.scrollTo(0, 0);
}

// sistema principal
async function iniciarSistema() {
  console.log("=== INICIANDO SISTEMA ===");
  const hemocentrosBD = await buscarHemocentrosBD();
  renderizarCardsHemocentros(hemocentrosBD);
  hemocentrosDataGlobal = [];
  for (const hemo of hemocentrosBD) {
    console.log(
      `\n=== Processando hemocentro: ${hemo.nome} (ID: ${hemo.id_hemocentro}) ===`
    );
    const estoqueArray = await buscarEstoquePorHemocentro(hemo.id_hemocentro);
    const estoqueMap = mapearEstoque(estoqueArray);
    console.log(`Estoque mapeado para ${hemo.nome}:`, estoqueMap);
    const hemocentroCompleto = {
      id: hemo.id_hemocentro,
      nome: hemo.nome,
      localizacao: `${hemo.endereco}, ${hemo.cidade} - ${hemo.estado}`,
      map_url: obterMapUrl(hemo),
      horarios: hemo.horarios || [],
      abertoAgora: hemo.aberto_agora || false,
      estoque: {
        "O+": { bolsas: estoqueMap["O+"] ?? 0, meta: 100 },
        "O-": { bolsas: estoqueMap["O-"] ?? 0, meta: 80 },
        "A+": { bolsas: estoqueMap["A+"] ?? 0, meta: 100 },
        "A-": { bolsas: estoqueMap["A-"] ?? 0, meta: 100 },
        "AB+": { bolsas: estoqueMap["AB+"] ?? 0, meta: 100 },
        "AB-": { bolsas: estoqueMap["AB-"] ?? 0, meta: 100 },
        "B+": { bolsas: estoqueMap["B+"] ?? 0, meta: 100 },
        "B-": { bolsas: estoqueMap["B-"] ?? 0, meta: 100 },
      },
    };
    hemocentrosDataGlobal.push(hemocentroCompleto);
  }
  console.log(
    "\n=== Dados completos de todos os hemocentros ===",
    hemocentrosDataGlobal
  );
  configurarEventListeners();
}

function configurarEventListeners() {
  setTimeout(() => {
    const visitarButtons = document.querySelectorAll(".btn-visitar");
    console.log("Botões Visitar encontrados:", visitarButtons.length);
    visitarButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const index = parseInt(this.getAttribute("data-index"));
        console.log("Clicou em Visitar, index:", index);
        mostrarDetalhes(index);
      });
    });

    const btnVoltar = document.getElementById("btn-voltar");
    if (btnVoltar) {
      btnVoltar.addEventListener("click", mostrarLista);
    }

    const agendarButtons = document.querySelectorAll(".btn-agendar");
    console.log("Botões Agendar encontrados:", agendarButtons.length);
    agendarButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const hemocentroIndex = parseInt(this.getAttribute("data-index"));
        const hemocentroId = this.getAttribute("data-id");
        if (hemocentrosDataGlobal[hemocentroIndex]) {
          const h = hemocentrosDataGlobal[hemocentroIndex];
          const nomeCodificado = encodeURIComponent(h.nome);
          window.location.href = `/agendamento?id_hemocentro=${hemocentroId}&nome_hemocentro=${nomeCodificado}`;
        } else {
          alert("Erro: Hemocentro não encontrado.");
        }
      });
    });
  }, 100);
}

// inicialização da página de hemocentros
document.addEventListener("DOMContentLoaded", () => {
  const listaView = document.getElementById("lista-view");
  if (listaView) {
    iniciarSistema();
  }
});

// cadastro de hemocentro
const cadastroHemocentro = document.getElementById("cadastroHemocentro");
if (cadastroHemocentro) {
  const nomeHemocentro = document.getElementById("nomeHemocentro");
  const email = document.getElementById("emailInstitucional");
  const tel = document.getElementById("telefone");
  const end = document.getElementById("endereco");
  const cep = document.getElementById("cep");
  const site = document.getElementById("site");
  const hoje = new Date();
  const dia = String(hoje.getDate()).padStart(2, "0");
  const mes = String(hoje.getMonth() + 1).padStart(2, "0");
  const ano = hoje.getFullYear();
  const dCadastro = `${ano}-${mes}-${dia}`;
  const ativo = true;
  const reMail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const reCEP = /^\d{5}-?\d{3}$/;
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
    [nomeHemocentro, email, tel, end, cep].forEach((elemento, index) => {
      const valids = [okNome, okEmail, okTel, okEnd, okCEP];
      elemento.classList.toggle("erro", !valids[index]);
    });
    return okNome && okEmail && okTel && okEnd && okCEP;
  }
  cadastroHemocentro.addEventListener("input", validar);
  cadastroHemocentro.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (!validar()) {
      alert("Por favor, preencha corretamente todos os campos obrigatórios.");
      return;
    }
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
        window.location.href = "#";
      } else {
        alert("Erro: " + res.msg);
      }
    } catch (err) {
      console.error(err);
      alert("Erro de conexão com o servidor.");
    }
  });
}

// login de hemocentro
const loginHemocentro = document.getElementById("login_hemocentro");
if (loginHemocentro) {
  const loginUser = document.getElementById("login-usuario");
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
