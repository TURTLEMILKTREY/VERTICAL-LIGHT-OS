"""
Hospital Benchmark Data Collection CLI Tool
Command-line interface for managing hospital benchmark data collection campaigns
"""

import asyncio
import click
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.text import Text

from ..services.benchmark_data_collection import HospitalDataCollector, BenchmarkAnalyzer
from ..config.advanced_config_manager import ConfigManager
from ..scripts.initialize_benchmark_db import BenchmarkDatabaseManager


console = Console()


@click.group()
@click.option('--config-file', default='config.json', help='Configuration file path')
@click.pass_context
def cli(ctx, config_file):
    """Hospital Benchmark Data Collection Management CLI"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = ConfigManager(config_file)
    
    console.print(Panel.fit(
        "[bold blue]Hospital AI Consulting OS[/bold blue]\n"
        "[cyan]Benchmark Data Collection Management[/cyan]",
        style="blue"
    ))


@cli.command()
@click.option('--drop-existing', is_flag=True, help='Drop existing database tables')
@click.pass_context
def init_database(ctx, drop_existing):
    """Initialize the benchmark database with schema and sample data"""
    
    async def _init_db():
        config = ctx.obj['config']
        if drop_existing:
            config.set('database.drop_existing', True)
        
        db_manager = BenchmarkDatabaseManager(config)
        
        with console.status("[bold green]Initializing database schema..."):
            await db_manager.create_database_schema()
        
        with console.status("[bold green]Populating initial data..."):
            await db_manager.populate_initial_data()
        
        with console.status("[bold green]Creating tracking tables..."):
            await db_manager.create_data_collection_tracking()
        
        report = await db_manager.generate_sample_report()
        
        # Display results
        table = Table(title="Database Initialization Summary", style="green")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Hospitals", str(report['total_hospitals']))
        table.add_row("Tier 1 Hospitals", str(report['tier_distribution'].get('tier_1', 0)))
        table.add_row("Tier 2 Hospitals", str(report['tier_distribution'].get('tier_2', 0)))
        table.add_row("Tier 3 Hospitals", str(report['tier_distribution'].get('tier_3', 0)))
        table.add_row("Avg Bed Occupancy", f"{report['sample_averages']['bed_occupancy_rate']:.1f}%")
        table.add_row("Avg Patient Satisfaction", f"{report['sample_averages']['patient_satisfaction_score']:.1f}/10")
        
        console.print(table)
        console.print("[bold green]✅ Database initialization completed successfully!")
        
        await db_manager.engine.dispose()
    
    asyncio.run(_init_db())


@cli.command()
@click.option('--tier', multiple=True, help='Filter by city tiers (tier_1, tier_2, tier_3, tier_4)')
@click.option('--hospital-type', multiple=True, help='Filter by hospital types')
@click.option('--output-file', help='Save results to file')
@click.pass_context
def list_targets(ctx, tier, hospital_type, output_file):
    """List target hospitals for data collection"""
    
    async def _list_targets():
        config = ctx.obj['config']
        # Mock database session for this example
        db_session = None
        
        collector = HospitalDataCollector(db_session, config)
        target_hospitals = await collector.identify_target_hospitals()
        
        # Apply filters
        if tier:
            target_hospitals = [h for h in target_hospitals if h['city_tier'].value in tier]
        if hospital_type:
            target_hospitals = [h for h in target_hospitals if h['hospital_type'].value in hospital_type]
        
        # Create display table
        table = Table(title=f"Target Hospitals ({len(target_hospitals)} hospitals)", style="blue")
        table.add_column("Hospital Name", style="cyan")
        table.add_column("City", style="white")
        table.add_column("State", style="white")
        table.add_column("Tier", style="yellow")
        table.add_column("Type", style="green")
        table.add_column("Beds", style="magenta")
        table.add_column("Data Method", style="red")
        
        for hospital in target_hospitals[:20]:  # Show first 20
            table.add_row(
                hospital['name'][:30],
                hospital['city'],
                hospital['state'],
                hospital['city_tier'].value,
                hospital['hospital_type'].value.replace('_', ' ').title(),
                str(hospital.get('bed_count', 'N/A')),
                hospital.get('data_availability', 'manual')
            )
        
        console.print(table)
        
        if len(target_hospitals) > 20:
            console.print(f"[yellow]... and {len(target_hospitals) - 20} more hospitals")
        
        # Save to file if requested
        if output_file:
            df = pd.DataFrame(target_hospitals)
            if output_file.endswith('.csv'):
                df.to_csv(output_file, index=False)
            elif output_file.endswith('.json'):
                df.to_json(output_file, orient='records', indent=2)
            console.print(f"[green]✅ Results saved to {output_file}")
    
    asyncio.run(_list_targets())


@cli.command()
@click.option('--methods', multiple=True, default=['hms_api', 'manual_survey'], 
              help='Collection methods to use')
@click.option('--priority-tiers', multiple=True, default=['tier_1', 'tier_2'],
              help='Priority city tiers')
@click.option('--dry-run', is_flag=True, help='Show plan without executing')
@click.pass_context
def start_collection(ctx, methods, priority_tiers, dry_run):
    """Start data collection campaign"""
    
    async def _start_collection():
        config = ctx.obj['config']
        db_session = None  # Mock for this example
        
        collector = HospitalDataCollector(db_session, config)
        
        # Get target hospitals
        target_hospitals = await collector.identify_target_hospitals()
        
        # Filter by priority tiers
        filtered_hospitals = [
            h for h in target_hospitals 
            if h['city_tier'].value in priority_tiers
        ]
        
        # Create collection campaigns
        campaigns = await collector.create_data_collection_campaigns(filtered_hospitals)
        
        # Display campaign plan
        for campaign_type, plan in campaigns.items():
            if campaign_type.replace('_', ' ').title() in [m.replace('_', ' ').title() for m in methods]:
                panel = Panel(
                    f"[bold]Target Hospitals:[/bold] {len(plan['hospitals'])}\n"
                    f"[bold]Timeline:[/bold] {plan['timeline']}\n"
                    f"[bold]Expected Completion:[/bold] {plan.get('expected_completion', 'N/A')}%\n"
                    f"[bold]Automation Level:[/bold] {plan['automation_level']}\n"
                    f"[bold]Method:[/bold] {plan.get('method', campaign_type)}",
                    title=f"Campaign: {campaign_type.replace('_', ' ').title()}",
                    style="green" if plan['priority'] == 'high' else "yellow"
                )
                console.print(panel)
        
        if not dry_run:
            console.print("\n[bold yellow]⚠️ Starting data collection campaigns...")
            
            with Progress() as progress:
                task = progress.add_task("[cyan]Collecting data...", total=len(filtered_hospitals))
                
                # Simulate collection process
                for i, hospital in enumerate(filtered_hospitals[:5]):  # Limit to 5 for demo
                    progress.update(task, advance=1)
                    console.print(f"[green]✅ Collected data for {hospital['name']}")
                    await asyncio.sleep(0.5)  # Simulate processing time
                
                progress.update(task, completed=len(filtered_hospitals))
            
            console.print("[bold green]🎉 Data collection campaign completed!")
        else:
            console.print("[yellow]📋 Dry run completed. Use --no-dry-run to execute.")
    
    asyncio.run(_start_collection())


@cli.command()
@click.option('--tier', help='Filter by city tier')
@click.option('--hospital-type', help='Filter by hospital type')
@click.option('--format', type=click.Choice(['table', 'json', 'csv']), default='table',
              help='Output format')
@click.pass_context
def show_benchmarks(ctx, tier, hospital_type, format):
    """Display benchmark analysis results"""
    
    async def _show_benchmarks():
        config = ctx.obj['config']
        db_session = None  # Mock for this example
        
        analyzer = BenchmarkAnalyzer(db_session)
        
        # Get tier benchmarks
        if tier:
            tier_enum = getattr(__import__('backend.models.hospital_benchmarks', fromlist=['CityTier']).CityTier, tier.upper())
            benchmarks = {tier: await analyzer._analyze_tier_performance(tier_enum)}
        else:
            benchmarks = await analyzer.create_tier_wise_benchmarks()
        
        if format == 'table':
            for tier_name, tier_data in benchmarks.items():
                if tier_data['sample_size'] == 0:
                    continue
                    
                table = Table(title=f"{tier_name.replace('_', ' ').title()} Benchmarks", style="blue")
                table.add_column("Metric", style="cyan")
                table.add_column("Median (P50)", style="white")
                table.add_column("P75", style="green")
                table.add_column("P90", style="yellow")
                table.add_column("Sample Size", style="magenta")
                
                for metric, stats in tier_data['benchmarks'].items():
                    table.add_row(
                        metric.replace('_', ' ').title(),
                        f"{stats['percentile_50']:.1f}",
                        f"{stats['percentile_75']:.1f}",
                        f"{stats['percentile_90']:.1f}",
                        str(stats['sample_size'])
                    )
                
                console.print(table)
                console.print()
        
        elif format == 'json':
            console.print(json.dumps(benchmarks, indent=2, default=str))
        
        elif format == 'csv':
            # Convert to DataFrame and display as CSV
            rows = []
            for tier_name, tier_data in benchmarks.items():
                for metric, stats in tier_data.get('benchmarks', {}).items():
                    rows.append({
                        'tier': tier_name,
                        'metric': metric,
                        'p50': stats['percentile_50'],
                        'p75': stats['percentile_75'],
                        'p90': stats['percentile_90'],
                        'sample_size': stats['sample_size']
                    })
            
            df = pd.DataFrame(rows)
            console.print(df.to_csv(index=False))
    
    asyncio.run(_show_benchmarks())


@cli.command()
@click.argument('hospital_id')
@click.option('--metrics', multiple=True, help='Specific metrics to compare')
@click.pass_context
def compare_hospital(ctx, hospital_id, metrics):
    """Compare specific hospital performance against benchmarks"""
    
    # Mock comparison data
    comparison_data = {
        'hospital_name': 'Apollo Hospital Mumbai',
        'city_tier': 'tier_1',
        'hospital_type': 'private_corporate',
        'metrics': {
            'bed_occupancy_rate': {
                'current': 78.5,
                'benchmark': 83.0,
                'percentile': 35,
                'variance': -5.4,
                'status': 'below_benchmark'
            },
            'patient_satisfaction_score': {
                'current': 8.1,
                'benchmark': 8.3,
                'percentile': 45,
                'variance': -2.4,
                'status': 'near_benchmark'
            },
            'revenue_per_bed': {
                'current': 26.5,
                'benchmark': 24.0,
                'percentile': 78,
                'variance': 10.4,
                'status': 'above_benchmark'
            }
        }
    }
    
    console.print(f"\n[bold blue]Benchmark Comparison: {comparison_data['hospital_name']}[/bold blue]")
    console.print(f"Tier: {comparison_data['city_tier']} | Type: {comparison_data['hospital_type']}")
    
    table = Table(title="Performance vs Benchmarks", style="white")
    table.add_column("Metric", style="cyan")
    table.add_column("Current", style="white")
    table.add_column("Benchmark", style="blue")
    table.add_column("Percentile", style="yellow")
    table.add_column("Variance %", style="red")
    table.add_column("Status", style="green")
    
    for metric, data in comparison_data['metrics'].items():
        if not metrics or metric in metrics:
            status_icon = {
                'above_benchmark': '🟢',
                'near_benchmark': '🟡', 
                'below_benchmark': '🔴'
            }.get(data['status'], '⚪')
            
            table.add_row(
                metric.replace('_', ' ').title(),
                f"{data['current']:.1f}",
                f"{data['benchmark']:.1f}",
                f"{data['percentile']}th",
                f"{data['variance']:+.1f}%",
                f"{status_icon} {data['status'].replace('_', ' ').title()}"
            )
    
    console.print(table)
    
    # Show improvement opportunities
    console.print("\n[bold yellow]🎯 Top Improvement Opportunities:[/bold yellow]")
    opportunities = [
        ("Bed Occupancy Rate", "5.4% increase potential", "₹8.5L/month additional revenue"),
        ("Patient Satisfaction", "0.2 points improvement", "Better patient retention")
    ]
    
    for i, (metric, potential, impact) in enumerate(opportunities, 1):
        console.print(f"{i}. [cyan]{metric}[/cyan]: {potential} → {impact}")


@cli.command()
@click.option('--scheme', help='Filter by government scheme')
@click.option('--tier', help='Filter by city tier')
@click.pass_context
def scheme_analysis(ctx, scheme, tier):
    """Analyze government scheme reimbursement patterns"""
    
    # Mock scheme analysis data
    scheme_data = {
        'ayushman_bharat': {
            'total_hospitals': 45,
            'total_cases': 15420,
            'average_approval_rate': 87.5,
            'average_reimbursement_days': 32,
            'tier_performance': {
                'tier_1': {'approval_rate': 91.2, 'reimbursement_days': 28},
                'tier_2': {'approval_rate': 86.8, 'reimbursement_days': 34},
                'tier_3': {'approval_rate': 82.1, 'reimbursement_days': 38}
            }
        },
        'cghs': {
            'total_hospitals': 28,
            'total_cases': 8960,
            'average_approval_rate': 93.2,
            'average_reimbursement_days': 25,
            'tier_performance': {
                'tier_1': {'approval_rate': 95.1, 'reimbursement_days': 22},
                'tier_2': {'approval_rate': 91.3, 'reimbursement_days': 28}
            }
        }
    }
    
    console.print("[bold blue]Government Scheme Analysis[/bold blue]\n")
    
    for scheme_name, data in scheme_data.items():
        if not scheme or scheme_name == scheme:
            panel_content = (
                f"[bold]Total Hospitals:[/bold] {data['total_hospitals']}\n"
                f"[bold]Total Cases:[/bold] {data['total_cases']:,}\n"
                f"[bold]Avg Approval Rate:[/bold] {data['average_approval_rate']:.1f}%\n"
                f"[bold]Avg Reimbursement Days:[/bold] {data['average_reimbursement_days']} days"
            )
            
            panel = Panel(
                panel_content,
                title=f"{scheme_name.replace('_', ' ').title()} Scheme",
                style="green"
            )
            console.print(panel)
            
            # Tier-wise breakdown
            if not tier:
                table = Table(title=f"{scheme_name.title()} - Tier Performance", style="blue")
                table.add_column("City Tier", style="cyan")
                table.add_column("Approval Rate", style="green")
                table.add_column("Reimbursement Days", style="yellow")
                
                for tier_name, tier_data in data['tier_performance'].items():
                    table.add_row(
                        tier_name.replace('_', ' ').title(),
                        f"{tier_data['approval_rate']:.1f}%",
                        f"{tier_data['reimbursement_days']} days"
                    )
                
                console.print(table)
                console.print()


@cli.command()
@click.option('--output-dir', default='./exports', help='Output directory for exports')
@click.option('--format', type=click.Choice(['excel', 'csv', 'json']), default='excel',
              help='Export format')
@click.option('--include-raw', is_flag=True, help='Include raw hospital data')
@click.pass_context
def export_data(ctx, output_dir, format, include_raw):
    """Export benchmark data for analysis"""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with console.status("[bold green]Exporting benchmark data..."):
        # Mock export process
        files_created = []
        
        if format == 'excel':
            filename = f"hospital_benchmarks_{timestamp}.xlsx"
            filepath = output_path / filename
            files_created.append(filepath)
        elif format == 'csv':
            files_created.extend([
                output_path / f"tier_benchmarks_{timestamp}.csv",
                output_path / f"specialty_benchmarks_{timestamp}.csv",
                output_path / f"scheme_analysis_{timestamp}.csv"
            ])
        elif format == 'json':
            filename = f"benchmark_data_{timestamp}.json"
            filepath = output_path / filename
            files_created.append(filepath)
        
        # Simulate file creation
        for filepath in files_created:
            filepath.touch()
    
    console.print("[bold green]✅ Export completed successfully!")
    console.print("\n[bold]Files created:[/bold]")
    for filepath in files_created:
        console.print(f"  📄 {filepath}")
    
    # Show export summary
    table = Table(title="Export Summary", style="green")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="white")
    
    table.add_row("Total Hospitals", "52")
    table.add_row("Performance Records", "624")
    table.add_row("Financial Records", "468")
    table.add_row("Benchmark Standards", "15")
    table.add_row("Export Format", format.upper())
    
    console.print(table)


@cli.command()
@click.pass_context
def status(ctx):
    """Show overall system status and data quality"""
    
    # Mock status data
    status_data = {
        'database_status': 'healthy',
        'total_hospitals': 52,
        'data_freshness': {
            'last_24h': 18,
            'last_week': 34,
            'last_month': 52
        },
        'data_quality': {
            'overall_score': 8.2,
            'completeness': 85.5,
            'accuracy': 91.2,
            'consistency': 88.7
        },
        'collection_campaigns': {
            'active': 2,
            'completed': 15,
            'failed': 1
        }
    }
    
    console.print("[bold blue]Hospital Benchmark System Status[/bold blue]\n")
    
    # System health
    health_status = "🟢 Healthy" if status_data['database_status'] == 'healthy' else "🔴 Issues"
    console.print(f"[bold]System Health:[/bold] {health_status}")
    console.print(f"[bold]Total Hospitals:[/bold] {status_data['total_hospitals']}")
    
    # Data freshness
    console.print(f"\n[bold yellow]📊 Data Freshness:[/bold yellow]")
    console.print(f"  Last 24 hours: {status_data['data_freshness']['last_24h']} hospitals")
    console.print(f"  Last week: {status_data['data_freshness']['last_week']} hospitals")
    console.print(f"  Last month: {status_data['data_freshness']['last_month']} hospitals")
    
    # Data quality metrics
    quality = status_data['data_quality']
    console.print(f"\n[bold green]🎯 Data Quality Metrics:[/bold green]")
    console.print(f"  Overall Score: {quality['overall_score']:.1f}/10")
    console.print(f"  Completeness: {quality['completeness']:.1f}%")
    console.print(f"  Accuracy: {quality['accuracy']:.1f}%")
    console.print(f"  Consistency: {quality['consistency']:.1f}%")
    
    # Collection campaigns
    campaigns = status_data['collection_campaigns']
    console.print(f"\n[bold magenta]🚀 Collection Campaigns:[/bold magenta]")
    console.print(f"  Active: {campaigns['active']}")
    console.print(f"  Completed: {campaigns['completed']}")
    console.print(f"  Failed: {campaigns['failed']}")


if __name__ == '__main__':
    cli()