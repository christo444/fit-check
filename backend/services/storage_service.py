from supabase import create_client, Client
import os
from datetime import datetime
from typing import Dict, List, Optional


class StorageService:
    """
    Service for handling Supabase storage and database operations
    
    Handles:
    - Uploading images to Supabase Storage
    - Creating outfit records in database
    - Retrieving outfit data
    """

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not configured")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.bucket_name = "outfits"  # Must match your Supabase storage bucket name

    def upload_outfit_image(self, file_path: str, filename: str) -> Dict:
        """
        Upload image to Supabase Storage and create database record
        
        Args:
            file_path: Local path to the image file
            filename: Name to use for the stored file
            
        Returns:
            Dictionary with outfit_id and image_url
        """
        try:
            # Check if file already exists and remove it
            try:
                existing_files = self.client.storage.from_(self.bucket_name).list(path="")
                if any(f["name"] == filename for f in existing_files):
                    print(f"Removing existing file: {filename}")
                    self.client.storage.from_(self.bucket_name).remove([filename])
            except Exception as check_error:
                print(f"Could not check for existing file: {str(check_error)}")
                # Continue anyway - file might not exist

            # Upload file to Supabase Storage
            print(f"Uploading file to Supabase: {filename}")
            with open(file_path, "rb") as f:
                file_data = f.read()
                storage_response = self.client.storage.from_(self.bucket_name).upload(
                    path=filename,
                    file=file_data,
                    file_options={"content-type": "image/jpeg", "upsert": "true"},
                )
            
            print(f"Upload response: {storage_response}")

            # Get public URL for the uploaded file
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(filename)
            print(f"Public URL: {public_url}")

            # Create outfit record in database
            outfit_data = {
                "image_url": public_url,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            print(f"Creating database record...")
            db_response = self.client.table("outfits").insert(outfit_data).execute()

            if not db_response.data or len(db_response.data) == 0:
                raise Exception("Failed to create outfit record in database")

            outfit = db_response.data[0]
            print(f"Outfit created with ID: {outfit['id']}")

            return {
                "outfit_id": outfit["id"],
                "image_url": outfit["image_url"],
                "status": outfit["status"],
            }

        except Exception as e:
            print(f"Storage service error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def get_outfit_by_id(self, outfit_id: str) -> Optional[Dict]:
        """
        Retrieve outfit data by ID
        
        Args:
            outfit_id: UUID of the outfit
            
        Returns:
            Outfit data dictionary or None if not found
        """
        try:
            response = (
                self.client.table("outfits")
                .select("*")
                .eq("id", outfit_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None

        except Exception as e:
            print(f"Error fetching outfit: {str(e)}")
            raise

    def get_all_outfits(self, limit: int = 50) -> List[Dict]:
        """
        Retrieve all outfits (will add user filtering later)
        
        Args:
            limit: Maximum number of outfits to return
            
        Returns:
            List of outfit dictionaries
        """
        try:
            response = (
                self.client.table("outfits")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return response.data if response.data else []

        except Exception as e:
            print(f"Error fetching outfits: {str(e)}")
            raise

    def update_outfit_status(self, outfit_id: str, status: str) -> Dict:
        """
        Update the status of an outfit
        
        Args:
            outfit_id: UUID of the outfit
            status: New status (pending, processing, completed, failed)
            
        Returns:
            Updated outfit data
        """
        try:
            response = (
                self.client.table("outfits")
                .update({"status": status, "updated_at": datetime.utcnow().isoformat()})
                .eq("id", outfit_id)
                .execute()
            )

            return response.data[0] if response.data else None

        except Exception as e:
            print(f"Error updating outfit status: {str(e)}")
            raise
