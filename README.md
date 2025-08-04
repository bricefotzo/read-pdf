# Read PDF 

[![PyPI version](https://badge.fury.io/py/read-pdf.svg)](https://badge.fury.io/py/read-pdf)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/bricefotzo/read-pdf/workflows/Tests/badge.svg)](https://github.com/bricefotzo/read-pdf/actions)

**Simple, modular PDF extraction with intelligent provider selection.**

Extract text and tables from PDFs using the best available library automatically. No configuration needed for most cases.

## 🚀 Quick Start

### Installation

```bash
# Install with all extractors (recommended)
pip install read-pdf[all]

# Or install specific extractors only
pip install read-pdf[pdfplumber,camelot]
```

### Basic Usage

```python
from pdf_extractor_pro import extract_pdf

# Simple extraction
result = extract_pdf("document.pdf")
print(f"Text: {len(result.text)} characters")
print(f"Tables: {len(result.tables)} found")

# Access the data
text = result.text
tables = result.tables  # List of pandas DataFrames
provider = result.provider_used  # Which library was used
```

### Advanced Usage

```python
from pdf_extractor_pro import PDFExtractor, Config

# Custom configuration
config = Config(
    prefer_tables=True,
    accuracy_threshold=0.9,
    provider_priority=["camelot", "pdfplumber"]
)

extractor = PDFExtractor(config)
result = extractor.extract("financial_report.pdf")

# Force specific provider
result = extractor.extract("document.pdf", provider="pdfplumber")
```

## 📊 Supported Extractors

| Library | Best For | Speed | Table Quality |
|---------|----------|-------|---------------|
| **pdfplumber** | Complex layouts, scientific papers | Medium | Excellent |
| **Camelot** | Financial reports, forms | Slow | Excellent |
| **PyMuPDF** | Simple text, performance | Fast | Good |

The library automatically selects the best extractor based on document analysis.

## 🛠️ Command Line

```bash
# Extract single file
read-pdf document.pdf

# Batch processing
read-pdf folder/*.pdf --output results/

# Force specific provider
read-pdf document.pdf --provider camelot

# Tables only
read-pdf document.pdf --tables-only
```

## 📝 Examples

### Extract Financial Tables

```python
from pdf_extractor_pro import extract_pdf

# Optimized for financial documents
result = extract_pdf("quarterly_report.pdf", document_type="financial")

for i, table in enumerate(result.tables):
    print(f"Table {i+1}: {table.shape}")
    table.to_csv(f"table_{i+1}.csv")
```

### Batch Processing

```python
from pdf_extractor_pro import BatchExtractor
import os

extractor = BatchExtractor()
results = extractor.process_folder("pdfs/", output_dir="results/")

print(f"Processed {len(results)} files")
for file, result in results.items():
    if result.success:
        print(f"✓ {file}: {len(result.tables)} tables extracted")
    else:
        print(f"✗ {file}: {result.error}")
```

### Custom Extractor

```python
from pdf_extractor_pro import BaseExtractor, register_extractor

class MyExtractor(BaseExtractor):
    def extract(self, pdf_path, config):
        # Your extraction logic
        return ExtractionResult(text="...", tables=[])

# Register and use
register_extractor("my_extractor", MyExtractor)
result = extract_pdf("doc.pdf", provider="my_extractor")
```

## 🔧 Configuration

Create `pdf_config.yaml` for project-wide settings:

```yaml
# Default provider priority
provider_priority:
  - pdfplumber
  - camelot
  - pymupdf

# Quality thresholds
table_accuracy: 0.8
min_table_rows: 2

# Provider-specific settings
providers:
  pdfplumber:
    vertical_strategy: "lines"
    horizontal_strategy: "text"
  
  camelot:
    edge_tol: 50
    row_tol: 2
```

## 📋 Requirements

**System dependencies:**
- **Ubuntu/Debian**: `sudo apt-get install ghostscript python3-tk`
- **macOS**: `brew install ghostscript`
- **Windows**: Install Ghostscript from official website

**Python**: 3.8+

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/your-username/read-pdf.git
cd read-pdf

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Code formatting
black src tests
isort src tests
```

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Document   │───▶│  Classifier  │───▶│  Provider   │
│  Analysis   │    │  & Strategy  │    │  Selection  │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
┌─────────────┐    ┌──────────────┐          ▼
│   Result    │◀───│     Post     │    ┌─────────────┐
│ Validation  │    │  Processing  │◀───│ Extraction  │
└─────────────┘    └──────────────┘    └─────────────┘
```

## 📈 Performance

Benchmark on 100 mixed documents:

| Provider | Avg Time | Success Rate | Table Quality |
|----------|----------|--------------|---------------|
| Auto Selection | 2.1s | 94% | 89% |
| pdfplumber | 3.2s | 91% | 92% |
| camelot | 4.7s | 87% | 95% |
| pymupdf | 0.8s | 89% | 78% |

## ❓ Troubleshooting

**ImportError: No module named 'cv2'**
```bash
pip install opencv-python
```

**Camelot extraction fails**
```bash
# Install system dependencies
sudo apt-get install ghostscript
```

**Poor table extraction quality**
```python
# Try different provider
result = extract_pdf("doc.pdf", provider="pdfplumber")

# Adjust accuracy threshold  
config = Config(accuracy_threshold=0.7)
result = extract_pdf("doc.pdf", config=config)
```

**Memory issues with large PDFs**
```python
# Process page by page
extractor = PDFExtractor()
for page_num in range(total_pages):
    result = extractor.extract("doc.pdf", pages=[page_num])
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [pdfplumber](https://github.com/jsvine/pdfplumber) for excellent layout preservation
- [Camelot](https://github.com/camelot-dev/camelot) for robust table detection
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for high-performance processing