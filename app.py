from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
import dwlr_analyzer  # For anomaly detection

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb+srv://jjaswanthk:liM4NHLBGOR6JafC@cluster0.6q9oj.mongodb.net/')
db = client['dwlr_db']
dwlrs = db['dwlrs_collection']

@app.route('/')
def home():
    """Render the homepage with a list of DWLRs and their status."""
    # Fetch all DWLRs from the database
    all_dwlrs = list(dwlrs.find({}))
    # Render the 'index.html' template and pass the DWLR data to it
    return render_template('index.html', dwlrs=all_dwlrs)

@app.route('/api/dwlr/<dwlr_id>', methods=['GET'])
def get_dwlr_data(dwlr_id):
    """Fetch data for a specific DWLR."""
    dwlr = dwlrs.find_one({"dwlr_id": dwlr_id})
    if dwlr:
        return jsonify(dwlr), 200
    else:
        return jsonify({"error": "DWLR not found"}), 404

@app.route('/api/dwlr/analyze/<dwlr_id>', methods=['GET'])
def analyze_dwlr(dwlr_id):
    """Analyze DWLR data for anomalies."""
    dwlr_data = dwlrs.find_one({"dwlr_id": dwlr_id})
    if dwlr_data:
        analysis_result = dwlr_analyzer.analyze(dwlr_data)
        return jsonify(analysis_result), 200
    else:
        return jsonify({"error": "DWLR not found"}), 404
    
@app.route('/dwlr/<dwlr_id>/old-data')
def dwlr_old_data(dwlr_id):
    """Display all historical data for a particular DWLR."""
    dwlr = dwlrs.find_one({"dwlr_id": dwlr_id})
    
    if dwlr:
        # Render the old data on a new page
        return render_template('old_data.html', dwlr=dwlr)
    else:
        return "DWLR not found", 404

@app.route('/api/dwlr', methods=['POST'])
def add_dwlr_data():
    """Insert new DWLR data."""
    data = request.json
    result = dwlrs.insert_one(data)
    return jsonify({"message": "DWLR data added", "id": str(result.inserted_id)}), 201

if __name__ == '__main__':
    app.run(debug=True)
