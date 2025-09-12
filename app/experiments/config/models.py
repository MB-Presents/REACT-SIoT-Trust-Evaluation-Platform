from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from trust.adaptive_trust_model_selector.TrustModelSelector import TrustModelSelector
from trust.data_models.TrasactionExchangeScheme import TransactionExchangeScheme
from trust.data_models.reputation.reputation import ReputationComputationStrategy, ReputationContextSettings, ReputationScope
from trust.data_models.transaction.data_models.trust_transaction import Transaction
from trust.decision_making_module.trust_decision_maker import TrustDecisionMethod
from trust.trust_recommenders.trust_model import TrustComputationModel
from trust.trust_update.trust_update import TrustUpdateModel
from .base import BaseConfiguration, ConfigurationValidationError


@dataclass(frozen=True)
class TrustConfiguration(BaseConfiguration):
    """Trust management configuration."""
    
    computation_model: TrustComputationModel
    decision_making_model: TrustDecisionMethod
    update_model: TrustUpdateModel
    transaction_exchange_scheme: TransactionExchangeScheme
    max_transaction_exchange_distance: int = 0
    use_relationship_context: bool = True
    trust_threshold: float = 0.5
    trustworthy_threshold_for_trustee: float = 0.7
    threshold_for_required_trustworthy_relationships: int = 2
    adaptive_trust_model_selector: Optional[TrustModelSelector] = None
    reputation_scope: ReputationScope = ReputationScope.LOCAL
    reputation_context: ReputationContextSettings = ReputationContextSettings.NO_CONTEXT
    reputation_computation_strategy: ReputationComputationStrategy = ReputationComputationStrategy.AVERAGE_OF_LAST_N_TRANSACTIONS
    
    def validate(self) -> None:
        """Validate trust configuration values."""
        if not 0.0 <= self.trust_threshold <= 1.0:
            raise ConfigurationValidationError(
                f"trust_threshold must be between 0.0 and 1.0, got {self.trust_threshold}"
            )
        
        if not 0.0 <= self.trustworthy_threshold_for_trustee <= 1.0:
            raise ConfigurationValidationError(
                f"trustworthy_threshold_for_trustee must be between 0.0 and 1.0, "
                f"got {self.trustworthy_threshold_for_trustee}"
            )
        
        if self.threshold_for_required_trustworthy_relationships < 0:
            raise ConfigurationValidationError(
                f"threshold_for_required_trustworthy_relationships must be >= 0, "
                f"got {self.threshold_for_required_trustworthy_relationships}"
            )


@dataclass(frozen=True)
class ReputationConfiguration(BaseConfiguration):
    """Reputation system configuration."""

    scope: ReputationScope = ReputationScope.LOCAL
    context: ReputationContextSettings = ReputationContextSettings.NO_CONTEXT
    computation_strategy: ReputationComputationStrategy = ReputationComputationStrategy.AVERAGE_OF_LAST_N_TRANSACTIONS


@dataclass(frozen=True)
class AuthenticationConfiguration(BaseConfiguration):
    """Authentication settings configuration."""
    
    verify_accident_authenticity: bool = True
    verify_traffic_light_authenticity: bool = True


@dataclass(frozen=True)
class SimulationConfiguration(BaseConfiguration):
    """Simulation runtime configuration."""
    
    max_simulation_runs: int = 3
    max_traffic_accidents: int = 10
    max_simulation_duration: int = 3600
    accident_interval: int = 100
    false_accident_interval: int = 100
    false_traffic_light_requests_interval: int = 60
    malicious_vehicle_percentage: float = 0.20
    
    def validate(self) -> None:
        """Validate simulation configuration values."""
        if self.max_simulation_runs <= 0:
            raise ConfigurationValidationError(
                f"max_simulation_runs must be > 0, got {self.max_simulation_runs}"
            )
        
        if not 0.0 <= self.malicious_vehicle_percentage <= 1.0:
            raise ConfigurationValidationError(
                f"malicious_vehicle_percentage must be between 0.0 and 1.0, "
                f"got {self.malicious_vehicle_percentage}"
            )
        
        if self.max_simulation_duration <= 0:
            raise ConfigurationValidationError(
                f"max_simulation_duration must be > 0, got {self.max_simulation_duration}"
            )


@dataclass(frozen=True)
class AccidentConfiguration(BaseConfiguration):
    """Accident simulation configuration."""
    
    service_requestor_distance: int = 40
    initial_emergency_parking_time: int = 10800
    parking_time_hospital: int = 3600
    parking_time_accident: int = 20
    reporter_radius: int = 30
    max_accidents: int = 20
    allowed_accident_speed: int = 5
    allowed_road_vehicles: List[str] = field(default_factory=lambda: [
        'private', 'emergency', 'authority', 'army', 'vip', 'passenger', 
        'hov', 'taxi', 'bus', 'coach', 'delivery', 'truck', 'trailer', 
        'motorcycle', 'moped', 'bicycle', 'evehicle', 'custom1', 'custom2'
    ])
    allowed_collision_types: List[str] = field(default_factory=lambda: ['veh_passenger'])
    allowed_fake_collision_types: List[str] = field(default_factory=lambda: [
        "veh_passenger", "truck_truck", "bus_bus"
    ])


@dataclass(frozen=True)
class TrafficLightConfiguration(BaseConfiguration):
    """Traffic light application configuration."""
    
    service_requestor_distance: int = 400
    vehicle_distance_sensing: int = 60
    smart_phone_distance_sensing: int = 60


@dataclass(frozen=True)
class ExperimentConfiguration(BaseConfiguration):
    """Complete experiment configuration."""
    
    # Experiment identification
    experiment_id: str
    experiment_name: str
    trust_model_name: str
    trust_model_description: str
    
    # Component configurations
    trust_config: TrustConfiguration
    reputation_config: ReputationConfiguration
    authentication_config: AuthenticationConfiguration
    simulation_config: SimulationConfiguration
    accident_config: AccidentConfiguration
    traffic_light_config: TrafficLightConfiguration
    
    
    def validate(self) -> None:
        """Validate the entire experiment configuration."""
        if not self.experiment_id:
            raise ConfigurationValidationError("experiment_id cannot be empty")
        
        if not self.experiment_name:
            raise ConfigurationValidationError("experiment_name cannot be empty")
        
        # Validate all sub-configurations
        self.trust_config.validate()
        self.reputation_config.validate()
        self.authentication_config.validate()
        self.simulation_config.validate()
        self.accident_config.validate()
        self.traffic_light_config.validate()