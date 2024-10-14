from flask import Flask, jsonify
import pandas as pd
from sqlalchemy import create_engine
import os

app = Flask(__name__)


# Create the database engine
connection_string = create_engine('mssql+pyodbc://SAL_USER01:%s@172.16.22.25:1433/SAL_DB?driver=ODBC+Driver+17+for+SQL+Server' % quote('Sal@123'))
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
