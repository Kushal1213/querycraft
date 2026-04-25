#To add test records in the data.db file using SQLite3

import sqlite3

# Connect to SQLite database
connection = sqlite3.connect("data.db")
cursor = connection.cursor()

# Create Students table
table = '''
CREATE TABLE IF NOT EXISTS Students (
    name VARCHAR(30),
    class VARCHAR(10),
    marks INT,
    company VARCHAR(30)
)
'''
cursor.execute(table)

# Insert records into Students table
cursor.execute("INSERT INTO Students VALUES ('Sijo', 'BTech', 75, 'JSW')")
cursor.execute("INSERT INTO Students VALUES ('Lijo', 'MTech', 69, 'TCS')")
cursor.execute("INSERT INTO Students VALUES ('Rijo', 'BSc', 79, 'WIPRO')")
cursor.execute("INSERT INTO Students VALUES ('Sibin', 'MSc', 89, 'INFOSYS')")
cursor.execute("INSERT INTO Students VALUES ('Dilsha', 'MCom', 99, 'Cyient')")

print("The inserted records:")

# Select and print all records from the Students table
df = cursor.execute("SELECT * FROM Students")
for row in df:
    print(row)

# Commit and close the connection
connection.commit()
connection.close()