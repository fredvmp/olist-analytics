import pandas as pd
import numpy as np
from app.utils.logger import logger
from app.repositories.customers_repository import fetch_customers_rfm


def get_customers_rfm() -> pd.DataFrame:
    """
    Procesa la segmentación de clientes mediante el modelo RFM.

    Transforma las métricas brutas en puntuaciones (1-5) usando quintiles y aplica 
    un motor de reglas basado en expresiones regulares para clasificar a los 
    clientes en segmentos de valor (Champions, Loyal, At Risk, etc.).

    Returns:
        pd.DataFrame | None: DataFrame procesado con las puntuaciones y el segmento final.
    """

    logger.info("Executing customer_service: get_customers_rfm")

    rows = fetch_customers_rfm()
    if not rows:
        return None

    df = pd.DataFrame(
        rows, columns=["customer_id", "recency", "frequency", "monetary"])

    df["recency"] = pd.to_numeric(df["recency"])
    df["monetary"] = pd.to_numeric(df["monetary"])
    df["frequency"] = pd.to_numeric(df["frequency"])

    df["r"] = pd.qcut(df["recency"], q=5, labels=[
                      5, 4, 3, 2, 1], duplicates="drop")
    df["f"] = pd.qcut(df["frequency"], q=5, labels=False,
                      duplicates="drop") + 1
    df["m"] = pd.qcut(df["monetary"], q=5, labels=False, duplicates="drop") + 1

    df["rfm"] = df["r"].astype(str) + df["f"].astype(str) + df["m"].astype(str)

    """
    segment_map = {
        r"^[4-5][4-5][4-5]$": "Champions",
        r"^[4-5][2-5].$": "Loyal Customers",
        r"^[4-5]1.$": "New Customers",
        r"^[3-4][3-4][3-4]$": "Potential Loyalists",
        r"^[1-2][4-5][4-5]$": "At risk",
        r"^[1-2][4-5].$": "Can't Lose Them",
        r"^[1-2][1-2].$": "Hibernating",
    }

    df["segment"] = df["rfm"].replace(segment_map, regex=True)
    """

    conditions = [
        df["rfm"].str.contains(r"^[4-5][4-5][4-5]$"),
        df["rfm"].str.contains(r"^[4-5][2-5].$"),
        df["rfm"].str.contains(r"^[4-5]1.$"),
        df["rfm"].str.contains(r"^[3-4][3-4][3-4]$"),
        df["rfm"].str.contains(r"^[1-2][4-5][4-5]$"),
        df["rfm"].str.contains(r"^[1-2][4-5].$"),
        df["rfm"].str.contains(r"^[1-2][1-2].$")
    ]

    choices = [
        "Champions", "Loyal Customers", "New Customers", "Potential Loyalists", "At Risk", "Can't Lose Them", "Hibernating"
    ]

    df["segment"] = np.select(
        conditions, choices, default="Standard Customers")

    df[["r", "f", "m"]] = df[["r", "f", "m"]].astype(int)

    return df
