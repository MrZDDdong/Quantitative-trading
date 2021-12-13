import pandas as pd
import talib as ta
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function
from zipline.utils.events import date_rules, time_rules

"""MOM指标"""


def initialize(context):
    print("init")
    context.asset = symbol('IBM')
    context.mom_window = 12
    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    history = data.history(assets=context.asset,
                           fields=['close'],
                           bar_count=context.mom_window + 1,
                           frequency='1d')
    date = history.index.values[-1]
    close = history['close'].values

    # 计算指标
    mom = ta.MOM(close, timeperiod=context.mom_window)

    current_price = data[context.asset].price
    record(price=current_price)

    buy_signal_triggered = False
    sell_signal_triggered = False

    if mom[-1] > 0:
        buy_signal_triggered = True
    elif mom[-1] < 0:
        sell_signal_triggered = True

    current_position = context.portfolio.positions[context.asset].amount

    if buy_signal_triggered and current_position == 0:
        print(str(date) + '==>Buy')
        order_target_percent(context.asset, 0.5)

    elif sell_signal_triggered and current_position > 0:
        print(str(date) + '==>Sell')
        order_target_percent(context.asset, 0.0)
    else:
        print("No trading")


if __name__ == '__main__':
    start_session = pd.to_datetime('2012-05-01', utc=True)
    end_session = pd.to_datetime('2013-05-01', utc=True)
    bundle_name = "custom-csv-bundle"
    capital = 10000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    perf.to_pickle("output.pkl")
