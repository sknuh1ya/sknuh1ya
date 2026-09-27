
import cv2


def analyze_quality(image) -> dict:
    if image is None:
        return {
            "score": 0,
            "issues": ["Corrupted or empty image."],
        }

    height, width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur_variance = cv2.Laplacian(
        gray,
        cv2.CV_64F,
    ).var()

    brightness = float(gray.mean())
    contrast = float(gray.std())

    score = 100
    issues = []

    if min(width, height) < 500:
        score -= 25
        issues.append("Low resolution detected.")

    if blur_variance < 60:
        score -= 35
        issues.append("Blurry image detected.")
    elif blur_variance < 120:
        score -= 15
        issues.append("Slight blur detected.")

    if brightness < 45 or brightness > 220:
        score -= 15
        issues.append("Brightness is outside the preferred range.")

    if contrast < 25:
        score -= 15
        issues.append("Low contrast detected.")

    score = max(0, min(100, score))

    return {
        "score": score,
        "issues": issues,
        "blur_variance": round(blur_variance, 2),
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
    }
