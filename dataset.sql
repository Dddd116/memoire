CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

INSERT INTO utilisateurs (username, password)
VALUES ('admin', 'admin123');

SELECT * FROM utilisateurs;

CREATE TABLE alertes (
    id SERIAL PRIMARY KEY,
    sensor_name VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(10),
    status VARCHAR(20),  -- 'critical', 'warning'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    user_ack VARCHAR(50)
);

-- Index performance
CREATE INDEX idx_alertes_status ON alertes(status);
CREATE INDEX idx_alertes_time ON alertes(timestamp);