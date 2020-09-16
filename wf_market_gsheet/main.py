import os
import statistics

import requests
import gspread


WF_MARKET_URL_BASE = "https://api.warframe.market/v1"


def dump_wf_market_data_to_gsheet():
    items = requests.get(f"{WF_MARKET_URL_BASE}/items").json()["payload"]["items"]

    rows = []
    for item in items[:5]:
        stats = requests.get(f"{WF_MARKET_URL_BASE}/items/{item['url_name']}/statistics").json()["payload"]["statistics_closed"]["90days"]
        total_volume = 0
        volumes = []
        num_days = 0
        total_median = 0
        while total_volume < 300:
            try:
                buy = stats.pop()
                sell = stats.pop()
                total_median += buy["volume"] * buy["median"]
                total_median += sell["volume"] * sell["median"]
                daily_volume = buy["volume"] + sell["volume"]
                total_volume += daily_volume
                volumes.append(daily_volume)
                num_days += 1
            except IndexError:
                break

        if num_days:
            median_of_medians = round(total_median / total_volume, 2)
            volume_per_day = round(statistics.median(volumes), 2)
        else:
            median_of_medians = 0
            volume_per_day = 0

        rows.append([item["item_name"], median_of_medians, volume_per_day])
        rows = sorted(rows, key=lambda x: -x[1])

    gc = gspread.service_account(filename=os.environ["GOOGLE_SHEETS_SERVICE_ACCOUNT"])
    wks = gc.open("warframe_market_prices_megasheet").get_worksheet(1)
    wks.update('A2', rows)


if __name__ == "__main__":
    dump_wf_market_data_to_gsheet()
