import streamlit as st
import os
import shutil
from PIL import Image
import glob

def setup_folders():
    # Create category folders if they don't exist
    categories = [
        'text_heavy',
        'visual_heavy',
        'formatting_layouts',
        'text_visual_combo',
        'exercises'
    ]
    for category in categories:
        if not os.path.exists(category):
            os.makedirs(category)

def get_image_files(source_folder):
    # Get all image files from the source folder
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif']
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(source_folder, ext)))
    return image_files

def main():
    st.title("Image Content Sorter")
    
    # Initialize session state for tracking progress
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'image_files' not in st.session_state:
        st.session_state.image_files = []
    if 'source_folder' not in st.session_state:
        st.session_state.source_folder = None
        
    # Setup category folders
    setup_folders()
    
    # Folder selection
    source_folder = st.text_input("Enter the path to your source image folder:")
    
    if source_folder and source_folder != st.session_state.source_folder:
        if os.path.exists(source_folder):
            st.session_state.source_folder = source_folder
            st.session_state.image_files = get_image_files(source_folder)
            st.session_state.current_index = 0
            st.st.rerun()
        else:
            st.error("Folder not found!")
            return
    
    # Check if we have images to process
    if not st.session_state.image_files:
        if st.session_state.source_folder:
            st.write("No images found in the specified folder!")
        return
    
    # Display current progress
    total_images = len(st.session_state.image_files)
    progress_text = f"Processing image {st.session_state.current_index + 1} of {total_images}"
    st.write(progress_text)
    
    # Add a progress bar
    progress_bar = st.progress(st.session_state.current_index / total_images)
    
    # Display current image
    current_image_path = st.session_state.image_files[st.session_state.current_index]
    img = Image.open(current_image_path)
    st.image(img, caption=os.path.basename(current_image_path))
    
    # Handle image categorization
    def move_image(category):
        dest_path = os.path.join(category, os.path.basename(current_image_path))
        shutil.copy2(current_image_path, dest_path)
        
        # Move to next image
        st.session_state.current_index += 1
        
        # Check if we're done
        if st.session_state.current_index >= len(st.session_state.image_files):
            st.balloons()  # Add a celebratory effect
            st.success("✨ All images have been sorted! ✨")
            st.session_state.current_index = 0
            st.session_state.image_files = []
            st.session_state.source_folder = None
        
        st.st.rerun()
    
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
            move_image('text_heavy')
    
    with col2:
        if st.button("Visual Heavy", use_container_width=True):
            move_image('visual_heavy')
    
    with col3:
        if st.button("Formatting & Layouts", use_container_width=True):
            move_image('formatting_layouts')
    
    # Second row of buttons
    with col4:
        if st.button("Text + Visual Combo", use_container_width=True):
            move_image('text_visual_combo')
    
    with col5:
        if st.button("Exercises", use_container_width=True):
            move_image('exercises')
    
    # Display statistics in the sidebar
    st.sidebar.header("📊 Sorting Statistics")
    categories = {
        'text_heavy': 'Text Heavy',
        'visual_heavy': 'Visual Heavy',
        'formatting_layouts': 'Formatting & Layouts',
        'text_visual_combo': 'Text + Visual Combo',
        'exercises': 'Exercises'
    }
    
    for folder, display_name in categories.items():
        count = len(os.listdir(folder))
        st.sidebar.write(f"{display_name}: {count} images")

if __name__ == "__main__":
    main()