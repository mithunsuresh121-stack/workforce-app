import sys
sys.path.append('./backend')

from app.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM shifts'))
    print('Shifts count:', result.fetchone()[0])

    result = conn.execute(text('SELECT COUNT(*) FROM employees'))
    print('Employees count:', result.fetchone()[0])

    result = conn.execute(text('SELECT COUNT(*) FROM leaves'))
    print('Leaves count:', result.fetchone()[0])
