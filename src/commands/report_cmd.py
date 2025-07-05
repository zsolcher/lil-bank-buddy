"""Report command for generating markdown reports."""
import click
import os
from ..core.report import ReportGenerator

@click.command()
@click.option('--person1-name', default='Person 1', 
              help='Name for person 1')
@click.option('--person2-name', default='Person 2', 
              help='Name for person 2') 
@click.option('--person1-percentage', default=50, type=int, 
              help='Percentage for person 1 (0-100)')
@click.option('--output', default='reports/USAA_Transaction_Report.md',
              help='Output path for the report')
@click.option('--db-path', default=None,
              help='Path to SQLite database (uses default if not specified)')
def report_cmd(person1_name, person2_name, person1_percentage, output, db_path):
    """Generate a comprehensive Markdown report with tables, charts, and expense splitting."""
    if person1_percentage < 0 or person1_percentage > 100:
        click.echo("Error: person1-percentage must be between 0 and 100")
        return
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Generate report
        report_gen = ReportGenerator(db_path=db_path)
        report_gen.generate_report(
            person1_name=person1_name,
            person2_name=person2_name,
            person1_percentage=person1_percentage,
            filename=output
        )
        
        click.echo(f"✓ Report generated at {output}")
        click.echo(f"  Split: {person1_name} {person1_percentage}% / {person2_name} {100-person1_percentage}%")
        click.echo(f"  Using intelligent settlement detection")
        
    except Exception as e:
        click.echo(f"✗ Error generating report: {e}")
        click.echo("Make sure the database exists and contains data. Try running 'buddy import' first.")
