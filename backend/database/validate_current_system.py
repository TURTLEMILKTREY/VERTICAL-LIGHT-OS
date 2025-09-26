#!/usr/bin/env python3
"""
Hospital Data Validation & Enhancement Strategy
==============================================

PROFESSIONAL ASSESSMENT: Current system validation before ma            await conn.execute(create_table_sql)
            
            print("PASS: Created hospital master table successfully")
            return True
            
        except Exception as e:
            print(f"FAIL: Failed to create master table: {e}")
            return Falseges
Focus on proving the existing system works with real data
"""

import asyncio
import asyncpg
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List

class CurrentSystemValidator:
    """Validate and enhance existing database structure"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    async def assess_current_data_quality(self) -> Dict[str, Any]:
        """Assess quality of current hospital data"""
        conn = await asyncpg.connect(self.connection_string)
        
        try:
            # Get current data
            records = await conn.fetch("""
                SELECT 
                    hospital_name,
                    lifecycle_stage,
                    confidence_score,
                    analysis_results,
                    created_at
                FROM hospital_analyses
                ORDER BY created_at DESC
            """)
            
            assessment = {
                "total_hospitals": len(records),
                "data_quality_issues": [],
                "missing_critical_fields": [],
                "recommendations": []
            }
            
            for record in records:
                analysis_data = record['analysis_results']
                
                # Check for critical missing fields
                critical_fields = [
                    'financial_analysis', 'operational_analysis', 
                    'quality_analysis', 'strategic_recommendations'
                ]
                
                missing_fields = []
                for field in critical_fields:
                    if field not in analysis_data:
                        missing_fields.append(field)
                
                if missing_fields:
                    assessment["missing_critical_fields"].extend(missing_fields)
                
                # Check data completeness
                if record['confidence_score'] < 0.7:
                    assessment["data_quality_issues"].append(
                        f"Low confidence score ({record['confidence_score']}) for {record['hospital_name']}"
                    )
            
            # Generate recommendations
            if len(records) < 5:
                assessment["recommendations"].append(
                    "CRITICAL: Need at least 5 hospitals for meaningful benchmarking"
                )
            
            if assessment["missing_critical_fields"]:
                assessment["recommendations"].append(
                    "Enhance JSONB structure with missing analysis components"
                )
            
            return assessment
            
        finally:
            await conn.close()
    
    async def enhance_current_structure(self) -> bool:
        """Enhance current structure without breaking changes"""
        conn = await asyncpg.connect(self.connection_string)
        
        try:
            # Add structured analysis columns to existing table
            enhancement_sql = """
            -- Add structured columns for better querying (keeping JSONB for flexibility)
            ALTER TABLE hospital_analyses 
            ADD COLUMN IF NOT EXISTS financial_score DECIMAL(5,2),
            ADD COLUMN IF NOT EXISTS operational_score DECIMAL(5,2),
            ADD COLUMN IF NOT EXISTS quality_score DECIMAL(5,2),
            ADD COLUMN IF NOT EXISTS overall_score DECIMAL(5,2),
            ADD COLUMN IF NOT EXISTS data_completeness DECIMAL(3,2),
            ADD COLUMN IF NOT EXISTS hospital_tier VARCHAR(20),
            ADD COLUMN IF NOT EXISTS hospital_type VARCHAR(50),
            ADD COLUMN IF NOT EXISTS annual_revenue DECIMAL(15,2),
            ADD COLUMN IF NOT EXISTS bed_count INTEGER;
            
            -- Add performance indexes
            CREATE INDEX IF NOT EXISTS idx_hospital_analyses_overall_score 
            ON hospital_analyses(overall_score DESC);
            
            CREATE INDEX IF NOT EXISTS idx_hospital_analyses_tier_type 
            ON hospital_analyses(hospital_tier, hospital_type);
            """
            
            await conn.execute(enhancement_sql)
            
            # Update existing records with extracted values
            update_sql = """
            UPDATE hospital_analyses 
            SET 
                financial_score = COALESCE((analysis_results->>'financial_score')::DECIMAL, 0),
                operational_score = COALESCE((analysis_results->>'operational_score')::DECIMAL, 0),
                overall_score = COALESCE((analysis_results->>'overall_performance_score')::DECIMAL, 0),
                data_completeness = COALESCE((analysis_results->>'data_completeness')::DECIMAL, confidence_score)
            WHERE overall_score IS NULL;
            """
            
            await conn.execute(update_sql)
            
            print("PASS: Enhanced current database structure successfully")
            return True
            
        except Exception as e:
            print(f"FAIL: Failed to enhance structure: {e}")
            return False
        finally:
            await conn.close()
    
    async def create_hospital_master_table(self) -> bool:
        """Create minimal hospital master table for better organization"""
        conn = await asyncpg.connect(self.connection_string)
        
        try:
            master_table_sql = """
            -- Create hospital master table (separate from analyses)
            CREATE TABLE IF NOT EXISTS hospital_master (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                hospital_id VARCHAR(50) UNIQUE NOT NULL,
                hospital_name VARCHAR(255) NOT NULL,
                city VARCHAR(100),
                state VARCHAR(100),
                tier VARCHAR(20) CHECK (tier IN ('tier_1', 'tier_2', 'tier_3', 'tier_4')),
                hospital_type VARCHAR(50),
                bed_count INTEGER CHECK (bed_count > 0),
                established_year INTEGER,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Link analyses to master table
            ALTER TABLE hospital_analyses 
            ADD COLUMN IF NOT EXISTS hospital_master_id UUID REFERENCES hospital_master(id);
            
            CREATE INDEX IF NOT EXISTS idx_hospital_master_name ON hospital_master(hospital_name);
            CREATE INDEX IF NOT EXISTS idx_hospital_master_tier ON hospital_master(tier);
            """
            
            await conn.execute(master_table_sql)
            
            # Populate with existing data
            populate_sql = """
            INSERT INTO hospital_master (hospital_id, hospital_name, tier, hospital_type)
            SELECT 
                UPPER(REPLACE(hospital_name, ' ', '_')) as hospital_id,
                hospital_name,
                COALESCE(hospital_tier, 'tier_1'),
                COALESCE(hospital_type, 'multi_specialty')
            FROM hospital_analyses
            ON CONFLICT (hospital_id) DO NOTHING;
            
            -- Link existing analyses
            UPDATE hospital_analyses 
            SET hospital_master_id = (
                SELECT id FROM hospital_master 
                WHERE hospital_master.hospital_name = hospital_analyses.hospital_name
            )
            WHERE hospital_master_id IS NULL;
            """
            
            await conn.execute(populate_sql)
            
            print("✅ Created hospital master table successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create master table: {e}")
            return False
        finally:
            await conn.close()

async def validate_current_system():
    """Main validation function"""
    DATABASE_URL = 'postgresql://postgres:testpass@localhost:5432/hospital_intelligence'
    
    validator = CurrentSystemValidator(DATABASE_URL)
    
    print("VALIDATING CURRENT SYSTEM")
    print("=" * 50)
    
    # Assess current data quality
    assessment = await validator.assess_current_data_quality()
    
    print(f"Current hospitals: {assessment['total_hospitals']}")
    print(f"Data quality issues: {len(assessment['data_quality_issues'])}")
    print(f"Missing fields: {set(assessment['missing_critical_fields'])}")
    
    print("\n📋 RECOMMENDATIONS:")
    for rec in assessment['recommendations']:
        print(f"  • {rec}")
    
    # Enhance current structure
    print(f"\n🔧 ENHANCING CURRENT STRUCTURE")
    structure_enhanced = await validator.enhance_current_structure()
    
    # Create master table
    print(f"CREATING HOSPITAL MASTER TABLE") 
    master_created = await validator.create_hospital_master_table()
    
    print(f"\nVALIDATION SUMMARY")
    print(f"Structure Enhanced: {'PASS' if structure_enhanced else 'FAIL'}")
    print(f"Master Table Created: {'PASS' if master_created else 'FAIL'}")
    
    if structure_enhanced and master_created:
        print(f"\nNEXT STEPS:")
        print(f"  1. Add 4+ more hospitals for meaningful benchmarking")
        print(f"  2. Enhance data collection for financial/operational metrics")
        print(f"  3. Implement peer comparison algorithms")
        print(f"  4. THEN consider full schema migration")
        
        return True
    else:
        print(f"\nVALIDATION FAILED - Address issues before proceeding")
        return False

if __name__ == "__main__":
    asyncio.run(validate_current_system())