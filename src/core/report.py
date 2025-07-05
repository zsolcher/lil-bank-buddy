"""
Report generation functionality.

Handles creation of markdown reports with charts and analysis.
"""

import datetime
import os
from pathlib import Path
from typing import Dict, Any
import matplotlib.pyplot as plt
import pandas as pd

from .analysis import BankAnalyzer, ExpenseSplitter
from ..utils.formatters import format_dollar, dict_to_md_table


class ReportGenerator:
    """Generates markdown reports with transaction analysis."""
    
    def __init__(self, db_path: str = None, output_dir: str = 'reports'):
        """
        Initialize the ReportGenerator.
        
        Args:
            db_path: Path to SQLite database (uses default if None)
            output_dir: Directory where reports will be saved
        """
        from .database import DatabaseManager
        
        self.output_dir = Path(output_dir)
        self.db_manager = DatabaseManager(db_path) if db_path else DatabaseManager()
        self.analyzer = BankAnalyzer(self.db_manager)
        self.splitter = ExpenseSplitter(self.db_manager)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_category_pie(self, categories: Dict[str, int], account_name: str, filename: str) -> str:
        """
        Create a pie chart for category data.
        
        Args:
            categories: Dictionary of category names and counts
            account_name: Name of the account for the chart title
            filename: Output filename for the chart
            
        Returns:
            Path to the saved chart file
        """
        if not categories:
            return None
        
        labels = list(categories.keys())
        sizes = list(categories.values())
        
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        plt.title(f'Top Categories - {account_name}')
        plt.tight_layout()
        
        chart_path = self.output_dir / filename
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return str(chart_path)
    
    def generate_current_balance_table(self, balance_data: Dict[str, Any]) -> str:
        """Generate markdown table for current balance split breakdown."""
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
        total_expenses = balance_data['total_expenses']
        person1_total = format_dollar(total_expenses * balance_data['person1_percentage'] / 100)
        person2_total = format_dollar(total_expenses * balance_data['person2_percentage'] / 100)
        rows.append(f"| **TOTAL EXPENSES** | **{format_dollar(total_expenses)}** | **{person1_total}** | **{person2_total}** |")
        
        return header + separator + '\n'.join(rows)
    
    def generate_payment_history_table(self, payment_data: Dict[str, Any]) -> str:
        """Generate markdown table for recent payment history."""
        if not payment_data['recent_payments']:
            return 'No recent payments found'
        
        header = "| Date | Amount | Description |\n"
        separator = "|---|---|---|\n"
        
        rows = []
        for payment in payment_data['recent_payments']:
            amount = format_dollar(payment['amount'])
            rows.append(f"| {payment['date']} | {amount} | {payment['description']} |")
        
        return header + separator + '\n'.join(rows)
    
    def generate_report(
        self, 
        person1_name: str = "Person 1", 
        person2_name: str = "Person 2", 
        person1_percentage: int = 50,
        filename: str = "Bank_Transaction_Report.md"
    ) -> str:
        """
        Generate a comprehensive transaction report.
        
        Args:
            person1_name: Name for person 1
            person2_name: Name for person 2
            person1_percentage: Percentage for person 1 (0-100)
            filename: Output filename for the report
            
        Returns:
            Path to the generated report file
        """
        # Gather all data
        cc_summary = self.analyzer.get_account_summary('team_beeb_cc')
        checking_summary = self.analyzer.get_account_summary('team_beeb_checking')
        cc_recent = self.analyzer.get_recent_activity('team_beeb_cc')
        checking_recent = self.analyzer.get_recent_activity('team_beeb_checking')
        
        # Generate charts
        cc_pie_path = 'cc_top_categories.png'
        checking_pie_path = 'checking_top_categories.png'
        self.plot_category_pie(cc_recent['top_categories'], 'Credit Card', cc_pie_path)
        self.plot_category_pie(checking_recent['top_categories'], 'Checking', checking_pie_path)
        
        # Calculate splits and analyze patterns
        cc_balance_split = self.splitter.calculate_current_balance_split('team_beeb_cc', person1_percentage, person1_name, person2_name)
        checking_balance_split = self.splitter.calculate_current_balance_split('team_beeb_checking', person1_percentage, person1_name, person2_name)
        
        cc_payments = self.analyzer.analyze_payment_patterns('team_beeb_cc')
        checking_payments = self.analyzer.analyze_payment_patterns('team_beeb_checking')
        
        cc_split = self.splitter.calculate_expense_split('team_beeb_cc', person1_percentage, person1_name, person2_name)
        checking_split = self.splitter.calculate_expense_split('team_beeb_checking', person1_percentage, person1_name, person2_name)
        
        # Generate report content
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        report_path = self.output_dir / filename
        
        with open(report_path, 'w') as f:
            self._write_header(f)
            self._write_account_summaries(f, cc_summary, checking_summary)
            self._write_current_balance_analysis(f, person1_name, person2_name, person1_percentage, 
                                               cc_balance_split, checking_balance_split, 
                                               cc_payments, checking_payments)
            self._write_new_expenses_section(f, cc_split, checking_split, person1_name, person2_name)
            self._write_recent_activity(f, cc_recent, checking_recent, cc_pie_path, checking_pie_path)
            self._write_footer(f, now)
        
        return str(report_path)
    
    def _write_header(self, f):
        """Write the report header."""
        f.write("# Bank Accounts Transaction Report\n\n")
        f.write("## Overview\n")
        f.write("This report summarizes key insights and statistics for your bank accounts, ")
        f.write("based on the latest imported transaction data.\n\n---\n\n")
    
    def _write_account_summaries(self, f, cc_summary, checking_summary):
        """Write the account summaries section."""
        f.write("## Account Summaries\n\n")
        f.write("| Account | Total Transactions | Total Amount | Largest Transaction | Most Frequent Category | Date Range |\n")
        f.write("|---|---|---|---|---|---|\n")
        f.write(f"| Credit Card (team_beeb_cc) | {cc_summary['total_transactions']} | {cc_summary['total_amount']} | {cc_summary['largest_transaction']} | {cc_summary['most_frequent_category']} | {cc_summary['date_range'][0]} to {cc_summary['date_range'][1]} |\n")
        f.write(f"| Checking (team_beeb_checking) | {checking_summary['total_transactions']} | {checking_summary['total_amount']} | {checking_summary['largest_transaction']} | {checking_summary['most_frequent_category']} | {checking_summary['date_range'][0]} to {checking_summary['date_range'][1]} |\n\n")
        f.write("---\n\n")
    
    def _write_current_balance_analysis(self, f, person1_name, person2_name, person1_percentage,
                                      cc_balance_split, checking_balance_split, 
                                      cc_payments, checking_payments):
        """Write the current balance analysis section."""
        f.write("## Current Balance Analysis\n\n")
        f.write(f"**Split Ratio:** {person1_name} {person1_percentage}% / {person2_name} {100-person1_percentage}%\n\n")
        f.write("*This section shows the total outstanding balance and how it should be split based on your agreed percentage.*\n\n")
        
        # Credit Card section
        f.write("### Credit Card Current Balance\n")
        f.write(f"- **Total Outstanding Balance:** {format_dollar(cc_balance_split['total_balance'])}\n")
        f.write(f"- **Total Expenses (All Time):** {format_dollar(cc_balance_split['total_expenses'])}\n")
        f.write(f"- **Total Payments Made:** {format_dollar(cc_balance_split['total_payments_credits'])}\n")
        f.write(f"- **{person1_name} Owes:** {format_dollar(cc_balance_split['person1_owes'])}\n")
        f.write(f"- **{person2_name} Owes:** {format_dollar(cc_balance_split['person2_owes'])}\n\n")
        
        f.write("#### Recent Credit Card Payments\n")
        f.write(f"{self.generate_payment_history_table(cc_payments)}\n\n")
        
        f.write("#### Credit Card Expense Breakdown (All Time)\n")
        f.write(f"{self.generate_current_balance_table(cc_balance_split)}\n\n")
        
        # Checking section
        f.write("### Checking Account Current Balance\n")
        f.write(f"- **Total Outstanding Balance:** {format_dollar(checking_balance_split['total_balance'])}\n")
        f.write(f"- **Total Expenses (All Time):** {format_dollar(checking_balance_split['total_expenses'])}\n")
        f.write(f"- **Total Payments Made:** {format_dollar(checking_balance_split['total_payments_credits'])}\n")
        f.write(f"- **{person1_name} Owes:** {format_dollar(checking_balance_split['person1_owes'])}\n")
        f.write(f"- **{person2_name} Owes:** {format_dollar(checking_balance_split['person2_owes'])}\n\n")
        
        f.write("#### Recent Checking Payments\n")
        f.write(f"{self.generate_payment_history_table(checking_payments)}\n\n")
        
        # Settlement summary
        total_combined_balance = cc_balance_split['total_balance'] + checking_balance_split['total_balance']
        total_person1_owes = cc_balance_split['person1_owes'] + checking_balance_split['person1_owes']
        total_person2_owes = cc_balance_split['person2_owes'] + checking_balance_split['person2_owes']
        
        f.write("### 💰 **SETTLEMENT SUMMARY** 💰\n")
        f.write(f"**Total Current Balance Across All Accounts:** {format_dollar(total_combined_balance)}\n\n")
        f.write(f"**💸 {person1_name} owes:** {format_dollar(total_person1_owes)}\n")
        f.write(f"**💸 {person2_name} owes:** {format_dollar(total_person2_owes)}\n\n")
        f.write("---\n\n")
    
    def _write_new_expenses_section(self, f, cc_split, checking_split, person1_name, person2_name):
        """Write the new expenses since last settlement section."""
        f.write("## New Expenses Since Last Settlement\n\n")
        f.write("*This section shows only new expenses since the last detected settlement payments.*\n\n")
        
        # Credit Card new expenses
        f.write("### Credit Card New Expenses\n")
        f.write(f"- **Period:** {cc_split['settlement_info']}\n")
        f.write(f"- **New Expenses:** {format_dollar(cc_split['total_expenses'])}\n")
        f.write(f"- **{person1_name} Share:** {format_dollar(cc_split['person1_share'])}\n")
        f.write(f"- **{person2_name} Share:** {format_dollar(cc_split['person2_share'])}\n")
        f.write(f"- **Expense Transactions:** {cc_split['num_expense_transactions']}\n")
        if cc_split['num_expense_transactions'] > 0:
            f.write(f"- **Date Range:** {cc_split['date_range'][0]} to {cc_split['date_range'][1]}\n\n")
        else:
            f.write("\n")
        
        # Checking new expenses
        f.write("### Checking New Expenses\n")
        f.write(f"- **Period:** {checking_split['settlement_info']}\n")
        f.write(f"- **New Expenses:** {format_dollar(checking_split['total_expenses'])}\n")
        f.write(f"- **{person1_name} Share:** {format_dollar(checking_split['person1_share'])}\n")
        f.write(f"- **{person2_name} Share:** {format_dollar(checking_split['person2_share'])}\n")
        f.write(f"- **Expense Transactions:** {checking_split['num_expense_transactions']}\n")
        if checking_split['num_expense_transactions'] > 0:
            f.write(f"- **Date Range:** {checking_split['date_range'][0]} to {checking_split['date_range'][1]}\n\n")
        else:
            f.write("\n")
        
        f.write("---\n\n")
    
    def _write_recent_activity(self, f, cc_recent, checking_recent, cc_pie_path, checking_pie_path):
        """Write the recent activity section."""
        f.write("## Recent Activity (Last 30 Days)\n\n")
        
        # Credit Card
        f.write("### Credit Card\n")
        f.write(f"- **Number of Transactions:** {cc_recent['num_transactions']}\n")
        f.write(f"- **Total Amount:** {cc_recent['total_amount']}\n")
        f.write(f"- **Top 3 Categories:**\n\n{dict_to_md_table(cc_recent['top_categories'])}\n\n")
        if os.path.exists(self.output_dir / cc_pie_path):
            f.write(f"![Credit Card Top Categories Pie Chart](./{cc_pie_path})\n\n")
        
        # Checking
        f.write("### Checking\n")
        f.write(f"- **Number of Transactions:** {checking_recent['num_transactions']}\n")
        f.write(f"- **Total Amount:** {checking_recent['total_amount']}\n")
        f.write(f"- **Top 3 Categories:**\n\n{dict_to_md_table(checking_recent['top_categories'])}\n\n")
        if os.path.exists(self.output_dir / checking_pie_path):
            f.write(f"![Checking Top Categories Pie Chart](./{checking_pie_path})\n\n")
    
    def _write_footer(self, f, now):
        """Write the report footer."""
        f.write("---\n\n")
        f.write(f"*Report generated on: {now}*\n")
