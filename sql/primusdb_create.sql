create database primusdb;

show databases;

grant all privileges on primusdb.* to ohgiraffers@'%';

show grants for ohgiraffers@'%';

use primusdb;

CREATE TABLE IF NOT EXISTS Region_Info
(
    region_code    		INT AUTO_INCREMENT COMMENT '지역코드',
    province_city    	VARCHAR(20) NOT NULL COMMENT '시도',
    district_city    	VARCHAR(20) COMMENT '군구',
    CONSTRAINT pk_region_code PRIMARY KEY (region_code)
) ENGINE=INNODB COMMENT '지역정보';

CREATE TABLE IF NOT EXISTS EV_Charger
(
    charger_code    	INT AUTO_INCREMENT COMMENT '충전소코드',
    region_code    		INT NOT NULL COMMENT '지역코드',
    charger_count    	INT NOT NULL COMMENT '충전소 개수',
    install_year    	INT NOT NULL COMMENT '설치년도',
    CONSTRAINT pk_charger_code PRIMARY KEY (charger_code),
    CONSTRAINT fk_ev_charger_region_code FOREIGN KEY (region_code) REFERENCES Region_Info (region_code)
) ENGINE=INNODB COMMENT '전기차 충전소';

CREATE TABLE IF NOT EXISTS EV_Registration
(
    region_code    				INT AUTO_INCREMENT COMMENT '지역코드',
    registrtation_count    		INT NOT NULL COMMENT '등록대수',
    CONSTRAINT pk_region_code PRIMARY KEY (region_code),
    CONSTRAINT fk_ev_registration_region_code FOREIGN KEY (region_code) REFERENCES Region_Info (region_code)
) ENGINE=INNODB COMMENT '전기차 등록 현황';

CREATE TABLE IF NOT EXISTS EV_Subsidy
(
    subsidy_code   		INT AUTO_INCREMENT COMMENT '보조금코드',
    region_code    		INT NOT NULL COMMENT '지역코드',
    manufacturer    	VARCHAR(50) NOT NULL COMMENT '제조사',
    model_name    		VARCHAR(50) NOT NULL COMMENT '모델명',
    subsidy_amount    	INT NOT NULL COMMENT '보조금',
    CONSTRAINT pk_subsidy_code PRIMARY KEY (subsidy_code),
    CONSTRAINT fk_ev_subsidy_region_code FOREIGN KEY (region_code) REFERENCES Region_Info (region_code)
) ENGINE=INNODB COMMENT '전기차 보조금 정보';

CREATE TABLE IF NOT EXISTS FAQ
(
    faq_code   		INT AUTO_INCREMENT COMMENT '질문코드',
    faq_title    	VARCHAR(100) NOT NULL COMMENT '질문제목',
    faq_answer    	TEXT NOT NULL COMMENT '질문답변',
    CONSTRAINT pk_faq_code PRIMARY KEY (faq_code)
) ENGINE=INNODB COMMENT 'FAQ';