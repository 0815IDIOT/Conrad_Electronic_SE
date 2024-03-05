CREATE TABLE customers(
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    address TEXT
);

CREATE TABLE stock_items(
    stock_id TEXT PRIMARY KEY,
    stock_descrip TEXT NOT NULL
);

CREATE TABLE invoice_types(
    invoice_types_id INT PRIMARY KEY,
    type_name TEXT NOT NULL
);

INSERT INTO invoice_types VALUES (1, "test");
INSERT INTO invoice_types VALUES (2, "training");

CREATE TABLE invoices(
    invoice_id TEXT PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    invoice_date TEXT NOT NULL,
    country TEXT NOT NULL,
    invoice_types_id INTEGER NOT NULL,
    FOREIGN KEY(invoice_types_id) REFERENCES invoice_types(invoice_types_id),
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE shopping_lists(
    invoice_id TEXT NOT NULL,
    stock_id TEXT NOT NULL, 
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL, 
    FOREIGN KEY(invoice_id) REFERENCES invoices(invoice_id),
    FOREIGN KEY(stock_id) REFERENCES stock_items(stock_id),
    PRIMARY KEY (invoice_id, stock_id)
);

CREATE TABLE bought_together(
    stock_id_1 TEXT NOT NULL,
    stock_id_2 TEXT NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (stock_id_1, stock_id_2)
);