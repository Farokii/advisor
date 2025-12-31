-- MySQL dump 10.13  Distrib 9.5.0, for Linux (x86_64)
--
-- Host: localhost    Database: db1
-- ------------------------------------------------------
-- Server version	9.5.0

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
-- Table structure for table `advisors`
--

DROP TABLE IF EXISTS `advisors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `advisors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `phone_number` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(50) NOT NULL,
  `bio` text,
  `work_experience` varchar(50) NOT NULL,
  `about` text,
  `service_status` enum('out_of_service','in_service') DEFAULT NULL,
  `work_status` enum('available','busy','urgent_only') DEFAULT NULL,
  `completed_readings` int NOT NULL,
  `readings` int NOT NULL,
  `ratings` float NOT NULL,
  `review_count` int NOT NULL,
  `coin` float NOT NULL,
  `accept_text_reading` tinyint(1) NOT NULL,
  `price_text_reading` float NOT NULL,
  `accept_audio_reading` tinyint(1) NOT NULL,
  `price_audio_reading` float NOT NULL,
  `accept_video_reading` tinyint(1) NOT NULL,
  `price_video_reading` float NOT NULL,
  `accept_live_text_chat` tinyint(1) NOT NULL,
  `price_live_text_chat` float NOT NULL,
  `accept_live_audio_chat` tinyint(1) NOT NULL,
  `price_live_audio_chat` float NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_advisors_phone_number` (`phone_number`),
  KEY `ix_advisors_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `advisors`
--

LOCK TABLES `advisors` WRITE;
/*!40000 ALTER TABLE `advisors` DISABLE KEYS */;
INSERT INTO `advisors` VALUES (1,'13900000001','$2b$12$wS2UtvWyuxshSxelwyQO6eZxoS8hkLwqYIQTJss8IZtLu5rytMNL2','Mike1','asfdsafsadfsdafas','5 years','I love coding and building APIs','in_service','available',1,4,4.5,10,134.5,1,3,1,3,1,3,1,1.5,1,1.5,'2025-12-25 03:54:18','2025-12-25 10:40:03'),(2,'13900000002','$2b$12$KsEFdHxwIBCnHognZbFaRuwHIEEQOuaQeImevIoFi7X.Rlq/ZRXfK','Mike2','dzfbgvdsfbfg','5 years','I love coding and building APIs','in_service','available',2,3,4.5,1,112,1,3,1,3,1,3,1,1.5,1,1.5,'2025-12-25 03:54:34','2025-12-29 10:41:32'),(3,'13900000003','$2b$12$uMFAdaIax65/1ZO7jJBJ2.XC95kS54o6J.5TKMnd6RG9SfKa7Qm0i','Mike3','dzfbgvdsfbfg','5 years','I love coding and building APIs','in_service','busy',0,0,0,0,100,1,8.5,1,12.6,1,21.2,1,9.2,1,15.4,'2025-12-25 03:54:40','2025-12-29 10:06:34'),(4,'13900000004','$2b$12$wmKnLuvYR8KEpuz0XImAJuhiFbZj7TDs4wH1RUDFTq6/TnQ1Ha4zq','Mike4','dzfbgvdsfbfg','5 years','I love coding and building APIs','in_service','available',0,0,0,0,100,1,3,1,3,1,3,1,1.5,1,1.5,'2025-12-25 03:54:45',NULL),(5,'13900000005','$2b$12$7i6xJ8jUpck1FObpA/cizelWvk0JW4hpRnCH1buyvHlSKbXLuNm.O','Mike5','dzfbgvdsfbfg','5 years','I love coding and building APIs','in_service','available',0,0,0,0,100,1,3,1,3,1,3,1,1.5,1,1.5,'2025-12-25 03:54:52',NULL);
/*!40000 ALTER TABLE `advisors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `favorites`
--

DROP TABLE IF EXISTS `favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `favorites` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `advisor_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `ix_favorites_id` (`id`),
  KEY `ix_favorites_advisor_id` (`advisor_id`),
  KEY `ix_favorites_user_id` (`user_id`),
  CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`advisor_id`) REFERENCES `advisors` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `favorites`
--

LOCK TABLES `favorites` WRITE;
/*!40000 ALTER TABLE `favorites` DISABLE KEYS */;
INSERT INTO `favorites` VALUES (1,1,1,'2025-12-25 08:30:33'),(3,1,3,'2025-12-25 08:30:44');
/*!40000 ALTER TABLE `favorites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `advisor_id` int NOT NULL,
  `order_type` enum('text_reading','audio_reading','video_reading','live_text_chat','live_audio_chat') NOT NULL,
  `general_situation` varchar(3000) NOT NULL,
  `specific_question` varchar(200) NOT NULL,
  `reply` varchar(5000) DEFAULT NULL,
  `order_status` enum('pending','completed','expired') NOT NULL,
  `completed_at` datetime DEFAULT NULL,
  `is_urgent` tinyint(1) NOT NULL,
  `current_price` float NOT NULL,
  `final_amount` float DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_orders_id` (`id`),
  KEY `ix_orders_advisor_id` (`advisor_id`),
  KEY `ix_orders_order_status` (`order_status`),
  KEY `ix_orders_created_at` (`created_at`),
  KEY `ix_orders_user_id` (`user_id`),
  KEY `ix_orders_is_urgent` (`is_urgent`),
  KEY `ix_orders_order_type` (`order_type`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`advisor_id`) REFERENCES `advisors` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,1,1,'text_reading','sdafgdegbgdfgv','safffvfvfv',NULL,'expired',NULL,0,0,0,'2025-12-25 07:06:48','2025-12-25 07:07:42'),(2,1,1,'text_reading','sdafgdegbgdfgv','safffvfvfv',NULL,'expired',NULL,0,0,0,'2025-12-25 07:51:11','2025-12-25 07:51:59'),(3,1,1,'text_reading','sdafgdegbgdfgv','safffvfvfv',NULL,'expired',NULL,0,0,0,'2025-12-25 08:20:59','2025-12-25 08:31:44'),(4,1,1,'text_reading','sdafgdegbgdfgv','safffvfvfv','siufhnieufhnifhnviofioadhdfiodfiohjniodsjopdsjjaspkf','completed','2025-12-25 16:41:13',0,4.5,4.5,'2025-12-25 08:40:46','2025-12-25 08:41:12'),(5,2,2,'text_reading','sdafgdegbgdfgv','safffvfvfv','abcdefghijklmnopqrstuvwxyz','completed','2025-12-29 09:57:47',0,4.5,4.5,'2025-12-29 09:57:46','2025-12-29 09:57:47'),(6,2,2,'text_reading','sdafgdegbgdfgv','safffvfvfv','abcdefghijklmnopqrstuvwxyz','completed','2025-12-29 10:01:26',0,4.5,4.5,'2025-12-29 10:01:26','2025-12-29 10:01:26'),(7,2,2,'text_reading','sdafgdegbgdfgv','safffvfvfv',NULL,'expired',NULL,0,0,0,'2025-12-29 10:41:32','2025-12-29 10:52:26');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `user_id` int NOT NULL,
  `advisor_id` int NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `order_type` enum('text_reading','audio_reading','video_reading','live_text_chat','live_audio_chat') NOT NULL,
  `rating` float NOT NULL,
  `review_text` varchar(300) DEFAULT NULL,
  `tip` float DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `ix_reviews_order_type` (`order_type`),
  KEY `ix_reviews_id` (`id`),
  KEY `ix_reviews_advisor_id` (`advisor_id`),
  KEY `ix_reviews_order_id` (`order_id`),
  KEY `ix_reviews_user_id` (`user_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `reviews_ibfk_3` FOREIGN KEY (`advisor_id`) REFERENCES `advisors` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (1,4,1,1,'Alan1','text_reading',4.5,'good job',3,'2025-12-25 08:58:04'),(2,4,1,1,'Alan1','text_reading',4.5,'good job',3,'2025-12-25 09:00:08'),(3,4,1,1,'Alan1','text_reading',4.5,'good job',3,'2025-12-25 09:08:51'),(4,4,1,1,'Alan1','text_reading',4.5,'good job',3,'2025-12-25 09:52:24'),(5,4,1,1,'Alan1','text_reading',4.5,'good job',3,'2025-12-25 09:55:00'),(6,4,1,1,'Alan1','text_reading',4.5,'good job',3,'2025-12-25 10:24:25'),(7,4,1,1,'Alan1','text_reading',4.5,'good job',3,'2025-12-25 10:27:13'),(8,4,1,1,'Alan1','text_reading',4.5,'good job',3,'2025-12-25 10:28:04'),(9,4,1,1,'Alan1','text_reading',4.5,'good job',3,'2025-12-25 10:32:45'),(10,4,1,1,'Alan1','text_reading',4.5,'good job',3,'2025-12-25 10:40:03'),(11,6,2,2,'Alan2','text_reading',4.5,'good job',3,'2025-12-29 10:01:26');
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `phone_number` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  `birth` date DEFAULT NULL,
  `gender` enum('male','female','other') DEFAULT NULL,
  `bio` text,
  `about` text,
  `coin` float DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_phone_number` (`phone_number`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'13800000001','$2b$12$lX/xxHQH5A1FxOMNxEWB8enwWY79SKth5K883hq9uBgYNID9CCL9W','Alan1','1990-01-01','male','Software Engineer','I love coding and building APIs',65.5,'2025-12-25 03:53:11','2025-12-25 10:40:03'),(2,'13800000002','$2b$12$H9G586Dq2DZnA5lBMUXBru9vhihp12GoY1/Gk/acsz3PBLannRqYS','Alan2','1990-01-01','male','Software Engineer','I love coding and building APIs',88,'2025-12-25 03:53:22','2025-12-29 10:52:26'),(3,'13800000003','$2b$12$OhzDU1Fvj1AF4PA2AuZixuvBCzMVohqRkR4YU7im8y/E.s3Q0ii5e','Alan3','1990-01-01','male','Software Engineer','I love coding and building APIs',100,'2025-12-25 03:53:29',NULL),(4,'13800000004','$2b$12$TMiUCJZsvc2CFx34H1782uQE.WbRQoYKpSUJFtm/lFK49bU1yCFzm','Alan4','1990-01-01','male','Software Engineer','I love coding and building APIs',100,'2025-12-25 03:53:35',NULL),(5,'13800000005','$2b$12$Bb6NNIxVtnJBN6iS9S5Tgu36e1aGvLwiB9fMblu6elxgG76jiqzOa','Alan5','1990-01-01','male','Software Engineer','I love coding and building APIs',100,'2025-12-25 03:53:41',NULL),(6,'13800000006','$2b$12$75fWVdmDZSsG1V3k3zBkmOhu84PdI5ik12qBNVJ.rtN7myVbe3Yqa','Alan6','1990-01-01','male','Software Engineer','I love coding and building APIs',100,'2025-12-30 12:27:05',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'db1'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-31 10:45:44
