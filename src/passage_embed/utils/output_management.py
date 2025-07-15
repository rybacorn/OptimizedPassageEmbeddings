"""Output directory management utilities for passage embedding analysis."""

from pathlib import Path
from typing import Optional
from ..core.config import Config


def get_output_directory(config: Optional[Config] = None, is_test: bool = False) -> Path:
    """Get the appropriate output directory based on configuration and context.
    
    Args:
        config: Configuration object. If None, loads default config.
        is_test: Whether this is a test run. If True, uses test_output_dir.
        
    Returns:
        Path to the output directory
    """
    if config is None:
        config = Config.load_from_file()
    
    if is_test:
        output_path = Path(config.test_output_dir)
    else:
        output_path = Path(config.output_dir)
    
    # Ensure directory exists
    output_path.mkdir(parents=True, exist_ok=True)
    
    return output_path


def create_test_run_directory(config: Optional[Config] = None, run_name: Optional[str] = None) -> Path:
    """Create a specific test run directory with optional run name.
    
    Args:
        config: Configuration object. If None, loads default config.
        run_name: Optional name for this test run. If None, uses timestamp.
        
    Returns:
        Path to the test run directory
    """
    from datetime import datetime
    
    if config is None:
        config = Config.load_from_file()
    
    base_test_dir = Path(config.test_output_dir)
    base_test_dir.mkdir(parents=True, exist_ok=True)
    
    if run_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"test_run_{timestamp}"
    
    test_run_dir = base_test_dir / run_name
    test_run_dir.mkdir(parents=True, exist_ok=True)
    
    return test_run_dir


def cleanup_old_test_runs(config: Optional[Config] = None, keep_days: int = 7) -> None:
    """Clean up old test run directories.
    
    Args:
        config: Configuration object. If None, loads default config.
        keep_days: Number of days to keep test runs
    """
    from datetime import datetime, timedelta
    
    if config is None:
        config = Config.load_from_file()
    
    base_test_dir = Path(config.test_output_dir)
    if not base_test_dir.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    
    for test_dir in base_test_dir.iterdir():
        if test_dir.is_dir():
            # Try to parse directory name for date
            try:
                # Assume format: test_run_YYYYMMDD_HHMMSS
                dir_name = test_dir.name
                if dir_name.startswith("test_run_"):
                    date_str = dir_name.split("_")[2]  # Get YYYYMMDD part
                    dir_date = datetime.strptime(date_str, "%Y%m%d")
                    
                    if dir_date < cutoff_date:
                        import shutil
                        shutil.rmtree(test_dir)
                        print(f"Cleaned up old test run: {test_dir}")
            except (ValueError, IndexError):
                # If we can't parse the date, skip this directory
                continue 