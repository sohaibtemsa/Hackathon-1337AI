import pandas as pd
import re
import json
import google.generativeai as genai
import cv2
import numpy as np
import pytesseract
import re
from PIL import Image
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import csv
import os

@dataclass
class CertificateInfo:
    """Data structure to hold extracted certificate information"""
    recipient_name: Optional[str] = None
    issuing_organization: Optional[str] = None
    additional_info: Dict[str, str] = None

    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}

class CertificateExtractor:
    def __init__(self, tesseract_path: str = None, languages: str = 'eng+fra+ara'):
        """
        Initialize the certificate extractor

        Args:
            tesseract_path: Path to tesseract executable (if not in PATH)
            languages: Languages for OCR (default: English + French + Arabic)
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        self.languages = languages

        # Focused patterns for student name and organization only
        self.patterns = {
            'names': [
                # French patterns for student name
                r'Le Doyen atteste que l\'étudiant[e]?\s*:\s*([A-Z\s]+?)(?:\n|Numéro)',
                r'étudiant[e]?\s*:\s*([A-Z\s]{5,40}?)(?:\n|Numéro)',
                r'que l\'étudiant[e]?\s*:\s*([A-Z\s]+?)(?:\n|\s*Numéro)',
                # English patterns
                r'(?:This is to certify that|Presented to|Awarded to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'(?:Name|Recipient)\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            ],
            'organizations': [
                # Specific patterns for this document
                r'(ROYAUME DU MAROC)',
                r'(Université Mohammed V de Rabat)',
                r'Faculté des ([A-Za-z\s]+)',
                # General patterns
                r'(?:Issued by|From|Authorized by)\s+([A-Z][A-Za-z\s&,\.]+?)(?:\n|$)',
                r'(?:University|Institute|Academy|School|College)\s+(?:of\s+)?([A-Za-z\s&,\.]+?)(?:\n|$)'
            ]
        }

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess the image for better OCR results

        Args:
            image_path: Path to the certificate image

        Returns:
            Preprocessed image as numpy array
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)

        # Resize image if it's too small (improves OCR accuracy)
        height, width = cleaned.shape
        if height < 600 or width < 800:
            scale_factor = max(800/width, 600/height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            cleaned = cv2.resize(cleaned, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        return cleaned

    def extract_raw_text(self, image: np.ndarray) -> str:
        """
        Extract raw text from image

        Args:
            image: Preprocessed image

        Returns:
            Raw extracted text
        """
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, lang=self.languages, config=custom_config)
        return text.strip()

    def find_pattern_matches(self, text: str, pattern_type: str) -> List[str]:
        """
        Find matches for specific pattern types

        Args:
            text: Text to search in
            pattern_type: Type of pattern to search for

        Returns:
            List of matches
        """
        matches = []
        if pattern_type in self.patterns:
            for pattern in self.patterns[pattern_type]:
                found = re.findall(pattern, text, re.IGNORECASE)
                matches.extend(found)
        return matches

    def extract_student_name(self, text: str) -> Optional[str]:
        """
        Extract student name with multiple pattern attempts

        Args:
            text: Raw extracted text

        Returns:
            Student name if found
        """
        # Try specific French patterns first
        student_patterns = [
            r'Le Doyen atteste que l\'étudiant[e]?\s*:\s*([A-Z\s]+?)(?:\n|Numéro)',
            r'étudiant[e]?\s*:\s*([A-Z\s]{5,40}?)(?:\n|Numéro)',
            r'que l\'étudiant[e]?\s*:\s*([A-Z\s]+?)(?:\n|\s*Numéro)'
        ]

        for pattern in student_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                name = match.group(1).strip()
                if len(name) > 3:  # Valid name should be longer than 3 chars
                    return name

        # Fallback to generic patterns
        names = self.find_pattern_matches(text, 'names')
        if names:
            return names[0].strip()

        return None

    def extract_organization(self, text: str) -> Optional[str]:
        """
        Extract organization name

        Args:
            text: Raw extracted text

        Returns:
            Organization name if found
        """
        # Check for specific university first
        if 'Université Mohammed V de Rabat' in text or 'Mohammed V' in text:
            return 'Université Mohammed V de Rabat'

        # Try other patterns
        orgs = self.find_pattern_matches(text, 'organizations')
        if orgs:
            return orgs[0].strip()

        return None

    def extract_certificate_info(self, image_path: str) -> CertificateInfo:
        """
        Main method to extract certificate information (student name and organization only)

        Args:
            image_path: Path to certificate image

        Returns:
            CertificateInfo object with extracted data
        """
        # Preprocess image
        processed_image = self.preprocess_image(image_path)

        # Extract text
        raw_text = self.extract_raw_text(processed_image)

        # Initialize certificate info
        cert_info = CertificateInfo()

        # Extract student name
        cert_info.recipient_name = self.extract_student_name(raw_text)

        # Extract organization
        cert_info.issuing_organization = self.extract_organization(raw_text)

        # Store raw text for debugging if needed
        cert_info.additional_info['raw_text'] = raw_text

        return cert_info

    def save_extracted_info(self, cert_info: CertificateInfo, output_path: str = "extracted_certificates.csv"):
        """
        Save extracted information to CSV file

        Args:
            cert_info: Certificate information object
            output_path: Path to save CSV file
        """
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.exists(output_path)

        # Prepare data row
        data_row = {
            'student_name': cert_info.recipient_name,
            'organization': cert_info.issuing_organization,
            'extraction_date': datetime.now().strftime('%Y-%m-%d'),
            'extraction_time': datetime.now().strftime('%H:%M:%S')
        }

        # Write to CSV file
        with open(output_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['student_name', 'organization', 'extraction_date', 'extraction_time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header if file is new
            if not file_exists:
                writer.writeheader()

            # Write data row
            writer.writerow(data_row)

def ocr_certid(certif):
    """Example usage of the certificate extractor"""

    # Initialize extractor with French and Arabic language support
    # If tesseract is not in PATH, specify the path:
    # extractor = CertificateExtractor(tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    extractor = CertificateExtractor(languages='eng+fra+ara')

    # Example usage
    try:
        # Extract information from certificate
        image_path = certif  # Replace with your image path
        cert_info = extractor.extract_certificate_info(image_path)

        # Print extracted information
        print("=== Extracted Certificate Information ===")
        print(f"Student Name: {cert_info.recipient_name}")
        print(f"Organization: {cert_info.issuing_organization}")

        # Save to CSV file
        extractor.save_extracted_info(cert_info, "extracted_certificates.csv")
        print("\nInformation saved to extracted_certificates.csv")

    except Exception as e:
        print(f"Error processing certificate: {str(e)}")