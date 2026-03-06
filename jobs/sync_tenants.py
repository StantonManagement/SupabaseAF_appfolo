"""
Sync Tenants - Hourly

Tenant data changes when:
- New tenants move in
- Tenant contact info updated
- Tenant status changes (active/inactive)
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
    logger.info("TENANTS SYNC - Hourly")
    logger.info("=" * 60)

    try:
        result = sync_details("tenant_directory", use_delta=True)
        logger.info(f"✅ Tenants sync completed: {result}")
        return 0
    except Exception as e:
        logger.error(f"❌ Tenants sync failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
