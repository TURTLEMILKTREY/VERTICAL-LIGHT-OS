-- PRODUCTION HOSPITAL INTELLIGENCE DATABASE SCHEMA
-- Critical for real-world hospital consultancy operations
-- Ensures 100% success rate through comprehensive data structure

-- ============================================================================
-- CORE HOSPITAL MASTER DATA
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Hospital master table
CREATE TABLE hospitals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_id VARCHAR(50) UNIQUE NOT NULL,
    hospital_name VARCHAR(255) NOT NULL,
    
    -- Basic Information
    established_year INTEGER CHECK (established_year >= 1800 AND established_year <= 2030),
    hospital_type VARCHAR(50) NOT NULL CHECK (hospital_type IN ('acute_care', 'specialty', 'super_specialty', 'critical_access', 'teaching', 'government', 'community')),
    ownership_type VARCHAR(50) NOT NULL CHECK (ownership_type IN ('private', 'government', 'trust', 'corporate_chain', 'public_private_partnership', 'charitable')),
    bed_count INTEGER NOT NULL CHECK (bed_count > 0),
    
    -- Location Details
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('tier_1', 'tier_2', 'tier_3', 'tier_4')),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Technology & Infrastructure  
    technology_maturity VARCHAR(50) NOT NULL DEFAULT 'basic' CHECK (technology_maturity IN ('basic', 'intermediate', 'advanced', 'cutting_edge')),
    has_emr BOOLEAN DEFAULT FALSE,
    has_his BOOLEAN DEFAULT FALSE,
    has_lis BOOLEAN DEFAULT FALSE,
    has_ris BOOLEAN DEFAULT FALSE,
    has_pacs BOOLEAN DEFAULT FALSE,
    emr_vendor VARCHAR(100),
    
    -- Accreditations
    accreditations TEXT[] DEFAULT '{}',
    nabh_level VARCHAR(30) CHECK (nabh_level IN ('entry', 'full', 'nursing_excellence') OR nabh_level IS NULL),
    jci_accredited BOOLEAN DEFAULT FALSE,
    iso_certifications TEXT[] DEFAULT '{}',
    
    -- Metadata
    data_quality_score DECIMAL(3,2) CHECK (data_quality_score BETWEEN 0 AND 1),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_pincode_format CHECK (pincode ~ '^[0-9]{6}$'),
    CONSTRAINT reasonable_bed_count CHECK (bed_count BETWEEN 10 AND 5000)
);

-- ============================================================================
-- FINANCIAL PERFORMANCE METRICS  
-- ============================================================================

CREATE TABLE hospital_financial_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_id UUID NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    
    -- Core Financial Data
    annual_revenue DECIMAL(15,2) NOT NULL CHECK (annual_revenue >= 0),
    operating_margin DECIMAL(5,2) NOT NULL CHECK (operating_margin BETWEEN -100 AND 100),
    ebitda_margin DECIMAL(5,2) CHECK (ebitda_margin BETWEEN -100 AND 100),
    net_margin DECIMAL(5,2) CHECK (net_margin BETWEEN -100 AND 100),
    
    -- Capital Structure
    debt_to_equity DECIMAL(5,2) CHECK (debt_to_equity >= 0),
    working_capital_days INTEGER CHECK (working_capital_days >= 0),
    capex_percentage DECIMAL(3,2) CHECK (capex_percentage BETWEEN 0 AND 1),
    
    -- Revenue Cycle Metrics
    days_in_ar INTEGER CHECK (days_in_ar >= 0 AND days_in_ar <= 365),
    collection_rate DECIMAL(3,2) CHECK (collection_rate BETWEEN 0 AND 1),
    denial_rate DECIMAL(3,2) CHECK (denial_rate BETWEEN 0 AND 1),
    bad_debt_percentage DECIMAL(3,2) CHECK (bad_debt_percentage BETWEEN 0 AND 1),
    
    -- Payer Mix (Indian Context)
    government_scheme_percentage DECIMAL(3,2) CHECK (government_scheme_percentage BETWEEN 0 AND 1),
    private_insurance_percentage DECIMAL(3,2) CHECK (private_insurance_percentage BETWEEN 0 AND 1),
    corporate_insurance_percentage DECIMAL(3,2) CHECK (corporate_insurance_percentage BETWEEN 0 AND 1),
    self_pay_percentage DECIMAL(3,2) CHECK (self_pay_percentage BETWEEN 0 AND 1),
    
    -- Reporting Context
    fiscal_year VARCHAR(20) NOT NULL,
    reporting_period VARCHAR(20) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    
    -- Data Quality
    data_completeness_score DECIMAL(3,2) CHECK (data_completeness_score BETWEEN 0 AND 1),
    data_source VARCHAR(100),
    validation_status VARCHAR(20) DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'rejected', 'needs_review')),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Business Logic Constraints
    CONSTRAINT payer_mix_totals CHECK (
        COALESCE(government_scheme_percentage, 0) + 
        COALESCE(private_insurance_percentage, 0) + 
        COALESCE(corporate_insurance_percentage, 0) + 
        COALESCE(self_pay_percentage, 0) <= 1.01  -- Allow small rounding errors
    )
);

-- ============================================================================
-- OPERATIONAL PERFORMANCE METRICS
-- ============================================================================

CREATE TABLE hospital_operational_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_id UUID NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    
    -- Capacity Metrics
    bed_count INTEGER NOT NULL CHECK (bed_count > 0),
    occupancy_rate DECIMAL(3,2) NOT NULL CHECK (occupancy_rate BETWEEN 0 AND 1),
    average_length_of_stay DECIMAL(4,1) CHECK (average_length_of_stay > 0),
    bed_turnover_rate DECIMAL(4,1) CHECK (bed_turnover_rate >= 0),
    
    -- Emergency Department
    ed_visits_annual INTEGER CHECK (ed_visits_annual >= 0),
    door_to_doc_time_minutes INTEGER CHECK (door_to_doc_time_minutes >= 0 AND door_to_doc_time_minutes <= 300),
    lwbs_rate DECIMAL(3,2) CHECK (lwbs_rate BETWEEN 0 AND 1),  -- Left Without Being Seen
    ed_average_los_hours DECIMAL(4,1) CHECK (ed_average_los_hours >= 0),
    
    -- Operating Room Efficiency
    or_count INTEGER CHECK (or_count >= 0),
    or_utilization_rate DECIMAL(3,2) CHECK (or_utilization_rate BETWEEN 0 AND 1),
    or_turnover_time_minutes INTEGER CHECK (or_turnover_time_minutes >= 0 AND or_turnover_time_minutes <= 300),
    surgery_cancellation_rate DECIMAL(3,2) CHECK (surgery_cancellation_rate BETWEEN 0 AND 1),
    
    -- Staffing Ratios
    doctor_to_bed_ratio DECIMAL(4,3) CHECK (doctor_to_bed_ratio >= 0),
    nurse_to_bed_ratio DECIMAL(4,2) CHECK (nurse_to_bed_ratio >= 0),
    staff_turnover_rate DECIMAL(3,2) CHECK (staff_turnover_rate BETWEEN 0 AND 1),
    
    -- Reporting Context
    reporting_period VARCHAR(20) NOT NULL,
    data_completeness_score DECIMAL(3,2) CHECK (data_completeness_score BETWEEN 0 AND 1),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- QUALITY & SAFETY METRICS
-- ============================================================================

CREATE TABLE hospital_quality_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_id UUID NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    
    -- Patient Safety Indicators
    hospital_acquired_infection_rate DECIMAL(4,3) CHECK (hospital_acquired_infection_rate BETWEEN 0 AND 1),
    medication_error_rate DECIMAL(4,3) CHECK (medication_error_rate BETWEEN 0 AND 1),
    patient_fall_rate DECIMAL(4,3) CHECK (patient_fall_rate BETWEEN 0 AND 1),
    pressure_ulcer_rate DECIMAL(4,3) CHECK (pressure_ulcer_rate BETWEEN 0 AND 1),
    
    -- Clinical Outcomes
    mortality_rate DECIMAL(4,3) CHECK (mortality_rate BETWEEN 0 AND 1),
    readmission_rate_30_day DECIMAL(3,2) CHECK (readmission_rate_30_day BETWEEN 0 AND 1),
    surgical_site_infection_rate DECIMAL(4,3) CHECK (surgical_site_infection_rate BETWEEN 0 AND 1),
    
    -- Patient Satisfaction (0-100 scale)
    overall_satisfaction_score DECIMAL(5,2) CHECK (overall_satisfaction_score BETWEEN 0 AND 100),
    communication_score DECIMAL(5,2) CHECK (communication_score BETWEEN 0 AND 100),
    cleanliness_score DECIMAL(5,2) CHECK (cleanliness_score BETWEEN 0 AND 100),
    pain_management_score DECIMAL(5,2) CHECK (pain_management_score BETWEEN 0 AND 100),
    
    -- Accreditation Scores
    nabh_score DECIMAL(6,2) CHECK (nabh_score BETWEEN 0 AND 1000),
    jci_accredited BOOLEAN DEFAULT FALSE,
    
    -- Reporting Context
    reporting_period VARCHAR(20) NOT NULL,
    data_completeness_score DECIMAL(3,2) CHECK (data_completeness_score BETWEEN 0 AND 1),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- CONSULTING ANALYSIS RESULTS
-- ============================================================================

CREATE TABLE hospital_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_id UUID NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    
    -- Analysis Context
    analysis_type VARCHAR(50) NOT NULL CHECK (analysis_type IN ('comprehensive', 'financial', 'operational', 'quality', 'benchmarking')),
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Hospital Lifecycle Analysis
    hospital_age INTEGER NOT NULL CHECK (hospital_age >= 0),
    lifecycle_stage VARCHAR(50) NOT NULL CHECK (lifecycle_stage IN ('STARTUP', 'GROWTH', 'MATURITY', 'OPTIMIZATION', 'TRANSFORMATION')),
    benchmark_target DECIMAL(5,2) NOT NULL,
    growth_velocity VARCHAR(50) NOT NULL CHECK (growth_velocity IN ('DECLINING', 'STABLE', 'GROWING', 'ACCELERATING')),
    
    -- Confidence & Quality Metrics
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    data_quality_score DECIMAL(3,2) CHECK (data_quality_score BETWEEN 0 AND 1),
    processing_duration DECIMAL(10,3) CHECK (processing_duration >= 0),
    
    -- Structured Analysis Results
    financial_analysis JSONB,
    operational_analysis JSONB,
    quality_analysis JSONB,
    benchmark_analysis JSONB,
    strategic_recommendations JSONB,
    implementation_roadmap JSONB,
    risk_assessment JSONB,
    
    -- Performance Scores
    overall_performance_score DECIMAL(5,2) CHECK (overall_performance_score BETWEEN 0 AND 100),
    financial_performance_score DECIMAL(5,2) CHECK (financial_performance_score BETWEEN 0 AND 100),
    operational_performance_score DECIMAL(5,2) CHECK (operational_performance_score BETWEEN 0 AND 100),
    quality_performance_score DECIMAL(5,2) CHECK (quality_performance_score BETWEEN 0 AND 100),
    
    -- Consultant Information
    consultant_id VARCHAR(50),
    analysis_version VARCHAR(20) DEFAULT 'v1.0',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- BENCHMARKING DATA
-- ============================================================================

CREATE TABLE hospital_benchmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_id UUID NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    
    -- Peer Group Definition
    peer_group_criteria JSONB NOT NULL,
    peer_hospital_count INTEGER CHECK (peer_hospital_count > 0),
    
    -- Performance Percentiles
    overall_percentile DECIMAL(5,2) CHECK (overall_percentile BETWEEN 0 AND 100),
    financial_percentile DECIMAL(5,2) CHECK (financial_percentile BETWEEN 0 AND 100),
    operational_percentile DECIMAL(5,2) CHECK (operational_percentile BETWEEN 0 AND 100),
    quality_percentile DECIMAL(5,2) CHECK (quality_percentile BETWEEN 0 AND 100),
    
    -- Benchmark Metrics
    metric_comparisons JSONB,
    performance_gaps JSONB,
    improvement_opportunities JSONB,
    
    -- Benchmark Context
    benchmark_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_sources TEXT[],
    confidence_level DECIMAL(3,2) CHECK (confidence_level BETWEEN 0 AND 1),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- AUDIT TRAIL FOR COMPLIANCE
-- ============================================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Audit Information
    user_id VARCHAR(100),
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id UUID,
    
    -- Change Details
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Hospital indexes
CREATE INDEX idx_hospitals_type_tier ON hospitals(hospital_type, tier);
CREATE INDEX idx_hospitals_city_state ON hospitals(city, state);
CREATE INDEX idx_hospitals_bed_count ON hospitals(bed_count);
CREATE INDEX idx_hospitals_active ON hospitals(is_active) WHERE is_active = TRUE;

-- Financial metrics indexes
CREATE INDEX idx_financial_hospital_period ON hospital_financial_metrics(hospital_id, fiscal_year);
CREATE INDEX idx_financial_revenue ON hospital_financial_metrics(annual_revenue);
CREATE INDEX idx_financial_margin ON hospital_financial_metrics(operating_margin);
CREATE INDEX idx_financial_quality ON hospital_financial_metrics(data_completeness_score);

-- Operational metrics indexes
CREATE INDEX idx_operational_hospital_period ON hospital_operational_metrics(hospital_id, reporting_period);
CREATE INDEX idx_operational_occupancy ON hospital_operational_metrics(occupancy_rate);
CREATE INDEX idx_operational_bed_count ON hospital_operational_metrics(bed_count);

-- Quality metrics indexes
CREATE INDEX idx_quality_hospital_period ON hospital_quality_metrics(hospital_id, reporting_period);
CREATE INDEX idx_quality_satisfaction ON hospital_quality_metrics(overall_satisfaction_score);
CREATE INDEX idx_quality_safety ON hospital_quality_metrics(hospital_acquired_infection_rate);

-- Analysis indexes
CREATE INDEX idx_analyses_hospital_date ON hospital_analyses(hospital_id, analysis_date DESC);
CREATE INDEX idx_analyses_lifecycle ON hospital_analyses(lifecycle_stage);
CREATE INDEX idx_analyses_confidence ON hospital_analyses(confidence_score);
CREATE INDEX idx_analyses_performance ON hospital_analyses(overall_performance_score);

-- Benchmark indexes
CREATE INDEX idx_benchmarks_hospital_date ON hospital_benchmarks(hospital_id, benchmark_date DESC);
CREATE INDEX idx_benchmarks_percentile ON hospital_benchmarks(overall_percentile);

-- Audit indexes
CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_user_action ON audit_logs(user_id, action);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(created_at DESC);

-- ============================================================================
-- DATA VALIDATION FUNCTIONS
-- ============================================================================

-- Function to validate financial data completeness
CREATE OR REPLACE FUNCTION validate_financial_completeness(
    p_hospital_id UUID,
    p_fiscal_year VARCHAR(20)
) RETURNS DECIMAL(3,2) AS $$
DECLARE
    completeness_score DECIMAL(3,2);
BEGIN
    SELECT 
        (
            CASE WHEN annual_revenue IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN operating_margin IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN days_in_ar IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN collection_rate IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN government_scheme_percentage IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN private_insurance_percentage IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN self_pay_percentage IS NOT NULL THEN 1 ELSE 0 END
        )::DECIMAL / 7.0
    INTO completeness_score
    FROM hospital_financial_metrics
    WHERE hospital_id = p_hospital_id AND fiscal_year = p_fiscal_year
    ORDER BY created_at DESC
    LIMIT 1;
    
    RETURN COALESCE(completeness_score, 0.0);
END;
$$ LANGUAGE plpgsql;

-- Function to calculate hospital performance score
CREATE OR REPLACE FUNCTION calculate_hospital_performance_score(
    p_hospital_id UUID
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    financial_score DECIMAL(5,2) := 0;
    operational_score DECIMAL(5,2) := 0;
    quality_score DECIMAL(5,2) := 0;
    overall_score DECIMAL(5,2);
BEGIN
    -- Calculate financial performance (0-100)
    SELECT 
        LEAST(100, GREATEST(0, 
            (operating_margin * 100 + 50) * 
            (CASE WHEN collection_rate IS NOT NULL THEN collection_rate ELSE 0.85 END)
        ))
    INTO financial_score
    FROM hospital_financial_metrics 
    WHERE hospital_id = p_hospital_id 
    ORDER BY created_at DESC 
    LIMIT 1;
    
    -- Calculate operational performance (0-100)
    SELECT 
        LEAST(100, GREATEST(0,
            (occupancy_rate * 100 + 
             CASE WHEN door_to_doc_time_minutes IS NOT NULL 
                  THEN (30 - LEAST(door_to_doc_time_minutes, 30)) * 2 
                  ELSE 0 END) / 2
        ))
    INTO operational_score
    FROM hospital_operational_metrics 
    WHERE hospital_id = p_hospital_id 
    ORDER BY created_at DESC 
    LIMIT 1;
    
    -- Calculate quality performance (0-100)
    SELECT 
        LEAST(100, GREATEST(0,
            COALESCE(overall_satisfaction_score, 75) * 0.6 +
            (1 - COALESCE(hospital_acquired_infection_rate, 0.03)) * 40
        ))
    INTO quality_score
    FROM hospital_quality_metrics 
    WHERE hospital_id = p_hospital_id 
    ORDER BY created_at DESC 
    LIMIT 1;
    
    -- Weighted average
    overall_score := (
        COALESCE(financial_score, 50) * 0.4 +
        COALESCE(operational_score, 50) * 0.35 +
        COALESCE(quality_score, 50) * 0.25
    );
    
    RETURN overall_score;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS FOR DATA INTEGRITY
-- ============================================================================

-- Update timestamps
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply timestamp triggers
CREATE TRIGGER hospitals_updated_at 
    BEFORE UPDATE ON hospitals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER financial_metrics_updated_at 
    BEFORE UPDATE ON hospital_financial_metrics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER operational_metrics_updated_at 
    BEFORE UPDATE ON hospital_operational_metrics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER quality_metrics_updated_at 
    BEFORE UPDATE ON hospital_quality_metrics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER analyses_updated_at 
    BEFORE UPDATE ON hospital_analyses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Audit trail trigger
CREATE OR REPLACE FUNCTION log_audit_trail()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        action, table_name, record_id, old_values, new_values
    ) VALUES (
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE to_jsonb(OLD) END,
        CASE WHEN TG_OP = 'DELETE' THEN NULL ELSE to_jsonb(NEW) END
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to critical tables
CREATE TRIGGER hospitals_audit 
    AFTER INSERT OR UPDATE OR DELETE ON hospitals 
    FOR EACH ROW EXECUTE FUNCTION log_audit_trail();

CREATE TRIGGER financial_metrics_audit 
    AFTER INSERT OR UPDATE OR DELETE ON hospital_financial_metrics 
    FOR EACH ROW EXECUTE FUNCTION log_audit_trail();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Comprehensive hospital dashboard view
CREATE VIEW hospital_dashboard AS
SELECT 
    h.id,
    h.hospital_id,
    h.hospital_name,
    h.hospital_type,
    h.tier,
    h.city,
    h.state,
    h.bed_count,
    h.established_year,
    (2025 - h.established_year) as hospital_age,
    
    -- Latest financial metrics
    f.annual_revenue,
    f.operating_margin,
    f.collection_rate,
    f.fiscal_year,
    
    -- Latest operational metrics  
    o.occupancy_rate,
    o.average_length_of_stay,
    o.door_to_doc_time_minutes,
    o.reporting_period as operational_period,
    
    -- Latest quality metrics
    q.overall_satisfaction_score,
    q.hospital_acquired_infection_rate,
    q.nabh_score,
    
    -- Performance score
    calculate_hospital_performance_score(h.id) as performance_score,
    
    h.updated_at as last_updated
    
FROM hospitals h
LEFT JOIN LATERAL (
    SELECT * FROM hospital_financial_metrics 
    WHERE hospital_id = h.id 
    ORDER BY created_at DESC 
    LIMIT 1
) f ON true
LEFT JOIN LATERAL (
    SELECT * FROM hospital_operational_metrics 
    WHERE hospital_id = h.id 
    ORDER BY created_at DESC 
    LIMIT 1
) o ON true
LEFT JOIN LATERAL (
    SELECT * FROM hospital_quality_metrics 
    WHERE hospital_id = h.id 
    ORDER BY created_at DESC 
    LIMIT 1
) q ON true
WHERE h.is_active = true;

-- ============================================================================
-- SAMPLE DATA POPULATION (FOR TESTING)
-- ============================================================================

-- Insert sample hospitals for testing
INSERT INTO hospitals (
    hospital_id, hospital_name, hospital_type, ownership_type, bed_count,
    address, city, state, pincode, tier, established_year
) VALUES 
    ('HOSP_001', 'Mumbai Medical Center', 'super_specialty', 'private', 250, 
     'Bandra West, Mumbai', 'Mumbai', 'Maharashtra', '400050', 'tier_1', 2010),
    ('HOSP_002', 'Chennai Cardiology Institute', 'specialty', 'trust', 150,
     'T. Nagar, Chennai', 'Chennai', 'Tamil Nadu', '600017', 'tier_1', 2005),
    ('HOSP_003', 'Delhi Community Hospital', 'community', 'government', 100,
     'Lajpat Nagar, New Delhi', 'New Delhi', 'Delhi', '110024', 'tier_1', 1995);

-- Insert sample financial metrics
INSERT INTO hospital_financial_metrics (
    hospital_id, annual_revenue, operating_margin, fiscal_year
) VALUES 
    ((SELECT id FROM hospitals WHERE hospital_id = 'HOSP_001'), 500000000.00, 12.5, 'FY2024-25'),
    ((SELECT id FROM hospitals WHERE hospital_id = 'HOSP_002'), 350000000.00, 15.2, 'FY2024-25'),
    ((SELECT id FROM hospitals WHERE hospital_id = 'HOSP_003'), 120000000.00, 8.5, 'FY2024-25');

-- ============================================================================
-- GRANTS AND PERMISSIONS
-- ============================================================================

-- Create roles for different access levels
-- These would be customized based on your deployment requirements

-- Grant permissions (example)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO hospital_analyst;
-- GRANT SELECT ON hospital_dashboard TO hospital_viewer;

COMMENT ON DATABASE hospital_intelligence IS 'Production database for VERTICAL LIGHT OS Hospital Intelligence System';