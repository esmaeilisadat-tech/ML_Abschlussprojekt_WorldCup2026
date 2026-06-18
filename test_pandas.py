import pandas as pd
import traceback
df = pd.DataFrame({'A':[1]})
try:
    df['B'], df['C'] = 2, 3
    print("Tuple unpack works")
except Exception as e:
    print("Tuple unpack failed:", traceback.format_exc())
