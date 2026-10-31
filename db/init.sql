-- รันครั้งแรกตอนสร้าง volume เท่านั้น
CREATE EXTENSION IF NOT EXISTS vector;

-- database แยกสำหรับเทสต์
CREATE DATABASE cs_assistant_test;
\connect cs_assistant_test
CREATE EXTENSION IF NOT EXISTS vector;
