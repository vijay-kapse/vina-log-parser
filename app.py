import streamlit as st
import zipfile
import tempfile
import os
import re
import pandas as pd

def extract_best_mode_info(file_bytes, filename):
    try:
        content = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            content = file_bytes.decode('latin1')
        except:
            return None

    lines = content.splitlines()

    # Find header line
    for i, line in enumerate(lines):
        if "mode" in line.lower() and "affinity" in line.lower() and "rmsd" in line.lower():
            # Look for table line 2 lines below
            if i + 2 < len(lines):
                best_line = lines[i + 2].strip()
                parts = re.split(r'\s+', best_line)
                if len(parts) >= 4:
                    try:
                        return {
                            'filename': filename,
                            'affinity_kcal_per_mol': float(parts[1]),
                            'rmsd_lb': float(parts[2]),
                            'rmsd_ub': float(parts[3])
                        }
                    except ValueError:
                        return None
            break

    return None


st.title("🧬 AutoDock Vina Log Parser")
st.markdown("Upload a `.zip` file containing your `.log` files. This tool extracts the **best docking mode** from each log.")

uploaded_zip = st.file_uploader("Upload ZIP file of .log files", type="zip")

if uploaded_zip:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "logs.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        results = []
        log_file_count = 0

        for root, _, files in os.walk(tmpdir):
            for file in files:
                if file.endswith(".log"):
                    log_file_count += 1
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        result = extract_best_mode_info(f.read(), file)
                        if result:
                            results.append(result)

        if results:
            df = pd.DataFrame(results)
            st.success(f"✅ Parsed {len(results)} log file(s) out of {log_file_count} found.")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name='vina_summary.csv',
                mime='text/csv'
            )
        elif log_file_count == 0:
            st.error("🚫 No `.log` files found in the ZIP.")
        else:
            st.warning("⚠️ `.log` files found but unable to parse results from them. Please check the format.")

