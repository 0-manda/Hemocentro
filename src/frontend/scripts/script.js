const formCadastro = document.getElementById("formCadastro");

if (formCadastro) {
  const mail = document.getElementById("email").value.trim();
  const nome = document.getElementById("nome").value.trim();
  const senha = document.getElementById("senha").value.trim();
  const senhaCheck = document.getElementById("senhaCheck").value.trim(); // usado para verificar se senha e senhaCheck batem
  const aviso = document.getElementById("aviso").value.trim();
  formCadastro.addEventListener("submit", function (e) {
    e.preventDefault();

    if (mail === "" || nome === "" || senha === "" || senhaCheck === "") {
      aviso.style.color = "red";
      aviso.textContent = "Algum dos campos está vazio";
      return;
    }

    window.location.href = "#";
  });
}

// analise de senhas
const f = document.getElementById("cadastro");
const nome = document.getElementById("nome");
const mail = document.getElementById("mail");
const curso = document.getElementById("curso");
const termos = document.getElementById("termos");
const btn = document.getElementById("btn");
const out = document.getElementById("resultado");
const mNome = document.getElementById("m-nome");
const mMail = document.getElementById("m-mail");
const mTerm = document.getElementById("m-termos");
// [2] Validadores puros (somente lógica)
const vNome = (v) => v.trim().length >= 3;
const reMail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const vMail = (v) => reMail.test(v.trim());
const vTerm = (c) => c === true;
// [3] Função de UI para aplicar feedback visual + texto
function setEstado(
  campo,
  msgEl,
  ok,
  msgOK = "Ok ",
  msgERRO = "Corrija este campo."
) {
  campo.classList.toggle("ok", ok);
  campo.classList.toggle("erro", !ok);
  campo.setAttribute("aria-invalid", String(!ok));
  msgEl.textContent = ok ? msgOK : msgERRO;
}
// [4] Checa tudo e habilita/desabilita botão
function revalidar() {
  const okN = vNome(nome.value);
  const okM = vMail(mail.value);
  const okT = vTerm(termos.checked);
  setEstado(nome, mNome, okN, "Nome válido.", "Mínimo 3 caracteres.");
  setEstado(mail, mMail, okM, "E-mail válido.", "Ex.: nome@dominio.com");
  setEstado(termos, mTerm, okT, "Aceito.", "É preciso aceitar os termos.");
  const tudoOK = okN && okM && okT;
  btn.disabled = !tudoOK;
  return tudoOK;
}
// [5] Eventos em cada campo (validação em tempo real)
nome.addEventListener("input", revalidar);
mail.addEventListener("input", revalidar);
curso.addEventListener("change", revalidar);
termos.addEventListener("change", revalidar);
// [6] Intercepta o envio
f.addEventListener("submit", (e) => {
  e.preventDefault(); // evita envio/reload
  if (!revalidar()) return; // garante validação final
  // Aqui você enviaria ao servidor (fetch/AJAX)
  out.textContent = "Formulário enviado com sucesso! ";
});
// [7] Estado inicial
revalidar();

// verificação <----------------------------

const f = document.getElementById("f");
const n = document.getElementById("n");
const e = document.getElementById("e");
const s = document.getElementById("s");
const c = document.getElementById("c");
const t = document.getElementById("t");
const bar = document.getElementById("bar");
const hN = document.getElementById("h-n");
const hE = document.getElementById("h-e");
const hS = document.getElementById("h-s");
const hC = document.getElementById("h-c");
const hT = document.getElementById("h-t");
const sum = document.getElementById("sum");
const send = document.getElementById("send");
const ok = document.getElementById("ok");

// --------------------------
// [2] Validadores (lógica pura)
// --------------------------
const reMail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const vNome = (v) => v.trim().length >= 3;
const vMail = (v) => reMail.test(v.trim());
const vCurso = (v) => v !== "";
const vTerm = (v) => v === true;
// Força de senha (pontuação simples)
function scoreSenha(v) {
  let p = 0;
  if (v.length >= 8) p += 30;
  if (/[A-Z]/.test(v)) p += 20;
  if (/[a-z]/.test(v)) p += 20;
  if (/\d/.test(v)) p += 15;
  if (/[^A-Za-z0-9]/.test(v)) p += 15;
  return Math.min(p, 100);
}
// --------------------------
// [3] UI helpers (apenas interface)
// --------------------------
function setEstado(campo, hintEl, ok, msgOK, msgERRO) {
  campo.classList.toggle("ok", ok);
  campo.classList.toggle("erro", !ok);
  campo.setAttribute("aria-invalid", String(!ok));
  hintEl.textContent = ok ? msgOK : msgERRO;
}
function setBarra(pct) {
  bar.style.width = pct + "%";
  bar.className = ""; // reset classes
  if (pct < 40) bar.classList.add("fraca");
  else if (pct < 80) bar.classList.add("media");
  else bar.classList.add("forte");
}

// --------------------------
// [4] Revalidação geral
// --------------------------
function revalidar() {
  const okN = vNome(n.value);
  const okE = vMail(e.value);
  const pts = scoreSenha(s.value);
  const okS = pts >= 40; // exige pelo menos "média"
  const okC = vCurso(c.value);
  const okT = vTerm(t.checked);
  setEstado(n, hN, okN, "Nome ok.", "Mínimo 3 caracteres.");
  setEstado(e, hE, okE, "E-mail ok.", "Ex.: nome@dominio.com");
  setBarra(pts);
  setEstado(s, hS, okS, "Senha adequada.", "Use 8+ chars, nº e símbolos.");
  setEstado(c, hC, okC, "Curso ok.", "Selecione um curso.");
  setEstado(t, hT, okT, "Termos .", "Marque para continuar.");

  // Sumário de erros para acessibilidade (screen readers)
  const erros = [];
  if (!okN) erros.push("Nome curto.");
  if (!okE) erros.push("E-mail inválido.");
  if (!okS) erros.push("Senha fraca.");
  if (!okC) erros.push("Curso não selecionado.");
  if (!okT) erros.push("Termos não aceitos.");
  sum.textContent = erros.join(" ");
  // Habilita envio apenas se tudo ok
  const tudoOK = okN && okE && okS && okC && okT;
  send.disabled = !tudoOK;
  return tudoOK;
}

// --------------------------
// [5] Ouvintes por campo
// --------------------------
n.addEventListener("input", revalidar);
e.addEventListener("input", revalidar);
s.addEventListener("input", revalidar);
c.addEventListener("change", revalidar);
t.addEventListener("change", revalidar);
// --------------------------
// [6] Envio
// --------------------------
f.addEventListener("submit", (ev) => {
  ev.preventDefault();
  if (!revalidar()) return;
  // Aqui caberia um fetch(...) real (é o início da API Fetch em JavaScript)
  ok.textContent = "Cadastro enviado com sucesso! ";
  f.reset();
  setBarra(0);
  revalidar(); // recalcula estados após reset
});

// --------------------------
// [5] Ouvintes por campo
// --------------------------
n.addEventListener("input", revalidar);
e.addEventListener("input", revalidar);
s.addEventListener("input", revalidar);
c.addEventListener("change", revalidar);
t.addEventListener("change", revalidar);
// --------------------------
// [6] Envio
// --------------------------
f.addEventListener("submit", (ev) => {
  ev.preventDefault();
  if (!revalidar()) return;
  // Aqui caberia um fetch(...) real (é o início da API Fetch em JavaScript)
  ok.textContent = "Cadastro enviado com sucesso! ";
  f.reset();
  setBarra(0);
  revalidar(); // recalcula estados após reset
});
