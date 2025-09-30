"""SQL Parser Utility - Parses SQL content into individual statements"""
from typing import List
from .logging import get_logger

log = get_logger(__name__)


def remove_comments_and_empty_lines(sql_content: str) -> str:
    """Remove SQL comments and empty lines"""
    lines = []
    for line in sql_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('--') and not line.startswith('#'):
            lines.append(line)
    return ' '.join(lines)


def split_by_semicolon(sql_text: str) -> List[str]:
    """
    Split SQL text by semicolon while preserving quoted strings.
    
    Handles both single (') and double (") quotes correctly.
    """
    statements = []
    current_statement = ""
    in_quotes = False
    quote_char = None
    
    for char in sql_text:
        # Handle quotes
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
        
        # Handle semicolon
        if char == ';' and not in_quotes:
            if current_statement.strip():
                statements.append(current_statement.strip())
            current_statement = ""
        else:
            current_statement += char
    
    # Add final statement if exists
    if current_statement.strip():
        statements.append(current_statement.strip())
    
    return statements


def parse_sql_statements(sql_content: str) -> List[str]:
    """
    Parse SQL content into individual executable statements.
    
    Args:
        sql_content: Raw SQL text with comments and multiple statements
        
    Returns:
        List of individual SQL statements
    """
    log.info("Parsing SQL statements")
    
    # Remove comments and empty lines
    cleaned_sql = remove_comments_and_empty_lines(sql_content)
    
    # Split by semicolon while preserving quotes
    statements = split_by_semicolon(cleaned_sql)
    
    # Filter out empty statements
    statements = [stmt for stmt in statements if stmt.strip()]
    
    log.info(f"✓ Parsed {len(statements)} SQL statements")
    return statements
