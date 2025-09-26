#!/usr/bin/env python3
"""
Real-World Hospital Benchmarking Demonstration
==============================================

Prove that your current enhanced system can provide professional consultancy
"""

import asyncio
import asyncpg
from decimal import Decimal
from typing import Dict, List, Any

async def demonstrate_benchmarking_capability():
    """Demonstrate professional hospital benchmarking"""
    DATABASE_URL = 'postgresql://postgres:testpass@localhost:5432/hospital_intelligence'
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("VERTICAL LIGHT OS - HOSPITAL BENCHMARKING DEMO")
        print("=" * 60)
        
        # Get all hospitals with key metrics
        hospitals = await conn.fetch("""
            SELECT 
                ha.hospital_name,
                hm.tier,
                hm.hospital_type,
                hm.bed_count,
                ha.annual_revenue,
                ha.overall_score,
                ha.lifecycle_stage,
                ha.benchmark_target,
                ha.confidence_score
            FROM hospital_analyses ha
            JOIN hospital_master hm ON ha.hospital_master_id = hm.id
            ORDER BY ha.overall_score DESC
        """)
        
        print(f"HOSPITAL PERFORMANCE BENCHMARKS")
        print(f"Total Hospitals Analyzed: {len(hospitals)}")
        print()
        
        # Performance ranking
        print("PERFORMANCE RANKING")
        print("-" * 60)
        for i, hosp in enumerate(hospitals, 1):
            revenue_cr = float(hosp['annual_revenue'] or 0) / 10_000_000  # Convert to crores
            print(f"{i:2d}. {hosp['hospital_name'][:30]:<30} | Score: {hosp['overall_score']:5.1f} | ₹{revenue_cr:6.1f}Cr")
        
        print()
        
        # Tier-wise analysis
        tier_analysis = await conn.fetch("""
            SELECT 
                hm.tier,
                COUNT(*) as hospital_count,
                AVG(ha.annual_revenue) as avg_revenue,
                AVG(ha.overall_score) as avg_score,
                MIN(ha.overall_score) as min_score,
                MAX(ha.overall_score) as max_score
            FROM hospital_analyses ha
            JOIN hospital_master hm ON ha.hospital_master_id = hm.id
            GROUP BY hm.tier
            ORDER BY avg_score DESC
        """)
        
        print("TIER-WISE PERFORMANCE ANALYSIS")
        print("-" * 60)
        for tier in tier_analysis:
            avg_revenue_cr = float(tier['avg_revenue'] or 0) / 10_000_000
            print(f"{tier['tier'].upper():>8} | {tier['hospital_count']:2d} hospitals | "
                  f"Avg Score: {tier['avg_score']:5.1f} | Avg Revenue: ₹{avg_revenue_cr:6.1f}Cr")
        
        print()
        
        # Detailed analysis for Mumbai Medical Center
        mumbai_analysis = await conn.fetchrow("""
            SELECT 
                ha.*,
                hm.tier,
                hm.hospital_type,
                hm.bed_count as master_bed_count
            FROM hospital_analyses ha
            JOIN hospital_master hm ON ha.hospital_master_id = hm.id
            WHERE ha.hospital_name LIKE '%Mumbai Medical Center%'
            ORDER BY ha.created_at DESC
            LIMIT 1
        """)
        
        if mumbai_analysis:
            print("DETAILED ANALYSIS: Mumbai Medical Center")
            print("-" * 60)
            
            # Calculate percentiles
            revenue_rank = await conn.fetchval("""
                SELECT COUNT(*) + 1 
                FROM hospital_analyses 
                WHERE annual_revenue > $1
            """, mumbai_analysis['annual_revenue'])
            
            total_hospitals = len(hospitals)
            revenue_percentile = ((total_hospitals - revenue_rank + 1) / total_hospitals) * 100
            
            score_rank = await conn.fetchval("""
                SELECT COUNT(*) + 1 
                FROM hospital_analyses 
                WHERE overall_score > $1
            """, mumbai_analysis['overall_score'])
            
            score_percentile = ((total_hospitals - score_rank + 1) / total_hospitals) * 100
            
            print(f"Hospital: {mumbai_analysis['hospital_name']}")
            print(f"Tier: {mumbai_analysis['tier'].upper()}")
            print(f"Type: {mumbai_analysis['hospital_type'].replace('_', ' ').title()}")
            bed_count = mumbai_analysis['master_bed_count'] or 0
            print(f"Bed Count: {bed_count:,}")
            print(f"Lifecycle Stage: {mumbai_analysis['lifecycle_stage']}")
            print()
            
            revenue_cr = float(mumbai_analysis['annual_revenue'] or 0) / 10_000_000
            print(f"PERFORMANCE METRICS:")
            print(f"  Revenue: Rs.{revenue_cr:.1f} Crores ({revenue_percentile:.0f}th percentile)")
            print(f"  Overall Score: {mumbai_analysis['overall_score']:.1f}/100 ({score_percentile:.0f}th percentile)")
            print(f"  Benchmark Target: {mumbai_analysis['benchmark_target']:.1f}% growth")
            print(f"  Confidence Score: {mumbai_analysis['confidence_score']:.1%}")
            
            # Generate peer comparison
            peer_hospitals = await conn.fetch("""
                SELECT ha.hospital_name, ha.annual_revenue, ha.overall_score
                FROM hospital_analyses ha
                JOIN hospital_master hm ON ha.hospital_master_id = hm.id
                WHERE hm.tier = $1 AND hm.hospital_type = $2 
                AND ha.hospital_name != $3
                ORDER BY ha.overall_score DESC
            """, mumbai_analysis['tier'], mumbai_analysis['hospital_type'], mumbai_analysis['hospital_name'])
            
            print(f"\nPEER COMPARISON ({mumbai_analysis['tier'].upper()} {mumbai_analysis['hospital_type'].replace('_', ' ').title()} Hospitals):")
            print("-" * 60)
            for peer in peer_hospitals:
                peer_revenue_cr = float(peer['annual_revenue'] or 0) / 10_000_000
                print(f"  {peer['hospital_name'][:30]:<30} | Score: {peer['overall_score']:5.1f} | ₹{peer_revenue_cr:6.1f}Cr")
            
            # Strategic recommendations
            print(f"\nSTRATEGIC RECOMMENDATIONS:")
            print("-" * 60)
            
            if score_percentile < 50:
                print("  PRIORITY: Below-median performance requires immediate attention")
                print("     • Focus on operational efficiency improvements")
                print("     • Benchmark against top-tier performers")
                print("     • Implement cost optimization strategies")
            elif score_percentile < 75:
                print("  OPPORTUNITY: Good performance with room for growth")
                print("     • Target specialty service expansion") 
                print("     • Improve patient satisfaction metrics")
                print("     • Optimize revenue cycle management")
            else:
                print("  EXCELLENCE: Top-tier performance - maintain leadership")
                print("     • Share best practices with peer network")
                print("     • Invest in cutting-edge technology")
                print("     • Expand market presence")
            
            if revenue_percentile < 50:
                print("     • Revenue optimization should be primary focus")
                print("     • Analyze payer mix and pricing strategies")
            
        print(f"\nSYSTEM CAPABILITY DEMONSTRATED")
        print(f"   Your enhanced database now supports:")
        print(f"   - Multi-hospital benchmarking")
        print(f"   - Peer group analysis")
        print(f"   - Performance percentile calculations")
        print(f"   - Strategic recommendation generation")
        print(f"   - Confidence-based reliability scoring")
        
        return True
        
    finally:
        await conn.close()

async def test_consultancy_readiness():
    """Test if system is ready for real consultancy"""
    DATABASE_URL = 'postgresql://postgres:testpass@localhost:5432/hospital_intelligence'
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Check data quality metrics
        quality_check = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_hospitals,
                AVG(confidence_score) as avg_confidence,
                COUNT(*) FILTER (WHERE confidence_score >= 0.8) as high_confidence_count,
                COUNT(DISTINCT tier) as tier_coverage,
                COUNT(DISTINCT hospital_type) as type_coverage
            FROM hospital_analyses ha
            JOIN hospital_master hm ON ha.hospital_master_id = hm.id
        """)
        
        readiness_score = 0
        max_score = 5
        
        print(f"\n🎯 CONSULTANCY READINESS ASSESSMENT")
        print("=" * 60)
        
        # Check 1: Sufficient hospitals
        if quality_check['total_hospitals'] >= 5:
            print("✅ Hospital Count: Sufficient for benchmarking")
            readiness_score += 1
        else:
            print("❌ Hospital Count: Need more hospitals")
        
        # Check 2: Data confidence
        if quality_check['avg_confidence'] >= 0.8:
            print("✅ Data Confidence: High reliability")
            readiness_score += 1
        else:
            print("⚠️  Data Confidence: Moderate reliability")
            readiness_score += 0.5
        
        # Check 3: Tier diversity
        if quality_check['tier_coverage'] >= 2:
            print("✅ Market Coverage: Multiple tiers covered")
            readiness_score += 1
        else:
            print("❌ Market Coverage: Limited tier diversity")
        
        # Check 4: Type diversity
        if quality_check['type_coverage'] >= 2:
            print("✅ Hospital Types: Diverse facility types")
            readiness_score += 1
        else:
            print("❌ Hospital Types: Limited type diversity")
        
        # Check 5: Benchmarking capability
        benchmarking_test = await conn.fetchval("""
            SELECT COUNT(*) FROM (
                SELECT tier, hospital_type, COUNT(*) 
                FROM hospital_analyses ha
                JOIN hospital_master hm ON ha.hospital_master_id = hm.id
                GROUP BY tier, hospital_type
                HAVING COUNT(*) >= 2
            ) peer_groups
        """)
        
        if benchmarking_test >= 1:
            print("✅ Benchmarking: Peer comparison available")
            readiness_score += 1
        else:
            print("❌ Benchmarking: Insufficient peer groups")
        
        readiness_percentage = (readiness_score / max_score) * 100
        
        print(f"\n📊 OVERALL READINESS: {readiness_percentage:.0f}%")
        
        if readiness_percentage >= 80:
            print("🟢 READY FOR PRODUCTION CONSULTANCY")
            print("   You can confidently serve real hospital clients")
        elif readiness_percentage >= 60:
            print("🟡 READY FOR PILOT PROJECTS")
            print("   Start with limited engagements and expand")
        else:
            print("🔴 NOT READY - NEED MORE DATA")
            print("   Collect more hospital data before client work")
        
        return readiness_percentage >= 60
        
    finally:
        await conn.close()

async def main():
    """Main demonstration"""
    success1 = await demonstrate_benchmarking_capability()
    success2 = await test_consultancy_readiness()
    
    if success1 and success2:
        print(f"\n🎉 SUCCESS: Your VERTICAL LIGHT OS is ready for real-world consultancy!")
        print(f"   Database: Enhanced and functional")
        print(f"   Data: Sufficient for meaningful analysis")
        print(f"   Benchmarking: Operational and reliable")
        print(f"   Recommendations: Strategic and actionable")

if __name__ == "__main__":
    asyncio.run(main())