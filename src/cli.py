"""
Main CLI entry point for lil-bank-buddy.
"""

import click
from .commands.import_cmd import import_cmd
from .commands.report_cmd import report_cmd
from .commands.analyze_cmd import analyze_cmd


@click.group()
@click.version_option(version="0.1.0")
@click.pass_context
def cli(ctx):
    """
    🏦 Lil Bank Buddy - Your friendly CLI for bank account analysis and reporting.
    
    Analyze transactions, generate reports, and split expenses with ease.
    """
    ctx.ensure_object(dict)


# Add commands
cli.add_command(import_cmd, name='import')
cli.add_command(report_cmd, name='report')
cli.add_command(analyze_cmd, name='analyze')


def main():
    """Entry point for the CLI application."""
    cli(prog_name="buddy")


if __name__ == '__main__':
    main()
