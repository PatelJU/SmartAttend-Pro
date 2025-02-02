"""
Tests for face recognition functionality.
"""
import pytest
import cv2
import numpy as np
import os
from src.core.face_recognition import FaceRecognizer
from src.utils.paths import get_model_path, get_image_path

@pytest.fixture
def face_recognizer():
    """Create a face recognizer instance for testing."""
    return FaceRecognizer()

def test_face_recognizer_initialization(face_recognizer):
    """Test that face recognizer is initialized properly."""
    assert face_recognizer.face_cascade is not None, "Face cascade classifier should be initialized"
    assert face_recognizer.recognizer is not None, "Face recognizer should be initialized"
    assert not face_recognizer.is_model_trained(), "Model should not be trained initially"

def test_face_detection_with_no_faces(face_recognizer):
    """Test face detection with an image containing no faces."""
    # Create a blank image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    faces = face_recognizer.detect_faces(img)
    assert len(faces) == 0, "Should not detect any faces in a blank image"

def test_face_recognition_training_empty_dir(face_recognizer, tmp_path):
    """Test face recognition model training with empty directory."""
    # Create empty training directory
    train_dir = tmp_path / "train"
    train_dir.mkdir()
    
    # Train model with empty directory
    face_recognizer.train(str(train_dir))
    assert not face_recognizer.is_model_trained(), "Model should not be trained with empty directory"

def test_recognize_without_training(face_recognizer):
    """Test recognition without training the model."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    result = face_recognizer.recognize(img)
    assert result is None, "Should return None when model is not trained"

@pytest.mark.skip(reason="Requires real face images for training")
def test_face_recognition_training(face_recognizer, tmp_path):
    """Test face recognition model training.
    
    Note: This test is skipped by default as it requires real face images.
    To run this test, you need to:
    1. Create a directory structure like:
       train/
         person1/
           image1.jpg
           image2.jpg
         person2/
           image1.jpg
           image2.jpg
    2. Add real face images to these directories
    3. Remove the @pytest.mark.skip decorator
    """
    # Create dummy training data
    train_dir = tmp_path / "train"
    train_dir.mkdir()
    
    # In a real test, you would:
    # 1. Copy real face images to the train directory
    # 2. Train the model
    # 3. Assert that the model is trained
    # 4. Test recognition on a known face
    
    # For now, we skip this test
    assert True

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