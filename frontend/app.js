// 1. Função para carregar as páginas baseada na URL atual do navegador
function gerenciarRoteamentoSPA() {
    const caminhoAtual = window.location.pathname; // Pega o caminho (ex: "/cadastro" ou "/ajuda")

    if (caminhoAtual === '/' || caminhoAtual === '/home') {
        // Ajustado o onclick para passar o event atual do clique
        document.getElementById('app').innerHTML = '<h1>Página Inicial</h1><p>Bem-vindo ao CHAVE13!</p><a href="/cadastro" onclick="navegarPara(\'/cadastro\', event)">cadastro</a>';
    } 
    else if (caminhoAtual === '/cadastro') {
        // Se a rota for /cadastro, busca dinamicamente o arquivo físico 'cadastro.html'
        fetch('/cadastro.html')
            .then(res => res.text())
            .then(html => {
                const container = document.getElementById('app');
                container.innerHTML = html;
                
                // EXECUTA OS SCRIPTS: Procura e roda os scripts do arquivo carregado
                executarScriptsInjetados(container);
            });
    } 
    else {
        document.getElementById('app').innerHTML = '<h1>Erro 404</h1><p>Rota não encontrada no Front-end.</p>';
    }
}

// NOVA FUNÇÃO: Copia os scripts do HTML injetado e força a execução no navegador
function executarScriptsInjetados(container) {
    const scripts = container.querySelectorAll('script');
    
    scripts.forEach(scriptAntigo => {
        // Cria um elemento script totalmente novo
        const scriptNovo = document.createElement('script');
        
        // Copia o código escrito direto na tag (se houver)
        scriptNovo.textContent = scriptAntigo.textContent;
        
        // Copia todos os atributos (como src, type, etc.) caso seja um script externo
        Array.from(scriptAntigo.attributes).forEach(attr => {
            scriptNovo.setAttribute(attr.name, attr.value);
        });
        
        // Injeta no body para executar e remove logo em seguida para não sujar o HTML
        document.body.appendChild(scriptNovo);
        scriptNovo.remove();
    });
}

// 2. Função para o usuário clicar em links sem recarregar a página
// Adicionado o parâmetro 'event' explicitamente para evitar comportamento obsoleto
function navegarPara(url, event) {
    if (event) event.preventDefault();      // Previne o comportamento padrão do link de recarregar a página
    window.history.pushState({}, '', url); // Altera a URL na barra de endereços do navegador
    gerenciarRoteamentoSPA();              // Executa a lógica de renderização
}

// 3. Escuta eventos para garantir que o "Voltar" e "Avançar" do navegador funcionem
window.addEventListener('popstate', gerenciarRoteamentoSPA);
window.addEventListener('DOMContentLoaded', gerenciarRoteamentoSPA);
