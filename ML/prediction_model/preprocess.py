import pandas as pd
import unicodedata
from prediction_model.data_loader import load_player_attributes, load_roster_update_data

# -----------------------------
# Split up player attribute data by pitcher and hitter
# -----------------------------
def split_attribute_data(attribute_data: pd.DataFrame):
    """
    Splits player attribute data into hitters and pitchers based on the 'is_hitter' flag.
    
    Returns:
        hitters_df (pd.DataFrame): Data for hitters
        pitchers_df (pd.DataFrame): Data for pitchers
    """
    hitters_df = attribute_data[attribute_data["is_hitter"] == True].copy()
    hitters_df = hitters_df.drop(columns=["hits_per_9", "k_per_9", "bb_per_9", "hr_per_9"])
    pitchers_df = attribute_data[attribute_data["is_hitter"] == False].copy()
    pitchers_df = pitchers_df.drop(columns=["contact_left", "contact_right", "power_left", "power_right", "vision", "discipline"])
    return hitters_df, pitchers_df


# -----------------------------
# Split up roster update data by pitcher and hitter
# -----------------------------
def merge_and_split_roster_update(df_changes: pd.DataFrame, attributes_df: pd.DataFrame):
    """
    Merges 'is_hitter' into the roster update DataFrame, then splits into hitters and pitchers.

    Args:
        df_changes (pd.DataFrame): Roster update info, includes player_id.
        attributes_df (pd.DataFrame): Player attribute info, includes player_id and is_hitter.

    Returns:
        hitters_changes (pd.DataFrame): Roster changes for hitters.
        pitchers_changes (pd.DataFrame): Roster changes for pitchers.
    """
    
    # Merge is_hitter from attributes_df into df_changes
    df_merged = df_changes.merge(
        attributes_df[["player_id", "is_hitter"]],
        on="player_id",
        how="left"
    )
    
    # Split into hitters and pitchers
    hitters_changes = df_merged[df_merged["is_hitter"] == True].copy()
    pitchers_changes = df_merged[df_merged["is_hitter"] == False].copy()

    return hitters_changes, pitchers_changes

# -----------------------------
# Merge Attribute and Roster Data
# -----------------------------
def merge_attribute_roster(attribute_df: pd.DataFrame, roster_df: pd.DataFrame):
    """
    Merge player attribute data with roster update data on 'player_id'.

    Parameters:
    - attribute_df (pd.DataFrame): DataFrame containing player attributes (e.g. contact, power, etc.)
    - roster_df (pd.DataFrame): DataFrame containing roster update info (e.g. old_overall, new_overall, upgrade_label)

    Returns:
    - pd.DataFrame: Merged DataFrame containing attributes and roster update info
    """

    # Drop duplicate columns from roster_df before merging
    roster_df = roster_df.drop(columns=["player_name", "is_hitter"], errors="ignore")
    
    # Ensure both have player_id and remove any potential duplicates
    attribute_df = attribute_df.drop_duplicates(subset='player_id')
    roster_df = roster_df.drop_duplicates(subset='player_id')

    # Merge on player_id
    merged_df = attribute_df.merge(roster_df, on="player_id", how="inner")
    
    return merged_df


# -----------------------------
# Merge LHP and RHP FanGraph Data
# -----------------------------
def merge_lhp_rhp(fangraphsLHP_csv_path, fangraphsRHP_csv_path, key="Name", id_col="playerId"):
    
    fg_lhp = pd.read_csv(fangraphsLHP_csv_path)
    fg_rhp = pd.read_csv(fangraphsRHP_csv_path)

    # Drop Unnecessary Columns
    fg_lhp = clean_fg_data(fg_lhp)
    fg_rhp = clean_fg_data(fg_rhp)

    # Prefix columns
    fg_lhp = fg_lhp.add_prefix("lhp_")
    fg_rhp = fg_rhp.add_prefix("rhp_")

    # Restore merge keys
    fg_lhp[key] = fg_lhp[f"lhp_{key}"]
    fg_rhp[key] = fg_rhp[f"rhp_{key}"]
    fg_lhp[id_col] = fg_lhp[f"lhp_{id_col}"]
    fg_rhp[id_col] = fg_rhp[f"rhp_{id_col}"]

    # Merge
    merged = pd.merge(fg_lhp, fg_rhp, on=[key, id_col], how="outer")

    # Drop redundant columns
    cols_to_drop = [f"lhp_{key}", f"rhp_{key}", f"lhp_{id_col}", f"rhp_{id_col}"]
    merged = merged.drop(columns=[col for col in cols_to_drop if col in merged.columns])

    # Reorder columns
    cols = merged.columns.tolist()
    first_cols = [id_col, key]
    remaining_cols = [col for col in cols if col not in first_cols]
    merged = merged[first_cols + remaining_cols]

    return merged


# -----------------------------
# Clean up FanGraph Data
# -----------------------------
def clean_fg_data(fg_data: pd.DataFrame):
    fg_data = fg_data.drop(columns = ['PA', 'BB/K', 'OPS', 'ISO', 'BABIP', 'wRC', 'wRAA', 'wOBA', 'wRC+', 'Season', 'Tm'])
    return fg_data


def normalize_name(name):
    if pd.isnull(name):
        return ""
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8").strip().lower()

# -----------------------------
# Merge Fangraph Data with Merged Attribute and Roster Update Data
# -----------------------------
def merge_fangraphs_data(attr_df, fg_df, name_col="Name"):
    """
    Merges Fangraphs stats into the attribute dataframe using player name.
    Also logs how many players matched and how many did not.

    Parameters:
        attr_df (pd.DataFrame): The main player attribute dataframe.
        fangraphs_csv_path (str): Path to the Fangraphs CSV file.
        name_col (str): The column in the CSV that contains player names (default 'Name').

    Returns:
        pd.DataFrame: Merged dataframe.
    """

    # Sanitize names
    fg_df["normalized_name"] = fg_df[name_col].apply(normalize_name)
    attr_df["normalized_name"] = attr_df["player_name"].apply(normalize_name)

    # Merge
    merged = attr_df.merge(fg_df.drop(columns=[name_col], errors="ignore"), on="normalized_name", how="left", indicator=True)

    # Log results
    total = len(merged)
    matched = (merged["_merge"] == "both").sum()
    unmatched = total - matched
    print(f"[merge_fangraphs_data] Total players: {total} | Matched: {matched} | Unmatched: {unmatched}")

    unmatched_df = merged[merged["_merge"] == "left_only"]
    print("Unmatched player names:", unmatched_df["player_name"].unique())

    # Clean up
    merged.drop(columns=["normalized_name", "_merge"], inplace=True, errors="ignore")

    return merged




