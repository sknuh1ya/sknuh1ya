
import numpy as np
import cv2

from modules.image_quality import analyze_quality


def test_quality_returns_score():
    image = np.full(
        (800, 1200, 3),
        128,
        dtype=np.uint8,
    )

    result = analyze_quality(image)

    assert 0 <= result["score"] <= 100
    assert "issues" in result
