"""
Sync Properties/Buildings - Daily

Properties rarely change (only add new properties every 3 months).
Daily sync is sufficient.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.sync import sync_details

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("PROPERTIES/BUILDINGS SYNC - Daily")
    logger.info("=" * 60)

    try:
        # Sync both property_group_directory and buildings (which uses transformation)
        result_properties = sync_details("property_group_directory", use_delta=True)
        logger.info(f"✅ Properties sync completed: {result_properties}")

        result_buildings = sync_details("buildings", use_delta=True)
        logger.info(f"✅ Buildings sync completed: {result_buildings}")

        return 0
    except Exception as e:
        logger.error(f"❌ Properties sync failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
