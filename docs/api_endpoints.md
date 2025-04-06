# API Endpoints Documentation

## 1. LSTM Music Generation Endpoints

### 1.1 Generate Music (LSTM v1)
- **Endpoint**: `/api/v1/lstm/generate`
- **Method**: POST
- **Description**: Generates melody using LSTM model with Context Bridging and Transposition Post-Processing
- **Request Body**:
```json
{
    "start_notes": [
        {
            "pitch": 60.0,
            "step": 1.0,
            "duration": 1.0
        }
    ],
    "num_predictions": 100,
    "temperature": 1.0,
    "tempo": 120
}
```
- **Response**: Returns generated MIDI file name

### 1.2 Generate Music (LSTM v2)
- **Endpoint**: `/api/v2/lstm/generate` 
- **Method**: POST
- **Description**: Enhanced melody generation with categorical duration prediction
- **Request Body**: Same as v1
- **Response**: Returns generated MIDI file name

## 2. FFN Harmonization Endpoint

### 2.1 Harmonize Melody
- **Endpoint**: `/api/ffn/harmonize/{filename}`
- **Method**: GET
- **Description**: Adds harmonic accompaniment to uploaded MIDI file
- **Parameters**: 
  - filename: Name of uploaded MIDI file
- **Response**: Returns harmonized MIDI file name

## 3. File Management Endpoints

### 3.1 Upload MIDI
- **Endpoint**: `/api/upload_midi`
- **Method**: POST
- **Description**: Uploads MIDI file for processing
- **Request**: multipart/form-data with file
- **Response**: Upload confirmation with filename

### 3.2 Download Generated File
- **Endpoint**: `/api/download/{filename}`
- **Method**: GET
- **Description**: Downloads and removes generated MIDI file
- **Parameters**:
  - filename: Name of generated file
- **Response**: MIDI file download

### 3.3 Preview Generated File
- **Endpoint**: `/api/preview/{filename}`
- **Method**: GET
- **Description**: Downloads generated MIDI file without removing it
- **Parameters**:
  - filename: Name of generated file
- **Response**: MIDI file download

## Implementation Details

Each endpoint is implemented using FastAPI framework with specific features:

1. **Error Handling**: All endpoints include proper error handling and validation
2. **Async Support**: Implemented using async/await for better performance
3. **File Management**: Automatic cleanup of old generated files
4. **CORS Support**: Configured for frontend integration
5. **Logging**: Comprehensive logging for debugging and monitoring

## Security Considerations

1. File validation for MIDI uploads
2. Temporary file cleanup
3. CORS policy configuration
4. Rate limiting (recommended for production)
