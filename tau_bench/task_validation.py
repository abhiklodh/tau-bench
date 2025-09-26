"""
Task validation module for syntactic and semantic checks.

This module provides a simplified validation approach for tasks:
1. Syntactic Check: Uses Python compiler to validate action function calls
2. Semantic Check: Automatically invokes functions with database and arguments
"""

import ast
import json
import traceback
from typing import Dict, List, Any, Tuple, Optional, Callable
from tau_bench.types import Task, Action


class TaskValidationError(Exception):
    """Exception raised when task validation fails."""
    pass


class SyntacticValidator:
    """Validates task actions for syntactic correctness."""
    
    @staticmethod
    def validate_action_syntax(action: Action) -> Tuple[bool, Optional[str]]:
        """
        Validate that an action has syntactically correct structure.
        
        Args:
            action: Action object to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if function name is valid Python identifier
            if not action.name.isidentifier():
                return False, f"Invalid function name '{action.name}': not a valid Python identifier"
            
            # Try to create a function call expression and compile it
            kwargs_str = json.dumps(action.kwargs, indent=None)
            function_call = f"{action.name}(**{kwargs_str})"
            
            # Parse as AST to check syntactic validity
            try:
                ast.parse(function_call, mode='eval')
            except SyntaxError as e:
                return False, f"Syntax error in function call: {str(e)}"
            
            # Try to compile the expression
            try:
                compile(function_call, '<string>', 'eval')
            except SyntaxError as e:
                return False, f"Compilation error in function call: {str(e)}"
                
            return True, None
            
        except Exception as e:
            return False, f"Unexpected error during syntax validation: {str(e)}"
    
    @staticmethod
    def validate_task_syntax(task: Task) -> Tuple[bool, List[str]]:
        """
        Validate all actions in a task for syntactic correctness.
        
        Args:
            task: Task object to validate
            
        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        errors = []
        
        for i, action in enumerate(task.actions):
            is_valid, error_msg = SyntacticValidator.validate_action_syntax(action)
            if not is_valid:
                errors.append(f"Action {i} ({action.name}): {error_msg}")
        
        return len(errors) == 0, errors


class SemanticValidator:
    """Validates task actions for semantic correctness by executing them."""
    
    def __init__(self, data: Dict[str, Any], tools: List[Any]):
        """
        Initialize semantic validator with data and tools.
        
        Args:
            data: Environment data dictionary
            tools: List of tool classes
        """
        self.data = data
        self.tool_map = {tool.__name__.lower(): tool for tool in tools}
        
        # Also try to map by the actual function names from get_info
        for tool in tools:
            try:
                info = tool.get_info()
                func_name = info['function']['name']
                self.tool_map[func_name] = tool
            except:
                # If get_info fails, skip this mapping
                pass
    
    def validate_action_semantics(self, action: Action) -> Tuple[bool, Optional[str], Any]:
        """
        Validate that an action can be executed semantically.
        
        Args:
            action: Action object to validate
            
        Returns:
            Tuple of (is_valid, error_message, result)
        """
        try:
            # Find the appropriate tool
            tool_class = None
            
            # Try exact match first
            if action.name in self.tool_map:
                tool_class = self.tool_map[action.name]
            else:
                # Try case-insensitive lookup
                for name, tool in self.tool_map.items():
                    if name.lower() == action.name.lower():
                        tool_class = tool
                        break
            
            if tool_class is None:
                return False, f"Tool '{action.name}' not found in available tools", None
            
            # Try to invoke the tool
            try:
                result = tool_class.invoke(self.data, **action.kwargs)
                return True, None, result
            except TypeError as e:
                return False, f"Invalid arguments for {action.name}: {str(e)}", None
            except Exception as e:
                return False, f"Runtime error in {action.name}: {str(e)}", None
                
        except Exception as e:
            return False, f"Unexpected error during semantic validation: {str(e)}", None
    
    def validate_task_semantics(self, task: Task, stop_on_first_error: bool = False) -> Tuple[bool, List[str], List[Any]]:
        """
        Validate all actions in a task for semantic correctness.
        
        Args:
            task: Task object to validate
            stop_on_first_error: If True, stop validation on first error
            
        Returns:
            Tuple of (all_valid, list_of_errors, list_of_results)
        """
        errors = []
        results = []
        
        for i, action in enumerate(task.actions):
            is_valid, error_msg, result = self.validate_action_semantics(action)
            
            if not is_valid:
                errors.append(f"Action {i} ({action.name}): {error_msg}")
                results.append(None)
                if stop_on_first_error:
                    break
            else:
                results.append(result)
        
        return len(errors) == 0, errors, results


class TaskValidator:
    """Main task validator that combines syntactic and semantic validation."""
    
    def __init__(self, data: Dict[str, Any], tools: List[Any]):
        """
        Initialize task validator.
        
        Args:
            data: Environment data dictionary
            tools: List of tool classes
        """
        self.semantic_validator = SemanticValidator(data, tools)
    
    def validate_task(self, task: Task, skip_semantics: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a task with both syntactic and semantic checks.
        
        Args:
            task: Task object to validate
            skip_semantics: If True, only run syntactic validation
            
        Returns:
            Tuple of (is_valid, validation_report)
        """
        report = {
            'task_id': getattr(task, 'task_id', 'unknown'),
            'user_id': task.user_id,
            'num_actions': len(task.actions),
            'syntactic': {
                'valid': False,
                'errors': []
            },
            'semantic': {
                'valid': False,
                'errors': [],
                'results': []
            },
            'overall_valid': False
        }
        
        # 1. Syntactic validation
        syntax_valid, syntax_errors = SyntacticValidator.validate_task_syntax(task)
        report['syntactic']['valid'] = syntax_valid
        report['syntactic']['errors'] = syntax_errors
        
        if not syntax_valid:
            # If syntax is invalid, don't proceed to semantics
            return False, report
        
        # 2. Semantic validation (if requested and syntax passed)
        if not skip_semantics:
            semantic_valid, semantic_errors, results = self.semantic_validator.validate_task_semantics(task)
            report['semantic']['valid'] = semantic_valid
            report['semantic']['errors'] = semantic_errors
            report['semantic']['results'] = [str(r)[:200] + "..." if r and len(str(r)) > 200 else str(r) for r in results]
            
            report['overall_valid'] = syntax_valid and semantic_valid
        else:
            report['overall_valid'] = syntax_valid
        
        return report['overall_valid'], report
    
    def validate_tasks(self, tasks: List[Task], skip_semantics: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a list of tasks.
        
        Args:
            tasks: List of Task objects to validate
            skip_semantics: If True, only run syntactic validation
            
        Returns:
            Tuple of (all_valid, validation_summary)
        """
        summary = {
            'total_tasks': len(tasks),
            'valid_tasks': 0,
            'failed_tasks': 0,
            'task_reports': [],
            'overall_valid': False
        }
        
        for i, task in enumerate(tasks):
            try:
                is_valid, report = self.validate_task(task, skip_semantics=skip_semantics)
                report['task_index'] = i
                summary['task_reports'].append(report)
                
                if is_valid:
                    summary['valid_tasks'] += 1
                else:
                    summary['failed_tasks'] += 1
                    
            except Exception as e:
                # Handle unexpected errors
                error_report = {
                    'task_index': i,
                    'task_id': getattr(task, 'task_id', 'unknown'),
                    'user_id': getattr(task, 'user_id', 'unknown'),
                    'validation_error': f"Unexpected validation error: {str(e)}",
                    'overall_valid': False
                }
                summary['task_reports'].append(error_report)
                summary['failed_tasks'] += 1
        
        summary['overall_valid'] = summary['failed_tasks'] == 0
        return summary['overall_valid'], summary


def print_validation_summary(summary: Dict[str, Any], verbose: bool = False):
    """Print a formatted validation summary."""
    print(f"\n{'='*60}")
    print(f"TASK VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total tasks: {summary['total_tasks']}")
    print(f"Valid tasks: {summary['valid_tasks']}")
    print(f"Failed tasks: {summary['failed_tasks']}")
    
    if summary['failed_tasks'] > 0:
        print(f"\n❌ FAILED TASKS:")
        for report in summary['task_reports']:
            if not report.get('overall_valid', False):
                task_id = report.get('task_id', 'unknown')
                user_id = report.get('user_id', 'unknown')
                print(f"  Task {report.get('task_index', '?')} ({task_id}, {user_id}):")
                
                if 'validation_error' in report:
                    print(f"    ❌ {report['validation_error']}")
                else:
                    if not report.get('syntactic', {}).get('valid', False):
                        print(f"    ❌ Syntax errors:")
                        for error in report.get('syntactic', {}).get('errors', []):
                            print(f"      - {error}")
                    
                    if not report.get('semantic', {}).get('valid', False):
                        print(f"    ❌ Semantic errors:")
                        for error in report.get('semantic', {}).get('errors', []):
                            print(f"      - {error}")
    
    if summary['overall_valid']:
        print(f"\n🎉 Overall result: ✅ ALL TASKS PASSED")
    else:
        print(f"\n⚠️  Overall result: ❌ {summary['failed_tasks']} TASK(S) FAILED")
        
    if verbose and summary['valid_tasks'] > 0:
        print(f"\n✅ VALID TASKS:")
        for report in summary['task_reports']:
            if report.get('overall_valid', False):
                task_id = report.get('task_id', 'unknown')
                user_id = report.get('user_id', 'unknown')
                num_actions = report.get('num_actions', 0)
                print(f"  Task {report.get('task_index', '?')} ({task_id}, {user_id}) - {num_actions} actions")