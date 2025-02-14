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
            'sorted_images': {},  # Dictionary to store image data more efficiently
            'current_index': 0,
            'sorting_complete': False,
            'last_activity': datetime.now().isoformat()
        }
    
    @property
    def current_index(self):
        return st.session_state.app_state['current_index']
    
    @current_index.setter
    def current_index(self, value):
        st.session_state.app_state['current_index'] = value
    
    @property
    def sorting_complete(self):
        return st.session_state.app_state['sorting_complete']
    
    @sorting_complete.setter
    def sorting_complete(self, value):
        st.session_state.app_state['sorting_complete'] = value
    
    def add_sorted_image(self, filename, category, data):
        """Store image information more efficiently"""
        if 'sorted_images' not in st.session_state.app_state:
            st.session_state.app_state['sorted_images'] = {}
        
        st.session_state.app_state['sorted_images'][filename] = {
            'category': category,
            'data': data
        }
    
    def get_sorted_images(self):
        """Get all sorted images"""
        return st.session_state.app_state.get('sorted_images', {})
    
    def get_category_counts(self):
        """Get counts of images per category"""
        counts = {}
        for img_data in self.get_sorted_images().values():
            category = img_data['category']
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def reset(self):
        self.initialize_state()

@st.cache_data
def resize_image(img, max_width=600):
    """Cache image resizing to improve performance"""
    width, height = img.size
    if width > max_width:
        ratio = max_width / width
        new_size = (max_width, int(height * ratio))
        return img.resize(new_size, Resampling.LANCZOS)
    return img

def create_download_zip(sorted_images):
    """Create zip file from sorted images"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, img_data in sorted_images.items():
            category = img_data['category']
            file_data = img_data['data']
            
            zip_path = f"{category}/{filename}"
            zip_file.writestr(zip_path, base64.b64decode(file_data))
    
    return zip_buffer

def get_download_link(zip_buffer, total_count):
    b64 = base64.b64encode(zip_buffer.getvalue()).decode()
    return f'<a href="data:application/zip;base64,{b64}" download="sorted_images.zip" class="download-button">📥 Download Sorted Images ({total_count} files)</a>'

def main():
    st.title("Image Content Sorter")
    
    state = ImageSorterState()
    
    # CSS remains the same...
    st.markdown("""
        <style>
        .download-button {
            display: inline-block;
            padding: 0.5em 1em;
            background-color: #4CAF50;
            color: white !important;
            text-decoration: none !important;
            border-radius: 4px;
            margin: 1em 0;
        }
        .download-button:hover {
            background-color: #45a049;
            color: white !important;
            text-decoration: none !important;
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
        
        # Display current progress
        total_files = len(uploaded_files)
        progress_text = f"Processing image {state.current_index + 1} of {total_files}"
        st.write(progress_text)
        
        # Progress bar
        progress = state.current_index / total_files
        st.progress(progress)
        
        # Display current image
        try:
            current_file = uploaded_files[state.current_index]
            img = Image.open(current_file)
            img = resize_image(img)
            st.image(img, caption=current_file.name, use_column_width=False)
            
            def save_image(category):
                current_file.seek(0)
                file_data = base64.b64encode(current_file.read()).decode()
                
                state.add_sorted_image(
                    filename=current_file.name,
                    category=category,
                    data=file_data
                )
                
                state.current_index += 1
                
                if state.current_index >= total_files:
                    state.sorting_complete = True
                
                st.rerun()
            
            # Button layout
            col1, col2, col3 = st.columns(3)
            col4, col5 = st.columns(2)
            
            with col1:
                if st.button("Text Heavy", use_container_width=True):
                    save_image('text_heavy')
            with col2:
                if st.button("Visual Heavy", use_container_width=True):
                    save_image('visual_heavy')
            with col3:
                if st.button("Formatting & Layouts", use_container_width=True):
                    save_image('formatting_layouts')
            with col4:
                if st.button("Text + Visual Combo", use_container_width=True):
                    save_image('text_visual_combo')
            with col5:
                if st.button("Exercises", use_container_width=True):
                    save_image('exercises')
                    
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            state.reset()
    else:
        st.write("Please upload some images to begin sorting.")
    
    # Sidebar statistics
    st.sidebar.header("📊 Sorting Statistics")
    
    category_counts = state.get_category_counts()
    categories = {
        'text_heavy': 'Text Heavy',
        'visual_heavy': 'Visual Heavy',
        'formatting_layouts': 'Formatting & Layouts',
        'text_visual_combo': 'Text + Visual Combo',
        'exercises': 'Exercises'
    }
    
    total_processed = sum(category_counts.values())
    for category_key, display_name in categories.items():
        count = category_counts.get(category_key, 0)
        st.sidebar.write(f"{display_name}: {count} images")
    
    # Download button
    sorted_images = state.get_sorted_images()
    if sorted_images:
        st.sidebar.markdown("---")
        zip_buffer = create_download_zip(sorted_images)
        st.sidebar.markdown(
            get_download_link(zip_buffer, total_processed),
            unsafe_allow_html=True
        )
    
    # Show completion message
    if state.sorting_complete:
        st.success("✨ All images have been sorted! ✨")
        if st.button("Start New Batch"):
            state.reset()
            st.rerun()

if __name__ == "__main__":
    main()