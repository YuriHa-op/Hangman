-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: May 23, 2025 at 06:28 PM
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
) ENGINE=MyISAM AUTO_INCREMENT=161 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
(63, 0, 'ranked', 0, '2025-05-01 03:07:10'),
(64, 2, 'hart', 1, '2025-05-11 21:44:39'),
(65, 0, 'hart', 1, '2025-05-11 21:44:42'),
(66, 2, 'byron', 1, '2025-05-11 21:44:49'),
(67, 2, 'crane', 1, '2025-05-11 21:45:06'),
(68, 0, 'crane', 1, '2025-05-11 21:45:11'),
(69, 0, 'crane', 1, '2025-05-11 22:29:17'),
(70, 0, 'strike', 1, '2025-05-11 22:29:27'),
(71, 2, 'strike', 1, '2025-05-11 22:29:30'),
(72, 0, 'strike', 1, '2025-05-11 22:29:37'),
(73, 2, 'strike', 1, '2025-05-11 22:29:41'),
(74, 2, 'byron', 1, '2025-05-11 23:31:11'),
(75, 0, 'byron', 1, '2025-05-11 23:31:21'),
(76, 2, 'franz', 1, '2025-05-11 23:31:49'),
(77, 0, 'hart', 1, '2025-05-11 23:36:24'),
(78, 2, 'hart', 1, '2025-05-11 23:36:32'),
(79, 0, 'byron', 1, '2025-05-11 23:36:58'),
(80, 0, 'franz', 1, '2025-05-11 23:41:26'),
(81, 0, 'crane', 1, '2025-05-11 23:42:12'),
(82, 2, 'crane', 1, '2025-05-11 23:54:57'),
(83, 2, 'blood', 1, '2025-05-11 23:55:09'),
(84, 0, 'franz', 1, '2025-05-11 23:58:11'),
(85, 0, 'hart', 1, '2025-05-11 23:58:14'),
(86, 0, 'crane', 1, '2025-05-11 23:58:19'),
(87, 2, 'hart', 1, '2025-05-11 23:58:29'),
(88, 2, 'crane', 1, '2025-05-11 23:58:39'),
(89, 0, 'byron', 1, '2025-05-12 00:37:58'),
(90, 2, 'byron', 1, '2025-05-12 00:38:21'),
(91, 2, 'byron', 1, '2025-05-12 00:42:03'),
(92, 0, 'byron', 1, '2025-05-12 00:42:13'),
(93, 2, 'franz', 1, '2025-05-12 00:46:14'),
(94, 2, 'crane', 1, '2025-05-12 00:49:04'),
(95, 2, 'byron', 1, '2025-05-12 00:49:17'),
(96, 2, 'franz', 1, '2025-05-12 00:49:21'),
(97, 0, 'byron', 1, '2025-05-12 00:49:32'),
(98, 0, 'franz', 1, '2025-05-12 00:49:43'),
(99, 0, 'blood', 1, '2025-05-12 00:49:52'),
(100, 0, 'crane', 1, '2025-05-12 00:54:09'),
(101, 0, 'blood', 1, '2025-05-12 00:54:17'),
(102, 2, 'blood', 1, '2025-05-12 00:54:21'),
(103, 0, 'strike', 1, '2025-05-12 00:54:29'),
(104, 0, 'hart', 1, '2025-05-12 01:17:05'),
(105, 0, 'byron', 1, '2025-05-12 01:17:11'),
(106, 0, 'franz', 1, '2025-05-12 01:17:16'),
(107, 0, 'blood', 1, '2025-05-12 01:24:12'),
(108, 0, 'crane', 1, '2025-05-12 01:24:16'),
(109, 0, 'franz', 1, '2025-05-12 01:24:21'),
(110, 2, 'hart', 1, '2025-05-12 01:32:06'),
(111, 2, 'franz', 1, '2025-05-12 01:32:12'),
(112, 2, 'blood', 1, '2025-05-12 01:32:17'),
(113, 0, 'franz', 1, '2025-05-12 01:38:19'),
(114, 0, 'byron', 1, '2025-05-12 01:38:24'),
(115, 0, 'hart', 1, '2025-05-12 01:38:27'),
(116, 2, 'byron', 1, '2025-05-12 01:50:40'),
(117, 0, 'byron', 1, '2025-05-12 01:50:46'),
(118, 2, 'strike', 1, '2025-05-12 01:50:51'),
(119, 0, 'strike', 1, '2025-05-12 01:50:57'),
(120, 2, 'hart', 1, '2025-05-12 01:51:02'),
(121, 0, 'crane', 1, '2025-05-12 02:04:30'),
(122, 2, 'crane', 1, '2025-05-12 02:04:45'),
(123, 2, 'franz', 1, '2025-05-12 02:04:56'),
(124, 0, 'franz', 1, '2025-05-12 02:05:06'),
(125, 0, 'blood', 1, '2025-05-12 02:05:23'),
(126, 0, 'franz', 1, '2025-05-12 02:17:00'),
(127, 2, 'franz', 1, '2025-05-12 02:17:10'),
(128, 0, 'strike', 1, '2025-05-12 02:17:20'),
(129, 2, 'strike', 1, '2025-05-12 02:17:29'),
(130, 0, 'blood', 1, '2025-05-12 02:17:46'),
(131, 2, 'strike', 1, '2025-05-12 02:20:10'),
(132, 0, 'strike', 1, '2025-05-12 02:20:17'),
(133, 0, 'hart', 1, '2025-05-12 02:20:24'),
(134, 2, 'hart', 1, '2025-05-12 02:20:27'),
(135, 2, 'byron', 1, '2025-05-12 02:20:48'),
(136, 0, 'byron', 1, '2025-05-12 04:59:05'),
(137, 0, 'crane', 1, '2025-05-12 04:59:15'),
(138, 0, 'strike', 1, '2025-05-12 04:59:21'),
(139, 2, 'blood', 1, '2025-05-12 05:19:51'),
(140, 0, 'blood', 1, '2025-05-12 05:19:55'),
(141, 2, 'byron', 1, '2025-05-12 05:20:04'),
(142, 2, 'strike', 1, '2025-05-12 05:20:08'),
(143, 0, 'blood', 1, '2025-05-12 05:24:54'),
(144, 0, 'franz', 1, '2025-05-12 05:25:03'),
(145, 0, 'strike', 1, '2025-05-12 05:25:07'),
(146, 2, 'franz', 1, '2025-05-12 05:28:13'),
(147, 2, 'byron', 1, '2025-05-12 05:28:21'),
(148, 2, 'strike', 1, '2025-05-12 05:28:24'),
(149, 0, 'crane', 1, '2025-05-12 05:34:32'),
(150, 0, 'franz', 1, '2025-05-12 05:34:53'),
(151, 0, 'blood', 1, '2025-05-12 05:35:06'),
(152, 2, 'byron', 1, '2025-05-12 05:37:35'),
(153, 2, 'franz', 1, '2025-05-12 05:37:41'),
(154, 2, 'hart', 1, '2025-05-12 05:37:55'),
(155, 2, 'strike', 1, '2025-05-12 05:40:16'),
(156, 2, 'byron', 1, '2025-05-12 05:40:26'),
(157, 2, 'franz', 1, '2025-05-12 05:40:33'),
(158, 0, 'crane', 1, '2025-05-12 06:07:35'),
(159, 0, 'blood', 1, '2025-05-12 06:07:45'),
(160, 0, 'byron', 1, '2025-05-12 06:07:54');

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
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `players`
--

INSERT INTO `players` (`id`, `username`, `password`, `wins`, `currently_logged_in`, `role`) VALUES
(0, 'yuri', '1111', 32, 1, 'admin'),
(2, 'Yuriha', '2222', 31, 1, 'player'),
(6, 'toomuch', '1111', 3, 1, 'player'),
(7, 'Idontwanna', '1111', 3, 0, 'player'),
(8, 'dontmake', '1111', 44, 0, 'player'),
(9, 'meclose', '', 40, 0, 'player'),
(10, 'onemoredoor', '1111', 35, 0, 'player'),
(12, 'crane', '1111', 0, 0, 'player');

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
(1, 10, 40);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- --------------------------------------------------------
-- Table structure for table `games`
--
DROP TABLE IF EXISTS `games`;
CREATE TABLE IF NOT EXISTS `games` (
  `game_id` varchar(36) NOT NULL,
  `total_rounds` int NOT NULL,
  `overall_winner` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
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
  KEY `game_id` (`game_id`),
  CONSTRAINT `rounds_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `game_players`
--
DROP TABLE IF EXISTS `game_players`;
CREATE TABLE IF NOT EXISTS `game_players` (
  `game_id` varchar(36) NOT NULL,
  `player_name` varchar(50) NOT NULL,
  PRIMARY KEY (`game_id`, `player_name`),
  KEY `game_id` (`game_id`),
  CONSTRAINT `game_players_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
