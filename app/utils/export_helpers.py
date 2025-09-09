"""
Helper functions to handle file exports (stream-only, no local storage)
"""
from io import BytesIO
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Tuple

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
    Process a file export and return a streaming response.
    Note: This no longer saves files to local storage; it only streams to the client.
    
    Args:
        file_buffer: The BytesIO buffer containing the file data
        session_type: Type of session (group or selection)
        session_id: ID of the session
        metadata: Session metadata
        file_extension: File extension (xlsx or pdf)
        media_type: Content type for the response
    save_directory: (Unused) Directory that was previously used for saving files
    host_info: (Unused) Information about the host user
        
    Returns:
        Tuple of (StreamingResponse, filename)
    """
    # Generate filename
    filename = f"{session_type}_session_{metadata['session_name'].replace(' ', '_')}_{session_id}.{file_extension}"

    # Return streaming response
    return StreamingResponse(
        file_buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    ), filename
