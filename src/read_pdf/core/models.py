"""
Système d'extraction PDF modulaire avec providers interchangeables
Permet de changer d'extracteur selon le type de document et les besoins
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import pandas as pd
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Types de documents supportés"""
    SCIENTIFIC_PAPER = "scientific_paper"
    FINANCIAL_REPORT = "financial_report"
    INVOICE = "invoice"
    FORM = "form"
    MIXED_LAYOUT = "mixed_layout"
    SCANNED = "scanned"
    SIMPLE_TEXT = "simple_text"


class ExtractionQuality(Enum):
    """Niveaux de qualité d'extraction"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    FAILED = "failed"


@dataclass
class ExtractionResult:
    """Résultat d'une extraction PDF"""
    text: str = ""
    tables: List[pd.DataFrame] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    quality_level: ExtractionQuality = ExtractionQuality.FAILED
    extraction_time: float = 0.0
    provider_used: str = ""
    page_count: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class ExtractionConfig:
    """Configuration pour l'extraction PDF"""
    # Paramètres généraux
    extract_text: bool = True
    extract_tables: bool = True
    extract_images: bool = False
    preserve_layout: bool = True
    
    # Paramètres spécifiques aux tables
    table_detection_strategy: str = "auto"  # auto, lines, text
    table_accuracy_threshold: float = 0.8
    merge_similar_tables: bool = False
    
    # Paramètres de qualité
    min_text_length: int = 50
    min_table_rows: int = 2
    
    # Paramètres de performance
    timeout: int = 300  # secondes
    use_parallel: bool = False
    
    # Paramètres spécifiques par provider
    provider_params: Dict[str, Dict[str, Any]] = field(default_factory=dict)
