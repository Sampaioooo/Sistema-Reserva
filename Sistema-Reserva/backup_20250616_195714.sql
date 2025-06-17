-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: reserva_laboratorio
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
-- Table structure for table `reservas`
--

DROP TABLE IF EXISTS `reservas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `id_sala` int NOT NULL,
  `data_reserva` date NOT NULL,
  `hora_inicio` time NOT NULL,
  `hora_fim` time NOT NULL,
  `status` enum('pendente','aprovada','rejeitada') DEFAULT 'pendente',
  PRIMARY KEY (`id`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_sala` (`id_sala`),
  CONSTRAINT `reservas_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `reservas_ibfk_2` FOREIGN KEY (`id_sala`) REFERENCES `salas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservas`
--

LOCK TABLES `reservas` WRITE;
/*!40000 ALTER TABLE `reservas` DISABLE KEYS */;
INSERT INTO `reservas` VALUES (1,1,1,'2025-06-15','08:00:00','10:00:00','pendente'),(2,2,2,'2025-06-16','14:00:00','16:00:00','aprovada'),(3,1,1,'2025-06-17','10:00:00','12:00:00','pendente'),(4,2,2,'2025-06-18','14:00:00','16:00:00','pendente'),(5,1,1,'2025-06-14','18:05:00','19:50:00','pendente'),(6,1,1,'2025-06-14','18:00:00','19:00:00','pendente'),(10,12,1,'2020-02-20','20:02:00','20:02:00','pendente'),(11,13,1,'0555-05-31','05:52:00','06:59:00','pendente');
/*!40000 ALTER TABLE `reservas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salas`
--

DROP TABLE IF EXISTS `salas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome_sala` varchar(50) NOT NULL,
  `capacidade` int NOT NULL,
  `equipamentos` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salas`
--

LOCK TABLES `salas` WRITE;
/*!40000 ALTER TABLE `salas` DISABLE KEYS */;
INSERT INTO `salas` VALUES (1,'Lab 01',25,'Projetor, Computadores'),(2,'Lab 02',20,'Quadro Interativo, Computadores');
/*!40000 ALTER TABLE `salas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `tipo` enum('aluno','professor','admin') DEFAULT 'aluno',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'João da Silva','joao@email.com','123456','aluno'),(2,'Maria Souza','maria@email.com','123456','professor'),(3,'Admin Sistema','admin@email.com','admin123','admin'),(5,'Sampaio','sampaioteste2005','$2b$12$a0zeIuoKON.EOFOQ3lyTnu/eyLpz6OlflNgEwn8HrceYOydpX6OQu','admin'),(6,'sampaio','sampaioteste','$2b$12$CJym8o4hVPqOCvhb7iupCubTiP7Mp5v2/GzXTckGS7M.gBN.FKuqy','admin'),(7,'sampaio','samuelteste@gmail.com','$2b$12$OX660dH6YTy5DuKNYUHRjeLCnZFKmhbsYY.3myXhu6bOQ1Npq.LrS','admin'),(8,'samuel','samuelsampaio','$2b$12$f0qj3SJtHAhU6SWrfG4jv.K.c.4BeORnd5UciZA6bpd0q/MZmJA8e','admin'),(9,'sampaio20','sampaio20','$2b$12$eEVAdT0C0w5/2J0.woYvV.sExxl/Tk9ZQu1V0LbcG.U36ga52xixC','admin'),(10,'sampaio','sampaio470','$2b$12$rX08.EprFuOJa1bjDAVas./aVM/mvTLfBwE8gJqvl5sH91hRz9xni','admin'),(11,'teste5','teste5','$2b$12$Nnrfp7BEaChXQIylqns9ketByrFiyiqWMWlmXD4Unvp/2lVT0qJ8q','aluno'),(12,'Sampaio','sampaioteste@gmail.com','$2b$12$MspoW6b7VZ6GLwgQ.V2tqe92OMZLJlv9HoSUYJmIzvlPzH16ft9Q6','admin'),(13,'teste','teste07@gmai.com','$2b$12$RH3g8uYZKn66zZP55up24OMTciFt7rabiPA7CEsvRlfnyTuBU4Cpy','aluno'),(15,'p','teste09@gmai.com','$2b$12$S3y8NTQbNYMADxw4WH1Htu0VF6U892Mx.mm/ZuMvbgXUs672US/KW','aluno'),(16,'pf','pf@gmail.com','$2b$12$uDACq9zjR/HNn.ycSrzgEeDM5gNYc0jkDX8ie9J13qSnZOTxkj.0u','professor');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-16 19:57:15
