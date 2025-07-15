#!/usr/bin/env python3
"""
Utility script to clean up test outputs and manage the output directory structure.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import argparse


def show_output_structure():
    """Show the current output directory structure."""
    print("📁 Current Output Directory Structure:")
    print("=" * 50)
    
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print("❌ No outputs directory found")
        return
    
    for item in sorted(outputs_dir.rglob("*")):
        if item.is_file():
            size = item.stat().st_size
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            print(f"  📄 {item.relative_to(outputs_dir)} ({size_str})")
        elif item.is_dir():
            print(f"  📁 {item.relative_to(outputs_dir)}/")


def cleanup_old_test_runs(keep_days=7):
    """Clean up test run directories older than keep_days."""
    print(f"🧹 Cleaning up test runs older than {keep_days} days...")
    
    test_runs_dir = Path("outputs/test_runs")
    if not test_runs_dir.exists():
        print("✅ No test_runs directory found - nothing to clean")
        return
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    cleaned_count = 0
    
    for test_dir in test_runs_dir.iterdir():
        if test_dir.is_dir():
            try:
                # Try to parse directory name for date
                dir_name = test_dir.name
                if dir_name.startswith("test_run_"):
                    # Extract date from test_run_YYYYMMDD_HHMMSS
                    date_str = dir_name.split("_")[2]  # Get YYYYMMDD part
                    dir_date = datetime.strptime(date_str, "%Y%m%d")
                    
                    if dir_date < cutoff_date:
                        shutil.rmtree(test_dir)
                        print(f"  🗑️  Removed: {test_dir.name}")
                        cleaned_count += 1
            except (ValueError, IndexError):
                # If we can't parse the date, skip this directory
                continue
    
    if cleaned_count == 0:
        print("✅ No old test runs found to clean")
    else:
        print(f"✅ Cleaned up {cleaned_count} old test run(s)")


def consolidate_scattered_outputs():
    """Move any scattered test outputs to the proper test_runs directory."""
    print("🔄 Consolidating scattered test outputs...")
    
    # Look for common scattered directory names
    scattered_dirs = [
        "test_output",
        "test_output_fixed", 
        "test_results",
        "outputs/heygen_test"
    ]
    
    consolidated_count = 0
    test_runs_dir = Path("outputs/test_runs")
    test_runs_dir.mkdir(parents=True, exist_ok=True)
    
    for dir_name in scattered_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            # Check if directory has files
            files = list(dir_path.glob("*"))
            if files:
                # Create timestamped subdirectory
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                target_dir = test_runs_dir / f"consolidated_{timestamp}_{dir_path.name}"
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Move files
                for file_path in files:
                    if file_path.is_file():
                        shutil.move(str(file_path), str(target_dir / file_path.name))
                    elif file_path.is_dir():
                        shutil.move(str(file_path), str(target_dir / file_path.name))
                
                print(f"  📦 Moved {len(files)} items from {dir_name} to {target_dir.name}")
                consolidated_count += 1
                
                # Remove empty directory
                try:
                    dir_path.rmdir()
                except OSError:
                    # Directory might not be empty, that's okay
                    pass
    
    if consolidated_count == 0:
        print("✅ No scattered outputs found to consolidate")
    else:
        print(f"✅ Consolidated {consolidated_count} scattered output directory(ies)")


def main():
    parser = argparse.ArgumentParser(description="Clean up and manage test outputs")
    parser.add_argument("--cleanup", action="store_true", 
                       help="Clean up old test runs (older than 7 days)")
    parser.add_argument("--consolidate", action="store_true",
                       help="Consolidate scattered test outputs")
    parser.add_argument("--keep-days", type=int, default=7,
                       help="Number of days to keep test runs (default: 7)")
    parser.add_argument("--show", action="store_true",
                       help="Show current output structure")
    
    args = parser.parse_args()
    
    if not any([args.cleanup, args.consolidate, args.show]):
        # Default: show structure
        args.show = True
    
    if args.show:
        show_output_structure()
        print()
    
    if args.consolidate:
        consolidate_scattered_outputs()
        print()
    
    if args.cleanup:
        cleanup_old_test_runs(args.keep_days)
        print()
    
    if args.show and (args.consolidate or args.cleanup):
        print("📁 Updated Output Directory Structure:")
        print("=" * 50)
        show_output_structure()


if __name__ == "__main__":
    main() 