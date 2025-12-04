document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("perfil")) {
    carregarDadosPerfil();
  }
  const btnSair = document.getElementById("saida");
  if (btnSair) {
    btnSair.addEventListener("click", (e) => {
      e.preventDefault();
      try {
        localStorage.removeItem("token");
        localStorage.removeItem("tipo_usuario");
        localStorage.removeItem("nome_usuario");
        localStorage.removeItem("email_usuario");
        localStorage.clear();
      } catch (err) {
        console.warn("Erro ao limpar storage:", err);
      }
      window.location.href = "/";
    });
  }
});

async function carregarDadosPerfil() {
  try {
    console.log("Iniciando busca de perfil...");
    const token = localStorage.getItem("token");
    if (!token) {
      console.warn("Sem token encontrado. Redirecionando...");
      window.location.href = "/login";
      return;
    }
    const resp = await fetch("/api/perfil", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    console.log("Passou da primeira api");
    if (!resp.ok) {
      console.error("Erro na resposta do servidor:", resp.status);
      if (resp.status === 401 || resp.status === 403) {
        alert("Sessão expirada. Faça login novamente.");
        window.location.href = "/login";
      }
      return;
    }

    const json = await resp.json();
    if (json.success) {
      const dados = json.usuario;
      console.log("Entrou no success de coleta de dados");
      const nomeUser = document.getElementById("campo-nome");
      if (nomeUser) nomeUser.textContent = dados.nome;
      const emailUser = document.getElementById("campo-email");
      if (emailUser) emailUser.textContent = dados.email;
      const tipoSangue = document.getElementById("tipo-sangue");
      if (tipoSangue) {
        tipoSangue.innerHTML = `<b>${
          dados.tipo_sanguineo || "Não informado"
        }</b>`;
      }
      const idUser = document.getElementById("id_user");
      if (idUser) {
        idUser.textContent = `ID de Usuário: ${dados.id_usuario}`;
      }
      if (dados.tipo_usuario === "doador" && dados.historico_doacoes) {
        renderizarEstatisticasDoacoes(dados.historico_doacoes.estatisticas);
        renderizarListaDoacoes(dados.historico_doacoes.doacoes);
        injetarFormularioPreferencias();
      }
    } else {
      console.error("Erro na lógica do back:", json.message);
    }
  } catch (err) {
    console.error("Erro técnico (fetch falhou):", err);
  }
}

// renderixar estatisticas
function renderizarEstatisticasDoacoes(stats) {
  const containerStats = document.getElementById("estatisticas-doacoes");
  if (!containerStats) {
    console.warn("Container 'estatisticas-doacoes' não encontrado no HTML");
    return;
  }
  let proximaDoacao = "Não há doações registradas";
  let statusDoacao = "";
  if (stats.proxima_doacao_permitida) {
    const dataProxima = new Date(stats.proxima_doacao_permitida);
    proximaDoacao = dataProxima.toLocaleDateString("pt-BR");
    if (stats.pode_doar_agora) {
      statusDoacao =
        '<span style="color: #c41e3a; font-weight: bold;">Você já pode doar!</span>';
    } else {
      statusDoacao =
        '<span style="color: #999; font-weight: bold;">Aguarde até a data permitida</span>';
    }
  }/**/
  containerStats.innerHTML = `
    <div class="stats-doacoes" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
      
      <div class="stat-card" style="background: darkred; color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; opacity: 0.9;">Total de Doações</div>
        <div style="font-size: 32px; font-weight: bold; margin: 10px 0;">${stats.total_doacoes}</div>
        <div style="font-size: 12px; opacity: 0.8;">Você é incrível!</div>
      </div>
      <div class="stat-card" style="background: #c41e3a; color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; opacity: 0.9;">Volume Doado</div>
        <div style="font-size: 32px; font-weight: bold; margin: 10px 0;">${stats.total_litros}L</div>
        <div style="font-size: 12px; opacity: 0.8;">${stats.total_ml}ml no total</div>
      </div>
      <div class="stat-card" style="background: #666; color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; opacity: 0.9;">Próxima Doação</div>
        <div style="font-size: 24px; font-weight: bold; margin: 10px 0;">${proximaDoacao}</div>
        <div style="font-size: 12px;">${statusDoacao}</div>
      </div>
    </div>
  `;
}

// lista de doações
function renderizarListaDoacoes(doacoes) {
  const containerLista = document.getElementById("lista-doacoes");
  if (!containerLista) {
    console.warn("Container 'lista-doacoes' não encontrado no HTML");
    return;
  }
  if (!doacoes || doacoes.length === 0) {
    containerLista.innerHTML = `
      <div style="text-align: center; padding: 40px; color: #666;">
        <p style="font-size: 18px;">Você ainda não tem doações registradas</p>
        <p style="font-size: 14px;">Faça seu agendamento e comece a salvar vidas!</p>
      </div>
    `;
    return;
  }
  let htmlDoacoes = `
    <div style="margin: 20px 0;">
      <h3 style="color: #c41e3a; margin-bottom: 15px;">Histórico de Doações</h3>
      <table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
        <thead>
          <tr style="background: #c41e3a; color: white;">
            <th style="padding: 12px; text-align: left;">Data</th>
            <th style="padding: 12px; text-align: left;">Tipo</th>
            <th style="padding: 12px; text-align: left;">Quantidade</th>
            <th style="padding: 12px; text-align: left;">Local</th>
            <th style="padding: 12px; text-align: left;">Observações</th>
          </tr>
        </thead>
        <tbody>
  `;
  doacoes.forEach((doacao, index) => {
    const dataDoacao = new Date(doacao.data_doacao).toLocaleDateString("pt-BR");
    const tipoDoacao = formatarTipoDoacao(doacao.tipo_doacao);
    const quantidade = `${doacao.quantidade_ml}ml`;
    const local =
      doacao.nome_hemocentro || `Hemocentro ID: ${doacao.id_hemocentro}`;
    const observacoes = doacao.observacoes || "-";
    const bgColor = index % 2 === 0 ? "#f9f9f9" : "white";
    htmlDoacoes += `
      <tr style="background: ${bgColor}; border-bottom: 1px solid #eee;">
        <td style="padding: 12px;">${dataDoacao}</td>
        <td style="padding: 12px;">${tipoDoacao}</td>
        <td style="padding: 12px; font-weight: bold; color: #c41e3a;">${quantidade}</td>
        <td style="padding: 12px;">${local}</td>
        <td style="padding: 12px; font-size: 12px; color: #666;">${observacoes}</td>
      </tr>
    `;
  });
  htmlDoacoes += `
        </tbody>
      </table>
    </div>
  `;
  containerLista.innerHTML = htmlDoacoes;
}

// formatar tipo de doação
function formatarTipoDoacao(tipo) {
  const tipos = {
    sangue_total: "Sangue Total",
    plaquetas: "Plaquetas",
    plasma: "Plasma",
    aferese: "Aférese",
  };
  return tipos[tipo] || tipo;
}

// gerenciar preferencias
function injetarFormularioPreferencias() {
  const containerPreferencias = document.getElementById(
    "formulario-preferencias"
  );
  if (!containerPreferencias) {
    console.warn("Container 'formulario-preferencias' não encontrado no HTML");
    return;
  }
  const diasSemana = [
    "segunda",
    "terca",
    "quarta",
    "quinta",
    "sexta",
    "sabado",
    "domingo",
  ];
  const periodosDia = ["manha", "tarde", "noite"];
  // HTML do formulário
  let htmlFormulario = `
    <form id="form-preferencias" style="max-width: 600px; margin: 20px 0;">
      
      <div style="margin-bottom: 25px;">
        <h3 style="color: #c41e3a; margin-bottom: 15px;">Dias da Semana Preferidos</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;">
  `;
  diasSemana.forEach((dia) => {
    const diaFormatado = dia.charAt(0).toUpperCase() + dia.slice(1);
    htmlFormulario += `
      <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 8px; border-radius: 6px; background: #f9f9f9; transition: background 0.2s;">
        <input type="checkbox" name="dias_preferencia" value="${dia}" style="cursor: pointer; width: 18px; height: 18px;" />
        <span>${diaFormatado}</span>
      </label>
    `;
  });
  htmlFormulario += `
        </div>
      </div>

      <div style="margin-bottom: 25px;">
        <h3 style="color: #c41e3a; margin-bottom: 15px;">Períodos Preferidos</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;">
  `;
  periodosDia.forEach((periodo) => {
    const periodoFormatado =
      periodo === "manha" ? "Manhã" : periodo === "tarde" ? "Tarde" : "Noite";
    htmlFormulario += `
      <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 8px; border-radius: 6px; background: #f9f9f9; transition: background 0.2s;">
        <input type="checkbox" name="periodos_preferencia" value="${periodo}" style="cursor: pointer; width: 18px; height: 18px;" />
        <span>${periodoFormatado}</span>
      </label>
    `;
  });
  htmlFormulario += `
        </div>
      </div>
      <div style="display: flex; gap: 12px; margin-top: 30px;">
        <button type="submit" class="btn-primario" style="flex: 1; padding: 12px; background: #c41e3a; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.3s;">
          Salvar Preferências
        </button>
        <button type="button" id="btn-carregar-prefs" style="flex: 1; padding: 12px; background: #666; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.3s;">
          Carregar Atuais
        </button>
      </div>
      <div id="mensagem-preferencias" style="margin-top: 15px; padding: 12px; border-radius: 6px; display: none; text-align: center; font-weight: bold;"></div>
    </form>
  `;
  containerPreferencias.innerHTML = htmlFormulario;
  const formPreferencias = document.getElementById("form-preferencias");
  const btnCarregarPrefs = document.getElementById("btn-carregar-prefs");
  formPreferencias.addEventListener("submit", salvarPreferencias);
  btnCarregarPrefs.addEventListener("click", carregarPreferenciasAtuais);
  carregarPreferenciasAtuais();
}

// pre seleciona preferencias
async function carregarPreferenciasAtuais() {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      console.warn("Sem token para carregar preferências");
      return;
    }
    const resp = await fetch("/api/minhas_preferencias", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    if (!resp.ok) {
      console.error("Erro ao carregar preferências:", resp.status);
      return;
    }
    const json = await resp.json();
    if (json.success && json.data) {
      const dados = json.data;
      if (dados.dias_preferencia && Array.isArray(dados.dias_preferencia)) {
        dados.dias_preferencia.forEach((dia) => {
          const checkbox = document.querySelector(
            `input[name="dias_preferencia"][value="${dia}"]`
          );
          if (checkbox) checkbox.checked = true;
        });
      }
      if (
        dados.periodos_preferencia &&
        Array.isArray(dados.periodos_preferencia)
      ) {
        dados.periodos_preferencia.forEach((periodo) => {
          const checkbox = document.querySelector(
            `input[name="periodos_preferencia"][value="${periodo}"]`
          );
          if (checkbox) checkbox.checked = true;
        });
      }
      console.log("Preferências carregadas:", dados);
    }
  } catch (err) {
    console.error("Erro ao carregar preferências:", err);
  }
}

// enviar preferências via fetch
async function salvarPreferencias(event) {
  event.preventDefault();
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Faça login para salvar suas preferências.");
      return;
    }
    const diasSelecionados = Array.from(
      document.querySelectorAll('input[name="dias_preferencia"]:checked')
    ).map((checkbox) => checkbox.value);
    const periodosSelecionados = Array.from(
      document.querySelectorAll('input[name="periodos_preferencia"]:checked')
    ).map((checkbox) => checkbox.value);
    if (diasSelecionados.length === 0) {
      mostrarMensagemPreferencias(
        "Selecione pelo menos um dia da semana",
        "error"
      );
      return;
    }
    if (periodosSelecionados.length === 0) {
      mostrarMensagemPreferencias(
        "Selecione pelo menos um período do dia",
        "error"
      );
      return;
    }
    const dados = {
      dias_preferencia: diasSelecionados,
      periodos_preferencia: periodosSelecionados,
    };
    console.log("Enviando preferências:", dados);
    const resp = await fetch("/api/minhas_preferencias", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(dados),
    });
    const json = await resp.json();
    if (json.success) {
      mostrarMensagemPreferencias(
        "Preferências salvas com sucesso!",
        "success"
      );
      console.log("Resposta do servidor:", json);
    } else {
      mostrarMensagemPreferencias(`Erro: ${json.message}`, "error");
      console.error("Erro do servidor:", json.message);
    }
  } catch (err) {
    mostrarMensagemPreferencias("Erro ao conectar com o servidor", "error");
    console.error("Erro técnico:", err);
  }
}

// mensagem de feedback
function mostrarMensagemPreferencias(mensagem, tipo) {
  const divMensagem = document.getElementById("mensagem-preferencias");
  if (!divMensagem) return;
  divMensagem.textContent = mensagem;
  divMensagem.style.display = "block";
  divMensagem.style.backgroundColor =
    tipo === "success" ? "#d4edda" : "#f8d7da";
  divMensagem.style.color = tipo === "success" ? "#155724" : "#721c24";
  divMensagem.style.border = `1px solid ${
    tipo === "success" ? "#c3e6cb" : "#f5c6cb"
  }`;

  // ocultar após 5 segundos
  setTimeout(() => {
    divMensagem.style.display = "none";
  }, 5000);
}

async function amostragemDePagina() {
  try {
    const token = localStorage.getItem("token");
    const listaContainer = document.getElementById("meus-agendamentos");
    console.log("Encontrou na Amostragem");
    if (!token) {
      alert("Faça login para ver seus agendamentos.");
      return;
    }
    const resp = await fetch("/api/perfil", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    console.warn("[perfil] amostragemDePagina: iniciando");
    const jsonPerfil = await resp.json();
    if (jsonPerfil.success) {
      console.log("Encontrou no sucesso");
      const dados = jsonPerfil.usuario;
      const tipoUser = dados.tipo_usuario;
      if (tipoUser === "doador") {
        console.log("Encontrou o doador");
        document
          .getElementById("parte-escondida-funcionario")
          .classList.add("esconda");
        const containerDoador = document.getElementById(
          "parte-escondida-doador"
        );
        if (containerDoador) containerDoador.classList.remove("esconda");
        const resp = await fetch("/api/meus-agendamentos?futuro=true", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });
        if (!resp.ok) {
          console.error("Erro na busca");
          if (listaContainer)
            listaContainer.innerHTML =
              "<tr><td colspan='4'>Erro ao carregar agendamentos.</td></tr>";
          return;
        }
        const json = await resp.json();
        if (listaContainer) listaContainer.innerHTML = "";
        if (json.success && json.agendamentos && json.agendamentos.length > 0) {
          json.agendamentos.forEach((agendamento) => {
            const dataObj = new Date(agendamento.data_hora);
            const dataFormatada = dataObj.toLocaleDateString("pt-BR");
            const horaFormatada = dataObj.toLocaleTimeString("pt-BR", {
              hour: '2-digit',
              minute: '2-digit'
            });
            const tipoDoacao = formatarTipoDoacao(agendamento.tipo_sangue_doado || 'sangue_total');
            const podeCancelar = agendamento.status === 'pendente' || agendamento.status === 'confirmado';
            const acaoHTML = podeCancelar 
              ? `<button 
                  onclick="cancelarAgendamentoDoador(${agendamento.id_agendamento})"
                  style="
                    padding: 8px 16px;
                    background: #FFD700;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: bold;
                    transition: background 0.3s;
                  "
                >
                  Cancelar
                </button>`
              : `<span style="color: #999; font-size: 12px;">Não disponível</span>`;

            const cardHTML = `
            <tr class="card-agendamento" style="border: 1px solid #ccc; padding: 15px; margin-bottom: 10px; border-radius: 8px;">
              <td data-label="Data">${dataFormatada}</td>
              <td data-label="Horário">${horaFormatada}</td>
              <td data-label="Doação">${tipoDoacao}</td>
              <td data-label="Ação">${acaoHTML}</td>
            </tr>
            `;
            if (listaContainer) listaContainer.innerHTML += cardHTML;
          });
        } else {
          if (listaContainer) {
            listaContainer.innerHTML = `
              <tr>
                <td colspan="4" style="text-align: center; padding: 20px;">
                  Você não tem agendamentos futuros.
                </td>
              </tr>
            `;
          }
        }
        
      } else {
        const ParteFunc = document.getElementById("parte-escondida-doador");
        if (ParteFunc) ParteFunc.classList.add("esconda");
        const containerFunc = document.getElementById(
          "parte-escondida-funcionario"
        );
        if (containerFunc) containerFunc.classList.remove("esconda");
        carregarAgendamentosColaborador();
      }
    }
  } catch (err) {
    console.error("Erro técnico:", err);
  }
}

// gerenciamento de agendamentos
let filtroAtualAgendamentos = 'pendente';
// carregar agendamentos do hemocentro
async function carregarAgendamentosColaborador(status = null) {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Faça login para ver os agendamentos.");
      return;
    }
    const statusQuery = status ? `?status=${status}` : '';
    const resp = await fetch(`/api/agendamentos${statusQuery}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    if (!resp.ok) {
      console.error("Erro ao buscar agendamentos:", resp.status);
      mostrarErroAgendamentos("Erro ao carregar agendamentos");
      return;
    }
    const json = await resp.json();
    if (json.success && json.agendamentos) {
      renderizarAgendamentosColaborador(json.agendamentos);
    } else {
      renderizarAgendamentosColaborador([]);
    }
  } catch (err) {
    console.error("Erro ao carregar agendamentos:", err);
    mostrarErroAgendamentos("Erro de conexão com o servidor");
  }
}

// renderizar tabela de agendamentos
function renderizarAgendamentosColaborador(agendamentos) {
  const tbody = document.getElementById("lista-agendamentos-colaborador");
  if (!tbody) {
    console.warn("Tbody 'lista-agendamentos-colaborador' não encontrado");
    return;
  }
  if (agendamentos.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; padding: 40px; color: #666;">
          Nenhum agendamento encontrado para este filtro.
        </td>
      </tr>
    `;
    return;
  }
  let htmlLinhas = '';
  agendamentos.forEach((agendamento) => {
    const dataObj = new Date(agendamento.data_hora);
    const dataFormatada = dataObj.toLocaleDateString("pt-BR");
    const horaFormatada = dataObj.toLocaleTimeString("pt-BR", {
      hour: '2-digit',
      minute: '2-digit'
    });
    const tipoDoacao = formatarTipoDoacao(agendamento.tipo_sangue_doado || 'sangue_total');
    const nomeDoador = agendamento.nome_usuario || 'Usuário não identificado';
    const statusFormatado = formatarStatusAgendamento(agendamento.status);
    // determinar quais ações exibir baseado no status
    const acoesHTML = gerarBotoesAcao(agendamento);
    htmlLinhas += `
      <tr style="border-bottom: 1px solid #eee;">
        <td style="padding: 12px;">#${agendamento.id_agendamento}</td>
        <td style="padding: 12px;">${nomeDoador}</td>
        <td style="padding: 12px;">${dataFormatada}</td>
        <td style="padding: 12px;">${horaFormatada}</td>
        <td style="padding: 12px;">${tipoDoacao}</td>
        <td style="padding: 12px;">${statusFormatado}</td>
        <td style="padding: 12px;">
          ${acoesHTML}
        </td>
      </tr>
    `;
  });
  tbody.innerHTML = htmlLinhas;
}

function formatarStatusAgendamento(status) {
  const statusMap = {
    'pendente': { texto: 'Pendente', cor: '#ffc107' },
    'confirmado': { texto: 'Confirmado', cor: '#17a2b8' },
    'realizado': { texto: 'Realizado', cor: '#28a745' },
    'cancelado': { texto: 'Cancelado', cor: '#6c757d' },
    'nao_compareceu': { texto: 'Não Compareceu', cor: '#dc3545' }
  };
  const info = statusMap[status] || { texto: status, cor: '#666' };
  return `<span style="
    background: ${info.cor};
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
  ">${info.texto}</span>`;
}

// botões de ação baseado no status
function gerarBotoesAcao(agendamento) {
  const id = agendamento.id_agendamento;
  const status = agendamento.status;
  let botoes = '';
  if (status === 'pendente' || status === 'confirmado') {
    botoes = `
      <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        <button 
          onclick="marcarComoRealizado(${id})"
          style="
            padding: 6px 12px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            transition: background 0.3s;
          "
          onmouseover="this.style.background='#218838'"
          onmouseout="this.style.background='#28a745'"
        >
          ✓ Realizado
        </button>
        <button 
          onclick="marcarComoNaoCompareceu(${id})"
          style="
            padding: 6px 12px;
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            transition: background 0.3s;
          "
          onmouseover="this.style.background='#c82333'"
          onmouseout="this.style.background='#dc3545'"
        >
          ✗ Não Compareceu
        </button>
      </div>
    `;
  } else if (status === 'realizado' || status === 'nao_compareceu' || status === 'cancelado') {
    botoes = `<span style="color: #999; font-size: 12px;">Sem ações disponíveis</span>`;
  }
  return botoes;
}

// marcar agendamento como realizado
async function marcarComoRealizado(idAgendamento) {
  if (!confirm('Confirmar que a doação foi realizada?')) {
    return;
  }
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Faça login para realizar esta ação.");
      return;
    }
    const resp = await fetch(`/api/agendamentos/${idAgendamento}/realizar`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const json = await resp.json();
    if (json.success) {
      mostrarMensagemAcaoAgendamento("Doação marcada como realizada!", "success");
      setTimeout(() => {
        carregarAgendamentosColaborador(filtroAtualAgendamentos === 'todos' ? null : filtroAtualAgendamentos);
      }, 1000);
    } else {
      mostrarMensagemAcaoAgendamento(`Erro: ${json.message}`, "error");
    }
  } catch (err) {
    console.error("Erro ao marcar como realizado:", err);
    mostrarMensagemAcaoAgendamento("Erro ao conectar com o servidor", "error");
  }
}

// agendamento como não compareceu
async function marcarComoNaoCompareceu(idAgendamento) {
  if (!confirm('Confirmar que o doador não compareceu?')) {
    return;
  }
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Faça login para realizar esta ação.");
      return;
    }
    const resp = await fetch(`/api/agendamentos/${idAgendamento}/nao-compareceu`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const json = await resp.json();
    if (json.success) {
      mostrarMensagemAcaoAgendamento("Agendamento marcado como não compareceu", "success");
      setTimeout(() => {
        carregarAgendamentosColaborador(filtroAtualAgendamentos === 'todos' ? null : filtroAtualAgendamentos);
      }, 1000);
    } else {
      mostrarMensagemAcaoAgendamento(`Erro: ${json.message}`, "error");
    }
  } catch (err) {
    console.error("Erro ao marcar como não compareceu:", err);
    mostrarMensagemAcaoAgendamento("Erro ao conectar com o servidor", "error");
  }
}

// filtrar agendamentos por status
function filtrarAgendamentos(status) {
  document.querySelectorAll('.btn-filtro').forEach(btn => {
    btn.classList.remove('btn-filtro-ativo');
  });
  if (status === 'todos') {
    document.getElementById('filtro-todos').classList.add('btn-filtro-ativo');
    filtroAtualAgendamentos = 'todos';
    carregarAgendamentosColaborador(null);
  } else if (status === 'pendente') {
    document.getElementById('filtro-pendentes').classList.add('btn-filtro-ativo');
    filtroAtualAgendamentos = 'pendente';
    carregarAgendamentosColaborador('pendente');
  } else if (status === 'confirmado') {
    document.getElementById('filtro-confirmados').classList.add('btn-filtro-ativo');
    filtroAtualAgendamentos = 'confirmado';
    carregarAgendamentosColaborador('confirmado');
  } else if (status === 'realizado') {
    document.getElementById('filtro-realizados').classList.add('btn-filtro-ativo');
    filtroAtualAgendamentos = 'realizado';
    carregarAgendamentosColaborador('realizado');
  }
}

// mensagem de feedback nas ações
function mostrarMensagemAcaoAgendamento(mensagem, tipo) {
  const divMensagem = document.getElementById("mensagem-agendamento-acao");
  if (!divMensagem) return;
  divMensagem.textContent = mensagem;
  divMensagem.style.display = "block";
  divMensagem.style.backgroundColor = tipo === "success" ? "#d4edda" : "#f8d7da";
  divMensagem.style.color = tipo === "success" ? "#155724" : "#721c24";
  divMensagem.style.border = `1px solid ${tipo === "success" ? "#c3e6cb" : "#f5c6cb"}`;
  setTimeout(() => {
    divMensagem.style.display = "none";
  }, 5000);
}

// erro ao carregar agendamentos
function mostrarErroAgendamentos(mensagem) {
  const tbody = document.getElementById("lista-agendamentos-colaborador");
  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; padding: 40px; color: #dc3545;">
          ${mensagem}
        </td>
      </tr>
    `;
  }
}

if (document.getElementById("parte-escondida-funcionario")) {
  const nomeCampanha = document.getElementById("nome-campanha");
  const descricao = document.getElementById("descricao");
  const tipoNecessario = document.getElementById("tipo-sanguineo-necessario");
  const qntMeta = document.getElementById("quantidade-meta-litros");
  const objetivo = document.getElementById("objetivo");
  const inicio = document.getElementById("data-inicio");
  const fim = document.getElementById("data-fim");
  const cadastroCampanha = document.getElementById("campanha");
  if (cadastroCampanha) {
    cadastroCampanha.addEventListener("submit", async (event) => {
      event.preventDefault();
      const token = localStorage.getItem("token");
      const dados = {
        nome: nomeCampanha.value.trim(),
        descricao: descricao.value.trim(),
        data_inicio: inicio.value,
        data_fim: fim.value,
        tipo_sanguineo_necessario: tipoNecessario.value,
        quantidade_meta_litros: qntMeta.value,
        objetivo: objetivo.value.trim(),
      };
      try {
        const resp = await fetch("/api/cadastrar_campanha", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(dados),
        });
        const res = await resp.json();
        const hint = document.getElementById("hint-aviso");
        if (res.success) {
          hint.style.color = "#c41e3a";
          hint.textContent = "Campanha cadastrado!";
          window.location.href = "/perfil";
        } else {
          hint.style.color = "red";
          hint.textContent = "Não foi possível cadastrar sua Campanha.";
        }
      } catch (err) {
        console.error("Erro de cadastro:", err);
        alert("Erro de conexão com o servidor.");
      }
    });
  }
}

// editar dados da conta
function abrirModalEditarConta(usuarioDados) {
  const modalAntigo = document.getElementById("modal-editar-conta");
  if (modalAntigo) modalAntigo.remove();
  const modal = document.createElement("section");
  modal.id = "modal-editar-conta";
  modal.className = "modal-overlay";
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  `;
  const tipoSanguineoField =
    usuarioDados.tipo_usuario === "doador"
      ? `
      <div class="form-row">
        <label for="edit-tipo-sanguineo">Tipo Sanguíneo</label>
        <select id="edit-tipo-sanguineo" class="input-select">
          <option value="">Não informado</option>
          <option value="O+">O+</option>
          <option value="O-">O-</option>
          <option value="A+">A+</option>
          <option value="A-">A-</option>
          <option value="B+">B+</option>
          <option value="B-">B-</option>
          <option value="AB+">AB+</option>
          <option value="AB-">AB-</option>
        </select>
      </div>
    `
      : "";
  modal.innerHTML = `
    <article class="modal-content" style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); max-width: 500px; width: 90%; max-height: 90vh; overflow-y: auto;">
      <header class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #c41e3a; padding-bottom: 15px;">
        <h2 style="color: #c41e3a; margin: 0;">Editar Conta</h2>
        <button class="btn-fechar" style="background: none; border: none; font-size: 28px; cursor: pointer; color: #999;">X</button>
      </header>
      <form id="form-editar-conta" class="form-grid" style="display: grid; gap: 20px;">
        <div class="form-row">
          <label for="edit-nome">Nome Completo</label>
          <input 
            type="text" 
            id="edit-nome" 
            class="input-text" 
            value="${usuarioDados.nome}" 
            placeholder="Digite seu nome"
            style="padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px;"
          />
        </div>
        <div class="form-row">
          <label for="edit-telefone">Telefone</label>
          <input 
            type="tel" 
            id="edit-telefone" 
            class="input-text" 
            value="${usuarioDados.telefone || ""}" 
            placeholder="(XX) XXXXX-XXXX"
            style="padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px;"
          />
        </div>
        ${tipoSanguineoField}
        <div id="mensagem-edicao" style="margin-top: 15px; padding: 12px; border-radius: 6px; display: none; text-align: center; font-weight: bold;"></div>
        <div style="display: flex; gap: 12px; margin-top: 25px;">
          <button type="submit" class="btn-salvar" style="flex: 1; padding: 12px; background: #c41e3a; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.3s;">
            Salvar Alterações
          </button>
          <button type="button" class="btn-cancelar" style="flex: 1; padding: 12px; background: #999; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">
            Cancelar
          </button>
        </div>
      </form>
    </article>
  `;
  document.body.appendChild(modal);
  modal
    .querySelector(".btn-fechar")
    .addEventListener("click", () => modal.remove());
  modal
    .querySelector(".btn-cancelar")
    .addEventListener("click", () => modal.remove());
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.remove();
  });
  document
    .getElementById("form-editar-conta")
    .addEventListener("submit", salvarAlteracoesPerfil);
  if (usuarioDados.tipo_usuario === "doador" && usuarioDados.tipo_sanguineo) {
    document.getElementById("edit-tipo-sanguineo").value =
      usuarioDados.tipo_sanguineo;
  }
}

// slavar alterações do perfil via fetch
async function salvarAlteracoesPerfil(event) {
  event.preventDefault();
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Faça login para editar sua conta.");
      return;
    }
    const nome = document.getElementById("edit-nome").value.trim();
    const telefone = document.getElementById("edit-telefone").value.trim();
    const tipoSanguineoField = document.getElementById("edit-tipo-sanguineo");
    const tipoSanguineo = tipoSanguineoField
      ? tipoSanguineoField.value.trim()
      : null;
    if (!nome || nome.length < 3) {
      mostrarMensagemEdicao("Nome deve ter no mínimo 3 caracteres", "error");
      return;
    }
    if (nome.length > 200) {
      mostrarMensagemEdicao(
        "Nome muito longo (máximo 200 caracteres)",
        "error"
      );
      return;
    }
    const dados = {};
    if (nome) dados.nome = nome;
    if (telefone) dados.telefone = telefone;
    if (tipoSanguineoField && tipoSanguineo)
      dados.tipo_sanguineo = tipoSanguineo;
    if (Object.keys(dados).length === 0) {
      mostrarMensagemEdicao("Nenhuma alteração para salvar", "error");
      return;
    }
    console.log("Enviando alterações:", dados);
    const resp = await fetch("/api/perfil", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(dados),
    });
    const json = await resp.json();
    if (json.success) {
      mostrarMensagemEdicao("Perfil atualizado com sucesso!", "success");
      console.log("Resposta do servidor:", json);
      setTimeout(() => {
        window.location.href = "/perfil";
      }, 1500);
    } else {
      mostrarMensagemEdicao(`Erro: ${json.message}`, "error");
      console.error("Erro do servidor:", json.message);
    }
  } catch (err) {
    mostrarMensagemEdicao("Erro ao conectar com o servidor", "error");
    console.error("Erro técnico:", err);
  }
}

//mensagem de feedback na edição
function mostrarMensagemEdicao(mensagem, tipo) {
  const divMensagem = document.getElementById("mensagem-edicao");
  if (!divMensagem) return;
  divMensagem.textContent = mensagem;
  divMensagem.style.display = "block";
  divMensagem.style.backgroundColor =
    tipo === "success" ? "#d4edda" : "#f8d7da";
  divMensagem.style.color = tipo === "success" ? "#155724" : "#721c24";
  divMensagem.style.border = `1px solid ${
    tipo === "success" ? "#c3e6cb" : "#f5c6cb"
  }`;
  if (tipo !== "success") {
    setTimeout(() => {
      divMensagem.style.display = "none";
    }, 5000);
  }
}
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("meus-agendamentos")) {
    amostragemDePagina();
  }

  // botão "Editar Conta"
  const btnEditarConta = document.getElementById("btn-editar-conta");
  if (btnEditarConta) {
    btnEditarConta.addEventListener("click", async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          alert("Faça login para editar sua conta.");
          return;
        }
        const resp = await fetch("/api/perfil", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });
        if (!resp.ok) {
          alert("Erro ao carregar dados da conta.");
          return;
        }
        const json = await resp.json();
        if (json.success && json.usuario) {
          abrirModalEditarConta(json.usuario);
        } else {
          alert("Erro ao carregare dados do usuário.");
        }
      } catch (err) {
        console.error("Erro ao carregar dados:", err);
        alert("Erro ao conectar com o servidor.");
      }
    });
  }
});

// botão "Agendar Doação" com último hemocentro
document.addEventListener("DOMContentLoaded", () => {
  const btnAgendarDoacao = document.getElementById("btn-agendar-doacao");
  if (btnAgendarDoacao) {
    btnAgendarDoacao.addEventListener("click", async (e) => {
      e.preventDefault();
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          alert("Faça login para agendar uma doação.");
          window.location.href = "/login";
          return;
        }
        const resp = await fetch("/api/perfil", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });
        if (!resp.ok) {
          alert("Erro ao carregar dados. Tente novamente.");
          return;
        }
        const json = await resp.json();
        if (json.success && json.usuario) {
          const historico = json.usuario.historico_doacoes?.doacoes;
          if (historico && historico.length > 0) {
            const ultimaDoacao = historico[0];
            const idHemocentro = ultimaDoacao.id_hemocentro;
            const nomeHemocentro = ultimaDoacao.nome_hemocentro || "Hemocentro";
            window.location.href = `/agendamento?id_hemocentro=${idHemocentro}&nome_hemocentro=${encodeURIComponent(nomeHemocentro)}`;
          } else {
            alert("Você ainda não tem doações registradas. Selecione um hemocentro na próxima tela.");
            window.location.href = "/agendamento";
          }
        }
      } catch (err) {
        console.error("Erro ao buscar histórico:", err);
        window.location.href = "/agendamento";
      }
    });
  }
});

async function cancelarAgendamentoDoador(idAgendamento) {
  if (!confirm('Tem certeza que deseja cancelar este agendamento?')) {
    return;
  }
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Faça login para cancelar o agendamento.");
      return;
    }
    const resp = await fetch(`/api/agendamentos/${idAgendamento}`, {
      method: "Delete",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const json = await resp.json();
    if (json.success) {
      alert("Agendamento cancelado com sucesso!");
      window.location.reload();
    } else {
      alert(`Erro ao cancelar: ${json.message}`);
    }
  } catch (err) {
    console.error("Erro ao cancelar agendamento:", err);
    alert("Erro ao conectar com o servidor");
  }
}
