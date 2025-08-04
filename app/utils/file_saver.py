import os
import shutil
from pathlib import Path
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, Optional

def save_export_file(
    buffer: BytesIO,
    session_type: str,
    session_id: int,
    session_name: str,
    file_extension: str,
    save_directory: str,
    additional_info: Optional[Dict[str, Any]] = None
) -> str:
    """
    Save an export file to disk with detailed logging
    
    Args:
        buffer: BytesIO buffer containing the file data
        session_type: Type of session ('group' or 'selection')
        session_id: Session ID
        session_name: Name of the session
        file_extension: File extension (e.g., 'xlsx', 'pdf')
        save_directory: Directory to save the file to
        additional_info: Additional information to include in the info file
        
    Returns:
        Path to the saved file
    """
    try:
        # Create directory if it doesn't exist
        Path(save_directory).mkdir(parents=True, exist_ok=True)
        
        # Generate safe filename
        session_name_safe = session_name.replace(" ", "_").replace("/", "_")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{session_type}_session_{session_name_safe}_{session_id}_{timestamp}.{file_extension}"
        filepath = os.path.join(save_directory, filename)
        
        # Save the file
        buffer.seek(0)
        with open(filepath, 'wb') as file:
            file.write(buffer.getvalue())
        
        # Create an info file with details
        info_filepath = f"{filepath}.info.txt"
        with open(info_filepath, 'w') as info_file:
            info_file.write(f"Export Details:\n")
            info_file.write(f"---------------\n")
            info_file.write(f"File: {filename}\n")
            info_file.write(f"Session Type: {session_type}\n")
            info_file.write(f"Session ID: {session_id}\n")
            info_file.write(f"Session Name: {session_name}\n")
            info_file.write(f"Export Time: {datetime.now()}\n")
            info_file.write(f"File Location: {filepath}\n")
            
            if additional_info:
                info_file.write(f"\nAdditional Information:\n")
                info_file.write(f"-----------------------\n")
                for key, value in additional_info.items():
                    info_file.write(f"{key}: {value}\n")
        
        # Also create a central log
        log_path = os.path.join(save_directory, "export_log.txt")
        with open(log_path, 'a') as log:
            log.write(f"{datetime.now()}: {session_type.upper()} {file_extension.upper()} export - {filepath}\n")
        
        print(f"SUCCESS: {file_extension.upper()} file for {session_type} session saved to: {filepath}")
        return filepath
        
    except Exception as e:
        error_message = f"ERROR: Failed to save {file_extension} file: {str(e)}"
        print(error_message)
        
        # Try to write to error log
        try:
            error_log_path = os.path.join(save_directory, "export_errors.txt")
            with open(error_log_path, 'a') as error_log:
                error_log.write(f"{datetime.now()}: {error_message}\n")
        except:
            pass
        
        return None
