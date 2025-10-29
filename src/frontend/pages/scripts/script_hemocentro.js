// Dados FALSOS de hemocentros 
const hemocentrosData = [
  {
    map_html:'<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d8741.167625691707!2d-47.07764876421763!3d-22.905688070253873!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x94c8c8ba62ad2081%3A0x8aa377b2aaaa82c1!2sHospital%20Vera%20Cruz!5e0!3m2!1spt-BR!2sbr!4v1761777499971!5m2!1spt-BR!2sbr" width="100%" height="100%" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>' ,
    nome: "HOSPITAL VERA CRUZ",
    localizacao: "Avenida Guilherme Campos, 500, Jd. Sta. Genebra, Campinas, SP, Brasil",
    estoque: {
      "O+": { bolsas: 85, meta: 100 },
      "O-": { bolsas: 45, meta: 80 }, 
      "A+": { bolsas: 85, meta: 100 },
      "A-": { bolsas: 85, meta: 100 },
      "AB+": { bolsas: 85, meta: 100 },
      "AB-": { bolsas: 85, meta: 100 },
      "B+": { bolsas: 85, meta: 100 },
      "B-": { bolsas: 85, meta: 100 },
    }
  },
  {
    map_html:'<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3677.3381426000074!2d-47.067064588266504!3d-22.826975929225156!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x94c8c6a5cf964eab%3A0x7537896ba851b164!2sHospital%20de%20Cl%C3%ADnicas%20da%20UNICAMP%20-%20Fonoaudiologia!5e0!3m2!1spt-BR!2sbr!4v1761774848560!5m2!1spt-BR!2sbr" width="100%" height="100%" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>',
    nome: "HOSPITAL UNICAMP",
    localizacao: "Rua Vital Brasil, 251 - Cidade Universitária, Campinas, SP, Brasil",
    estoque: {
      "O+": { bolsas: 60, meta: 100 }, 
      "O-": { bolsas: 30, meta: 80 }, 
      "A+": { bolsas: 90, meta: 100 },
      "A-": { bolsas: 50, meta: 100 },
      "AB+": { bolsas: 70, meta: 100 },
      "AB-": { bolsas: 95, meta: 100 },
      "B+": { bolsas: 75, meta: 100 },
      "B-": { bolsas: 60, meta: 100 },
    }
  },
  {
    map_html:'<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d919.7152021420259!2d-47.15087616985404!3d-22.770546281895285!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x94c8bfe3b66efc1b%3A0x7b55b1389d6f9cec!2sHospital%20Municipal%20de%20Paul%C3%ADnia!5e0!3m2!1spt-BR!2sbr!4v1761777454254!5m2!1spt-BR!2sbr" width="100%" height="100%" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>',
    nome: "HOSPITAL PAULÍNIA",

    localizacao: "Avenida José Paulino, 100, Paulínia, SP",
    estoque: {
      "O+": { bolsas: 95, meta: 100 },
      "O-": { bolsas: 75, meta: 80 },
      "A+": { bolsas: 40, meta: 100 }, 
      "A-": { bolsas: 50, meta: 100 }, 
      "AB+": { bolsas: 80, meta: 100 },
      "AB-": { bolsas: 70, meta: 100 },
      "B+": { bolsas: 90, meta: 100 },
      "B-": { bolsas: 55, meta: 100 },
    }
  }
];

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
  const grid = document.getElementById('estoque-grid');
  grid.innerHTML = ''; 

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

function mostrarDetalhes(index) {
  const hemocentro = hemocentrosData[index];

  document.getElementById('detalhe-nome').textContent = hemocentro.nome;
  document.getElementById('detalhe-localizacao').textContent = hemocentro.localizacao;
  const mapaContainer = document.getElementById('mapa-container-js'); 
  mapaContainer.innerHTML = hemocentro.map_html || '<p>Mapa não disponível.</p>';
 
  

  renderizarEstoque(hemocentro.estoque);

  document.getElementById('lista-view').style.display = 'none';
  document.getElementById('detalhe-view').classList.add('ativo');
  
  window.scrollTo(0, 0); 
}

function mostrarLista() {
  document.getElementById('lista-view').style.display = 'flex';
  document.getElementById('detalhe-view').classList.remove('ativo');
  window.scrollTo(0, 0); 
}

document.addEventListener('DOMContentLoaded', () => {
    // Ouvintes para os botões "Visitar"
    const botoesVisitar = document.querySelectorAll('.btn-visitar');

    botoesVisitar.forEach(botao => {
        botao.addEventListener('click', (evento) => {
            // Pega o índice do atributo 'data-index' definido no HTML
            const index = evento.target.getAttribute('data-index');
            // Converte para número e chama a função
            mostrarDetalhes(Number(index)); 
        });
    });

    // Ouvinte para o botão "Voltar"
    const botaoVoltar = document.getElementById('btn-voltar');
    if (botaoVoltar) {
        botaoVoltar.addEventListener('click', mostrarLista);
    }
});
