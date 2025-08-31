-- 사용자 생성 및 권한 부여
CREATE USER 'user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'user'@'%';

-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS vuln;
USE vuln;

-- 권한 새로고침
FLUSH PRIVILEGES;
