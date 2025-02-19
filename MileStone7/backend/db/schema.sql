CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);
CREATE TABLE routing_policies (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    regex_pattern TEXT NOT NULL,
    redirect_model VARCHAR(255) NOT NULL
);
