"""
Natal Chart Service using jyotishganit library.
Generates and parses Vedic birth charts.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from jyotishganit import calculate_birth_chart, get_birth_chart_json_string

from api.models import (
    BirthData,
    NatalChart,
    Planet,
    Sign,
    Nakshatra,
    Dignity,
    PlanetPlacement,
    HouseInfo,
)


class NatalChartService:
    """Service for generating and managing natal charts."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the natal chart service.
        
        Args:
            output_dir: Directory to save chart JSON files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_chart(
        self,
        birth_data: BirthData,
        save_json: bool = True
    ) -> NatalChart:
        """
        Generate a complete natal chart from birth data.
        
        Args:
            birth_data: Birth information (date, location, name)
            save_json: Whether to save the raw JSON output
            
        Returns:
            NatalChart: Parsed natal chart with all placements
        """
        # Calculate birth chart using jyotishganit
        jg_chart = calculate_birth_chart(
            birth_date=birth_data.date,
            latitude=birth_data.location.latitude,
            longitude=birth_data.location.longitude,
            timezone_offset=self._get_timezone_offset(birth_data.location.timezone),
            name=birth_data.name or "Unknown"
        )
        
        # Save raw JSON if requested
        chart_id = str(uuid.uuid4())
        if save_json:
            json_string = get_birth_chart_json_string(jg_chart)
            json_path = self.output_dir / f"chart_{chart_id}.json"
            with open(json_path, "w") as f:
                f.write(json_string)
        
        # Parse the chart into our data model
        json_data = json.loads(get_birth_chart_json_string(jg_chart))
        natal_chart = self._parse_chart(json_data, birth_data, chart_id)
        
        return natal_chart
    
    def _get_timezone_offset(self, timezone_str: str) -> float:
        """
        Get timezone offset in hours from timezone string.
        
        Args:
            timezone_str: Timezone string (e.g., "Asia/Kolkata")
            
        Returns:
            float: Timezone offset in hours
        """
        # Common timezone mappings
        timezone_offsets = {
            "Asia/Kolkata": 5.5,
            "Asia/Calcutta": 5.5,
            "UTC": 0.0,
            "GMT": 0.0,
            "America/New_York": -5.0,
            "America/Los_Angeles": -8.0,
            "Europe/London": 0.0,
            "Australia/Sydney": 10.0,
        }
        
        return timezone_offsets.get(timezone_str, 0.0)
    
    def _parse_chart(
        self,
        json_data: dict,
        birth_data: BirthData,
        chart_id: str
    ) -> NatalChart:
        """
        Parse jyotishganit JSON into NatalChart model.
        
        Args:
            json_data: Raw JSON data from jyotishganit
            birth_data: Original birth data
            chart_id: Unique chart identifier
            
        Returns:
            NatalChart: Parsed natal chart
        """
        d1_chart = json_data["d1Chart"]
        
        # Extract ascendant (from first house)
        first_house = d1_chart["houses"][0]
        ascendant_sign = Sign(first_house["sign"])
        ascendant_degree = first_house.get("signDegrees", 0.0)
        
        # Parse all planet placements
        planets = self._parse_planets(d1_chart["houses"])
        
        # Parse house information
        houses = self._parse_houses(d1_chart["houses"])
        
        # Get Moon sign (Chandra Lagna)
        moon_sign = planets[Planet.MOON].sign
        
        # Create NatalChart
        natal_chart = NatalChart(
            chart_id=chart_id,
            birth_data=birth_data,
            ascendant_sign=ascendant_sign,
            ascendant_degree=ascendant_degree,
            planets=planets,
            houses=houses,
            moon_sign=moon_sign,
            ashtakavarga=None  # Can be added later if needed
        )
        
        return natal_chart

    def _parse_planets(self, houses_data: list) -> Dict[Planet, PlanetPlacement]:
        """
        Parse planet placements from houses data.

        Args:
            houses_data: List of house data from jyotishganit

        Returns:
            Dict mapping Planet to PlanetPlacement
        """
        planets = {}

        for house in houses_data:
            house_number = house["number"]

            for occupant in house.get("occupants", []):
                planet_name = occupant["celestialBody"]

                # Map to our Planet enum
                try:
                    planet = Planet(planet_name)
                except ValueError:
                    continue  # Skip unknown planets

                # Extract placement data
                sign = Sign(occupant["sign"])
                degree = occupant["signDegrees"]
                nakshatra_str = occupant.get("nakshatra")
                nakshatra = self._map_nakshatra(nakshatra_str) if nakshatra_str else None
                nakshatra_pada = occupant.get("pada")

                # Dignity
                dignity_str = occupant.get("dignities", {}).get("dignity")
                dignity = self._map_dignity(dignity_str) if dignity_str else None

                # Retrograde status
                motion_type = occupant.get("motion_type", "direct")
                is_retrograde = motion_type == "retrograde"

                # Lordship houses
                rules_houses = occupant.get("hasLordshipHouses", [])

                # Create PlanetPlacement
                placement = PlanetPlacement(
                    planet=planet,
                    sign=sign,
                    house=house_number,
                    degree=degree,
                    nakshatra=nakshatra,
                    nakshatra_pada=nakshatra_pada,
                    dignity=dignity,
                    is_retrograde=is_retrograde,
                    is_combust=False,  # Can be calculated later
                    rules_houses=rules_houses
                )

                planets[planet] = placement

        return planets

    def _parse_houses(self, houses_data: list) -> Dict[int, HouseInfo]:
        """
        Parse house information from houses data.

        Args:
            houses_data: List of house data from jyotishganit

        Returns:
            Dict mapping house number to HouseInfo
        """
        houses = {}

        for house in houses_data:
            house_number = house["number"]
            sign = Sign(house["sign"])
            lord_str = house["lord"]

            # Map lord to Planet enum
            try:
                lord = Planet(lord_str)
            except ValueError:
                lord = None

            # Get cusp degree (from signDegrees if available)
            degree = house.get("signDegrees", 0.0)

            house_info = HouseInfo(
                house_number=house_number,
                sign=sign,
                degree=degree,
                lord=lord
            )

            houses[house_number] = house_info

        return houses

    def _map_nakshatra(self, nakshatra_str: str) -> Optional[Nakshatra]:
        """
        Map nakshatra string to Nakshatra enum.

        Args:
            nakshatra_str: Nakshatra name from jyotishganit

        Returns:
            Nakshatra enum or None
        """
        # Handle variations in nakshatra names
        nakshatra_mapping = {
            "Ashwini": Nakshatra.ASHWINI,
            "Bharani": Nakshatra.BHARANI,
            "Krittika": Nakshatra.KRITTIKA,
            "Rohini": Nakshatra.ROHINI,
            "Mrigashira": Nakshatra.MRIGASHIRA,
            "Ardra": Nakshatra.ARDRA,
            "Punarvasu": Nakshatra.PUNARVASU,
            "Pushya": Nakshatra.PUSHYA,
            "Ashlesha": Nakshatra.ASHLESHA,
            "Magha": Nakshatra.MAGHA,
            "Purva Phalguni": Nakshatra.PURVA_PHALGUNI,
            "Uttara Phalguni": Nakshatra.UTTARA_PHALGUNI,
            "Hasta": Nakshatra.HASTA,
            "Chitra": Nakshatra.CHITRA,
            "Swati": Nakshatra.SWATI,
            "Vishakha": Nakshatra.VISHAKHA,
            "Anuradha": Nakshatra.ANURADHA,
            "Jyeshtha": Nakshatra.JYESHTHA,
            "Mula": Nakshatra.MULA,
            "Purva Ashadha": Nakshatra.PURVA_ASHADHA,
            "Uttara Ashadha": Nakshatra.UTTARA_ASHADHA,
            "Shravana": Nakshatra.SHRAVANA,
            "Dhanishta": Nakshatra.DHANISHTA,
            "Shatabhisha": Nakshatra.SHATABHISHA,
            "Purva Bhadrapada": Nakshatra.PURVA_BHADRAPADA,
            "Uttara Bhadrapada": Nakshatra.UTTARA_BHADRAPADA,
            "Revati": Nakshatra.REVATI,
        }

        return nakshatra_mapping.get(nakshatra_str)

    def _map_dignity(self, dignity_str: str) -> Optional[Dignity]:
        """
        Map dignity string to Dignity enum.

        Args:
            dignity_str: Dignity name from jyotishganit

        Returns:
            Dignity enum or None
        """
        dignity_mapping = {
            "exalted": Dignity.EXALTED,
            "own_sign": Dignity.OWN_SIGN,
            "moolatrikona": Dignity.MOOLATRIKONA,
            "friendly": Dignity.FRIENDLY,
            "neutral": Dignity.NEUTRAL,
            "enemy": Dignity.ENEMY,
            "debilitated": Dignity.DEBILITATED,
        }

        return dignity_mapping.get(dignity_str.lower() if dignity_str else "")

