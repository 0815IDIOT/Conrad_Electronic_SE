CREATE TABLE purchases(
    invoice_id INTEGER NOT NULL, 
    stock_id TEXT NOT NULL, 
    descrip TEXT NOT NULL,
    quantity INTEGER NOT NULL, 
    invoice_date TEXT NOT NULL,
    unit_price REAL NOT NULL, 
    cunstomer_id INTEGER NOT NULL,
    country TEXT NOT NULL,
    PRIMARY KEY (invoice_id, stock_id, cunstomer_id));