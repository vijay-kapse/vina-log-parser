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
            st.warning(f"❌ Could not decode {filename}")
            return None

    mode1_match = re.search(
        r"mode\s+\|\s+affinity\s+\|.*?\n[-+\s]+\n\s*1\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    if mode1_match:
        try:
            affinity = float(mode1_match.group(1))
            rmsd_lb = float(mode1_match.group(2))
            rmsd_ub = float(mode1_match.group(3))
            return {
                'filename': filename,
                'affinity_kcal_per_mol': affinity,
                'rmsd_lb': rmsd_lb,
                'rmsd_ub': rmsd_ub
            }
        except ValueError:
            st.warning(f"⚠️ Found Mode 1 line but couldn't parse numbers in {filename}")
    else:
        st.warning(f"⚠️ Mode 1 block not found in {filename}")
    return None

# --- Streamlit UI ---
st.title("🧬 AutoDock Vina Log Parser")
st.markdown("""
Upload `.log` files individually or as a `.zip` archive containing multiple `.log` files.
This tool extracts the **best docking mode (Mode 1)** from each file and summarizes the results.
""")

uploaded_logs = st.file_uploader(
    "Upload `.log` file(s)",
    type=["log"],
    accept_multiple_files=True
)

zip_log = st.file_uploader(
    "Or upload a `.zip` file of `.log` files",
    type="zip"
)

results = []

# --- Handle multiple individual .log files ---
if uploaded_logs:
    for file in uploaded_logs:
        result = extract_best_mode_info(file.read(), file.name)
        if result:
            results.append(result)
    if results:
        st.success(f"✅ Parsed {len(results)} of {len(uploaded_logs)} uploaded `.log` files.")
    else:
        st.warning("⚠️ No valid results parsed from uploaded files.")

# --- Handle ZIP upload ---
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
            st.success(f"✅ Parsed {len(results)} out of {log_file_count} `.log` file(s) in ZIP.")
        elif log_file_count == 0:
            st.error("🚫 No `.log` files found in the ZIP.")
        else:
            st.warning("⚠️ `.log` files found but unable to parse results from them.")

# --- Display results ---
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
