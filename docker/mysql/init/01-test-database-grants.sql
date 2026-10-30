-- Runs once when the MySQL volume is created (see docker-compose.yml).
-- Django's test runner creates a separate database named test_<NAME> (here
-- test_conceito_os). The application user needs rights on it to run the tests
-- against MySQL. Rights on other databases are not granted.
GRANT ALL PRIVILEGES ON `test_conceito_os`.* TO 'conceito'@'%';
FLUSH PRIVILEGES;
