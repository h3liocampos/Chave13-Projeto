// =========================================================
// CHAVE 13 - APP.JS
// =========================================================


// =========================================================
// MOSTRAR / ESCONDER SENHA
// =========================================================

function mostrarSenha(id) {
    const campo = document.getElementById(id);

    if (!campo) return;

    if (campo.type === "password") {
        campo.type = "text";
    } else {
        campo.type = "password";
    }
}


// =========================================================
// MÁSCARA CNPJ
// =========================================================

function mascaraCNPJ(valor) {

    valor = valor.replace(/\D/g, "");

    valor = valor.replace(/^(\d{2})(\d)/, "$1.$2");
    valor = valor.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
    valor = valor.replace(/\.(\d{3})(\d)/, ".$1/$2");
    valor = valor.replace(/(\d{4})(\d)/, "$1-$2");

    return valor.substring(0, 18);
}


// =========================================================
// MÁSCARA CEP
// =========================================================

function mascaraCEP(valor) {

    valor = valor.replace(/\D/g, "");

    valor = valor.replace(/^(\d{5})(\d)/, "$1-$2");

    return valor.substring(0, 9);
}


// =========================================================
// MÁSCARA CELULAR
// =========================================================

function mascaraCelular(valor) {

    valor = valor.replace(/\D/g, "");

    valor = valor.replace(/^(\d{2})(\d)/, "($1) $2");
    valor = valor.replace(/(\d{5})(\d)/, "$1-$2");

    return valor.substring(0, 15);
}


// =========================================================
// MÁSCARA TELEFONE
// =========================================================

function mascaraTelefone(valor) {

    valor = valor.replace(/\D/g, "");

    if (valor.length <= 10) {

        valor = valor.replace(/^(\d{2})(\d)/, "($1) $2");
        valor = valor.replace(/(\d{4})(\d)/, "$1-$2");

    } else {

        valor = valor.replace(/^(\d{2})(\d)/, "($1) $2");
        valor = valor.replace(/(\d{5})(\d)/, "$1-$2");

    }

    return valor.substring(0, 15);
}


// =========================================================
// BUSCAR CEP
// =========================================================

async function buscarCEP() {

    const campoCEP = document.getElementById("cep");
    const campoEndereco = document.getElementById("endereco");

    if (!campoCEP || !campoEndereco) return;

    const cep = campoCEP.value.replace(/\D/g, "");

    if (cep.length !== 8) {
        return;
    }

    campoEndereco.value = "Buscando endereço...";

    try {

        const resposta = await fetch(
            `https://viacep.com.br/ws/${cep}/json/`
        );

        if (!resposta.ok) {
            throw new Error("Erro ao consultar CEP");
        }

        const dados = await resposta.json();

        if (dados.erro) {

            campoEndereco.value = "";

            alert("CEP não encontrado.");

            return;
        }

        let endereco = "";

        if (dados.logradouro) {
            endereco += dados.logradouro;
        }

        if (dados.bairro) {
            endereco += `, ${dados.bairro}`;
        }

        if (dados.localidade) {
            endereco += `, ${dados.localidade}`;
        }

        if (dados.uf) {
            endereco += ` - ${dados.uf}`;
        }

        campoEndereco.value = endereco;

    } catch (erro) {

        console.error(erro);

        campoEndereco.value = "";

        alert("Não foi possível buscar o endereço.");
    }
}


// =========================================================
// LOGIN
// =========================================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const emailCampo =
            document.getElementById("email");

        const senhaCampo =
            document.getElementById("senha");

        const mensagem =
            document.getElementById("mensagem");

        if (!emailCampo || !senhaCampo) {
            return;
        }

        const email =
            emailCampo.value.trim();

        const senha =
            senhaCampo.value;

        if (!email || !senha) {

            if (mensagem) {

                mensagem.innerText =
                    "Preencha o e-mail e a senha.";

                mensagem.style.color = "red";
            }

            return;
        }

        if (mensagem) {

            mensagem.innerText =
                "Entrando...";

            mensagem.style.color = "#555";
        }

        try {

            const resposta = await fetch(
                "/api/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    credentials: "same-origin",

                    body: JSON.stringify({
                        email: email,
                        senha: senha
                    })
                }
            );

            const dados =
                await resposta.json();

            if (dados.sucesso) {

                if (mensagem) {

                    mensagem.innerText =
                        dados.mensagem ||
                        "Login realizado com sucesso!";

                    mensagem.style.color =
                        "green";
                }

                setTimeout(function() {

                    window.location.href = "/";

                }, 1000);

            } else {

                if (mensagem) {

                    mensagem.innerText =
                        dados.erro ||
                        dados.mensagem ||
                        "E-mail ou senha incorretos.";

                    mensagem.style.color =
                        "red";
                }
            }

        } catch (erro) {

            console.error(erro);

            if (mensagem) {

                mensagem.innerText =
                    "Erro ao conectar com o servidor.";

                mensagem.style.color =
                    "red";
            }
        }
    });
}


// =========================================================
// CADASTRO DE USUÁRIO
// =========================================================

const usuarioForm =
    document.getElementById("usuarioForm");

if (usuarioForm) {

    usuarioForm.addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();

            const nomeCampo =
                document.getElementById("nome") ||
                document.getElementById("nome_completo");

            const emailCampo =
                document.getElementById("email") ||
                document.getElementById("email_usuario");

            const telefoneCampo =
                document.getElementById("telefone") ||
                document.getElementById("celular");

            const senhaCampo =
                document.getElementById("senha") ||
                document.getElementById("senha_usuario");

            const confirmarCampo =
                document.getElementById("confirmar_senha");

            const perfilCampo =
                document.getElementById("perfil");

            const mensagem =
                document.getElementById("mensagem");

            if (!nomeCampo ||
                !emailCampo ||
                !senhaCampo) {

                if (mensagem) {

                    mensagem.innerText =
                        "Não foi possível encontrar os campos do cadastro.";

                    mensagem.style.color =
                        "red";
                }

                return;
            }

            const nome =
                nomeCampo.value.trim();

            const email =
                emailCampo.value.trim();

            const telefone =
                telefoneCampo
                    ? telefoneCampo.value.replace(/\D/g, "")
                    : "";

            const senha =
                senhaCampo.value;

            const confirmar =
                confirmarCampo
                    ? confirmarCampo.value
                    : senha;

            const perfil =
                perfilCampo
                    ? perfilCampo.value.trim()
                    : "usuario";


            // VALIDAÇÕES

            if (!nome ||
                !email ||
                !senha) {

                if (mensagem) {

                    mensagem.innerText =
                        "Preencha os campos obrigatórios.";

                    mensagem.style.color =
                        "red";
                }

                return;
            }

            if (senha !== confirmar) {

                if (mensagem) {

                    mensagem.innerText =
                        "As senhas não são iguais.";

                    mensagem.style.color =
                        "red";
                }

                return;
            }

            if (mensagem) {

                mensagem.innerText =
                    "Cadastrando...";

                mensagem.style.color =
                    "#555";
            }


            // ENVIA PARA O FLASK

            try {

                const resposta =
                    await fetch(
                        "/api/usuarios",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            credentials:
                                "same-origin",

                            body: JSON.stringify({

                                nome: nome,

                                email: email,

                                senha: senha,

                                telefone:
                                    telefone || null,

                                perfil:
                                    perfil || "usuario"
                            })
                        }
                    );

                const dados =
                    await resposta.json();

                if (dados.sucesso) {

                    if (mensagem) {

                        mensagem.innerText =
                            dados.mensagem ||
                            "Cadastro realizado com sucesso!";

                        mensagem.style.color =
                            "green";
                    }

                    usuarioForm.reset();

                    setTimeout(function() {

                        window.location.href =
                            "/";

                    }, 1500);

                } else {

                    if (mensagem) {

                        mensagem.innerText =
                            dados.erro ||
                            dados.mensagem ||
                            "Erro ao cadastrar.";

                        mensagem.style.color =
                            "red";
                    }
                }

            } catch (erro) {

                console.error(erro);

                if (mensagem) {

                    mensagem.innerText =
                        "Erro ao conectar com o servidor.";

                    mensagem.style.color =
                        "red";
                }
            }
        }
    );
}


// =========================================================
// CADASTRO DE MECÂNICA
// =========================================================

const mecanicoForm =
    document.getElementById("mecanicoForm");

if (mecanicoForm) {

    mecanicoForm.addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();

            const nomeCampo =
                document.getElementById(
                    "nome_mecanica"
                );

            const cnpjCampo =
                document.getElementById("cnpj");

            const cepCampo =
                document.getElementById("cep");

            const enderecoCampo =
                document.getElementById(
                    "endereco"
                );

            const mensagem =
                document.getElementById(
                    "mensagem"
                );

            if (!nomeCampo ||
                !cnpjCampo ||
                !cepCampo ||
                !enderecoCampo) {

                if (mensagem) {

                    mensagem.innerText =
                        "Campos da mecânica não encontrados.";

                    mensagem.style.color =
                        "red";
                }

                return;
            }

            const nome =
                nomeCampo.value.trim();

            const cnpj =
                cnpjCampo.value.replace(
                    /\D/g,
                    ""
                );

            const cep =
                cepCampo.value.replace(
                    /\D/g,
                    ""
                );

            const endereco =
                enderecoCampo.value.trim();


            // VALIDAÇÕES

            if (!nome ||
                !cnpj ||
                !cep) {

                if (mensagem) {

                    mensagem.innerText =
                        "Preencha todos os campos.";

                    mensagem.style.color =
                        "red";
                }

                return;
            }

            if (cnpj.length !== 14) {

                if (mensagem) {

                    mensagem.innerText =
                        "Digite um CNPJ válido.";

                    mensagem.style.color =
                        "red";
                }

                return;
            }

            if (cep.length !== 8) {

                if (mensagem) {

                    mensagem.innerText =
                        "Digite um CEP válido.";

                    mensagem.style.color =
                        "red";
                }

                return;
            }

            if (!endereco) {

                if (mensagem) {

                    mensagem.innerText =
                        "Informe o endereço através do CEP.";

                    mensagem.style.color =
                        "red";
                }

                return;
            }

            if (mensagem) {

                mensagem.innerText =
                    "Cadastrando mecânica...";

                mensagem.style.color =
                    "#555";
            }


            // ENVIA PARA O FLASK

            try {

                const resposta =
                    await fetch(
                        "/api/mecanicas",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            credentials:
                                "same-origin",

                            body: JSON.stringify({

                                nome: nome,

                                cnpj: cnpj,

                                cep: cep,

                                endereco:
                                    endereco
                            })
                        }
                    );

                const dados =
                    await resposta.json();

                if (dados.sucesso) {

                    if (mensagem) {

                        mensagem.innerText =
                            dados.mensagem ||
                            "Mecânica cadastrada com sucesso!";

                        mensagem.style.color =
                            "green";
                    }

                    mecanicoForm.reset();

                    setTimeout(function() {

                        window.location.href =
                            "/";

                    }, 1500);

                } else {

                    if (mensagem) {

                        mensagem.innerText =
                            dados.erro ||
                            dados.mensagem ||
                            "Erro ao cadastrar mecânica.";

                        mensagem.style.color =
                            "red";
                    }
                }

            } catch (erro) {

                console.error(erro);

                if (mensagem) {

                    mensagem.innerText =
                        "Erro ao conectar com o servidor.";

                    mensagem.style.color =
                        "red";
                }
            }
        }
    );
}


// =========================================================
// MÁSCARA DO CNPJ
// =========================================================

const campoCNPJ =
    document.getElementById("cnpj");

if (campoCNPJ) {

    campoCNPJ.addEventListener(
        "input",
        function() {

            this.value =
                mascaraCNPJ(this.value);
        }
    );
}


// =========================================================
// MÁSCARA DO CEP
// =========================================================

const campoCEP =
    document.getElementById("cep");

if (campoCEP) {

    campoCEP.addEventListener(
        "input",
        function() {

            this.value =
                mascaraCEP(this.value);
        }
    );

    campoCEP.addEventListener(
        "blur",
        buscarCEP
    );
}


// =========================================================
// MÁSCARA DO CELULAR
// =========================================================

const campoCelular =
    document.getElementById("celular");

if (campoCelular) {

    campoCelular.addEventListener(
        "input",
        function() {

            this.value =
                mascaraCelular(this.value);
        }
    );
}


// =========================================================
// MÁSCARA DO TELEFONE
// =========================================================

const campoTelefone =
    document.getElementById("telefone");

if (campoTelefone) {

    campoTelefone.addEventListener(
        "input",
        function() {

            this.value =
                mascaraTelefone(this.value);
        }
    );
}