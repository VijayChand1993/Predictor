"""
Dasha calculation service using jyotishganit library.
"""
from datetime import date, datetime
from typing import Optional, Dict
from pathlib import Path
import json

from api.models import Planet, DashaPeriod, ActiveDashas, DashaWeight
from api.core.config import ScoringConfig


class DashaService:
    """Service for calculating Vimshottari dasha periods."""
    
    def __init__(self, config: Optional[ScoringConfig] = None):
        """
        Initialize dasha service.
        
        Args:
            config: Scoring configuration (optional)
        """
        self.config = config or ScoringConfig()
    
    def get_active_dashas(self, chart_json: dict, target_date: date) -> ActiveDashas:
        """
        Get active dasha periods for a specific date.
        
        Args:
            chart_json: Complete chart JSON from jyotishganit
            target_date: Date for which to get active dashas
            
        Returns:
            ActiveDashas object with current periods
        """
        dashas_data = chart_json.get("dashas", {})
        
        # Try to get from 'current' first, otherwise search through 'all'
        current_dashas = dashas_data.get("current", {})
        
        if current_dashas and "mahadashas" in current_dashas:
            # Parse current dashas
            return self._parse_current_dashas(current_dashas, target_date)
        
        # Fall back to searching through all dashas
        all_dashas = dashas_data.get("all", {}).get("mahadashas", {})
        return self._find_active_dashas(all_dashas, target_date)
    
    def _parse_current_dashas(self, current_dashas: dict, target_date: date) -> ActiveDashas:
        """Parse current dashas from jyotishganit output."""
        mahadashas = current_dashas.get("mahadashas", {})
        
        # Get the first (and should be only) mahadasha
        for md_planet_str, md_data in mahadashas.items():
            md_planet = Planet(md_planet_str)
            md_start = self._parse_date(md_data["start"])
            md_end = self._parse_date(md_data["end"])
            
            mahadasha = DashaPeriod(
                planet=md_planet,
                start_date=md_start,
                end_date=md_end,
                level="mahadasha"
            )
            
            # Get antardasha
            antardashas = md_data.get("antardashas", {})
            for ad_planet_str, ad_data in antardashas.items():
                ad_planet = Planet(ad_planet_str)
                ad_start = self._parse_date(ad_data["start"])
                ad_end = self._parse_date(ad_data["end"])
                
                antardasha = DashaPeriod(
                    planet=ad_planet,
                    start_date=ad_start,
                    end_date=ad_end,
                    level="antardasha"
                )
                
                # Get pratyantar dasha
                pratyantardashas = ad_data.get("pratyantardashas", {})
                pratyantar = None
                
                for pd_planet_str, pd_data in pratyantardashas.items():
                    pd_planet = Planet(pd_planet_str)
                    pd_start = self._parse_date(pd_data["start"])
                    pd_end = self._parse_date(pd_data["end"])
                    
                    pratyantar = DashaPeriod(
                        planet=pd_planet,
                        start_date=pd_start,
                        end_date=pd_end,
                        level="pratyantar"
                    )
                    break  # Take the first one
                
                return ActiveDashas(
                    date=target_date,
                    mahadasha=mahadasha,
                    antardasha=antardasha,
                    pratyantar=pratyantar,
                    sookshma=None  # Not provided in current structure
                )
        
        raise ValueError("No active dashas found in current dashas")
    
    def _find_active_dashas(self, all_mahadashas: dict, target_date: date) -> ActiveDashas:
        """Find active dashas by searching through all periods."""
        for md_planet_str, md_data in all_mahadashas.items():
            md_start = self._parse_date(md_data["start"])
            md_end = self._parse_date(md_data["end"])
            
            if md_start <= target_date <= md_end:
                md_planet = Planet(md_planet_str)
                mahadasha = DashaPeriod(
                    planet=md_planet,
                    start_date=md_start,
                    end_date=md_end,
                    level="mahadasha"
                )
                
                # Find active antardasha
                antardashas = md_data.get("antardashas", {})
                for ad_planet_str, ad_data in antardashas.items():
                    ad_start = self._parse_date(ad_data["start"])
                    ad_end = self._parse_date(ad_data["end"])
                    
                    if ad_start <= target_date <= ad_end:
                        ad_planet = Planet(ad_planet_str)
                        antardasha = DashaPeriod(
                            planet=ad_planet,
                            start_date=ad_start,
                            end_date=ad_end,
                            level="antardasha"
                        )
                        
                        # Find active pratyantar dasha
                        pratyantardashas = ad_data.get("pratyantardashas", {})
                        pratyantar = None
                        
                        for pd_planet_str, pd_data in pratyantardashas.items():
                            pd_start = self._parse_date(pd_data["start"])
                            pd_end = self._parse_date(pd_data["end"])
                            
                            if pd_start <= target_date <= pd_end:
                                pd_planet = Planet(pd_planet_str)
                                pratyantar = DashaPeriod(
                                    planet=pd_planet,
                                    start_date=pd_start,
                                    end_date=pd_end,
                                    level="pratyantar"
                                )
                                break

                        return ActiveDashas(
                            date=target_date,
                            mahadasha=mahadasha,
                            antardasha=antardasha,
                            pratyantar=pratyantar,
                            sookshma=None
                        )

        raise ValueError(f"No active dashas found for date {target_date}")

    def _parse_date(self, date_str: str) -> date:
        """Parse date string from jyotishganit format."""
        # Try different date formats
        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.date()
            except ValueError:
                continue

        # If all formats fail, try ISO format
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.date()
        except ValueError:
            raise ValueError(f"Unable to parse date: {date_str}")

    def calculate_dasha_weight(
        self,
        planet: Planet,
        active_dashas: ActiveDashas
    ) -> DashaWeight:
        """
        Calculate dasha weight for a planet based on active dashas.

        Formula: Score = 40·D_md + 30·D_ad + 20·D_pd + 10·D_sd
        where D_x = 1 if planet matches dasha lord, 0 otherwise

        Args:
            planet: Planet to calculate weight for
            active_dashas: Active dasha periods

        Returns:
            DashaWeight object with detailed scores
        """
        # Calculate individual scores (100 if match, 0 otherwise)
        md_match = 1.0 if active_dashas.mahadasha.planet == planet else 0.0
        ad_match = 1.0 if active_dashas.antardasha.planet == planet else 0.0
        pd_match = 1.0 if active_dashas.pratyantar and active_dashas.pratyantar.planet == planet else 0.0
        sd_match = 1.0 if active_dashas.sookshma and active_dashas.sookshma.planet == planet else 0.0

        # Calculate individual scores (weight if match, 0 otherwise)
        md_score = self.config.dasha_weights.mahadasha * md_match
        ad_score = self.config.dasha_weights.antardasha * ad_match
        pd_score = self.config.dasha_weights.pratyantar * pd_match
        sd_score = self.config.dasha_weights.sookshma * sd_match

        # Calculate weighted total
        total = md_score + ad_score + pd_score + sd_score

        return DashaWeight(
            planet=planet,
            date=active_dashas.date,
            mahadasha_planet=active_dashas.mahadasha.planet,
            antardasha_planet=active_dashas.antardasha.planet,
            pratyantardasha_planet=active_dashas.pratyantar.planet if active_dashas.pratyantar else None,
            sookshmadasha_planet=active_dashas.sookshma.planet if active_dashas.sookshma else None,
            mahadasha_score=md_score,
            antardasha_score=ad_score,
            pratyantardasha_score=pd_score,
            sookshmadasha_score=sd_score,
            total_weight=total
        )

    def get_all_mahadashas(self, chart_json: dict) -> Dict[Planet, DashaPeriod]:
        """
        Get all mahadasha periods from birth chart.

        Args:
            chart_json: Complete chart JSON from jyotishganit

        Returns:
            Dictionary mapping planet to mahadasha period
        """
        dashas_data = chart_json.get("dashas", {})
        all_dashas = dashas_data.get("all", {}).get("mahadashas", {})

        result = {}
        for planet_str, md_data in all_dashas.items():
            planet = Planet(planet_str)
            start = self._parse_date(md_data["start"])
            end = self._parse_date(md_data["end"])

            result[planet] = DashaPeriod(
                planet=planet,
                start_date=start,
                end_date=end,
                level="mahadasha"
            )

        return result

