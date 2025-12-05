# ESG Data Translator and Analyst

Names: MACE Ulysse, MORVAN Arthur

A Streamlit web application that translates ESG (Environmental, Social, and Governance) data from Chinese to English and provides AI-powered analysis using DeepSeek via Ollama.

## Overview

This project processes labeled ESG data, translating all columns (sentences, labels, and quality indicators) from Chinese to English. It then uses a local LLM (DeepSeek R1) to generate summaries and answer questions about the translated ESG statements.

## Features

- **Multi-column Translation**: Translates all columns in the dataset (sentences, label, quality) creating `translated_{column}` columns for each
- **AI-Powered Analysis**: Generates ESG-themed summaries using DeepSeek R1 model
- **Interactive Q&A**: Ask questions about the translated ESG data and get contextual answers
- **Caching**: Translation results are cached to avoid redundant API calls
- **Progress Tracking**: Real-time progress indicators during translation

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally
- DeepSeek R1 model available in Ollama

## Setup

1. **Install Ollama** (if not already installed):
   - Visit [https://ollama.ai](https://ollama.ai) and follow installation instructions
   - Pull the DeepSeek R1 model:
     ```bash
     ollama pull deepseek-r1:1.5b
     ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables** (optional):
   - `OLLAMA_HOST`: Default is `http://localhost:11434`
   - `OLLAMA_MODEL`: Default is `deepseek-r1:1.5b`

## Usage

1. **Start Ollama** (if not running as a service):
   ```bash
   ollama serve
   ```

2. **Run the Streamlit Application**:
   ```bash
   streamlit run app.py
   ```

3. **Use the Application**:
   - Adjust the number of rows to translate using the sidebar slider
   - Click "Translate & Analyze" to process the data
   - View translated data and AI-generated summaries
   - Ask questions about the ESG data in the Q&A section

## Data Format

The application expects a CSV file (`data/labeled_esg_data.csv`) with semicolon (`;`) delimiter containing:
- `sentences`: Main ESG-related text (in Chinese)
- `label`: Classification label (in Chinese)
- `quality`: Quality indicator (in Chinese)

After translation, the application creates:
- `translated_sentences`: English translation of sentences
- `translated_label`: English translation of label
- `translated_quality`: English translation of quality

## Project Structure

```
lab6/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── data/
    └── labeled_esg_data.csv  # ESG dataset (semicolon-delimited)
```

## Technologies Used

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and CSV processing
- **Ollama**: Local LLM API
- **DeepSeek R1**: Language model for translation and analysis

## Notes

- Translation is performed row-by-row and column-by-column, which may take time for large datasets
- Results are cached in the session state to improve performance
- The application processes up to 200 rows by default (configurable via slider)

