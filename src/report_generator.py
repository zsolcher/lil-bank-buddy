# report_generator.py
import datetime
from .analysis import get_account_summary, get_recent_activity, calculate_expense_split, format_dollar, analyze_payment_patterns, calculate_current_balance_split
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import os
import click

REPORT_PATH = 'reports/USAA_Transaction_Report.md'

def dict_to_md_table(d):
    if not d:
        return 'None'
    header = '| Category | Count |\n|---|---|'
    rows = [f"| {k} | {v} |" for k, v in d.items()]
    return '\n'.join([header] + rows)

def plot_category_pie(categories, account_name, filename):
    if not categories:
        return None
    labels = list(categories.keys())
    sizes = list(categories.values())
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    plt.title(f'Top Categories - {account_name}')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close(fig)
    return filename

def generate_current_balance_table(balance_data):
    """Generate markdown table for current balance split breakdown"""
    if not balance_data['category_breakdown']:
        return 'No expense data available'
    
    header = f"| Category | Total Amount | {balance_data['person1_name']} ({balance_data['person1_percentage']}%) | {balance_data['person2_name']} ({balance_data['person2_percentage']}%) |\n"
    separator = "|---|---|---|---|\n"
    
    rows = []
    for item in balance_data['category_breakdown']:
        person1_amount = format_dollar(item[f"{balance_data['person1_name']}_share"])
        person2_amount = format_dollar(item[f"{balance_data['person2_name']}_share"])
        total_amount = format_dollar(item['total_amount'])
        rows.append(f"| {item['category']} | {total_amount} | {person1_amount} | {person2_amount} |")
    
    # Add totals row
    rows.append(f"| **TOTAL EXPENSES** | **{format_dollar(balance_data['total_expenses'])}** | **{format_dollar(balance_data['total_expenses'] * balance_data['person1_percentage'] / 100)}** | **{format_dollar(balance_data['total_expenses'] * balance_data['person2_percentage'] / 100)}** |")
    
    return header + separator + '\n'.join(rows)

def generate_payment_history_table(payment_data):
    """Generate markdown table for recent payment history"""
    if not payment_data['recent_payments']:
        return 'No recent payments found'
    
    header = "| Date | Amount | Description |\n"
    separator = "|---|---|---|\n"
    
    rows = []
    for payment in payment_data['recent_payments']:
        amount = format_dollar(payment['amount'])
        rows.append(f"| {payment['date']} | {amount} | {payment['description']} |")
    
    return header + separator + '\n'.join(rows)

def generate_report(person1_name="Person 1", person2_name="Person 2", person1_percentage=50):
    cc_summary = get_account_summary('team_beeb_cc')
    checking_summary = get_account_summary('team_beeb_checking')
    cc_recent = get_recent_activity('team_beeb_cc')
    checking_recent = get_recent_activity('team_beeb_checking')
    now = datetime.datetime.now().strftime('%Y-%m-%d')

    # Generate pie charts for top categories
    cc_pie_path = 'reports/cc_top_categories.png'
    checking_pie_path = 'reports/checking_top_categories.png'
    plot_category_pie(cc_recent['top_categories'], 'Credit Card', cc_pie_path)
    plot_category_pie(checking_recent['top_categories'], 'Checking', checking_pie_path)

    # Calculate current balance splits (total outstanding balance)
    cc_balance_split = calculate_current_balance_split('team_beeb_cc', person1_percentage, person1_name, person2_name)
    checking_balance_split = calculate_current_balance_split('team_beeb_checking', person1_percentage, person1_name, person2_name)
    
    # Analyze payment patterns
    cc_payments = analyze_payment_patterns('team_beeb_cc')
    checking_payments = analyze_payment_patterns('team_beeb_checking')

    # Calculate expense splits since last settlement (automatically detects settlement period)
    cc_split = calculate_expense_split('team_beeb_cc', person1_percentage, person1_name, person2_name)
    checking_split = calculate_expense_split('team_beeb_checking', person1_percentage, person1_name, person2_name)
    
    # Ensure reports directory exists
    os.makedirs('reports', exist_ok=True)
    
    with open(REPORT_PATH, 'w') as f:
        f.write(f"# USAA Accounts Transaction Report\n\n")
        f.write(f"## Overview\nThis report summarizes key insights and statistics for your USAA accounts, based on the latest imported transaction data.\n\n---\n\n")
        f.write(f"## Account Summaries\n\n")
        f.write("| Account | Total Transactions | Total Amount | Largest Transaction | Most Frequent Category | Date Range |\n")
        f.write("|---|---|---|---|---|---|\n")
        f.write(f"| Credit Card (team_beeb_cc) | {cc_summary['total_transactions']} | {cc_summary['total_amount']} | {cc_summary['largest_transaction']} | {cc_summary['most_frequent_category']} | {cc_summary['date_range'][0]} to {cc_summary['date_range'][1]} |\n")
        f.write(f"| Checking (team_beeb_checking) | {checking_summary['total_transactions']} | {checking_summary['total_amount']} | {checking_summary['largest_transaction']} | {checking_summary['most_frequent_category']} | {checking_summary['date_range'][0]} to {checking_summary['date_range'][1]} |\n\n")
        f.write(f"---\n\n")
        
        # Add current balance analysis section
        f.write(f"## Current Balance Analysis\n\n")
        f.write(f"**Split Ratio:** {person1_name} {person1_percentage}% / {person2_name} {100-person1_percentage}%\n\n")
        f.write(f"*This section shows the total outstanding balance and how it should be split based on your agreed percentage.*\n\n")
        
        f.write(f"### Credit Card Current Balance\n")
        f.write(f"- **Total Outstanding Balance:** {format_dollar(cc_balance_split['total_balance'])}\n")
        f.write(f"- **Total Expenses (All Time):** {format_dollar(cc_balance_split['total_expenses'])}\n")
        f.write(f"- **Total Payments Made:** {format_dollar(cc_balance_split['total_payments_credits'])}\n")
        f.write(f"- **{person1_name} Owes:** {format_dollar(cc_balance_split['person1_owes'])}\n")
        f.write(f"- **{person2_name} Owes:** {format_dollar(cc_balance_split['person2_owes'])}\n\n")
        
        f.write(f"#### Recent Credit Card Payments\n")
        f.write(f"{generate_payment_history_table(cc_payments)}\n\n")
        
        f.write(f"#### Credit Card Expense Breakdown (All Time)\n")
        f.write(f"{generate_current_balance_table(cc_balance_split)}\n\n")
        
        f.write(f"### Checking Account Current Balance\n")
        f.write(f"- **Total Outstanding Balance:** {format_dollar(checking_balance_split['total_balance'])}\n")
        f.write(f"- **Total Expenses (All Time):** {format_dollar(checking_balance_split['total_expenses'])}\n")
        f.write(f"- **Total Payments Made:** {format_dollar(checking_balance_split['total_payments_credits'])}\n")
        f.write(f"- **{person1_name} Owes:** {format_dollar(checking_balance_split['person1_owes'])}\n")
        f.write(f"- **{person2_name} Owes:** {format_dollar(checking_balance_split['person2_owes'])}\n\n")
        
        f.write(f"#### Recent Checking Payments\n")
        f.write(f"{generate_payment_history_table(checking_payments)}\n\n")
        
        # Combined current balance totals
        total_combined_balance = cc_balance_split['total_balance'] + checking_balance_split['total_balance']
        total_person1_current_owes = cc_balance_split['person1_owes'] + checking_balance_split['person1_owes']
        total_person2_current_owes = cc_balance_split['person2_owes'] + checking_balance_split['person2_owes']
        
        f.write(f"### 💰 **SETTLEMENT SUMMARY** 💰\n")
        f.write(f"**Total Current Balance Across All Accounts:** {format_dollar(total_combined_balance)}\n\n")
        f.write(f"**💸 {person1_name} owes:** {format_dollar(total_person1_current_owes)}\n")
        f.write(f"**💸 {person2_name} owes:** {format_dollar(total_person2_current_owes)}\n\n")
        
        f.write(f"---\n\n")
        
        # Add expense splitting section (since last settlement)
        f.write(f"## New Expenses Since Last Settlement\n\n")
        f.write(f"*This section shows only new expenses since the last detected settlement payments.*\n\n")
        
        f.write(f"### Credit Card New Expenses\n")
        f.write(f"- **Period:** {cc_split['settlement_info']}\n")
        f.write(f"- **New Expenses:** {format_dollar(cc_split['total_expenses'])}\n")
        f.write(f"- **{person1_name} Share:** {format_dollar(cc_split['person1_share'])}\n")
        f.write(f"- **{person2_name} Share:** {format_dollar(cc_split['person2_share'])}\n")
        f.write(f"- **Expense Transactions:** {cc_split['num_expense_transactions']}\n")
        if cc_split['num_expense_transactions'] > 0:
            f.write(f"- **Date Range:** {cc_split['date_range'][0]} to {cc_split['date_range'][1]}\n\n")
        else:
            f.write(f"\n")
        
        f.write(f"### Checking New Expenses\n")
        f.write(f"- **Period:** {checking_split['settlement_info']}\n")
        f.write(f"- **New Expenses:** {format_dollar(checking_split['total_expenses'])}\n")
        f.write(f"- **{person1_name} Share:** {format_dollar(checking_split['person1_share'])}\n")
        f.write(f"- **{person2_name} Share:** {format_dollar(checking_split['person2_share'])}\n")
        f.write(f"- **Expense Transactions:** {checking_split['num_expense_transactions']}\n")
        if checking_split['num_expense_transactions'] > 0:
            f.write(f"- **Date Range:** {checking_split['date_range'][0]} to {checking_split['date_range'][1]}\n\n")
        else:
            f.write(f"\n")
        
        f.write(f"---\n\n")
        
        # Move Recent Activity section to the end
        f.write(f"## Recent Activity (Last 30 Days)\n\n")
        f.write(f"### Credit Card\n")
        f.write(f"- **Number of Transactions:** {cc_recent['num_transactions']}\n")
        f.write(f"- **Total Amount:** {cc_recent['total_amount']}\n")
        f.write(f"- **Top 3 Categories:**\n\n{dict_to_md_table(cc_recent['top_categories'])}\n\n")
        if os.path.exists(cc_pie_path):
            f.write(f"![Credit Card Top Categories Pie Chart](./cc_top_categories.png)\n\n")
        f.write(f"### Checking\n")
        f.write(f"- **Number of Transactions:** {checking_recent['num_transactions']}\n")
        f.write(f"- **Total Amount:** {checking_recent['total_amount']}\n")
        f.write(f"- **Top 3 Categories:**\n\n{dict_to_md_table(checking_recent['top_categories'])}\n\n")
        if os.path.exists(checking_pie_path):
            f.write(f"![Checking Top Categories Pie Chart](./checking_top_categories.png)\n\n")
        
        f.write(f"---\n\n*Report generated on: {now}*\n")

@click.group()
def cli():
    """lil' bank buddy: Your friendly CLI for bank account analysis and reporting."""
    pass

@cli.command()
@click.option('--person1-name', default='Person 1', help='Name for person 1')
@click.option('--person2-name', default='Person 2', help='Name for person 2') 
@click.option('--person1-percentage', default=50, type=int, help='Percentage for person 1 (0-100)')
def report(person1_name, person2_name, person1_percentage):
    """Generate a Markdown report with tables, charts, and expense splitting."""
    if person1_percentage < 0 or person1_percentage > 100:
        click.echo("Error: person1-percentage must be between 0 and 100")
        return
    
    generate_report(person1_name, person2_name, person1_percentage)
    click.echo(f"Report generated at reports/USAA_Transaction_Report.md")
    click.echo(f"Split: {person1_name} {person1_percentage}% / {person2_name} {100-person1_percentage}%")
    click.echo(f"Using intelligent settlement detection")

# Allow running as 'python -m buddy' or 'buddy' if installed as a CLI
cli.prog_name = "buddy"

if __name__ == '__main__':
    cli()
