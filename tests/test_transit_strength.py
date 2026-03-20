#!/usr/bin/env python3
"""Test script for transit-based strength calculation."""

from api.services.strength_service import StrengthService
from api.models import Planet, Sign, TransitPlacement, MotionType

def test_transit_strength():
    """Test strength calculation using transit data."""
    strength_service = StrengthService()
    
    # Test 1: Jupiter in Cancer (Exalted) + Retrograde
    print("=" * 60)
    print("Test 1: Jupiter in Cancer (Exalted) + Retrograde")
    print("=" * 60)
    
    jupiter_transit = TransitPlacement(
        planet=Planet.JUPITER,
        sign=Sign.CANCER,
        sign_no=4,
        house=1,
        degree=15.0,
        is_retrograde=True,
        speed=0.05,
        motion_type=MotionType.RETROGRADE
    )
    
    sun_transit = TransitPlacement(
        planet=Planet.SUN,
        sign=Sign.ARIES,
        sign_no=1,
        house=10,
        degree=10.0,
        is_retrograde=False,
        speed=1.0,
        motion_type=MotionType.NORMAL
    )
    
    strength = strength_service.calculate_strength_from_transit(
        Planet.JUPITER,
        jupiter_transit,
        sun_transit
    )
    
    print(f"Sign: {jupiter_transit.sign.value}")
    print(f"Dignity: {strength.breakdown.dignity.value}")
    print(f"Dignity Score: {strength.breakdown.dignity_score}")
    print(f"Retrograde: {strength.breakdown.is_retrograde}")
    print(f"Retrograde Score: {strength.breakdown.retrograde_score}")
    print(f"Combust: {strength.breakdown.is_combust}")
    print(f"Combustion Score: {strength.breakdown.combustion_score}")
    print(f"Total Strength: {strength.breakdown.total_strength}")
    print(f"Strength Weight: {strength.strength_weight}")
    print()
    
    # Test 2: Jupiter in Capricorn (Debilitated)
    print("=" * 60)
    print("Test 2: Jupiter in Capricorn (Debilitated)")
    print("=" * 60)
    
    jupiter_transit2 = TransitPlacement(
        planet=Planet.JUPITER,
        sign=Sign.CAPRICORN,
        sign_no=10,
        house=7,
        degree=20.0,
        is_retrograde=False,
        speed=0.12,
        motion_type=MotionType.NORMAL
    )
    
    strength2 = strength_service.calculate_strength_from_transit(
        Planet.JUPITER,
        jupiter_transit2,
        sun_transit
    )
    
    print(f"Sign: {jupiter_transit2.sign.value}")
    print(f"Dignity: {strength2.breakdown.dignity.value}")
    print(f"Dignity Score: {strength2.breakdown.dignity_score}")
    print(f"Total Strength: {strength2.breakdown.total_strength}")
    print(f"Strength Weight: {strength2.strength_weight}")
    print()
    
    # Test 3: Venus combust (same sign as Sun, within 10 degrees)
    print("=" * 60)
    print("Test 3: Venus Combust (same sign as Sun)")
    print("=" * 60)
    
    venus_transit = TransitPlacement(
        planet=Planet.VENUS,
        sign=Sign.ARIES,
        sign_no=1,
        house=10,
        degree=15.0,  # Within 10 degrees of Sun at 10.0
        is_retrograde=False,
        speed=1.2,
        motion_type=MotionType.NORMAL
    )
    
    strength3 = strength_service.calculate_strength_from_transit(
        Planet.VENUS,
        venus_transit,
        sun_transit
    )
    
    print(f"Sign: {venus_transit.sign.value}")
    print(f"Dignity: {strength3.breakdown.dignity.value}")
    print(f"Combust: {strength3.breakdown.is_combust}")
    print(f"Combustion Score: {strength3.breakdown.combustion_score}")
    print(f"Total Strength: {strength3.breakdown.total_strength}")
    print(f"Strength Weight: {strength3.strength_weight}")
    print()

if __name__ == "__main__":
    test_transit_strength()

