-- MySQL dump 10.13  Distrib 5.6.24, for Win64 (x86_64)
--
-- Host: localhost    Database: testRC
-- ------------------------------------------------------
-- Server version	5.1.73

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `enableddetectors`
--

DROP TABLE IF EXISTS `enableddetectors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `enableddetectors` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `run_id` bigint(20) NOT NULL,
  `detectorid` int(11) NOT NULL,
  `detectorname` varchar(32) NOT NULL,
  `validitystart` datetime DEFAULT NULL,
  `validityend` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `detector_run_id_idx` (`run_id`),
  CONSTRAINT `detector_run_id` FOREIGN KEY (`run_id`) REFERENCES `run` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=25923 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `nimdetname`
--

DROP TABLE IF EXISTS `nimdetname`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `nimdetname` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `detnumber` int(11) NOT NULL,
  `detname` varchar(32) NOT NULL,
  `validitystart` datetime DEFAULT NULL,
  `validityend` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `primitivedetname`
--

DROP TABLE IF EXISTS `primitivedetname`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `primitivedetname` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `detnumber` int(11) NOT NULL,
  `detmask` char(10) NOT NULL,
  `detname` varchar(32) NOT NULL,
  `validitystart` datetime DEFAULT NULL,
  `validityend` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `run`
--

DROP TABLE IF EXISTS `run`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `run` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `number` int(11) NOT NULL,
  `runtype_id` bigint(20) NOT NULL,
  `timestart` datetime DEFAULT NULL,
  `timestop` datetime DEFAULT NULL,
  `startcomment` varchar(256) DEFAULT NULL,
  `endcomment` varchar(256) DEFAULT NULL,
  `totalburst` int(11) DEFAULT NULL,
  `totalL0` bigint(20) DEFAULT NULL,
  `totalL1` bigint(20) DEFAULT NULL,
  `totalL2` bigint(20) DEFAULT NULL,
  `totalMerger` bigint(20) DEFAULT NULL,
  `usercomment` varchar(4000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `runtype_id` (`runtype_id`),
  CONSTRAINT `runtype_id` FOREIGN KEY (`runtype_id`) REFERENCES `runtype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3386 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `runtrigger`
--

DROP TABLE IF EXISTS `runtrigger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `runtrigger` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `run_id` bigint(20) NOT NULL,
  `validitystart` datetime DEFAULT NULL,
  `validityend` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `run_id_idx` (`run_id`),
  CONSTRAINT `run_id` FOREIGN KEY (`run_id`) REFERENCES `run` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=4420 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `runtype`
--

DROP TABLE IF EXISTS `runtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `runtype` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `runtypename` varchar(32) NOT NULL,
  `runtypedesc` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `triggercalib`
--

DROP TABLE IF EXISTS `triggercalib`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `triggercalib` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `runtrigger_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_triggercalib_1_idx` (`runtrigger_id`),
  CONSTRAINT `fk_triggercalib_1` FOREIGN KEY (`runtrigger_id`) REFERENCES `runtrigger` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `triggernim`
--

DROP TABLE IF EXISTS `triggernim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `triggernim` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `runtrigger_id` bigint(20) NOT NULL,
  `triggernimtype_id` bigint(20) NOT NULL,
  `triggernimdownscaling` int(11) DEFAULT NULL,
  `triggernimreference` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `runtrigger_id_idx` (`runtrigger_id`),
  KEY `triggernimtype_id_idx` (`triggernimtype_id`),
  CONSTRAINT `nim_runtrigger_id` FOREIGN KEY (`runtrigger_id`) REFERENCES `runtrigger` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `nim_triggernimtype_id` FOREIGN KEY (`triggernimtype_id`) REFERENCES `triggernimtype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1094 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `triggernimtype`
--

DROP TABLE IF EXISTS `triggernimtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `triggernimtype` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `mask` char(5) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `triggerperiodic`
--

DROP TABLE IF EXISTS `triggerperiodic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `triggerperiodic` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `runtrigger_id` bigint(20) NOT NULL,
  `triggerperiodictype_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `periodic_runtrigger_id_idx` (`runtrigger_id`),
  KEY `periodic_triggerperiodictype_id_idx` (`triggerperiodictype_id`),
  CONSTRAINT `periodic_runtrigger_id` FOREIGN KEY (`runtrigger_id`) REFERENCES `runtrigger` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `periodic_triggerperiodictype_id` FOREIGN KEY (`triggerperiodictype_id`) REFERENCES `triggerperiodictype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1052 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `triggerperiodictype`
--

DROP TABLE IF EXISTS `triggerperiodictype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `triggerperiodictype` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `period` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `triggerprimitive`
--

DROP TABLE IF EXISTS `triggerprimitive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `triggerprimitive` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `runtrigger_id` bigint(20) NOT NULL,
  `triggerprimitivetype_id` bigint(20) NOT NULL,
  `triggerprimitivedownscaling` int(11) DEFAULT NULL,
  `triggerprimitivereference` int(11) DEFAULT NULL,
  `masknumber` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `runtrigger_id_idx` (`runtrigger_id`),
  KEY `triggerprimitivetype_id_idx` (`triggerprimitivetype_id`),
  CONSTRAINT `prim_runtrigger_id` FOREIGN KEY (`runtrigger_id`) REFERENCES `runtrigger` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `prim_triggerprimitivetype_id` FOREIGN KEY (`triggerprimitivetype_id`) REFERENCES `triggerprimitivetype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=6010 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `triggerprimitivetype`
--

DROP TABLE IF EXISTS `triggerprimitivetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `triggerprimitivetype` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `maskA` char(10) NOT NULL,
  `maskB` char(10) NOT NULL,
  `maskC` char(10) NOT NULL,
  `maskD` char(10) NOT NULL,
  `maskE` char(10) NOT NULL,
  `maskF` char(10) NOT NULL,
  `maskG` char(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=867 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `triggersync`
--

DROP TABLE IF EXISTS `triggersync`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `triggersync` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `runtrigger_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_triggersync_1_idx` (`runtrigger_id`),
  CONSTRAINT `fk_triggersync_1` FOREIGN KEY (`runtrigger_id`) REFERENCES `runtrigger` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `viewcalibration`
--

DROP TABLE IF EXISTS `viewcalibration`;
/*!50001 DROP VIEW IF EXISTS `viewcalibration`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewcalibration` AS SELECT 
 1 AS `run_id`,
 1 AS `id`,
 1 AS `validitystart`,
 1 AS `validityend`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewenableddet`
--

DROP TABLE IF EXISTS `viewenableddet`;
/*!50001 DROP VIEW IF EXISTS `viewenableddet`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewenableddet` AS SELECT 
 1 AS `run_id`,
 1 AS `enabledstring`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewnim`
--

DROP TABLE IF EXISTS `viewnim`;
/*!50001 DROP VIEW IF EXISTS `viewnim`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewnim` AS SELECT 
 1 AS `nim_id`,
 1 AS `run_id`,
 1 AS `triggerstring`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewnimdetail`
--

DROP TABLE IF EXISTS `viewnimdetail`;
/*!50001 DROP VIEW IF EXISTS `viewnimdetail`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewnimdetail` AS SELECT 
 1 AS `nim_id`,
 1 AS `run_id`,
 1 AS `validitystart`,
 1 AS `validityend`,
 1 AS `triggernimdownscaling`,
 1 AS `triggernimreference`,
 1 AS `det_0`,
 1 AS `det_1`,
 1 AS `det_2`,
 1 AS `det_3`,
 1 AS `det_4`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewnimmerged`
--

DROP TABLE IF EXISTS `viewnimmerged`;
/*!50001 DROP VIEW IF EXISTS `viewnimmerged`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewnimmerged` AS SELECT 
 1 AS `run_id`,
 1 AS `nimstring`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewnimname`
--

DROP TABLE IF EXISTS `viewnimname`;
/*!50001 DROP VIEW IF EXISTS `viewnimname`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewnimname` AS SELECT 
 1 AS `nim_id`,
 1 AS `run_id`,
 1 AS `validitystart`,
 1 AS `validityend`,
 1 AS `triggernimdownscaling`,
 1 AS `triggernimreference`,
 1 AS `det_0`,
 1 AS `det_1`,
 1 AS `det_2`,
 1 AS `det_3`,
 1 AS `det_4`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewnimtype`
--

DROP TABLE IF EXISTS `viewnimtype`;
/*!50001 DROP VIEW IF EXISTS `viewnimtype`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewnimtype` AS SELECT 
 1 AS `run_id`,
 1 AS `id`,
 1 AS `validitystart`,
 1 AS `validityend`,
 1 AS `mask`,
 1 AS `triggernimdownscaling`,
 1 AS `triggernimreference`,
 1 AS `nim_id`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewperiodic`
--

DROP TABLE IF EXISTS `viewperiodic`;
/*!50001 DROP VIEW IF EXISTS `viewperiodic`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewperiodic` AS SELECT 
 1 AS `run_id`,
 1 AS `id`,
 1 AS `validitystart`,
 1 AS `validityend`,
 1 AS `frequency`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewperiodicmerged`
--

DROP TABLE IF EXISTS `viewperiodicmerged`;
/*!50001 DROP VIEW IF EXISTS `viewperiodicmerged`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewperiodicmerged` AS SELECT 
 1 AS `run_id`,
 1 AS `periodstring`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewprimitive`
--

DROP TABLE IF EXISTS `viewprimitive`;
/*!50001 DROP VIEW IF EXISTS `viewprimitive`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewprimitive` AS SELECT 
 1 AS `run_id`,
 1 AS `triggerstring`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewprimitivedetail_useless`
--

DROP TABLE IF EXISTS `viewprimitivedetail_useless`;
/*!50001 DROP VIEW IF EXISTS `viewprimitivedetail_useless`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewprimitivedetail_useless` AS SELECT 
 1 AS `run_id`,
 1 AS `validitystart`,
 1 AS `validityend`,
 1 AS `triggerprimitivedownscaling`,
 1 AS `triggerprimitivereference`,
 1 AS `det_0`,
 1 AS `det_1`,
 1 AS `det_2`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewprimitivemerged`
--

DROP TABLE IF EXISTS `viewprimitivemerged`;
/*!50001 DROP VIEW IF EXISTS `viewprimitivemerged`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewprimitivemerged` AS SELECT 
 1 AS `run_id`,
 1 AS `primitivestring`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewprimitivename`
--

DROP TABLE IF EXISTS `viewprimitivename`;
/*!50001 DROP VIEW IF EXISTS `viewprimitivename`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewprimitivename` AS SELECT 
 1 AS `run_id`,
 1 AS `triggerprimitivedownscaling`,
 1 AS `triggerprimitivereference`,
 1 AS `validitystart`,
 1 AS `validityend`,
 1 AS `masknumber`,
 1 AS `maskA`,
 1 AS `maskB`,
 1 AS `maskC`,
 1 AS `maskD`,
 1 AS `maskE`,
 1 AS `maskF`,
 1 AS `maskG`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewprimitivetype`
--

DROP TABLE IF EXISTS `viewprimitivetype`;
/*!50001 DROP VIEW IF EXISTS `viewprimitivetype`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewprimitivetype` AS SELECT 
 1 AS `run_id`,
 1 AS `id`,
 1 AS `validitystart`,
 1 AS `validityend`,
 1 AS `maskA`,
 1 AS `maskB`,
 1 AS `maskC`,
 1 AS `maskD`,
 1 AS `maskE`,
 1 AS `maskF`,
 1 AS `maskG`,
 1 AS `triggerprimitivedownscaling`,
 1 AS `triggerprimitivereference`,
 1 AS `masknumber`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewsync`
--

DROP TABLE IF EXISTS `viewsync`;
/*!50001 DROP VIEW IF EXISTS `viewsync`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewsync` AS SELECT 
 1 AS `run_id`,
 1 AS `id`,
 1 AS `validitystart`,
 1 AS `validityend`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewtrigger`
--

DROP TABLE IF EXISTS `viewtrigger`;
/*!50001 DROP VIEW IF EXISTS `viewtrigger`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewtrigger` AS SELECT 
 1 AS `run_id`,
 1 AS `triggerstring`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `viewtriggerfull`
--

DROP TABLE IF EXISTS `viewtriggerfull`;
/*!50001 DROP VIEW IF EXISTS `viewtriggerfull`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `viewtriggerfull` AS SELECT 
 1 AS `run_id`,
 1 AS `triggerstring`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `viewcalibration`
--

/*!50001 DROP VIEW IF EXISTS `viewcalibration`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewcalibration` AS select `runtrigger`.`run_id` AS `run_id`,`runtrigger`.`id` AS `id`,`runtrigger`.`validitystart` AS `validitystart`,`runtrigger`.`validityend` AS `validityend` from (`triggercalib` left join `runtrigger` on((`triggercalib`.`runtrigger_id` = `runtrigger`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewenableddet`
--

/*!50001 DROP VIEW IF EXISTS `viewenableddet`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewenableddet` AS select `enableddetectors`.`run_id` AS `run_id`,group_concat(distinct `enableddetectors`.`detectorname` order by `enableddetectors`.`detectorname` ASC separator '+') AS `enabledstring` from `enableddetectors` group by `enableddetectors`.`run_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewnim`
--

/*!50001 DROP VIEW IF EXISTS `viewnim`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewnim` AS select `viewnimname`.`nim_id` AS `nim_id`,`viewnimname`.`run_id` AS `run_id`,concat(concat_ws('x',`viewnimname`.`det_0`,`viewnimname`.`det_1`,`viewnimname`.`det_2`,`viewnimname`.`det_3`,`viewnimname`.`det_4`),'/',`viewnimname`.`triggernimdownscaling`,'(',if(isnull(`viewnimname`.`triggernimreference`),-(1),`viewnimname`.`triggernimreference`),')') AS `triggerstring` from `viewnimname` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewnimdetail`
--

/*!50001 DROP VIEW IF EXISTS `viewnimdetail`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewnimdetail` AS select `viewnimtype`.`nim_id` AS `nim_id`,`viewnimtype`.`run_id` AS `run_id`,`viewnimtype`.`validitystart` AS `validitystart`,`viewnimtype`.`validityend` AS `validityend`,`viewnimtype`.`triggernimdownscaling` AS `triggernimdownscaling`,`viewnimtype`.`triggernimreference` AS `triggernimreference`,substr(`viewnimtype`.`mask`,1,1) AS `det_0`,substr(`viewnimtype`.`mask`,2,1) AS `det_1`,substr(`viewnimtype`.`mask`,3,1) AS `det_2`,substr(`viewnimtype`.`mask`,4,1) AS `det_3`,substr(`viewnimtype`.`mask`,5,1) AS `det_4` from `viewnimtype` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewnimmerged`
--

/*!50001 DROP VIEW IF EXISTS `viewnimmerged`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewnimmerged` AS select `viewnim`.`run_id` AS `run_id`,concat('NIM:',group_concat(distinct `viewnim`.`triggerstring` separator '+')) AS `nimstring` from `viewnim` group by `viewnim`.`run_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewnimname`
--

/*!50001 DROP VIEW IF EXISTS `viewnimname`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewnimname` AS select distinct `viewnimdetail`.`nim_id` AS `nim_id`,`viewnimdetail`.`run_id` AS `run_id`,`viewnimdetail`.`validitystart` AS `validitystart`,`viewnimdetail`.`validityend` AS `validityend`,`viewnimdetail`.`triggernimdownscaling` AS `triggernimdownscaling`,`viewnimdetail`.`triggernimreference` AS `triggernimreference`,if((`viewnimdetail`.`det_0` = '1'),`D0`.`detname`,if((`viewnimdetail`.`det_0` = '0'),concat('!',`D0`.`detname`),NULL)) AS `det_0`,if((`viewnimdetail`.`det_1` = '1'),`D1`.`detname`,if((`viewnimdetail`.`det_1` = '0'),concat('!',`D1`.`detname`),NULL)) AS `det_1`,if((`viewnimdetail`.`det_2` = '1'),`D2`.`detname`,if((`viewnimdetail`.`det_2` = '0'),concat('!',`D2`.`detname`),NULL)) AS `det_2`,if((`viewnimdetail`.`det_3` = '1'),`D3`.`detname`,if((`viewnimdetail`.`det_3` = '0'),concat('!',`D3`.`detname`),NULL)) AS `det_3`,if((`viewnimdetail`.`det_4` = '1'),`D4`.`detname`,if((`viewnimdetail`.`det_4` = '0'),concat('!',`D4`.`detname`),NULL)) AS `det_4` from (`viewnimdetail` join ((((`nimdetname` `D0` join `nimdetname` `D1`) join `nimdetname` `D2`) join `nimdetname` `D3`) join `nimdetname` `D4`) on(((`D0`.`validitystart` <= `viewnimdetail`.`validitystart`) and ((`D0`.`validityend` >= `viewnimdetail`.`validityend`) or isnull(`D0`.`validityend`)) and (`D1`.`validitystart` <= `viewnimdetail`.`validitystart`) and ((`D1`.`validityend` >= `viewnimdetail`.`validityend`) or isnull(`D1`.`validityend`)) and (`D2`.`validitystart` <= `viewnimdetail`.`validitystart`) and ((`D2`.`validityend` >= `viewnimdetail`.`validityend`) or isnull(`D2`.`validityend`)) and (`D3`.`validitystart` <= `viewnimdetail`.`validitystart`) and ((`D3`.`validityend` >= `viewnimdetail`.`validityend`) or isnull(`D3`.`validityend`)) and (`D4`.`validitystart` <= `viewnimdetail`.`validitystart`) and ((`D4`.`validityend` >= `viewnimdetail`.`validityend`) or isnull(`D4`.`validityend`)) and (`D0`.`detnumber` = 0) and (`D1`.`detnumber` = 1) and (`D2`.`detnumber` = 2) and (`D3`.`detnumber` = 3) and (`D4`.`detnumber` = 4)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewnimtype`
--

/*!50001 DROP VIEW IF EXISTS `viewnimtype`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewnimtype` AS select `runtrigger`.`run_id` AS `run_id`,`runtrigger`.`id` AS `id`,`runtrigger`.`validitystart` AS `validitystart`,`run`.`timestop` AS `validityend`,`triggernimtype`.`mask` AS `mask`,`triggernim`.`triggernimdownscaling` AS `triggernimdownscaling`,`triggernim`.`triggernimreference` AS `triggernimreference`,`triggernim`.`id` AS `nim_id` from (`runtrigger` join ((`triggernim` join `triggernimtype`) join `run`) on(((`triggernim`.`runtrigger_id` = `runtrigger`.`id`) and (`triggernim`.`triggernimtype_id` = `triggernimtype`.`id`) and (`runtrigger`.`run_id` = `run`.`id`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewperiodic`
--

/*!50001 DROP VIEW IF EXISTS `viewperiodic`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewperiodic` AS select `runtrigger`.`run_id` AS `run_id`,`runtrigger`.`id` AS `id`,`runtrigger`.`validitystart` AS `validitystart`,`runtrigger`.`validityend` AS `validityend`,(cast((40 / `triggerperiodictype`.`period`) as char charset utf8) + 0) AS `frequency` from (`runtrigger` join (`triggerperiodic` join `triggerperiodictype`) on(((`triggerperiodic`.`runtrigger_id` = `runtrigger`.`id`) and (`triggerperiodictype`.`id` = `triggerperiodic`.`triggerperiodictype_id`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewperiodicmerged`
--

/*!50001 DROP VIEW IF EXISTS `viewperiodicmerged`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewperiodicmerged` AS select `viewperiodic`.`run_id` AS `run_id`,concat('Period:',group_concat(distinct concat(`viewperiodic`.`frequency`,'MHz') separator ',')) AS `periodstring` from `viewperiodic` group by `viewperiodic`.`run_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewprimitive`
--

/*!50001 DROP VIEW IF EXISTS `viewprimitive`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewprimitive` AS select distinct `viewprimitivename`.`run_id` AS `run_id`,concat(concat_ws('x',convert(`viewprimitivename`.`maskA` using utf8),convert(`viewprimitivename`.`maskB` using utf8),convert(`viewprimitivename`.`maskC` using utf8),convert(`viewprimitivename`.`maskD` using utf8),convert(`viewprimitivename`.`maskE` using utf8),convert(`viewprimitivename`.`maskF` using utf8),convert(`viewprimitivename`.`maskG` using utf8)),'/',`viewprimitivename`.`triggerprimitivedownscaling`,'(',if(isnull(`viewprimitivename`.`triggerprimitivereference`),-(1),`viewprimitivename`.`triggerprimitivereference`),')') AS `triggerstring` from (`viewprimitivename` join `run` on(((`viewprimitivename`.`validityend` > `run`.`timestart`) or (isnull(`viewprimitivename`.`validityend`) and (`viewprimitivename`.`run_id` = `run`.`id`))))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewprimitivedetail_useless`
--

/*!50001 DROP VIEW IF EXISTS `viewprimitivedetail_useless`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewprimitivedetail_useless` AS select `viewprimitivetype`.`run_id` AS `run_id`,`viewprimitivetype`.`validitystart` AS `validitystart`,`viewprimitivetype`.`validityend` AS `validityend`,`viewprimitivetype`.`triggerprimitivedownscaling` AS `triggerprimitivedownscaling`,`viewprimitivetype`.`triggerprimitivereference` AS `triggerprimitivereference`,substr(`viewprimitivetype`.`maskA`,1,1) AS `det_0`,substr(`viewprimitivetype`.`maskB`,2,1) AS `det_1`,substr(`viewprimitivetype`.`maskC`,3,1) AS `det_2` from `viewprimitivetype` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewprimitivemerged`
--

/*!50001 DROP VIEW IF EXISTS `viewprimitivemerged`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewprimitivemerged` AS select distinct `viewprimitive`.`run_id` AS `run_id`,concat('Primitive:',group_concat(distinct `viewprimitive`.`triggerstring` separator '+')) AS `primitivestring` from `viewprimitive` group by `viewprimitive`.`run_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewprimitivename`
--

/*!50001 DROP VIEW IF EXISTS `viewprimitivename`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewprimitivename` AS select distinct `viewprimitivetype`.`run_id` AS `run_id`,`viewprimitivetype`.`triggerprimitivedownscaling` AS `triggerprimitivedownscaling`,`viewprimitivetype`.`triggerprimitivereference` AS `triggerprimitivereference`,`viewprimitivetype`.`validitystart` AS `validitystart`,`viewprimitivetype`.`validityend` AS `validityend`,`viewprimitivetype`.`masknumber` AS `masknumber`,if((`viewprimitivetype`.`maskA` <> '0x7fff7fff'),`D0`.`detname`,NULL) AS `maskA`,if((`viewprimitivetype`.`maskB` <> '0x7fff7fff'),`D1`.`detname`,NULL) AS `maskB`,if((`viewprimitivetype`.`maskC` <> '0x7fff7fff'),`D2`.`detname`,NULL) AS `maskC`,if((`viewprimitivetype`.`maskD` <> '0x7fff7fff'),`D3`.`detname`,NULL) AS `maskD`,if((`viewprimitivetype`.`maskE` <> '0x7fff7fff'),`D4`.`detname`,NULL) AS `maskE`,if((`viewprimitivetype`.`maskF` <> '0x7fff7fff'),`D5`.`detname`,NULL) AS `maskF`,if((`viewprimitivetype`.`maskG` <> '0x7fff7fff'),`D6`.`detname`,NULL) AS `maskG` from (`viewprimitivetype` join ((((((`primitivedetname` `D0` join `primitivedetname` `D1`) join `primitivedetname` `D2`) join `primitivedetname` `D3`) join `primitivedetname` `D4`) join `primitivedetname` `D5`) join `primitivedetname` `D6`) on(((`D0`.`validitystart` < `viewprimitivetype`.`validitystart`) and (`D1`.`validitystart` < `viewprimitivetype`.`validitystart`) and (`D2`.`validitystart` < `viewprimitivetype`.`validitystart`) and (`D3`.`validitystart` < `viewprimitivetype`.`validitystart`) and (`D4`.`validitystart` < `viewprimitivetype`.`validitystart`) and (`D5`.`validitystart` < `viewprimitivetype`.`validitystart`) and (`D6`.`validitystart` < `viewprimitivetype`.`validitystart`) and (`D0`.`detnumber` = 0) and (`D1`.`detnumber` = 1) and (`D2`.`detnumber` = 2) and (`D3`.`detnumber` = 3) and (`D4`.`detnumber` = 4) and (`D5`.`detnumber` = 5) and (`D6`.`detnumber` = 6) and (`D0`.`detmask` = `viewprimitivetype`.`maskA`) and (`D1`.`detmask` = `viewprimitivetype`.`maskB`) and (`D2`.`detmask` = `viewprimitivetype`.`maskC`) and (`D3`.`detmask` = `viewprimitivetype`.`maskD`) and (`D4`.`detmask` = `viewprimitivetype`.`maskE`) and (`D5`.`detmask` = `viewprimitivetype`.`maskF`) and (`D6`.`detmask` = `viewprimitivetype`.`maskG`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewprimitivetype`
--

/*!50001 DROP VIEW IF EXISTS `viewprimitivetype`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewprimitivetype` AS select `runtrigger`.`run_id` AS `run_id`,`runtrigger`.`id` AS `id`,`runtrigger`.`validitystart` AS `validitystart`,`runtrigger`.`validityend` AS `validityend`,`triggerprimitivetype`.`maskA` AS `maskA`,`triggerprimitivetype`.`maskB` AS `maskB`,`triggerprimitivetype`.`maskC` AS `maskC`,`triggerprimitivetype`.`maskD` AS `maskD`,`triggerprimitivetype`.`maskE` AS `maskE`,`triggerprimitivetype`.`maskF` AS `maskF`,`triggerprimitivetype`.`maskG` AS `maskG`,`triggerprimitive`.`triggerprimitivedownscaling` AS `triggerprimitivedownscaling`,`triggerprimitive`.`triggerprimitivereference` AS `triggerprimitivereference`,`triggerprimitive`.`masknumber` AS `masknumber` from (`runtrigger` join (`triggerprimitive` join `triggerprimitivetype`) on(((`triggerprimitive`.`runtrigger_id` = `runtrigger`.`id`) and (`triggerprimitive`.`triggerprimitivetype_id` = `triggerprimitivetype`.`id`)))) order by `runtrigger`.`run_id`,`triggerprimitive`.`masknumber` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewsync`
--

/*!50001 DROP VIEW IF EXISTS `viewsync`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewsync` AS select `runtrigger`.`run_id` AS `run_id`,`runtrigger`.`id` AS `id`,`runtrigger`.`validitystart` AS `validitystart`,`runtrigger`.`validityend` AS `validityend` from (`triggersync` left join `runtrigger` on((`triggersync`.`runtrigger_id` = `runtrigger`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewtrigger`
--

/*!50001 DROP VIEW IF EXISTS `viewtrigger`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewtrigger` AS select `viewperiodicmerged`.`run_id` AS `run_id`,concat_ws('+',`viewperiodicmerged`.`periodstring`,group_concat(distinct `viewnimmerged`.`nimstring` separator '+')) AS `triggerstring` from (`viewperiodicmerged` left join `viewnimmerged` on((`viewperiodicmerged`.`run_id` = `viewnimmerged`.`run_id`))) group by `viewperiodicmerged`.`run_id` union select `viewnimmerged`.`run_id` AS `run_id`,concat_ws('+',`viewperiodicmerged`.`periodstring`,group_concat(distinct `viewnimmerged`.`nimstring` separator '+')) AS `triggerstring` from (`viewnimmerged` left join `viewperiodicmerged` on((`viewperiodicmerged`.`run_id` = `viewnimmerged`.`run_id`))) group by `viewnimmerged`.`run_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `viewtriggerfull`
--

/*!50001 DROP VIEW IF EXISTS `viewtriggerfull`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`nlurkin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `viewtriggerfull` AS select `viewtrigger`.`run_id` AS `run_id`,concat_ws('+',`viewtrigger`.`triggerstring`,group_concat(distinct `viewprimitivemerged`.`primitivestring` separator '+')) AS `triggerstring` from (`viewtrigger` left join `viewprimitivemerged` on((`viewtrigger`.`run_id` = `viewprimitivemerged`.`run_id`))) group by `viewtrigger`.`run_id` union select `viewprimitivemerged`.`run_id` AS `run_id`,concat_ws('+',`viewtrigger`.`triggerstring`,group_concat(distinct `viewprimitivemerged`.`primitivestring` separator '+')) AS `triggerstring` from (`viewprimitivemerged` left join `viewtrigger` on((`viewtrigger`.`run_id` = `viewprimitivemerged`.`run_id`))) group by `viewprimitivemerged`.`run_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-10-25  9:47:16
