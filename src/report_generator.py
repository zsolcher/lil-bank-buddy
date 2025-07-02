# report_generator.py
import datetime
from analysis import get_account_summary, get_recent_activity
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

def generate_report():
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

    with open(REPORT_PATH, 'w') as f:
        f.write(f"# USAA Accounts Transaction Report\n\n")
        f.write(f"## Overview\nThis report summarizes key insights and statistics for your USAA accounts, based on the latest imported transaction data.\n\n---\n\n")
        f.write(f"## Account Summaries\n\n")
        f.write("| Account | Total Transactions | Total Amount | Largest Transaction | Most Frequent Category | Date Range |\n")
        f.write("|---|---|---|---|---|---|\n")
        f.write(f"| Credit Card (team_beeb_cc) | {cc_summary['total_transactions']} | {cc_summary['total_amount']} | {cc_summary['largest_transaction']} | {cc_summary['most_frequent_category']} | {cc_summary['date_range'][0]} to {cc_summary['date_range'][1]} |\n")
        f.write(f"| Checking (team_beeb_checking) | {checking_summary['total_transactions']} | {checking_summary['total_amount']} | {checking_summary['largest_transaction']} | {checking_summary['most_frequent_category']} | {checking_summary['date_range'][0]} to {checking_summary['date_range'][1]} |\n\n")
        f.write(f"---\n\n")
        f.write(f"## Recent Activity (Last 30 Days)\n\n")
        f.write(f"### Credit Card\n")
        f.write(f"- **Number of Transactions:** {cc_recent['num_transactions']}\n")
        f.write(f"- **Total Amount:** {cc_recent['total_amount']}\n")
        f.write(f"- **Top 3 Categories:**\n\n{dict_to_md_table(cc_recent['top_categories'])}\n\n")
        if os.path.exists(cc_pie_path):
            f.write(f"![Credit Card Top Categories Pie Chart]({cc_pie_path})\n\n")
        f.write(f"### Checking\n")
        f.write(f"- **Number of Transactions:** {checking_recent['num_transactions']}\n")
        f.write(f"- **Total Amount:** {checking_recent['total_amount']}\n")
        f.write(f"- **Top 3 Categories:**\n\n{dict_to_md_table(checking_recent['top_categories'])}\n\n")
        if os.path.exists(checking_pie_path):
            f.write(f"![Checking Top Categories Pie Chart]({checking_pie_path})\n\n")
        f.write(f"---\n\n*Report generated on: {now}*\n")

@click.group()
def cli():
    """lil' bank buddy: Your friendly CLI for bank account analysis and reporting."""
    pass

@cli.command()
def report():
    """Generate a Markdown report with tables and charts."""
    generate_report()
    click.echo("Report generated at reports/USAA_Transaction_Report.md")

# Allow running as 'python -m buddy' or 'buddy' if installed as a CLI
cli.prog_name = "buddy"

if __name__ == '__main__':
    cli()
