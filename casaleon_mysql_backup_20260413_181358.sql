-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: fabrica_pieles2
-- ------------------------------------------------------
-- Server version	8.0.40

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
-- Current Database: `fabrica_pieles2`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `fabrica_pieles2` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `fabrica_pieles2`;

--
-- Table structure for table `auditoria_logs`
--

DROP TABLE IF EXISTS `auditoria_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auditoria_logs` (
  `id_log` int NOT NULL AUTO_INCREMENT,
  `modulo` varchar(50) NOT NULL,
  `accion` varchar(120) NOT NULL,
  `detalle` varchar(255) NOT NULL,
  `severidad` varchar(20) NOT NULL,
  `actor_tipo` varchar(20) DEFAULT NULL,
  `actor_id` int DEFAULT NULL,
  `actor_nombre` varchar(150) DEFAULT NULL,
  `actor_email` varchar(120) DEFAULT NULL,
  `ip_addr` varchar(45) DEFAULT NULL,
  `user_agent` varchar(255) DEFAULT NULL,
  `creado_en` datetime NOT NULL,
  PRIMARY KEY (`id_log`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auditoria_logs`
--

LOCK TABLES `auditoria_logs` WRITE;
/*!40000 ALTER TABLE `auditoria_logs` DISABLE KEYS */;
INSERT INTO `auditoria_logs` VALUES (1,'Autenticación','Inicio de sesión','Usuario administrador inició sesión exitosamente','INFO',NULL,NULL,'Martín López Herrera','admin@casaleon.com','192.168.1.100',NULL,'2026-04-13 14:16:40'),(2,'Compras','Orden de compra registrada','Se registró una compra de cuero vacuno liso color café','INFO',NULL,NULL,'Paola Jiménez Ortega','compras@casaleon.com','192.168.1.105',NULL,'2026-04-13 14:16:40'),(3,'Ventas','Venta procesada','Venta VEN20260401-0001 procesada correctamente','INFO',NULL,NULL,'Diego Fernández Cruz','ventas@casaleon.com','192.168.1.108',NULL,'2026-04-13 14:16:40'),(4,'Usuarios','Usuario creado','Nuevo usuario \'produccion@casaleon.com\' creado','INFO',NULL,NULL,'Martín López Herrera','admin@casaleon.com','192.168.1.100',NULL,'2026-04-13 14:16:40'),(5,'Inventario','Materia prima actualizada','Se actualizó el stock del material \'Cierre metálico 20 cm níquel\'','INFO',NULL,NULL,'Ana Sofía Ramírez','empleado@casaleon.com','192.168.1.112',NULL,'2026-04-13 14:16:40'),(6,'Producción','Receta recalculada','Se recalculó el costo estimado de la receta \'Receta Bolsa Tote Siena\'','INFO',NULL,NULL,'Luis Arturo Navarro','produccion@casaleon.com','192.168.1.110',NULL,'2026-04-13 14:16:40'),(7,'Autenticación','Cambio de contraseña','Usuario actualizó su contraseña correctamente','INFO',NULL,NULL,'Diego Fernández Cruz','ventas@casaleon.com','192.168.1.108',NULL,'2026-04-13 14:16:40'),(8,'Pedidos','Pedido entregado','Pedido PED20260401-0001 marcado como entregado','INFO',NULL,NULL,'Sistema','sistema@casaleon.com','192.168.1.1',NULL,'2026-04-13 14:16:40'),(9,'Usuarios','Acceso denegado','Intento de acceso sin permisos suficientes','WARNING',NULL,NULL,'Invitado','invitado@casaleon.com','192.168.1.200',NULL,'2026-04-13 14:16:40'),(10,'Sistema','Backup completado','Respaldo automático completado correctamente','INFO',NULL,NULL,'Sistema','sistema@casaleon.com','192.168.1.1',NULL,'2026-04-13 14:16:40'),(11,'Proveedores','Proveedor actualizado','Se actualizó información de \'Herrajes Finos de León\'','INFO',NULL,NULL,'Paola Jiménez Ortega','compras@casaleon.com','192.168.1.105',NULL,'2026-04-13 14:16:40'),(12,'Autenticación','Inicio de sesión','Usuario \'admin@casaleon.com\' inició sesión exitosamente','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 14:17:00'),(13,'Ventas','Pedido marcado como entregado','Pedido \'PED20260412-0004\' marcado como Entregado','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 14:23:45'),(14,'Autenticación','Inicio de sesión','Usuario \'admin@casaleon.com\' inició sesión exitosamente','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:09:38'),(15,'Autenticación','Cierre de sesión','Sesión cerrada por \'admin@casaleon.com\'','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:09:42'),(16,'Autenticación','Inicio de sesión','Usuario \'admin@casaleon.com\' inició sesión exitosamente','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:09:53'),(17,'Autenticación','Cierre de sesión','Sesión cerrada por \'admin@casaleon.com\'','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:09:55'),(18,'Autenticación','Inicio de sesión','Usuario \'admin@casaleon.com\' inició sesión exitosamente','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:25:26'),(19,'Autenticación','Cierre de sesión','Sesión cerrada por \'admin@casaleon.com\'','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:25:55'),(20,'Autenticación','Inicio de sesión','Usuario \'admin@casaleon.com\' inició sesión exitosamente','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:40:52'),(21,'Autenticación','Cierre de sesión','Sesión cerrada por \'admin@casaleon.com\'','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:41:28'),(22,'Usuarios','Cliente registrado','Nuevo cliente \'martin@gmail.com\' creado desde registro público','INFO','CLIENTE',4,'Martin','martin@gmail.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:56:04'),(23,'Autenticación','Inicio de sesión','Cliente \'martin@gmail.com\' inició sesión exitosamente','INFO','CLIENTE',4,'Martin','martin@gmail.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:56:16'),(24,'Pedidos','Pedido creado','Pedido PED20260413-0005 registrado por cliente \'martin@gmail.com\' con total $7695.00','INFO','CLIENTE',4,'Martin','martin@gmail.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:57:48'),(25,'Autenticación','Cierre de sesión','Sesión cerrada por \'martin@gmail.com\'','INFO','CLIENTE',4,'Martin','martin@gmail.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:58:13'),(26,'Autenticación','Inicio de sesión','Usuario \'admin@casaleon.com\' inició sesión exitosamente','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 17:58:24'),(27,'Proveedores','Proveedor creado','Proveedor \'Proveedor 1\' creado con estado Activo','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 18:00:10'),(28,'Inventario','Materia prima creada','Materia prima \'Piel premium\' creada con proveedor \'Proveedor 1\', stock 300.00 dm2','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 18:02:05'),(29,'Autenticación','Inicio de sesión','Usuario \'admin@casaleon.com\' inició sesión exitosamente','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 18:10:33'),(30,'Recetas','Receta creada','Receta \'Receta 1\' creada con 2 insumo(s)','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 18:11:01'),(31,'Producción','Orden de producción creada','Orden OP20260413-0001 registrada para \'Bolsa Tote Siena\' con cantidad 10 en estado PENDIENTE','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 18:11:29'),(32,'Producción','Orden de producción finalizada','Orden OP20260413-0001 finalizada. Producto terminado +10.00. Sobrante reintegrado MP: 0. Merma generada: 25.33.','INFO','USUARIO',1,'Martín López Herrera','admin@casaleon.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-13 18:11:50');
/*!40000 ALTER TABLE `auditoria_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authtoken`
--

DROP TABLE IF EXISTS `authtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `authtoken` (
  `id_token` int NOT NULL AUTO_INCREMENT,
  `subject_type` enum('USUARIO','CLIENTE') NOT NULL,
  `subject_id` int NOT NULL,
  `token_hash` varchar(64) NOT NULL,
  `created_at` datetime NOT NULL,
  `expires_at` datetime NOT NULL,
  `revoked` int NOT NULL,
  `user_agent` varchar(255) DEFAULT NULL,
  `ip_addr` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_token`),
  UNIQUE KEY `token_hash` (`token_hash`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authtoken`
--

LOCK TABLES `authtoken` WRITE;
/*!40000 ALTER TABLE `authtoken` DISABLE KEYS */;
INSERT INTO `authtoken` VALUES (1,'USUARIO',1,'19ea9006b2717d318d4dae2b019ff9be552b296c43ede92b2e81745eb739e92a','2026-04-13 14:17:00','2026-04-13 20:27:00',0,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','127.0.0.1'),(2,'USUARIO',1,'f91e64e23f0ccd70a5fb9116bcac12c4436a36835e5afbea1a53f24b5f9ea8e8','2026-04-13 17:09:38','2026-04-13 23:19:38',1,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','127.0.0.1'),(3,'USUARIO',1,'5dcc186f53eb3889aa6ab1308f6f17ab1948d8597dbd0604e25e067282c50b22','2026-04-13 17:09:53','2026-04-13 23:19:53',1,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','127.0.0.1'),(4,'USUARIO',1,'c91f9428896c992c18e33c0c8d4a0b0a8b12fb79b6c5bf3de0bd0dff4e487903','2026-04-13 17:25:26','2026-04-13 23:35:26',1,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','127.0.0.1'),(5,'USUARIO',1,'fc657b4ad64b0234c427a799bfca5f528d7b4ceed5ed14a6fa45bd93acc14c09','2026-04-13 17:40:52','2026-04-13 23:50:52',1,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','127.0.0.1'),(6,'CLIENTE',4,'78fc5aacdf7b6f109c85c93697147f7fe1e7ed0d8946e23a6f0b633d8bb9138e','2026-04-13 17:56:16','2026-04-14 00:06:16',1,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','127.0.0.1'),(7,'USUARIO',1,'ca80d0df50e8f718887e12ce7fb1f587059085755973777db5b464583456e843','2026-04-13 17:58:24','2026-04-14 00:08:24',0,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','127.0.0.1'),(8,'USUARIO',1,'1113de6b954495b4d3143e7bc72c6124c2080d5b7293c7b7a17d8315d2d03fff','2026-04-13 18:10:33','2026-04-14 00:20:33',0,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','127.0.0.1');
/*!40000 ALTER TABLE `authtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias_materia_prima`
--

DROP TABLE IF EXISTS `categorias_materia_prima`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_materia_prima` (
  `id_categoria_materia_prima` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(60) NOT NULL,
  `activo` int NOT NULL,
  PRIMARY KEY (`id_categoria_materia_prima`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias_materia_prima`
--

LOCK TABLES `categorias_materia_prima` WRITE;
/*!40000 ALTER TABLE `categorias_materia_prima` DISABLE KEYS */;
INSERT INTO `categorias_materia_prima` VALUES (1,'Cuero',1),(2,'Forro',1),(3,'Herrajes',1),(4,'Químicos',1),(5,'Costura',1),(6,'Refuerzo',1),(7,'Empaque',1);
/*!40000 ALTER TABLE `categorias_materia_prima` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias_producto`
--

DROP TABLE IF EXISTS `categorias_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_producto` (
  `id_categoria_producto` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(60) NOT NULL,
  PRIMARY KEY (`id_categoria_producto`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias_producto`
--

LOCK TABLES `categorias_producto` WRITE;
/*!40000 ALTER TABLE `categorias_producto` DISABLE KEYS */;
INSERT INTO `categorias_producto` VALUES (5,'Bolsas tote'),(6,'Bolsos de mano'),(1,'Carteras'),(4,'Cinturones'),(13,'Estuches lentes'),(11,'Fundas laptop'),(14,'Llaveros'),(8,'Mariconeras'),(7,'Mochilas'),(2,'Monederos'),(10,'Neceseres'),(12,'Porta pasaportes'),(9,'Portafolios'),(15,'Pulseras'),(3,'Tarjeteros');
/*!40000 ALTER TABLE `categorias_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `rfc` varchar(20) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `telefono` varchar(30) DEFAULT NULL,
  `calle` varchar(120) DEFAULT NULL,
  `numero` varchar(20) DEFAULT NULL,
  `colonia` varchar(120) DEFAULT NULL,
  `ciudad` varchar(80) DEFAULT NULL,
  `estado` varchar(80) DEFAULT NULL,
  `pais` varchar(80) DEFAULT NULL,
  `cp` varchar(10) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `creado_en` datetime NOT NULL,
  `activo` int NOT NULL,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (1,'Juan Carlos Gómez Torres','GOTJ900315KJ2','juan.gomez@correo.com','4776123456','Av. Panorama','145','Panorama','León','Guanajuato','México','37160','scrypt:32768:8:1$n87XB7cxR5t9wffV$f54c7dfbe6f982a00e3e3375d26188e04023c8276234e63c5d99cc6af04cfd4bbd1d986851142897fae3e3042c7138c083e8ded85992c6f0306849e5543272de','2026-04-13 14:16:39',1),(2,'María Fernanda Ruiz Saldaña','RUSM920824PU4','maria.ruiz@correo.com','4776987412','Blvd. Campestre','2208','Jardines del Moral','León','Guanajuato','México','37160','scrypt:32768:8:1$FrF8aeb6uXoSSAXF$3599997d153bdbfbf51bb30e6800df1552efdac8671e6a7e58b3917b3dfb45e0dd9f7709af7abf30ffd500283c0187c9794ec15de7559062ff0e476af33f382f','2026-04-13 14:16:39',1),(3,'Carlos Alberto Mendoza Vega','MEVC910112NB7','carlos.mendoza@correo.com','4423012298','Av. Universidad','812','Centro Sur','Querétaro','Querétaro','México','76090','scrypt:32768:8:1$lS18mkwsltHn3xq5$3e2e1615d25ac61caba07b7b0f552dc586b785a1cf3d3ff00ceb44855624e09d5406195a32850bb211189ed01e90e1559115cc26925cc571b458390dad9b16a5','2026-04-13 14:16:39',1),(4,'Martin',NULL,'martin@gmail.com','3321663503','UTL','10','Av Universidad','Leon','Guanajuato','México','37500','scrypt:32768:8:1$unKeOGETM6Oa1YGd$6909a95c9869dd8aab1deb7bc38b1e9fe816f04b5f5c0550b61585b6e933010433c365a2aeec940ba6fd0666a92490ea108d4c3e2746d0a03e61d997902ed866','2026-04-13 17:56:04',1);
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lotes`
--

DROP TABLE IF EXISTS `lotes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lotes` (
  `id_lote` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `cantidad` int NOT NULL,
  `activo` int NOT NULL,
  PRIMARY KEY (`id_lote`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lotes`
--

LOCK TABLES `lotes` WRITE;
/*!40000 ALTER TABLE `lotes` DISABLE KEYS */;
INSERT INTO `lotes` VALUES (1,'Lote pequeño (10 piezas)',10,1),(2,'Lote básico (20 piezas)',20,1),(3,'Lote medio (50 piezas)',50,1),(4,'Lote grande (100 piezas)',100,1),(5,'Lote producción (200 piezas)',200,1);
/*!40000 ALTER TABLE `lotes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `materias_primas`
--

DROP TABLE IF EXISTS `materias_primas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `materias_primas` (
  `id_materia_prima` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(120) NOT NULL,
  `id_categoria_materia_prima` int NOT NULL,
  `id_unidad_medida` int NOT NULL,
  `id_proveedor` int NOT NULL,
  `stock_actual` decimal(14,2) NOT NULL,
  `stock_minimo` decimal(14,2) NOT NULL,
  `costo_unit_prom` decimal(12,2) NOT NULL,
  `merma_pct` decimal(5,2) DEFAULT NULL,
  `activo` int NOT NULL,
  PRIMARY KEY (`id_materia_prima`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `id_categoria_materia_prima` (`id_categoria_materia_prima`),
  KEY `id_unidad_medida` (`id_unidad_medida`),
  KEY `id_proveedor` (`id_proveedor`),
  CONSTRAINT `materias_primas_ibfk_1` FOREIGN KEY (`id_categoria_materia_prima`) REFERENCES `categorias_materia_prima` (`id_categoria_materia_prima`),
  CONSTRAINT `materias_primas_ibfk_2` FOREIGN KEY (`id_unidad_medida`) REFERENCES `unidades_medida` (`id_unidad_medida`),
  CONSTRAINT `materias_primas_ibfk_3` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materias_primas`
--

LOCK TABLES `materias_primas` WRITE;
/*!40000 ALTER TABLE `materias_primas` DISABLE KEYS */;
INSERT INTO `materias_primas` VALUES (1,'Cuero vacuno liso color café',1,1,1,950.00,120.00,29.50,6.00,1),(2,'Cuero vacuno liso color negro',1,1,1,1100.00,140.00,28.80,6.00,1),(3,'Cuero vacuno graneado miel',1,1,1,254.80,100.00,31.20,6.00,1),(4,'Forro textil poliéster beige',2,2,3,175.41,25.00,42.00,2.00,1),(5,'Forro textil poliéster negro',2,2,3,220.00,30.00,42.00,2.00,1),(6,'Microfibra gamuzada camel',2,2,3,90.00,15.00,68.00,2.00,1),(7,'Cierre metálico 20 cm níquel',3,3,2,350.00,60.00,8.50,0.00,1),(8,'Cierre metálico 35 cm níquel',3,3,2,230.00,40.00,14.50,0.00,1),(9,'Hebilla clásica para cinturón 40 mm',3,3,2,180.00,30.00,32.00,0.00,1),(10,'Broche magnético 18 mm',3,3,2,420.00,80.00,6.80,0.00,1),(11,'Argolla D 25 mm',3,3,2,280.00,50.00,4.20,0.00,1),(12,'Remache doble cabeza 9 mm',3,3,2,1000.00,200.00,1.20,0.00,1),(13,'Pegamento para cuero base solvente',4,4,4,54.48,8.00,118.00,3.00,1),(14,'Tinta para canto color café',4,4,4,18.00,3.00,165.00,2.00,1),(15,'Hilo encerado café 0.8 mm',5,2,3,7880.00,1200.00,0.55,0.00,1),(16,'Hilo encerado negro 0.8 mm',5,2,3,8200.00,1200.00,0.55,0.00,1),(17,'Espuma laminada 3 mm',6,2,3,110.00,15.00,36.00,1.00,1),(18,'Entretela rígida adhesiva',6,2,3,127.98,20.00,24.00,1.00,1),(19,'Caja kraft mediana',7,3,5,250.00,50.00,11.50,0.00,1),(20,'Bolsa cubrepolvo de tela',7,3,5,180.00,40.00,9.80,0.00,1),(21,'Piel premium',1,1,6,300.00,50.00,50.00,0.00,1);
/*!40000 ALTER TABLE `materias_primas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mermas`
--

DROP TABLE IF EXISTS `mermas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mermas` (
  `id_merma` int NOT NULL AUTO_INCREMENT,
  `id_orden_produccion` int NOT NULL,
  `tipo` varchar(30) NOT NULL,
  `estado` varchar(30) NOT NULL,
  `observaciones` varchar(255) DEFAULT NULL,
  `creado_en` datetime NOT NULL,
  PRIMARY KEY (`id_merma`),
  KEY `id_orden_produccion` (`id_orden_produccion`),
  CONSTRAINT `mermas_ibfk_1` FOREIGN KEY (`id_orden_produccion`) REFERENCES `ordenes_produccion` (`id_orden_produccion`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mermas`
--

LOCK TABLES `mermas` WRITE;
/*!40000 ALTER TABLE `mermas` DISABLE KEYS */;
INSERT INTO `mermas` VALUES (1,1,'RECUPERABLE','DISPONIBLE','Merma capturada manualmente al finalizar la orden OP20260413-0001','2026-04-13 18:11:50');
/*!40000 ALTER TABLE `mermas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mermas_detalle`
--

DROP TABLE IF EXISTS `mermas_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mermas_detalle` (
  `id_merma_detalle` int NOT NULL AUTO_INCREMENT,
  `id_merma` int NOT NULL,
  `id_materia_prima` int NOT NULL,
  `materia_prima_nombre` varchar(120) NOT NULL,
  `unidad_medida` varchar(20) NOT NULL,
  `cantidad` decimal(14,2) NOT NULL,
  `clasificacion` varchar(50) NOT NULL,
  `valor_estimado_unit` decimal(12,2) NOT NULL,
  `valor_estimado_total` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id_merma_detalle`),
  KEY `id_merma` (`id_merma`),
  KEY `id_materia_prima` (`id_materia_prima`),
  CONSTRAINT `mermas_detalle_ibfk_1` FOREIGN KEY (`id_merma`) REFERENCES `mermas` (`id_merma`),
  CONSTRAINT `mermas_detalle_ibfk_2` FOREIGN KEY (`id_materia_prima`) REFERENCES `materias_primas` (`id_materia_prima`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mermas_detalle`
--

LOCK TABLES `mermas_detalle` WRITE;
/*!40000 ALTER TABLE `mermas_detalle` DISABLE KEYS */;
INSERT INTO `mermas_detalle` VALUES (1,1,3,'Cuero vacuno graneado miel','dm2',25.20,'MERMA_PROCESO',31.20,786.24),(2,1,4,'Forro textil poliéster beige','m',0.09,'MERMA_PROCESO',42.00,3.78),(3,1,13,'Pegamento para cuero base solvente','litro',0.02,'MERMA_PROCESO',118.00,2.36),(4,1,18,'Entretela rígida adhesiva','m',0.02,'MERMA_PROCESO',24.00,0.48);
/*!40000 ALTER TABLE `mermas_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos_materia_prima`
--

DROP TABLE IF EXISTS `movimientos_materia_prima`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos_materia_prima` (
  `id_movimiento_materia_prima` int NOT NULL AUTO_INCREMENT,
  `id_materia_prima` int NOT NULL,
  `id_proveedor` int DEFAULT NULL,
  `tipo` varchar(20) NOT NULL,
  `cantidad` decimal(14,2) NOT NULL,
  `motivo` varchar(255) DEFAULT NULL,
  `creado_en` datetime NOT NULL,
  PRIMARY KEY (`id_movimiento_materia_prima`),
  KEY `id_materia_prima` (`id_materia_prima`),
  KEY `id_proveedor` (`id_proveedor`),
  CONSTRAINT `movimientos_materia_prima_ibfk_1` FOREIGN KEY (`id_materia_prima`) REFERENCES `materias_primas` (`id_materia_prima`),
  CONSTRAINT `movimientos_materia_prima_ibfk_2` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_materia_prima`
--

LOCK TABLES `movimientos_materia_prima` WRITE;
/*!40000 ALTER TABLE `movimientos_materia_prima` DISABLE KEYS */;
INSERT INTO `movimientos_materia_prima` VALUES (1,1,1,'ENTRADA',180.00,'Compra inicial de cuero café','2026-04-13 14:16:40'),(2,2,1,'ENTRADA',220.00,'Compra inicial de cuero negro','2026-04-13 14:16:40'),(3,4,NULL,'ENTRADA',40.00,'Ingreso por ajuste de inventario','2026-04-13 14:16:40'),(4,7,2,'ENTRADA',100.00,'Compra de cierres 20 cm','2026-04-13 14:16:40'),(5,9,2,'ENTRADA',40.00,'Compra de hebillas','2026-04-13 14:16:40'),(6,13,4,'ENTRADA',10.00,'Compra de adhesivo','2026-04-13 14:16:40');
/*!40000 ALTER TABLE `movimientos_materia_prima` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordenes_produccion`
--

DROP TABLE IF EXISTS `ordenes_produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordenes_produccion` (
  `id_orden_produccion` int NOT NULL AUTO_INCREMENT,
  `id_producto` int NOT NULL,
  `folio` varchar(30) NOT NULL,
  `id_lote` int NOT NULL,
  `cantidad` decimal(14,2) NOT NULL,
  `estado` varchar(30) NOT NULL,
  `costo_estimado` decimal(12,2) NOT NULL,
  `observaciones` varchar(255) DEFAULT NULL,
  `creado_en` datetime NOT NULL,
  PRIMARY KEY (`id_orden_produccion`),
  UNIQUE KEY `folio` (`folio`),
  KEY `id_producto` (`id_producto`),
  KEY `id_lote` (`id_lote`),
  CONSTRAINT `ordenes_produccion_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `ordenes_produccion_ibfk_2` FOREIGN KEY (`id_lote`) REFERENCES `lotes` (`id_lote`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordenes_produccion`
--

LOCK TABLES `ordenes_produccion` WRITE;
/*!40000 ALTER TABLE `ordenes_produccion` DISABLE KEYS */;
INSERT INTO `ordenes_produccion` VALUES (1,5,'OP20260413-0001',1,10.00,'COMPLETADA',14487.27,NULL,'2026-04-13 18:11:29');
/*!40000 ALTER TABLE `ordenes_produccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordenes_produccion_detalles`
--

DROP TABLE IF EXISTS `ordenes_produccion_detalles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordenes_produccion_detalles` (
  `id_orden_produccion_detalle` int NOT NULL AUTO_INCREMENT,
  `id_orden_produccion` int NOT NULL,
  `id_materia_prima` int NOT NULL,
  `materia_prima_nombre` varchar(120) NOT NULL,
  `unidad_medida` varchar(20) NOT NULL,
  `cantidad_base` decimal(14,2) NOT NULL,
  `cantidad_teorica` decimal(14,2) NOT NULL,
  `cantidad_consumida` decimal(14,2) NOT NULL,
  `costo_unitario` decimal(12,2) NOT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id_orden_produccion_detalle`),
  KEY `id_orden_produccion` (`id_orden_produccion`),
  KEY `id_materia_prima` (`id_materia_prima`),
  CONSTRAINT `ordenes_produccion_detalles_ibfk_1` FOREIGN KEY (`id_orden_produccion`) REFERENCES `ordenes_produccion` (`id_orden_produccion`),
  CONSTRAINT `ordenes_produccion_detalles_ibfk_2` FOREIGN KEY (`id_materia_prima`) REFERENCES `materias_primas` (`id_materia_prima`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordenes_produccion_detalles`
--

LOCK TABLES `ordenes_produccion_detalles` WRITE;
/*!40000 ALTER TABLE `ordenes_produccion_detalles` DISABLE KEYS */;
INSERT INTO `ordenes_produccion_detalles` VALUES (1,1,3,'Cuero vacuno graneado miel','dm2',42.00,420.00,445.20,31.20,13890.24),(2,1,4,'Forro textil poliéster beige','m',0.45,4.50,4.59,42.00,192.78),(3,1,8,'Cierre metálico 35 cm níquel','pieza',1.00,10.00,10.00,14.50,145.00),(4,1,11,'Argolla D 25 mm','pieza',2.00,20.00,20.00,4.20,84.00),(5,1,13,'Pegamento para cuero base solvente','litro',0.05,0.50,0.52,118.00,60.77),(6,1,15,'Hilo encerado café 0.8 mm','m',12.00,120.00,120.00,0.55,66.00),(7,1,18,'Entretela rígida adhesiva','m',0.20,2.00,2.02,24.00,48.48);
/*!40000 ALTER TABLE `ordenes_produccion_detalles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_detalles`
--

DROP TABLE IF EXISTS `pedido_detalles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_detalles` (
  `id_pedido_detalle` int NOT NULL AUTO_INCREMENT,
  `id_pedido` int NOT NULL,
  `id_producto` int NOT NULL,
  `producto_nombre` varchar(120) NOT NULL,
  `precio_unitario` decimal(12,2) NOT NULL,
  `cantidad` int NOT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id_pedido_detalle`),
  KEY `id_pedido` (`id_pedido`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `pedido_detalles_ibfk_1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`),
  CONSTRAINT `pedido_detalles_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_detalles`
--

LOCK TABLES `pedido_detalles` WRITE;
/*!40000 ALTER TABLE `pedido_detalles` DISABLE KEYS */;
INSERT INTO `pedido_detalles` VALUES (1,1,1,'Cartera Bifold Clásica',899.00,1,899.00),(2,1,2,'Monedero Compacto con Cierre',429.00,1,429.00),(3,1,14,'Llavero de Piel Artesanal',189.00,1,189.00),(4,2,5,'Bolsa Tote Siena',1699.00,1,1699.00),(5,3,1,'Cartera Bifold Clásica',899.00,1,899.00),(6,3,14,'Llavero de Piel Artesanal',189.00,1,189.00),(7,4,5,'Bolsa Tote Siena',1699.00,1,1699.00),(8,4,2,'Monedero Compacto con Cierre',429.00,1,429.00),(9,5,5,'Bolsa Tote Siena',1699.00,4,6796.00),(10,5,1,'Cartera Bifold Clásica',899.00,1,899.00);
/*!40000 ALTER TABLE `pedido_detalles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos` (
  `id_pedido` int NOT NULL AUTO_INCREMENT,
  `id_cliente` int NOT NULL,
  `folio` varchar(30) NOT NULL,
  `estado` varchar(30) NOT NULL,
  `total` decimal(12,2) NOT NULL,
  `nombre_envio` varchar(150) NOT NULL,
  `telefono_envio` varchar(30) DEFAULT NULL,
  `calle_envio` varchar(120) NOT NULL,
  `numero_envio` varchar(20) NOT NULL,
  `colonia_envio` varchar(120) NOT NULL,
  `ciudad_envio` varchar(80) NOT NULL,
  `estado_envio` varchar(80) NOT NULL,
  `pais_envio` varchar(80) NOT NULL,
  `cp_envio` varchar(10) NOT NULL,
  `notas` varchar(255) DEFAULT NULL,
  `creado_en` datetime NOT NULL,
  PRIMARY KEY (`id_pedido`),
  UNIQUE KEY `folio` (`folio`),
  KEY `id_cliente` (`id_cliente`),
  CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos`
--

LOCK TABLES `pedidos` WRITE;
/*!40000 ALTER TABLE `pedidos` DISABLE KEYS */;
INSERT INTO `pedidos` VALUES (1,1,'PED20260401-0001','Entregado',1508.00,'Juan Carlos Gómez Torres','4776123456','Av. Panorama','145','Panorama','León','Guanajuato','México','37160','Entregar por la tarde','2026-04-13 14:16:40'),(2,2,'PED20260402-0002','Pendiente',1699.00,'María Fernanda Ruiz Saldaña','4776987412','Blvd. Campestre','2208','Jardines del Moral','León','Guanajuato','México','37160','Tocar antes de entregar','2026-04-13 14:16:40'),(3,1,'PED20260411-0003','Entregado',1088.00,'Juan Carlos Gómez Torres','4776123456','Av. Panorama','145','Panorama','León','Guanajuato','México','37160','Entrega en recepción','2026-04-11 14:30:00'),(4,2,'PED20260412-0004','Entregado',2128.00,'María Fernanda Ruiz Saldaña','4776987412','Blvd. Campestre','2208','Jardines del Moral','León','Guanajuato','México','37160','Cliente solicita llamada previa','2026-04-12 11:15:00'),(5,4,'PED20260413-0005','Pendiente',7695.00,'Martin','3321663503','UTL','10','Av Universidad','Leon','Guanajuato','México','37500','Notas','2026-04-13 23:57:48');
/*!40000 ALTER TABLE `pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT,
  `id_categoria_producto` int NOT NULL,
  `sku` varchar(40) DEFAULT NULL,
  `nombre` varchar(120) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `precio_venta` decimal(12,2) NOT NULL,
  `stock_actual` decimal(14,2) NOT NULL,
  `costo_unit_prom` decimal(12,2) NOT NULL,
  `activo` int NOT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_producto`),
  UNIQUE KEY `nombre` (`nombre`),
  UNIQUE KEY `sku` (`sku`),
  KEY `id_categoria_producto` (`id_categoria_producto`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`id_categoria_producto`) REFERENCES `categorias_producto` (`id_categoria_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,1,'CL-CAR-001','Cartera Bifold Clásica','Cartera Bifold Clásica elaborada con materiales para marroquinería y acabado artesanal.',899.00,17.00,377.58,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/cartera_tfstrs.jpg'),(2,2,'CL-MON-001','Monedero Compacto con Cierre','Monedero Compacto con Cierre elaborada con materiales para marroquinería y acabado artesanal.',429.00,28.00,180.18,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/monedero_lcrize.jpg'),(3,3,'CL-TAR-001','Tarjetero Ejecutivo Slim','Tarjetero Ejecutivo Slim elaborada con materiales para marroquinería y acabado artesanal.',359.00,26.00,150.78,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/tarjetero_s2sdli.jpg'),(4,4,'CL-CIN-001','Cinturón Casual de Piel','Cinturón Casual de Piel elaborada con materiales para marroquinería y acabado artesanal.',649.00,20.00,272.58,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031772/cinturon_wt16ky.jpg'),(5,5,'CL-TOT-001','Bolsa Tote Siena','Bolsa Tote Siena elaborada con materiales para marroquinería y acabado artesanal.',1699.00,17.00,713.58,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031380/bolsaTote_oy10p0.jpg'),(6,6,'CL-BOL-001','Bolso de Mano Verona','Bolso de Mano Verona elaborada con materiales para marroquinería y acabado artesanal.',1499.00,10.00,629.58,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031772/bolsoMano_hjkdkd.jpg'),(7,7,'CL-MOC-001','Mochila Urbana de Piel','Mochila Urbana de Piel elaborada con materiales para marroquinería y acabado artesanal.',2199.00,8.00,923.58,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/mochila_r8f2b2.jpg'),(8,8,'CL-MAR-001','Mariconera Crossbody','Mariconera Crossbody elaborada con materiales para marroquinería y acabado artesanal.',1099.00,14.00,461.58,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/mariconera_uh5yja.jpg'),(9,9,'CL-POR-001','Portafolio Ejecutivo Premium','Portafolio Ejecutivo Premium elaborada con materiales para marroquinería y acabado artesanal.',2699.00,6.00,1133.58,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/portafolio_cav9al.jpg'),(10,10,'CL-NEC-001','Neceser de Viaje','Neceser de Viaje elaborada con materiales para marroquinería y acabado artesanal.',649.00,22.00,272.58,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031767/neceser_ogn1ti.jpg'),(11,11,'CL-FUN-001','Funda Laptop 15 Pulgadas','Funda Laptop 15 Pulgadas elaborada con materiales para marroquinería y acabado artesanal.',1299.00,11.00,545.58,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031771/fundaLaptop_kys2db.jpg'),(12,12,'CL-PAS-001','Porta Pasaporte Atlas','Porta Pasaporte Atlas elaborada con materiales para marroquinería y acabado artesanal.',469.00,24.00,196.98,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/portaPasaporte_yfgmxa.jpg'),(13,13,'CL-EST-001','Estuche para Lentes Soft Case','Estuche para Lentes Soft Case elaborada con materiales para marroquinería y acabado artesanal.',399.00,22.00,167.58,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031771/estucheLentes_g2wsng.jpg'),(14,14,'CL-LLA-001','Llavero de Piel Artesanal','Llavero de Piel Artesanal elaborada con materiales para marroquinería y acabado artesanal.',189.00,45.00,79.38,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031771/llavero_jawo3i.jpg'),(15,15,'CL-PUL-001','Pulsera Trenzada de Piel','Pulsera Trenzada de Piel elaborada con materiales para marroquinería y acabado artesanal.',249.00,34.00,104.58,1,'https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/pulsera_euavph.jpg');
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id_proveedor` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `rfc` varchar(20) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `telefono` varchar(30) DEFAULT NULL,
  `calle` varchar(120) DEFAULT NULL,
  `numero` varchar(20) DEFAULT NULL,
  `colonia` varchar(120) DEFAULT NULL,
  `ciudad` varchar(80) DEFAULT NULL,
  `estado` varchar(80) DEFAULT NULL,
  `pais` varchar(80) DEFAULT NULL,
  `cp` varchar(10) DEFAULT NULL,
  `activo` int NOT NULL,
  PRIMARY KEY (`id_proveedor`),
  UNIQUE KEY `rfc` (`rfc`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES (1,'Pieles y Acabados del Bajío','PAB190315QH1','ventas@pabajio.com','4777142201','Blvd. Timoteo Lozano','4210','Ciudad Industrial','León','Guanajuato','México','37490',1),(2,'Herrajes Finos de León','HFL180928LJ3','contacto@herrajesfinosleon.com','4777138842','Calle Delta','152','Industrial Delta','León','Guanajuato','México','37545',1),(3,'Textiles y Forros del Centro','TFC170611MT8','pedidos@forroscentro.com','3331457788','Av. Colón','1880','Del Fresno','Guadalajara','Jalisco','México','44900',1),(4,'Suministros Químicos Industriales MX','SQI160902DA5','ventas@sqmexico.com','8183321109','Av. Ruiz Cortines','5400','Mitras Norte','Monterrey','Nuevo León','México','64320',1),(5,'Empaques y Accesorios de Piel Occidente','EAP210430TR6','info@eapoccidente.com','3319274650','Calzada Independencia','3245','San Andrés','Guadalajara','Jalisco','México','44810',1),(6,'Proveedor 1','DGSE040506AB1','proveedor1@test.com','4775669822','UTL','10','Av Universidad','Leon','Guanajuato','México','37500',1);
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receta_detalles`
--

DROP TABLE IF EXISTS `receta_detalles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receta_detalles` (
  `id_receta_detalle` int NOT NULL AUTO_INCREMENT,
  `id_receta` int NOT NULL,
  `id_materia_prima` int NOT NULL,
  `cantidad` decimal(14,2) NOT NULL,
  PRIMARY KEY (`id_receta_detalle`),
  KEY `id_receta` (`id_receta`),
  KEY `id_materia_prima` (`id_materia_prima`),
  CONSTRAINT `receta_detalles_ibfk_1` FOREIGN KEY (`id_receta`) REFERENCES `recetas` (`id_receta`),
  CONSTRAINT `receta_detalles_ibfk_2` FOREIGN KEY (`id_materia_prima`) REFERENCES `materias_primas` (`id_materia_prima`)
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receta_detalles`
--

LOCK TABLES `receta_detalles` WRITE;
/*!40000 ALTER TABLE `receta_detalles` DISABLE KEYS */;
INSERT INTO `receta_detalles` VALUES (1,1,1,18.00),(2,1,4,0.12),(3,1,13,0.02),(4,1,15,5.00),(5,1,14,0.01),(6,2,2,8.00),(7,2,5,0.06),(8,2,7,1.00),(9,2,13,0.01),(10,2,16,3.00),(11,3,2,7.00),(12,3,6,0.04),(13,3,13,0.01),(14,3,16,2.50),(15,3,14,0.01),(16,4,1,22.00),(17,4,9,1.00),(18,4,15,2.00),(19,4,14,0.01),(20,5,3,42.00),(21,5,4,0.45),(22,5,8,1.00),(23,5,11,2.00),(24,5,13,0.05),(25,5,15,12.00),(26,5,18,0.20),(27,6,1,34.00),(28,6,6,0.35),(29,6,8,1.00),(30,6,10,1.00),(31,6,13,0.04),(32,6,15,9.00),(33,6,18,0.18),(34,7,2,58.00),(35,7,5,0.75),(36,7,8,2.00),(37,7,10,2.00),(38,7,11,4.00),(39,7,13,0.08),(40,7,16,18.00),(41,7,17,0.35),(42,8,2,24.00),(43,8,5,0.18),(44,8,7,2.00),(45,8,11,2.00),(46,8,13,0.03),(47,8,16,7.00),(48,9,1,68.00),(49,9,6,0.80),(50,9,8,2.00),(51,9,10,2.00),(52,9,11,4.00),(53,9,12,6.00),(54,9,13,0.10),(55,9,15,20.00),(56,9,17,0.40),(57,9,18,0.30),(58,10,2,16.00),(59,10,5,0.16),(60,10,7,1.00),(61,10,13,0.02),(62,10,16,4.00),(63,11,2,30.00),(64,11,6,0.40),(65,11,8,2.00),(66,11,13,0.04),(67,11,16,8.00),(68,11,17,0.45),(69,12,1,9.00),(70,12,6,0.05),(71,12,13,0.01),(72,12,15,2.00),(73,12,14,0.01),(74,13,2,10.00),(75,13,6,0.08),(76,13,10,1.00),(77,13,13,0.01),(78,13,16,2.00),(79,13,17,0.05),(80,14,1,1.50),(81,14,12,1.00),(82,14,15,0.50),(83,15,2,2.50),(84,15,10,1.00),(85,15,16,0.50),(86,16,11,1.00),(87,16,3,50.00);
/*!40000 ALTER TABLE `receta_detalles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recetas`
--

DROP TABLE IF EXISTS `recetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas` (
  `id_receta` int NOT NULL AUTO_INCREMENT,
  `id_producto` int DEFAULT NULL,
  `nombre` varchar(150) NOT NULL,
  `rendimiento` decimal(14,2) NOT NULL,
  `costo_estimado` decimal(12,2) NOT NULL,
  `activo` int NOT NULL,
  `creado_en` datetime NOT NULL,
  PRIMARY KEY (`id_receta`),
  UNIQUE KEY `id_producto` (`id_producto`),
  CONSTRAINT `recetas_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas`
--

LOCK TABLES `recetas` WRITE;
/*!40000 ALTER TABLE `recetas` DISABLE KEYS */;
INSERT INTO `recetas` VALUES (1,1,'Receta Cartera Bifold Clásica',1.00,574.86,1,'2026-04-13 14:16:39'),(2,2,'Receta Monedero Compacto con Cierre',1.00,258.16,1,'2026-04-13 14:16:39'),(3,3,'Receta Tarjetero Ejecutivo Slim',1.00,220.74,1,'2026-04-13 14:16:39'),(4,4,'Receta Cinturón Casual de Piel',1.00,722.72,1,'2026-04-13 14:16:39'),(5,5,'Receta Bolsa Tote Siena',1.00,1448.73,1,'2026-04-13 14:16:39'),(6,6,'Receta Bolso de Mano Verona',1.00,1122.93,1,'2026-04-13 14:16:39'),(7,7,'Receta Mochila Urbana de Piel',1.00,1894.50,1,'2026-04-13 14:16:40'),(8,8,'Receta Mariconera Crossbody',1.00,773.28,1,'2026-04-13 14:16:40'),(9,9,'Receta Portafolio Ejecutivo Premium',1.00,2293.42,1,'2026-04-13 14:16:40'),(10,10,'Receta Neceser de Viaje',1.00,508.43,1,'2026-04-13 14:16:40'),(11,11,'Receta Funda Laptop 15 Pulgadas',1.00,998.21,1,'2026-04-13 14:16:40'),(12,12,'Receta Porta Pasaporte Atlas',1.00,288.90,1,'2026-04-13 14:16:40'),(13,13,'Receta Estuche para Lentes Soft Case',1.00,321.76,1,'2026-04-13 14:16:40'),(14,14,'Receta Llavero de Piel Artesanal',1.00,48.38,1,'2026-04-13 14:16:40'),(15,15,'Receta Pulsera Trenzada de Piel',1.00,83.40,1,'2026-04-13 14:16:40'),(16,NULL,'Receta 1',1.00,1657.80,1,'2026-04-13 18:11:01');
/*!40000 ALTER TABLE `recetas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(30) NOT NULL,
  `descripcion` varchar(120) NOT NULL,
  PRIMARY KEY (`id_rol`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'ADMIN','Administrador'),(2,'EMPLEADO','Empleado');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unidades_medida`
--

DROP TABLE IF EXISTS `unidades_medida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unidades_medida` (
  `id_unidad_medida` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(20) NOT NULL,
  `activo` int NOT NULL,
  PRIMARY KEY (`id_unidad_medida`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unidades_medida`
--

LOCK TABLES `unidades_medida` WRITE;
/*!40000 ALTER TABLE `unidades_medida` DISABLE KEYS */;
INSERT INTO `unidades_medida` VALUES (1,'dm2',1),(2,'m',1),(3,'pieza',1),(4,'litro',1);
/*!40000 ALTER TABLE `unidades_medida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `id_rol` int NOT NULL,
  `nombre` varchar(120) NOT NULL,
  `email` varchar(120) NOT NULL,
  `telefono` varchar(10) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `activo` int NOT NULL,
  `creado_en` datetime NOT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `telefono` (`telefono`),
  KEY `id_rol` (`id_rol`),
  CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,1,'Martín López Herrera','admin@casaleon.com','4771010101','scrypt:32768:8:1$O2ggBsxS2MO6Y8xx$35019fe9144e1768afaeea38fd9abeceff95df91f00882976441860e28576208ef5c448a92142a87c9d1eb34a7b61258db7007304471a9002a6c1c2cfe93509f',1,'2026-04-13 14:16:39'),(2,2,'Ana Sofía Ramírez','empleado@casaleon.com','4772020202','scrypt:32768:8:1$ecDrVEhWxQwawui5$d0a81c478c7bf4844f9fd4912310fb67a7105804ce4aacf7df7563ef0b400439c677917106af02add96f01e7c41ab6c9cab5ebe7af6e2d16cc687d69a2b39837',1,'2026-04-13 14:16:39'),(3,2,'Diego Fernández Cruz','ventas@casaleon.com','4773030303','scrypt:32768:8:1$hExT9UcS59JwXLTA$54deb03971ab38e639f19707962e369b21e734b124ce82ada75ac278fb1ca60c2d4c1fade18612fe434ed1f6c3039c699d3114f541160913d3ce8e5c8a2603f8',1,'2026-04-13 14:16:39'),(4,2,'Luis Arturo Navarro','produccion@casaleon.com','4774040404','scrypt:32768:8:1$BjhuTIlOAXOMAluK$0f1c8936d668f671d699d20a4239533ab24135f209927d5df66ec2aa7fca148e5b698663333178dafe60d47766da3addd1458963a732d83878ae634c8f2af645',1,'2026-04-13 14:16:39'),(5,2,'Paola Jiménez Ortega','compras@casaleon.com','4775050505','scrypt:32768:8:1$JyQgHQXGNn5KLvJd$d371a81ad0c87551659b66625b1249cb3661cb480db9d1a318872a47fd738933207ccc6bd2f1afeff2ebb908079fc04592e865a5e06ffbecf425894320c6b8a3',1,'2026-04-13 14:16:39');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id_venta` int NOT NULL AUTO_INCREMENT,
  `folio` varchar(30) NOT NULL,
  `id_usuario` int NOT NULL,
  `total` decimal(12,2) NOT NULL,
  `metodo_pago` varchar(30) NOT NULL,
  `observaciones` varchar(255) DEFAULT NULL,
  `creado_en` datetime NOT NULL,
  PRIMARY KEY (`id_venta`),
  UNIQUE KEY `folio` (`folio`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas_detalle`
--

DROP TABLE IF EXISTS `ventas_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas_detalle` (
  `id_venta_detalle` int NOT NULL AUTO_INCREMENT,
  `id_venta` int NOT NULL,
  `id_producto` int NOT NULL,
  `producto_nombre` varchar(120) NOT NULL,
  `precio_unitario` decimal(12,2) NOT NULL,
  `cantidad` decimal(14,2) NOT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id_venta_detalle`),
  KEY `id_venta` (`id_venta`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `ventas_detalle_ibfk_1` FOREIGN KEY (`id_venta`) REFERENCES `ventas` (`id_venta`),
  CONSTRAINT `ventas_detalle_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas_detalle`
--

LOCK TABLES `ventas_detalle` WRITE;
/*!40000 ALTER TABLE `ventas_detalle` DISABLE KEYS */;
/*!40000 ALTER TABLE `ventas_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'fabrica_pieles2'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-13 18:13:59
