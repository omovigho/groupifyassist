"""
Helper functions to handle file exports
"""
from io import BytesIO
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Tuple
from app.utils.file_saver import save_export_file

def process_file_export(
    file_buffer: BytesIO,
    session_type: str,
    session_id: int,
    metadata: Dict[str, Any],
    file_extension: str,
    media_type: str,
    save_directory: str,
    host_info: Dict[str, Any]
) -> Tuple[StreamingResponse, str]:
    """
    Process a file export - saving to disk and returning streaming response
    
    Args:
        file_buffer: The BytesIO buffer containing the file data
        session_type: Type of session (group or selection)
        session_id: ID of the session
        metadata: Session metadata
        file_extension: File extension (xlsx or pdf)
        media_type: Content type for the response
        save_directory: Directory to save the file to
        host_info: Information about the host user
        
    Returns:
        Tuple of (StreamingResponse, filename)
    """
    # Copy the buffer for saving (since we'll use it for streaming too)
    save_buffer = BytesIO(file_buffer.getvalue())
    
    # Generate filename
    filename = f"{session_type}_session_{metadata['session_name'].replace(' ', '_')}_{session_id}.{file_extension}"
    
    # Save the file to disk
    save_export_file(
        buffer=save_buffer,
        session_type=session_type,
        session_id=session_id,
        session_name=metadata['session_name'],
        file_extension=file_extension,
        save_directory=save_directory,
        additional_info={
            "Host ID": host_info.get("id"),
            "Host Name": host_info.get("email"),
            "Export Type": file_extension.upper(),
            "Description": metadata.get('session_description', 'N/A')
        }
    )
    
    # Return streaming response
    return StreamingResponse(
        file_buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    ), filename
