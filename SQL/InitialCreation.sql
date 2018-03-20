-- MySQL Script generated by MySQL Workbench
-- Tue Mar 20 02:16:11 2018
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS = @@UNIQUE_CHECKS, UNIQUE_CHECKS = 0;
SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0;
SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE = 'TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema eve-insight-db
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Table `api_raw_system_kills`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `api_raw_system_kills` (
  `last_modified` DATETIME NOT NULL,
  `expires`       DATETIME NOT NULL,
  `retrieval`     DATETIME NOT NULL,
  `raw_json`      LONGTEXT NULL DEFAULT NULL,
  PRIMARY KEY (`last_modified`)
)
  ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4;


-- -----------------------------------------------------
-- Table `regions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `regions` (
  `region_id`   INT(11)     NOT NULL,
  `region_name` VARCHAR(32) NULL DEFAULT NULL,
  `region_desc` TEXT        NULL DEFAULT NULL,
  PRIMARY KEY (`region_id`)
)
  ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4;


-- -----------------------------------------------------
-- Table `constellations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `constellations` (
  `constellation_id`   INT(11)     NOT NULL,
  `constellation_name` VARCHAR(32) NULL DEFAULT NULL,
  `c_pos_x`            DOUBLE      NULL DEFAULT NULL,
  `c_pos_y`            DOUBLE      NULL DEFAULT NULL,
  `c_pos_z`            DOUBLE      NULL DEFAULT NULL,
  `region_id_fk`       INT(15)     NULL DEFAULT NULL,
  PRIMARY KEY (`constellation_id`),
  INDEX `region_id_fk` (`region_id_fk` ASC),
  CONSTRAINT `constellations_ibfk_1`
  FOREIGN KEY (`region_id_fk`)
  REFERENCES `regions` (`region_id`)
)
  ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4;


-- -----------------------------------------------------
-- Table `systems`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `systems` (
  `system_id`           INT(11)     NOT NULL,
  `system_name`         VARCHAR(32) NULL DEFAULT NULL,
  `star_id`             INT(11)     NULL DEFAULT NULL,
  `s_pos_x`             DOUBLE      NULL DEFAULT NULL,
  `s_pos_y`             DOUBLE      NULL DEFAULT NULL,
  `s_pos_z`             DOUBLE      NULL DEFAULT NULL,
  `security_status`     FLOAT       NULL DEFAULT NULL,
  `security_class`      VARCHAR(5)  NULL DEFAULT NULL,
  `constellation_id_fk` INT(11)     NULL DEFAULT NULL,
  PRIMARY KEY (`system_id`),
  INDEX `constellation_id_fk` (`constellation_id_fk` ASC),
  CONSTRAINT `systems_ibfk_1`
  FOREIGN KEY (`constellation_id_fk`)
  REFERENCES `constellations` (`constellation_id`)
)
  ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4;


-- -----------------------------------------------------
-- Table `pve_stats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pve_stats` (
  `date`       DATETIME NOT NULL,
  `system_fk`  INT(11)  NOT NULL,
  `ship_kills` INT(11)  NOT NULL,
  `npc_kills`  INT(11)  NOT NULL,
  `pod_kills`  INT(11)  NOT NULL,
  PRIMARY KEY (`date`, `system_fk`),
  INDEX `system_fk` (`system_fk` ASC),
  CONSTRAINT `pve_stats_ibfk_1`
  FOREIGN KEY (`system_fk`)
  REFERENCES `systems` (`system_id`)
)
  ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4;


-- -----------------------------------------------------
-- Table `alliances`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `alliances` (
  `alliance_id`             INT          NOT NULL,
  `alliance_name`           VARCHAR(255) NULL DEFAULT NULL,
  `creator_id`              INT          NULL DEFAULT NULL,
  `creator_corporation_id`  INT          NULL DEFAULT NULL,
  `ticker`                  VARCHAR(10)  NULL DEFAULT NULL,
  `executor_corporation_id` INT          NULL DEFAULT NULL,
  `date_founded`            DATETIME     NULL DEFAULT NULL,
  `faction_id`              INT          NULL DEFAULT NULL,
  PRIMARY KEY (`alliance_id`),
  INDEX `creator_idx` (`creator_id` ASC),
  INDEX `creator_corporation_id_idx` (`creator_corporation_id` ASC),
  INDEX `executor_corporation_id_idx` (`executor_corporation_id` ASC),
  INDEX `alliance_name` (`alliance_name` ASC),
  CONSTRAINT `creator_pilot_id`
  FOREIGN KEY (`creator_id`)
  REFERENCES `pilots` (`pilot_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `creator_corporation_id`
  FOREIGN KEY (`creator_corporation_id`)
  REFERENCES `corps` (`corp_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `executor_corporation_id`
  FOREIGN KEY (`executor_corporation_id`)
  REFERENCES `corps` (`corp_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `corps`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `corps` (
  `corp_id`         INT          NOT NULL,
  `corp_name`       VARCHAR(255) NULL DEFAULT NULL,
  `corp_ticker`     VARCHAR(10)  NULL DEFAULT NULL,
  `member_count`    INT          NULL DEFAULT NULL,
  `ceo_id`          INT          NULL DEFAULT NULL,
  `alliance_id`     INT          NULL DEFAULT NULL,
  `description`     LONGTEXT     NULL DEFAULT NULL,
  `tax_rate`        FLOAT        NULL DEFAULT NULL,
  `date_founded`    DATETIME     NULL DEFAULT NULL,
  `creator_id`      INT          NULL DEFAULT NULL,
  `url`             VARCHAR(300) NULL DEFAULT NULL,
  `faction_id`      INT          NULL DEFAULT NULL,
  `home_station_id` INT          NULL DEFAULT NULL,
  `shares`          BIGINT       NULL DEFAULT NULL,
  PRIMARY KEY (`corp_id`),
  INDEX `ceo_idx` (`ceo_id` ASC),
  INDEX `creator_idx` (`creator_id` ASC),
  INDEX `alliance_idx` (`alliance_id` ASC),
  INDEX `corp_name` USING BTREE (`corp_name` ASC),
  CONSTRAINT `corp_in_alliance`
  FOREIGN KEY (`alliance_id`)
  REFERENCES `alliances` (`alliance_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `ceo_of_corp`
  FOREIGN KEY (`ceo_id`)
  REFERENCES `pilots` (`pilot_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `creator_of_corp`
  FOREIGN KEY (`creator_id`)
  REFERENCES `pilots` (`pilot_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `pilots`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pilots` (
  `pilot_id`          INT          NOT NULL,
  `pilot_name`        VARCHAR(255) NULL DEFAULT NULL,
  `pilot_description` LONGTEXT     NULL DEFAULT NULL,
  `corporation_id`    INT          NULL DEFAULT NULL,
  `pilot_birthday`    DATETIME     NULL DEFAULT NULL,
  `gender`            VARCHAR(45)  NULL DEFAULT NULL,
  `race_id`           INT          NULL DEFAULT NULL,
  `bloodline_id`      INT          NULL DEFAULT NULL,
  `ancestry_id`       INT          NULL DEFAULT NULL,
  `security_status`   FLOAT        NULL DEFAULT 0,
  `faction_id`        INT          NULL DEFAULT NULL,
  PRIMARY KEY (`pilot_id`),
  INDEX `corp_idx` (`corporation_id` ASC),
  INDEX `pilot_name` USING BTREE (`pilot_name` ASC),
  CONSTRAINT `pilot_in_corp`
  FOREIGN KEY (`corporation_id`)
  REFERENCES `corps` (`corp_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `zk_kills`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `zk_kills` (
  `killmail_id`   INT            NOT NULL,
  `killmail_time` DATETIME       NOT NULL,
  `system_id`     INT            NOT NULL,
  `fittedValue`   DECIMAL(24, 2) NOT NULL DEFAULT 0,
  `totalValue`    DECIMAL(24, 2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`killmail_id`),
  INDEX `system_idx` (`system_id` ASC),
  CONSTRAINT `system`
  FOREIGN KEY (`system_id`)
  REFERENCES `systems` (`system_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `item_category`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `item_category` (
  `category_id`        INT          NOT NULL,
  `category_name`      VARCHAR(250) NULL DEFAULT NULL,
  `category_published` TINYINT      NULL DEFAULT NULL,
  PRIMARY KEY (`category_id`)
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `item_groups`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `item_groups` (
  `group_id`         INT          NOT NULL,
  `group_name`       VARCHAR(250) NULL DEFAULT NULL,
  `published`        TINYINT      NULL DEFAULT NULL,
  `item_category_fk` INT          NULL DEFAULT NULL,
  PRIMARY KEY (`group_id`),
  INDEX `category_idx` (`item_category_fk` ASC),
  CONSTRAINT `category`
  FOREIGN KEY (`item_category_fk`)
  REFERENCES `item_category` (`category_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `item_types`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `item_types` (
  `type_id`          INT          NOT NULL,
  `type_name`        VARCHAR(255) NULL DEFAULT NULL,
  `type_description` LONGTEXT     NULL DEFAULT NULL,
  `type_published`   TINYINT      NULL DEFAULT NULL,
  `group_id_fk`      INT          NULL DEFAULT NULL,
  PRIMARY KEY (`type_id`),
  INDEX `group_id_idx` (`group_id_fk` ASC),
  INDEX `type_name` USING BTREE (`type_name` ASC),
  CONSTRAINT `group_id`
  FOREIGN KEY (`group_id_fk`)
  REFERENCES `item_groups` (`group_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `zk_involved`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `zk_involved` (
  `kill_id`        INT     NOT NULL,
  `character_id`   INT     NULL     DEFAULT NULL,
  `corporation_id` INT     NULL     DEFAULT NULL,
  `alliance_id`    INT     NULL     DEFAULT NULL,
  `faction_id`     INT     NULL     DEFAULT NULL,
  `ship_type_id`   INT     NULL     DEFAULT NULL,
  `weapon_type_id` INT     NULL     DEFAULT NULL,
  `damage`         FLOAT   NOT NULL DEFAULT 0,
  `is_final_blow`  TINYINT NOT NULL DEFAULT 0,
  `is_victim`      TINYINT NOT NULL DEFAULT 0,
  INDEX `charater_id_idx` (`character_id` ASC),
  INDEX `corp_idx` (`corporation_id` ASC),
  INDEX `alliance_idx` (`alliance_id` ASC),
  INDEX `kill_id_idx` (`kill_id` ASC),
  INDEX `involved_ship_type_idx` (`ship_type_id` ASC),
  INDEX `involved_weapon_type_idx` (`weapon_type_id` ASC),
  CONSTRAINT `involved_pilot`
  FOREIGN KEY (`character_id`)
  REFERENCES `pilots` (`pilot_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `involved_corp`
  FOREIGN KEY (`corporation_id`)
  REFERENCES `corps` (`corp_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `involved_alliance`
  FOREIGN KEY (`alliance_id`)
  REFERENCES `alliances` (`alliance_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `involved_kill_id`
  FOREIGN KEY (`kill_id`)
  REFERENCES `zk_kills` (`killmail_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `involved_ship_type`
  FOREIGN KEY (`ship_type_id`)
  REFERENCES `item_types` (`type_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `involved_weapon_type`
  FOREIGN KEY (`weapon_type_id`)
  REFERENCES `item_types` (`type_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `discord_servers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `discord_servers` (
  `server_id`   BIGINT       NOT NULL,
  `server_name` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`server_id`)
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `discord_channels`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `discord_channels` (
  `channel_id`            BIGINT       NOT NULL,
  `channel_name`          VARCHAR(255) NULL     DEFAULT NULL,
  `display_statusOnStart` TINYINT      NOT NULL DEFAULT 0,
  `server_id`             BIGINT       NULL     DEFAULT NULL,
  PRIMARY KEY (`channel_id`),
  INDEX `d_server_idx` (`server_id` ASC),
  CONSTRAINT `d_server`
  FOREIGN KEY (`server_id`)
  REFERENCES `discord_servers` (`server_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `discord_EntityFeed`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `discord_EntityFeed` (
  `EntityFeed_channel`    BIGINT  NOT NULL,
  `is_running`            TINYINT NOT NULL DEFAULT 0,
  `display_statusOnStart` TINYINT NOT NULL DEFAULT 1,
  INDEX `channel_idx` (`EntityFeed_channel` ASC),
  PRIMARY KEY (`EntityFeed_channel`),
  CONSTRAINT `channel`
  FOREIGN KEY (`EntityFeed_channel`)
  REFERENCES `discord_channels` (`channel_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `discord_EntityFeed_tracking`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `discord_EntityFeed_tracking` (
  `EntityFeed_fk`          BIGINT         NOT NULL,
  `alliance_tracking`      INT            NULL     DEFAULT NULL,
  `corp_tracking`          INT            NULL     DEFAULT NULL,
  `pilot_tracking`         INT            NULL     DEFAULT NULL,
  `ignore_citadel`         TINYINT        NOT NULL DEFAULT 0,
  `ignore_deployable`      TINYINT        NOT NULL DEFAULT 0,
  `pod_isk_floor`          DECIMAL(24, 2) NOT NULL DEFAULT 20000000000000,
  `show_loses`             TINYINT        NOT NULL DEFAULT 1,
  `show_kills`             TINYINT        NOT NULL DEFAULT 1,
  `mentionOnKill_iskFloor` DECIMAL(24, 2) NOT NULL DEFAULT 20000000000000,
  `mentionOnLoss_iskFloor` DECIMAL(24, 2) NOT NULL DEFAULT 20000000000000,
  INDEX `alliance_tracking_idx` (`alliance_tracking` ASC),
  INDEX `corp_tracking_idx` (`corp_tracking` ASC),
  INDEX `pilot_tracking_idx` (`pilot_tracking` ASC),
  INDEX `setting_for_killfeed_idx` (`EntityFeed_fk` ASC),
  PRIMARY KEY (`EntityFeed_fk`),
  CONSTRAINT `alliance_tracking`
  FOREIGN KEY (`alliance_tracking`)
  REFERENCES `alliances` (`alliance_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `corp_tracking`
  FOREIGN KEY (`corp_tracking`)
  REFERENCES `corps` (`corp_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `pilot_tracking`
  FOREIGN KEY (`pilot_tracking`)
  REFERENCES `pilots` (`pilot_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `setting_for_EntityFeed`
  FOREIGN KEY (`EntityFeed_fk`)
  REFERENCES `discord_EntityFeed` (`EntityFeed_channel`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `discord_EntityFeed_posted`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `discord_EntityFeed_posted` (
  `kill_id_posted`       INT      NOT NULL,
  `EntityFeed_posted_to` BIGINT   NOT NULL,
  `posted_date`          DATETIME NOT NULL,
  INDEX `kill_posted_idx` (`kill_id_posted` ASC),
  INDEX `posted_to_feed_idx` (`EntityFeed_posted_to` ASC),
  PRIMARY KEY (`EntityFeed_posted_to`, `kill_id_posted`),
  CONSTRAINT `kill_posted`
  FOREIGN KEY (`kill_id_posted`)
  REFERENCES `zk_kills` (`killmail_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `posted_to_feed`
  FOREIGN KEY (`EntityFeed_posted_to`)
  REFERENCES `discord_EntityFeed` (`EntityFeed_channel`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `discord_CapRadar`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `discord_CapRadar` (
  `channel`               BIGINT                                  NOT NULL,
  `display_statusOnStart` TINYINT                                 NOT NULL DEFAULT 1,
  `is_running`            TINYINT                                 NOT NULL DEFAULT 1,
  `track_supers`          TINYINT                                 NOT NULL DEFAULT 1,
  `track_capitals`        TINYINT                                 NOT NULL DEFAULT 1,
  `track_blops`           TINYINT                                 NOT NULL DEFAULT 0,
  `system_base`           INT                                     NOT NULL DEFAULT 30000142,
  `maxLY_fromBase`        INT                                     NOT NULL DEFAULT 10,
  `max_Age`               MEDIUMINT ZEROFILL                      NOT NULL DEFAULT 45
  COMMENT 'max age in minutes',
  `super_notification`    ENUM ('@everyone', '@here', 'disabled') NOT NULL DEFAULT 'disabled',
  `capital_notification`  ENUM ('@everyone', '@here', 'disabled') NOT NULL DEFAULT 'disabled',
  `blops_notification`    ENUM ('@everyone', '@here', 'disabled') NOT NULL DEFAULT 'disabled',
  PRIMARY KEY (`channel`),
  INDEX `system_idx` (`system_base` ASC),
  CONSTRAINT `cap_radar_channel`
  FOREIGN KEY (`channel`)
  REFERENCES `discord_channels` (`channel_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `cr_system_track`
  FOREIGN KEY (`system_base`)
  REFERENCES `systems` (`system_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `discord_CapRadar_ignore_pilots`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `discord_CapRadar_ignore_pilots` (
  `channel_cr` BIGINT NOT NULL,
  `pilot_id`   INT    NOT NULL,
  INDEX `pilot_ignore_idx` (`pilot_id` ASC),
  PRIMARY KEY (`channel_cr`, `pilot_id`),
  CONSTRAINT `cap_radar`
  FOREIGN KEY (`channel_cr`)
  REFERENCES `discord_CapRadar` (`channel`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `pilot_ignore`
  FOREIGN KEY (`pilot_id`)
  REFERENCES `pilots` (`pilot_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `discord_CapRadar_posted`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `discord_CapRadar_posted` (
  `kill_id_posted`     INT      NOT NULL,
  `CapRadar_posted_to` BIGINT   NOT NULL,
  `posted_date`        DATETIME NOT NULL,
  PRIMARY KEY (`kill_id_posted`, `CapRadar_posted_to`),
  INDEX `cr_posted_to_idx` (`CapRadar_posted_to` ASC),
  CONSTRAINT `cr_kill_posted`
  FOREIGN KEY (`kill_id_posted`)
  REFERENCES `zk_kills` (`killmail_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `cr_posted_to`
  FOREIGN KEY (`CapRadar_posted_to`)
  REFERENCES `discord_CapRadar` (`channel`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `discord_CapRadar_ignore_corps`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `discord_CapRadar_ignore_corps` (
  `channel_cr` BIGINT NOT NULL,
  `corp_id`    INT    NOT NULL,
  PRIMARY KEY (`channel_cr`, `corp_id`),
  INDEX `corp_ignored_idx` (`corp_id` ASC),
  CONSTRAINT `cap_radar1`
  FOREIGN KEY (`channel_cr`)
  REFERENCES `discord_CapRadar` (`channel`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `corp_ignored`
  FOREIGN KEY (`corp_id`)
  REFERENCES `corps` (`corp_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `discord_CapRadar_ignore_alliances`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `discord_CapRadar_ignore_alliances` (
  `channel_cr`  BIGINT NOT NULL,
  `alliance_id` INT    NOT NULL,
  PRIMARY KEY (`channel_cr`, `alliance_id`),
  INDEX `alliance_ignore_idx` (`alliance_id` ASC),
  CONSTRAINT `cap_radar2`
  FOREIGN KEY (`channel_cr`)
  REFERENCES `discord_CapRadar` (`channel`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `alliance_ignore`
  FOREIGN KEY (`alliance_id`)
  REFERENCES `alliances` (`alliance_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Placeholder table for view `pilots_to_kms`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pilots_to_kms` (
  `character_id`    INT,
  `pilot_name`      INT,
  `corporation_id`  INT,
  `corp_name`       INT,
  `corp_ticker`     INT,
  `alliance_id`     INT,
  `alliance_name`   INT,
  `alliance_ticker` INT,
  `ship_type_id`    INT,
  `ship_name`       INT,
  `is_victim`       INT,
  `killmail_time`   INT,
  `system_id`       INT,
  `system_name`     INT,
  `region_name`     INT,
  `is_super`        INT
);

-- -----------------------------------------------------
-- Placeholder table for view `ships`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ships` (
  `type_id`          INT,
  `type_name`        INT,
  `type_description` INT,
  `group_id`         INT,
  `group_name`       INT,
  `category_id`      INT,
  `category_name`    INT
);

-- -----------------------------------------------------
-- Placeholder table for view `kill_id_victimFB`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kill_id_victimFB` (
  `kill_id`               INT,
  `kill_time`             INT,
  `totalValue`            INT,
  `total_involved`        INT,
  `pilot_id`              INT,
  `pilot_name`            INT,
  `corp_id`               INT,
  `corp_name`             INT,
  `corp_ticker`           INT,
  `alliance_id`           INT,
  `alliance_name`         INT,
  `alliance_ticker`       INT,
  `faction_id`            INT,
  `system_id`             INT,
  `system_name`           INT,
  `region_name`           INT,
  `damage_taken`          INT,
  `ship_id`               INT,
  `ship_name`             INT,
  `ship_group_id`         INT,
  `ship_group_name`       INT,
  `ship_category_id`      INT,
  `ship_category_name`    INT,
  `fb_pilot_id`           INT,
  `fb_pilot_name`         INT,
  `fb_corp_id`            INT,
  `fb_corp_name`          INT,
  `fb_corp_ticker`        INT,
  `fb_alliance_id`        INT,
  `fb_alliance_name`      INT,
  `fb_alliance_ticker`    INT,
  `fb_damage_done`        INT,
  `fb_ship_id`            INT,
  `fb_ship_name`          INT,
  `fb_ship_group_id`      INT,
  `fb_ship_group_name`    INT,
  `fb_ship_category_id`   INT,
  `fb_ship_category_name` INT
);

-- -----------------------------------------------------
-- Placeholder table for view `kills_inv_SuperOrCap120M`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kills_inv_SuperOrCap120M` (
  `kill_id`   INT,
  `kill_time` INT,
  `system_id` INT
);

-- -----------------------------------------------------
-- View `pilots_to_kms`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pilots_to_kms`;
CREATE OR REPLACE VIEW `pilots_to_kms` AS
  SELECT
    zk_involved.character_id,
    pilots.pilot_name,
    zk_involved.corporation_id,
    corps.corp_name,
    corps.corp_ticker,
    zk_involved.alliance_id,
    alliances.alliance_name,
    alliances.ticker AS alliance_ticker,
    zk_involved.ship_type_id,
    ships.type_name  AS ship_name,
    zk_involved.is_victim,
    zk_kills.killmail_time,
    zk_kills.system_id,
    systems.system_name,
    regions.region_name,
    (CASE WHEN (ships.group_id = 30 OR ships.group_id = 659)
      THEN TRUE
     ELSE FALSE END) AS is_super
  FROM pilots
    INNER JOIN zk_involved ON pilots.pilot_id = zk_involved.character_id
    INNER JOIN zk_kills ON zk_involved.kill_id = zk_kills.killmail_id
    LEFT JOIN corps ON zk_involved.corporation_id = corps.corp_id
    LEFT JOIN alliances ON zk_involved.alliance_id = alliances.alliance_id
    LEFT JOIN systems ON zk_kills.system_id = systems.system_id
    LEFT JOIN constellations ON systems.constellation_id_fk = constellations.constellation_id
    LEFT JOIN regions ON constellations.region_id_fk = regions.region_id
    INNER JOIN ships ON zk_involved.ship_type_id = ships.type_id
  WHERE ships.group_id != 29 AND character_id IS NOT NULL;

-- -----------------------------------------------------
-- View `ships`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ships`;
CREATE OR REPLACE VIEW `ships` AS
  SELECT
    item_types.type_id,
    item_types.type_name,
    item_types.type_description,
    item_groups.group_id,
    item_groups.group_name,
    item_category.category_id,
    item_category.category_name
  FROM item_types
    INNER JOIN item_groups ON item_types.group_id_fk = item_groups.group_id
    INNER JOIN item_category ON item_groups.item_category_fk = item_category.category_id
  WHERE item_category.category_name = 'Ship';

-- -----------------------------------------------------
-- View `kill_id_victimFB`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `kill_id_victimFB`;
CREATE OR REPLACE VIEW `kill_id_victimFB` AS
  SELECT final.*
  FROM
    (SELECT
       victim.*,
       final_blow.fb_pilot_id,
       final_blow.fb_pilot_name,
       final_blow.fb_corp_id,
       final_blow.fb_corp_name,
       final_blow.fb_corp_ticker,
       final_blow.fb_alliance_id,
       final_blow.fb_alliance_name,
       final_blow.fb_alliance_ticker,
       fb_damage_done,
       fb_ship_id,
       fb_ship_name,
       fb_ship_group_id,
       fb_ship_group_name,
       fb_ship_category_id,
       fb_ship_category_name
     FROM
       (
         SELECT
           iv.kill_id,
           k.killmail_time                                               AS kill_time,
           k.totalValue,
           (SELECT count(*)
            FROM zk_involved AS inv_c
            WHERE inv_c.kill_id = k.killmail_id AND NOT inv_c.is_victim) AS total_involved,
           iv.character_id                                               AS pilot_id,
           pilots.pilot_name,
           iv.corporation_id                                             AS corp_id,
           corps.corp_name,
           corps.corp_ticker                                             AS corp_ticker,
           iv.alliance_id,
           alliances.alliance_name,
           alliances.ticker                                              AS alliance_ticker,
           iv.faction_id,
           sy.system_id,
           sy.system_name,
           rg.region_name,
           damage                                                        AS damage_taken,
           type_id                                                       AS ship_id,
           type_name                                                     AS ship_name,
           group_id                                                      AS ship_group_id,
           group_name                                                    AS ship_group_name,
           category_id                                                   AS ship_category_id,
           category_name                                                 AS ship_category_name
         FROM zk_involved AS iv
           INNER JOIN item_types ON iv.ship_type_id = item_types.type_id
           INNER JOIN item_groups ON item_types.group_id_fk = item_groups.group_id
           INNER JOIN item_category ON item_groups.item_category_fk = item_category.category_id
           INNER JOIN zk_kills AS k ON iv.kill_id = k.killmail_id
           INNER JOIN systems AS sy ON k.system_id = sy.system_id
           INNER JOIN constellations AS con ON sy.constellation_id_fk = con.constellation_id
           INNER JOIN regions AS rg ON con.region_id_fk = rg.region_id
           LEFT JOIN pilots ON iv.character_id = pilots.pilot_id
           LEFT JOIN corps ON iv.corporation_id = corps.corp_id
           LEFT JOIN alliances ON iv.alliance_id = alliances.alliance_id
         WHERE iv.is_victim = 1
       ) AS victim LEFT JOIN
       (
         SELECT
           fb_i.kill_id,
           fb_i.character_id   AS fb_pilot_id,
           fb_p.pilot_name     AS fb_pilot_name,
           fb_i.corporation_id AS fb_corp_id,
           fb_c.corp_name      AS fb_corp_name,
           fb_c.corp_ticker    AS fb_corp_ticker,
           fb_i.alliance_id    AS fb_alliance_id,
           fb_a.alliance_name  AS fb_alliance_name,
           fb_a.ticker         AS fb_alliance_ticker,
           fb_i.damage         AS fb_damage_done,
           type_id             AS fb_ship_id,
           type_name           AS fb_ship_name,
           group_id            AS fb_ship_group_id,
           group_name          AS fb_ship_group_name,
           category_id         AS fb_ship_category_id,
           category_name       AS fb_ship_category_name
         FROM zk_involved AS fb_i
           LEFT JOIN pilots AS fb_p ON fb_i.character_id = fb_p.pilot_id
           LEFT JOIN corps AS fb_c ON fb_i.corporation_id = fb_c.corp_id
           LEFT JOIN alliances AS fb_a ON fb_i.alliance_id = fb_a.alliance_id
           INNER JOIN item_types ON fb_i.ship_type_id = item_types.type_id
           INNER JOIN item_groups ON item_types.group_id_fk = item_groups.group_id
           INNER JOIN item_category ON item_groups.item_category_fk = item_category.category_id
         WHERE is_final_blow
       ) AS final_blow ON victim.kill_id = final_blow.kill_id
    ) AS final;

-- -----------------------------------------------------
-- View `kills_inv_SuperOrCap120M`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `kills_inv_SuperOrCap120M`;
CREATE OR REPLACE VIEW `kills_inv_SuperOrCap120M` AS
  SELECT
    kill_id,
    killmail_time AS kill_time,
    system_id
  FROM zk_involved
    INNER JOIN zk_kills ON kill_id = killmail_id
    INNER JOIN item_types ON ship_type_id = item_types.type_id
    INNER JOIN item_groups ON group_id_fk = group_id
  WHERE killmail_time > (UTC_TIMESTAMP() - INTERVAL 120 MINUTE)
        AND
        (
          group_id <=> 659
          OR group_id <=> 30
          OR group_id <=> 485
          OR group_id <=> 547
          OR group_id <=> 1538
          OR group_id <=> 883
          OR group_id <=> 898)
        AND NOT is_victim
  GROUP BY killmail_id;

DELIMITER $$
CREATE DEFINER = CURRENT_USER TRIGGER `alliances_BEFORE_INSERT`
  BEFORE INSERT
  ON `alliances`
  FOR EACH ROW
  BEGIN
    IF new.creator_id = 1
    THEN
      SET new.creator_id = NULL;
    END IF;
    IF new.creator_corporation_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `corps` (`corp_id`) VALUES (new.creator_corporation_id);
    END IF;
    IF new.executor_corporation_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `corps` (`corp_id`) VALUES (new.executor_corporation_id);
    END IF;
    IF new.creator_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `pilots` (`pilot_id`) VALUES (new.creator_id);
    END IF;
  END$$

CREATE DEFINER = CURRENT_USER TRIGGER `alliances_BEFORE_UPDATE`
  BEFORE UPDATE
  ON `alliances`
  FOR EACH ROW
  BEGIN
    IF new.creator_id = 1
    THEN
      SET new.creator_id = NULL;
    END IF;
    IF new.creator_corporation_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `corps` (`corp_id`) VALUES (new.creator_corporation_id);
    END IF;
    IF new.executor_corporation_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `corps` (`corp_id`) VALUES (new.executor_corporation_id);
    END IF;
    IF new.creator_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `pilots` (`pilot_id`) VALUES (new.creator_id);
    END IF;
  END$$

CREATE DEFINER = CURRENT_USER TRIGGER `corps_BEFORE_INSERT`
  BEFORE INSERT
  ON `corps`
  FOR EACH ROW
  BEGIN
    IF new.ceo_id = 1
    THEN
      SET new.ceo_id = NULL;
    END IF;
    IF new.creator_id = 1
    THEN
      SET new.creator_id = NULL;
    END IF;
    IF new.alliance_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `alliances` (`alliance_id`) VALUES (new.alliance_id);
    END IF;
    IF new.ceo_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `pilots` (`pilot_id`) VALUES (new.ceo_id);
    END IF;
    IF new.creator_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `pilots` (`pilot_id`) VALUES (new.creator_id);
    END IF;
  END$$

CREATE DEFINER = CURRENT_USER TRIGGER `corps_BEFORE_UPDATE`
  BEFORE UPDATE
  ON `corps`
  FOR EACH ROW
  BEGIN
    IF new.ceo_id = 1
    THEN
      SET new.ceo_id = NULL;
    END IF;
    IF new.creator_id = 1
    THEN
      SET new.creator_id = NULL;
    END IF;
    IF new.alliance_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `alliances` (`alliance_id`) VALUES (new.alliance_id);
    END IF;
    IF new.ceo_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `pilots` (`pilot_id`) VALUES (new.ceo_id);
    END IF;
    IF new.creator_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `pilots` (`pilot_id`) VALUES (new.creator_id);
    END IF;
  END$$

CREATE DEFINER = CURRENT_USER TRIGGER `pilots_BEFORE_INSERT`
  BEFORE INSERT
  ON `pilots`
  FOR EACH ROW
  BEGIN
    IF new.corporation_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `corps` (`corp_id`) VALUES (new.corporation_id);
    END IF;
  END$$

CREATE DEFINER = CURRENT_USER TRIGGER `pilots_BEFORE_UPDATE`
  BEFORE UPDATE
  ON `pilots`
  FOR EACH ROW
  BEGIN
    IF new.corporation_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `corps` (`corp_id`) VALUES (new.corporation_id);
    END IF;
  END$$

CREATE DEFINER = CURRENT_USER TRIGGER `zk_involved_BEFORE_INSERT`
  BEFORE INSERT
  ON `zk_involved`
  FOR EACH ROW
  BEGIN
    IF new.character_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `pilots` (`pilot_id`) VALUES (new.character_id);
    END IF;
    IF new.corporation_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `corps` (`corp_id`) VALUES (new.corporation_id);
    END IF;
    IF new.alliance_id IS NOT NULL
    THEN
      INSERT IGNORE INTO `alliances` (`alliance_id`) VALUES (new.alliance_id);
    END IF;
  END$$

CREATE DEFINER = CURRENT_USER TRIGGER `discord_EntityFeed_tracking_AFTER_INSERT`
  AFTER INSERT
  ON `discord_EntityFeed_tracking`
  FOR EACH ROW
  BEGIN
    INSERT IGNORE INTO discord_EntityFeed_posted (kill_id_posted, EntityFeed_posted_to, posted_date)
      SELECT
        kill_id,
        tr.EntityFeed_fk,
        UTC_TIMESTAMP()
      FROM discord_EntityFeed_tracking AS tr
        INNER JOIN zk_involved AS i
          ON (tr.alliance_tracking IS NOT NULL AND i.alliance_id <=> tr.alliance_tracking)
             OR (tr.corp_tracking IS NOT NULL AND i.corporation_id <=> tr.corp_tracking)
             OR (tr.pilot_tracking IS NOT NULL AND i.character_id <=> tr.pilot_tracking)
      WHERE EntityFeed_fk = new.EntityFeed_fk
      GROUP BY kill_id;
  END$$

CREATE DEFINER = CURRENT_USER TRIGGER `discord_CapRadar_AFTER_INSERT`
  AFTER INSERT
  ON `discord_CapRadar`
  FOR EACH ROW
  BEGIN
    INSERT IGNORE INTO discord_CapRadar_posted (kill_id_posted, CapRadar_posted_to, posted_date)
      SELECT
        zk.kill_id,
        new.channel,
        UTC_TIMESTAMP()
      FROM
        kills_inv_SuperOrCap120M AS zk;
  END$$


DELIMITER ;

SET SQL_MODE = @OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS = @OLD_UNIQUE_CHECKS;
