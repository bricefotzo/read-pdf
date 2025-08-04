class PDFPlumberExtractor(PDFExtractorInterface):
    """Extracteur basé sur pdfplumber - optimal pour structures complexes"""
    
    def __init__(self):
        try:
            import pdfplumber
            self.pdfplumber = pdfplumber
        except ImportError:
            raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")
    
    def get_provider_name(self) -> str:
        return "pdfplumber"
    
    def supports_document_type(self, doc_type: DocumentType) -> bool:
        # pdfplumber excelle sur les documents complexes
        return doc_type in [
            DocumentType.SCIENTIFIC_PAPER,
            DocumentType.FINANCIAL_REPORT,
            DocumentType.FORM,
            DocumentType.MIXED_LAYOUT
        ]
    
    def extract(self, pdf_path: Union[str, Path], config: ExtractionConfig) -> ExtractionResult:
        import time
        start_time = time.time()
        result = ExtractionResult(provider_used=self.get_provider_name())
        
        try:
            # Paramètres spécifiques pdfplumber
            params = config.provider_params.get('pdfplumber', {})
            
            with self.pdfplumber.open(pdf_path) as pdf:
                result.page_count = len(pdf.pages)
                
                # Extraction du texte
                if config.extract_text:
                    text_parts = []
                    for page in pdf.pages:
                        if config.preserve_layout:
                            text_parts.append(page.extract_text(layout=True))
                        else:
                            text_parts.append(page.extract_text())
                    result.text = "\n".join(filter(None, text_parts))
                
                # Extraction des tables
                if config.extract_tables:
                    tables = []
                    for page_num, page in enumerate(pdf.pages):
                        # Configuration table adaptative
                        table_settings = {
                            "vertical_strategy": params.get("vertical_strategy", "lines"),
                            "horizontal_strategy": params.get("horizontal_strategy", "text"),
                            "intersection_tolerance": params.get("intersection_tolerance", 3),
                            "text_tolerance": params.get("text_tolerance", 3),
                        }
                        
                        page_tables = page.extract_tables(table_settings)
                        for table_data in page_tables:
                            if table_data and len(table_data) >= config.min_table_rows:
                                df = pd.DataFrame(table_data[1:], columns=table_data[0])
                                df.attrs['page'] = page_num + 1
                                tables.append(df)
                    
                    result.tables = tables
                
                # Métadonnées
                result.metadata = {
                    'creator': getattr(pdf.metadata, 'creator', ''),
                    'producer': getattr(pdf.metadata, 'producer', ''),
                    'creation_date': getattr(pdf.metadata, 'creation_date', None),
                }
                
        except Exception as e:
            result.errors.append(f"PDFPlumber extraction failed: {str(e)}")
            logger.error(f"PDFPlumber extraction error: {e}")
        
        result.extraction_time = time.time() - start_time
        result.quality_score = self.estimate_quality(result)
        result.quality_level = self._get_quality_level(result.quality_score)
        
        return result
    
    def estimate_quality(self, result: ExtractionResult) -> float:
        score = 0.0
        
        # Score basé sur le texte extrait
        if result.text and len(result.text) > 50:
            score += 0.4
            # Bonus pour cohérence du layout
            if '\n' in result.text and not result.text.count('\n') > len(result.text) * 0.1:
                score += 0.1
        
        # Score basé sur les tables
        if result.tables:
            score += 0.3
            # Bonus pour tables bien formées
            well_formed_tables = sum(1 for t in result.tables if len(t.columns) > 1 and len(t) > 1)
            score += min(0.2, well_formed_tables * 0.05)
        
        return min(1.0, score)
    
    def _get_quality_level(self, score: float) -> ExtractionQuality:
        if score >= 0.8:
            return ExtractionQuality.HIGH
        elif score >= 0.5:
            return ExtractionQuality.MEDIUM
        elif score > 0:
            return ExtractionQuality.LOW
        return ExtractionQuality.FAILED