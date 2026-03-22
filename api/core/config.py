"""
Configuration for the astrology scoring engine.
All weights and constants from scoreLogic.md.
"""
from typing import Dict, ClassVar
from pydantic import BaseModel, Field
from api.models.enums import Planet, HouseType


class DashaWeights(BaseModel):
    """
    Weights for different dasha levels (multiplicative factors, not additive).

    These are used to calculate dasha_factor = 0.2 + 0.8 * (50*md + 30*ad + 20*pd)/100
    where md, ad, pd are 0 or 1 (match or no match).

    CRITICAL: These are ABSOLUTE values (50, 30, 20), NOT fractions (0.5, 0.3, 0.2)
    """
    mahadasha: float = Field(50.0, description="Mahadasha contribution (50 points)")
    antardasha: float = Field(30.0, description="Antardasha contribution (30 points)")
    pratyantar: float = Field(20.0, description="Pratyantar contribution (20 points)")
    sookshma: float = Field(0.0, description="Sookshma contribution (0 points - too granular)")

    # Dasha gate parameters
    baseline: float = Field(0.20, description="Baseline factor for non-dasha planets (20%)")
    multiplier: float = Field(0.80, description="Multiplier for dasha strength (80%)")


class PlanetImportance(BaseModel):
    """
    Importance weights for planets (multiplicative factors).

    Based on traditional Vedic hierarchy:
    - Slow planets (Saturn, Jupiter) dominate long-term trends
    - Fast planets (Moon, Mercury) create short-term fluctuations
    """
    Saturn: float = 1.30   # Slowest, most karmic, long-term impact
    Jupiter: float = 1.20  # Great benefic, slow-moving, expansive
    Rahu: float = 1.15     # Shadow planet, karmic, ambitious
    Ketu: float = 1.15     # Shadow planet, spiritual, detachment
    Mars: float = 1.00     # Baseline (medium speed, action-oriented)
    Sun: float = 0.90      # Fast but important (soul, authority)
    Venus: float = 0.90    # Fast benefic (relationships, beauty)
    Mercury: float = 0.85  # Very fast, changeable (intellect)
    Moon: float = 0.75     # Fastest, most changeable (mind, emotions)

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
    """
    Weights for combining different scoring components.

    NOTE: Dasha is NOT included here - it's a MULTIPLICATIVE factor, not additive.
    Dasha gates/amplifies the base score, it doesn't contribute to it.
    """
    transit: float = Field(0.35, description="Transit component weight (where planet is now)")
    strength: float = Field(0.30, description="Planet strength component weight (dignity, combustion)")
    aspect: float = Field(0.20, description="Aspect component weight (houses aspected)")
    motion: float = Field(0.15, description="Motion component weight (retrograde, speed)")

    def validate_sum(self) -> bool:
        """Ensure weights sum to 1.0."""
        total = self.transit + self.strength + self.aspect + self.motion
        return abs(total - 1.0) < 0.001


class HouseDistribution(BaseModel):
    """
    Distribution of planet score to different houses.

    Transit is weighted highest because it represents current reality.
    """
    transit: float = Field(0.40, description="Transit house contribution (current reality)")
    owned: float = Field(0.25, description="Owned houses contribution (background potential)")
    natal: float = Field(0.20, description="Natal placement contribution (birth chart)")
    aspected: float = Field(0.15, description="Aspected houses contribution (influence)")

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
                    "mahadasha": 50.0,
                    "antardasha": 30.0,
                    "pratyantar": 20.0,
                    "sookshma": 0.0,
                    "baseline": 0.20,
                    "multiplier": 0.80
                },
                "component_weights": {
                    "transit": 0.35,
                    "strength": 0.30,
                    "aspect": 0.20,
                    "motion": 0.15
                }
            }
        }


# Global configuration instance
config = ScoringConfig()

