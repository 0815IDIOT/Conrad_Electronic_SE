import sqlite3
import csv

def loading_data():
    data_path = "data/data.csv"
    db_path = "resources/data.db"

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
                sql = "INSERT INTO purchases VALUES ("

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

if __name__ == "__main__":
    loading_data()