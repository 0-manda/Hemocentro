// dah acesso somente a quem tem o token hemocentro
if (localStorage.getItem("hemotoken")) {
  // registro de campanha
  const campanha = document.getElementById("campanha");

  if (campanha) {
    const descricao = document.getElementById("descricao");
    const dInic = document.getElementById("diaInicio");
    const dFim = document.getElementById("diaFim");
    const tipoSangueRequerido = document.getElementById("tipoSangueRequerido");
    const qtdMetaLitros = document.getElementById("qtdMetaLitros");
    const qtdAtual = document.getElementById("qtdAtual");
    const objetivo = document.getElementById("objetivo");
    const destaque = document.getElementById("destaque");
    let ativo = true;

    // Pega a data atual
    const hoje = new Date();
    const dia = String(hoje.getDate()).padStart(2, "0");
    const mes = String(hoje.getMonth() + 1).padStart(2, "0");
    const ano = hoje.getFullYear();
    const dCriacao = `${ano}-${mes}-${dia}`;

    // --------------------------
    // Validação
    // --------------------------
    const vTexto = (v) => v.trim().length >= 3;
    const vData = (v) => /^\d{4}-\d{2}-\d{2}$/.test(v);
    const vNumero = (v) => !isNaN(v) && Number(v) >= 0;
    const compararDatas = (inicio, fim) => new Date(inicio) <= new Date(fim);

    function validar() {
      const okDescricao = vTexto(descricao.value);
      const okInicio = vData(dInic.value);
      const okFim = vData(dFim.value);
      const ordemCerta =
        okInicio && okFim && compararDatas(dInic.value, dFim.value);
      const okTipo = vTexto(tipoSangueRequerido.value);
      const okMeta = vNumero(qtdMetaLitros.value);
      const okAtual = vNumero(qtdAtual.value);

      // aplicar classes de erro simples
      descricao.classList.toggle("erro", !okDescricao);
      dInic.classList.toggle("erro", !okInicio);
      dFim.classList.toggle("erro", !okFim || !ordemCerta);
      tipoSangueRequerido.classList.toggle("erro", !okTipo);
      qtdMetaLitros.classList.toggle("erro", !okMeta);
      qtdAtual.classList.toggle("erro", !okAtual);

      return (
        okDescricao &&
        okInicio &&
        okFim &&
        ordemCerta &&
        okTipo &&
        okMeta &&
        okAtual
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
        descricao: descricao.value.trim(),
        diaInicio: dInic.value.trim(),
        diaFim: dFim.value.trim(),
        tipoSangueRequerido: tipoSangueRequerido.value.trim(),
        qtdMetaLitros: Number(qtdMetaLitros.value),
        qtdAtual: Number(qtdAtual.value),
        objetivo: objetivo.value.trim(),
        destaque: destaque.checked || false,
        ativo: ativo,
        dCriacao: dCriacao,
      };

      // ver conectividade com o flask
      try {
        const resp = await fetch("/campanha", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(dados),
        });

        const res = await resp.json();

        if (res.ok) {
          alert("Campanha registrada com sucesso!");
          campanha.reset();
        } else {
          alert("Erro: " + res.msg);
        }
      } catch (err) {
        console.error(err);
        alert("Erro ao conectar com o servidor.");
      }
    });
  }
}
