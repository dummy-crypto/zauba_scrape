import pandas as pd
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Step 1: Authenticate
gauth = GoogleAuth()
gauth.LoadClientConfigFile(r'C:\Users\pc\OneDrive\Desktop\client_secret.json')  
gauth.LocalWebserverAuth()  # Creates a local webserver for authentication

drive = GoogleDrive(gauth)

# Step 2: Create a DataFrame
df = pd.DataFrame({
    'Column1': [1, 2, 3],
    'Column2': ['A', 'B', 'C']
})

# Step 3: Save the DataFrame as a CSV file locally
local_csv_path = 'my_data.csv'
df.to_csv(local_csv_path, index=False)

# Step 4: Upload the CSV file to Google Drive
file_to_upload = drive.CreateFile({'title': 'my_data.csv'})
file_to_upload.SetContentFile(local_csv_path)
file_to_upload.Upload()

print('File uploaded to Google Drive with ID:', file_to_upload.get('id'))
