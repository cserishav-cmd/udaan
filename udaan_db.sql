-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 24, 2025 at 01:16 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `udaan_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `activities`
--

CREATE TABLE `activities` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `type` enum('Game','Meditation','Music') NOT NULL,
  `description` text DEFAULT NULL,
  `embed_url` text NOT NULL,
  `image_url` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `activities`
--

INSERT INTO `activities` (`id`, `name`, `title`, `type`, `description`, `embed_url`, `image_url`) VALUES
(1, 'pinball-world-cup', 'Pinball World Cup', 'Game', 'World Cup Pinball is an enjoyable game for all football fans. ', 'https://html5-games.io/pinball-world-cup', 'https://html5-games.io/cache/data/image/game/pinball-world-cup-img-f167x167.png'),
(3, 'Snake-Game', 'Snake Game', 'Game', 'The classic Snake Game is back with many exciting new improvements and is completely free-to-play online. Let\'s see, how patient are you? ', 'https://html5-games.io/pinball-world-cup', 'https://html5-games.io/cache/data/image/snakelogo-f167x167.png'),
(4, '10-min-mindfulness', 'Daily Calm | 10 Minute Mindfulness Meditation', 'Meditation', 'A 10-minute guided mindfulness meditation to help you restore and re-connect with the present moment. Ideal for beginners.', 'https://www.youtube.com/watch?v=ZToicYcHIOU', 'https://yt3.ggpht.com/ytc/AIdro_kyX1mWTQR4tCQPDwAata5PBrUWcI_qqN27RFDrXjHk26E=s48-c-k-c0x00ffffff-no-rj'),
(5, 'Shiv-Tandav-Stotram', 'Shiv Tandav Stotram', 'Music', 'Shiv Tandav Stotram | Shankar Mahadevan | रावण रचित शिव तांडव स्तोत्र | Shiv Bhajan | Shiv Bhakti', 'https://www.youtube.com/watch?v=S980-z1qx3g&list=RDS980-z1qx3g&start_radio=1', '');

-- --------------------------------------------------------

--
-- Table structure for table `appointments`
--

CREATE TABLE `appointments` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `counselor_id` int(11) NOT NULL,
  `slot_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `appointments`
--

INSERT INTO `appointments` (`id`, `user_id`, `counselor_id`, `slot_id`, `created_at`) VALUES
(1, 3, 1, 1, '2025-09-20 11:59:22'),
(2, 3, 2, 2, '2025-09-20 12:09:20'),
(3, 3, 3, 3, '2025-09-20 12:09:25'),
(4, 5, 4, 5, '2025-09-20 18:37:43'),
(5, 3, 3, 6, '2025-09-22 11:16:12'),
(6, 1, 3, 6, '2025-09-22 11:28:54'),
(7, 8, 3, 6, '2025-09-22 13:49:36'),
(8, 1, 3, 7, '2025-09-23 17:13:16'),
(9, 1, 3, 9, '2025-09-23 17:14:43'),
(10, 1, 5, 10, '2025-09-23 18:55:53');

-- --------------------------------------------------------

--
-- Table structure for table `appointment_feedback`
--

CREATE TABLE `appointment_feedback` (
  `id` int(11) NOT NULL,
  `appointment_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `counselor_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `assessment_scores`
--

CREATE TABLE `assessment_scores` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `assessment_type` varchar(50) NOT NULL,
  `score` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `assessment_scores`
--

INSERT INTO `assessment_scores` (`id`, `user_id`, `assessment_type`, `score`, `created_at`) VALUES
(1, 1, 'PHQ-9', 24, '2025-09-21 15:43:35'),
(2, 1, 'PHQ-9', 13, '2025-09-21 15:49:01'),
(3, 1, 'PHQ-9', 13, '2025-09-21 15:57:38'),
(4, 1, 'PHQ-9', 15, '2025-09-22 11:28:32'),
(5, 1, 'PHQ-9', 3, '2025-09-22 14:55:37'),
(6, 1, 'PHQ-9', 12, '2025-09-23 15:35:01'),
(7, 1, 'GAD-7', 9, '2025-09-23 19:16:39'),
(8, 1, 'GAD-7', 19, '2025-09-23 19:17:58');

-- --------------------------------------------------------

--
-- Table structure for table `available_slots`
--

CREATE TABLE `available_slots` (
  `id` int(11) NOT NULL,
  `counselor_id` int(11) NOT NULL,
  `slot_date` date NOT NULL,
  `start_time` time NOT NULL,
  `capacity` int(11) NOT NULL DEFAULT 1,
  `is_booked` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `available_slots`
--

INSERT INTO `available_slots` (`id`, `counselor_id`, `slot_date`, `start_time`, `capacity`, `is_booked`) VALUES
(1, 1, '2025-09-20', '05:30:00', 10, 0),
(10, 5, '2025-09-25', '14:00:00', 5, 0);

-- --------------------------------------------------------

--
-- Table structure for table `bug_reports`
--

CREATE TABLE `bug_reports` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `reporter_name` varchar(255) NOT NULL,
  `report_description` text NOT NULL,
  `report_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_resolved` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `bug_reports`
--

INSERT INTO `bug_reports` (`id`, `user_id`, `reporter_name`, `report_description`, `report_date`, `is_resolved`) VALUES
(1, 1, 'Gold', 'No issue its working properly.', '2025-09-21 17:00:01', 1),
(3, 3, 'Salmon Bhoi', 'Appointment section is not working properly!!!! plz fix the issue!!!!', '2025-09-22 11:24:44', 1),
(4, 1, 'Sidhu Moose wala', 'Too good Software!!!', '2025-09-23 19:06:23', 1),
(5, 1, 'Jeans Pant', 'Risav is bad boy bad developer no ML knowledge ', '2025-09-24 11:10:31', 0);

-- --------------------------------------------------------

--
-- Table structure for table `chat_history`
--

CREATE TABLE `chat_history` (
  `id` int(11) NOT NULL,
  `session_id` varchar(36) NOT NULL,
  `user_id` int(11) NOT NULL,
  `sender` enum('user','bot') NOT NULL,
  `message` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `chat_history`
--

INSERT INTO `chat_history` (`id`, `session_id`, `user_id`, `sender`, `message`, `created_at`) VALUES
(1, '', 1, 'user', 'no', '2025-09-23 09:44:00'),
(2, '', 1, '', 'Hi there! How can I help you today?  I\'m Udaan AI Companion, here to offer support and guidance.', '2025-09-23 09:44:05'),
(3, '', 1, 'user', 'I feelig not well', '2025-09-23 09:44:29'),
(4, '', 1, '', 'I\'m sorry to hear you\'re not feeling well.  Can you tell me a little more about what\'s happening?  Knowing more about how you\'re feeling will help me understand how I can best support you.  In the meantime, it might be helpful to explore some of the resources we have available.  Would you like to try one of our self-assessment tools to get a better understanding of what you might be experiencing?', '2025-09-23 09:44:31'),
(5, '', 1, 'user', 'I feeling too much tired from few days', '2025-09-23 09:45:51'),
(6, '', 1, '', 'I\'m sorry to hear you\'re feeling so tired.  That can be really draining.  It might be helpful to explore what might be causing this fatigue.  Would you like to talk more about it?  In the meantime, taking a break might help.  We have some relaxing activities in our Curricular Activities section that might help you recharge. [Find an Activity]({url_for(\'student_activities\')})', '2025-09-23 09:45:54'),
(7, 'b4ad99bb-d39b-431e-b245-06154d63db44', 1, 'user', 'hii', '2025-09-23 10:51:13'),
(8, 'b4ad99bb-d39b-431e-b245-06154d63db44', 1, '', 'Hi there! How can I help you today?', '2025-09-23 10:51:17'),
(9, 'b4ad99bb-d39b-431e-b245-06154d63db44', 1, 'user', 'I not feeling too much well', '2025-09-23 10:51:33'),
(10, 'b4ad99bb-d39b-431e-b245-06154d63db44', 1, '', 'I\'m sorry to hear you\'re not feeling well.  It sounds like you might be having a tough time.  To help me understand what\'s going on and suggest the best resources, could you tell me a little more about how you\'re feeling?  In the meantime, you might find it helpful to explore some of our resources.  We have a range of tools and information to support your well-being.\n\n[Explore Resources]({url_for(\'student_resources\')})', '2025-09-23 10:51:35'),
(11, '146ecd32-b128-4ccb-bf8a-72d68532ce52', 1, 'user', 'hii', '2025-09-23 10:58:59'),
(12, '146ecd32-b128-4ccb-bf8a-72d68532ce52', 1, '', 'Hi there! How can I help you today?', '2025-09-23 10:59:03'),
(13, '146ecd32-b128-4ccb-bf8a-72d68532ce52', 1, 'user', 'nothing', '2025-09-23 10:59:08'),
(14, '146ecd32-b128-4ccb-bf8a-72d68532ce52', 1, '', 'Hi there! How are you doing today?  Is there anything I can help you with?  I\'m here to listen and offer support.', '2025-09-23 10:59:09'),
(15, '324e1f62-1c8d-4c2e-9734-e5227987e354', 1, 'user', 'hey', '2025-09-23 11:07:55'),
(16, '324e1f62-1c8d-4c2e-9734-e5227987e354', 1, '', 'Hey there! How can I help you today?', '2025-09-23 11:07:59'),
(17, 'a12963da-4573-4317-83bc-2ce492d89606', 1, 'user', 'hii I m not feeling not well.', '2025-09-23 11:08:48'),
(18, 'a12963da-4573-4317-83bc-2ce492d89606', 1, '', 'Hi there! I\'m sorry to hear you\'re not feeling well.  It sounds like you\'re having a tough time.  To help me understand what\'s going on and how I can best support you, could you tell me a little more about what you\'re experiencing?  In the meantime, you might find it helpful to explore some of our resources.  Would you like to try one of our self-assessments or perhaps browse our Wellness Journal?\n\n[Take the PHQ-9 Assessment]({url_for(\'student_assessment\', assessment_name=\'phq9\')})\n\n[Open Your Wellness Journal]({url_for(\'student_journal\')})', '2025-09-23 11:08:50'),
(19, 'a12963da-4573-4317-83bc-2ce492d89606', 1, 'user', 'thanks', '2025-09-23 11:08:55'),
(20, 'a12963da-4573-4317-83bc-2ce492d89606', 1, '', 'You\'re welcome! Is there anything I can help you with today?  Perhaps you\'d like to explore some of the resources we offer?', '2025-09-23 11:08:56'),
(21, '5ad10746-7d29-48d8-979d-bde13b0b63ab', 1, 'user', 'hii I m not feeling not well.', '2025-09-23 11:29:37'),
(22, '5ad10746-7d29-48d8-979d-bde13b0b63ab', 1, '', 'Hi there! I\'m sorry to hear you\'re not feeling well.  It sounds like you\'re having a tough time.  To help me understand better and offer the best support, could you tell me a little more about what\'s going on?  In the meantime, you might find it helpful to explore some of our resources.  Would you like to take a look at our Wellness Journal to write down your thoughts? [Open Your Wellness Journal]({url_for(\'student_journal\')})  Or perhaps try one of our relaxing activities to help you de-stress? [Find an Activity]({url_for(\'student_activities\')})  I\'m here to listen and help in any way I can.', '2025-09-23 11:29:42'),
(23, '8a034b34-37fd-4bb8-900a-5ef9956198aa', 1, 'user', 'ok', '2025-09-23 11:36:06'),
(24, '8a034b34-37fd-4bb8-900a-5ef9956198aa', 1, '', 'Hi there!  How can I help you today?', '2025-09-23 11:36:09'),
(25, '6063e649-025f-401d-bab7-a09faf1e3c1f', 1, 'user', 'is ok??', '2025-09-23 12:00:48'),
(26, '6063e649-025f-401d-bab7-a09faf1e3c1f', 1, '', 'Hi there!  Is everything okay?  I\'m here to listen and offer support.  If you\'d like to talk about what\'s on your mind, I\'m happy to listen.  If you prefer, you can also explore some of our resources.  For example, if you\'re feeling stressed or anxious, you might find our GAD-7 assessment helpful: [Take the GAD-7 Assessment]({url_for(\'student_assessment\', assessment_name=\'gad7\')}).  Or, if you just need a moment to relax, you could check out our Curricular Activities: [Find an Activity]({url_for(\'student_activities\')}). Let me know what you\'d like to do.', '2025-09-23 12:00:53'),
(27, '8a034b34-37fd-4bb8-900a-5ef9956198aa', 1, 'user', 'ok', '2025-09-23 12:01:04'),
(28, '8a034b34-37fd-4bb8-900a-5ef9956198aa', 1, '', 'Hi there!  How can I help you today?', '2025-09-23 12:01:05'),
(29, '0b78b61b-9150-4948-971d-53886286aaff', 1, 'user', 'hii', '2025-09-23 12:18:07'),
(30, '0b78b61b-9150-4948-971d-53886286aaff', 1, 'bot', 'Hello! How can I help you today?', '2025-09-23 12:18:12'),
(31, '43a3c828-d06f-4e4b-a64c-5e2d9f70ea2d', 1, 'user', 'Hii, I not feeling well.', '2025-09-23 12:19:21'),
(32, '43a3c828-d06f-4e4b-a64c-5e2d9f70ea2d', 1, 'bot', 'Hello!  I\'m sorry to hear you\'re not feeling well. Can you tell me a little more about what\'s going on?  Knowing more will help me understand how I can best support you.', '2025-09-23 12:19:24'),
(33, '57d7dee4-d9b6-4976-bc89-8eb38e474d19', 1, 'user', 'I\'m feeling too much depressed.', '2025-09-23 12:19:34'),
(34, '57d7dee4-d9b6-4976-bc89-8eb38e474d19', 1, 'bot', 'It sounds like you\'re having a tough time. It might be helpful to understand these feelings better. You can take our confidential PHQ-9 assessment for depression. [Take the PHQ-9 Assessment]({url_for(\'student_assessment\', assessment_name=\'phq9\')})', '2025-09-23 12:19:35'),
(35, '95b3f19d-1e51-4495-bb4a-7d382ec98c98', 1, 'user', 'ok i got you', '2025-09-23 12:22:43'),
(36, '95b3f19d-1e51-4495-bb4a-7d382ec98c98', 1, 'bot', 'Okay, I understand. How can I help you today?', '2025-09-23 12:22:45'),
(37, 'e230bba9-d6d1-4a59-85b4-18bdf3cd2370', 1, 'user', 'nothing', '2025-09-23 12:25:04'),
(38, 'e230bba9-d6d1-4a59-85b4-18bdf3cd2370', 1, 'bot', 'Hello! How can I help you today?', '2025-09-23 12:25:07'),
(39, '43a3c828-d06f-4e4b-a64c-5e2d9f70ea2d', 1, 'user', 'now ok', '2025-09-23 12:35:37'),
(40, '43a3c828-d06f-4e4b-a64c-5e2d9f70ea2d', 1, 'bot', 'Okay, how can I help you today?', '2025-09-23 12:35:42'),
(41, 'e59c4b5e-98c3-46b2-9f16-1c714fbe9aa6', 1, 'user', 'I\'m feeling really tired from all this studying.', '2025-09-23 14:09:57'),
(42, 'e59c4b5e-98c3-46b2-9f16-1c714fbe9aa6', 1, 'bot', 'Taking a break is important for your well-being. We have some games, guided meditations, and relaxing music in our Curricular Activities section. [Find an Activity]({url_for(\'student_activities\')})', '2025-09-23 14:10:01'),
(43, '9962113b-e239-4651-8e7c-4d17bfa8b73b', 1, 'user', 'ok', '2025-09-23 14:10:24'),
(44, '9962113b-e239-4651-8e7c-4d17bfa8b73b', 1, 'bot', 'Okay. How can I help you today?', '2025-09-23 14:10:25'),
(45, 'e14f5fff-595a-4e5d-a11f-444fd6762938', 1, 'user', 'I\'m feeling really tired from all this studying.', '2025-09-23 14:12:12'),
(46, 'e14f5fff-595a-4e5d-a11f-444fd6762938', 1, 'bot', 'I understand you\'re feeling tired from studying.  That\'s completely understandable!  It sounds like you might need a break. Taking some time for self-care is important for your well-being. We have some games, guided meditations, and relaxing music in our Curricular Activities section that might help. [Find an Activity]({url_for(\'student_activities\')})', '2025-09-23 14:12:23'),
(47, 'bde91354-77d1-49e5-8f44-03215ff782a6', 1, 'user', 'ok', '2025-09-23 14:12:27'),
(48, 'bde91354-77d1-49e5-8f44-03215ff782a6', 1, 'bot', 'Okay. How can I help you today?', '2025-09-23 14:12:29'),
(49, 'e14f5fff-595a-4e5d-a11f-444fd6762938', 1, 'user', 'ok', '2025-09-23 14:14:24'),
(50, 'e14f5fff-595a-4e5d-a11f-444fd6762938', 1, 'bot', 'Okay! How can I help you today?', '2025-09-23 14:14:28'),
(51, 'd02aa882-cc3e-43db-bbe9-f13217223611', 1, 'user', 'ok', '2025-09-23 15:13:33'),
(52, 'e14f5fff-595a-4e5d-a11f-444fd6762938', 1, 'user', 'nothing', '2025-09-23 15:14:04'),
(53, 'e14f5fff-595a-4e5d-a11f-444fd6762938', 1, 'bot', 'Hello! How can I help you today?', '2025-09-23 15:14:16'),
(54, 'd02aa882-cc3e-43db-bbe9-f13217223611', 1, 'bot', 'Okay. How can I help you today?', '2025-09-23 15:14:40'),
(55, 'e6927dc1-1a12-4026-a12f-5a900fd59035', 1, 'user', 'I not feeling well.', '2025-09-23 15:33:31'),
(56, 'e6927dc1-1a12-4026-a12f-5a900fd59035', 1, 'bot', 'I\'m sorry to hear you\'re not feeling well.  Can you tell me a little more about what\'s going on?  Knowing more about how you\'re feeling will help me understand how I can best support you.', '2025-09-23 15:33:36'),
(57, '4d4c3931-5c42-49e9-928c-cebe9afb5eca', 1, 'user', 'I want to kill myself.', '2025-09-23 15:33:50'),
(58, '4d4c3931-5c42-49e9-928c-cebe9afb5eca', 1, 'bot', 'It sounds like you are going through a difficult time. Please consider reaching out to a crisis hotline or a mental health professional immediately. You can call a local crisis line or the National Suicide Prevention Lifeline at 988. Your well-being is very important.', '2025-09-23 15:33:56'),
(59, 'e6927dc1-1a12-4026-a12f-5a900fd59035', 1, 'user', 'ok', '2025-09-23 17:16:06'),
(60, 'e6927dc1-1a12-4026-a12f-5a900fd59035', 1, 'bot', 'Okay! How can I help you today?', '2025-09-23 17:16:11'),
(61, 'e6927dc1-1a12-4026-a12f-5a900fd59035', 1, 'user', 'i am too tired', '2025-09-23 17:16:22'),
(62, 'e6927dc1-1a12-4026-a12f-5a900fd59035', 1, 'bot', 'Taking a break is important for your well-being. We have some games, guided meditations, and relaxing music in our Curricular Activities section. [Find an Activity]({url_for(\'student_activities\')})', '2025-09-23 17:16:24'),
(63, 'a25766e2-8535-417c-b51c-aa58f4d4e459', 1, 'user', 'I not feeling well.', '2025-09-23 17:18:51'),
(64, 'a25766e2-8535-417c-b51c-aa58f4d4e459', 1, 'bot', 'I\'m sorry to hear you\'re not feeling well.  Can you tell me a little more about what\'s happening?  Knowing more about how you\'re feeling will help me understand how I can best support you.', '2025-09-23 17:18:56'),
(65, 'a25766e2-8535-417c-b51c-aa58f4d4e459', 1, 'user', 'I\'m feeling too much tired.', '2025-09-23 17:19:06'),
(66, 'a25766e2-8535-417c-b51c-aa58f4d4e459', 1, 'bot', 'I\'m sorry to hear you\'re feeling tired.  That can be really draining.  Taking a break is important for your well-being. We have some games, guided meditations, and relaxing music in our Curricular Activities section that might help. [Find an Activity]({url_for(\'student_activities\')})  We also have resources on stress management which might offer some helpful strategies. [Explore Resources]({url_for(\'student_resources\')})  Is there anything else I can help you with today?', '2025-09-23 17:19:17'),
(67, 'a25766e2-8535-417c-b51c-aa58f4d4e459', 1, 'user', 'I\'m feeling too much tired.', '2025-09-23 17:27:40'),
(68, 'a25766e2-8535-417c-b51c-aa58f4d4e459', 1, 'bot', 'Feeling tired can be really draining.  Taking a break is important for your well-being. We have some games, guided meditations, and relaxing music in our Curricular Activities section that might help you recharge. [Find an Activity]({url_for(\'student_activities\')})  We also have resources on stress management which might be helpful if tiredness is related to stress. [Explore Resources]({url_for(\'student_resources\')})', '2025-09-23 17:27:52'),
(69, '2f38ad6e-1fe1-401c-84ea-11eecdb77746', 1, 'user', 'I\'m feeling too much tired.', '2025-09-23 17:50:43'),
(70, '2f38ad6e-1fe1-401c-84ea-11eecdb77746', 1, 'bot', 'Feeling tired can be really draining.  Taking a break is important for your well-being. We have some games, guided meditations, and relaxing music in our Curricular Activities section that might help you feel refreshed. [Find an Activity]({url_for(\'student_activities\')})  We also have resources on stress management which might offer additional strategies. [Explore Resources]({url_for(\'student_resources\')})', '2025-09-23 17:50:56'),
(71, '2f38ad6e-1fe1-401c-84ea-11eecdb77746', 1, 'user', 'I want to scan my facial recognition.', '2025-09-23 17:57:54'),
(72, '68cba950-b48a-4074-8512-cf649dcb627a', 1, 'user', 'I want to scan my facial recognition.', '2025-09-23 18:01:27'),
(73, '2f38ad6e-1fe1-401c-84ea-11eecdb77746', 1, 'user', 'I want to scan my facial recognition.', '2025-09-23 18:01:47'),
(74, '68cba950-b48a-4074-8512-cf649dcb627a', 1, 'bot', 'I\'m not able to find specific information about facial recognition scanning in our resources.  However, I\'m here to offer general support. Is there anything else I can help you with today? Perhaps you\'d like to explore some of our other features?  For example, you might find our Wellness Journal helpful for writing down your thoughts and feelings. [Open Your Wellness Journal]({url_for(\'student_journal\')})', '2025-09-23 18:01:48'),
(75, '2f38ad6e-1fe1-401c-84ea-11eecdb77746', 1, 'bot', 'I\'m not sure I understand what you mean by \"scan my facial recognition.\"  Could you tell me more about what you\'re hoping to achieve?  I\'m here to offer support, and while I can\'t provide specific help with that request, I can offer general support if you\'re feeling stressed or overwhelmed.  Is there anything else I can assist you with today?', '2025-09-23 18:01:57'),
(76, '09b855d4-54de-4163-a710-4649f12e359c', 1, 'user', 'I\'m feeling too much tired can you tell me how can I refresh myself???', '2025-09-23 19:10:29'),
(77, '09b855d4-54de-4163-a710-4649f12e359c', 1, 'bot', 'Taking a break is important for your well-being.  We have some games, guided meditations, and relaxing music in our Curricular Activities section that might help you refresh yourself. [Find an Activity]({url_for(\'student_activities\')})', '2025-09-23 19:10:34'),
(78, '09b855d4-54de-4163-a710-4649f12e359c', 1, 'user', 'what is Burj-khalifa???', '2025-09-23 19:11:22'),
(79, '09b855d4-54de-4163-a710-4649f12e359c', 1, 'bot', 'I\'m sorry, I can\'t find specific information about the Burj Khalifa in the information I have access to.  I\'m here to offer support for your mental wellness, though.  Is there anything else I can help you with today?', '2025-09-23 19:11:30'),
(80, '09b855d4-54de-4163-a710-4649f12e359c', 1, 'user', 'i will kill myself!!!', '2025-09-23 19:12:12'),
(81, '09b855d4-54de-4163-a710-4649f12e359c', 1, 'bot', 'It sounds like you are going through a difficult time. Please consider reaching out to a crisis hotline or a mental health professional immediately. You can call a local crisis line or the National Suicide Prevention Lifeline at 988. Your well-being is very important.', '2025-09-23 19:12:16');

-- --------------------------------------------------------

--
-- Table structure for table `chat_sessions`
--

CREATE TABLE `chat_sessions` (
  `id` varchar(36) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(100) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `chat_sessions`
--

INSERT INTO `chat_sessions` (`id`, `user_id`, `title`, `created_at`) VALUES
('09b855d4-54de-4163-a710-4649f12e359c', 1, 'I\'m feeling too much tired can you tell ...', '2025-09-23 19:10:29'),
('2f38ad6e-1fe1-401c-84ea-11eecdb77746', 1, 'I\'m feeling too much tired.', '2025-09-23 17:50:43'),
('43a3c828-d06f-4e4b-a64c-5e2d9f70ea2d', 1, 'Hii, I not feeling well.', '2025-09-23 12:19:21'),
('4d4c3931-5c42-49e9-928c-cebe9afb5eca', 1, 'I want to kill myself.', '2025-09-23 15:33:50'),
('57d7dee4-d9b6-4976-bc89-8eb38e474d19', 1, 'I\'m feeling too much depressed.', '2025-09-23 12:19:33'),
('68cba950-b48a-4074-8512-cf649dcb627a', 1, 'I want to scan my facial recognition.', '2025-09-23 18:01:27'),
('95b3f19d-1e51-4495-bb4a-7d382ec98c98', 1, 'ok i got you', '2025-09-23 12:22:43'),
('9962113b-e239-4651-8e7c-4d17bfa8b73b', 1, 'ok', '2025-09-23 14:10:24'),
('a25766e2-8535-417c-b51c-aa58f4d4e459', 1, 'I not feeling well.', '2025-09-23 17:18:51'),
('bde91354-77d1-49e5-8f44-03215ff782a6', 1, 'ok', '2025-09-23 14:12:27'),
('d02aa882-cc3e-43db-bbe9-f13217223611', 1, 'ok', '2025-09-23 15:13:33'),
('e14f5fff-595a-4e5d-a11f-444fd6762938', 1, 'I\'m feeling really tired from all this s...', '2025-09-23 14:12:12'),
('e230bba9-d6d1-4a59-85b4-18bdf3cd2370', 1, 'nothing', '2025-09-23 12:25:04'),
('e59c4b5e-98c3-46b2-9f16-1c714fbe9aa6', 1, 'I\'m feeling really tired from all this s...', '2025-09-23 14:09:57'),
('e6927dc1-1a12-4026-a12f-5a900fd59035', 1, 'I not feeling well.', '2025-09-23 15:33:31');

-- --------------------------------------------------------

--
-- Table structure for table `counselors`
--

CREATE TABLE `counselors` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `specialty` varchar(255) DEFAULT NULL,
  `image_url` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `counselors`
--

INSERT INTO `counselors` (`id`, `name`, `specialty`, `image_url`) VALUES
(6, 'Dr. Roddur Roy', 'Academic Counselor', '');

-- --------------------------------------------------------

--
-- Table structure for table `counselor_feedback`
--

CREATE TABLE `counselor_feedback` (
  `id` int(11) NOT NULL,
  `appointment_id` int(11) NOT NULL,
  `counselor_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `daily_tasks`
--

CREATE TABLE `daily_tasks` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `task_description` varchar(255) NOT NULL,
  `is_completed` tinyint(1) NOT NULL DEFAULT 0,
  `task_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `daily_tasks`
--

INSERT INTO `daily_tasks` (`id`, `user_id`, `task_description`, `is_completed`, `task_date`) VALUES
(1, 1, 'Write in your Wellness Journal', 0, '2025-09-21'),
(2, 1, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-21'),
(3, 1, 'Connect with a friend or family member', 0, '2025-09-21'),
(4, 1, 'Get at least 15 minutes of physical activity', 0, '2025-09-21'),
(5, 1, 'Review one helpful article from the Resources section', 0, '2025-09-21'),
(6, 1, 'Write in your Wellness Journal', 0, '2025-09-22'),
(7, 1, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-22'),
(8, 1, 'Connect with a friend or family member', 0, '2025-09-22'),
(9, 1, 'Get at least 15 minutes of physical activity', 0, '2025-09-22'),
(10, 1, 'Review one helpful article from the Resources section', 0, '2025-09-22'),
(11, 3, 'Write in your Wellness Journal', 0, '2025-09-22'),
(12, 3, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-22'),
(13, 3, 'Connect with a friend or family member', 0, '2025-09-22'),
(14, 3, 'Get at least 15 minutes of physical activity', 0, '2025-09-22'),
(15, 3, 'Review one helpful article from the Resources section', 0, '2025-09-22'),
(16, 5, 'Write in your Wellness Journal', 0, '2025-09-22'),
(17, 5, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-22'),
(18, 5, 'Connect with a friend or family member', 0, '2025-09-22'),
(19, 5, 'Get at least 15 minutes of physical activity', 0, '2025-09-22'),
(20, 5, 'Review one helpful article from the Resources section', 0, '2025-09-22'),
(21, 4, 'Write in your Wellness Journal', 0, '2025-09-22'),
(22, 4, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-22'),
(23, 4, 'Connect with a friend or family member', 0, '2025-09-22'),
(24, 4, 'Get at least 15 minutes of physical activity', 0, '2025-09-22'),
(25, 4, 'Review one helpful article from the Resources section', 0, '2025-09-22'),
(26, 6, 'Write in your Wellness Journal', 0, '2025-09-22'),
(27, 6, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-22'),
(28, 6, 'Connect with a friend or family member', 0, '2025-09-22'),
(29, 6, 'Get at least 15 minutes of physical activity', 0, '2025-09-22'),
(30, 6, 'Review one helpful article from the Resources section', 0, '2025-09-22'),
(31, 7, 'Write in your Wellness Journal', 0, '2025-09-22'),
(32, 7, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-22'),
(33, 7, 'Connect with a friend or family member', 0, '2025-09-22'),
(34, 7, 'Get at least 15 minutes of physical activity', 0, '2025-09-22'),
(35, 7, 'Review one helpful article from the Resources section', 0, '2025-09-22'),
(36, 8, 'Write in your Wellness Journal', 0, '2025-09-22'),
(37, 8, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-22'),
(38, 8, 'Connect with a friend or family member', 0, '2025-09-22'),
(39, 8, 'Get at least 15 minutes of physical activity', 0, '2025-09-22'),
(40, 8, 'Review one helpful article from the Resources section', 0, '2025-09-22'),
(41, 1, 'Write in your Wellness Journal', 0, '2025-09-23'),
(42, 1, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-23'),
(43, 1, 'Connect with a friend or family member', 0, '2025-09-23'),
(44, 1, 'Get at least 15 minutes of physical activity', 0, '2025-09-23'),
(45, 1, 'Review one helpful article from the Resources section', 0, '2025-09-23'),
(46, 3, 'Write in your Wellness Journal', 0, '2025-09-23'),
(47, 3, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-23'),
(48, 3, 'Connect with a friend or family member', 0, '2025-09-23'),
(49, 3, 'Get at least 15 minutes of physical activity', 0, '2025-09-23'),
(50, 3, 'Review one helpful article from the Resources section', 0, '2025-09-23'),
(51, 5, 'Write in your Wellness Journal', 0, '2025-09-23'),
(52, 5, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-23'),
(53, 5, 'Connect with a friend or family member', 0, '2025-09-23'),
(54, 5, 'Get at least 15 minutes of physical activity', 0, '2025-09-23'),
(55, 5, 'Review one helpful article from the Resources section', 0, '2025-09-23'),
(56, 4, 'Write in your Wellness Journal', 0, '2025-09-23'),
(57, 4, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-23'),
(58, 4, 'Connect with a friend or family member', 0, '2025-09-23'),
(59, 4, 'Get at least 15 minutes of physical activity', 0, '2025-09-23'),
(60, 4, 'Review one helpful article from the Resources section', 0, '2025-09-23'),
(61, 1, 'Write in your Wellness Journal', 0, '2025-09-24'),
(62, 1, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-24'),
(63, 1, 'Connect with a friend or family member', 0, '2025-09-24'),
(64, 1, 'Get at least 15 minutes of physical activity', 0, '2025-09-24'),
(65, 1, 'Review one helpful article from the Resources section', 0, '2025-09-24'),
(66, 4, 'Write in your Wellness Journal', 0, '2025-09-24'),
(67, 4, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-24'),
(68, 4, 'Connect with a friend or family member', 0, '2025-09-24'),
(69, 4, 'Get at least 15 minutes of physical activity', 0, '2025-09-24'),
(70, 4, 'Review one helpful article from the Resources section', 0, '2025-09-24'),
(71, 5, 'Write in your Wellness Journal', 0, '2025-09-24'),
(72, 5, 'Spend 5 minutes on a relaxation activity', 0, '2025-09-24'),
(73, 5, 'Connect with a friend or family member', 0, '2025-09-24'),
(74, 5, 'Get at least 15 minutes of physical activity', 0, '2025-09-24'),
(75, 5, 'Review one helpful article from the Resources section', 0, '2025-09-24');

-- --------------------------------------------------------

--
-- Table structure for table `emotion_logs`
--

CREATE TABLE `emotion_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `log_time` timestamp NOT NULL DEFAULT current_timestamp(),
  `neutral` int(11) DEFAULT 0,
  `happy` int(11) DEFAULT 0,
  `surprise` int(11) DEFAULT 0,
  `angry` int(11) DEFAULT 0,
  `disgust` int(11) DEFAULT 0,
  `fear` int(11) DEFAULT 0,
  `sad` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `emotion_logs`
--

INSERT INTO `emotion_logs` (`id`, `user_id`, `log_time`, `neutral`, `happy`, `surprise`, `angry`, `disgust`, `fear`, `sad`) VALUES
(1, 1, '2025-09-23 15:18:45', 1, 0, 0, 0, 0, 0, 0),
(2, 1, '2025-09-23 15:18:53', 1, 0, 0, 0, 0, 0, 0),
(3, 3, '2025-09-23 15:20:06', 0, 1, 0, 0, 0, 0, 0),
(4, 3, '2025-09-23 15:20:14', 0, 1, 0, 0, 0, 0, 0),
(5, 3, '2025-09-23 15:20:45', 0, 1, 0, 0, 0, 0, 0),
(6, 3, '2025-09-23 15:20:58', 0, 1, 0, 0, 0, 0, 0),
(7, 3, '2025-09-23 15:21:03', 0, 1, 0, 0, 0, 0, 0),
(8, 3, '2025-09-23 15:21:08', 0, 1, 0, 0, 0, 0, 0),
(9, 3, '2025-09-23 15:21:20', 0, 1, 0, 0, 0, 0, 0),
(10, 3, '2025-09-23 15:21:25', 0, 1, 0, 0, 0, 0, 0),
(11, 3, '2025-09-23 15:21:30', 1, 0, 0, 0, 0, 0, 0),
(12, 1, '2025-09-23 15:35:37', 1, 0, 1, 0, 0, 0, 0),
(13, 1, '2025-09-23 15:35:42', 1, 0, 0, 0, 0, 0, 0),
(14, 1, '2025-09-23 15:35:49', 0, 0, 1, 0, 0, 0, 0),
(15, 1, '2025-09-23 15:35:54', 3, 0, 0, 0, 0, 0, 0),
(16, 1, '2025-09-23 15:35:59', 1, 0, 0, 0, 0, 0, 0),
(17, 1, '2025-09-23 15:36:04', 0, 0, 0, 1, 0, 0, 0),
(18, 1, '2025-09-23 15:36:09', 0, 1, 0, 0, 0, 0, 0),
(19, 1, '2025-09-23 15:36:15', 0, 0, 0, 1, 0, 0, 0),
(20, 1, '2025-09-23 17:38:28', 0, 0, 0, 0, 0, 1, 0),
(21, 1, '2025-09-23 17:38:33', 1, 0, 0, 0, 0, 0, 0),
(22, 1, '2025-09-23 17:38:39', 0, 0, 0, 1, 0, 0, 0),
(23, 1, '2025-09-23 17:38:44', 0, 0, 0, 1, 0, 0, 0),
(24, 1, '2025-09-23 17:38:49', 0, 0, 0, 1, 0, 0, 0),
(25, 1, '2025-09-23 17:38:54', 0, 0, 0, 0, 0, 1, 0),
(26, 1, '2025-09-23 19:18:55', 0, 1, 0, 1, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `forum_guidelines`
--

CREATE TABLE `forum_guidelines` (
  `id` int(11) NOT NULL,
  `guideline` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `forum_guidelines`
--

INSERT INTO `forum_guidelines` (`id`, `guideline`) VALUES
(1, 'Be respectful and courteous to others at all times.'),
(2, 'Do not share any personal identifying information, such as your real name, address, or phone number.'),
(3, 'This is a support forum, not a substitute for professional medical advice. If you are in crisis, please contact emergency services.'),
(4, 'No hate speech, bullying, or harassment will be tolerated.'),
(5, 'Keep discussions supportive and constructive.'),
(6, 'Do not post spam, advertisements, or irrelevant content.');

-- --------------------------------------------------------

--
-- Table structure for table `forum_posts`
--

CREATE TABLE `forum_posts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `topic_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('open','resolved') NOT NULL DEFAULT 'open'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `forum_posts`
--

INSERT INTO `forum_posts` (`id`, `user_id`, `topic_id`, `title`, `content`, `created_at`, `status`) VALUES
(1, 5, 1, 'How to interact with everybody.', 'Please anyone explain how can I talk with a random person actually live in PG.', '2025-09-23 15:27:20', 'resolved'),
(2, 5, 4, 'Hii', 'hiii', '2025-09-23 15:39:47', 'resolved'),
(3, 1, 3, 'I\'m tired on my current relationship', 'How can concentrate on my education for this reason!!!??', '2025-09-23 19:00:26', 'resolved');

-- --------------------------------------------------------

--
-- Table structure for table `forum_replies`
--

CREATE TABLE `forum_replies` (
  `id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `forum_replies`
--

INSERT INTO `forum_replies` (`id`, `post_id`, `user_id`, `content`, `created_at`) VALUES
(1, 1, 3, 'okk', '2025-09-20 09:31:10'),
(2, 1, 3, 'Try to talk with everyone very politely and don\'t make any type of problem.', '2025-09-23 15:28:49'),
(3, 2, 1, 'okkk', '2025-09-23 15:40:44'),
(4, 3, 4, 'Go fuck!! your self!!!', '2025-09-23 19:02:20');

-- --------------------------------------------------------

--
-- Table structure for table `forum_reports`
--

CREATE TABLE `forum_reports` (
  `id` int(11) NOT NULL,
  `post_id` int(11) DEFAULT NULL,
  `reply_id` int(11) DEFAULT NULL,
  `reported_user_id` int(11) NOT NULL,
  `reported_by_user_id` int(11) NOT NULL,
  `reason` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('pending','resolved') NOT NULL DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `forum_reports`
--

INSERT INTO `forum_reports` (`id`, `post_id`, `reply_id`, `reported_user_id`, `reported_by_user_id`, `reason`, `created_at`, `status`) VALUES
(1, NULL, 1, 3, 2, 'too good', '2025-09-23 15:50:03', 'resolved'),
(2, NULL, 4, 4, 1, 'hate speech', '2025-09-23 19:04:56', 'resolved');

-- --------------------------------------------------------

--
-- Table structure for table `forum_topics`
--

CREATE TABLE `forum_topics` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `forum_topics`
--

INSERT INTO `forum_topics` (`id`, `name`, `description`) VALUES
(1, 'General Discussion', 'A place for general chat and support.'),
(2, 'Academic Stress', 'Discuss exam pressure, deadlines, and study strategies.'),
(3, 'Relationships', 'Talk about friendships, family, and romantic relationships.'),
(4, 'Anxiety & Stress', 'Share experiences and coping mechanisms for anxiety.'),
(5, 'Feeling Low', 'A space to talk when you are feeling down or lonely.');

-- --------------------------------------------------------

--
-- Table structure for table `game_scores`
--

CREATE TABLE `game_scores` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `game_name` varchar(255) NOT NULL,
  `score` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `game_scores`
--

INSERT INTO `game_scores` (`id`, `user_id`, `game_name`, `score`) VALUES
(1, 5, 'pinball-world-cup', 5),
(2, 1, 'pinball-world-cup', 10);

-- --------------------------------------------------------

--
-- Table structure for table `journal_entries`
--

CREATE TABLE `journal_entries` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `entry_text` text NOT NULL,
  `mood` varchar(50) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `journal_entries`
--

INSERT INTO `journal_entries` (`id`, `user_id`, `entry_text`, `mood`, `created_at`) VALUES
(1, 4, 'Ami aaj 2 plate 2 biriyani niyechii!!! too much happy', 'happy', '2025-09-20 18:47:13'),
(2, 4, 'aaj amar mon bhalo nei!!!', 'sad', '2025-09-20 18:47:47'),
(3, 3, 'i feeling good !!', 'happy', '2025-09-22 08:48:41'),
(4, 3, 'I am feeling not good.', 'neutral', '2025-09-22 11:14:04'),
(5, 1, 'Hi I am feeling too much grateful.', 'great', '2025-09-22 15:02:55'),
(6, 1, 'aajj ami loochi kheyechi!! bhub ananda hochee!!!', 'great', '2025-09-23 19:20:35'),
(7, 1, 'aaj amar breakup hoyeche', 'sad', '2025-09-23 19:20:53'),
(8, 1, 'aaj ami ranna korlam', 'okay', '2025-09-23 19:21:06'),
(9, 1, 'hii', 'happy', '2025-09-23 19:21:14');

-- --------------------------------------------------------

--
-- Table structure for table `platform_settings`
--

CREATE TABLE `platform_settings` (
  `setting_key` varchar(255) NOT NULL,
  `setting_value` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `platform_settings`
--

INSERT INTO `platform_settings` (`setting_key`, `setting_value`) VALUES
('emergency_contact_name', 'Anti Ragging Portal'),
('emergency_contact_number', '1800-180-5522'),
('forum_anonymity', 'anonymous'),
('maintenance_mode', 'off'),
('welcome_message', 'Nothing');

-- --------------------------------------------------------

--
-- Table structure for table `resources`
--

CREATE TABLE `resources` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `content` text DEFAULT NULL,
  `resource_type` varchar(50) DEFAULT NULL,
  `link` text DEFAULT NULL,
  `image_url` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `resources`
--

INSERT INTO `resources` (`id`, `title`, `description`, `content`, `resource_type`, `link`, `image_url`, `created_at`) VALUES
(3, 'Chronic inflammation messes with your mind. Here\'s how to calm it', 'Golam Khandaker’s mother has had arthritis for as long as he can remember. She also lives with depression, and it always struck Khandaker how precisely her arthritis flare-ups coincide with her most severe episodes of low mood.\r\n\r\nPerhaps it isn’t surprising that these bouts of painful inflammation might cause her to feel low. But as Khandaker, then studying for a PhD at the University of Cambridge, investigated more closely, it became clear there was more going on.\r\n\r\nIn fact, research is revealing the profound effect persistent low-level inflammation has on the brain – which was once thought largely impervious to the fires burning elsewhere in the body – and what this means not only for depression, but for anxiety, schizophrenia, Alzheimer’s and more. By unpicking the mechanisms driving these connections, researchers are coming up with new ways to protect people’s brains and mental health, on top of the many day-to-day ways we can help ourselves.\r\n\r\nOur immune defences are vital for survival. When the body detects an infection or injury, it activates an immune response, characterised by a cascade of inflammatory proteins called cytokines, to eliminate the pathogen and promote tissue repair. “Sickness behaviour” can also be triggered – a constellation of symptoms such as fatigue, social withdrawal and loss of appetite that is strikingly similar to major depression. In the acute phase of an illness, this behaviour is beneficial and signals the need to rest and recover during times of physical injury or infection.\r\n\r\nSometimes, however, the acute immune response doesn’t fade, and cytokines linger long after the initial battle is won, resulting in chronic low-grade inflammation. This is one of the scourges of the modern world, contributing to heart disease, type 2 diabetes, kidney disease and more. Now, the toll this takes on our brains is also becoming evident.', 'From depression to dementia, we are now realising the profound impacts of long-term inflammation on the brain. A better understanding of the underlying mechanisms is unlocking new treatments to protect our cognitive function and mental health', 'Article', 'https://www.newscientist.com/article/2491017-chronic-inflammation-messes-with-your-mind-heres-how-to-calm-it/', 'https://images.newscientist.com/wp-content/uploads/2025/08/14165146/6mb.gif?width=1100', '2025-09-24 10:56:56'),
(4, 'How to Get Your Brain to Focus | Chris Bailey | TEDxManchester', 'The latest research is clear: the state of our attention determines the state of our lives. So how do we harness our attention to focus deeper, get distracted less, and even become more creative? Chris Bailey, author of the recent book Hyperfocus, talks about how our ability to focus is the key to productivity, creativity, and living a meaningful life.\r\n\r\nFollow Chris on @chris_bailey Chris Bailey was recently described by TED as possibly “the most productive man you’d ever hope to meet”. He is the international bestselling author of Hyperfocus and The Productivity Project, which have been published in sixteen languages. Chris works with organisations around the globe on how they can become more productive without hating the process.\r\n\r\nTo date, Chris has written hundreds of articles on the subject of productivity, and has garnered coverage in media as diverse as The New York Times, The Wall Street Journal, New York magazine, The Huffington Post, Harvard Business Review, TED, Fortune, Fast Company, and Lifehacker. This talk was given at a TEDx event using the TED conference format but independently organized by a local community.', 'The latest research is clear: the state of our attention determines the state of our lives. So how do we harness our attention to focus deeper, get distracted less, and even become more creative? Chris Bailey, author of the recent book Hyperfocus, talks about how our ability to focus is the key to productivity, creativity, and living a meaningful life.\r\n\r\nFollow Chris on @chris_bailey Chris Bailey was recently described by TED as possibly “the most productive man you’d ever hope to meet”. He is the international bestselling author of Hyperfocus and The Productivity Project, which have been published in sixteen languages. Chris works with organisations around the globe on how they can become more productive without hating the process.\r\n\r\nTo date, Chris has written hundreds of articles on the subject of productivity, and has garnered coverage in media as diverse as The New York Times, The Wall Street Journal, New York magazine, The Huffington Post, Harvard Business Review, TED, Fortune, Fast Company, and Lifehacker. This talk was given at a TEDx event using the TED conference format but independently organized by a local community.', 'Video', 'https://www.youtube.com/watch?v=Hu4Yvq-g7_Y', 'data:image/jpeg;base64,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', '2025-09-24 10:59:10'),
(5, 'Herbs and supplements for depression', 'A remedy may be herbal or natural, but this does not mean it is safe or effective. In the United States, the Food and Drug Administration (FDA) does not regulate supplements in the same way as drugs. This means supplements can vary significantly in quality.\r\n\r\nHerbs and supplements can also interact with other substances. Sometimes, this can result in dangerous side effects.\r\n\r\nPeople should not try to treat depression on their own. Wherever possible, speak with a mental health professional about the symptoms, and always check with a doctor before trying a new supplement.\r\n\r\nThe following herbs and supplements may help with symptoms of depression.\r\n\r\n**To read click below link', 'Depression is a potentially serious mood disorder. Herbal remedies may help reduce the symptoms, but there is little information about their long-term effects.', 'Article', 'https://www.medicalnewstoday.com/articles/314421#st-johns-wort', 'data:image/jpeg;base64,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', '2025-09-24 11:08:28');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL DEFAULT 'student',
  `institute_name` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_volunteer` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `role`, `institute_name`, `created_at`, `is_volunteer`) VALUES
(1, 'Swarnil', 'swarnil@gmail.com', 'scrypt:32768:8:1$aOgk8DGm9nRUhlnw$0a0837139a7ccfc3e8c649398c45ed240a567c25c3a955e48d496f2977d61c17878354398ffdf0eb9c52e6aebaeabd61b3554e309296063390fbc2e972f231aa', 'student', NULL, '2025-09-20 09:10:38', 0),
(2, 'admin_fit@gmail.com', 'fit@gmail.com', 'scrypt:32768:8:1$VMTdrDtgMBHJnt3l$0605ecdf90996810110b3da9e92ec1515dddc92a792df48741351a3fb4f22c5dfabba9ceb31e0828e9028791bb406b486314eeb7625d27dc0913f106f8839f34', 'admin', 'Future Institute of Technology', '2025-09-20 09:11:16', 0),
(3, 'Rishav', 'rishav@gmail.com', 'scrypt:32768:8:1$i5VC5EU0OnIXZsed$0e0d98987eede94578cf58f90b23f8249e5ee762d33e10aa4876abbc9f4e128a5c62553c720368a3aca98efa2401fd4a90271bb3e53f320142c33cf042186f36', 'student', NULL, '2025-09-20 09:24:02', 1),
(4, 'Debjit', 'debjit@gmail.com', 'scrypt:32768:8:1$qdMEwUvbEnDHuxIT$423269799c168e0d5ca62b1cb8ad5a775e27441a9c3750e2579eed0b7fd0dfc868986422311a473c259450b7f297877eaa1045cd844bb50091a3dab96bb12425', 'student', NULL, '2025-09-20 18:32:02', 1),
(5, 'Bithika', 'bithika@gmail.com', 'scrypt:32768:8:1$HsgnqVL5t4mX3vMj$db128459b3b2603e2ad2626f7b90118929976c35fce429ecb34105e8b3009fe263b3bc8c89ccd00c781162b9317355b895788e0129305f37ee12903361df8d38', 'student', NULL, '2025-09-20 18:32:30', 0),
(6, 'Arka', 'arka@gmail.com', 'scrypt:32768:8:1$sDxe9EC9ND67l3Yb$296451de8e47521721d460db7370dadc17bcbda76f83660bc1107387570bccc3a882f40cb4878111be0ef470f9b7cfd8d288bde7d7028099a5514a7f0271f6a6', 'student', NULL, '2025-09-22 08:40:27', 0),
(7, 'Samrat', 'samrat@gmail.com', 'scrypt:32768:8:1$1pWnuvcL5ENeWKLK$e610cc32389d38bf1ed8e509642850f5177b58b37323c65cee8ae42847ce89cd9377fa3415af7c05a9dc15b4405d64bfb477ee997bc4de3bc818a70427e884e4', 'student', NULL, '2025-09-22 08:40:57', 0),
(8, 'Swapnil', 'swapnil@gmail.com', 'scrypt:32768:8:1$hqnIus4OxHKsJiGB$9b18ee1548148266d97d9930f9eca437069cae12599b086f8c123c05957ffac27333a5e82bc4a5ac778f1dac7f9b8a765a7e120655d875782bbb6e94af5c05d9', 'student', NULL, '2025-09-22 08:41:29', 0);

-- --------------------------------------------------------

--
-- Table structure for table `volunteer_feedback`
--

CREATE TABLE `volunteer_feedback` (
  `id` int(11) NOT NULL,
  `volunteer_user_id` int(11) NOT NULL,
  `feedback_by_user_id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `volunteer_feedback`
--

INSERT INTO `volunteer_feedback` (`id`, `volunteer_user_id`, `feedback_by_user_id`, `post_id`, `rating`, `comment`, `created_at`) VALUES
(1, 1, 5, 2, 5, '', '2025-09-23 15:41:17'),
(2, 1, 5, 2, 5, '', '2025-09-23 15:42:40'),
(3, 3, 5, 1, 5, '', '2025-09-23 15:42:50'),
(4, 3, 5, 1, 5, '', '2025-09-23 15:42:54'),
(5, 4, 1, 3, 5, 'Best Guy in the world!!!', '2025-09-23 19:03:06');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `activities`
--
ALTER TABLE `activities`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `appointment_feedback`
--
ALTER TABLE `appointment_feedback`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `assessment_scores`
--
ALTER TABLE `assessment_scores`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `available_slots`
--
ALTER TABLE `available_slots`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `bug_reports`
--
ALTER TABLE `bug_reports`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `chat_history`
--
ALTER TABLE `chat_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `chat_sessions`
--
ALTER TABLE `chat_sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `counselors`
--
ALTER TABLE `counselors`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `counselor_feedback`
--
ALTER TABLE `counselor_feedback`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `appointment_id` (`appointment_id`);

--
-- Indexes for table `daily_tasks`
--
ALTER TABLE `daily_tasks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`,`task_date`);

--
-- Indexes for table `emotion_logs`
--
ALTER TABLE `emotion_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `forum_guidelines`
--
ALTER TABLE `forum_guidelines`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `forum_posts`
--
ALTER TABLE `forum_posts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `topic_id` (`topic_id`);

--
-- Indexes for table `forum_replies`
--
ALTER TABLE `forum_replies`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `forum_reports`
--
ALTER TABLE `forum_reports`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `forum_topics`
--
ALTER TABLE `forum_topics`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `game_scores`
--
ALTER TABLE `game_scores`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_game` (`user_id`,`game_name`);

--
-- Indexes for table `journal_entries`
--
ALTER TABLE `journal_entries`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `platform_settings`
--
ALTER TABLE `platform_settings`
  ADD PRIMARY KEY (`setting_key`);

--
-- Indexes for table `resources`
--
ALTER TABLE `resources`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `volunteer_feedback`
--
ALTER TABLE `volunteer_feedback`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `activities`
--
ALTER TABLE `activities`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `appointments`
--
ALTER TABLE `appointments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `appointment_feedback`
--
ALTER TABLE `appointment_feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `assessment_scores`
--
ALTER TABLE `assessment_scores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `available_slots`
--
ALTER TABLE `available_slots`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `bug_reports`
--
ALTER TABLE `bug_reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `chat_history`
--
ALTER TABLE `chat_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=82;

--
-- AUTO_INCREMENT for table `counselors`
--
ALTER TABLE `counselors`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `counselor_feedback`
--
ALTER TABLE `counselor_feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `daily_tasks`
--
ALTER TABLE `daily_tasks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=76;

--
-- AUTO_INCREMENT for table `emotion_logs`
--
ALTER TABLE `emotion_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `forum_guidelines`
--
ALTER TABLE `forum_guidelines`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `forum_posts`
--
ALTER TABLE `forum_posts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `forum_replies`
--
ALTER TABLE `forum_replies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `forum_reports`
--
ALTER TABLE `forum_reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `forum_topics`
--
ALTER TABLE `forum_topics`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `game_scores`
--
ALTER TABLE `game_scores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `journal_entries`
--
ALTER TABLE `journal_entries`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `resources`
--
ALTER TABLE `resources`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `volunteer_feedback`
--
ALTER TABLE `volunteer_feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `emotion_logs`
--
ALTER TABLE `emotion_logs`
  ADD CONSTRAINT `emotion_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `forum_posts`
--
ALTER TABLE `forum_posts`
  ADD CONSTRAINT `forum_posts_ibfk_1` FOREIGN KEY (`topic_id`) REFERENCES `forum_topics` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
