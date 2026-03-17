"""
Configuration for the astrology scoring engine.
All weights and constants from scoreLogic.md.
"""
from typing import Dict, ClassVar
from pydantic import BaseModel, Field
from api.models.enums import Planet, HouseType


class DashaWeights(BaseModel):
    """Weights for different dasha levels (on 0-100 scale)."""
    mahadasha: float = Field(40, description="Mahadasha weight")
    antardasha: float = Field(30, description="Antardasha weight")
    pratyantar: float = Field(20, description="Pratyantar weight")
    sookshma: float = Field(10, description="Sookshma weight")


class PlanetImportance(BaseModel):
    """Importance weights for planets in transit."""
    Sun: float = 0.6
    Moon: float = 0.8
    Mars: float = 0.7
    Mercury: float = 0.5
    Jupiter: float = 1.0
    Venus: float = 0.6
    Saturn: float = 1.0
    Rahu: float = 0.9
    Ketu: float = 0.9
    
    def get_weight(self, planet: Planet) -> float:
        """Get weight for a specific planet."""
        return getattr(self, planet.value)


class HouseImportance(BaseModel):
    """Importance weights for different house types."""
    kendra: float = Field(1.0, description="Kendra houses (1,4,7,10)")
    trikona: float = Field(0.9, description="Trikona houses (1,5,9)")
    upachaya: float = Field(0.8, description="Upachaya houses (3,6,10,11)")
    dusthana: float = Field(0.6, description="Dusthana houses (6,8,12)")
    other: float = Field(0.7, description="Other houses")

    # House type mappings (ClassVar to avoid Pydantic treating them as fields)
    KENDRA_HOUSES: ClassVar[set[int]] = {1, 4, 7, 10}
    TRIKONA_HOUSES: ClassVar[set[int]] = {1, 5, 9}
    UPACHAYA_HOUSES: ClassVar[set[int]] = {3, 6, 10, 11}
    DUSTHANA_HOUSES: ClassVar[set[int]] = {6, 8, 12}
    
    def get_house_weight(self, house: int) -> float:
        """Get weight for a specific house number."""
        # Check in order of priority (some houses belong to multiple categories)
        if house in self.KENDRA_HOUSES:
            return self.kendra
        elif house in self.TRIKONA_HOUSES:
            return self.trikona
        elif house in self.UPACHAYA_HOUSES:
            return self.upachaya
        elif house in self.DUSTHANA_HOUSES:
            return self.dusthana
        else:
            return self.other


class ComponentWeights(BaseModel):
    """Weights for combining different scoring components."""
    dasha: float = Field(0.35, description="Dasha component weight")
    transit: float = Field(0.25, description="Transit component weight")
    strength: float = Field(0.20, description="Planet strength component weight")
    aspect: float = Field(0.12, description="Aspect component weight")
    motion: float = Field(0.08, description="Motion component weight")
    
    def validate_sum(self) -> bool:
        """Ensure weights sum to 1.0."""
        total = self.dasha + self.transit + self.strength + self.aspect + self.motion
        return abs(total - 1.0) < 0.001


class HouseDistribution(BaseModel):
    """Distribution of planet score to different houses."""
    transit: float = Field(0.30, description="Transit house contribution")
    owned: float = Field(0.30, description="Owned houses contribution")
    natal: float = Field(0.20, description="Natal placement contribution")
    aspected: float = Field(0.20, description="Aspected houses contribution")
    
    def validate_sum(self) -> bool:
        """Ensure weights sum to 1.0."""
        total = self.transit + self.owned + self.natal + self.aspected
        return abs(total - 1.0) < 0.001


class ScoringConfig(BaseModel):
    """Complete configuration for the scoring engine."""
    dasha_weights: DashaWeights = Field(default_factory=DashaWeights)
    planet_importance: PlanetImportance = Field(default_factory=PlanetImportance)
    house_importance: HouseImportance = Field(default_factory=HouseImportance)
    component_weights: ComponentWeights = Field(default_factory=ComponentWeights)
    house_distribution: HouseDistribution = Field(default_factory=HouseDistribution)
    
    # Scaling factors
    aspect_scaling_factor: float = Field(20, description="Scaling factor for aspect calculation")
    ashtakavarga_normalization: float = Field(40, description="Normalization value for Ashtakavarga")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dasha_weights": {
                    "mahadasha": 40,
                    "antardasha": 30,
                    "pratyantar": 20,
                    "sookshma": 10
                },
                "component_weights": {
                    "dasha": 0.35,
                    "transit": 0.25,
                    "strength": 0.20,
                    "aspect": 0.12,
                    "motion": 0.08
                }
            }
        }


# Global configuration instance
config = ScoringConfig()

