import pandas as pd
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
    pitchers_df = attribute_data[attribute_data["is_hitter"] == False].copy()
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





