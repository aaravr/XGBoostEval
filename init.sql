-- Initialize PostgreSQL database for Legal Name Comparison Enterprise System

-- Create database for MLflow
CREATE DATABASE mlflow;
CREATE DATABASE airflow;

-- Connect to main database
\c legal_name_comparison;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL, -- In production, use proper password hashing
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Models table
CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    model_path VARCHAR(500) NOT NULL,
    accuracy DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES users(id)
);

-- Predictions table
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    model_id UUID REFERENCES models(id),
    name1 TEXT NOT NULL,
    name2 TEXT NOT NULL,
    prediction BOOLEAN NOT NULL,
    confidence DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID REFERENCES predictions(id),
    user_correction BOOLEAN NOT NULL,
    confidence_score DECIMAL(5,4),
    feedback_text TEXT,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- Model performance metrics
CREATE TABLE model_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID REFERENCES models(id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,6) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- A/B test experiments
CREATE TABLE ab_experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    model_a_id UUID REFERENCES models(id),
    model_b_id UUID REFERENCES models(id),
    traffic_split DECIMAL(3,2) DEFAULT 0.5,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id)
);

-- A/B test results
CREATE TABLE ab_test_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID REFERENCES ab_experiments(id),
    user_id UUID REFERENCES users(id),
    variant VARCHAR(10) NOT NULL, -- 'a' or 'b'
    prediction_id UUID REFERENCES predictions(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System logs
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level VARCHAR(20) NOT NULL, -- 'INFO', 'WARNING', 'ERROR'
    message TEXT NOT NULL,
    component VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API usage logs
CREATE TABLE api_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_predictions_user_id ON predictions(user_id);
CREATE INDEX idx_predictions_created_at ON predictions(created_at);
CREATE INDEX idx_feedback_prediction_id ON feedback(prediction_id);
CREATE INDEX idx_feedback_processed ON feedback(processed);
CREATE INDEX idx_model_metrics_model_id ON model_metrics(model_id);
CREATE INDEX idx_model_metrics_recorded_at ON model_metrics(recorded_at);
CREATE INDEX idx_api_logs_user_id ON api_logs(user_id);
CREATE INDEX idx_api_logs_created_at ON api_logs(created_at);

-- Create views for common queries
CREATE VIEW daily_predictions AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_predictions,
    AVG(confidence) as avg_confidence,
    COUNT(CASE WHEN prediction = true THEN 1 END) as material_count,
    COUNT(CASE WHEN prediction = false THEN 1 END) as immaterial_count
FROM predictions 
GROUP BY DATE(created_at);

CREATE VIEW model_performance AS
SELECT 
    m.name,
    m.version,
    m.accuracy,
    COUNT(p.id) as prediction_count,
    AVG(p.confidence) as avg_confidence,
    m.created_at
FROM models m
LEFT JOIN predictions p ON m.id = p.model_id
GROUP BY m.id, m.name, m.version, m.accuracy, m.created_at
ORDER BY m.created_at DESC;

CREATE VIEW user_activity AS
SELECT 
    u.email,
    u.name,
    COUNT(p.id) as prediction_count,
    AVG(p.confidence) as avg_confidence,
    MAX(p.created_at) as last_activity
FROM users u
LEFT JOIN predictions p ON u.id = p.user_id
GROUP BY u.id, u.email, u.name
ORDER BY prediction_count DESC;

-- Insert default admin user (password: admin123)
INSERT INTO users (email, name, password, role) 
VALUES ('admin@company.com', 'System Administrator', 'admin123', 'admin');

-- Insert sample data for testing
INSERT INTO users (email, name, password, role) 
VALUES 
    ('user1@company.com', 'John Doe', 'password123', 'user'),
    ('user2@company.com', 'Jane Smith', 'password123', 'user'),
    ('analyst@company.com', 'Data Analyst', 'password123', 'analyst');

-- Create functions for common operations
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to get model statistics
CREATE OR REPLACE FUNCTION get_model_stats(model_uuid UUID)
RETURNS TABLE(
    total_predictions BIGINT,
    avg_confidence DECIMAL,
    material_count BIGINT,
    immaterial_count BIGINT,
    accuracy DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(p.id)::BIGINT as total_predictions,
        AVG(p.confidence) as avg_confidence,
        COUNT(CASE WHEN p.prediction = true THEN 1 END)::BIGINT as material_count,
        COUNT(CASE WHEN p.prediction = false THEN 1 END)::BIGINT as immaterial_count,
        CASE 
            WHEN COUNT(p.id) > 0 THEN 
                COUNT(CASE WHEN p.prediction = true THEN 1 END)::DECIMAL / COUNT(p.id)::DECIMAL
            ELSE 0 
        END as accuracy
    FROM predictions p
    WHERE p.model_id = model_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function to get user activity summary
CREATE OR REPLACE FUNCTION get_user_activity_summary(days INTEGER DEFAULT 30)
RETURNS TABLE(
    user_email VARCHAR,
    user_name VARCHAR,
    prediction_count BIGINT,
    avg_confidence DECIMAL,
    last_activity TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.email as user_email,
        u.name as user_name,
        COUNT(p.id)::BIGINT as prediction_count,
        AVG(p.confidence) as avg_confidence,
        MAX(p.created_at) as last_activity
    FROM users u
    LEFT JOIN predictions p ON u.id = p.user_id
    WHERE p.created_at >= CURRENT_TIMESTAMP - INTERVAL '1 day' * days
    GROUP BY u.id, u.email, u.name
    ORDER BY prediction_count DESC;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres; 