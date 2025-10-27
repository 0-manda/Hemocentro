const formCadastro = document.getElementById("formCadastro");

if(formCadastro){
    const mail = document.getElementById("email").value.trim();
    const nome = document.getElementById("nome").value.trim();
    const senha = document.getElementById("senha").value.trim();
    const senhaCheck = document.getElementById("senhaCheck").value.trim(); // usado para verificar se senha e senhaCheck batem
    const aviso = document.getElementById("aviso").value.trim();
    formCadastro.addEventListener("submit", function(e){
        e.preventDefault();

        if(mail===""||nome===""||senha===""||senhaCheck===""){
            aviso.style.color = "red";
            aviso.textContent = "Algum dos campos está vazio";
            return;
        }

        window.location.href = "#";
    })

}