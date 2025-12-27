-- MySQL dump 10.13  Distrib 8.0.40, for Linux (x86_64)
--
-- Host: sheikhrehan.mysql.pythonanywhere-services.com    Database: sheikhrehan$event_db
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `books` (
  `uid` int DEFAULT NULL,
  `eid` int DEFAULT NULL,
  `person1` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `person2` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  KEY `books_ibfk_1` (`uid`),
  KEY `books_ibfk_2` (`eid`),
  CONSTRAINT `books_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE,
  CONSTRAINT `books_ibfk_2` FOREIGN KEY (`eid`) REFERENCES `event` (`eid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books`
--

LOCK TABLES `books` WRITE;
/*!40000 ALTER TABLE `books` DISABLE KEYS */;
INSERT INTO `books` VALUES (1,1,'Epsilon Gamma',NULL),(5,3,'sourabh',NULL),(5,4,NULL,NULL),(5,5,NULL,NULL),(5,6,'yash',NULL),(5,7,'aakash',NULL),(7,8,'Mine',NULL),(8,9,'Sheikh',NULL),(8,10,NULL,NULL),(7,11,'Jazab',NULL),(7,12,'Jazab','Uski Bandi'),(7,13,NULL,NULL);
/*!40000 ALTER TABLE `books` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contact`
--

DROP TABLE IF EXISTS `contact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contact` (
  `pid` int DEFAULT NULL,
  `contact1` decimal(10,0) DEFAULT NULL,
  `contact2` decimal(10,0) DEFAULT NULL,
  `contact3` decimal(10,0) DEFAULT NULL,
  KEY `contact_ibfk_1` (`pid`),
  CONSTRAINT `contact_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `personal` (`pid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contact`
--

LOCK TABLES `contact` WRITE;
/*!40000 ALTER TABLE `contact` DISABLE KEYS */;
INSERT INTO `contact` VALUES (1,9924161231,1231231221,12312434),(2,7385550597,0,0),(3,7385550597,0,0),(4,7385550597,8329870397,0),(5,3129760454,3129650808,0),(6,2345678998,3129650808,456);
/*!40000 ALTER TABLE `contact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event` (
  `eid` int NOT NULL AUTO_INCREMENT,
  `etype` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `edate` date NOT NULL,
  `etier` int NOT NULL,
  `ecost` int NOT NULL,
  `evenue` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `emax_people` int NOT NULL,
  `especial` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_general_ci DEFAULT 'pending',
  `visibility` varchar(20) COLLATE utf8mb4_general_ci DEFAULT 'private',
  `extras` varchar(255) COLLATE utf8mb4_general_ci DEFAULT 'None',
  PRIMARY KEY (`eid`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event`
--

LOCK TABLES `event` WRITE;
/*!40000 ALTER TABLE `event` DISABLE KEYS */;
INSERT INTO `event` VALUES (1,'Birthday','2020-06-27',3,35000,'Sunrays Hall, Santacruz (W), Mumbai',34,'Theme of decoration should be blue.','completed','private','None'),(2,'Birthday','2025-03-19',3,137500,'pimpri',100,'banana','completed','private','None'),(3,'Birthday','2025-03-19',3,137500,'pimpri',100,'banana','completed','private','None'),(4,'manifest','2025-03-18',2,241000,'akurdi',200,'milk','completed','private','None'),(5,'farewell','2025-03-27',3,266000,'di mora',180,'no drinks','completed','private','None'),(6,'Birthday','2025-03-16',2,60000,'raga palace',50,'nothing','completed','private','None'),(7,'Birthday','2025-03-18',2,60000,'raga palace',50,'nothing','completed','private','None'),(8,'Birthday','2025-12-26',2,22000,'Don\'t Know changed',12,'None','pending','private','None'),(9,'Birthday','2025-12-30',0,47500,'Anywhere',40,'None | Meal Preference: Standard','pending','public','DJ, SoundSystem, ValetParking'),(10,'dfgjk','2025-12-18',0,97500,'dfghj',100,'nhhb | Meal Preference: Veg','pending','public','ValetParking'),(11,'Birthday','2025-12-16',0,40500,'Ghar',10,'Bas krdo! (Test 1) | Meal Preference: Standard','pending','public','DJ, SoundSystem'),(12,'Anniversary','2025-12-19',0,46000,'Hotel Sasta Vala',10,'Imaginary | Meal Preference: Veg','pending','public','DJ, ValetParking'),(13,'Jazab ki Nunu Cutting','2025-12-25',0,890000,'Sarkari Hospital',1000,' | Meal Preference: Standard','pending','public','DJ, ValetParking');
/*!40000 ALTER TABLE `event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `has`
--

DROP TABLE IF EXISTS `has`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `has` (
  `uid` int DEFAULT NULL,
  `pid` int DEFAULT NULL,
  KEY `has_ibfk_1` (`uid`),
  KEY `has_ibfk_2` (`pid`),
  CONSTRAINT `has_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE,
  CONSTRAINT `has_ibfk_2` FOREIGN KEY (`pid`) REFERENCES `personal` (`pid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `has`
--

LOCK TABLES `has` WRITE;
/*!40000 ALTER TABLE `has` DISABLE KEYS */;
INSERT INTO `has` VALUES (1,1),(5,3),(6,4),(7,5),(8,6);
/*!40000 ALTER TABLE `has` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `personal`
--

DROP TABLE IF EXISTS `personal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `personal` (
  `pid` int NOT NULL AUTO_INCREMENT,
  `fname` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `mname` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `lname` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `dob` date NOT NULL,
  `gender` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `address` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `personal`
--

LOCK TABLES `personal` WRITE;
/*!40000 ALTER TABLE `personal` DISABLE KEYS */;
INSERT INTO `personal` VALUES (1,'Alpha','Beta','Gamma','2020-06-01','Male','Mumbai, Maharashtra, India'),(2,'yash','k','yadav','2004-03-03','Male','pimpri'),(3,'test1','test2','test3','2004-11-10','Male','pimpri'),(4,'yash','tejbahadur','yadav','2004-03-10','Male','Nehru nagar, near suyog hospital, old telco road, pimpri'),(5,'Sheikh','M.','Rehan','2025-12-09','Male','Askari X'),(6,'Sheikh','','Rehan','2025-12-18','Male','Hassan Abad');
/*!40000 ALTER TABLE `personal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `uid` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `last_login` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `role` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'user',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `profile_pic` varchar(255) COLLATE utf8mb4_general_ci DEFAULT 'default.png',
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'ABC','abc@xyz.com','e99a18c428cb38d5f260853678922e03','2020-06-05 18:12:45','user','2025-03-17 10:28:53','default.png'),(2,'XYZ','xyz@abc.com','613d3b9c91e9445abaeca02f2342e5a6','2020-06-05 13:53:52','user','2025-03-17 10:28:53','default.png'),(4,'kuldeep','kuldeep@gmail.com','8e4436dc3ba832ddd00caf213d2913de','2025-03-17 04:27:42','admin','2025-03-17 10:28:53','default.png'),(5,'test1','test1@gmail.com','51ce84a6db96daaa7081869fd38c517a','2025-03-17 05:36:09','user','2025-03-17 10:28:53','default.png'),(6,'yashyadav','yash@gmail.com','1e8d95050c46fe153d31c33bf93f61df','2025-03-17 06:03:21','user','2025-03-17 11:32:51','default.png'),(7,'sheikhrehan','sr033155@gmail.com','202cb962ac59075b964b07152d234b70','2025-12-13 21:22:59','user','2025-12-13 19:31:43','sheikhrehan_1765660203_DSC_408170944122388489.png'),(8,'sheikhrehanadmin','sr033155@gmail.com','202cb962ac59075b964b07152d234b70','2025-12-13 19:38:21','admin','2025-12-13 19:38:21','default.png');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-13 21:51:53
