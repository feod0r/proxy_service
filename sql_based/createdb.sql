DROP TABLE `apr`.`proxy`;
CREATE TABLE `apr`.`proxy` 
(
    `id` INT NOT NULL AUTO_INCREMENT ,
    `address` VARCHAR(100) NOT NULL ,
    `deleted_flag` VARCHAR(1) NOT NULL DEFAULT 'N' ,
    `as_of_day` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    `country` VARCHAR(2) NOT NULL DEFAULT 'RU',
    `rpw` INT NOT NULL DEFAULT 0,
    `resourse_ids` VARCHAR(210) NOT NULL DEFAULT '[]',
    PRIMARY KEY (`id`),
    INDEX `proxy_adr_indx` (`address`)
)
ENGINE = InnoDB;


DROP TABLE `apr`.`access_log`;
CREATE TABLE `apr`.`access_log`
(
    `id` INT NOT NULL AUTO_INCREMENT ,
    `address` VARCHAR(100) NOT NULL ,
    `resource_id` INT NOT NULL DEFAULT '0' ,
    `effective_from` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , 
    `effective_to` TIMESTAMP NOT NULL , 
     PRIMARY KEY (`id`), 
     INDEX `access_log_to_indx` (`effective_to`),
     INDEX `access_log_adr_indx` (`address`)
) ENGINE = InnoDB;