"""
Tests for face recognition functionality.
"""
import pytest
import cv2
import numpy as np
import os
from src.core.face_recognition import FaceRecognizer

@pytest.fixture
def face_recognizer():
    """Create a face recognizer instance for testing."""
    return FaceRecognizer()

def test_face_detection(face_recognizer):
    """Test that face detection works on a sample image."""
    # Create a dummy image with a face (white square)
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[30:70, 30:70] = 255  # White square representing a face
    
    faces = face_recognizer.detect_faces(img)
    assert len(faces) > 0, "Should detect at least one face"

def test_face_recognition_training(face_recognizer, tmp_path):
    """Test face recognition model training."""
    # Create dummy training data
    train_dir = tmp_path / "train"
    train_dir.mkdir()
    
    # Create dummy face image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[30:70, 30:70] = 255
    
    # Save dummy image
    img_path = train_dir / "person1"
    img_path.mkdir()
    cv2.imwrite(str(img_path / "1.jpg"), img)
    
    # Train model
    face_recognizer.train(str(train_dir))
    
    # Verify model was created
    assert face_recognizer.is_model_trained(), "Model should be trained"

def test_face_recognition(face_recognizer):
    """Test face recognition on a trained model."""
    # Skip if model is not trained
    if not face_recognizer.is_model_trained():
        pytest.skip("Model not trained")
    
    # Create test image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[30:70, 30:70] = 255
    
    # Test recognition
    result = face_recognizer.recognize(img)
    assert result is not None, "Should return recognition result" 