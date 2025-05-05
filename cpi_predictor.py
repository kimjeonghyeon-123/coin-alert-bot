import requests
import pandas as pd
from datetime import datetime
import numpy as np

FRED_API_KEY = "4c660d85c6caa3480c4dd60c1e2fa823"

# ✅ 사용할 경제 지표와 코드
FRED_SERIES = {
    "WTI": "DCOILWTICO",            # WTI 유가
    "UNRATE": "UNRATE",            # 미국 실업률
    "RETAIL": "RSAFS"              # 소매판매
}

def fetch_fred_series(series_id, start_date="2015-01-01"):
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date
    }
    response = requests.get(url, params=params)
    data = response.json()["observations"]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date")["value"]

def prepare_feature_df():
    df_wti = fetch_fred_series(FRED_SERIES["WTI"])
    df_unrate = fetch_fred_series(FRED_SERIES["UNRATE"])
    df_retail = fetch_fred_series(FRED_SERIES["RETAIL"])
    df_cpi = fetch_fred_series("CPIAUCSL")  # 소비자물가지수 (미국 CPI)

    # 월별 리샘플링 및 결측치 보간
    features = pd.concat([
        df_wti.resample("M").mean().interpolate(),
        df_unrate.resample("M").mean().interpolate(),
        df_retail.resample("M").mean().interpolate(),
        df_cpi.resample("M").last().interpolate()
    ], axis=1)

    features.columns = ["WTI", "Unemployment", "RetailSales", "CPI"]
    features = features.dropna()

    # 타겟: 다음 달 CPI
    features["Next_CPI"] = features["CPI"].shift(-1)
    return features.dropna()

def train_cpi_prediction_model():
    df = prepare_feature_df()
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    X = df[["WTI", "Unemployment", "RetailSales"]]
    y = df["Next_CPI"]
    model.fit(X, y)
    return model, df

def predict_next_cpi(country="USA", date=None):
    if country != "USA":
        raise ValueError("❌ 현재는 미국(USA)만 지원됩니다.")

    model, df = train_cpi_prediction_model()
    latest = df.iloc[-1][["WTI", "Unemployment", "RetailSales"]].values.reshape(1, -1)
    predicted_cpi = model.predict(latest)[0]
    return round(predicted_cpi, 2)

if __name__ == "__main__":
    print(f"📈 예측된 다음 CPI: {predict_next_cpi()}") 

