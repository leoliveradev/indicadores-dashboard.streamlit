from services.transformers import last_period_delta


def apply_operation(df, cfg):
    df = df.copy()

    if cfg.get("type") == "sum":

        df["_metric"] = (
            df[cfg["columns"]]
            .sum(axis=1)
        )

    elif cfg.get("type") == "ratio":

        total = (
            df[cfg["den"]]
            .sum(axis=1)
        )

        df["_metric"] = (
            df[cfg["num"]]
            / total
            * 100
        )
    else:
        df["_metric"] = df[cfg["column"]]

    return df, "_metric"


def build_kpis(kpi_config, datasets, default_dataset=None):
    kpis = []

    for cfg in kpi_config:
        dataset_key = cfg.get("dataset", default_dataset)

        if dataset_key is None:
            raise ValueError("KPI sin dataset")

        df = datasets[dataset_key]

        df_calc, col = apply_operation(df, cfg)
        val, delta = last_period_delta(df_calc, col)

        kpis.append({
            "label": cfg["label"],
            "value": val,
            "delta": delta,
            "format": cfg["format"],
        })

    return kpis


def build_kpis_agg(kpi_config, df):
    kpis = []

    for cfg in kpi_config:
        col = cfg["column"]

        if cfg["agg"] == "sum":
            val = df[col].sum()
        elif cfg["agg"] == "mean":
            val = df[col].mean()
        else:
            raise ValueError(f"agg no soportado: {cfg['agg']}")

        kpis.append({
            "label": cfg["label"],
            "value": val,
            "format": cfg["format"],
        })

    return kpis