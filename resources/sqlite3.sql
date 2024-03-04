CREATE TABLE purchases_training(
    invoice_id INTEGER NOT NULL, 
    stock_id TEXT NOT NULL, 
    descrip TEXT NOT NULL,
    quantity INTEGER NOT NULL, 
    invoice_date TEXT NOT NULL,
    unit_price REAL NOT NULL, 
    cunstomer_id INTEGER NOT NULL,
    country TEXT NOT NULL,
    PRIMARY KEY (invoice_id, stock_id));

CREATE TABLE purchases_test(
    invoice_id INTEGER NOT NULL, 
    stock_id TEXT NOT NULL, 
    descrip TEXT NOT NULL,
    quantity INTEGER NOT NULL, 
    invoice_date TEXT NOT NULL,
    unit_price REAL NOT NULL, 
    cunstomer_id INTEGER NOT NULL,
    country TEXT NOT NULL,
    PRIMARY KEY (invoice_id, stock_id));

CREATE TABLE bought_together(
    stock_id_1 TEXT NOT NULL,
    stock_id_2 TEXT NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (stock_id_1, stock_id_2)
);