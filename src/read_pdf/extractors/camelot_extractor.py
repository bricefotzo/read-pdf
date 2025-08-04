class CamelotExtractor(PDFExtractorInterface):
    """Extracteur basé sur Camelot - spécialisé pour les tables"""
    
    def __init__(self):
        try:
            import camelot
            self.camelot = camelot
        except ImportError:
            raise ImportError("camelot-py not installed. Run: pip install camelot-py[cv]")
    
    def get_provider_name(self) -> str:
        return "camelot"
    
    def supports_document_type(self, doc_type: DocumentType) -> bool:
        # Camelot excellent pour documents avec beaucoup de tables
        return doc_type in [
            DocumentType.FINANCIAL_REPORT,
            DocumentType.INVOICE,
            DocumentType.FORM
        ]
    
    def extract(self, pdf_path: Union[str, Path], config: ExtractionConfig) -> ExtractionResult:
        import time
        start_time = time.time()
        result = ExtractionResult(provider_used=self.get_provider_name())
        
        try:
            # Paramètres spécifiques camelot
            params = config.provider_params.get('camelot', {})
            
            # Extraction avec algorithme Lattice (bordures)
            try:
                tables_lattice = self.camelot.read_pdf(
                    str(pdf_path), 
                    flavor='lattice',
                    **params
                )
                result.tables.extend([t.df for t in tables_lattice if t.parsing_report['accuracy'] > config.table_accuracy_threshold])
            except Exception as e:
                result.errors.append(f"Lattice extraction failed: {str(e)}")
            
            # Extraction avec algorithme Stream (pas de bordures)
            try:
                tables_stream = self.camelot.read_pdf(
                    str(pdf_path), 
                    flavor='stream',
                    **params
                )
                result.tables.extend([t.df for t in tables_stream if t.parsing_report['accuracy'] > config.table_accuracy_threshold])
            except Exception as e:
                result.errors.append(f"Stream extraction failed: {str(e)}")
            
            # Numérotation des pages pour les tables
            for i, table in enumerate(result.tables):
                table.attrs['extraction_method'] = 'camelot'
                table.attrs['table_id'] = i
            
            # Extraction texte basique (fallback vers pdfplumber si disponible)
            if config.extract_text:
                try:
                    import pdfplumber
                    with pdfplumber.open(pdf_path) as pdf:
                        result.text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                        result.page_count = len(pdf.pages)
                except ImportError:
                    result.errors.append("Text extraction requires pdfplumber")
            
        except Exception as e:
            result.errors.append(f"Camelot extraction failed: {str(e)}")
            logger.error(f"Camelot extraction error: {e}")
        
        result.extraction_time = time.time() - start_time
        result.quality_score = self.estimate_quality(result)
        result.quality_level = self._get_quality_level(result.quality_score)
        
        return result
    
    def estimate_quality(self, result: ExtractionResult) -> float:
        score = 0.0
        
        # Camelot se concentre sur les tables
        if result.tables:
            score += 0.6
            # Bonus pour nombre de tables trouvées
            score += min(0.3, len(result.tables) * 0.1)
            # Bonus pour tables bien structurées
            well_structured = sum(1 for t in result.tables if len(t.columns) > 2 and len(t) > 2)
            score += min(0.1, well_structured * 0.02)
        
        # Score texte (moindre importance)
        if result.text:
            score += 0.1
        
        return min(1.0, score)
    
    def _get_quality_level(self, score: float) -> ExtractionQuality:
        if score >= 0.7:
            return ExtractionQuality.HIGH
        elif score >= 0.4:
            return ExtractionQuality.MEDIUM
        elif score > 0:
            return ExtractionQuality.LOW
        return ExtractionQuality.FAILED

