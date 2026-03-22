import ast
import difflib
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class CodeMetrics:
    complexity: int
    maintainability: float
    test_coverage: Optional[float]
    security_score: float

@dataclass 
class DiffAnalysis:
    added_lines: int
    removed_lines: int
    modified_lines: int
    impact_score: float
    affected_functions: List[str]
    metrics_delta: CodeMetrics

class CodeAnalyzer:
    def __init__(self):
        self.ast_parser = ast.parse
        self.diff_tool = difflib.unified_diff

    def analyze_diff(self, old_code: str, new_code: str) -> DiffAnalysis:
        """Analyzes code differences and generates comprehensive metrics."""
        # Parse both versions
        old_ast = self.ast_parser(old_code)
        new_ast = self.ast_parser(new_code)

        # Generate diff
        diff = list(self.diff_tool(
            old_code.splitlines(True),
            new_code.splitlines(True)
        ))

        # Calculate basic metrics
        added = len([l for l in diff if l.startswith('+')])
        removed = len([l for l in diff if l.startswith('-')])
        modified = len([l for l in diff if l.startswith('?')])

        # Analyze affected functions
        old_functions = self._extract_functions(old_ast)
        new_functions = self._extract_functions(new_ast)
        affected = self._get_affected_functions(old_functions, new_functions)

        # Calculate impact score based on changes
        impact = self._calculate_impact_score(added, removed, modified, affected)

        # Generate metrics delta
        metrics_delta = self._calculate_metrics_delta(old_ast, new_ast)

        return DiffAnalysis(
            added_lines=added,
            removed_lines=removed,
            modified_lines=modified,
            impact_score=impact,
            affected_functions=affected,
            metrics_delta=metrics_delta
        )

    def _extract_functions(self, tree: ast.AST) -> Dict[str, ast.FunctionDef]:
        """Extracts all function definitions from an AST."""
        functions = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = node
        return functions

    def _get_affected_functions(self,
        old_funcs: Dict[str, ast.FunctionDef],
        new_funcs: Dict[str, ast.FunctionDef]) -> List[str]:
        """Identifies functions that were modified between versions."""
        affected = []
        all_names = set(old_funcs.keys()) | set(new_funcs.keys())
        
        for name in all_names:
            if name not in old_funcs:
                affected.append(name)  # New function
            elif name not in new_funcs:
                affected.append(name)  # Removed function
            elif ast.dump(old_funcs[name]) != ast.dump(new_funcs[name]):
                affected.append(name)  # Modified function

        return affected

    def _calculate_impact_score(self,
        added: int,
        removed: int,
        modified: int,
        affected_funcs: List[str]) -> float:
        """Calculates a normalized impact score for the changes."""
        base_score = (added + removed + modified) / 100.0
        func_impact = len(affected_funcs) * 0.5
        return min(1.0, base_score + func_impact)

    def _calculate_metrics_delta(self,
        old_ast: ast.AST,
        new_ast: ast.AST) -> CodeMetrics:
        """Calculates the difference in code quality metrics."""
        old_metrics = self._calculate_metrics(old_ast)
        new_metrics = self._calculate_metrics(new_ast)

        return CodeMetrics(
            complexity=new_metrics.complexity - old_metrics.complexity,
            maintainability=new_metrics.maintainability - old_metrics.maintainability,
            test_coverage=None,  # Requires runtime analysis
            security_score=new_metrics.security_score - old_metrics.security_score
        )

    def _calculate_metrics(self, tree: ast.AST) -> CodeMetrics:
        """Calculates code quality metrics for a single AST."""
        # Simplified metrics calculation
        complexity = sum(1 for _ in ast.walk(tree))
        maintainability = 100.0 - (complexity * 0.1)
        security_score = self._analyze_security(tree)

        return CodeMetrics(
            complexity=complexity,
            maintainability=maintainability,
            test_coverage=None,
            security_score=security_score
        )

    def _analyze_security(self, tree: ast.AST) -> float:
        """Performs basic security analysis of the code."""
        security_score = 100.0
        
        for node in ast.walk(tree):
            # Check for potentially unsafe calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'input']:
                        security_score -= 20.0

        return max(0.0, security_score)
