from flask import Flask, jsonify
import pandas as pd
from sqlalchemy import create_engine
import os

app = Flask(__name__)
# Database configuration
DB_USER = 'SAL_USER01'        # Replace with your SQL Server username
DB_PASSWORD = 'Sal@123'     # Replace with your SQL Server password
DB_SERVER = '172.16.22.25'           # Replace with your SQL Server address
DB_PORT = '1433'                  # Default SQL Server port
DB_NAME = 'SAL_DB'         # Replace with your SQL Server database name

# Create the database engine
connection_string = f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server'
engine = create_engine(connection_string)

@app.route('/save-data', methods=['GET'])
def save_data():
    # Create a sample DataFrame
    data = {
        'Column1': [1, 2, 3],
        'Column2': ['A', 'B', 'C']
    }
    df = pd.DataFrame(data)

    # Save DataFrame to SQL Server
    df.to_sql('my_table', engine, index=False, if_exists='replace')

    # Save DataFrame to CSV file in the local file system
    csv_file_path = 'data.csv'
    df.to_csv(csv_file_path, index=False)

    return jsonify(message="Data saved to SQL Server and file system.", csv_file=csv_file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
