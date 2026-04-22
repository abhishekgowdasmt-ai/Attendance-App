from storage import get_employees

def authenticate(username, password):
    df = get_employees()
    if df.empty:
        return None

    df.columns = [str(c).strip().lower() for c in df.columns]

    match = df[
        (df["username"].astype(str).str.strip() == str(username).strip()) &
        (df["password"].astype(str).str.strip() == str(password).strip()) &
        (df["active"].astype(str).str.upper() == "TRUE")
    ]

    return match.iloc[0].to_dict() if not match.empty else None