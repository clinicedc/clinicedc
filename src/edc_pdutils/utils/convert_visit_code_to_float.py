def convert_visit_code_to_float(df):
    """Convert visit_code to float using visit_code_sequence"""
    df["visit_code"] = df["visit_code"].astype(float)
    df["visit_code_sequence"] = df["visit_code_sequence"].astype(float)
    df["visit_code_sequence"] = df["visit_code_sequence"].apply(
        lambda x: x / 10.0 if x > 0.0 else 0.0
    )
    df["visit_code"] = df["visit_code"] + df["visit_code_sequence"]
