from flask import Flask, render_template, request, jsonify
import speedtest
from datetime import datetime
import json
import csv
import os

app = Flask(__name__)

# Path to JSON file
JSON_FILE = 'speedtest_results.json'

# Function to save JSON data to a file
def save_to_json(data):
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as file:
            results = json.load(file)
    else:
        results = []

    results.append(data)

    with open(JSON_FILE, 'w') as file:
        json.dump(results, file, indent=4)

# Function to convert JSON to CSV
def convert_json_to_csv(json_file, csv_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        # Write CSV headers
        writer.writerow(["Name", "Address", "ISP", "Users", "Download Speed (Mbps)", "Upload Speed (Mbps)", "Ping (ms)", "Server", "DateTime"])

        # Write data
        for entry in data:
            writer.writerow([
                entry['name'], 
                entry['address'], 
                entry['isp'], 
                entry['users'], 
                entry['download_speed'], 
                entry['upload_speed'], 
                entry['ping'], 
                entry['server'], 
                entry['datetime']
            ])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/speedtest', methods=['POST'])
def run_speedtest():
    try:
        # Get form data
        data = request.json
        name = data.get('name')
        address = data.get('address')
        isp = data.get('isp')
        users = data.get('users')

        # Perform speed test
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        ping = st.results.ping
        server = st.results.server['sponsor']  # Get server info
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare result data
        result_data = {
            'name': name,
            'address': address,
            'isp': isp,
            'users': users,
            'download_speed': round(download_speed, 2),
            'upload_speed': round(upload_speed, 2),
            'ping': ping,
            'server': server,
            'datetime': current_datetime
        }

        # Save to JSON file
        save_to_json(result_data)

        # Convert JSON to CSV
        convert_json_to_csv(JSON_FILE, 'speedtest_results.csv')

        # Return result as JSON
        return jsonify(result_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
