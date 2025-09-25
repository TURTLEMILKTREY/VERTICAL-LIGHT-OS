-- Hospital Intelligence Database Schema
-- Production-ready schema for single hospital deployment

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main table for hospital analyses
CREATE TABLE IF NOT EXISTS hospital_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_name VARCHAR(255) NOT NULL,
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    hospital_age INTEGER NOT NULL CHECK (hospital_age >= 0),
    lifecycle_stage VARCHAR(50) NOT NULL CHECK (lifecycle_stage IN ('STARTUP', 'GROWTH', 'EXPANSION', 'MATURITY', 'ESTABLISHED')),
    benchmark_target DECIMAL(5,2) NOT NULL CHECK (benchmark_target >= 0 AND benchmark_target <= 100),
    growth_velocity VARCHAR(50) NOT NULL CHECK (growth_velocity IN ('BREAKTHROUGH', 'ACCELERATING', 'STEADY', 'SLOW', 'DECLINING')),
    analysis_results JSONB NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    processing_duration DECIMAL(10,3) NOT NULL CHECK (processing_duration >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_hospital_analyses_name_date 
ON hospital_analyses(hospital_name, analysis_date DESC);

CREATE INDEX IF NOT EXISTS idx_hospital_analyses_lifecycle 
ON hospital_analyses(lifecycle_stage);

CREATE INDEX IF NOT EXISTS idx_hospital_analyses_created 
ON hospital_analyses(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_hospital_analyses_confidence 
ON hospital_analyses(confidence_score DESC);

-- Table for audit trail (HIPAA compliance)
CREATE TABLE IF NOT EXISTS analysis_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES hospital_analyses(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL CHECK (action IN ('CREATE', 'READ', 'UPDATE', 'DELETE')),
    user_id VARCHAR(255),
    user_role VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    data_accessed JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for audit log
CREATE INDEX IF NOT EXISTS idx_audit_log_analysis_id 
ON analysis_audit_log(analysis_id);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp 
ON analysis_audit_log(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_audit_log_user 
ON analysis_audit_log(user_id, timestamp DESC);

-- Table for hospital configuration (single hospital deployment)
CREATE TABLE IF NOT EXISTS hospital_configuration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_name VARCHAR(255) NOT NULL UNIQUE,
    emr_system VARCHAR(100),
    financial_system VARCHAR(100),
    api_endpoints JSONB,
    compliance_settings JSONB,
    notification_settings JSONB,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for system health monitoring
CREATE TABLE IF NOT EXISTS system_health_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('HEALTHY', 'WARNING', 'ERROR', 'CRITICAL')),
    message TEXT,
    metrics JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for health monitoring
CREATE INDEX IF NOT EXISTS idx_health_log_component_timestamp 
ON system_health_log(component, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_health_log_status 
ON system_health_log(status, timestamp DESC);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_hospital_analyses_updated_at 
    BEFORE UPDATE ON hospital_analyses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hospital_configuration_updated_at 
    BEFORE UPDATE ON hospital_configuration 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function for analysis statistics
CREATE OR REPLACE FUNCTION get_analysis_summary()
RETURNS TABLE (
    total_analyses BIGINT,
    unique_hospitals BIGINT,
    avg_confidence NUMERIC,
    avg_processing_time NUMERIC,
    most_common_stage TEXT,
    last_analysis TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT,
        COUNT(DISTINCT hospital_name)::BIGINT,
        ROUND(AVG(confidence_score), 3),
        ROUND(AVG(processing_duration), 3),
        (
            SELECT lifecycle_stage 
            FROM hospital_analyses 
            GROUP BY lifecycle_stage 
            ORDER BY COUNT(*) DESC 
            LIMIT 1
        ),
        MAX(created_at)
    FROM hospital_analyses;
END;
$$ LANGUAGE plpgsql;

-- View for recent analyses
CREATE OR REPLACE VIEW recent_analyses AS
SELECT 
    id,
    hospital_name,
    analysis_date,
    lifecycle_stage,
    benchmark_target,
    growth_velocity,
    confidence_score,
    processing_duration,
    created_at
FROM hospital_analyses
ORDER BY created_at DESC;

-- View for lifecycle stage distribution
CREATE OR REPLACE VIEW lifecycle_distribution AS
SELECT 
    lifecycle_stage,
    COUNT(*) as analysis_count,
    ROUND(AVG(benchmark_target), 2) as avg_benchmark_target,
    ROUND(AVG(confidence_score), 3) as avg_confidence,
    MIN(created_at) as first_analysis,
    MAX(created_at) as last_analysis
FROM hospital_analyses
GROUP BY lifecycle_stage
ORDER BY analysis_count DESC;

-- Insert default hospital configuration (for single hospital deployment)
INSERT INTO hospital_configuration (
    hospital_name,
    emr_system,
    financial_system,
    api_endpoints,
    compliance_settings,
    notification_settings
) VALUES (
    'Default Hospital',
    'Epic',
    'SAP',
    '{
        "emr_api": "https://hospital.epic.com/api",
        "financial_api": "https://hospital.sap.com/api",
        "notification_webhook": "https://hospital.internal/notifications"
    }'::jsonb,
    '{
        "hipaa_enabled": true,
        "audit_all_access": true,
        "encrypt_sensitive_data": true,
        "data_retention_days": 2555
    }'::jsonb,
    '{
        "email_alerts": true,
        "slack_notifications": false,
        "sms_alerts": false
    }'::jsonb
) ON CONFLICT (hospital_name) DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE hospital_analyses IS 'Main table storing hospital intelligence analysis results';
COMMENT ON TABLE analysis_audit_log IS 'Audit trail for HIPAA compliance and security monitoring';
COMMENT ON TABLE hospital_configuration IS 'Configuration settings for hospital integration';
COMMENT ON TABLE system_health_log IS 'System health and performance monitoring';

COMMENT ON COLUMN hospital_analyses.benchmark_target IS 'Intelligent benchmark target calculated by lifecycle-aware engine';
COMMENT ON COLUMN hospital_analyses.growth_velocity IS 'Growth velocity tier determined by analysis engine';
COMMENT ON COLUMN hospital_analyses.analysis_results IS 'Complete analysis results in JSON format';
COMMENT ON COLUMN hospital_analyses.confidence_score IS 'Analysis confidence score (0.0 to 1.0)';

-- Grant permissions (adjust for production users)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO hospital_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO hospital_app_user;