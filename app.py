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
        except Exception as e:
            return None

    lines = content.splitlines()

    for i, line in enumerate(lines):
        if "mode" in line.lower() and "affinity" in line.lower() and "rmsd" in line.lower():
            if i + 2 < len(lines):
                best_line = lines[i + 2].strip()
                parts = re.split(r'\s+', best_line)
                if len(parts) >= 4 and parts[0].isdigit():
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

st.markdown("""
Upload either a single `.log` file **or** a `.zip` file containing multiple `.log` files.
The app extracts the **best docking conformation** (Mode 1) and displays the results.
""")

debug = st.sidebar.checkbox("🔧 Enable Debug Logs")

col1, col2 = st.columns(2)
with col1:
    single_log = st.file_uploader("Upload a single `.log` file", type="log")
with col2:
    zip_log = st.file_uploader("Upload a `.zip` file of `.log` files", type="zip")

results = []

if single_log:
    file_bytes = single_log.read()
    result = extract_best_mode_info(file_bytes, single_log.name)
    if result:
        results.append(result)
        st.success("✅ Parsed single `.log` file.")
        if debug:
            st.write("Parsed result:", result)
    else:
        st.warning("⚠️ Unable to parse the uploaded `.log` file.")
        if debug:
            st.write("Raw content:", file_bytes[:300])

if zip_log:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "logs.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_log.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        log_file_count = 0
        for root, _, files in os.walk(tmpdir):
            for file in files:
                if file.endswith(".log"):
                    log_file_count += 1
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            file_bytes = f.read()
                            result = extract_best_mode_info(file_bytes, file)
                            if result:
                                results.append(result)
                                if debug:
                                    st.write(f"Parsed: {file}")
                            elif debug:
                                st.write(f"Could not parse: {file}")
                    except Exception as e:
                        if debug:
                            st.error(f"Error reading {file}: {e}")

        if results:
            st.success(f"✅ Parsed {len(results)} out of {log_file_count} `.log` file(s).")
        elif log_file_count == 0:
            st.error("🚫 No `.log` files found in the ZIP.")
        else:
            st.warning("⚠️ `.log` files found but unable to parse results from them.")

if results:
    df = pd.DataFrame(results)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='vina_summary.csv',
        mime='text/csv'
    )

