from flask import Flask, Response
import pandas as pd
import io

app = Flask(__name__)

@app.route('/download')
def download_csv():
    # Create a sample DataFrame
    data = {
        'Column1': [1, 2, 3],
        'Column2': ['A', 'B', 'C']
    }
    df = pd.DataFrame(data)

    # Convert DataFrame to CSV
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=data.csv"}
    )

if __name__ == '__main__':
    app.run()
