if (!localStorage.getItem("token")) {
  console.warn("Sem token — bloqueando horários.");
} else {
  let horariosTemp = [];
  const DIAS_SEMANA_NOMES = [
    'Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira',
    'Quinta-feira', 'Sexta-feira', 'Sábado'
  ];

  const horarioFuncionamento = document.getElementById("horarioFuncionamento");
  const dFuncionamento = document.getElementById("diaFuncionamento");
  const hAbertura = document.getElementById("horaAbertura");
  const hFechamento = document.getElementById("horaFechamento");
  const observacao = document.getElementById("observacao");
  const aviso = document.getElementById("aviso-horario");
  const container = document.getElementById("horarios-container");
  const btnAdicionar = document.getElementById("btn-adicionar-horario");
  const vDia = (v) => v.trim().length > 0;
  const vHora = (v) => /^\d{2}:\d{2}$/.test(v.trim());
  const compararHoras = (inicio, fim) => {
    const [h1, m1] = inicio.split(":").map(Number);
    const [h2, m2] = fim.split(":").map(Number);
    return h1 < h2 || (h1 === h2 && m1 < m2);
  };

  function validarCampos() {
    const okDia = vDia(dFuncionamento.value);
    const okAbertura = vHora(hAbertura.value);
    const okFechado = vHora(hFechamento.value);
    const ordem = okAbertura && okFechado && compararHoras(hAbertura.value, hFechamento.value);
    dFuncionamento.classList.toggle("erro", !okDia);
    hAbertura.classList.toggle("erro", !okAbertura);
    hFechamento.classList.toggle("erro", !okFechado || !ordem);
    return okDia && okAbertura && okFechado && ordem;
  }

  function renderizarHorariosTemp() {
    if (horariosTemp.length === 0) {
      container.innerHTML =
        '<p style="color:#999;font-style:italic;">Nenhum horário adicionado ainda.</p>';
      return;
    }

    container.innerHTML = horariosTemp
      .map((horario, index) => `
      <div class="horario-item" style="display:flex;justify-content:space-between;align-items:center;padding:12px;background:#f0f0f0;border-radius:5px;border-left:4px solid #c8102e;margin-bottom:8px;">
        <div>
          <strong style="color:#c8102e">${DIAS_SEMANA_NOMES[horario.dia_semana]}</strong>
          <span>•</span>
          ${horario.horario_abertura} - ${horario.horario_fechamento}
          ${horario.observacao ? `<br><small style="color:#666;">💬 ${horario.observacao}</small>` : ""}
        </div>
        <button style="padding:6px 10px;background:#dc3545;color:white;border:none;border-radius:4px;cursor:pointer"
          onclick="removerHorarioTemp(${index})">🗑️ Remover</button>
      </div>
    `)
      .join("");
  }
  window.removerHorarioTemp = function (index) {
    const removido = horariosTemp[index];
    horariosTemp.splice(index, 1);
    renderizarHorariosTemp();
    aviso.textContent = ` ${DIAS_SEMANA_NOMES[removido.dia_semana]} removido`;
    aviso.style.color = "orange";
    setTimeout(() => (aviso.textContent = ""), 3000);
  };

  function adicionarHorarioTemp() {
    if (!validarCampos()) {
      aviso.textContent = "Verifique os dados antes de continuar.";
      aviso.style.color = "red";
      return;
    }

    const diaSemana = parseInt(dFuncionamento.value);
    if (horariosTemp.some((h) => h.dia_semana === diaSemana)) {
      aviso.textContent = `${DIAS_SEMANA_NOMES[diaSemana]} já foi adicionado`;
      aviso.style.color = "red";
      return;
    }
    horariosTemp.push({
      dia_semana: diaSemana,
      horario_abertura: hAbertura.value.trim(),
      horario_fechamento: hFechamento.value.trim(),
      observacao: observacao.value.trim()
    });
    horariosTemp.sort((a, b) => a.dia_semana - b.dia_semana);
    renderizarHorariosTemp();
    aviso.textContent = `${DIAS_SEMANA_NOMES[diaSemana]} adicionado`;
    aviso.style.color = "green";
    dFuncionamento.value = "";
    hAbertura.value = "";
    hFechamento.value = "";
    observacao.value = "";
    setTimeout(() => (aviso.textContent = ""), 3000);
  }
  if (btnAdicionar) {
    btnAdicionar.addEventListener("click", adicionarHorarioTemp);
  }
  [dFuncionamento, hAbertura, hFechamento, observacao].forEach((campo) => {
    campo.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        adicionarHorarioTemp();
      }
    });
  });
  // envio final ao backend (todos os horários da lista)
  horarioFuncionamento.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (horariosTemp.length === 0) {
      alert("Adicione pelo menos um horário.");
      return;
    }
    const token = localStorage.getItem("token");
    let sucesso = 0;
    let erro = 0;
    for (const h of horariosTemp) {
      try {
        const resp = await fetch("/horario/horarios", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + token,
          },
          body: JSON.stringify({
            dia_semana: h.dia_semana,
            horario_abertura: h.horario_abertura,
            horario_fechamento: h.horario_fechamento,
            observacao: h.observacao,
            ativo: true
          }),
        });
        const res = await resp.json();
        if (res.success) sucesso++;
        else erro++;
      } catch {
        erro++;
      }
    }
    if (erro > 0) {
      alert(`${sucesso} horário(s) salvos, ${erro} falharam.`);
    } else {
      alert("Todos os horários cadastrados com sucesso!");
      horariosTemp = [];
      renderizarHorariosTemp();
      horarioFuncionamento.reset();
    }
  });
  renderizarHorariosTemp();
}
