"""
Sync Units - Hourly

Unit data changes when:
- Unit becomes vacant/occupied
- Unit details updated (rent, amenities)
- New units added
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
    logger.info("UNITS SYNC - Hourly")
    logger.info("=" * 60)

    try:
        result = sync_details("unit_directory", use_delta=True)
        logger.info(f"✅ Units sync completed: {result}")
        return 0
    except Exception as e:
        logger.error(f"❌ Units sync failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
