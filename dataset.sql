CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

INSERT INTO utilisateurs (username, password)
VALUES ('admin', 'admin123');

SELECT * FROM utilisateurs;
