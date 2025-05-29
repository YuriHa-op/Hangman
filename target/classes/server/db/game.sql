-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: May 29, 2025 at 02:05 AM
-- Server version: 9.1.0
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `game`
--

-- --------------------------------------------------------

--
-- Table structure for table `games`
--

DROP TABLE IF EXISTS `games`;
CREATE TABLE IF NOT EXISTS `games` (
  `game_id` varchar(36) NOT NULL,
  `total_rounds` int NOT NULL,
  `overall_winner` varchar(50) DEFAULT NULL,
  `game_end_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `games`
--

INSERT INTO `games` (`game_id`, `total_rounds`, `overall_winner`, `game_end_time`) VALUES
('00a86bb1-0723-44a7-9419-2705d1f1c683', 2, 'toomuch', '2025-05-28 17:43:26'),
('00b6302b-6c6c-459b-92af-eaa07be51ccf', 3, 'yuri', '2025-05-28 01:07:15'),
('02b0df08-fee6-47ab-8b19-cb6a933dc501', 4, 'onemoredoor', '2025-05-28 21:27:39'),
('063099f6-425e-42e8-9d4c-3aaa05e35ac0', 2, 'yuri', '2025-05-28 22:02:43'),
('08723048-ba2b-45ee-987b-3dac974b7d29', 3, 'yuri', '2025-05-28 18:40:39'),
('0d7ca943-92a9-4d01-89c2-d80bf3223fbe', 3, 'toomuch', '2025-05-28 01:07:15'),
('15da0168-2e98-4bea-989f-a838c0101871', 4, 'toomuch', '2025-05-28 19:08:40'),
('165541a5-d4a5-43e0-978b-a8585735125e', 5, 'toomuch', '2025-05-28 01:07:15'),
('19d8d4ac-52a4-416d-a581-8e3233f94a0b', 3, 'toomuch', '2025-05-28 01:07:15'),
('1c7164f8-17c9-4f6e-8d3e-185fd69b4c80', 2, 'yuri', '2025-05-28 01:14:21'),
('1eecab5c-5916-4e07-b942-37f1728c186f', 5, 'yuriha', '2025-05-28 01:07:15'),
('26994501-75a2-40b9-a256-f24c59bceffb', 4, 'crane', '2025-05-28 21:12:23'),
('299c35d9-e028-4496-88cf-ed284748bc5f', 3, 'yuriha', '2025-05-28 01:07:15'),
('2bd3c6df-0d00-4bc8-9fbf-5b98dae47298', 3, 'yuri', '2025-05-28 01:07:15'),
('30e93aa0-7c0c-4072-923e-643386d69527', 5, 'yuriha', '2025-05-28 01:07:15'),
('3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 7, 'toomuch', '2025-05-28 01:07:15'),
('3dec840b-fbc8-4568-b0b8-0ad9818f6645', 3, 'crane', '2025-05-28 17:42:24'),
('3e60f930-5222-4494-8142-23d9fe4aee73', 6, 'yuriha', '2025-05-28 01:07:15'),
('4ea0c587-7b69-4d27-94b0-d0f951b49cf5', 2, 'yuriha', '2025-05-28 18:53:01'),
('5187fafd-6c4c-4116-a6f5-b999b7ebd62b', 5, 'yuriha', '2025-05-28 01:07:15'),
('5287e9db-0e59-40f4-900e-89ef78342bbb', 2, 'onemoredoor', '2025-05-28 21:34:40'),
('5c507e58-860c-4c80-8463-9956ed631fb5', 5, 'yuri', '2025-05-28 01:07:15'),
('65544f8a-d001-4dc8-87ab-0d6aee5616af', 4, 'crane', '2025-05-28 21:18:15'),
('66ba666b-3574-4d0f-aacb-1ad5a848b302', 5, 'yuriha', '2025-05-28 01:07:15'),
('70931c70-803a-4b83-87ee-dd473801e20a', 2, 'yuri', '2025-05-28 02:35:06'),
('736b68e5-6f9e-44fb-ae66-f7db6709c504', 4, 'toomuch', '2025-05-28 01:07:15'),
('755c69b3-308a-454b-aea2-115f1766c1d8', 3, 'crane', '2025-05-28 19:02:20'),
('7b76c178-dffe-484f-9f63-257fa03a88cc', 3, 'yuri', '2025-05-28 01:22:56'),
('7c49c16a-b851-4604-8cc2-37e6032de253', 4, 'yuri', '2025-05-28 01:07:15'),
('7d090094-a7bf-4950-9f1d-d710f82e943e', 3, 'yuriha', '2025-05-28 01:07:15'),
('819bba4e-dbb5-46b4-b66d-6e99bae0fc2b', 2, 'yuriha', '2025-05-28 01:07:15'),
('8eda820f-c20d-4a53-bf5b-689eded4b542', 2, 'yuri', '2025-05-28 21:38:46'),
('8f8eab42-4b6c-4d1c-b197-f664abee4c2f', 3, 'yuriha', '2025-05-28 01:07:15'),
('92a33d73-3a47-472e-a916-100a051cd0da', 4, 'yuri', '2025-05-28 01:07:15'),
('935a7a1b-a55c-41be-aca0-28efbc09f0dc', 3, 'toomuch', '2025-05-28 01:07:15'),
('97058e14-c670-4639-9896-cf50d8c2c614', 1, 'yuri', '2025-05-28 21:56:58'),
('a3b6a5ab-381a-4e00-8039-3333bc84c88b', 3, 'yuri', '2025-05-28 22:43:33'),
('a5cf04d0-32ea-4104-b23e-c83302d7eeaf', 2, 'crane', '2025-05-28 17:45:52'),
('aa6a4731-9471-4ffa-aa96-c3fe8300764d', 3, 'toomuch', '2025-05-28 01:07:15'),
('ae241490-ced9-461a-b18e-4b32759a8076', 2, 'toomuch', '2025-05-28 18:47:55'),
('b88bacfa-f6f6-4ca9-bd24-71dd2d58581d', 4, 'yuriha', '2025-05-28 01:07:15'),
('bf32d312-7ae3-4018-a552-055f1ee9a39b', 4, 'toomuch', '2025-05-28 01:07:15'),
('c1d0fb9b-86bf-4ecc-839d-657114192417', 2, 'yuri', '2025-05-28 01:50:51'),
('c530a61f-62bd-415c-af62-6a76f374f428', 3, 'yuri', '2025-05-28 01:07:15'),
('c5dc63e9-14ec-4965-99e6-2123950bfc4b', 2, 'yuri', '2025-05-28 22:01:19'),
('d0ce578e-6bb1-48dd-acf3-47feabc2c541', 2, 'yuriha', '2025-05-28 21:07:52'),
('d43ee0d5-372d-4575-a4c5-859b861144d7', 2, 'dontmake', '2025-05-28 18:10:20'),
('d4b22875-dc49-4fff-b336-589ba82adaaf', 3, 'yuri', '2025-05-28 22:25:12'),
('d6b1943d-4cf4-409b-8701-3a84d5aebf99', 4, 'yuri', '2025-05-28 21:01:37'),
('da03b263-2dd1-4dec-879e-530522eea90a', 2, 'yuri', '2025-05-28 01:15:21'),
('dd863b2d-cf90-41fe-b2a9-caf3ca102691', 3, 'toomuch', '2025-05-28 01:07:15'),
('e7dd87ca-e02c-484b-86a3-767a1c3a3b8d', 3, 'yuriha', '2025-05-28 01:07:15'),
('e8d11aff-d9a6-419b-b6c1-d2aacc90a010', 2, 'yuri', '2025-05-28 21:22:45'),
('ee5fc475-1983-431c-9166-fb5e8c952790', 3, 'yuri', '2025-05-28 01:07:15'),
('f3cf3efe-cb9a-4ba6-a762-af0274bcaecc', 3, 'yuriha', '2025-05-28 01:45:50'),
('ffe448fe-28ff-49e0-abb6-18e28168ffbd', 4, 'yuri', '2025-05-28 01:07:15');

-- --------------------------------------------------------

--
-- Table structure for table `game_players`
--

DROP TABLE IF EXISTS `game_players`;
CREATE TABLE IF NOT EXISTS `game_players` (
  `game_id` varchar(36) NOT NULL,
  `player_name` varchar(50) NOT NULL,
  PRIMARY KEY (`game_id`,`player_name`),
  KEY `game_id` (`game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `game_players`
--

INSERT INTO `game_players` (`game_id`, `player_name`) VALUES
('00a86bb1-0723-44a7-9419-2705d1f1c683', 'crane'),
('00a86bb1-0723-44a7-9419-2705d1f1c683', 'toomuch'),
('00a86bb1-0723-44a7-9419-2705d1f1c683', 'yuri'),
('02b0df08-fee6-47ab-8b19-cb6a933dc501', 'onemoredoor'),
('02b0df08-fee6-47ab-8b19-cb6a933dc501', 'yuri'),
('063099f6-425e-42e8-9d4c-3aaa05e35ac0', 'yuri'),
('063099f6-425e-42e8-9d4c-3aaa05e35ac0', 'yuriha'),
('08723048-ba2b-45ee-987b-3dac974b7d29', 'crane'),
('08723048-ba2b-45ee-987b-3dac974b7d29', 'yuri'),
('08723048-ba2b-45ee-987b-3dac974b7d29', 'yuriha'),
('15da0168-2e98-4bea-989f-a838c0101871', 'toomuch'),
('15da0168-2e98-4bea-989f-a838c0101871', 'yuri'),
('1c7164f8-17c9-4f6e-8d3e-185fd69b4c80', 'yuri'),
('1c7164f8-17c9-4f6e-8d3e-185fd69b4c80', 'yuriha'),
('26994501-75a2-40b9-a256-f24c59bceffb', 'crane'),
('26994501-75a2-40b9-a256-f24c59bceffb', 'yuri'),
('3dec840b-fbc8-4568-b0b8-0ad9818f6645', 'crane'),
('3dec840b-fbc8-4568-b0b8-0ad9818f6645', 'toomuch'),
('3dec840b-fbc8-4568-b0b8-0ad9818f6645', 'yuri'),
('4ea0c587-7b69-4d27-94b0-d0f951b49cf5', 'toomuch'),
('4ea0c587-7b69-4d27-94b0-d0f951b49cf5', 'yuri'),
('4ea0c587-7b69-4d27-94b0-d0f951b49cf5', 'yuriha'),
('5287e9db-0e59-40f4-900e-89ef78342bbb', 'onemoredoor'),
('5287e9db-0e59-40f4-900e-89ef78342bbb', 'yuri'),
('65544f8a-d001-4dc8-87ab-0d6aee5616af', 'crane'),
('65544f8a-d001-4dc8-87ab-0d6aee5616af', 'yuri'),
('70931c70-803a-4b83-87ee-dd473801e20a', 'toomuch'),
('70931c70-803a-4b83-87ee-dd473801e20a', 'yuri'),
('70931c70-803a-4b83-87ee-dd473801e20a', 'yuriha'),
('755c69b3-308a-454b-aea2-115f1766c1d8', 'crane'),
('755c69b3-308a-454b-aea2-115f1766c1d8', 'toomuch'),
('755c69b3-308a-454b-aea2-115f1766c1d8', 'yuri'),
('755c69b3-308a-454b-aea2-115f1766c1d8', 'yuriha'),
('7b76c178-dffe-484f-9f63-257fa03a88cc', 'onemoredoor'),
('7b76c178-dffe-484f-9f63-257fa03a88cc', 'toomuch'),
('7b76c178-dffe-484f-9f63-257fa03a88cc', 'yuri'),
('7b76c178-dffe-484f-9f63-257fa03a88cc', 'yuriha'),
('8eda820f-c20d-4a53-bf5b-689eded4b542', 'yuri'),
('8eda820f-c20d-4a53-bf5b-689eded4b542', 'yuriha'),
('97058e14-c670-4639-9896-cf50d8c2c614', 'yuri'),
('97058e14-c670-4639-9896-cf50d8c2c614', 'yuriha'),
('a3b6a5ab-381a-4e00-8039-3333bc84c88b', 'toomuch'),
('a3b6a5ab-381a-4e00-8039-3333bc84c88b', 'yuri'),
('a5cf04d0-32ea-4104-b23e-c83302d7eeaf', 'crane'),
('a5cf04d0-32ea-4104-b23e-c83302d7eeaf', 'toomuch'),
('a5cf04d0-32ea-4104-b23e-c83302d7eeaf', 'yuri'),
('ae241490-ced9-461a-b18e-4b32759a8076', 'toomuch'),
('ae241490-ced9-461a-b18e-4b32759a8076', 'yuri'),
('ae241490-ced9-461a-b18e-4b32759a8076', 'yuriha'),
('c1d0fb9b-86bf-4ecc-839d-657114192417', 'yuri'),
('c1d0fb9b-86bf-4ecc-839d-657114192417', 'yuriha'),
('c5dc63e9-14ec-4965-99e6-2123950bfc4b', 'yuri'),
('c5dc63e9-14ec-4965-99e6-2123950bfc4b', 'yuriha'),
('d0ce578e-6bb1-48dd-acf3-47feabc2c541', 'yuri'),
('d0ce578e-6bb1-48dd-acf3-47feabc2c541', 'yuriha'),
('d43ee0d5-372d-4575-a4c5-859b861144d7', 'dontmake'),
('d43ee0d5-372d-4575-a4c5-859b861144d7', 'yuri'),
('d4b22875-dc49-4fff-b336-589ba82adaaf', 'crane'),
('d4b22875-dc49-4fff-b336-589ba82adaaf', 'toomuch'),
('d4b22875-dc49-4fff-b336-589ba82adaaf', 'yuri'),
('d6b1943d-4cf4-409b-8701-3a84d5aebf99', 'toomuch'),
('d6b1943d-4cf4-409b-8701-3a84d5aebf99', 'yuri'),
('da03b263-2dd1-4dec-879e-530522eea90a', 'yuri'),
('da03b263-2dd1-4dec-879e-530522eea90a', 'yuriha'),
('e8d11aff-d9a6-419b-b6c1-d2aacc90a010', 'yuri'),
('e8d11aff-d9a6-419b-b6c1-d2aacc90a010', 'yuriha'),
('f3cf3efe-cb9a-4ba6-a762-af0274bcaecc', 'yuri'),
('f3cf3efe-cb9a-4ba6-a762-af0274bcaecc', 'yuriha');

-- --------------------------------------------------------

--
-- Table structure for table `game_results`
--

DROP TABLE IF EXISTS `game_results`;
CREATE TABLE IF NOT EXISTS `game_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `player_id` int DEFAULT NULL,
  `word_guessed` varchar(100) DEFAULT NULL,
  `win_status` tinyint(1) DEFAULT NULL,
  `game_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `player_id` (`player_id`)
) ENGINE=MyISAM AUTO_INCREMENT=161 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `players`
--

DROP TABLE IF EXISTS `players`;
CREATE TABLE IF NOT EXISTS `players` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `wins` int DEFAULT '0',
  `currently_logged_in` tinyint(1) DEFAULT '0',
  `role` enum('player','admin') DEFAULT 'player',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `players`
--

INSERT INTO `players` (`id`, `username`, `password`, `wins`, `currently_logged_in`, `role`) VALUES
(0, 'yuri', '1111', 32, 0, 'admin'),
(2, 'Yuriha', '2222', 5, 0, 'player'),
(6, 'toomuch', '1111', 3, 0, 'player'),
(7, 'Idontwanna', '1111', 0, 0, 'player'),
(8, 'dontmake', '1111', 2, 0, 'player'),
(9, 'meclose', '', 0, 0, 'player'),
(10, 'onemoredoor', '1111', 2, 0, 'player'),
(12, 'crane', '1111', 6, 0, 'player'),
(13, 'yura', '1111', 0, 0, 'player');

-- --------------------------------------------------------

--
-- Table structure for table `rounds`
--

DROP TABLE IF EXISTS `rounds`;
CREATE TABLE IF NOT EXISTS `rounds` (
  `round_id` int NOT NULL AUTO_INCREMENT,
  `game_id` varchar(36) NOT NULL,
  `round_number` int NOT NULL,
  `word` varchar(100) NOT NULL,
  `winner` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`round_id`),
  KEY `game_id` (`game_id`)
) ENGINE=InnoDB AUTO_INCREMENT=209 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `rounds`
--

INSERT INTO `rounds` (`round_id`, `game_id`, `round_number`, `word`, `winner`) VALUES
(1, '30e93aa0-7c0c-4072-923e-643386d69527', 1, 'strike', 'yuri'),
(2, '30e93aa0-7c0c-4072-923e-643386d69527', 2, 'hart', 'yuri'),
(3, '30e93aa0-7c0c-4072-923e-643386d69527', 3, 'itlog', 'yuriha'),
(4, '30e93aa0-7c0c-4072-923e-643386d69527', 4, 'blood', 'yuriha'),
(5, '30e93aa0-7c0c-4072-923e-643386d69527', 5, 'byron', 'yuriha'),
(6, '299c35d9-e028-4496-88cf-ed284748bc5f', 1, 'hart', 'yuriha'),
(7, '299c35d9-e028-4496-88cf-ed284748bc5f', 2, 'itlog', 'yuriha'),
(8, '299c35d9-e028-4496-88cf-ed284748bc5f', 3, 'byron', 'yuriha'),
(9, '736b68e5-6f9e-44fb-ae66-f7db6709c504', 1, 'crane', 'yuri'),
(10, '736b68e5-6f9e-44fb-ae66-f7db6709c504', 2, 'blood', 'toomuch'),
(11, '736b68e5-6f9e-44fb-ae66-f7db6709c504', 3, 'hart', 'toomuch'),
(12, '736b68e5-6f9e-44fb-ae66-f7db6709c504', 4, 'itlog', 'toomuch'),
(13, '00b6302b-6c6c-459b-92af-eaa07be51ccf', 1, 'itlog', 'yuri'),
(14, '00b6302b-6c6c-459b-92af-eaa07be51ccf', 2, 'blood', 'yuri'),
(15, '00b6302b-6c6c-459b-92af-eaa07be51ccf', 3, 'crane', 'yuri'),
(16, 'e7dd87ca-e02c-484b-86a3-767a1c3a3b8d', 1, 'strike', 'yuriha'),
(17, 'e7dd87ca-e02c-484b-86a3-767a1c3a3b8d', 2, 'byron', 'yuriha'),
(18, 'e7dd87ca-e02c-484b-86a3-767a1c3a3b8d', 3, 'hart', 'yuriha'),
(19, 'bf32d312-7ae3-4018-a552-055f1ee9a39b', 1, 'strike', 'toomuch'),
(20, 'bf32d312-7ae3-4018-a552-055f1ee9a39b', 2, 'byron', 'toomuch'),
(21, 'bf32d312-7ae3-4018-a552-055f1ee9a39b', 3, 'blood', 'yuriha'),
(22, 'bf32d312-7ae3-4018-a552-055f1ee9a39b', 4, 'franz', 'toomuch'),
(23, '0d7ca943-92a9-4d01-89c2-d80bf3223fbe', 1, 'franz', 'toomuch'),
(24, '0d7ca943-92a9-4d01-89c2-d80bf3223fbe', 2, 'byron', 'toomuch'),
(25, '0d7ca943-92a9-4d01-89c2-d80bf3223fbe', 3, 'itlog', 'toomuch'),
(26, '1eecab5c-5916-4e07-b942-37f1728c186f', 1, 'hart', 'yuri'),
(27, '1eecab5c-5916-4e07-b942-37f1728c186f', 2, 'byron', 'yuriha'),
(28, '1eecab5c-5916-4e07-b942-37f1728c186f', 3, 'blood', 'yuri'),
(29, '1eecab5c-5916-4e07-b942-37f1728c186f', 4, 'crane', 'yuriha'),
(30, '1eecab5c-5916-4e07-b942-37f1728c186f', 5, 'franz', 'yuriha'),
(31, '165541a5-d4a5-43e0-978b-a8585735125e', 1, 'franz', 'toomuch'),
(32, '165541a5-d4a5-43e0-978b-a8585735125e', 2, 'strike', 'yuriha'),
(33, '165541a5-d4a5-43e0-978b-a8585735125e', 3, 'itlog', 'yuriha'),
(34, '165541a5-d4a5-43e0-978b-a8585735125e', 4, 'hart', 'toomuch'),
(35, '165541a5-d4a5-43e0-978b-a8585735125e', 5, 'blood', 'toomuch'),
(36, '3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 1, 'strike', 'yuriha'),
(37, '3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 2, 'hart', 'yuriha'),
(38, '3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 3, 'franz', 'yuri'),
(39, '3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 4, 'itlog', 'yuri'),
(40, '3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 5, 'crane', 'toomuch'),
(41, '3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 6, 'byron', 'toomuch'),
(42, '3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 7, 'blood', 'toomuch'),
(43, '19d8d4ac-52a4-416d-a581-8e3233f94a0b', 1, 'hart', 'toomuch'),
(44, '19d8d4ac-52a4-416d-a581-8e3233f94a0b', 2, 'strike', 'toomuch'),
(45, '19d8d4ac-52a4-416d-a581-8e3233f94a0b', 3, 'itlog', 'toomuch'),
(46, 'ee5fc475-1983-431c-9166-fb5e8c952790', 1, 'byron', 'yuri'),
(47, 'ee5fc475-1983-431c-9166-fb5e8c952790', 2, 'hart', 'yuri'),
(48, 'ee5fc475-1983-431c-9166-fb5e8c952790', 3, 'itlog', 'yuri'),
(49, '935a7a1b-a55c-41be-aca0-28efbc09f0dc', 1, 'hart', 'toomuch'),
(50, '935a7a1b-a55c-41be-aca0-28efbc09f0dc', 2, 'crane', 'toomuch'),
(51, '935a7a1b-a55c-41be-aca0-28efbc09f0dc', 3, 'strike', 'toomuch'),
(52, '7d090094-a7bf-4950-9f1d-d710f82e943e', 1, 'franz', 'yuriha'),
(53, '7d090094-a7bf-4950-9f1d-d710f82e943e', 2, 'strike', 'yuriha'),
(54, '7d090094-a7bf-4950-9f1d-d710f82e943e', 3, 'blood', 'yuriha'),
(55, 'ffe448fe-28ff-49e0-abb6-18e28168ffbd', 1, 'blood', 'yura'),
(56, 'ffe448fe-28ff-49e0-abb6-18e28168ffbd', 2, 'strike', 'yuri'),
(57, 'ffe448fe-28ff-49e0-abb6-18e28168ffbd', 3, 'hart', 'yuri'),
(58, 'ffe448fe-28ff-49e0-abb6-18e28168ffbd', 4, 'itlog', 'yuri'),
(59, 'b88bacfa-f6f6-4ca9-bd24-71dd2d58581d', 1, 'crane', 'yuriha'),
(60, 'b88bacfa-f6f6-4ca9-bd24-71dd2d58581d', 2, 'byron', 'yuri'),
(61, 'b88bacfa-f6f6-4ca9-bd24-71dd2d58581d', 3, 'blood', 'yuriha'),
(62, 'b88bacfa-f6f6-4ca9-bd24-71dd2d58581d', 4, 'strike', 'yuriha'),
(63, '3e60f930-5222-4494-8142-23d9fe4aee73', 1, 'blood', 'yuriha'),
(64, '3e60f930-5222-4494-8142-23d9fe4aee73', 2, 'strike', 'yuri'),
(65, '3e60f930-5222-4494-8142-23d9fe4aee73', 3, 'itlog', ''),
(66, '3e60f930-5222-4494-8142-23d9fe4aee73', 4, 'franz', 'yuri'),
(67, '3e60f930-5222-4494-8142-23d9fe4aee73', 5, 'byron', 'yuriha'),
(68, '3e60f930-5222-4494-8142-23d9fe4aee73', 6, 'hart', 'yuriha'),
(69, '92a33d73-3a47-472e-a916-100a051cd0da', 1, 'franz', 'yuri'),
(70, '92a33d73-3a47-472e-a916-100a051cd0da', 2, 'itlog', 'yuri'),
(71, '92a33d73-3a47-472e-a916-100a051cd0da', 3, 'blood', 'yuriha'),
(72, '92a33d73-3a47-472e-a916-100a051cd0da', 4, 'crane', 'yuri'),
(73, '5c507e58-860c-4c80-8463-9956ed631fb5', 1, 'blood', 'yuri'),
(74, '5c507e58-860c-4c80-8463-9956ed631fb5', 2, 'byron', 'yuriha'),
(75, '5c507e58-860c-4c80-8463-9956ed631fb5', 3, 'strike', 'yuriha'),
(76, '5c507e58-860c-4c80-8463-9956ed631fb5', 4, 'franz', 'yuri'),
(77, '5c507e58-860c-4c80-8463-9956ed631fb5', 5, 'crane', 'yuri'),
(78, '2bd3c6df-0d00-4bc8-9fbf-5b98dae47298', 1, 'franz', 'yuri'),
(79, '2bd3c6df-0d00-4bc8-9fbf-5b98dae47298', 2, 'blood', 'yuri'),
(80, '2bd3c6df-0d00-4bc8-9fbf-5b98dae47298', 3, 'strike', 'yuri'),
(81, 'aa6a4731-9471-4ffa-aa96-c3fe8300764d', 1, 'hart', 'toomuch'),
(82, 'aa6a4731-9471-4ffa-aa96-c3fe8300764d', 2, 'byron', 'toomuch'),
(83, 'aa6a4731-9471-4ffa-aa96-c3fe8300764d', 3, 'itlog', 'toomuch'),
(84, '7c49c16a-b851-4604-8cc2-37e6032de253', 1, 'byron', 'yuri'),
(85, '7c49c16a-b851-4604-8cc2-37e6032de253', 2, 'crane', 'yuri'),
(86, '7c49c16a-b851-4604-8cc2-37e6032de253', 3, 'hart', 'yuriha'),
(87, '7c49c16a-b851-4604-8cc2-37e6032de253', 4, 'itlog', 'yuri'),
(88, '5187fafd-6c4c-4116-a6f5-b999b7ebd62b', 1, 'blood', 'toomuch'),
(89, '5187fafd-6c4c-4116-a6f5-b999b7ebd62b', 2, 'hart', 'yuriha'),
(90, '5187fafd-6c4c-4116-a6f5-b999b7ebd62b', 3, 'strike', 'yuriha'),
(91, '5187fafd-6c4c-4116-a6f5-b999b7ebd62b', 4, 'byron', 'toomuch'),
(92, '5187fafd-6c4c-4116-a6f5-b999b7ebd62b', 5, 'crane', 'yuriha'),
(93, 'dd863b2d-cf90-41fe-b2a9-caf3ca102691', 1, 'crane', 'toomuch'),
(94, 'dd863b2d-cf90-41fe-b2a9-caf3ca102691', 2, 'hart', 'toomuch'),
(95, 'dd863b2d-cf90-41fe-b2a9-caf3ca102691', 3, 'itlog', 'toomuch'),
(96, '66ba666b-3574-4d0f-aacb-1ad5a848b302', 1, 'hart', 'toomuch'),
(97, '66ba666b-3574-4d0f-aacb-1ad5a848b302', 2, 'itlog', 'toomuch'),
(98, '66ba666b-3574-4d0f-aacb-1ad5a848b302', 3, 'strike', 'yuriha'),
(99, '66ba666b-3574-4d0f-aacb-1ad5a848b302', 4, 'byron', 'yuriha'),
(100, '66ba666b-3574-4d0f-aacb-1ad5a848b302', 5, 'franz', 'yuriha'),
(101, '8f8eab42-4b6c-4d1c-b197-f664abee4c2f', 1, 'blood', 'yuriha'),
(102, '8f8eab42-4b6c-4d1c-b197-f664abee4c2f', 2, 'strike', 'yuriha'),
(103, '8f8eab42-4b6c-4d1c-b197-f664abee4c2f', 3, 'franz', 'yuriha'),
(104, 'c530a61f-62bd-415c-af62-6a76f374f428', 1, 'franz', 'yuri'),
(105, 'c530a61f-62bd-415c-af62-6a76f374f428', 2, 'strike', 'yuri'),
(106, 'c530a61f-62bd-415c-af62-6a76f374f428', 3, 'blood', 'yuri'),
(107, '819bba4e-dbb5-46b4-b66d-6e99bae0fc2b', 0, 'byron', 'yuriha'),
(108, '819bba4e-dbb5-46b4-b66d-6e99bae0fc2b', 1, 'franz', 'yuriha'),
(109, '819bba4e-dbb5-46b4-b66d-6e99bae0fc2b', 2, 'hart', 'yuriha'),
(110, '1c7164f8-17c9-4f6e-8d3e-185fd69b4c80', 0, 'itlog', 'yuri'),
(111, '1c7164f8-17c9-4f6e-8d3e-185fd69b4c80', 1, 'blood', 'yuri'),
(112, '1c7164f8-17c9-4f6e-8d3e-185fd69b4c80', 2, 'hart', 'yuri'),
(113, 'da03b263-2dd1-4dec-879e-530522eea90a', 0, 'hart', 'yuri'),
(114, 'da03b263-2dd1-4dec-879e-530522eea90a', 1, 'itlog', 'yuri'),
(115, 'da03b263-2dd1-4dec-879e-530522eea90a', 2, 'byron', 'yuri'),
(116, '7b76c178-dffe-484f-9f63-257fa03a88cc', 0, 'byron', 'yuri'),
(117, '7b76c178-dffe-484f-9f63-257fa03a88cc', 1, 'franz', 'yuri'),
(118, '7b76c178-dffe-484f-9f63-257fa03a88cc', 2, 'strike', 'yuriha'),
(119, '7b76c178-dffe-484f-9f63-257fa03a88cc', 3, 'crane', 'yuri'),
(120, 'f3cf3efe-cb9a-4ba6-a762-af0274bcaecc', 0, 'hart', 'yuriha'),
(121, 'f3cf3efe-cb9a-4ba6-a762-af0274bcaecc', 1, 'crane', 'yuri'),
(122, 'f3cf3efe-cb9a-4ba6-a762-af0274bcaecc', 2, 'blood', 'yuriha'),
(123, 'f3cf3efe-cb9a-4ba6-a762-af0274bcaecc', 3, 'franz', 'yuriha'),
(124, 'c1d0fb9b-86bf-4ecc-839d-657114192417', 0, 'franz', 'yuri'),
(125, 'c1d0fb9b-86bf-4ecc-839d-657114192417', 1, 'crane', 'yuri'),
(126, 'c1d0fb9b-86bf-4ecc-839d-657114192417', 2, 'hart', 'yuri'),
(127, '70931c70-803a-4b83-87ee-dd473801e20a', 0, 'blood', 'yuri'),
(128, '70931c70-803a-4b83-87ee-dd473801e20a', 1, 'itlog', 'yuri'),
(129, '70931c70-803a-4b83-87ee-dd473801e20a', 2, 'crane', 'yuri'),
(130, '3dec840b-fbc8-4568-b0b8-0ad9818f6645', 0, 'blood', 'yuri'),
(131, '3dec840b-fbc8-4568-b0b8-0ad9818f6645', 1, 'hart', 'crane'),
(132, '3dec840b-fbc8-4568-b0b8-0ad9818f6645', 2, 'franz', 'crane'),
(133, '3dec840b-fbc8-4568-b0b8-0ad9818f6645', 3, 'crane', 'crane'),
(134, '00a86bb1-0723-44a7-9419-2705d1f1c683', 0, 'strike', 'toomuch'),
(135, '00a86bb1-0723-44a7-9419-2705d1f1c683', 1, 'hart', 'toomuch'),
(136, '00a86bb1-0723-44a7-9419-2705d1f1c683', 2, 'blood', 'toomuch'),
(137, 'a5cf04d0-32ea-4104-b23e-c83302d7eeaf', 0, 'crane', 'crane'),
(138, 'a5cf04d0-32ea-4104-b23e-c83302d7eeaf', 1, 'byron', 'crane'),
(139, 'a5cf04d0-32ea-4104-b23e-c83302d7eeaf', 2, 'franz', 'crane'),
(140, 'd43ee0d5-372d-4575-a4c5-859b861144d7', 0, 'strike', 'dontmake'),
(141, 'd43ee0d5-372d-4575-a4c5-859b861144d7', 1, 'blood', 'dontmake'),
(142, 'd43ee0d5-372d-4575-a4c5-859b861144d7', 2, 'itlog', 'dontmake'),
(143, '08723048-ba2b-45ee-987b-3dac974b7d29', 0, 'byron', 'yuri'),
(144, '08723048-ba2b-45ee-987b-3dac974b7d29', 1, 'hart', 'yuri'),
(145, '08723048-ba2b-45ee-987b-3dac974b7d29', 2, 'itlog', 'crane'),
(146, '08723048-ba2b-45ee-987b-3dac974b7d29', 3, 'franz', 'yuri'),
(147, 'ae241490-ced9-461a-b18e-4b32759a8076', 0, 'hart', 'toomuch'),
(148, 'ae241490-ced9-461a-b18e-4b32759a8076', 1, 'blood', 'toomuch'),
(149, 'ae241490-ced9-461a-b18e-4b32759a8076', 2, 'strike', 'toomuch'),
(150, '4ea0c587-7b69-4d27-94b0-d0f951b49cf5', 0, 'strike', 'yuriha'),
(151, '4ea0c587-7b69-4d27-94b0-d0f951b49cf5', 1, 'crane', 'yuriha'),
(152, '4ea0c587-7b69-4d27-94b0-d0f951b49cf5', 2, 'hart', 'yuriha'),
(153, '755c69b3-308a-454b-aea2-115f1766c1d8', 0, 'itlog', 'crane'),
(154, '755c69b3-308a-454b-aea2-115f1766c1d8', 1, 'hart', 'crane'),
(155, '755c69b3-308a-454b-aea2-115f1766c1d8', 2, 'crane', 'yuri'),
(156, '755c69b3-308a-454b-aea2-115f1766c1d8', 3, 'franz', 'crane'),
(157, '15da0168-2e98-4bea-989f-a838c0101871', 0, 'strike', 'yuri'),
(158, '15da0168-2e98-4bea-989f-a838c0101871', 1, 'byron', 'yuri'),
(159, '15da0168-2e98-4bea-989f-a838c0101871', 2, 'franz', 'toomuch'),
(160, '15da0168-2e98-4bea-989f-a838c0101871', 3, 'crane', 'toomuch'),
(161, '15da0168-2e98-4bea-989f-a838c0101871', 4, 'blood', 'toomuch'),
(162, 'd6b1943d-4cf4-409b-8701-3a84d5aebf99', 0, 'blood', 'toomuch'),
(163, 'd6b1943d-4cf4-409b-8701-3a84d5aebf99', 1, 'crane', 'toomuch'),
(164, 'd6b1943d-4cf4-409b-8701-3a84d5aebf99', 2, 'franz', 'yuri'),
(165, 'd6b1943d-4cf4-409b-8701-3a84d5aebf99', 3, 'itlog', 'yuri'),
(166, 'd6b1943d-4cf4-409b-8701-3a84d5aebf99', 4, 'hart', 'yuri'),
(167, 'd0ce578e-6bb1-48dd-acf3-47feabc2c541', 0, 'strike', 'yuriha'),
(168, 'd0ce578e-6bb1-48dd-acf3-47feabc2c541', 1, 'franz', 'yuriha'),
(169, 'd0ce578e-6bb1-48dd-acf3-47feabc2c541', 2, 'byron', 'yuriha'),
(170, '26994501-75a2-40b9-a256-f24c59bceffb', 0, 'franz', 'yuri'),
(171, '26994501-75a2-40b9-a256-f24c59bceffb', 1, 'blood', 'crane'),
(172, '26994501-75a2-40b9-a256-f24c59bceffb', 2, 'itlog', 'yuri'),
(173, '26994501-75a2-40b9-a256-f24c59bceffb', 3, 'crane', 'crane'),
(174, '26994501-75a2-40b9-a256-f24c59bceffb', 4, 'hart', 'crane'),
(175, '65544f8a-d001-4dc8-87ab-0d6aee5616af', 0, 'strike', 'yuri'),
(176, '65544f8a-d001-4dc8-87ab-0d6aee5616af', 1, 'itlog', 'yuri'),
(177, '65544f8a-d001-4dc8-87ab-0d6aee5616af', 2, 'byron', 'crane'),
(178, '65544f8a-d001-4dc8-87ab-0d6aee5616af', 3, 'hart', 'crane'),
(179, '65544f8a-d001-4dc8-87ab-0d6aee5616af', 4, 'crane', 'crane'),
(180, 'e8d11aff-d9a6-419b-b6c1-d2aacc90a010', 0, 'strike', 'yuri'),
(181, 'e8d11aff-d9a6-419b-b6c1-d2aacc90a010', 1, 'byron', 'yuri'),
(182, 'e8d11aff-d9a6-419b-b6c1-d2aacc90a010', 2, 'crane', 'yuri'),
(183, '02b0df08-fee6-47ab-8b19-cb6a933dc501', 0, 'franz', 'yuri'),
(184, '02b0df08-fee6-47ab-8b19-cb6a933dc501', 1, 'strike', 'yuri'),
(185, '02b0df08-fee6-47ab-8b19-cb6a933dc501', 2, 'hart', 'onemoredoor'),
(186, '02b0df08-fee6-47ab-8b19-cb6a933dc501', 3, 'blood', 'onemoredoor'),
(187, '02b0df08-fee6-47ab-8b19-cb6a933dc501', 4, 'itlog', 'onemoredoor'),
(188, '5287e9db-0e59-40f4-900e-89ef78342bbb', 0, 'byron', 'onemoredoor'),
(189, '5287e9db-0e59-40f4-900e-89ef78342bbb', 1, 'hart', 'onemoredoor'),
(190, '5287e9db-0e59-40f4-900e-89ef78342bbb', 2, 'itlog', 'onemoredoor'),
(191, '8eda820f-c20d-4a53-bf5b-689eded4b542', 0, 'strike', 'yuri'),
(192, '8eda820f-c20d-4a53-bf5b-689eded4b542', 1, 'byron', 'yuri'),
(193, '8eda820f-c20d-4a53-bf5b-689eded4b542', 2, 'blood', 'yuri'),
(194, '97058e14-c670-4639-9896-cf50d8c2c614', 0, 'blood', 'yuri'),
(195, 'c5dc63e9-14ec-4965-99e6-2123950bfc4b', 0, 'crane', 'yuri'),
(196, 'c5dc63e9-14ec-4965-99e6-2123950bfc4b', 1, 'itlog', 'yuri'),
(197, 'c5dc63e9-14ec-4965-99e6-2123950bfc4b', 2, 'strike', 'yuri'),
(198, '063099f6-425e-42e8-9d4c-3aaa05e35ac0', 0, 'byron', 'yuri'),
(199, '063099f6-425e-42e8-9d4c-3aaa05e35ac0', 1, 'franz', 'yuri'),
(200, '063099f6-425e-42e8-9d4c-3aaa05e35ac0', 2, 'blood', 'yuri'),
(201, 'd4b22875-dc49-4fff-b336-589ba82adaaf', 0, 'hart', 'crane'),
(202, 'd4b22875-dc49-4fff-b336-589ba82adaaf', 1, 'franz', 'yuri'),
(203, 'd4b22875-dc49-4fff-b336-589ba82adaaf', 2, 'crane', 'yuri'),
(204, 'd4b22875-dc49-4fff-b336-589ba82adaaf', 3, 'itlog', 'yuri'),
(205, 'a3b6a5ab-381a-4e00-8039-3333bc84c88b', 0, 'itlog', ''),
(206, 'a3b6a5ab-381a-4e00-8039-3333bc84c88b', 1, 'byron', 'yuri'),
(207, 'a3b6a5ab-381a-4e00-8039-3333bc84c88b', 2, 'strike', 'yuri'),
(208, 'a3b6a5ab-381a-4e00-8039-3333bc84c88b', 3, 'hart', 'yuri');

-- --------------------------------------------------------

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
CREATE TABLE IF NOT EXISTS `settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `waiting_time_seconds` int DEFAULT '10',
  `round_time_seconds` int DEFAULT '30',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `settings`
--

INSERT INTO `settings` (`id`, `waiting_time_seconds`, `round_time_seconds`) VALUES
(1, 15, 35);

-- --------------------------------------------------------

--
-- Table structure for table `sp_games`
--

DROP TABLE IF EXISTS `sp_games`;
CREATE TABLE IF NOT EXISTS `sp_games` (
  `game_id` varchar(36) NOT NULL,
  `total_rounds` int NOT NULL,
  `overall_winner` varchar(50) DEFAULT NULL,
  `game_end_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sp_game_players`
--

DROP TABLE IF EXISTS `sp_game_players`;
CREATE TABLE IF NOT EXISTS `sp_game_players` (
  `game_id` varchar(36) NOT NULL,
  `player_name` varchar(50) NOT NULL,
  PRIMARY KEY (`game_id`,`player_name`),
  KEY `idx_sp_game_players_game_id` (`game_id`),
  CONSTRAINT `fk_sp_game_players_game_id` FOREIGN KEY (`game_id`) REFERENCES `sp_games` (`game_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sp_rounds`
--

DROP TABLE IF EXISTS `sp_rounds`;
CREATE TABLE IF NOT EXISTS `sp_rounds` (
  `round_id` int NOT NULL AUTO_INCREMENT,
  `game_id` varchar(36) NOT NULL,
  `round_number` int NOT NULL,
  `word` varchar(100) NOT NULL,
  `winner` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`round_id`),
  KEY `idx_sp_rounds_game_id` (`game_id`),
  CONSTRAINT `fk_sp_rounds_game_id` FOREIGN KEY (`game_id`) REFERENCES `sp_games` (`game_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `game_players`
--
ALTER TABLE `game_players`
  ADD CONSTRAINT `game_players_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE;

--
-- Constraints for table `rounds`
--
ALTER TABLE `rounds`
  ADD CONSTRAINT `rounds_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
