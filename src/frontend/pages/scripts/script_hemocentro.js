// Dados FALSOS de hemocentros (serão substituídos pelo banco de dados)
const hemocentrosData = [
  {
    nome: "HOSPITAL VERA CRUZ",
    localizacao: "Avenida Guilherme Campos, 500, Jd. Sta. Genebra, Campinas, SP, Brasil",
    estoque: {
      "O+": { bolsas: 85, meta: 100 },
      "O-": { bolsas: 45, meta: 80 }, // Baixo
      "A+": { bolsas: 85, meta: 100 },
      "A-": { bolsas: 85, meta: 100 },
      "AB+": { bolsas: 85, meta: 100 },
      "AB-": { bolsas: 85, meta: 100 },
      "B+": { bolsas: 85, meta: 100 },
      "B-": { bolsas: 85, meta: 100 },
    }
  },
  {
    nome: "HOSPITAL UNICAMP",
    localizacao: "Rua Vital Brasil, 251 - Cidade Universitária, Campinas, SP, Brasil",
    estoque: {
      "O+": { bolsas: 60, meta: 100 }, // Baixo
      "O-": { bolsas: 30, meta: 80 }, // Baixo
      "A+": { bolsas: 90, meta: 100 },
      "A-": { bolsas: 50, meta: 100 },
      "AB+": { bolsas: 70, meta: 100 },
      "AB-": { bolsas: 95, meta: 100 },
      "B+": { bolsas: 75, meta: 100 },
      "B-": { bolsas: 60, meta: 100 },
    }
  },
  {
    nome: "HOSPITAL PAULÍNIA",
    localizacao: "Avenida José Paulino, 100, Paulínia, SP",
    estoque: {
      "O+": { bolsas: 95, meta: 100 },
      "O-": { bolsas: 75, meta: 80 },
      "A+": { bolsas: 40, meta: 100 }, // Baixo
      "A-": { bolsas: 50, meta: 100 }, // Baixo
      "AB+": { bolsas: 80, meta: 100 },
      "AB-": { bolsas: 70, meta: 100 },
      "B+": { bolsas: 90, meta: 100 },
      "B-": { bolsas: 55, meta: 100 },
    }
  }
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
  const grid = document.getElementById('estoque-grid');
  grid.innerHTML = ''; // Limpa o conteúdo anterior

  for (const tipo in estoqueData) {
    const data = estoqueData[tipo];
    const { bolsas, meta } = data;
    const { porcentagem, statusTexto, statusClasse } = calcularStatus(bolsas, meta);

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
  document.getElementById('detalhe-nome').textContent = hemocentro.nome;
  document.getElementById('detalhe-localizacao').textContent = hemocentro.localizacao;

  // 2. Renderiza os cartões de estoque na coluna direita
  renderizarEstoque(hemocentro.estoque);

  // 3. Altera a visibilidade das telas
  document.getElementById('lista-view').style.display = 'none';
  document.getElementById('detalhe-view').classList.add('ativo');
  
  // Rola para o topo da página
  window.scrollTo(0, 0); 
}

// Função para mostrar a lista (Botão "Voltar")
function mostrarLista() {
  document.getElementById('lista-view').style.display = 'flex';
  document.getElementById('detalhe-view').classList.remove('ativo');
  window.scrollTo(0, 0); 
}