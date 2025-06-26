import numpy as np
import pandas as pd


def convert_numbers_to_nullable_dtype(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["number"]).columns:
        if pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].astype("Float64")
        elif pd.api.types.is_integer_dtype(df[col]):
            df[col] = df[col].astype("Int64")
    df.replace({np.nan: pd.NA})
    return df
