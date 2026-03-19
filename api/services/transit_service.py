"""
Transit calculation service using kerykeion.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from kerykeion import AstrologicalSubjectFactory
import json
from pathlib import Path

from api.models import (
    Planet, Sign, TransitPlacement, TransitData,
    TimeSegment, MotionType, NatalChart
)
from api.core.config import ScoringConfig


class TransitService:
    """Service for calculating planetary transits."""
    
    def __init__(self, config: ScoringConfig = None, output_dir: str = "output"):
        self.config = config or ScoringConfig()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def get_transit_data(
        self,
        target_date: datetime,
        natal_chart: NatalChart,
        save_json: bool = False
    ) -> TransitData:
        """
        Get planetary positions for a specific date/time.
        
        Args:
            target_date: Date/time for transit calculation
            natal_chart: Natal chart for house calculation
            save_json: Whether to save raw transit JSON
            
        Returns:
            TransitData with all planetary positions
        """
        # Get location from natal chart
        location = natal_chart.birth_data.location
        
        # Create kerykeion transit chart
        transit_chart = AstrologicalSubjectFactory.from_birth_data(
            name="Transit",
            year=target_date.year,
            month=target_date.month,
            day=target_date.day,
            hour=target_date.hour,
            minute=target_date.minute,
            lng=location.longitude,
            lat=location.latitude,
            tz_str=location.timezone,
            zodiac_type="Sidereal",
            sidereal_mode="LAHIRI",
            online=False
        )
        
        # Parse transit data
        planets = self._parse_transit_planets(transit_chart, natal_chart, target_date)
        
        # Save JSON if requested
        if save_json:
            self._save_transit_json(transit_chart, target_date, location)
        
        return TransitData(
            date=target_date,
            planets=planets
        )
    
    def _parse_transit_planets(
        self,
        transit_chart,
        natal_chart: NatalChart,
        target_date: datetime
    ) -> Dict[Planet, TransitPlacement]:
        """Parse kerykeion transit chart into TransitPlacement objects."""
        
        planets = {}
        
        # Define the 9 planets with their kerykeion attributes
        planet_mapping = [
            (Planet.SUN, "Surya", transit_chart.sun),
            (Planet.MOON, "Chandra", transit_chart.moon),
            (Planet.MARS, "Mangal", transit_chart.mars),
            (Planet.MERCURY, "Budh", transit_chart.mercury),
            (Planet.JUPITER, "Guru", transit_chart.jupiter),
            (Planet.VENUS, "Shukra", transit_chart.venus),
            (Planet.SATURN, "Shani", transit_chart.saturn),
            (Planet.RAHU, "Rahu", transit_chart.true_north_lunar_node),
            (Planet.KETU, "Ketu", transit_chart.true_south_lunar_node),
        ]
        
        for planet_enum, vedic_name, planet_obj in planet_mapping:
            # Get sign number (1-based: 1=Aries, 2=Taurus, ..., 12=Pisces)
            # kerykeion uses 0-based indexing, so we add 1
            sign_num = planet_obj.sign_num + 1

            # Convert to Sign enum
            sign = self._sign_num_to_sign(sign_num)

            # Get degree within sign
            degree = planet_obj.position

            # Calculate house relative to natal ascendant (Whole Sign system)
            house = self._calculate_house(sign_num, degree, natal_chart)
            
            # Get retrograde status
            is_retrograde = planet_obj.retrograde
            
            # Calculate speed
            speed = self._get_average_speed(planet_enum)
            
            # Determine motion type
            motion_type = self._determine_motion_type(planet_enum, speed, is_retrograde)
            
            planets[planet_enum] = TransitPlacement(
                planet=planet_enum,
                sign=sign,
                house=house,
                degree=degree,
                is_retrograde=is_retrograde,
                speed=speed,
                motion_type=motion_type
            )
        
        return planets
    
    def _calculate_house(
        self,
        transit_sign_num: int,
        transit_degree: float,
        natal_chart: NatalChart
    ) -> int:
        """
        Calculate which house a transiting planet occupies.

        House is calculated relative to natal ascendant using Whole Sign house system.
        This matches the traditional Vedic astrology approach where each sign = one house.

        Formula: ((Transit Sign - Natal Lagna Sign) % 12) + 1
        """
        # Get natal ascendant sign
        asc_sign = natal_chart.ascendant_sign

        # Convert ascendant sign to number (1-12)
        natal_lagna_sign_num = self._sign_to_num(asc_sign)

        # Calculate house position relative to natal Lagna using Whole Sign system
        # Each zodiac sign = one house, starting from ascendant sign
        house_from_lagna = ((transit_sign_num - natal_lagna_sign_num) % 12) + 1

        return house_from_lagna

    def calculate_transit_weight(
        self,
        planet: Planet,
        transit_house: int
    ) -> float:
        """
        Calculate transit weight for a planet.

        Formula: W_transit(p) = 100 × PlanetWeight(p) × HouseWeight(h_transit)

        Args:
            planet: The transiting planet
            transit_house: House number the planet is transiting

        Returns:
            Transit weight (0-100 range)
        """
        planet_weight = self.config.planet_importance.get_weight(planet)
        house_weight = self.config.house_importance.get_house_weight(transit_house)

        return 100 * planet_weight * house_weight

    def get_time_segments(
        self,
        start_date: datetime,
        end_date: datetime,
        natal_chart: NatalChart,
        fast_planets: List[Planet] = None
    ) -> List[TimeSegment]:
        """
        Generate time segments based on transit changes.

        Detects sign changes for fast-moving planets (Moon, Sun, Mars, Mercury)
        and creates segments where planetary positions are constant.

        Args:
            start_date: Start of date range
            end_date: End of date range
            natal_chart: Natal chart for house calculations
            fast_planets: List of planets to track (default: Moon, Sun, Mars, Mercury)

        Returns:
            List of TimeSegment objects
        """
        if fast_planets is None:
            fast_planets = [Planet.MOON, Planet.SUN, Planet.MARS, Planet.MERCURY]

        segments = []
        current_date = start_date

        # Get initial transit data
        current_transit = self.get_transit_data(current_date, natal_chart)
        segment_start = current_date

        # Iterate through date range
        while current_date <= end_date:
            # Move to next day
            next_date = current_date + timedelta(days=1)

            if next_date > end_date:
                # Create final segment
                segments.append(TimeSegment(
                    start_date=segment_start,
                    end_date=end_date,
                    transit_data=current_transit
                ))
                break

            # Get next day's transit
            next_transit = self.get_transit_data(next_date, natal_chart)

            # Check if any fast planet changed sign
            sign_changed = False
            for planet in fast_planets:
                if current_transit.planets[planet].sign != next_transit.planets[planet].sign:
                    sign_changed = True
                    break

            if sign_changed:
                # Create segment for current period
                segments.append(TimeSegment(
                    start_date=segment_start,
                    end_date=current_date,
                    transit_data=current_transit
                ))

                # Start new segment
                segment_start = next_date
                current_transit = next_transit

            current_date = next_date

        return segments

    def _sign_to_num(self, sign: Sign) -> int:
        """Convert Sign enum to number (1-12)."""
        sign_to_num = {
            Sign.ARIES: 1, Sign.TAURUS: 2, Sign.GEMINI: 3,
            Sign.CANCER: 4, Sign.LEO: 5, Sign.VIRGO: 6,
            Sign.LIBRA: 7, Sign.SCORPIO: 8, Sign.SAGITTARIUS: 9,
            Sign.CAPRICORN: 10, Sign.AQUARIUS: 11, Sign.PISCES: 12
        }
        return sign_to_num[sign]

    def _sign_num_to_sign(self, num: int) -> Sign:
        """Convert number (1-12) to Sign enum."""
        num_to_sign = {
            1: Sign.ARIES, 2: Sign.TAURUS, 3: Sign.GEMINI,
            4: Sign.CANCER, 5: Sign.LEO, 6: Sign.VIRGO,
            7: Sign.LIBRA, 8: Sign.SCORPIO, 9: Sign.SAGITTARIUS,
            10: Sign.CAPRICORN, 11: Sign.AQUARIUS, 12: Sign.PISCES
        }
        return num_to_sign[num]

    def _get_average_speed(self, planet: Planet) -> float:
        """Get average speed for a planet in degrees per day."""
        average_speeds = {
            Planet.SUN: 1.0,
            Planet.MOON: 13.2,
            Planet.MARS: 0.5,
            Planet.MERCURY: 1.2,
            Planet.JUPITER: 0.08,
            Planet.VENUS: 1.0,
            Planet.SATURN: 0.03,
            Planet.RAHU: 0.05,
            Planet.KETU: 0.05
        }
        return average_speeds.get(planet, 0.5)

    def _determine_motion_type(
        self,
        planet: Planet,
        speed: float,
        is_retrograde: bool
    ) -> MotionType:
        """Determine motion type based on speed and retrograde status."""
        if is_retrograde:
            return MotionType.RETROGRADE

        # Define speed thresholds for each planet
        if planet == Planet.MOON:
            if speed > 14.0:
                return MotionType.FAST
            elif speed < 12.0:
                return MotionType.SLOW
            elif speed < 0.1:
                return MotionType.STATIONARY
            else:
                return MotionType.NORMAL
        elif planet == Planet.SUN:
            if speed > 1.05:
                return MotionType.FAST
            elif speed < 0.95:
                return MotionType.SLOW
            elif speed < 0.01:
                return MotionType.STATIONARY
            else:
                return MotionType.NORMAL
        elif planet in [Planet.MERCURY, Planet.VENUS]:
            if speed < 0.1:
                return MotionType.STATIONARY
            elif speed > 1.5:
                return MotionType.FAST
            elif speed < 0.5:
                return MotionType.SLOW
            else:
                return MotionType.NORMAL
        elif planet in [Planet.MARS, Planet.JUPITER, Planet.SATURN]:
            if speed < 0.01:
                return MotionType.STATIONARY
            else:
                return MotionType.NORMAL

        return MotionType.NORMAL

    def _save_transit_json(
        self,
        transit_chart,
        target_date: datetime,
        location
    ) -> None:
        """Save raw transit data as JSON."""
        # Build JSON structure
        transit_json = {
            "date": target_date.strftime("%Y-%m-%d"),
            "time": target_date.strftime("%H:%M:%S"),
            "location": f"{location.city}, {location.country}",
            "zodiac_type": "Sidereal (Lahiri)",
            "planets": []
        }

        # Define the 9 planets
        planets = [
            ("Sun", "Surya", transit_chart.sun),
            ("Moon", "Chandra", transit_chart.moon),
            ("Mars", "Mangal", transit_chart.mars),
            ("Mercury", "Budh", transit_chart.mercury),
            ("Jupiter", "Guru", transit_chart.jupiter),
            ("Venus", "Shukra", transit_chart.venus),
            ("Saturn", "Shani", transit_chart.saturn),
            ("Rahu", "Rahu", transit_chart.true_north_lunar_node),
            ("Ketu", "Ketu", transit_chart.true_south_lunar_node),
        ]

        for planet_name, vedic_name, planet_obj in planets:
            sign_num = 1 if planet_obj.sign_num + 1 == 13 else planet_obj.sign_num + 1
            planet_data = {
                "name": planet_name,
                "vedic_name": vedic_name,
                "sign_num": sign_num,
                "degree": round(planet_obj.position, 2),
                "retrograde": planet_obj.retrograde
            }
            transit_json["planets"].append(planet_data)

        # Save to file
        filename = f"transit_{target_date.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(transit_json, f, indent=2)

        print(f"Transit data saved to {filepath}")

