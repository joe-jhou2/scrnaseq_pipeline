
"""
Streamlit Web Form for Sample Registration
Run with: streamlit run sample_registration_form.py
"""
import os
import streamlit as st
from sqlalchemy import create_engine, text, bindparam
import pandas as pd
from datetime import datetime
# import psycopg2
# from pathlib import Path

# Load environment variables (customize this as needed)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POSTGRES_USER=os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB=os.getenv('POSTGRES_DB')
POSTGRES_HOST = 'mydb'
POSTGRES_PORT = 32395

# Page config
st.set_page_config(
    page_title="Sample Registration System",
    page_icon="🧬",
    layout="wide"
)


def connect_db():
    """Connect to PostgreSQL database"""
    try:
        # conn = psycopg2.connect(**DB_CONFIG)
        engine = create_engine(f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
        return engine
        # return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


def register_sample(sample_data):
    """Register a single sample to database using SQLAlchemy"""
    engine = connect_db()
    if not engine:
        return False
    
    try:
        with engine.begin() as conn:
        # Check if sample already exists
            check_query = text("""
                    SELECT SampleName
                    FROM scRNAseq_Samples
                    WHERE SampleName = :sample_name
                """)
            result = conn.execute(check_query, {"sample_name": sample_data["SampleName"]}).fetchone()

            if result:
                st.warning(f"⚠️ Sample '{sample_data['SampleName']}' already exists!")
                return False
        
            # Insert new sample
            insert_query = text("""
                    INSERT INTO scRNAseq_Samples
                    (SampleName, AnonyName, Subject, PID, Alias, Batch, Tissue,
                    TimePoint, log10_VL, Plate, SampleDate, Days2Lesion, SeqType,
                    FileName, FilePath, Status, PipelineVersion, Checksum, Notes)
                    VALUES (:SampleName, :AnonyName, :Subject, :PID, :Alias, :Batch, :Tissue,
                            :TimePoint, :log10_VL, :Plate, :SampleDate, :Days2Lesion, :SeqType,
                            :FileName, :FilePath, :Status, :PipelineVersion, :Checksum, :Notes)
                """)

            conn.execute(insert_query, {
                    "SampleName": sample_data["SampleName"],
                    "AnonyName": sample_data.get("AnonyName"),
                    "Subject": sample_data.get("Subject"),
                    "PID": sample_data.get("PID"),
                    "Alias": sample_data.get("Alias"),
                    "Batch": sample_data.get("Batch"),
                    "Tissue": sample_data.get("Tissue"),
                    "TimePoint": sample_data.get("TimePoint"),
                    "log10_VL": sample_data.get("log10_VL"),
                    "Plate": sample_data.get("Plate"),
                    "SampleDate": sample_data.get("SampleDate"),
                    "Days2Lesion": sample_data.get("Days2Lesion"),
                    "SeqType": sample_data.get("SeqType"),
                    "FileName": sample_data.get("FileName"),
                    "FilePath": sample_data.get("FilePath"),
                    "Status": sample_data.get("Status", "raw"),
                    "PipelineVersion": sample_data.get("PipelineVersion"),
                    "Checksum": sample_data.get("Checksum"),
                    "Notes": sample_data.get("Notes"),
                })

        st.success(f"✅ Sample '{sample_data['SampleName']}' registered successfully!")
        return True
        
    except Exception as e:
        st.error(f"Error registering sample: {e}")
        return False
    
    
def bulk_upload(df):
    """Bulk register samples from DataFrame using SQLAlchemy"""
    engine = connect_db()
    if not engine:
        return

    inserted = 0
    skipped = 0
    errors = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    insert_query = text("""
        INSERT INTO scRNAseq_Samples
        (SampleName, AnonyName, Subject, PID, Alias, Batch, Tissue,
         TimePoint, log10_VL, Plate, SampleDate, Days2Lesion, SeqType,
         FileName, FilePath, Status, PipelineVersion, Checksum, Notes)
        VALUES (:SampleName, :AnonyName, :Subject, :PID, :Alias, :Batch, :Tissue,
                :TimePoint, :log10_VL, :Plate, :SampleDate, :Days2Lesion, :SeqType,
                :FileName, :FilePath, :Status, :PipelineVersion, :Checksum, :Notes)
    """)

    with engine.begin() as conn:  # automatic commit or rollback
        for idx, row in df.iterrows():
            try:
                sample_name = str(row["SampleName"]).strip()
                check_query = text("""
                    SELECT SampleName FROM scRNAseq_Samples WHERE SampleName = :sample_name
                """)
                exists = conn.execute(check_query, {"sample_name": sample_name}).fetchone()

                if exists:
                    skipped += 1
                    status_text.text(f"Skipped: {sample_name} (already exists)")
                else:
                    conn.execute(insert_query, {
                        "SampleName": sample_name,
                        "AnonyName": str(row.get("AnonyName")) if pd.notna(row.get("AnonyName")) else None,
                        "Subject": str(row.get("Subject")) if pd.notna(row.get("Subject")) else None,
                        "PID": str(row.get("PID")) if pd.notna(row.get("PID")) else None,
                        "Alias": str(row.get("Alias")) if pd.notna(row.get("Alias")) else None,
                        "Batch": str(row.get("Batch")) if pd.notna(row.get("Batch")) else None,
                        "Tissue": str(row.get("Tissue")) if pd.notna(row.get("Tissue")) else None,
                        "TimePoint": str(row.get("TimePoint")) if pd.notna(row.get("TimePoint")) else None,
                        "log10_VL": float(row.get("log10_VL")) if pd.notna(row.get("log10_VL")) else None,
                        "Plate": str(row.get("Plate")) if pd.notna(row.get("Plate")) else None,
                        "SampleDate": pd.to_datetime(row.get("SampleDate")).date() if pd.notna(row.get("SampleDate")) else None,
                        "Days2Lesion": int(row.get("Days2Lesion")) if pd.notna(row.get("Days2Lesion")) else None,
                        "SeqType": str(row.get("SeqType")) if pd.notna(row.get("SeqType")) else None,
                        "FileName": str(row.get("FileName")) if pd.notna(row.get("FileName")) else None,
                        "FilePath": str(row.get("FilePath")) if pd.notna(row.get("FilePath")) else None,
                        "Status": str(row.get("Status", "raw")),
                        "PipelineVersion": str(row.get("PipelineVersion")) if pd.notna(row.get("PipelineVersion")) else None,
                        "Checksum": str(row.get("Checksum")) if pd.notna(row.get("Checksum")) else None,
                        "Notes": str(row.get("Notes")) if pd.notna(row.get("Notes")) else None
                    })
                    inserted += 1
                    status_text.text(f"Inserted: {sample_name}")

                progress_bar.progress((idx + 1) / len(df))

            except Exception as e:
                errors.append(f"{sample_name}: {str(e)}")
                status_text.text(f"Error with {sample_name}")

    progress_bar.empty()
    status_text.empty()

    st.success(f"✅ Bulk upload complete: {inserted} inserted, {skipped} skipped")

    if errors:
        with st.expander("⚠️ Errors encountered"):
            for err in errors:
                st.text(err)

def view_samples():
    """View registered samples"""
    engine = connect_db()
    if not engine:
        return

    # Filters
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        sample_name_filter = st.text_input("Filter by Sample Name:", "", key="filter_sample_name")
    with col2:
        subject_name_filter = st.text_input("Filter by Subject Name:", "", key="filter_subject_name")
    with col3:
        batch_filter = st.text_input("Filter by Batch:", "", key="filter_batch")
    with col4:
        tissue_filter = st.text_input("Filter by Tissue:", "", key="filter_tissue")
    with col5:
        seqtype_filter = st.text_input("Filter by SeqType:", "", key="filter_seqtype")


    # Build query dynamically
    query = """
        SELECT * FROM scRNAseq_Samples WHERE 1=1
    """
    params = {}
    if sample_name_filter:
        query += " AND samplename ILIKE :samplename"
        params["samplename"] = f"%{sample_name_filter}%"
    if subject_name_filter:
        query += " AND subject ILIKE :subject"
        params["subject"] = f"%{subject_name_filter}%"
    if batch_filter:
        query += " AND batch ILIKE :batch"
        params["batch"] = f"%{batch_filter}%"
    if tissue_filter:
        query += " AND tissue ILIKE :tissue"
        params["tissue"] = f"%{tissue_filter}%"
    if seqtype_filter:
        query += " AND seqtype ILIKE :seqtype"
        params["seqtype"] = f"%{seqtype_filter}%"

    query += " ORDER BY SampleDate DESC, SampleName LIMIT 100"

    try:
        df = pd.read_sql(text(query), engine, params=params)

        if df.empty:
            st.info("No samples found matching the filters")
            return

        st.write("### Samples Table")
        st.caption("Select rows below to delete specific samples.")

        df_display = df.copy()
        df_display.insert(0, "Select", False)

        edited_df = st.data_editor(df_display, width='stretch', height=400, key="sample_editor")
        selected_rows = edited_df[edited_df["Select"]]

        if not selected_rows.empty:
            st.warning(f"{len(selected_rows)} sample(s) selected for deletion.")
            if st.button("❌ Delete Selected Samples"):
                st.session_state["confirm_delete"] = True

        if st.session_state.get("confirm_delete", False):
            st.warning("⚠️ Are you sure you want to permanently delete the selected samples?")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Yes, delete"):
                    try:
                        with engine.begin() as conn:
                            sample_names = selected_rows["samplename"].tolist()
                            if sample_names:
                                with engine.begin() as conn:
                                    delete_query = text(
                                        "DELETE FROM scrnaseq_samples WHERE samplename IN :names"
                                    ).bindparams(bindparam("names", expanding=True))
                                    conn.execute(delete_query, {"names": sample_names})

                                st.success(f"Deleted {len(sample_names)} sample(s) successfully.")
                                st.session_state["confirm_delete"] = False
                                st.rerun()

                    except Exception as e:
                        st.error(f"Error deleting samples: {e}")

            with col_b:
                if st.button("❌ Cancel"):
                    st.session_state["confirm_delete"] = False

        # Summary + download
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Samples", len(df))
        col2.metric("Batches", df["Batch"].nunique() if "Batch" in df.columns else 0)
        col3.metric("Tissues", df["Tissue"].nunique() if "Tissue" in df.columns else 0)
        col4.metric("Raw Samples", len(df[df["Status"] == "raw"]) if "Status" in df.columns else 0)

        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"samples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error querying database: {e}")


def create_template():
    """Create Excel/CSV template"""
    template_data = {
        'SampleName': ['JK_9149', 'JK_9150', 'JK_9151'],
        'AnonyName': ['Sample001', 'Sample002', 'Sample003'],
        'Subject': ['Subject1', 'Subject1', 'Subject2'],
        'PID': ['PID001', 'PID001', 'PID002'],
        'Alias': ['Alias1', 'Alias2', 'Alias3'],
        'Batch': ['Batch4', 'Batch4', 'Batch4'],
        'Tissue': ['Cervix', 'Cervix', 'Blood'],
        'TimePoint': ['8wk', '8wk', '12wk'],
        'log10_VL': [0, 2.5, 1.8],
        'Plate': ['Y', 'Y', 'N'],
        'SampleDate': ['2020-03-11', '2020-03-11', '2020-03-15'],
        'Days2Lesion': [56, 56, 84],
        'SeqType': ["GEX", "TCR", "BCR"],
        'FileName': ['', '', ''],
        'FilePath': ['', '', ''],
        'Status': ['raw', 'raw', 'raw'],
        'PipelineVersion': ['', '', ''],
        'Checksum': ['', '', ''],
        'Notes': ['Good quality', 'May need rerun', 'Priority sample']
    }
    
    return pd.DataFrame(template_data)


# ==============================================================================
# MAIN APP
# ==============================================================================

st.title("🧬 HSV Lab Single-cell Sequencing Sample Registration System")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ["Register Single Sample", "Bulk Upload", "View Samples"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")

# Quick stats using SQLAlchemy
engine = connect_db()
if engine:
    try:
        with engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM scrnaseq_samples")).scalar()
            subject = conn.execute(text("SELECT COUNT(DISTINCT pid) FROM scrnaseq_samples")).scalar()
            GEX = conn.execute(text("SELECT COUNT(*) FROM scrnaseq_samples WHERE seqtype = 'GEX'")).scalar()
            TCR = conn.execute(text("SELECT COUNT(*) FROM scrnaseq_samples WHERE seqtype = 'TCR'")).scalar()
            BCR = conn.execute(text("SELECT COUNT(*) FROM scrnaseq_samples WHERE seqtype = 'BCR'")).scalar()

        st.sidebar.metric("Total Samples", total)
        st.sidebar.metric("Total Subjects", subject)
        st.sidebar.metric("GEX samples", GEX)
        st.sidebar.metric("TCR samples", TCR)
        st.sidebar.metric("BCR samples", BCR)
    except Exception as e:
        st.sidebar.error(f"Error fetching stats: {e}")
        
# ==============================================================================
# PAGE 1: Single Sample Registration
# ==============================================================================

if page == "Register Single Sample":
    st.header("Register Single Sample")
    
    with st.form("single_sample_form"):
        st.subheader("🔹 Basic Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sample_name = st.text_input("Sample Name *", placeholder="e.g., JK_9149", help="Required - Primary key")
            anony_name = st.text_input("Anonymous Name", placeholder="e.g., Sample001")
            subject = st.text_input("Subject", placeholder="e.g., Subject1")
        
        with col2:
            pid = st.text_input("Patient ID (PID)", placeholder="e.g., PID001")
            alias = st.text_input("Alias", placeholder="Alternative name")
            batch = st.text_input("Batch", placeholder="e.g., Batch4")
        
        with col3:
            tissue = st.text_input("Tissue", placeholder="e.g., Cervix")
            timepoint = st.text_input("Time Point", placeholder="e.g., 8wk")
            plate = st.text_input("Plate", placeholder="e.g., Y or N")
        
        st.subheader("🔹 Clinical Data")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            log10_vl = st.number_input("log10 Viral Load", value=0.0, step=0.1, format="%.2f")
        with col2:
            sample_date = st.date_input("Sample Date", value=None)
        with col3:
            days2lesion = st.number_input("Days to Lesion", value=0, step=1, min_value=0)
        
        st.subheader("🔹 Sequencing Information")
        col1, col2 = st.columns(2)
        
        with col1:
            seq_type = st.selectbox("Sequencing Type", ["", "GEX", "TCR", "BCR", "ATAC", "CITE-seq", "Multiome"])
            file_name = st.text_input("File Name", placeholder="Processed filename")
        
        with col2:
            file_path = st.text_input("File Path", placeholder="Full path to file")
            status = st.selectbox("Status", ["raw", "processing", "processed", "failed", "qc_failed"])
        
        st.subheader("🔹 Pipeline & QC")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pipeline_version = st.text_input("Pipeline Version", placeholder="e.g., nf-core/scrnaseq v2.1.0")
        with col2:
            checksum = st.text_input("Checksum (MD5)", placeholder="32-character MD5 hash")
        with col3:
            st.write("")  # Spacer
        
        notes = st.text_area("Notes", placeholder="Any additional information...", height=100)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            submitted = st.form_submit_button("Register Sample", type="primary", width='stretch')
        with col3:
            clear = st.form_submit_button("Clear Form", width='stretch')
        
        if submitted:
            if not sample_name:
                st.error("❌ Sample Name is required!")
            else:
                sample_data = {
                    'SampleName': sample_name.strip(),
                    'AnonyName': anony_name.strip() if anony_name else None,
                    'Subject': subject.strip() if subject else None,
                    'PID': pid.strip() if pid else None,
                    'Alias': alias.strip() if alias else None,
                    'Batch': batch.strip() if batch else None,
                    'Tissue': tissue.strip() if tissue else None,
                    'TimePoint': timepoint.strip() if timepoint else None,
                    'log10_VL': log10_vl if log10_vl != 0.0 else None,
                    'Plate': plate.strip() if plate else None,
                    'SampleDate': sample_date,
                    'Days2Lesion': days2lesion if days2lesion > 0 else None,
                    'SeqType': seq_type if seq_type else None,
                    'FileName': file_name.strip() if file_name else None,
                    'FilePath': file_path.strip() if file_path else None,
                    'Status': status,
                    'PipelineVersion': pipeline_version.strip() if pipeline_version else None,
                    'Checksum': checksum.strip() if checksum else None,
                    'Notes': notes.strip() if notes else None
                }
                register_sample(sample_data)

# ==============================================================================
# PAGE 2: Bulk Upload
# ==============================================================================

elif page == "Bulk Upload":
    st.header("Bulk Upload Samples")
    
    st.markdown("""
    Upload an Excel or CSV file with your samples. 
    
    **Required column:**
    - `SampleName` (unique identifier)
    - `AnonyName`, `Subject`, `PID`, `Alias`, `Batch`, `Tissue`, `TimePoint`, 
    `log10_VL`, `Plate`, `SampleDate`, `Days2Lesion`, `SeqType`, `FileName`, 
    `FilePath`, `Status`, `PipelineVersion`, `Checksum`, `Notes`
    """)
    
    # Download template
    col1, col2 = st.columns(2)
    
    with col1:
        template_df = create_template()
        template_csv = template_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV Template",
            data=template_csv,
            file_name="sample_registration_template.csv",
            mime="text/csv",
            width='stretch'
        )
    
    with col2:
        # Create Excel template
        import io
        template_excel = io.BytesIO()
        with pd.ExcelWriter(template_excel, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Samples')
        template_excel.seek(0)
        
        st.download_button(
            label="📥 Download Excel Template",
            data=template_excel,
            file_name="sample_registration_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )
    
    st.markdown("---")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your sample file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload Excel or CSV file with sample information"
    )
    
    if uploaded_file:
        # Read file
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File loaded: {len(df)} samples found")
            
            # Preview
            st.subheader("Preview")
            st.dataframe(df.head(10), width='stretch')
            
            # Validate
            if 'SampleName' not in df.columns:
                st.error("❌ Missing required column: SampleName")
            else:
                # Check for duplicates in file
                duplicates = df[df.duplicated(subset=['SampleName'], keep=False)]
                if not duplicates.empty:
                    st.warning(f"⚠️ Found {len(duplicates)} duplicate SampleNames in file:")
                    st.dataframe(duplicates[['SampleName']], width='stretch')
                
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("🚀 Import All Samples", type="primary", width='stretch'):
                        bulk_upload(df)
                with col2:
                    if st.button("🔍 Check for Existing", width='stretch'):
                        engine = connect_db()
                        if engine:
                            existing = []
                            try:
                                with engine.connect() as conn:
                                    # Prepare parameterized query
                                    check_query = text("""
                                        SELECT SampleName
                                        FROM scRNAseq_Samples
                                        WHERE SampleName = :sample
                                    """)

                                    # Loop through all SampleNames in the uploaded DataFrame
                                    for sample in df["SampleName"]:
                                        result = conn.execute(check_query, {"sample": sample}).fetchone()
                                        if result:
                                            existing.append(sample)

                                # Show results
                                if existing:
                                    st.warning(f"⚠️ {len(existing)} samples already exist:")
                                    st.write(existing[:10])
                                    if len(existing) > 10:
                                        st.write(f"... and {len(existing) - 10} more")
                                else:
                                    st.success("✅ No existing samples found")

                            except Exception as e:
                                st.error(f"Error checking existing samples: {e}")

        except Exception as e:
            st.error(f"Error reading file: {e}")

# ==============================================================================
# PAGE 3: View Samples
# ==============================================================================

elif page == "View Samples":
    st.header("View Registered Samples")
    view_samples()


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>scRNA-seq Sample Registration System v1.0</div>",
    unsafe_allow_html=True
)