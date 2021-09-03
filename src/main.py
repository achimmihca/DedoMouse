from __future__ import annotations
import logging
from common.version import version
from common.Log import init_logging
from common.AppContext import AppContext

# Setup logging
init_logging()
logging.getLogger('root').info("=============================================")
logging.getLogger('root').info(f"DedoMouse {version} started")
logging.getLogger('root').info("=============================================")

AppContext.configure_json_handlers()
appContext = AppContext()
