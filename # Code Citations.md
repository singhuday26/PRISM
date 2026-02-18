# Code Citations

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/aahilario/phlegiscope/blob/94fb6d9070ab93a80a48d0eed2b8f7170151abdc/legiscope.nodejs/sp-test.js

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/aahilario/phlegiscope/blob/94fb6d9070ab93a80a48d0eed2b8f7170151abdc/legiscope.nodejs/sp-test.js

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/aahilario/phlegiscope/blob/94fb6d9070ab93a80a48d0eed2b8f7170151abdc/legiscope.nodejs/sp-test.js

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: Apache-2.0

https://github.com/Znerual/FastLogin/blob/5c203ea995a605dbe1f5bf4a39114784a0fff449/client.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/aahilario/phlegiscope/blob/94fb6d9070ab93a80a48d0eed2b8f7170151abdc/legiscope.nodejs/sp-test.js

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: Apache-2.0

https://github.com/Znerual/FastLogin/blob/5c203ea995a605dbe1f5bf4a39114784a0fff449/client.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/aahilario/phlegiscope/blob/94fb6d9070ab93a80a48d0eed2b8f7170151abdc/legiscope.nodejs/sp-test.js

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: Apache-2.0

https://github.com/Znerual/FastLogin/blob/5c203ea995a605dbe1f5bf4a39114784a0fff449/client.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/aahilario/phlegiscope/blob/94fb6d9070ab93a80a48d0eed2b8f7170151abdc/legiscope.nodejs/sp-test.js

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: Apache-2.0

https://github.com/Znerual/FastLogin/blob/5c203ea995a605dbe1f5bf4a39114784a0fff449/client.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/aahilario/phlegiscope/blob/94fb6d9070ab93a80a48d0eed2b8f7170151abdc/legiscope.nodejs/sp-test.js

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: Apache-2.0

https://github.com/Znerual/FastLogin/blob/5c203ea995a605dbe1f5bf4a39114784a0fff449/client.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/aahilario/phlegiscope/blob/94fb6d9070ab93a80a48d0eed2b8f7170151abdc/legiscope.nodejs/sp-test.js

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: Apache-2.0

https://github.com/Znerual/FastLogin/blob/5c203ea995a605dbe1f5bf4a39114784a0fff449/client.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/aahilario/phlegiscope/blob/94fb6d9070ab93a80a48d0eed2b8f7170151abdc/legiscope.nodejs/sp-test.js

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "
`````

## License: Apache-2.0

https://github.com/Znerual/FastLogin/blob/5c203ea995a605dbe1f5bf4a39114784a0fff449/client.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/aahilario/phlegiscope/blob/94fb6d9070ab93a80a48d0eed2b8f7170151abdc/legiscope.nodejs/sp-test.js

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: Apache-2.0

https://github.com/Znerual/FastLogin/blob/5c203ea995a605dbe1f5bf4a39114784a0fff449/client.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/hyz/dotfiles/blob/b16a8639f1bb4a684ae122ded46e7d62d37b31f1/bin/get-em.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/fbb4c92aa5b6f26fd7fd51ed8a32831c4c689686/2023/12/07/parseHeaders.mjs

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/aahilario/phlegiscope/blob/94fb6d9070ab93a80a48d0eed2b8f7170151abdc/legiscope.nodejs/sp-test.js

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: Apache-2.0

https://github.com/Znerual/FastLogin/blob/5c203ea995a605dbe1f5bf4a39114784a0fff449/client.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````

## License: unknown

https://github.com/Hyperx837/google-search/blob/d605dc8dc009bc8ded67c53ee7e7308a0c1215ac/vdex/vdex.py

`````
Looking at the workspace structure, I need to create/update the `backend/scripts/ingest_idsp.py` file with the requested improvements.

````python
// filepath: c:\0001_Project\PRISM\backend\scripts\ingest_idsp.py
"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and loads it into the PRISM MongoDB database.

Usage:
    # Fetch from URL (may be blocked by government site):
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file "path/to/idsp_report.pdf"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pdfplumber

# Add project root to path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---

# Primary IDSP report URL
IDSP_REPORT_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

# Browser-mimicking headers to bypass User-Agent blocking on government portals
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
`````
