"""Analysis command for running account analysis."""
import click
from ..core.analysis import BankAnalyzer
from ..core.database import DatabaseManager

@click.command()
@click.option('--account', default='both', 
              type=click.Choice(['both', 'cc', 'checking']),
              help='Account to analyze (both, cc, or checking)')
@click.option('--days', default=30, type=int,
              help='Number of days for recent activity analysis')
@click.option('--person1-name', default='Person 1',
              help='Name for person 1')
@click.option('--person2-name', default='Person 2',
              help='Name for person 2')
@click.option('--person1-percentage', default=50, type=int,
              help='Percentage for person 1 (0-100)')
@click.option('--db-path', default=None,
              help='Path to SQLite database (uses default if not specified)')
def analyze_cmd(account, days, person1_name, person2_name, person1_percentage, db_path):
    """Analyze account data and show summaries, splits, and patterns."""
    if person1_percentage < 0 or person1_percentage > 100:
        click.echo("Error: person1-percentage must be between 0 and 100")
        return
    
    try:
        db_manager = DatabaseManager(db_path)
        analyzer = BankAnalyzer(db_manager)
        
        accounts_to_analyze = []
        if account == 'both':
            accounts_to_analyze = ['team_beeb_cc', 'team_beeb_checking']
        elif account == 'cc':
            accounts_to_analyze = ['team_beeb_cc']
        elif account == 'checking':
            accounts_to_analyze = ['team_beeb_checking']
        
        for account_name in accounts_to_analyze:
            display_name = "Credit Card" if account_name == 'team_beeb_cc' else "Checking"
            click.echo(f"\n{'='*50}")
            click.echo(f"  {display_name.upper()} ACCOUNT ANALYSIS")
            click.echo(f"{'='*50}")
            
            # Account summary
            summary = analyzer.get_account_summary(account_name)
            click.echo(f"\n📊 ACCOUNT SUMMARY:")
            click.echo(f"  Total Transactions: {summary['total_transactions']}")
            click.echo(f"  Total Amount: {summary['total_amount']}")
            click.echo(f"  Largest Transaction: {summary['largest_transaction']}")
            click.echo(f"  Most Frequent Category: {summary['most_frequent_category']}")
            click.echo(f"  Date Range: {summary['date_range'][0]} to {summary['date_range'][1]}")
            
            # Recent activity
            recent = analyzer.get_recent_activity(account_name, days=days)
            click.echo(f"\n📅 RECENT ACTIVITY (Last {days} days):")
            click.echo(f"  Number of Transactions: {recent['num_transactions']}")
            click.echo(f"  Total Amount: {recent['total_amount']}")
            click.echo(f"  Top Categories: {dict(list(recent['top_categories'].items())[:5])}")
            
            # Payment patterns
            payments = analyzer.analyze_payment_patterns(account_name)
            click.echo(f"\n💳 PAYMENT PATTERNS:")
            click.echo(f"  Recent Payments: {len(payments['recent_payments'])}")
            if payments['recent_payments']:
                click.echo(f"  Latest Payment: {payments['recent_payments'][0]['date']} - {payments['recent_payments'][0]['amount']} - {payments['recent_payments'][0]['description']}")
            
            # Current balance split
            balance_split = analyzer.calculate_current_balance_split(
                account_name, person1_percentage, person1_name, person2_name
            )
            click.echo(f"\n💰 CURRENT BALANCE SPLIT:")
            click.echo(f"  Total Outstanding Balance: {balance_split['total_balance']}")
            click.echo(f"  {person1_name} Owes: {balance_split['person1_owes']}")
            click.echo(f"  {person2_name} Owes: {balance_split['person2_owes']}")
            
            # Expense split since settlement
            expense_split = analyzer.calculate_expense_split(
                account_name, person1_percentage, person1_name, person2_name
            )
            click.echo(f"\n🔄 NEW EXPENSES SINCE SETTLEMENT:")
            click.echo(f"  Period: {expense_split['settlement_info']}")
            click.echo(f"  New Expenses: {expense_split['total_expenses']}")
            click.echo(f"  {person1_name} Share: {expense_split['person1_share']}")
            click.echo(f"  {person2_name} Share: {expense_split['person2_share']}")
        
        click.echo(f"\n{'='*50}")
        click.echo("Analysis complete!")
        
    except Exception as e:
        click.echo(f"✗ Error during analysis: {e}")
        click.echo("Make sure the database exists and contains data. Try running 'buddy import' first.")
