// dah acesso somente a quem tem o token
if (localStorage.getItem("token")) {
  // registro de campanha
  const campanha = document.getElementById("campanha");

  if (campanha) {
    const nome = document.getElementById("nome");
    const descricao = document.getElementById("descricao");
    const dInic = document.getElementById("diaInicio");
    const dFim = document.getElementById("diaFim");
    const tipoSangueRequerido = document.getElementById("tipoSangueRequerido");
    const qtdMetaLitros = document.getElementById("qtdMetaLitros");
    const qtdAtual = document.getElementById("qtdAtual");
    const objetivo = document.getElementById("objetivo");
    const destaque = document.getElementById("destaque");
    let ativo = true;

    //pega a data atual
    const hoje = new Date();
    const dia = String(hoje.getDate()).padStart(2, "0");
    const mes = String(hoje.getMonth() + 1).padStart(2, "0");
    const ano = hoje.getFullYear();
    const dCriacao = `${ano}-${mes}-${dia}`;

    //validação
    const vTexto = (v) => v.trim().length >= 3;
    const vData = (v) => /^\d{4}-\d{2}-\d{2}$/.test(v);
    const vNumero = (v) => !isNaN(v) && Number(v) >= 0;
    const compararDatas = (inicio, fim) => new Date(inicio) <= new Date(fim);

    function validar() {
      const okNome = vTexto(nome.value);
      const okDescricao = vTexto(descricao.value);
      const okInicio = vData(dInic.value);
      const okFim = vData(dFim.value);
      const ordemCerta =
        okInicio && okFim && compararDatas(dInic.value, dFim.value);
      const okTipo = vTexto(tipoSangueRequerido.value);
      const okMeta = vNumero(qtdMetaLitros.value);
      const okObjetivo = vTexto(objetivo.value);

      // aplicar classes de erro simples
      nome.classList.toggle("erro", !okNome);
      descricao.classList.toggle("erro", !okDescricao);
      dInic.classList.toggle("erro", !okInicio);
      dFim.classList.toggle("erro", !okFim || !ordemCerta);
      tipoSangueRequerido.classList.toggle("erro", !okTipo);
      qtdMetaLitros.classList.toggle("erro", !okMeta);
      objetivo.classList.toggle("erro", !okObjetivo);

      return (
        okNome &&
        okDescricao &&
        okInicio &&
        okFim &&
        ordemCerta &&
        okTipo &&
        okMeta &&
        okObjetivo
      );
    }

    campanha.addEventListener("input", validar);

    // envio pro backend
    campanha.addEventListener("submit", async (e) => {
      e.preventDefault();

      if (!validar()) {
        alert("Verifique os campos antes de enviar. Há erros no formulário.");
        return;
      }

      const dados = {
        nome: nome.value.trim(),
        descricao: descricao.value.trim(),
        data_inicio: dInic.value.trim(),
        data_fim: dFim.value.trim(),
        tipo_sanguineo_necessario: tipoSangueRequerido.value.trim(),
        quantidade_meta_litros: Number(qtdMetaLitros.value),
        objetivo: objetivo.value.trim(),
        destaque: destaque.checked || false,
      };

      // ver conectividade com o flask
      try {
        const token = localStorage.getItem("token");
        const resp = await fetch("/api/cadastrar_campanha", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(dados),
        });

        const res = await resp.json();

        if (res.success) {
          alert("Campanha registrada com sucesso!");
          campanha.reset();
          //recarrega a lista de campanhas
          if (typeof buscarCampanhas === "function") {
            buscarCampanhas();
          }
        } else {
          alert("Erro: " + res.message);
        }
      } catch (err) {
        console.error(err);
        alert("Erro ao conectar com o servidor.");
      }
    });
  }
}

// buscar e exibir campanhas (SEMPRE PÚBLICO)

async function buscarCampanhas() {
  console.log("Iniciando busca de campanhas...");

  try {
    const token = localStorage.getItem("token");
    console.log("Token existe?", token ? "SIM" : "NÃO");

    // MUDANÇA: Sempre usa o endpoint público
    const endpoint = "/api/campanhas";
    console.log("Endpoint que será chamado:", endpoint);

    const headers = {
      "Content-Type": "application/json",
    };

    // Token é enviado apenas para verificar se é colaborador (opcional)
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    console.log("Fazendo requisição...");
    const resp = await fetch(endpoint, {
      method: "GET",
      headers: headers,
    });

    console.log("Status da resposta:", resp.status);
    console.log("Resposta OK?", resp.ok);

    const res = await resp.json();
    console.log("Resposta completa do servidor:", res);

    if (res.success && res.campanhas) {
      console.log("Número de campanhas encontradas:", res.campanhas.length);
      renderizarCampanhas(res.campanhas);
    } else {
      console.error("Erro ao buscar campanhas:", res.message);
      document.getElementById(
        "lista-campanhas"
      ).innerHTML = `<p>Erro ao carregar campanhas: ${
        res.message || "Erro desconhecido"
      }</p>`;
    }
  } catch (err) {
    console.error("ERRO NO CATCH:", err);
    document.getElementById(
      "lista-campanhas"
    ).innerHTML = `<p>Erro ao conectar com o servidor: ${err.message}</p>`;
  }
}

function renderizarCampanhas(campanhas) {
  console.log("Renderizando campanhas...");
  console.log("Campanhas recebidas:", campanhas);

  const listaCampanhas = document.getElementById("lista-campanhas");

  if (!listaCampanhas) {
    console.error("Elemento #lista-campanhas não encontrado!");
    return;
  }

  listaCampanhas.innerHTML = "";

  if (campanhas.length === 0) {
    listaCampanhas.innerHTML = "<p>Nenhuma campanha cadastrada no momento.</p>";
    return;
  }

  const token = localStorage.getItem("token");
  const tipoUsuario = localStorage.getItem("tipo_usuario");
  const ehColaborador = token && tipoUsuario === "colaborador";

  campanhas.forEach((camp, index) => {
    console.log(`Renderizando campanha ${index + 1}:`, camp);

    const article = document.createElement("article");
    article.className = "card-campanha";

    const dataInicio = new Date(camp.data_inicio).toLocaleDateString("pt-BR");
    const dataFim = new Date(camp.data_fim).toLocaleDateString("pt-BR");
    const percentual = Math.round(
      (camp.quantidade_atual_litros / camp.quantidade_meta_litros) * 100
    );

    article.innerHTML = `
      <h3>${camp.nome} ${camp.destaque ? "⭐" : ""}</h3>
      <p><strong>Descrição:</strong> ${camp.descricao}</p>
      <p><strong>Período:</strong> ${dataInicio} até ${dataFim}</p>
      <p><strong>Tipo Sanguíneo:</strong> ${camp.tipo_sanguineo_necessario}</p>
      <p><strong>Objetivo:</strong> ${camp.objetivo || "Não especificado"}</p>
      <p><strong>Meta:</strong> ${
        camp.quantidade_meta_litros
      }L | <strong>Atual:</strong> ${
      camp.quantidade_atual_litros
    }L (${percentual}%)</p>
      <p><strong>Status:</strong> ${camp.ativa ? "✓ Ativa" : "✗ Inativa"}</p>
      ${
        camp.nome_hemocentro
          ? `<p><strong>Hemocentro:</strong> ${camp.nome_hemocentro} - ${camp.cidade}/${camp.estado}</p>`
          : ""
      }
      <progress value="${camp.quantidade_atual_litros}" max="${
      camp.quantidade_meta_litros
    }"></progress>
      ${
        ehColaborador
          ? `<button class="btn-editar" onclick="abrirModalEdicao(${camp.id_campanha})">✏️ Editar Campanha</button>`
          : ""
      }
    `;

    listaCampanhas.appendChild(article);
  });

  console.log("Campanhas renderizadas com sucesso!");
}

function abrirModalEdicao(idCampanha) {
  console.log("Abrindo modal para editar campanha ID:", idCampanha);

  // buscar dados da campanha
  fetch(`/api/campanhas/${idCampanha}`)
    .then((resp) => resp.json())
    .then((res) => {
      if (res.success && res.campanha) {
        preencherModalEdicao(res.campanha);
      } else {
        alert("Erro ao carregar dados da campanha: " + res.message);
      }
    })
    .catch((err) => {
      console.error(err);
      alert("Erro ao conectar com o servidor.");
    });
}

function preencherModalEdicao(campanha) {
  // criar modal dinamicamente se não existir
  let modal = document.getElementById("modal-edicao-campanha");

  if (!modal) {
    modal = document.createElement("section");
    modal.id = "modal-edicao-campanha";
    modal.className = "modal";
    modal.innerHTML = `
      <article class="modal-conteudo">
        <span class="fechar" onclick="fecharModalEdicao()">&times;</span>
        <h2>Editar Campanha</h2>
        <form id="form-edicao-campanha">
          <input type="hidden" id="edit-id-campanha">
          
          <label for="edit-nome">Nome da Campanha:</label>
          <input type="text" id="edit-nome" required>
          
          <label for="edit-descricao">Descrição:</label>
          <textarea id="edit-descricao" required rows="4"></textarea>
          
          <label for="edit-data-fim">Data de Término:</label>
          <input type="date" id="edit-data-fim" required>
          
          <label for="edit-tipo-sanguineo">Tipo Sanguíneo:</label>
          <select id="edit-tipo-sanguineo" required>
            <option value="A+">A+</option>
            <option value="A-">A-</option>
            <option value="B+">B+</option>
            <option value="B-">B-</option>
            <option value="AB+">AB+</option>
            <option value="AB-">AB-</option>
            <option value="O+">O+</option>
            <option value="O-">O-</option>
          </select>
          
          <label for="edit-meta-litros">Meta (litros):</label>
          <input type="number" id="edit-meta-litros" required min="1">
          
          <label for="edit-atual-litros">Quantidade Atual (litros):</label>
          <input type="number" id="edit-atual-litros" required min="0">
          
          <label for="edit-objetivo">Objetivo:</label>
          <textarea id="edit-objetivo" required rows="3"></textarea>
          
          <label>
            <input type="checkbox" id="edit-ativa">
            Campanha Ativa
          </label>
          
          <label>
            <input type="checkbox" id="edit-destaque">
            Campanha em Destaque
          </label>
          
          <button type="submit" class="btn-salvar">💾 Salvar Alterações</button>
          <button type="button" class="btn-cancelar" onclick="fecharModalEdicao()">❌ Cancelar</button>
        </form>
      </article>
    `;
    document.body.appendChild(modal);
  }

  // preencher campos com dados da campanha
  document.getElementById("edit-id-campanha").value = campanha.id_campanha;
  document.getElementById("edit-nome").value = campanha.nome;
  document.getElementById("edit-descricao").value = campanha.descricao;
  document.getElementById("edit-data-fim").value = campanha.data_fim;
  document.getElementById("edit-tipo-sanguineo").value =
    campanha.tipo_sanguineo_necessario;
  document.getElementById("edit-meta-litros").value =
    campanha.quantidade_meta_litros;
  document.getElementById("edit-atual-litros").value =
    campanha.quantidade_atual_litros;
  document.getElementById("edit-objetivo").value = campanha.objetivo || "";
  document.getElementById("edit-ativa").checked = campanha.ativa;
  document.getElementById("edit-destaque").checked = campanha.destaque || false;

  // mostrar modal
  modal.style.display = "flex";

  // adicionar listener do form se ainda não tiver
  const form = document.getElementById("form-edicao-campanha");
  form.onsubmit = salvarEdicaoCampanha;
}

function fecharModalEdicao() {
  const modal = document.getElementById("modal-edicao-campanha");
  if (modal) {
    modal.style.display = "none";
  }
}

async function salvarEdicaoCampanha(e) {
  e.preventDefault();

  const idCampanha = document.getElementById("edit-id-campanha").value;
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Você precisa estar logado como colaborador para editar campanhas.");
    return;
  }

  const dadosAtualizados = {
    nome: document.getElementById("edit-nome").value.trim(),
    descricao: document.getElementById("edit-descricao").value.trim(),
    data_fim: document.getElementById("edit-data-fim").value,
    tipo_sanguineo_necessario: document
      .getElementById("edit-tipo-sanguineo")
      .value.trim(),
    quantidade_meta_litros: Number(
      document.getElementById("edit-meta-litros").value
    ),
    quantidade_atual_litros: Number(
      document.getElementById("edit-atual-litros").value
    ),
    objetivo: document.getElementById("edit-objetivo").value.trim(),
    ativa: document.getElementById("edit-ativa").checked,
    destaque: document.getElementById("edit-destaque").checked,
  };

  console.log("Enviando atualização:", dadosAtualizados);

  try {
    const resp = await fetch(`/api/campanhas/${idCampanha}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(dadosAtualizados),
    });

    const res = await resp.json();

    if (res.success) {
      alert("✅ Campanha atualizada com sucesso!");
      fecharModalEdicao();
      buscarCampanhas(); // recarrega a lista
    } else {
      alert("❌ Erro ao atualizar: " + res.message);
    }
  } catch (err) {
    console.error(err);
    alert("Erro ao conectar com o servidor.");
  }
}

// fechar modal ao clicar fora dele
window.onclick = function (event) {
  const modal = document.getElementById("modal-edicao-campanha");
  if (modal && event.target === modal) {
    fecharModalEdicao();
  }
};

// carrega as campanhas ao abrir a página
console.log("Script carregado. Verificando se #lista-campanhas existe...");
if (document.getElementById("lista-campanhas")) {
  console.log("Elemento encontrado! Chamando buscarCampanhas()...");
  buscarCampanhas();
} else {
  console.log("Elemento #lista-campanhas NÃO encontrado na página.");
}
