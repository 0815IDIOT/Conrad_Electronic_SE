from databace_connector import Database_connector 

if __name__ == "__main__":
    db_path = "resources/data.db"
    data_path = "data/data.csv"

    dbc = Database_connector(db_path, dataset_type = "training")

    dbc.load_raw_data(data_path)
    dbc.calc_regression()