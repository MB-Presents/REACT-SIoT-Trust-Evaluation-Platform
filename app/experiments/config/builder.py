from typing import Optional, List
from .models import (
    ExperimentConfiguration,
    TrustConfiguration,
    ReputationConfiguration,
    AuthenticationConfiguration,
    SimulationConfiguration,
    AccidentConfiguration,
    TrafficLightConfiguration
)


class ExperimentConfigurationBuilder:
    """Builder for creating ExperimentConfiguration instances."""
    
    def __init__(self, experiment_id: str, experiment_name: str):
        self.experiment_id = experiment_id
        self.experiment_name = experiment_name
        self.trust_model_name: Optional[str] = None
        self.trust_model_description: Optional[str] = None
        
        # Initialize with default configurations
        self._trust_config = TrustConfiguration(
            computation_model="",
            decision_making_model="",
            update_model="",
            transaction_exchange_scheme=""
        )
        self._reputation_config = ReputationConfiguration()
        self._authentication_config = AuthenticationConfiguration()
        self._simulation_config = SimulationConfiguration()
        self._accident_config = AccidentConfiguration()
        self._traffic_light_config = TrafficLightConfiguration()
        self._adaptive_trust_model_selector: Optional[str] = None
    
    def with_trust_model(self, name: str, description: str) -> 'ExperimentConfigurationBuilder':
        """Set trust model information."""
        self.trust_model_name = name
        self.trust_model_description = description
        return self
    
    def with_trust_configuration(self, trust_config: TrustConfiguration) -> 'ExperimentConfigurationBuilder':
        """Set trust configuration."""
        self._trust_config = trust_config
        return self
    
    def with_reputation_configuration(self, reputation_config: ReputationConfiguration) -> 'ExperimentConfigurationBuilder':
        """Set reputation configuration."""
        self._reputation_config = reputation_config
        return self
    
    def with_authentication_configuration(self, auth_config: AuthenticationConfiguration) -> 'ExperimentConfigurationBuilder':
        """Set authentication configuration."""
        self._authentication_config = auth_config
        return self
    
    def with_simulation_configuration(self, sim_config: SimulationConfiguration) -> 'ExperimentConfigurationBuilder':
        """Set simulation configuration."""
        self._simulation_config = sim_config
        return self
    
    def with_accident_configuration(self, accident_config: AccidentConfiguration) -> 'ExperimentConfigurationBuilder':
        """Set accident configuration."""
        self._accident_config = accident_config
        return self
    
    def with_traffic_light_configuration(self, traffic_config: TrafficLightConfiguration) -> 'ExperimentConfigurationBuilder':
        """Set traffic light configuration."""
        self._traffic_light_config = traffic_config
        return self
    
    def with_adaptive_trust_model_selector(self, selector: str) -> 'ExperimentConfigurationBuilder':
        """Set adaptive trust model selector."""
        self._adaptive_trust_model_selector = selector
        return self
    
    def build(self) -> ExperimentConfiguration:
        """Build and validate the experiment configuration."""
        if not self.trust_model_name or not self.trust_model_description:
            raise ValueError("Trust model name and description must be set")
        
        config = ExperimentConfiguration(
            experiment_id=self.experiment_id,
            experiment_name=self.experiment_name,
            trust_model_name=self.trust_model_name,
            trust_model_description=self.trust_model_description,
            trust_config=self._trust_config,
            reputation_config=self._reputation_config,
            authentication_config=self._authentication_config,
            simulation_config=self._simulation_config,
            accident_config=self._accident_config,
            traffic_light_config=self._traffic_light_config,
            adaptive_trust_model_selector=self._adaptive_trust_model_selector
        )
        
        config.validate()
        return config