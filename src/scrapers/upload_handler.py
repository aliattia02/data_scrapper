"""
src/scrapers/upload_handler.py - Handle manual catalogue uploads
"""
import os
import shutil
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import img2pdf
from PIL import Image

from src.database.manager import DatabaseManager
from src.database.models import Catalogue, Store, Product
from src.ocr.processor import OCRProcessor
from pdf2image import convert_from_path


class UploadHandler:
    """Handle manual catalogue file uploads (images or PDFs)"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.ocr_processor = OCRProcessor()
        self.upload_dir = Path("data/flyers")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def process_upload(
        self,
        files: List[Any],
        store: str,
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process uploaded catalogue files
        
        Args:
            files: List of uploaded files (UploadFile objects)
            store: Store identifier (kazyon, carrefour, metro, etc.)
            valid_from: Offer start date (ISO format)
            valid_until: Offer end date (ISO format)
            
        Returns:
            Dict with processing results
        """
        # Determine file types
        file_paths = []
        file_types = []
        
        for file in files:
            # Save uploaded file temporarily
            filename = file.filename
            file_ext = os.path.splitext(filename)[1].lower()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_path = self.upload_dir / f"temp_{timestamp}_{filename}"
            
            # Save file
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_paths.append(temp_path)
            
            if file_ext == '.pdf':
                file_types.append('pdf')
            elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                file_types.append('image')
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Process based on file types
        if all(ft == 'pdf' for ft in file_types):
            # Single or multiple PDFs - merge if multiple
            pdf_path = self._handle_pdf_files(file_paths)
        elif all(ft == 'image' for ft in file_types):
            # Multiple images - merge to PDF
            pdf_path = self._merge_images_to_pdf(file_paths)
        else:
            # Mixed types - convert images to PDF first, then merge
            converted_paths = []
            for fpath, ftype in zip(file_paths, file_types):
                if ftype == 'image':
                    # Convert single image to PDF
                    single_pdf = self._merge_images_to_pdf([fpath])
                    converted_paths.append(single_pdf)
                else:
                    converted_paths.append(fpath)
            pdf_path = self._merge_pdfs(converted_paths)
        
        # Create catalogue record in database
        catalogue = self._create_catalogue_record(
            pdf_path, store, valid_from, valid_until
        )
        
        # Process with OCR
        products = self._process_with_ocr(pdf_path, catalogue.id)
        
        # Cleanup temp files
        for temp_file in file_paths:
            if temp_file.exists() and temp_file != pdf_path:
                temp_file.unlink()
        
        return {
            "status": "completed",
            "catalogue_id": catalogue.id,
            "pdf_path": str(pdf_path),
            "products_extracted": len(products),
            "pages_processed": catalogue.page_count
        }
    
    def _handle_pdf_files(self, pdf_paths: List[Path]) -> Path:
        """Handle PDF files - merge if multiple"""
        if len(pdf_paths) == 1:
            return pdf_paths[0]
        else:
            return self._merge_pdfs(pdf_paths)
    
    def _merge_pdfs(self, pdf_paths: List[Path]) -> Path:
        """Merge multiple PDFs into one using img2pdf"""
        # Convert each PDF to images first, then merge
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.upload_dir / f"merged_{timestamp}.pdf"
        
        all_images = []
        temp_image_files = []
        
        for pdf_path in pdf_paths:
            # Convert PDF to images
            images = convert_from_path(str(pdf_path), dpi=300)
            
            # Save images temporarily
            for idx, img in enumerate(images):
                temp_img = self.upload_dir / f"temp_merge_{timestamp}_{len(temp_image_files)}.png"
                img.save(temp_img)
                temp_image_files.append(temp_img)
                all_images.append(str(temp_img))
        
        # Merge all images into one PDF
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(all_images))
        
        # Clean up temp images
        for temp_file in temp_image_files:
            if temp_file.exists():
                temp_file.unlink()
        
        return output_path
    
    def _merge_images_to_pdf(self, image_paths: List[Path]) -> Path:
        """Merge multiple images into a single PDF"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.upload_dir / f"upload_{timestamp}.pdf"
        
        # Sort images by filename to maintain order
        image_paths = sorted(image_paths)
        
        # Convert images to RGB if needed (img2pdf requires RGB for JPEG)
        processed_images = []
        for img_path in image_paths:
            img = Image.open(img_path)
            # Convert to RGB if necessary
            if img.mode not in ['RGB', 'L']:
                img = img.convert('RGB')
            # Save as temporary file if conversion was needed
            if img.mode != Image.open(img_path).mode:
                temp_path = img_path.parent / f"converted_{img_path.name}"
                img.save(temp_path)
                processed_images.append(str(temp_path))
            else:
                processed_images.append(str(img_path))
        
        # Create PDF from images
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(processed_images))
        
        # Clean up converted temp files
        for proc_img in processed_images:
            proc_path = Path(proc_img)
            if proc_path.name.startswith("converted_") and proc_path.exists():
                proc_path.unlink()
        
        return output_path
    
    def _create_catalogue_record(
        self,
        pdf_path: Path,
        store: str,
        valid_from: Optional[str],
        valid_until: Optional[str]
    ) -> Catalogue:
        """Create catalogue record in database"""
        session = self.db_manager.get_session()
        
        try:
            # Get or create store
            store_obj = session.query(Store).filter(
                Store.store_id == store.lower()
            ).first()
            
            if not store_obj:
                # Create store if doesn't exist
                store_obj = Store(
                    store_id=store.lower(),
                    name_ar=store.capitalize(),
                    name_en=store.capitalize(),
                    active=True
                )
                session.add(store_obj)
                session.flush()
            
            # Parse dates
            valid_from_dt = None
            valid_until_dt = None
            if valid_from:
                try:
                    valid_from_dt = datetime.fromisoformat(valid_from.replace('Z', '+00:00'))
                except:
                    pass
            if valid_until:
                try:
                    valid_until_dt = datetime.fromisoformat(valid_until.replace('Z', '+00:00'))
                except:
                    pass
            
            # Count pages in PDF
            try:
                from pdf2image.pdf2image import pdfinfo_from_path
                info = pdfinfo_from_path(pdf_path)
                page_count = info.get("Pages", 0)
            except:
                page_count = 0
            
            # Create catalogue
            catalogue = Catalogue(
                store_id=store_obj.id,
                title_ar=f"كتالوج {store.capitalize()} - {datetime.now().strftime('%Y-%m-%d')}",
                title_en=f"{store.capitalize()} Catalogue - {datetime.now().strftime('%Y-%m-%d')}",
                valid_from=valid_from_dt,
                valid_until=valid_until_dt,
                status='uploaded',
                file_path=str(pdf_path),
                file_type='pdf',
                page_count=page_count,
                source_url='manual_upload'
            )
            
            session.add(catalogue)
            session.commit()
            session.refresh(catalogue)
            
            return catalogue
            
        finally:
            session.close()
    
    def _process_with_ocr(self, pdf_path: Path, catalogue_id: int) -> List[Product]:
        """Process PDF with OCR to extract products"""
        # Convert PDF to images
        images = convert_from_path(str(pdf_path), dpi=300)
        
        all_products = []
        session = self.db_manager.get_session()
        
        try:
            # Get catalogue
            catalogue = session.query(Catalogue).filter(
                Catalogue.id == catalogue_id
            ).first()
            
            if not catalogue:
                return []
            
            # Process each page
            for page_num, image in enumerate(images, start=1):
                # Save image temporarily
                temp_img_path = self.upload_dir / f"temp_page_{catalogue_id}_{page_num}.png"
                image.save(temp_img_path)
                
                try:
                    # Process with OCR
                    products = self.ocr_processor.process_flyer(str(temp_img_path))
                    all_products.extend(products)
                finally:
                    # Clean up temp image
                    if temp_img_path.exists():
                        temp_img_path.unlink()
            
            # Update catalogue status
            catalogue.status = 'completed'
            catalogue.ocr_processed = True
            catalogue.processed_at = datetime.utcnow()
            session.commit()
            
            return all_products
            
        except Exception as e:
            # Update catalogue status to failed
            catalogue = session.query(Catalogue).filter(
                Catalogue.id == catalogue_id
            ).first()
            if catalogue:
                catalogue.status = 'failed'
                session.commit()
            raise e
        finally:
            session.close()
