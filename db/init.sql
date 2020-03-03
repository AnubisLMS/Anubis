CREATE DATABASE IF NOT EXISTS `os`;

GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;

SET GLOBAL time_zone = 'America/New_York';
SET time_zone = 'America/New_York';
