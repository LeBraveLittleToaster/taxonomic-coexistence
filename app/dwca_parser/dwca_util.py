from pandas import DataFrame


class DwcaUtil:

    # noinspection PyTypeChecker
    @staticmethod
    def column_exists(dataframe: DataFrame, column_name: str) -> bool:
        columns: list = dataframe.columns.values.tolist()
        return column_name.upper() in map(str.upper, columns)

