import sqlite3
import csv
import itertools
import random
import sys

class Database_connector():
    def __init__(self, db_path, dataset_type: str):
        self.db_path = db_path
        self.invoice_types_id = self.set_dataset(dataset_type)

    def get_connection(self):
        con = sqlite3.connect(self.db_path)      
        cur = con.cursor()

        return con, cur
    
    def set_dataset(self, dataset_type: str) -> int:
        """
        Here, the user can set on which type of dataset the correlation should
        be calculated. The standard values are 'test' and 'training'.
        """

        if not isinstance(dataset_type, str): raise Exception("in function 'set_dataset': 'dataset_type' is not from type 'str' but from type '" + str(type(dataset_type)) + "'")

        con, cur = self.get_connection()

        sql_statment = "SELECT invoice_types_id FROM invoice_types WHERE type_name = '" + str(dataset_type) + "'"
        id = con.execute(sql_statment).fetchone()

        if len(id) == 0:
            raise ValueError("Unkown dataset type '" + str(dataset_type) + "'")
        
        id = id[0]
        self.invoice_types_id = id

        con.close()

        return id

    
    def load_raw_data(self, data_path:str, split_training:float = 70.):

        if not isinstance(data_path, str): raise Exception("in function 'load_raw_data': 'data_path' is not from type 'str' but from type '" + str(type(data_path)) + "'")
        if not isinstance(split_training, float): raise Exception("in function 'load_raw_data': 'split_training' is not from type 'float' but from type '" + str(type(split_training)) + "'")

        """
        This function loads the local raw csv file downloadable from Kaggle
        (https://www.kaggle.com/datasets/carrie1/ecommerce-data) into the DB.
        """

        print("[*] loading raw data from csv ...")

        with open(data_path, "r",encoding = 'utf-8',errors = 'ignore') as csv_file:

            con, cur = self.get_connection()

            first_row = True
            csv_reader = csv.reader(csv_file, dialect = csv.excel, delimiter = ",")

            for data in csv_reader:
                if first_row:

                    first_row = False
                else:
                    # Order the raw data
                    invoice_id = data[0]
                    stock_id = data[1]
                    stock_descrip = data[2]
                    quantity = int(data[3])
                    invoice_date = data[4]
                    unit_price = float(data[5])
                    customer_id = 0 if data[6] == "" else int(data[6])
                    country = data[7]
                    # 1 equals test data and 2 trainings data -> see the invoice_types table
                    invoice_types_id = 1 if random.random() > split_training / 100. else 2

                    self.insert_customer(cur, customer_id)
                    self.insert_stock_item(cur, stock_id, stock_descrip)
                    self.insert_invoice(cur, invoice_id, customer_id, invoice_date, country, invoice_types_id)
                    self.insert_shopping_list(cur, invoice_id, stock_id, quantity, unit_price)

            con.commit()
            con.close()


    def calc_regression(self, force:bool = False):
        """
        This function to calculate the number of times each bundle has been
        bought. Note that this function can take some time. 
        """

        if not isinstance(force, bool): raise Exception("in function 'calc_regression': 'force' is not from type 'bool' but from type '" + str(type(force)) + "'")

        con, cur = self.get_connection()

        # Testing wether already data in the DB table 'bought_together'.
        # If so, ask the user if he wants to delete the old data and recalculate 
        # the model data. Note, that the force flag ignores the user input.

        sql_statment = "SELECT count(*) FROM bought_together"
        count = cur.execute(sql_statment).fetchone()[0]

        if count > 0:
            if not force:
                inp = ""
                while inp not in ["Y", "y", "N", "n"]:
                    inp = input("[!] Deleting old regression data (Y/N): ")

                if inp in ["N", "n"]:
                    print("[*] function aborted!")
                    sys.exit()

            print("[*] Delete old regression data")
            sql_statment = "DELETE FROM bought_together"
            cur.execute(sql_statment)
            con.commit()

        print("[*] Calculating regression")
        print("[*] This may take a while. Loading ... ")
    
        sql_statment = "INSERT INTO bought_together "
        sql_statment += "SELECT r.stock_id AS r_stock, l.stock_id AS l_stock, COUNT(*) FROM shopping_lists AS l JOIN shopping_lists AS r ON "
        sql_statment += "r.invoice_id = l.invoice_id AND l.stock_id != r.stock_id AND (SELECT invoice_types_id FROM invoices WHERE invoice_id = l.invoice_id) = 2 GROUP BY r.stock_id, l.stock_id"

        cur.execute(sql_statment)
        con.commit()
        con.close()

    def get_recommanded_product(self, stock_id:str, limit:int = 20) -> list:

        """
        This function calculates the percentage at which a second product is
        bought together with the product of 'stock_id'. The top 'limit' products
        are returned.
        """

        if not isinstance(stock_id, str): raise Exception("in function 'get_recommanded_product': 'stock_id' is not from type 'str' but from type '" + str(type(stock_id)) + "'")
        if not isinstance(limit, int): raise Exception("in function 'get_recommanded_product': 'limit' is not from type 'int' but from type '" + str(type(limit)) + "'")

        con, cur = self.get_connection()

        sql_statment = "SELECT count(*) FROM shopping_lists JOIN invoices ON shopping_lists.invoice_id = invoices.invoice_id"
        sql_statment += " WHERE stock_id = '" + str(stock_id) + "' AND invoice_types_id = " + str(self.invoice_types_id)
        count_max = cur.execute(sql_statment).fetchone()[0]

        if count_max == 0:
            return {}

        sql_statment = "SELECT * FROM bought_together WHERE stock_id_1 = '" + str(stock_id) + "' or stock_id_2 = '" + str(stock_id) + "' ORDER BY count DESC LIMIT " + str(limit)
        data = cur.execute(sql_statment).fetchall()

        sql_statment = "SELECT DISTINCT unit_price FROM shopping_lists WHERE stock_id = '" + str(stock_id) + "'"
        prices_1 = cur.execute(sql_statment).fetchall()
        price_1_max = max(prices_1)[0]
        price_1_min = min(prices_1)[0]

        rec_stocks = []

        for row in data:
            if row[0] == stock_id:
                stock_id_2 = row[1]
            else:
                stock_id_2 = row[0]
            count = row[2]
            
            sql_statment = "SELECT DISTINCT unit_price FROM shopping_lists WHERE stock_id = '" + str(stock_id_2) + "'"
            prices_2 = cur.execute(sql_statment).fetchall()
            price_2_max = max(prices_2)[0]
            price_2_min = min(prices_2)[0]

            sql_statment = "SELECT stock_descrip FROM stock_items WHERE stock_id = '" + str(stock_id_2) + "'"
            stock_2_descrip = cur.execute(sql_statment).fetchone()[0]

            rec_stocks.append({"stock": stock_id_2, 
                               "stock_descrip" : stock_2_descrip,
                               "percentage":100. * count / count_max,
                               "max_bundle_price" : price_1_max + price_2_max,
                               "min_bundle_price" : price_1_min + price_2_min})
            print(rec_stocks[-1])

        con.close()
        return rec_stocks
    

    def get_recommanded_price(self, stock_id:str) -> float:
        
        """
        Recommand a unit price for a product, depending on the historic mean
        sales price. It stays to discuess, wether this is sufficent.
        """

        if not isinstance(stock_id, str): raise Exception("in function 'get_recommanded_price': 'stock_id' is not from type 'str' but from type '" + str(type(stock_id)) + "'")

        con, cur = self.get_connection()

        sql_statment = "SELECT unit_price, count(*) FROM shopping_lists WHERE stock_id = '" + str(stock_id) + "' GROUP BY unit_price"
        price_data = cur.execute(sql_statment).fetchall()
        count = 0.
        price = 0.
        for price_item in price_data:
            count += price_item[1]
            price += price_item[0] * price_item[1]
        
        if count == 0:
            return 0.
        
        price = round(price / count, 2)
        print(price)

        con.close()

        return price


    def insert_customer(self, cur, customer_id:int, name:str = "", address:str = ""):
        
        if not isinstance(customer_id, int): raise Exception("in function 'insert_customer': 'customer_id' is not from type 'int' but from type '" + str(type(customer_id)) + "'")
        if not isinstance(name, str): raise Exception("in function 'insert_customer': 'name' is not from type 'str' but from type '" + str(type(name)) + "'")
        if not isinstance(address, str): raise Exception("in function 'insert_customer': 'address' is not from type 'str' but from type '" + str(type(address)) + "'")

        sql_statment = "INSERT OR IGNORE INTO customers VALUES (" + str(customer_id) + ", '" + str(name) + "', '" + str(address) + "')"
        cur.execute(sql_statment)


    def insert_stock_item(self, cur, stock_id:str, stock_descrip:str):

        if not isinstance(stock_id, str): raise Exception("in function 'insert_stock_item': 'stock_id' is not from type 'str' but from type '" + str(type(stock_id)) + "'")
        if not isinstance(stock_descrip, str): raise Exception("in function 'insert_stock_item': 'stock_descrip' is not from type 'str' but from type '" + str(type(stock_descrip)) + "'")

        sql_statment = "INSERT OR IGNORE INTO stock_items VALUES ('" + str(stock_id) + "', '" + str(stock_descrip.replace("\"","").replace("'","")) + "')"
        cur.execute(sql_statment)


    def insert_invoice(self, cur, invoice_id:str, customer_id:int, invoice_date:str, country:str, invoice_types_id:int):

        if not isinstance(invoice_id, str): raise Exception("in function 'insert_invoice': 'invoice_id' is not from type 'str' but from type '" + str(type(invoice_id)) + "'")
        if not isinstance(customer_id, int): raise Exception("in function 'insert_invoice': 'customer_id' is not from type 'int' but from type '" + str(type(customer_id)) + "'")
        if not isinstance(invoice_date, str): raise Exception("in function 'insert_invoice': 'invoice_date' is not from type 'str' but from type '" + str(type(invoice_date)) + "'")
        if not isinstance(country, str): raise Exception("in function 'insert_invoice': 'country' is not from type 'str' but from type '" + str(type(invoice_types_id)) + "'")
        if not isinstance(invoice_types_id, int): raise Exception("in function 'insert_invoice': 'invoice_types_id' is not from type 'int' but from type '" + str(type(invoice_types_id)) + "'")

        sql_statment = "INSERT OR IGNORE INTO invoices VALUES ('" + str(invoice_id) + "', " + str(customer_id) +  ", '" + str(invoice_date) + "', '" + str(country) + "', " + str(invoice_types_id) + ")"
        cur.execute(sql_statment)


    def insert_shopping_list(self, cur, invoice_id:str, stock_id:str, quantity:int, unit_price:float):        

        if not isinstance(invoice_id, str): raise Exception("in function 'insert_shopping_list': 'invoice_id' is not from type 'str' but from type '" + str(type(invoice_id)) + "'")
        if not isinstance(stock_id, str): raise Exception("in function 'insert_shopping_list': 'stock_id' is not from type 'str' but from type '" + str(type(stock_id)) + "'")
        if not isinstance(quantity, int): raise Exception("in function 'insert_shopping_list': 'quantity' is not from type 'int' but from type '" + str(type(quantity)) + "'")
        if not isinstance(unit_price, float): raise Exception("in function 'insert_shopping_list': 'unit_price' is not from type 'float' but from type '" + str(type(unit_price)) + "'")

        sql_statment = "INSERT OR IGNORE INTO shopping_lists VALUES ('" + str(invoice_id) + "', '" + str(stock_id) + "', " + str(quantity) + ", " + str(unit_price) + ")"
        cur.execute(sql_statment)
