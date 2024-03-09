from fastapi import FastAPI
from databace_connector import Database_connector 

db_path = "resources/data.db"

app = FastAPI()
dbc = Database_connector(db_path, dataset_type = "training")

@app.get("/stock_items/{stock_id}/recommendations/bundle")
async def bundle_recommendations(stock_id):
    return dbc.get_recommanded_product(stock_id = stock_id)

@app.get("/stock_items/{stock_id}/recommendations/price")
async def price_recommendations(stock_id):
    return dbc.get_recommanded_price(stock_id = stock_id)
