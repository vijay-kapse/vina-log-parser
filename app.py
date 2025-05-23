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
            st.warning(f"❌ Failed to decode {filename}: {e}")
            return None

    # Normalize line endings
    lines = content.replace('\r\n', '\n').splitlines()

    for i, line in enumerate(lines):
        if "mode" in line.lower() and "affinity" in line.lower() and "rmsd" in line.lower():
            # Look for best mode on the 4th line after header
            if i + 3 < len(lines):
                best_line = lines[i + 3].strip()
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
                        st.warning(f"⚠️ Could not parse numbers in line: {best_line}")
                        return None
                else:
                    st.warning(f"⚠️ Unexpected format in line: {best_line}")
            else:
                st.warning(f"⚠️ Not enough lines after header in {filename}")
            break

    st.warning(f"⚠️ Header line not found in {filename}")
    return None

# Streamlit UI
st.title("🧬 AutoDock Vina Log Parser")
st.markdown("""
Upload either a single `.log` file **or** a `.zip` file containing multiple `.log` files.
The app extracts the **best docking conformation** (Mode 1) and displays the results.
""")

col1, col2 = st.columns(2)
with col1:
    single_log = st.file_uploader("Upload a single `.log` file", type="log")
with col2:
    zip_log = st.file_uploader("Upload a `.zip` file of `.log` files", type="zip")

results = []

# Single file
if single_log:
    result = extract_best_mode_info(single_log.read(), single_log.name)
    if result:
        results.append(result)
        st.success("✅ Parsed single `.log` file.")
    else:
        st.warning("⚠️ Unable to parse the uploaded `.log` file.")

# Zip file
elif zip_log:
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
                    with open(file_path, 'rb') as f:
                        result = extract_best_mode_info(f.read(), file)
                        if result:
                            results.append(result)

        if results:
            st.success(f"✅ Parsed {len(results)} out of {log_file_count} `.log` file(s).")
        elif log_file_count == 0:
            st.error("🚫 No `.log` files found in the ZIP.")
        else:
            st.warning("⚠️ `.log` files found but unable to parse results from them.")

# Results
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
