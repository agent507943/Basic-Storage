import sys, importlib
sys.path.insert(0, 'Hardware_Learning')
import app
res = app.api_components_refresh()
try:
    # Flask Response
    data = res.get_data(as_text=True)
    print(data)
except Exception as e:
    print('Result:', res)
    print(repr(e))
