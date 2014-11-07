-- MySQL Script generated by MySQL Workbench
-- Fri 07 Nov 2014 03:56:40 PM CET
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

-- -----------------------------------------------------
-- Table `runtype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `runtype` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `runtypename` VARCHAR(32) NOT NULL,
  `runtypedesc` VARCHAR(256) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `run`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `run` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `number` INT(11) NOT NULL,
  `runtype_id` BIGINT(20) NOT NULL,
  `timestart` DATETIME NULL DEFAULT NULL,
  `timestop` DATETIME NULL DEFAULT NULL,
  `startcomment` VARCHAR(256) NULL,
  `endcomment` VARCHAR(256) NULL,
  PRIMARY KEY (`id`),
  INDEX `runtype_id` (`runtype_id` ASC),
  CONSTRAINT `runtype_id`
    FOREIGN KEY (`runtype_id`)
    REFERENCES `runtype` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `runtrigger`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `runtrigger` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `run_id` BIGINT NOT NULL,
  `validitystart` DATETIME NULL,
  `validityend` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `run_id_idx` (`run_id` ASC),
  CONSTRAINT `run_id`
    FOREIGN KEY (`run_id`)
    REFERENCES `run` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggerperiodictype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `triggerperiodictype` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `period` INT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggerperiodic`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `triggerperiodic` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `runtrigger_id` BIGINT NOT NULL,
  `triggerperiodictype_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `periodic_runtrigger_id_idx` (`runtrigger_id` ASC),
  INDEX `periodic_triggerperiodictype_id_idx` (`triggerperiodictype_id` ASC),
  CONSTRAINT `periodic_runtrigger_id`
    FOREIGN KEY (`runtrigger_id`)
    REFERENCES `runtrigger` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `periodic_triggerperiodictype_id`
    FOREIGN KEY (`triggerperiodictype_id`)
    REFERENCES `triggerperiodictype` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggernimtype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `triggernimtype` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `mask` CHAR(5) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggernim`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `triggernim` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `runtrigger_id` BIGINT NOT NULL,
  `triggernimtype_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `runtrigger_id_idx` (`runtrigger_id` ASC),
  INDEX `triggernimtype_id_idx` (`triggernimtype_id` ASC),
  CONSTRAINT `nim_runtrigger_id`
    FOREIGN KEY (`runtrigger_id`)
    REFERENCES `runtrigger` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `nim_triggernimtype_id`
    FOREIGN KEY (`triggernimtype_id`)
    REFERENCES `triggernimtype` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggerprimitivetype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `triggerprimitivetype` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `mask` CHAR(3) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggerprimitive`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `triggerprimitive` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `runtrigger_id` BIGINT NOT NULL,
  `triggerprimitivetype_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `runtrigger_id_idx` (`runtrigger_id` ASC),
  INDEX `triggerprimitivetype_id_idx` (`triggerprimitivetype_id` ASC),
  CONSTRAINT `prim_runtrigger_id`
    FOREIGN KEY (`runtrigger_id`)
    REFERENCES `runtrigger` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `prim_triggerprimitivetype_id`
    FOREIGN KEY (`triggerprimitivetype_id`)
    REFERENCES `triggerprimitivetype` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `nimdetname`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `nimdetname` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `detnumber` INT NOT NULL,
  `detname` VARCHAR(32) NOT NULL,
  `validitystart` DATETIME NULL,
  `validityend` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `primitivedetname`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `primitivedetname` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `detnumber` INT NOT NULL,
  `detname` VARCHAR(32) NOT NULL,
  `validitystart` DATETIME NULL,
  `validityend` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `enableddetectors`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `enableddetectors` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `run_id` BIGINT NOT NULL,
  `detectorid` INT NOT NULL,
  `detectorname` VARCHAR(32) NOT NULL,
  `validitystart` DATETIME NULL,
  `validityend` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `detector_run_id_idx` (`run_id` ASC),
  CONSTRAINT `detector_run_id`
    FOREIGN KEY (`run_id`)
    REFERENCES `run` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggersync`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `triggersync` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `runtrigger_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_triggersync_1_idx` (`runtrigger_id` ASC),
  CONSTRAINT `fk_triggersync_1`
    FOREIGN KEY (`runtrigger_id`)
    REFERENCES `runtrigger` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggercalib`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `triggercalib` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `runtrigger_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_triggercalib_1_idx` (`runtrigger_id` ASC),
  CONSTRAINT `fk_triggercalib_1`
    FOREIGN KEY (`runtrigger_id`)
    REFERENCES `runtrigger` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Placeholder table for view `viewnim`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `viewnim` (`run_id` INT, `triggerstring` INT);

-- -----------------------------------------------------
-- Placeholder table for view `viewperiodic`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `viewperiodic` (`run_id` INT, `id` INT, `period` INT);

-- -----------------------------------------------------
-- Placeholder table for view `viewnimtype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `viewnimtype` (`run_id` INT, `id` INT, `validitystart` INT, `validityend` INT, `mask` INT);

-- -----------------------------------------------------
-- Placeholder table for view `viewnimdetail`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `viewnimdetail` (`run_id` INT, `validitystart` INT, `validityend` INT, `det_0` INT, `det_1` INT, `det_2` INT, `det_3` INT, `det_4` INT);

-- -----------------------------------------------------
-- Placeholder table for view `viewnimname`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `viewnimname` (`run_id` INT, `det_0` INT, `det_1` INT, `det_2` INT, `det_3` INT, `det_4` INT);

-- -----------------------------------------------------
-- Placeholder table for view `viewtrigger`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `viewtrigger` (`run_id` INT, `triggerstring` INT);

-- -----------------------------------------------------
-- Placeholder table for view `viewenableddet`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `viewenableddet` (`run_id` INT, `enabledstring` INT);

-- -----------------------------------------------------
-- Placeholder table for view `viewperiodicmerged`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `viewperiodicmerged` (`run_id` INT, `periodstring` INT);

-- -----------------------------------------------------
-- Placeholder table for view `viewnimmerged`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `viewnimmerged` (`run_id` INT, `nimstring` INT);

-- -----------------------------------------------------
-- View `viewnim`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `viewnim`;
CREATE  OR REPLACE VIEW `viewnim` AS
    SELECT 
        viewnimname.run_id,
        CONCAT_WS('x',
                viewnimname.det_0,
                viewnimname.det_1,
                viewnimname.det_2,
                viewnimname.det_3,
                viewnimname.det_4) AS triggerstring
    FROM
        viewnimname;

-- -----------------------------------------------------
-- View `viewperiodic`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `viewperiodic`;
CREATE  OR REPLACE VIEW `viewperiodic` AS
    SELECT 
        runtrigger.run_id,
        runtrigger.id,
        triggerperiodictype.period
    FROM
        runtrigger
            INNER JOIN
        (triggerperiodic, triggerperiodictype) ON (triggerperiodic.runtrigger_id = runtrigger.id
            AND triggerperiodictype.id = triggerperiodic.triggerperiodictype_id);

-- -----------------------------------------------------
-- View `viewnimtype`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `viewnimtype`;
CREATE  OR REPLACE VIEW `viewnimtype` AS
    SELECT 
        runtrigger.run_id,
        runtrigger.id,
        runtrigger.validitystart,
        runtrigger.validityend,
        triggernimtype.mask
    FROM
        runtrigger
            INNER JOIN
        (triggernim, triggernimtype) ON (triggernim.runtrigger_id = runtrigger.id
            AND triggernim.triggernimtype_id = triggernimtype.id);

-- -----------------------------------------------------
-- View `viewnimdetail`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `viewnimdetail`;
CREATE  OR REPLACE VIEW `viewnimdetail` AS
    SELECT 
        viewnimtype.run_id,
        viewnimtype.validitystart,
        viewnimtype.validityend,
        SUBSTRING(viewnimtype.mask, 1, 1) AS det_0,
        SUBSTRING(viewnimtype.mask, 2, 1) AS det_1,
        SUBSTRING(viewnimtype.mask, 3, 1) AS det_2,
        SUBSTRING(viewnimtype.mask, 4, 1) AS det_3,
        SUBSTRING(viewnimtype.mask, 5, 1) AS det_4
    FROM
        viewnimtype;

-- -----------------------------------------------------
-- View `viewnimname`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `viewnimname`;
CREATE  OR REPLACE VIEW `viewnimname` AS
    SELECT DISTINCT
        viewnimdetail.run_id,
        IF(det_0 = '1',
            D0.detname,
            IF(det_0 = 2,
                CONCAT('!', D0.detname),
                NULL)) AS det_0,
        IF(det_1 = '1',
            D1.detname,
            IF(det_1 = 2,
                CONCAT('!', D1.detname),
                NULL)) AS det_1,
        IF(det_2 = '1',
            D2.detname,
            IF(det_2 = 2,
                CONCAT('!', D2.detname),
                NULL)) AS det_2,
        IF(det_3 = '1',
            D3.detname,
            IF(det_3 = 2,
                CONCAT('!', D3.detname),
                NULL)) AS det_3,
        IF(det_4 = '1',
            D4.detname,
            IF(det_4 = 2,
                CONCAT('!', D4.detname),
                NULL)) AS det_4
    FROM
        viewnimdetail
            INNER JOIN
        (nimdetname AS D0, nimdetname AS D1, nimdetname AS D2, nimdetname AS D3, nimdetname AS D4) ON (D0.validitystart < viewnimdetail.validitystart
            AND D1.validitystart < viewnimdetail.validitystart
            AND D2.validitystart < viewnimdetail.validitystart
            AND D3.validitystart < viewnimdetail.validitystart
            AND D4.validitystart < viewnimdetail.validitystart
            AND D0.detnumber = 0
            AND D1.detnumber = 1
            AND D2.detnumber = 2
            AND D3.detnumber = 3
            AND D4.detnumber = 4)
;

-- -----------------------------------------------------
-- View `viewtrigger`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `viewtrigger`;
CREATE  OR REPLACE VIEW `viewtrigger` AS
    SELECT 
        viewperiodicmerged.run_id,
        CONCAT_WS('+',
                viewperiodicmerged.periodstring,
                GROUP_CONCAT(DISTINCT viewnimmerged.nimstring
                    SEPARATOR '+')) AS triggerstring
    FROM
        viewperiodicmerged
            LEFT JOIN
        viewnimmerged ON (viewperiodicmerged.run_id = viewnimmerged.run_id)
    GROUP BY viewperiodicmerged.run_id 
    UNION SELECT 
        viewnimmerged.run_id,
        CONCAT_WS('+',
                viewperiodicmerged.periodstring,
                GROUP_CONCAT(DISTINCT viewnimmerged.nimstring
                    SEPARATOR '+')) AS triggerstring
    FROM
        viewperiodicmerged
            RIGHT JOIN
        viewnimmerged ON (viewperiodicmerged.run_id = viewnimmerged.run_id)
    GROUP BY viewnimmerged.run_id;

-- -----------------------------------------------------
-- View `viewenableddet`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `viewenableddet`;
CREATE  OR REPLACE VIEW `viewenableddet` AS
    SELECT 
        enableddetectors.run_id,
        GROUP_CONCAT(DISTINCT enableddetectors.detectorname
            ORDER BY enableddetectors.detectorname
            SEPARATOR '+') as enabledstring
    FROM
        enableddetectors
    GROUP BY enableddetectors.run_id;

-- -----------------------------------------------------
-- View `viewperiodicmerged`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `viewperiodicmerged`;
CREATE  OR REPLACE VIEW `viewperiodicmerged` AS
    SELECT 
        viewperiodic.run_id,
        CONCAT('Period:',
                GROUP_CONCAT(DISTINCT viewperiodic.period
                    SEPARATOR ',')) AS periodstring
    FROM
        viewperiodic
    GROUP BY viewperiodic.run_id;

-- -----------------------------------------------------
-- View `viewnimmerged`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `viewnimmerged`;
CREATE  OR REPLACE VIEW `viewnimmerged` AS
    SELECT 
        viewnim.run_id,
        viewnim.triggerstring AS nimstring
    FROM
        viewnim;
