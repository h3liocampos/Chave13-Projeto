CREATE DATABASE CHAVE13DB;
USE CHAVE13DB;


-- =========================================================
-- USUÁRIOS
-- =========================================================

CREATE TABLE `usuarios` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `nome` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL,
    `senha` VARCHAR(255) NOT NULL,
    `telefone` VARCHAR(14) NULL,
    `perfil` VARCHAR(30) NOT NULL,

    PRIMARY KEY (`id`),

    UNIQUE KEY `usuarios_email_unique` (`email`),
    UNIQUE KEY `usuarios_telefone_unique` (`telefone`)
);


-- =========================================================
-- ESTABELECIMENTOS
-- =========================================================

CREATE TABLE `estabelecimentos` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `nome` VARCHAR(100) NOT NULL,
    `cnpj` CHAR(14) NOT NULL,
    `email` VARCHAR(120) NOT NULL,
    `telefone` VARCHAR(14) NOT NULL,
    `dono_id` BIGINT UNSIGNED NOT NULL,

    PRIMARY KEY (`id`),

    UNIQUE KEY `estabelecimentos_cnpj_unique` (`cnpj`),
    UNIQUE KEY `estabelecimentos_email_unique` (`email`),
    UNIQUE KEY `estabelecimentos_telefone_unique` (`telefone`),

    CONSTRAINT `estabelecimentos_dono_id_foreign`
        FOREIGN KEY (`dono_id`)
        REFERENCES `usuarios` (`id`)
);


-- =========================================================
-- ENDEREÇOS
-- =========================================================

CREATE TABLE `enderecos` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `estabelecimento_id` BIGINT UNSIGNED NOT NULL,

    `cep` CHAR(8) NOT NULL,
    `numero` VARCHAR(10) NOT NULL,
    `logradouro` VARCHAR(70) NOT NULL,
    `bairro` VARCHAR(70) NOT NULL,
    `cidade` VARCHAR(70) NOT NULL,
    `estado` CHAR(2) NOT NULL,
    `pais` VARCHAR(60) NOT NULL,

    `complemento` VARCHAR(100) NULL,
    `observacao` VARCHAR(255) NULL,

    PRIMARY KEY (`id`),

    UNIQUE KEY `enderecos_estabelecimento_unique`
        (`estabelecimento_id`),

    CONSTRAINT `enderecos_estabelecimento_id_foreign`
        FOREIGN KEY (`estabelecimento_id`)
        REFERENCES `estabelecimentos` (`id`)
);


-- =========================================================
-- FUNCIONÁRIOS
-- =========================================================

CREATE TABLE `funcionarios` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `usuario_id` BIGINT UNSIGNED NOT NULL,
    `estabelecimento_id` BIGINT UNSIGNED NOT NULL,

    PRIMARY KEY (`id`),

    UNIQUE KEY `funcionarios_usuario_estabelecimento_unique`
        (`usuario_id`, `estabelecimento_id`),

    CONSTRAINT `funcionarios_usuario_id_foreign`
        FOREIGN KEY (`usuario_id`)
        REFERENCES `usuarios` (`id`),

    CONSTRAINT `funcionarios_estabelecimento_id_foreign`
        FOREIGN KEY (`estabelecimento_id`)
        REFERENCES `estabelecimentos` (`id`)
);


-- =========================================================
-- SESSÕES
-- =========================================================

CREATE TABLE `sessoes` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `sessao` VARCHAR(255) NOT NULL,
    `usuario_id` BIGINT UNSIGNED NOT NULL,

    PRIMARY KEY (`id`),

    UNIQUE KEY `sessoes_sessao_unique` (`sessao`),

    CONSTRAINT `sessoes_usuario_id_foreign`
        FOREIGN KEY (`usuario_id`)
        REFERENCES `usuarios` (`id`)
);


-- =========================================================
-- CARROS
-- =========================================================

CREATE TABLE `carros` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `usuario_id` BIGINT UNSIGNED NOT NULL,

    `placa` CHAR(7) NOT NULL,
    `modelo` VARCHAR(60) NOT NULL,
    `marca` VARCHAR(40) NOT NULL,
    `ano` YEAR NOT NULL,
    `chassi` VARCHAR(30) NOT NULL,

    PRIMARY KEY (`id`),

    UNIQUE KEY `carros_placa_unique` (`placa`),
    UNIQUE KEY `carros_chassi_unique` (`chassi`),

    CONSTRAINT `carros_usuario_id_foreign`
        FOREIGN KEY (`usuario_id`)
        REFERENCES `usuarios` (`id`)
);


-- =========================================================
-- MANUTENÇÕES
-- =========================================================

CREATE TABLE `manutencoes` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

    `cliente_id` BIGINT UNSIGNED NOT NULL,
    `carro_id` BIGINT UNSIGNED NOT NULL,
    `estabelecimento_id` BIGINT UNSIGNED NOT NULL,
    `funcionario_id` BIGINT UNSIGNED NOT NULL,

    `servico` VARCHAR(60) NOT NULL,
    `preco_servico` DECIMAL(8, 2) NOT NULL,

    `pagamento` ENUM(
        'realizado',
        'andamento',
        'pendente'
    ) NOT NULL DEFAULT 'pendente',

    PRIMARY KEY (`id`),

    CONSTRAINT `manutencoes_cliente_id_foreign`
        FOREIGN KEY (`cliente_id`)
        REFERENCES `usuarios` (`id`),

    CONSTRAINT `manutencoes_carro_id_foreign`
        FOREIGN KEY (`carro_id`)
        REFERENCES `carros` (`id`),

    CONSTRAINT `manutencoes_estabelecimento_id_foreign`
        FOREIGN KEY (`estabelecimento_id`)
        REFERENCES `estabelecimentos` (`id`),

    CONSTRAINT `manutencoes_funcionario_id_foreign`
        FOREIGN KEY (`funcionario_id`)
        REFERENCES `funcionarios` (`id`)
);


-- =========================================================
-- PEÇAS
-- =========================================================

CREATE TABLE `pecas` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `manutencao_id` BIGINT UNSIGNED NOT NULL,

    `nome` VARCHAR(70) NOT NULL,
    `descricao` VARCHAR(255) NOT NULL,
    `preco_unitario` DECIMAL(8, 2) NOT NULL,

    PRIMARY KEY (`id`),

    CONSTRAINT `pecas_manutencao_id_foreign`
        FOREIGN KEY (`manutencao_id`)
        REFERENCES `manutencoes` (`id`)
);