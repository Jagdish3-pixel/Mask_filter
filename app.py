from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pandas as pd
import os
from io import BytesIO

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flashing messages

UPLOAD_FOLDER = 'static'
EXCEL_FILES = {
    'GF130BCD': 'GF130BCD.xlsx',
    'GF55BCD': 'GF55BCD.xlsx',
    'GF22FDX': 'GF22FDX.xlsx',
    'GF28SLPeESF3': 'GF28SLPeESF3.xlsx',
    'GF40LP_ESF3H': 'GF40LP_ESF3H.xlsx',
    'GF12LPP': 'GF12LPP.xlsx'
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        mask_input = request.form.get('mask_input', '')
        selected_tech = request.form.get('tech_option', '')
        if not mask_input or not selected_tech:
            flash("Please provide both mask input and technology.")
            return redirect(url_for('index'))

        mask_set = set(m.strip() for m in mask_input.split(',') if m.strip())
        file_name = EXCEL_FILES.get(selected_tech)

        if not file_name or not os.path.exists(file_name):
            flash(f"Excel file for {selected_tech} not found.")
            return redirect(url_for('index'))

        df = pd.read_excel(file_name, dtype=str)
        if 'Device_Name' not in df.columns or 'Additional_Mask' not in df.columns:
            flash("Excel must have 'Device_Name' and 'Additional_Mask' columns.")
            return redirect(url_for('index'))

        results = []
        for _, row in df.iterrows():
            masks = [m.strip() for m in str(row['Additional_Mask']).replace(';', ',').split(',') if m.strip()]
            if masks and set(masks).issubset(mask_set):
                results.append((row['Device_Name'], ', '.join(masks)))

        joined_data = '|'.join(str(row) for row in results)
        return render_template('result.html', data=results, tech=selected_tech, joined_data=joined_data)


    return render_template('index.html', tech_list=EXCEL_FILES.keys())

@app.route('/download', methods=['POST'])
def download():
    results = request.form.get('results')
    if results:
        rows = [eval(row) for row in results.split('|') if row]
        df = pd.DataFrame(rows, columns=['Device_Name', 'Additional_Mask'])
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return send_file(output, download_name="filtered_results.xlsx", as_attachment=True)
    flash("No data to download.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
