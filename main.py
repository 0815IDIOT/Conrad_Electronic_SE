import sqlite3
import csv
import itertools
import random

def loading_data(db_path, share_training=70):
    data_path = "data/data.csv"

    con = sqlite3.connect(db_path)      
    cur = con.cursor()

    with open(data_path, "r",encoding='utf-8',errors='ignore') as csv_file:

        print("[*] This may take a while. Loading ... ")

        first_row = True
        i = 1
        acc_num = 0
        exc_num = 0
        csv_reader = csv.reader(csv_file, dialect=csv.excel, delimiter=",")
        for row in csv_reader:
            if first_row:
                first_row = False
            else:
                
                if random.random() > share_training/100.:
                    table = "purchases_test"
                else:
                    table = "purchases_training"

                sql = "INSERT INTO " + table + " VALUES ("

                for item in row:
                    if str(item).isnumeric():
                        sql += item + ","
                    else:
                        sql += "\"" + str(item) + "\", "

                sql = sql[:-2] + ");"
                
                try:
                    cur.execute(sql)
                    acc_num += 1
                except Exception as e:
                    exc_num += 1
            i += 1
    
    con.commit()
    con.close()

    print("[*] Total new lines: " + str(acc_num))
    print("[*] Lines with exceptions: " + str(exc_num))
    print("")

def calc_regression(db_path):
    
    print("[*] Calculating regression")

    con = sqlite3.connect(db_path)      
    cur = con.cursor()

    invoice_ids = cur.execute("SELECT DISTINCT invoice_id FROM purchases_training;").fetchall()

    i = 1
    for invoice_id in invoice_ids:
        print("    [-] invoice " + str(i) + "/" + str(len(invoice_ids)) + "          \r",end="")
        stock_ids = cur.execute("SELECT stock_id FROM purchases_training WHERE invoice_id = '" + str(invoice_id[0]) + "'")
        stock_id = [stock_id[0] for stock_id in stock_ids.fetchall()]

        for pair in itertools.combinations(stock_id, r=2):
            pair = sorted(pair)
 
            sql = "SELECT EXISTS(SELECT count FROM bought_together WHERE stock_id_1='" + str(pair[0]) + "' and stock_id_2='" + str(pair[1]) + "');"
            exists = cur.execute(sql).fetchone()[0]

            if exists == 0:
                # does not exist
                # BUG FIX: why or ignore?
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

if __name__ == "__main__":
    db_path = "resources/data.db"

    loading_data(db_path=db_path)
    calc_regression(db_path=db_path)