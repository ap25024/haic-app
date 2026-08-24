import pandas as pd


def eda_insights(df):
    """
    Performs structured exploratory data analysis.

    The EDA package contains:
    1. Dataset overview
    2. Column classification
    3. Missing data
    4. Descriptive statistics
    5. Categorical analysis
    6. Correlations
    7. Outliers
    """

    df = df.copy()


    # 1. DATASET OVERVIEW

    dataset_overview = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "duplicate_rows": int(df.duplicated().sum())
    }


    # 2. COLUMN CLASSIFICATION

    identifiers = []
    numeric_columns = []
    categorical_columns = []
    datetime_columns = []

    for column in df.columns:

        series = df[column]
        column_name = column.lower().strip()

        unique_ratio = (
            series.nunique(dropna=True) / len(series)
            if len(series) > 0
            else 0
        )

        is_identifier = (
            column_name == "id"
            or column_name.endswith("_id")
            or column_name.startswith("id_")
            or "identifier" in column_name
        )

        if is_identifier and unique_ratio >= 0.8:
            identifiers.append(column)
            continue

        if pd.api.types.is_datetime64_any_dtype(series):
            datetime_columns.append(column)
            continue

        if pd.api.types.is_numeric_dtype(series):
            numeric_columns.append(column)
            continue

        date_hint = any(
            word in column_name
            for word in ["date", "time", "month", "year"]
        )

        if date_hint:

            parsed_dates = pd.to_datetime(
                series,
                errors="coerce"
            )

            if parsed_dates.notna().mean() >= 0.8:
                datetime_columns.append(column)
                continue

        categorical_columns.append(column)

    column_classification = {
        "identifiers": identifiers,
        "numeric": numeric_columns,
        "categorical": categorical_columns,
        "datetime": datetime_columns
    }


    # 3. MISSING DATA

    missing_data = (
        df.isnull()
        .sum()
        .astype(int)
        .to_dict()
    )

    missing_percentages = {}

    for column, count in missing_data.items():

        if len(df) > 0:

            missing_percentages[column] = round(
                (count / len(df)) * 100,
                2
            )

        else:

            missing_percentages[column] = 0.0

    # 4. DESCRIPTIVE STATISTICS
    if numeric_columns:

        summary_statistics = (
            df[numeric_columns]
            .describe()
            .round(2)
            .to_dict()
        )

    else:

        summary_statistics = {}

    # 5. CATEGORICAL ANALYSIS

    categorical_analysis = {}

    for column in categorical_columns:

        values = df[column].dropna()

        if values.empty:
            continue


        value_counts = (
            values
            .value_counts()
            .head(5)
        )

        percentages = (
            value_counts / len(values) * 100
        ).round(2)


        top_values = {}

        for value in value_counts.index:

           top_values[str(value)] = {
            "count": int(value_counts[value]),
            "percentage": float(percentages[value])
        }


        categorical_analysis[column] = {
            "unique_values": int(values.nunique()),
            "top_values": top_values
        }

    # 6. CORRELATIONS

    correlations = {}

    if len(numeric_columns) >= 2:

        correlation_matrix = (
            df[numeric_columns]
            .corr()
            .round(2)
        )

        correlation_pairs = []

        columns = correlation_matrix.columns

        for i in range(len(columns)):

            for j in range(i + 1, len(columns)):

                column_1 = columns[i]
                column_2 = columns[j]

                score = correlation_matrix.loc[
                    column_1,
                    column_2
                ]

                if (
                    pd.notna(score)
                    and abs(score) >= 0.50
                ):

                    correlation_pairs.append(
                        (
                            column_1,
                            column_2,
                            float(score)
                        )
                    )

        correlation_pairs.sort(
            key=lambda item: abs(item[2]),
            reverse=True
        )

        for column_1, column_2, score in correlation_pairs[:5]:

            correlations.setdefault(
                column_1,
                {}
            )[column_2] = score

    # 7. OUTLIERS

    outliers = []

    for column in numeric_columns:

        values = df[column].dropna()
        if len(values) < 4:
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outlier_mask = (
            (values < lower_bound)
            |
            (values > upper_bound)
        )

        outlier_count = int(
            outlier_mask.sum()
        )

        if outlier_count > 0:

            outliers.append({
                "column": column,
                "outlier_count": outlier_count,

                "outlier_percentage": round(
                    (outlier_count / len(values)) * 100,
                    2
                ),

                "lower_bound": round(
                    float(lower_bound),
                    2
                ),

                "upper_bound": round(
                    float(upper_bound),
                    2
                ),

                "minimum_outlier": round(
                    float(values[outlier_mask].min()),
                    2
                ),

                "maximum_outlier": round(
                    float(values[outlier_mask].max()),
                    2
                )
            })

    # FINAL STRUCTURED EDA PACKAGE
    
    return {

        "dataset_overview":
            dataset_overview,

        "column_classification":
            column_classification,

        "missing_data":
            missing_data,

        "missing_percentages":
            missing_percentages,

        "summary_statistics":
            summary_statistics,

        "categorical_analysis":
            categorical_analysis,

        "correlations":
            correlations,

        "outliers":
            outliers
    }