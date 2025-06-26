import matplotlib.pyplot as plt

def inspect_dataframe(df, id_col="player_id", name_col="player_name", drop_duplicates=False):
    """
    Runs sanity checks on a merged player dataset before modeling.
    
    Args:
        df (pd.DataFrame): The DataFrame to inspect.
        id_col (str): Column representing player IDs.
        name_col (str): Column representing player names.
        drop_duplicates (bool): Whether to drop duplicate player IDs/names.

    Returns:
        pd.DataFrame: Cleaned DataFrame (if drop_duplicates=True), otherwise original.
    """
    
    print("="*50)
    print(f"🧾 Shape of DataFrame: {df.shape}")
    print("="*50)

    # Null checks
    print("🧯 Missing Values:")
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if not nulls.empty:
        print(nulls.sort_values(ascending=False))
    else:
        print("✅ No missing values found.")
    
    print("="*50)

    # Duplicates
    dup_ids = df[id_col].duplicated().sum()
    dup_names = df[name_col].duplicated().sum()
    print(f"🔁 Duplicate player IDs: {dup_ids}")
    print(f"🔁 Duplicate player names: {dup_names}")

    if drop_duplicates:
        before = df.shape[0]
        df = df.drop_duplicates(subset=[id_col])
        after = df.shape[0]
        print(f"✅ Dropped duplicates — {before - after} rows removed (based on {id_col})")
    else:
        if dup_ids > 0 or dup_names > 0:
            print("⚠️  Consider setting drop_duplicates=True to remove duplicates.")

    print("="*50)

    # Basic statistics
    print("📊 Summary statistics (numerical columns):")
    print(df.describe(include='number').T)

    print("="*50)

    # Histogram: new overall rating (if exists)
    if "new_overall" in df.columns:
        df["new_overall"].hist(bins=15)
        plt.title("Distribution of New Overall Ratings")
        plt.xlabel("Overall")
        plt.ylabel("Frequency")
        plt.show()

    # Sample rows
    print("🔎 Sample of 5 random rows:")
    print(df.sample(5, random_state=42))

    # Column groupings
    print("="*50)
    print("📁 Column categories:")
    print("Attribute columns:")
    print([col for col in df.columns if "contact" in col or "power" in col])
    print("FanGraphs LHP columns:")
    print([col for col in df.columns if "lhp_" in col])
    print("FanGraphs RHP columns:")
    print([col for col in df.columns if "rhp_" in col])

    print("="*50)

    return df


def add_missing_indicators(df, prefix):
    """
    Adds a single missing indicator column for a group of columns with the same prefix.

    Parameters:
        df (pd.DataFrame): The input dataframe.
        prefix (str): Column prefix to search for (e.g., 'lhp_' or 'rhp_').

    Returns:
        pd.DataFrame: Modified dataframe with a single missing indicator column.
    """
    cols = [col for col in df.columns if col.startswith(prefix) and not col.endswith("_missing")]
    if not cols:
        print(f"[add_missing_indicators] No columns found with prefix '{prefix}'")
        return df

    missing_col_name = f"missing_{prefix.rstrip('_')}_stats"
    df[missing_col_name] = df[cols].isnull().all(axis=1).astype(int)
    print(f"Columns used for '{prefix}': {cols}")


    return df

