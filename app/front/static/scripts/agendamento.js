function obterParametroURL(nome) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(nome);
}

document.addEventListener("DOMContentLoaded", () => {
  const idHemocentro = obterParametroURL("id_hemocentro");
  const nomeHemocentro = obterParametroURL("nome_hemocentro");

  console.log("ID Hemocentro da URL:", idHemocentro);
  console.log("Nome Hemocentro da URL:", nomeHemocentro);

  // Preencher o campo hidden
  const inputHemocentro = document.getElementById("id_hemocentro");
  if (inputHemocentro && idHemocentro) {
    inputHemocentro.value = idHemocentro;
    console.log("Campo id_hemocentro preenchido com:", idHemocentro);
  }

  // Preencher o nome do hemocentro na tela
  const nomeHemocentroDetalhe = document.getElementById("nome_hemocentro_detalhe");
  if (nomeHemocentroDetalhe && nomeHemocentro) {
    nomeHemocentroDetalhe.textContent = decodeURIComponent(nomeHemocentro);
  } else if (nomeHemocentroDetalhe) {
    nomeHemocentroDetalhe.textContent = "Hemocentro não identificado";
  }
});

const agendamento = document.getElementById("agendamento");

if (agendamento) {
  // Pega as referências dos elementos
  const tempo = document.getElementById("data_hora");
  const tipoDoacao = document.getElementById("tipo_doacao");
  const tipoDoar = document.getElementById("tipo_sangue_doado");
  const obs = document.getElementById("observacoes");
  const inputHemocentro = document.getElementById("id_hemocentro");

  agendamento.addEventListener("submit", async (event) => {
    event.preventDefault();

    // 1. PEGA O TOKEN
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Você precisa estar logado para agendar.");
      return;
    }

    let idUser = null;
    try {
      const resp = await fetch("http://127.0.0.1:5000/api/perfil", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!resp.ok) {
        console.error("Erro na busca");
        return;
      }

      const json = await resp.json();

      if (json.success) {
        idUser = json.usuario.id_usuario;
      } else {
        alert("Erro ao identificar usuário.");
        return;
      }
    } catch (err) {
      console.error(err);
      return;
    }

    const idHemocentro = parseInt(inputHemocentro.value);
    
    if (!idHemocentro || idHemocentro === 0 || isNaN(idHemocentro)) {
      alert("Erro: Nenhum hemocentro foi selecionado. Por favor, volte à página de hemocentros e clique em 'Agendar' novamente.");
      return;
    }

    const dados = {
      id_hemocentro: idHemocentro,
      id_usuario: idUser,
      data_hora: tempo.value,
      tipo_doacao: tipoDoacao.value,
      tipo_sangue: tipoDoar.value,
      observacoes: obs.value,
    };

    console.log("Enviando dados:", dados);

    try {
      const resp = await fetch("http://127.0.0.1:5000/api/agendamentos", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(dados),
      });

      const res = await resp.json();

      if (resp.ok && res.success) {
        console.log("Agendamento realizado.");
        alert("Agendamento realizado com sucesso!");
        agendamento.reset();
        window.location.href = "/perfil";
      } else {
        alert("Erro: " + (res.message || "Falha ao agendar"));
      }
    } catch (err) {
      console.error("Erro de agendamento:", err);
      alert("Erro de conexão com o servidor.");
    }
  });
}