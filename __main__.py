import data_stream as ds
import time as t

print("\n".join(map(str, ds.DataStream("AAPL", "Stock").get_fundamentals().keys())))
print(ds.DataStream("AAPL", "Stock").get_fundamentals()[('AAPL', '2023-08-04', 'balance_sheet')])
t.sleep(3)
print(ds.DataStream("AAPL", "Stock").get_fundamentals()[('AAPL', '2023-02-03', 'balance_sheet')])
