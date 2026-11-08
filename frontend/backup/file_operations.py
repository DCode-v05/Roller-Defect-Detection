"""
File Operations Helper
Handles file discovery and size calculations
"""

import os
from pathlib import Path


class FileOperations:
    """Static methods for file operations."""
    
    @staticmethod
    def get_files_to_copy(src_path, selected_files):
        """
        Get list of files to copy based on source selection.
        
        Args:
            src_path: Source path (folder or file indicator)
            selected_files: List of selected files
            
        Returns:
            list: List of file paths to copy
        """
        files = []
        
        if selected_files:
            return selected_files
        
        if src_path and os.path.isdir(src_path):
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
            
            for root, dirs, filenames in os.walk(src_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    if Path(file_path).suffix.lower() in image_extensions:
                        files.append(file_path)
        
        return files
    
    @staticmethod
    def calculate_total_size(file_list):
        """
        Calculate total size of files to copy.
        
        Args:
            file_list: List of file paths
            
        Returns:
            int: Total size in bytes
        """
        total_size = 0
        for file_path in file_list:
            try:
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
            except Exception as e:
                print(f"Error getting size of {file_path}: {e}")
        
        return total_size
