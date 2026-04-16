"""
my personal project
ADAS Performance Verification Test Script
Author: Prateek Dattaprasad Bhat
Purpose: To Detect AEB
"""

import csv
import pandas as pd
from datetime import datetime


def load_mydrive_data(filename): 
    try:
        df = pd.read_csv(filename)
        print(f"✓ Successfully loaded {len(df)} rows of data")
        return df
    except FileNotFoundError:
        print(f"✗ Error: File '{filename}' not found")
        return None
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return None

def detect_braking_events(df):
    """
    Detect hard braking events.
    A hard braking event = deceleration > 3.0 m/s²
    """
    events = []
    
    for index, row in df.iterrows():
        decel = row['deceleration_ms2']
        speed = row['speed_kmh']
        timestamp = row['timestamp']
        
        if decel > 3.0:
            events.append({
                'timestamp': timestamp,
                'speed_kmh': speed,
                'deceleration_ms2': decel,
                'severity': 'HIGH' if decel > 5.0 else 'MEDIUM'
            })
    
    return events

def test_aeb_requirement(df):
    """
    Test if AEB function meets requirement:
    When target distance < 30m, braking must start within 0.5 seconds
    """
    failures = []
    
    for index, row in df.iterrows():
        distance = row['target_distance_m']
        decel = row['deceleration_ms2']
        timestamp = row['timestamp']
        
        # If car is too close but not braking hard enough
        if distance < 30 and decel < 1.0:
            failures.append({
                'timestamp': timestamp,
                'distance_m': distance,
                'deceleration_ms2': decel,
                'issue': 'Insufficient braking when target too close'
            })
    
    return failures

def create_playlist(df, events):
    """Create a playlist of interesting events (hard braking)"""
    playlist = []
    
    for event in events:
        # Get 1 second before and after the event (for context)
        event_time = event['timestamp']
        start_time = max(0, event_time - 0.5)
        end_time = event_time + 0.5
        
        playlist.append({
            'event_time': event_time,
            'start_time': start_time,
            'end_time': end_time,
            'speed': event['speed_kmh'],
            'deceleration': event['deceleration_ms2'],
            'severity': event['severity']
        })
    
    return playlist


# GENERATE TEST REPORT


def generate_test_report(filename, df, events, failures, playlist):
    """Generate a complete test report in text format"""
    
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("ADAS PERFORMANCE VERIFICATION TEST REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Test Engineer: [Your Name]")
    report_lines.append(f"Data Source: {filename}")
    report_lines.append(f"Total Data Points: {len(df)}")
    report_lines.append("")
    
    # Summary
    report_lines.append("-" * 40)
    report_lines.append("EXECUTIVE SUMMARY")
    report_lines.append("-" * 40)
    report_lines.append(f"Total Braking Events Detected: {len(events)}")
    report_lines.append(f"Total AEB Requirement Failures: {len(failures)}")
    
    if len(failures) == 0:
        report_lines.append("OVERALL RESULT: PASS ✓")
        report_lines.append("All AEB requirements met within specification.")
    else:
        report_lines.append("OVERALL RESULT: FAIL ✗")
        report_lines.append("One or more AEB requirements violated.")
    
    report_lines.append("")
    
    # Detailed events
    report_lines.append("-" * 40)
    report_lines.append("DETECTED HARD BRAKING EVENTS")
    report_lines.append("-" * 40)
    
    if len(events) == 0:
        report_lines.append("No hard braking events detected (deceleration > 3.0 m/s²)")
    else:
        for i, event in enumerate(events, 1):
            report_lines.append(f"{i}. Time: {event['timestamp']}s | Speed: {event['speed_kmh']} km/h | Decel: {event['deceleration_ms2']} m/s² | Severity: {event['severity']}")
    
    report_lines.append("")
    
    # Failures
    report_lines.append("-" * 40)
    report_lines.append("AEB REQUIREMENT FAILURES")
    report_lines.append("-" * 40)
    report_lines.append("Requirement: When target distance < 30m, deceleration must exceed 1.0 m/s²")
    
    if len(failures) == 0:
        report_lines.append("✓ No failures detected")
    else:
        for i, failure in enumerate(failures, 1):
            report_lines.append(f"{i}. Time: {failure['timestamp']}s | Distance: {failure['distance_m']}m | Decel: {failure['deceleration_ms2']} m/s²")
            report_lines.append(f"   Issue: {failure['issue']}")
    
    report_lines.append("")
    
    # Playlist
    report_lines.append("-" * 40)
    report_lines.append("DATA PLAYLIST (Events for Deep Analysis)")
    report_lines.append("-" * 40)
    
    if len(playlist) == 0:
        report_lines.append("No events to add to playlist")
    else:
        for i, clip in enumerate(playlist, 1):
            report_lines.append(f"{i}. {clip['severity']} severity braking at {clip['event_time']}s")
            report_lines.append(f"   → Extract from {clip['start_time']}s to {clip['end_time']}s")
            report_lines.append(f"   → Speed: {clip['speed']} km/h, Decel: {clip['deceleration']} m/s²")
    
    report_lines.append("")
    report_lines.append("=" * 60)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 60)
    
    return "\n".join(report_lines)


# SAVE RESULTS


def save_results_to_csv(events, failures, output_filename):
    """Save detected events and failures to CSV for further analysis"""
    
    # Save events
    if events:
        events_df = pd.DataFrame(events)
        events_df.to_csv('detected_events.csv', index=False)
        print(f"✓ Saved {len(events)} events to 'detected_events.csv'")
    
    # Save failures
    if failures:
        failures_df = pd.DataFrame(failures)
        failures_df.to_csv('test_failures.csv', index=False)
        print(f"✓ Saved {len(failures)} failures to 'test_failures.csv'")
    
    # Save playlist
    if 'playlist' in locals():
        playlist_df = pd.DataFrame(playlist)
        playlist_df.to_csv('playlist.csv', index=False)
        print(f"✓ Saved playlist to 'playlist.csv'")



def main():
    print("\n" + "=" * 50)
    print("ADAS PERFORMANCE VERIFICATION TEST SCRIPT")
    print("=" * 50 + "\n")
    
    # Load the data
    filename = 'test_mydrive_data.csv'  # Change this to your file path
    df = load_mydrive_data(filename)
    
    if df is None:
        print("\nCreating sample data file for you...")
        # Create the sample data if it doesn't exist
        sample_data = """timestamp,speed_kmh,target_distance_m,deceleration_ms2
0.0,45,60,0.0
0.5,46,58,0.2
1.0,48,55,0.3
1.5,50,50,0.4
2.0,51,42,0.5
2.5,52,35,0.6
3.0,53,28,0.8
3.5,54,22,1.2
4.0,52,18,2.0
4.5,48,15,3.5
5.0,42,12,5.0
5.5,35,10,4.5
6.0,30,8,3.0
6.5,25,7,2.0
7.0,20,6,1.5
7.5,15,5,1.0
8.0,10,4,0.5
8.5,5,3,0.2
9.0,0,2,0.0"""
        
        with open(filename, 'w') as f:
            f.write(sample_data)
        print(f"✓ Created '{filename}' with sample drive data\n")
        df = load_drive_data(filename)
    
    # Analyze the data
    print("\n--- ANALYZING DRIVE DATA ---")
    events = detect_braking_events(df)
    print(f"Found {len(events)} hard braking events (deceleration > 3.0 m/s²)")
    
    failures = test_aeb_requirement(df)
    print(f"Found {len(failures)} AEB requirement failures")
    
    playlist = create_playlist(df, events)
    print(f"Created playlist with {len(playlist)} clips for deep analysis")
    
    # Generate report
    print("\n--- GENERATING TEST REPORT ---")
    report = generate_test_report(filename, df, events, failures, playlist)
    
    # Save report to file
    report_filename = f'adas_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(report_filename, 'w') as f:
        f.write(report)
    print(f"✓ Report saved to '{report_filename}'")
    
    # Save additional CSV files
    save_results_to_csv(events, failures, None)
    
    # Print report to screen
    print("\n" + report)
    
    print("\n" + "=" * 50)
    print("✓ TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    main()
