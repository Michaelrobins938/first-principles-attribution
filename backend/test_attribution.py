"""
Quick test script for the Attribution Engine
Run: python backend/test_attribution.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from models.attribution import Journey, TouchPoint
from engines.attribution import AttributionEngine


def load_test_journeys():
    """Load journeys from the data file or create test data."""
    data_path = os.path.join(
        os.path.dirname(__file__),
        "Data", "attribution_input", "journeys_all.json"
    )
    
    if os.path.exists(data_path):
        print(f"Loading journeys from: {data_path}")
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            journeys = [Journey(**item) for item in data[:1000]]
            print(f"Loaded {len(journeys)} journeys (using first 1000 for testing)")
            return journeys
    
    print("Creating test journeys...")
    journeys = []
    
    test_paths = [
        ["Google_Search", "Facebook_Social", "Direct"],
        ["Facebook_Social", "Direct"],
        ["Google_Search", "Instagram", "Email", "Direct"],
        ["Direct"],
        ["Google_Search", "Direct"],
        ["Facebook_Social", "Instagram", "Direct"],
        ["Email", "Direct"],
        ["Google_Search", "Facebook_Social", "Instagram", "Email", "Direct"],
    ]
    
    from datetime import datetime, timedelta
    
    for i, path in enumerate(test_paths):
        journey = Journey(
            journey_id=f"test_{i:04d}",
            path=[
                TouchPoint(
                    channel=channel,
                    timestamp=datetime.now() - timedelta(hours=len(path) - idx),
                    context=f"test interaction {idx}"
                )
                for idx, channel in enumerate(path)
            ],
            conversion=i % 3 != 0,
            conversion_value=1.0 if i % 3 != 0 else 0.0,
            num_touchpoints=len(path),
            duration_hours=len(path) * 2.5
        )
        journeys.append(journey)
    
    return journeys


def test_markov():
    """Test Markov attribution."""
    print("\n" + "="*50)
    print("Testing Markov Attribution")
    print("="*50)
    
    journeys = load_test_journeys()
    engine = AttributionEngine(journeys)
    
    result = engine.run_analysis(alpha=0.0)
    
    print(f"Total Journeys: {result['total_journeys']}")
    print(f"Total Conversions: {result['total_conversions']}")
    print(f"Unique Channels: {result['unique_channels']}")
    print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
    
    if result['markov_result']:
        print("\nMarkov Attributions:")
        for channel, value in sorted(
            result['markov_result']['channel_attributions'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {channel}: {value:.4f}")
    
    return result


def test_shapley():
    """Test Shapley attribution."""
    print("\n" + "="*50)
    print("Testing Shapley Attribution")
    print("="*50)
    
    journeys = load_test_journeys()
    engine = AttributionEngine(journeys)
    
    result = engine.run_analysis(alpha=1.0)
    
    print(f"Total Journeys: {result['total_journeys']}")
    print(f"Total Conversions: {result['total_conversions']}")
    
    if result['shapley_result']:
        print("\nShapley Values:")
        for channel, value in sorted(
            result['shapley_result']['channel_values'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {channel}: {value:.4f}")
    
    return result


def test_hybrid():
    """Test hybrid attribution."""
    print("\n" + "="*50)
    print("Testing Hybrid Attribution (alpha=0.5)")
    print("="*50)
    
    journeys = load_test_journeys()
    engine = AttributionEngine(journeys)
    
    result = engine.run_analysis(alpha=0.5)
    
    print(f"Total Journeys: {result['total_journeys']}")
    print(f"Total Conversions: {result['total_conversions']}")
    
    if result['hybrid_result']:
        print(f"Alpha Used: {result['hybrid_result']['alpha_used']}")
        print(f"Markov Weight: {result['hybrid_result']['markov_weight']}")
        print(f"Shapley Weight: {result['hybrid_result']['shapley_weight']}")
        
        print("\nHybrid Attributions:")
        for channel, value in sorted(
            result['hybrid_result']['channel_attributions'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {channel}: {value:.4f}")
    
    return result


if __name__ == "__main__":
    print("Attribution Engine Test")
    print("="*50)
    
    try:
        test_markov()
        test_shapley()
        test_hybrid()
        
        print("\n" + "="*50)
        print("All tests passed!")
        print("="*50)
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
