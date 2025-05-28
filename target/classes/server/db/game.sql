-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: May 26, 2025 at 10:44 PM
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
  `game_end_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `games`
--

INSERT INTO `games` (`game_id`, `total_rounds`, `overall_winner`) VALUES
('00b6302b-6c6c-459b-92af-eaa07be51ccf', 3, 'yuri'),
('0d7ca943-92a9-4d01-89c2-d80bf3223fbe', 3, 'toomuch'),
('165541a5-d4a5-43e0-978b-a8585735125e', 5, 'toomuch'),
('19d8d4ac-52a4-416d-a581-8e3233f94a0b', 3, 'toomuch'),
('1eecab5c-5916-4e07-b942-37f1728c186f', 5, 'yuriha'),
('299c35d9-e028-4496-88cf-ed284748bc5f', 3, 'yuriha'),
('2bd3c6df-0d00-4bc8-9fbf-5b98dae47298', 3, 'yuri'),
('30e93aa0-7c0c-4072-923e-643386d69527', 5, 'yuriha'),
('3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 7, 'toomuch'),
('3e60f930-5222-4494-8142-23d9fe4aee73', 6, 'yuriha'),
('5187fafd-6c4c-4116-a6f5-b999b7ebd62b', 5, 'yuriha'),
('5c507e58-860c-4c80-8463-9956ed631fb5', 5, 'yuri'),
('66ba666b-3574-4d0f-aacb-1ad5a848b302', 5, 'yuriha'),
('736b68e5-6f9e-44fb-ae66-f7db6709c504', 4, 'toomuch'),
('7c49c16a-b851-4604-8cc2-37e6032de253', 4, 'yuri'),
('7d090094-a7bf-4950-9f1d-d710f82e943e', 3, 'yuriha'),
('819bba4e-dbb5-46b4-b66d-6e99bae0fc2b', 2, 'yuriha'),
('8f8eab42-4b6c-4d1c-b197-f664abee4c2f', 3, 'yuriha'),
('92a33d73-3a47-472e-a916-100a051cd0da', 4, 'yuri'),
('935a7a1b-a55c-41be-aca0-28efbc09f0dc', 3, 'toomuch'),
('aa6a4731-9471-4ffa-aa96-c3fe8300764d', 3, 'toomuch'),
('b88bacfa-f6f6-4ca9-bd24-71dd2d58581d', 4, 'yuriha'),
('bf32d312-7ae3-4018-a552-055f1ee9a39b', 4, 'toomuch'),
('c530a61f-62bd-415c-af62-6a76f374f428', 3, 'yuri'),
('dd863b2d-cf90-41fe-b2a9-caf3ca102691', 3, 'toomuch'),
('e7dd87ca-e02c-484b-86a3-767a1c3a3b8d', 3, 'yuriha'),
('ee5fc475-1983-431c-9166-fb5e8c952790', 3, 'yuri'),
('ffe448fe-28ff-49e0-abb6-18e28168ffbd', 4, 'yuri');

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
('00b6302b-6c6c-459b-92af-eaa07be51ccf', 'toomuch'),
('00b6302b-6c6c-459b-92af-eaa07be51ccf', 'yuri'),
('00b6302b-6c6c-459b-92af-eaa07be51ccf', 'yuriha'),
('0d7ca943-92a9-4d01-89c2-d80bf3223fbe', 'toomuch'),
('0d7ca943-92a9-4d01-89c2-d80bf3223fbe', 'yuri'),
('0d7ca943-92a9-4d01-89c2-d80bf3223fbe', 'yuriha'),
('165541a5-d4a5-43e0-978b-a8585735125e', 'toomuch'),
('165541a5-d4a5-43e0-978b-a8585735125e', 'yuri'),
('165541a5-d4a5-43e0-978b-a8585735125e', 'yuriha'),
('19d8d4ac-52a4-416d-a581-8e3233f94a0b', 'toomuch'),
('19d8d4ac-52a4-416d-a581-8e3233f94a0b', 'yuri'),
('19d8d4ac-52a4-416d-a581-8e3233f94a0b', 'yuriha'),
('1eecab5c-5916-4e07-b942-37f1728c186f', 'toomuch'),
('1eecab5c-5916-4e07-b942-37f1728c186f', 'yuri'),
('1eecab5c-5916-4e07-b942-37f1728c186f', 'yuriha'),
('299c35d9-e028-4496-88cf-ed284748bc5f', 'toomuch'),
('299c35d9-e028-4496-88cf-ed284748bc5f', 'yuri'),
('299c35d9-e028-4496-88cf-ed284748bc5f', 'yuriha'),
('2bd3c6df-0d00-4bc8-9fbf-5b98dae47298', 'yuri'),
('2bd3c6df-0d00-4bc8-9fbf-5b98dae47298', 'yuriha'),
('30e93aa0-7c0c-4072-923e-643386d69527', 'toomuch'),
('30e93aa0-7c0c-4072-923e-643386d69527', 'yuri'),
('30e93aa0-7c0c-4072-923e-643386d69527', 'yuriha'),
('3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 'toomuch'),
('3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 'yuri'),
('3a931cfa-c9c3-4a98-aad2-2d7778f1e61b', 'yuriha'),
('3e60f930-5222-4494-8142-23d9fe4aee73', 'yuri'),
('3e60f930-5222-4494-8142-23d9fe4aee73', 'yuriha'),
('5187fafd-6c4c-4116-a6f5-b999b7ebd62b', 'toomuch'),
('5187fafd-6c4c-4116-a6f5-b999b7ebd62b', 'yuriha'),
('5c507e58-860c-4c80-8463-9956ed631fb5', 'yuri'),
('5c507e58-860c-4c80-8463-9956ed631fb5', 'yuriha'),
('66ba666b-3574-4d0f-aacb-1ad5a848b302', 'toomuch'),
('66ba666b-3574-4d0f-aacb-1ad5a848b302', 'yuriha'),
('736b68e5-6f9e-44fb-ae66-f7db6709c504', 'toomuch'),
('736b68e5-6f9e-44fb-ae66-f7db6709c504', 'yuri'),
('736b68e5-6f9e-44fb-ae66-f7db6709c504', 'yuriha'),
('7c49c16a-b851-4604-8cc2-37e6032de253', 'yuri'),
('7c49c16a-b851-4604-8cc2-37e6032de253', 'yuriha'),
('7d090094-a7bf-4950-9f1d-d710f82e943e', 'yuri'),
('7d090094-a7bf-4950-9f1d-d710f82e943e', 'yuriha'),
('819bba4e-dbb5-46b4-b66d-6e99bae0fc2b', 'yuri'),
('819bba4e-dbb5-46b4-b66d-6e99bae0fc2b', 'yuriha'),
('8f8eab42-4b6c-4d1c-b197-f664abee4c2f', 'yuri'),
('8f8eab42-4b6c-4d1c-b197-f664abee4c2f', 'yuriha'),
('92a33d73-3a47-472e-a916-100a051cd0da', 'yuri'),
('92a33d73-3a47-472e-a916-100a051cd0da', 'yuriha'),
('935a7a1b-a55c-41be-aca0-28efbc09f0dc', 'toomuch'),
('935a7a1b-a55c-41be-aca0-28efbc09f0dc', 'yuri'),
('935a7a1b-a55c-41be-aca0-28efbc09f0dc', 'yuriha'),
('aa6a4731-9471-4ffa-aa96-c3fe8300764d', 'toomuch'),
('aa6a4731-9471-4ffa-aa96-c3fe8300764d', 'yuri'),
('b88bacfa-f6f6-4ca9-bd24-71dd2d58581d', 'yuri'),
('b88bacfa-f6f6-4ca9-bd24-71dd2d58581d', 'yuriha'),
('bf32d312-7ae3-4018-a552-055f1ee9a39b', 'toomuch'),
('bf32d312-7ae3-4018-a552-055f1ee9a39b', 'yuri'),
('bf32d312-7ae3-4018-a552-055f1ee9a39b', 'yuriha'),
('c530a61f-62bd-415c-af62-6a76f374f428', 'yuri'),
('c530a61f-62bd-415c-af62-6a76f374f428', 'yuriha'),
('dd863b2d-cf90-41fe-b2a9-caf3ca102691', 'toomuch'),
('dd863b2d-cf90-41fe-b2a9-caf3ca102691', 'yuriha'),
('e7dd87ca-e02c-484b-86a3-767a1c3a3b8d', 'toomuch'),
('e7dd87ca-e02c-484b-86a3-767a1c3a3b8d', 'yuri'),
('e7dd87ca-e02c-484b-86a3-767a1c3a3b8d', 'yuriha'),
('ee5fc475-1983-431c-9166-fb5e8c952790', 'onemoredoor'),
('ee5fc475-1983-431c-9166-fb5e8c952790', 'yuri'),
('ffe448fe-28ff-49e0-abb6-18e28168ffbd', 'yura'),
('ffe448fe-28ff-49e0-abb6-18e28168ffbd', 'yuri');

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
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `players`
--

INSERT INTO `players` (`id`, `username`, `password`, `wins`, `currently_logged_in`, `role`) VALUES
(0, 'yuri', '1111', 547, 0, 'admin'),
(2, 'Yuriha', '2222', 58, 0, 'player'),
(6, 'toomuch', '1111', 18, 0, 'player'),
(7, 'Idontwanna', '1111', 3, 0, 'player'),
(8, 'dontmake', '1111', 44, 0, 'player'),
(9, 'meclose', '', 40, 0, 'player'),
(10, 'onemoredoor', '1111', 36, 0, 'player'),
(12, 'crane', '1111', 0, 0, 'player'),
(13, 'yura', '1111', 1, 0, 'player');

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
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
(109, '819bba4e-dbb5-46b4-b66d-6e99bae0fc2b', 2, 'hart', 'yuriha');

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
