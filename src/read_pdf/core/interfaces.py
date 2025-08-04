class PDFExtractorInterface(ABC):
    """Interface abstraite pour les extracteurs PDF"""
    
    @abstractmethod
    def extract(self, pdf_path: Union[str, Path], config: ExtractionConfig) -> ExtractionResult:
        """Extrait le contenu d'un PDF selon la configuration"""
        pass
    
    @abstractmethod
    def supports_document_type(self, doc_type: DocumentType) -> bool:
        """Vérifie si l'extracteur supporte un type de document"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Retourne le nom du provider"""
        pass
    
    @abstractmethod
    def estimate_quality(self, result: ExtractionResult) -> float:
        """Estime la qualité de l'extraction (0-1)"""
        pass
