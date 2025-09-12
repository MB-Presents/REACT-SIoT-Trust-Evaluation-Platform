from typing import List
from .models import ExperimentConfiguration
from .factory import ExperimentConfigurationFactory


class ExperimentRegistry:
    """Registry for managing experiment configurations."""
    
    def __init__(self):
        self._experiments: List[ExperimentConfiguration] = []
        self._load_default_experiments()
    
    def _load_default_experiments(self) -> None:
        """Load default experiment configurations."""
        factory = ExperimentConfigurationFactory()
        
        self._experiments = [
            factory.create_mutual_context_aware_experiment(),
            factory.create_cbstm_iot_experiment(),
            factory.create_ctms_siot_experiment()
        ]
    
    def get_all_experiments(self) -> List[ExperimentConfiguration]:
        """Get all registered experiments."""
        return self._experiments.copy()
    
    def add_experiment(self, experiment: ExperimentConfiguration) -> None:
        """Add a new experiment to the registry."""
        experiment.validate()
        self._experiments.append(experiment)
    
    def get_experiment_by_id(self, experiment_id: str) -> ExperimentConfiguration:
        """Get experiment by ID."""
        for exp in self._experiments:
            if exp.experiment_id == experiment_id:
                return exp
        raise ValueError(f"Experiment with ID '{experiment_id}' not found")
    
    def clear(self) -> None:
        """Clear all experiments from registry."""
        self._experiments.clear()