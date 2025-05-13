-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 30, 2025 at 07:09 PM
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
) ENGINE=MyISAM AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `game_results`
--

INSERT INTO `game_results` (`id`, `player_id`, `word_guessed`, `win_status`, `game_time`) VALUES
(1, 1, 'carping', 1, '2025-04-29 23:36:21'),
(2, 1, 'umpires', 1, '2025-04-29 23:41:37'),
(3, 1, 'blasts', 0, '2025-04-30 00:15:29'),
(4, 1, 'obfuscating', 0, '2025-04-30 00:21:25'),
(5, 1, 'thrown', 0, '2025-04-30 00:23:46'),
(6, 1, 'wildest', 0, '2025-04-30 00:33:20'),
(7, 1, 'vindicate', 0, '2025-04-30 00:35:21'),
(8, 1, 'unscrewing', 0, '2025-04-30 00:46:32'),
(9, 1, 'bandied', 0, '2025-04-30 00:47:53'),
(10, 1, 'mailings', 0, '2025-04-30 00:58:12'),
(11, 1, 'skunks', 0, '2025-04-30 01:01:55'),
(12, 1, 'global', 0, '2025-04-30 01:06:38'),
(13, 1, 'discovered', 0, '2025-04-30 01:12:42'),
(14, 1, 'slaughterhouse', 0, '2025-04-30 01:13:53'),
(15, 1, 'jocosely', 0, '2025-04-30 01:17:23'),
(16, 1, 'squads', 0, '2025-04-30 01:18:34'),
(17, 1, 'carfare', 0, '2025-04-30 01:20:33'),
(18, 1, 'fatalism', 0, '2025-04-30 01:21:37'),
(19, 1, 'majestically', 0, '2025-04-30 01:22:25'),
(20, 1, 'spacious', 0, '2025-04-30 01:23:28'),
(21, 2, 'localizes', 0, '2025-04-30 01:24:05'),
(22, 1, 'underage', 0, '2025-04-30 01:25:21'),
(23, 1, 'perforation', 0, '2025-04-30 01:25:56'),
(24, 1, 'smilingly', 0, '2025-04-30 01:26:11'),
(25, 1, 'exhumes', 0, '2025-04-30 01:28:13'),
(26, 1, 'deciphered', 0, '2025-04-30 02:49:01'),
(27, 1, 'rehearses', 0, '2025-04-30 02:56:16'),
(28, 1, 'stillbirth', 0, '2025-04-30 04:20:32'),
(29, 1, 'lionisation', 0, '2025-04-30 04:22:34'),
(30, 1, 'rogering', 0, '2025-04-30 04:27:08'),
(31, 1, 'backslid', 0, '2025-04-30 04:27:40'),
(32, 1, 'pussies', 0, '2025-04-30 04:27:56'),
(33, 1, 'illustrating', 0, '2025-04-30 04:28:13'),
(34, 1, 'achievers', 0, '2025-04-30 04:31:47'),
(35, 1, 'furloughing', 0, '2025-04-30 04:33:38'),
(36, 1, 'crane', 1, '2025-04-30 04:34:34'),
(37, 1, 'crane', 1, '2025-04-30 04:44:01'),
(38, 1, 'crane', 0, '2025-04-30 04:44:28'),
(39, 1, 'crane', 1, '2025-04-30 04:47:28'),
(40, 2, 'crane', 1, '2025-04-30 04:51:09'),
(41, 2, 'crane', 0, '2025-04-30 04:51:29'),
(42, 1, 'crane', 1, '2025-04-30 05:01:59'),
(43, 1, 'crane', 1, '2025-04-30 05:07:22'),
(44, 1, 'crane', 0, '2025-04-30 05:07:30'),
(45, 1, 'crane', 0, '2025-04-30 05:07:46'),
(46, 1, 'crane', 0, '2025-04-30 05:10:05'),
(47, 1, 'crane', 0, '2025-04-30 05:10:30'),
(48, 1, 'crane', 0, '2025-04-30 05:13:16'),
(49, 1, 'crane', 0, '2025-04-30 05:16:09'),
(50, 2, 'crane', 0, '2025-04-30 05:21:40'),
(51, 2, 'crane', 0, '2025-04-30 05:23:18'),
(52, 2, 'crane', 0, '2025-04-30 05:25:22'),
(53, 2, 'crane', 1, '2025-04-30 05:26:22'),
(54, 2, 'crane', 0, '2025-04-30 05:27:33'),
(55, 2, 'crane', 1, '2025-04-30 05:27:55'),
(56, 2, 'crane', 0, '2025-04-30 05:30:39'),
(57, 1, 'counsels', 0, '2025-04-30 18:55:35'),
(58, 6, 'culottes', 0, '2025-05-01 00:04:59'),
(59, 5, 'paramountcy', 0, '2025-05-01 01:11:18'),
(60, 5, 'tinker', 0, '2025-05-01 01:21:54'),
(61, 0, 'privies', 0, '2025-05-01 01:37:22'),
(62, 0, 'detoxifies', 0, '2025-05-01 02:30:17'),
(63, 0, 'ranked', 0, '2025-05-01 03:07:10');

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
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `players`
--

INSERT INTO `players` (`id`, `username`, `password`, `wins`, `currently_logged_in`, `role`) VALUES
(0, 'yuri', '1111', 3, 1, 'admin'),
(2, 'Yuriha', '2222', 69, 1, 'player'),
(6, 'toomuch', '1111', 2, 0, 'player'),
(7, 'Idontwanna', '1111', 10, 1, 'player'),
(8, 'dontmake', '1111', 44, 1, 'player'),
(9, 'meclose', '', 40, 0, 'player'),
(10, 'onemoredoor', '1111', 35, 0, 'player');

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
(1, 10, 30);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
