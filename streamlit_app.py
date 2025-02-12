import streamlit as st
import os
from PIL import Image
import io
import tempfile
import zipfile
import base64

def setup_folders():
    # Create temporary directory for this session if it doesn't exist
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()
        
    # Create category folders within the temp directory
    categories = [
        'text_heavy',
        'visual_heavy',
        'formatting_layouts',
        'text_visual_combo',
        'exercises'
    ]
    for category in categories:
        category_path = os.path.join(st.session_state.temp_dir, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)

def create_download_zip():
    """Create a zip file containing all sorted images"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file_info in st.session_state.processed_files:
            category = file_info['category']
            file_obj = file_info['data']
            filename = file_info['name']
            
            # Save in appropriate folder structure within zip
            zip_path = f"{category}/{filename}"
            zip_file.writestr(zip_path, file_obj.getvalue())
    
    return zip_buffer

def get_download_link(zip_buffer):
    """Generate a download link for the zip file"""
    b64 = base64.b64encode(zip_buffer.getvalue()).decode()
    return f'<a href="data:application/zip;base64,{b64}" download="sorted_images.zip">Download Sorted Images</a>'

def main():
    st.title("Image Content Sorter")
    
    # Initialize session state
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'sorting_complete' not in st.session_state:
        st.session_state.sorting_complete = False
    
    # Setup folders
    setup_folders()
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload your images", 
        type=['png', 'jpg', 'jpeg', 'gif'],
        accept_multiple_files=True
    )
    
    # Handle newly uploaded files
    if uploaded_files and uploaded_files != st.session_state.uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.session_state.current_index = 0
        st.session_state.sorting_complete = False
        st.session_state.processed_files = []
        st.rerun()

    # Show completion state if sorting is done
    if st.session_state.sorting_complete:
        st.balloons()
        st.success("✨ All images have been sorted! ✨")
        
        # Create download link for zip file
        zip_buffer = create_download_zip()
        st.markdown(get_download_link(zip_buffer), unsafe_allow_html=True)
        
        # Display categorized files
        st.write("### Sorted Images")
        categories = ['text_heavy', 'visual_heavy', 'formatting_layouts', 
                    'text_visual_combo', 'exercises']
        
        for category in categories:
            files = [f for f in st.session_state.processed_files 
                    if f['category'] == category]
            if files:
                st.write(f"**{category.replace('_', ' ').title()}**")
                for file in files:
                    st.write(f"- {file['name']}")
        
        if st.button("Start New Batch"):
            st.session_state.current_index = 0
            st.session_state.uploaded_files = []
            st.session_state.processed_files = []
            st.session_state.sorting_complete = False
            st.experimental_rerun()
        return

    # Check if we have files to process
    if not st.session_state.uploaded_files:
        st.write("Please upload some images to begin sorting.")
        return
    
    # Display current progress
    total_files = len(st.session_state.uploaded_files)
    progress_text = f"Processing image {st.session_state.current_index + 1} of {total_files}"
    st.write(progress_text)
    
    # Add a progress bar
    progress_bar = st.progress(st.session_state.current_index / total_files)
    
    # Display current image
    current_file = st.session_state.uploaded_files[st.session_state.current_index]
    img = Image.open(current_file)
    st.image(img, caption=current_file.name)
    
    def save_image(category):
        current_file = st.session_state.uploaded_files[st.session_state.current_index]
        
        # Store file data in session state
        current_file.seek(0)  # Reset file pointer
        st.session_state.processed_files.append({
            'name': current_file.name,
            'category': category,
            'data': io.BytesIO(current_file.read())
        })
        
        # Move to next image
        st.session_state.current_index += 1
        
        # Check if we're done
        if st.session_state.current_index >= len(st.session_state.uploaded_files):
            st.session_state.sorting_complete = True
        
        st.rerun()
    
    # Create buttons with custom styling
    button_style = """
    <style>
    div.stButton > button {
        height: 75px;
        white-space: normal;
        padding: 10px;
    }
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
    
    # Create columns for buttons
    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)
    
    # First row of buttons
    with col1:
        if st.button("Text Heavy", use_container_width=True):
            save_image('text_heavy')
    
    with col2:
        if st.button("Visual Heavy", use_container_width=True):
            save_image('visual_heavy')
    
    with col3:
        if st.button("Formatting & Layouts", use_container_width=True):
            save_image('formatting_layouts')
    
    # Second row of buttons
    with col4:
        if st.button("Text + Visual Combo", use_container_width=True):
            save_image('text_visual_combo')
    
    with col5:
        if st.button("Exercises", use_container_width=True):
            save_image('exercises')
    
    # Display statistics in the sidebar
    st.sidebar.header("📊 Sorting Statistics")
    categories = {
        'text_heavy': 'Text Heavy',
        'visual_heavy': 'Visual Heavy',
        'formatting_layouts': 'Formatting & Layouts',
        'text_visual_combo': 'Text + Visual Combo',
        'exercises': 'Exercises'
    }
    
    for category, display_name in categories.items():
        count = len([f for f in st.session_state.processed_files 
                    if f['category'] == category])
        st.sidebar.write(f"{display_name}: {count} images")

if __name__ == "__main__":
    main()