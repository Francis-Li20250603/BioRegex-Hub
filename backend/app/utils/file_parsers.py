import pandas as pd
from pathlib import Path
import pyreadstat
from lxml import etree
from fastapi import UploadFile
import io
import magic
import logging

logger = logging.getLogger(__name__)

async def parse_file(file: UploadFile) -> pd.DataFrame:
    suffix = Path(file.filename).suffix.lower()
    file_content = await file.read()
    file_io = io.BytesIO(file_content)
    
    # Detect file type using magic numbers
    file_type = magic.from_buffer(file_content[:1024], mime=True)
    
    try:
        if 'sas' in file_type or suffix == '.sas7bdat':
            df, _ = pyreadstat.read_sas7bdat(file_io)
        elif 'csv' in file_type or suffix == '.csv':
            df = pd.read_csv(file_io)
        elif 'excel' in file_type or suffix in ['.xls', '.xlsx']:
            df = pd.read_excel(file_io)
        elif 'xml' in file_type or suffix == '.xml':
            # For SDTM XML
            tree = etree.parse(file_io)
            root = tree.getroot()
            
            # Extract data from XML - this is a simplified example
            # In reality, we would parse according to SDTM schema
            data = []
            for item in root.findall('.//ItemData'):
                record = {}
                for child in item:
                    record[child.tag] = child.text
                data.append(record)
            df = pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Basic data cleaning
        df = df.dropna(how='all', axis=1)  # Remove empty columns
        df = df.rename(columns=lambda x: x.strip().lower().replace(' ', '_'))
        
        return df
    except Exception as e:
        logger.error(f"Error parsing file: {str(e)}")
        raise ValueError(f"Failed to parse file: {file.filename} ({file_type})") from e
