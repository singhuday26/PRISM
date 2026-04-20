import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
from backend.services.resources import ResourceService

svc = ResourceService()
date_str = datetime.now().strftime("%Y-%m-%d")
print("Target Date:", date_str)
res = svc.predict_demand("IN-MH", date_str, "DENGUE")
print(res)
