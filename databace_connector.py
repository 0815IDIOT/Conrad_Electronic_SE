import sqlite3
import csv
import itertools
import random
import sys

class Database_connector():
    def __init__(self, db_path, dataset_type):
        self.db_path = db_path
        self.invoice_types_id = self.set_dataset(dataset_type)

    def get_connection(self):
        con = sqlite3.connect(self.db_path)      
        cur = con.cursor()

        return con, cur
    
    def set_dataset(self, dataset_type):
        """
        Here, the user can set on which type of dataset the correlation should
        be calculated. The standard values are 'test' and 'training'.
        """

        con, cur = self.get_connection()

        sql = "SELECT invoice_types_id FROM invoice_types WHERE type_name = '" + str(dataset_type) + "'"
        id = con.execute(sql).fetchone()

        if len(id) == 0:
            raise ValueError("Unkown dataset type '" + str(dataset_type) + "'")
        
        id = id[0]
        self.invoice_types_id = id

        con.close()

        return id

    
    def load_raw_data(self, data_path, split_training=70):

        """
        This function to loads the local raw csv file downloadable from Kaggle
        (https://www.kaggle.com/datasets/carrie1/ecommerce-data) into the DB.
        """

        print("[*] loading raw data from csv ...")

        with open(data_path, "r",encoding='utf-8',errors='ignore') as csv_file:

            con, cur = self.get_connection()

            first_row = True
            csv_reader = csv.reader(csv_file, dialect=csv.excel, delimiter=",")

            for data in csv_reader:
                if first_row:

                    first_row = False
                else:
                    # Order the raw data
                    invoice_id = data[0]
                    stock_id = data[1]
                    stock_descrip = data[2]
                    quantity = data[3]
                    invoice_date = data[4]
                    unit_price = data[5]
                    customer_id = data[6]
                    country = data[7]
                    # 1 equals test data and 2 trainings data -> see the invoice_types table
                    invoice_types_id = 1 if random.random() > split_training / 100. else 2

                    if customer_id == "":
                        customer_id = 0

                    self.insert_customer(cur, customer_id)
                    self.insert_stock_item(cur, stock_id, stock_descrip)
                    self.insert_invoice(cur, invoice_id, customer_id, invoice_date, country, invoice_types_id)
                    self.insert_shopping_list(cur, invoice_id, stock_id, quantity, unit_price)

            con.commit()
            con.close()


    def calc_regression(self, force = False):

        """
        Function to calculate the numbers of time each bundles has been bought.
        Note, that this function can take some time. 
        """

        con, cur = self.get_connection()

        # Testing wether already data in the DB table 'bought_together'.
        # If so, ask the user if he wants to delete the old data and recalculate 
        # the model data. Note, that the force flag ignores the user input.

        sql = "SELECT count(*) FROM bought_together"
        count = cur.execute(sql).fetchone()[0]

        if count > 0:
            if not force:
                inp = ""
                while inp not in ["Y", "y", "N", "n"]:
                    inp = input("[!] Deleting old regression data (Y/N): ")

                if inp in ["N", "n"]:
                    print("[*] function aborted!")
                    sys.exit()

            print("[*] Delet old regression data")
            sql = "DELETE FROM bought_together"
            cur.execute(sql)
            con.commit()

        print("[*] Calculating regression")
        print("[*] This may take a while. Loading ... ")


        invoice_ids = cur.execute("SELECT invoice_id FROM invoices WHERE invoice_types_id = " + str(self.invoice_types_id)).fetchall()
        i = 1

        for invoice_id in invoice_ids:
            print("    [-] invoice " + str(i) + "/" + str(len(invoice_ids)) + "          \r",end="")
            
            stock_ids = cur.execute("SELECT stock_id FROM shopping_lists WHERE invoice_id = '" + str(invoice_id[0]) + "'")
            stock_ids = [stock_id[0] for stock_id in stock_ids.fetchall()]

            for pair in itertools.combinations(stock_ids, r=2):
                pair = sorted(pair)

                sql = "SELECT EXISTS(SELECT count FROM bought_together WHERE stock_id_1='" + str(pair[0]) + "' and stock_id_2='" + str(pair[1]) + "');"
                exists = cur.execute(sql).fetchone()[0]

                if exists == 0:
                    # does not exist
                    # BUG FIX: why 'or ignore'?
                    sql = "INSERT OR IGNORE INTO bought_together VALUES ('" + str(pair[0]) + "', '" + str(pair[1]) + "', 1)"
                    #sql = "INSERT INTO bought_together (stock_id_1, stock_id_2, count) VALUES ('" + str(pair[0]) + "', '" + str(pair[1]) + "', 1)"
                    cur.execute(sql)
                else:
                    # does exist
                    sql = "SELECT count FROM bought_together WHERE stock_id_1='" + str(pair[0]) + "' and stock_id_2='" + str(pair[1]) + "'"
                    count = cur.execute(sql).fetchone()[0]
                    count += 1
                    sql = "UPDATE bought_together SET count = " + str(count) + " WHERE stock_id_1='" + str(pair[0]) + "' and stock_id_2='" + str(pair[1]) + "'"
            
            cur.execute(sql)
            i += 1

        print("")
        con.commit()
        con.close()


    def get_recommanded_product(self, stock_id, limit = 20):

        """
        This function calculates the percentage at which a second product is
        bought together with the product of 'stock_id'. The top 'limit' products
        are returned.
        """

        con, cur = self.get_connection()

        sql = "SELECT count(*) FROM shopping_lists JOIN invoices ON shopping_lists.invoice_id = invoices.invoice_id"
        sql += " WHERE stock_id = '" + str(stock_id) + "' AND invoice_types_id = " + str(self.invoice_types_id)
        count_max = cur.execute(sql).fetchone()[0]

        sql = "SELECT * FROM bought_together WHERE stock_id_1 = '" + str(stock_id) + "' or stock_id_2 = '" + str(stock_id) + "' ORDER BY count DESC LIMIT " + str(limit)
        data = cur.execute(sql).fetchall()

        sql = "SELECT DISTINCT unit_price FROM shopping_lists WHERE stock_id = '" + str(stock_id) + "'"
        prices_1 = cur.execute(sql).fetchall()
        price_1_max = max(prices_1)[0]
        price_1_min = min(prices_1)[0]

        rec_stocks = []

        for row in data:
            if row[0] == stock_id:
                stock_id_2 = row[1]
            else:
                stock_id_2 = row[0]
            count = row[2]
            
            sql = "SELECT DISTINCT unit_price FROM shopping_lists WHERE stock_id = '" + str(stock_id_2) + "'"
            prices_2 = cur.execute(sql).fetchall()
            price_2_max = max(prices_2)[0]
            price_2_min = min(prices_2)[0]

            sql = "SELECT stock_descrip FROM stock_items WHERE stock_id = '" + str(stock_id_2) + "'"
            stock_2_descrip = cur.execute(sql).fetchone()[0]

            rec_stocks.append({"stock": stock_id_2, 
                               "stock_descrip" : stock_2_descrip,
                               "percentage":100. * count / count_max,
                               "max_bundle_price" : price_1_max + price_2_max,
                               "min_bundle_price" : price_1_min + price_2_min})
            print(rec_stocks[-1])

        con.close()
        return rec_stocks
    

    def get_recommanded_price(self, stock_id):
        
        """
        Recommand a unit price for a product, depending on the historic mean
        sales price. It stays to discuess, wether this is sufficent.
        """

        con, cur = self.get_connection()

        sql = "SELECT unit_price, count(*) FROM shopping_lists WHERE stock_id = '" + str(stock_id) + "' GROUP BY unit_price"
        price_data = cur.execute(sql).fetchall()
        count = 0.
        price = 0.
        for price_item in price_data:
            count += price_item[1]
            price += price_item[0] * price_item[1]
        
        price = round(price / count, 2)
        print(price)

        con.close()

        return price


    def insert_customer(self, cur, customer_id, name = "", address = ""):
        
        sql = "INSERT OR IGNORE INTO customers VALUES (" + str(customer_id) + ", '" + str(name) + "', '" + str(address) + "')"
        cur.execute(sql)


    def insert_stock_item(self, cur, stock_id, stock_descrip):

        sql = "INSERT OR IGNORE INTO stock_items VALUES ('" + str(stock_id) + "', '" + str(stock_descrip.replace("\"","").replace("'","")) + "')"
        cur.execute(sql)


    def insert_invoice(self, cur, invoice_id, customer_id, invoice_date, country, invoice_types_id):

        sql = "INSERT OR IGNORE INTO invoices VALUES ('" + str(invoice_id) + "', " + str(customer_id) +  ", '" + str(invoice_date) + "', '" + str(country) + "', " + str(invoice_types_id) + ")"
        cur.execute(sql)


    def insert_shopping_list(self, cur, invoice_id, stock_id, quantity, unit_price):        

        sql = "INSERT OR IGNORE INTO shopping_lists VALUES ('" + str(invoice_id) + "', '" + str(stock_id) + "', " + str(quantity) + ", " + str(unit_price) + ")"
        cur.execute(sql)


if __name__ == "__main__":
    db_path = "resources/data.db"
    data_path = "data/data.csv"

    dbc = Database_connector(db_path, dataset_type = "training")

    #dbc.load_raw_data(data_path)
    #dbc.calc_regression()
    dbc.get_recommanded_product(stock_id="22865")
    dbc.get_recommanded_price(stock_id="22865")