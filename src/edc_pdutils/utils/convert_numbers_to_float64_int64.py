import pandas as pd


def convert_numbers_to_float64_int64(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["number"]).columns:
        if pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].astype("float64")
        elif pd.api.types.is_integer_dtype(df[col]):
            # df[col].replace({pd.NA: np.nan})
            df[col] = df[col].astype("float64")
    # df.replace({pd.NA: np.nan})
    return df
