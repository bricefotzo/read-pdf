class PyMuPDFExtractor(PDFExtractorInterface):
    """Extracteur basé sur PyMuPDF - optimal pour performance"""
    
    def __init__(self):
        try:
            import pymupdf
            self.pymupdf = pymupdf
        except ImportError:
            raise ImportError("PyMuPDF not installed. Run: pip install PyMuPDF")
    
    def get_provider_name(self) -> str:
        return "pymupdf"
    
    def supports_document_type(self, doc_type: DocumentType) -> bool:
        # PyMuPDF bon pour tous types, excellent pour performance
        return True
    
    def extract(self, pdf_path: Union[str, Path], config: ExtractionConfig) -> ExtractionResult:
        import time
        start_time = time.time()
        result = ExtractionResult(provider_used=self.get_provider_name())
        
        try:
            doc = self.pymupdf.open(pdf_path)
            result.page_count = len(doc)
            
            # Extraction du texte
            if config.extract_text:
                text_parts = []
                for page in doc:
                    if config.preserve_layout:
                        text_parts.append(page.get_text("dict"))  # Préserve mise en page
                    else:
                        text_parts.append(page.get_text())
                
                if config.preserve_layout:
                    # Reconstruction du texte avec layout
                    result.text = self._reconstruct_layout_text(text_parts)
                else:
                    result.text = "\n".join(text_parts)
            
            # Extraction des tables (disponible depuis v1.23.0)
            if config.extract_tables:
                tables = []
                for page_num, page in enumerate(doc):
                    try:
                        page_tables = page.find_tables()
                        for table in page_tables:
                            df = table.to_pandas()
                            if len(df) >= config.min_table_rows:
                                df.attrs['page'] = page_num + 1
                                df.attrs['extraction_method'] = 'pymupdf'
                                tables.append(df)
                    except Exception as e:
                        result.errors.append(f"Table extraction failed on page {page_num + 1}: {str(e)}")
                
                result.tables = tables
            
            # Métadonnées
            result.metadata = doc.metadata or {}
            
            doc.close()
            
        except Exception as e:
            result.errors.append(f"PyMuPDF extraction failed: {str(e)}")
            logger.error(f"PyMuPDF extraction error: {e}")
        
        result.extraction_time = time.time() - start_time
        result.quality_score = self.estimate_quality(result)
        result.quality_level = self._get_quality_level(result.quality_score)
        
        return result
    
    def _reconstruct_layout_text(self, text_dicts: List[Dict]) -> str:
        """Reconstruit le texte en préservant la mise en page"""
        # Implémentation simplifiée - peut être améliorée
        text_parts = []
        for page_dict in text_dicts:
            if isinstance(page_dict, dict) and "blocks" in page_dict:
                for block in page_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            line_text = ""
                            for span in line["spans"]:
                                line_text += span["text"]
                            text_parts.append(line_text)
            else:
                text_parts.append(str(page_dict))
        return "\n".join(text_parts)
    
    def estimate_quality(self, result: ExtractionResult) -> float:
        score = 0.0
        
        # Score texte
        if result.text and len(result.text) > 50:
            score += 0.5
        
        # Score tables
        if result.tables:
            score += 0.3
            score += min(0.2, len(result.tables) * 0.05)
        
        return min(1.0, score)
    
    def _get_quality_level(self, score: float) -> ExtractionQuality:
        if score >= 0.7:
            return ExtractionQuality.HIGH
        elif score >= 0.4:
            return ExtractionQuality.MEDIUM
        elif score > 0:
            return ExtractionQuality.LOW
        return ExtractionQuality.FAILED

