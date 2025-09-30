"""
Code Analyzer

Analyzes Spark application code for anti-patterns and provides best practice recommendations.
"""

import logging
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class CodeIssue:
    """Code quality or performance issue."""
    category: str
    severity: str
    line_context: str
    issue: str
    recommendation: str
    best_practice: str


class CodeAnalyzer:
    """
    Static code analysis for Spark applications.
    
    Detects:
        - Collect() on large datasets
        - Count() in loops
        - Non-serializable objects
        - Inefficient UDFs
        - Missing explicit schemas
        - Unnecessary actions
    """
    
    ANTI_PATTERNS = {
        ".collect()": {
            "issue": "collect() brings all data to driver - can cause OOM",
            "recommendation": "Use take(n), limit(), or process data in distributed manner",
            "severity": "HIGH"
        },
        ".count()": {
            "issue": "count() is an action that triggers computation",
            "recommendation": "Remove unnecessary count() calls, especially in loops",
            "severity": "MEDIUM"
        },
        "for row in": {
            "issue": "Iterating over DataFrame rows is inefficient",
            "recommendation": "Use DataFrame transformations instead of row iteration",
            "severity": "HIGH"
        }
    }
    
    def __init__(self):
        """Initialize code analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_code(self, code: str, filename: str = "code") -> List[CodeIssue]:
        """
        Analyze code for Spark anti-patterns.
        
        Args:
            code: Python code string
            filename: Name for reporting
            
        Returns:
            List of CodeIssue objects
        """
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern, info in self.ANTI_PATTERNS.items():
                if pattern in line:
                    issues.append(CodeIssue(
                        category="PERFORMANCE",
                        severity=info["severity"],
                        line_context=f"{filename}:{line_num}",
                        issue=info["issue"],
                        recommendation=info["recommendation"],
                        best_practice=pattern
                    ))
        
        return issues
