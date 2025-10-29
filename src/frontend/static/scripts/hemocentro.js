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
  });
}
