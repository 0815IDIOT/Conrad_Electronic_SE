from databace_connector import Database_connector 

db_path = "resources/data.db"
data_path = "data/data.csv"

dbc = Database_connector(db_path, dataset_type = "training")

dbc.load_raw_data(data_path)
dbc.calc_regression()
dbc.get_recommanded_product(stock_id="22865")
dbc.get_recommanded_price(stock_id="22865")