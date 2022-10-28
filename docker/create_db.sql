CREATE DATABASE IF NOT EXISTS prenacs_test;
GRANT USAGE ON *.* to 'myuser'@localhost identified by 'mypass';
GRANT ALL PRIVILEGES ON `prenacs_test`.* to 'myuser'@localhost;
FLUSH PRIVILEGES;
