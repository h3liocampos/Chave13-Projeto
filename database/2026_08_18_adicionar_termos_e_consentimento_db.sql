-- USE CHAVE13DB;

CREATE TABLE `termos`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `versao` VARCHAR(255) NOT NULL,
    `titulo` VARCHAR(255) NOT NULL,
    `conteudo` TEXT NOT NULL,
    `data_publicacao` TIMESTAMP NOT NULL
);
ALTER TABLE
    `termos` ADD UNIQUE `termos_versao_unique`(`versao`);
CREATE TABLE `consentimentos`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `termo_id` BIGINT NOT NULL,
    `usuario_id` BIGINT NOT NULL,
    `tipo_finalidade` VARCHAR(255) NOT NULL,
    `aceito` BOOLEAN NOT NULL DEFAULT 0,
    `data_confirmacao` TIMESTAMP NOT NULL
);
ALTER TABLE
    `consentimentos` ADD UNIQUE `consentimentos_usuario_id_termo_id_unique`(`usuario_id`, `termo_id`);
-- Altera o tipo e cria a chave estrangeira do usuário
ALTER TABLE `consentimentos` 
    MODIFY `usuario_id` BIGINT UNSIGNED NOT NULL,
    ADD CONSTRAINT `consentimentos_usuario_id_foreign` FOREIGN KEY(`usuario_id`) REFERENCES `usuarios`(`id`);

-- Altera o tipo e cria a chave estrangeira do termo
ALTER TABLE `consentimentos` 
    MODIFY `termo_id` BIGINT UNSIGNED NOT NULL,
    ADD CONSTRAINT `consentimentos_termo_id_foreign` FOREIGN KEY(`termo_id`) REFERENCES `termos`(`id`);
