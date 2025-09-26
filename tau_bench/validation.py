# Copyright Sierra

"""Generic task validation module for syntactic and semantic checks."""

from hashlib import sha256
from typing import Any, Dict, List, Set, Tuple, Union, Callable
from tau_bench.types import Action, Task, RewardResult, RewardOutputInfo, RewardActionInfo, RESPOND_ACTION_NAME


ToHashable = Union[
    str, int, float, Dict[str, "ToHashable"], List["ToHashable"], Set["ToHashable"]
]
Hashable = Union[str, int, float, Tuple["Hashable"], Tuple[Tuple[str, "Hashable"]]]


def to_hashable(item: ToHashable) -> Hashable:
    """Convert a potentially unhashable item to a hashable representation."""
    if isinstance(item, dict):
        return tuple((key, to_hashable(value)) for key, value in sorted(item.items()))
    elif isinstance(item, list):
        return tuple(to_hashable(element) for element in item)
    elif isinstance(item, set):
        return tuple(sorted(to_hashable(element) for element in item))
    else:
        return item


def consistent_hash(value: Hashable) -> str:
    """Generate a consistent hash for a hashable value."""
    return sha256(str(value).encode("utf-8")).hexdigest()


class TaskValidator:
    """Generic task validation system for syntactic and semantic checks."""
    
    def __init__(
        self,
        data_load_func: Callable[[], Dict[str, Any]],
        tools_map: Dict[str, Any],
        terminate_tools: List[str]
    ):
        """
        Initialize the task validator.
        
        Args:
            data_load_func: Function to load/reset environment data
            tools_map: Mapping of tool names to tool classes 
            terminate_tools: List of tool names that terminate execution
        """
        self.data_load_func = data_load_func
        self.tools_map = tools_map
        self.terminate_tools = terminate_tools
    
    def get_data_hash(self, data: Dict[str, Any]) -> str:
        """Generate a hash of the current data state."""
        return consistent_hash(to_hashable(data))
    
    def execute_action(self, action: Action, data: Dict[str, Any]) -> None:
        """Execute a single action on the data."""
        if action.name in self.tools_map and action.name not in self.terminate_tools:
            try:
                self.tools_map[action.name].invoke(data=data, **action.kwargs)
            except Exception:
                # Ignore exceptions during validation execution
                pass
    
    def validate_syntactic(self, task: Task, current_data: Dict[str, Any]) -> RewardActionInfo:
        """
        Perform syntactic validation by checking if database changes match expected.
        
        Args:
            task: The task with ground truth actions
            current_data: Current state of the environment data
            
        Returns:
            RewardActionInfo with validation result
        """
        current_data_hash = self.get_data_hash(current_data)
        
        # Execute ground truth actions to get expected final state
        gt_data = self.data_load_func()
        for action in task.actions:
            self.execute_action(action, gt_data)
        gt_data_hash = self.get_data_hash(gt_data)
        
        return RewardActionInfo(
            r_actions=current_data_hash == gt_data_hash,
            gt_data_hash=gt_data_hash
        )
    
    def validate_semantic(self, task: Task, agent_actions: List[Action]) -> RewardOutputInfo:
        """
        Perform semantic validation by checking if expected outputs are present.
        
        Args:
            task: The task with expected outputs
            agent_actions: Actions taken by the agent
            
        Returns:
            RewardOutputInfo with validation result
        """
        if not task.outputs:
            # No outputs to validate
            return RewardOutputInfo(r_outputs=1.0, outputs={})
        
        r_outputs = 1.0
        outputs = {}
        
        for expected_output in task.outputs:
            found = False
            for action in agent_actions:
                if (
                    action.name == RESPOND_ACTION_NAME
                    and expected_output.lower()
                    in action.kwargs["content"].lower().replace(",", "")
                ):
                    found = True
                    break
            outputs[expected_output] = found
            if not found:
                r_outputs = 0.0
        
        return RewardOutputInfo(r_outputs=r_outputs, outputs=outputs)
    
    def validate_task(
        self, 
        task: Task, 
        agent_actions: List[Action], 
        current_data: Dict[str, Any]
    ) -> RewardResult:
        """
        Perform complete task validation including both syntactic and semantic checks.
        
        Args:
            task: The task to validate
            agent_actions: Actions taken by the agent
            current_data: Current state of the environment data
            
        Returns:
            RewardResult with overall validation outcome
        """
        reward = 1.0
        
        # Filter out respond actions for syntactic validation
        non_respond_actions = [
            action for action in task.actions if action.name != RESPOND_ACTION_NAME
        ]
        
        # Syntactic validation - check database changes
        syntactic_info = self.validate_syntactic(task, current_data)
        if not syntactic_info.r_actions:
            reward = 0.0
        
        # Semantic validation - check outputs
        semantic_info = self.validate_semantic(task, agent_actions)
        if semantic_info.r_outputs < 1.0:
            reward = 0.0
        
        # Return the appropriate info based on what was validated
        info = semantic_info if task.outputs else syntactic_info
        
        return RewardResult(reward=reward, info=info, actions=non_respond_actions)