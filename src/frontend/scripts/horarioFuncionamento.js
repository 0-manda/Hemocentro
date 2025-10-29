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
