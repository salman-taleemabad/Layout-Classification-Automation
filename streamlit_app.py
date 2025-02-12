import streamlit as st
from PIL import Image
from PIL.Image import Resampling
import io
import zipfile
import base64
from datetime import datetime

class ImageSorterState:
    def __init__(self):
        if 'app_state' not in st.session_state:
            self.initialize_state()
        
    def initialize_state(self):
        st.session_state.app_state = {
            'processed_files': [],
            'current_index': 0,
            'sorting_complete': False,
            'last_activity': datetime.now().isoformat(),
            'total_processed': 0
        }
    
    def update_activity(self):
        st.session_state.app_state['last_activity'] = datetime.now().isoformat()
    
    @property
    def processed_files(self):
        return st.session_state.app_state['processed_files']
    
    @property
    def current_index(self):
        return st.session_state.app_state['current_index']
    
    @current_index.setter
    def current_index(self, value):
        st.session_state.app_state['current_index'] = value
        self.update_activity()
    
    @property
    def sorting_complete(self):
        return st.session_state.app_state['sorting_complete']
    
    @sorting_complete.setter
    def sorting_complete(self, value):
        st.session_state.app_state['sorting_complete'] = value
        self.update_activity()
    
    def add_processed_file(self, file_info):
        st.session_state.app_state['processed_files'].append(file_info)
        st.session_state.app_state['total_processed'] += 1
        self.update_activity()
    
    def reset(self):
        self.initialize_state()

def create_download_zip(processed_files):
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file_info in processed_files:
            category = file_info['category']
            file_data = file_info['data']
            filename = file_info['name']
            
            zip_path = f"{category}/{filename}"
            zip_file.writestr(zip_path, base64.b64decode(file_data))
    
    return zip_buffer

def get_download_link(zip_buffer, processed_count):
    b64 = base64.b64encode(zip_buffer.getvalue()).decode()
    return f'<a href="data:application/zip;base64,{b64}" download="sorted_images.zip" class="download-button">📥 Download Sorted Images ({processed_count} files)</a>'

def main():
    st.title("Image Content Sorter")
    
    state = ImageSorterState()
    
    
    st.markdown("""
        <style>
        .download-button {
            display: inline-block;
            padding: 0.5em 1em;
            background-color: #4CAF50;
            color: white !important;  /* Force white text color */
            text-decoration: none !important;  /* Remove underline */
            border-radius: 4px;
            margin: 1em 0;
        }
        .download-button:hover {
            background-color: #45a049;  /* Slightly darker on hover */
            color: white !important;  /* Keep text white on hover */
            text-decoration: none !important;  /* Ensure no underline on hover */
        }
        div.stButton > button {
            height: 75px;
            white-space: normal;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload your images", 
        type=['png', 'jpg', 'jpeg', 'gif'],
        accept_multiple_files=True,
        key='file_uploader'
    )

    if uploaded_files:
        if 'current_files' not in st.session_state or uploaded_files != st.session_state.current_files:
            st.session_state.current_files = uploaded_files
            state.reset()
    
    # Show completion state if sorting is done
    if state.sorting_complete and state.processed_files:
        st.success("✨ All images have been sorted! ✨")
        
        if st.button("Start New Batch"):
            state.reset()
            st.rerun()
            
    # Main sorting interface
    if uploaded_files:
        # Display current progress
        total_files = len(uploaded_files)
        progress_text = f"Processing image {state.current_index + 1} of {total_files}"
        st.write(progress_text)
        
        # Add a progress bar
        progress_bar = st.progress(state.current_index / total_files)
        
        # Display current image
        try:
            current_file = uploaded_files[state.current_index]
            img = Image.open(current_file)
            
            # Calculate new size while maintaining aspect ratio
            max_width = 600
            width, height = img.size
            if width > max_width:
                ratio = max_width / width
                new_size = (max_width, int(height * ratio))
                img = img.resize(new_size, Resampling.LANCZOS)
            
            st.image(img, caption=current_file.name, use_container_width =False)
            
            def save_image(category):
                current_file.seek(0)
                file_data = base64.b64encode(current_file.read()).decode()
                
                state.add_processed_file({
                    'name': current_file.name,
                    'category': category,
                    'data': file_data
                })
                
                state.current_index += 1
                
                if state.current_index >= total_files:
                    state.sorting_complete = True
                
                st.rerun()
            
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
            
        except Exception as e:
            st.error("Error processing image. Please try uploading again.")
            state.reset()
    else:
        st.write("Please upload some images to begin sorting.")
    
    # Display statistics in the sidebar
    st.sidebar.header("📊 Sorting Statistics")
    categories = {
        'text_heavy': 'Text Heavy',
        'visual_heavy': 'Visual Heavy',
        'formatting_layouts': 'Formatting & Layouts',
        'text_visual_combo': 'Text + Visual Combo',
        'exercises': 'Exercises'
    }
    
    total_processed = 0
    for category, display_name in categories.items():
        count = len([f for f in state.processed_files if f['category'] == category])
        total_processed += count
        st.sidebar.write(f"{display_name}: {count} images")
    
    # Add download button in sidebar if there are processed files
    if state.processed_files:
        st.sidebar.markdown("---")
        zip_buffer = create_download_zip(state.processed_files)
        st.sidebar.markdown(
            get_download_link(zip_buffer, total_processed), 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()