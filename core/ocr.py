"""OCR text extraction using EasyOCR for high-quality results."""

import logging
from pathlib import Path
from typing import Optional, Union

import easyocr

from config import OCR_LANGUAGES, OCR_GPU

logger = logging.getLogger(__name__)

# Global reader instance (lazy loaded)
_reader: Optional[easyocr.Reader] = None


def get_ocr_reader() -> easyocr.Reader:
    """
    Get or create the OCR reader instance.
    Uses lazy loading to avoid startup delay.
    """
    global _reader
    
    if _reader is None:
        logger.info(f"Initializing OCR reader (languages: {OCR_LANGUAGES}, gpu: {OCR_GPU})")
        _reader = easyocr.Reader(
            OCR_LANGUAGES,
            gpu=OCR_GPU,
            verbose=False,
        )
    
    return _reader


def extract_text(
    image_source: Union[str, Path, bytes],
    detail: bool = False,
    paragraph: bool = True,
) -> Union[str, list]:
    """
    Extract text from an image using EasyOCR.
    
    Args:
        image_source: Path to image file or image bytes
        detail: If True, return detailed results with bounding boxes
        paragraph: If True, combine text into paragraphs
    
    Returns:
        Extracted text as string, or list of detailed results if detail=True
    """
    reader = get_ocr_reader()
    
    # Convert Path to string
    if isinstance(image_source, Path):
        image_source = str(image_source)
    
    try:
        # Perform OCR
        results = reader.readtext(
            image_source,
            detail=1,  # Always get detail for processing
            paragraph=paragraph,
        )
        
        if detail:
            # Return full results with bounding boxes and confidence
            return [
                {
                    "bbox": result[0],
                    "text": result[1],
                    "confidence": result[2],
                }
                for result in results
            ]
        
        # Return just the text, joined with newlines
        text_lines = [result[1] for result in results]
        extracted_text = "\n".join(text_lines)
        
        logger.debug(f"Extracted {len(text_lines)} text blocks ({len(extracted_text)} chars)")
        
        return extracted_text
    
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return "" if not detail else []


def extract_text_with_confidence(
    image_source: Union[str, Path, bytes],
    min_confidence: float = 0.5,
) -> tuple[str, float]:
    """
    Extract text and return average confidence score.
    
    Args:
        image_source: Path to image file or image bytes
        min_confidence: Minimum confidence threshold for text blocks
    
    Returns:
        Tuple of (extracted_text, average_confidence)
    """
    results = extract_text(image_source, detail=True)
    
    if not results:
        return "", 0.0
    
    # Filter by confidence and extract text
    filtered = [r for r in results if r["confidence"] >= min_confidence]
    
    if not filtered:
        return "", 0.0
    
    text = "\n".join(r["text"] for r in filtered)
    avg_confidence = sum(r["confidence"] for r in filtered) / len(filtered)
    
    return text, avg_confidence
