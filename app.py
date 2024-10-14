from flask import Flask, Response
import pandas as pd
import io
import os

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

# No need for if __name__ block when using Render
app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
