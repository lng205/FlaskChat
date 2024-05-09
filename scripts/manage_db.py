"""
This is a helper script to manage the database.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db

res = db.set_account_type("admin", "admin")
print(res)