"""
Sync Work Orders - Every 5 minutes

CRITICAL: Work orders must sync frequently for emergency maintenance
(e.g., burst pipes, HVAC failures, etc.)
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
    logger.info("WORK ORDERS SYNC - Every 5 minutes")
    logger.info("=" * 60)

    try:
        result = sync_details("work_order", use_delta=True)
        logger.info(f"✅ Work orders sync completed: {result}")
        return 0
    except Exception as e:
        logger.error(f"❌ Work orders sync failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
