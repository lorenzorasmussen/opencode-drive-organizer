"""
Google Drive API Integration
"""

import os
import json
import mimetypes
from typing import Dict, List, Optional
from datetime import datetime


class GoogleDriveAPI:
    """
    Integration with Google Drive API

    Features:
    - List files and folders
    - Upload files
    - Download files
    - Delete files
    - Create folders
    - Search files
    - Get file information
    - Move files
    - Batch operations
    - Graceful handling without credentials
    """

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Drive API

        Args:
            credentials_path: Path to credentials file (optional)
        """
        self.credentials_path = credentials_path or os.path.join(
            os.path.expanduser("~"),
            ".config",
            "google-drive-organizer",
            "credentials.json",
        )
        self.service = None
        self.authenticated = False

        # Try to authenticate
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive API"""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.credentials_path):
                print("⚠️  No credentials found, API will be disabled")
                return

            # Import Google API libraries
            try:
                from google.oauth2.credentials import Credentials
                from google_auth_oauthlib.flow import InstalledAppFlow
                from google.auth.transport.requests import Request

                # Load credentials
                if os.path.exists("token.json"):
                    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save credentials
                with open("token.json", "w") as token:
                    token.write(creds.to_json())

                # Build service
                from googleapiclient.discovery import build

                self.service = build("drive", "v3", credentials=creds)
                self.authenticated = True
                print("✓ Google Drive API authenticated")

            except ImportError:
                print("⚠️  Google API libraries not installed, API will be disabled")
            except Exception as e:
                print(f"⚠️  Authentication failed: {e}")

        except Exception as e:
            print(f"⚠️  Error during authentication: {e}")

    def _check_authenticated(self) -> bool:
        """Check if API is authenticated"""
        if not self.authenticated or not self.service:
            print("⚠️  API not authenticated")
            return False
        return True

    def list_files(
        self, query: Optional[str] = None, page_size: int = 100
    ) -> Optional[List[Dict]]:
        """
        List files from Google Drive

        Args:
            query: Search query string
            page_size: Number of results per page

        Returns:
            List of file dicts or None if not authenticated
        """
        if not self._check_authenticated():
            return None

        try:
            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=page_size,
                    fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, parents)",
                )
                .execute()
            )

            return results.get("files", [])
        except Exception as e:
            print(f"⚠️  Error listing files: {e}")
            return None

    def upload_file(
        self,
        file_path: str,
        file_name: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Upload a file to Google Drive

        Args:
            file_path: Path to file to upload
            file_name: Custom file name (optional)
            folder_id: Parent folder ID (optional)

        Returns:
            File ID or None if failed
        """
        if not self._check_authenticated():
            return None

        try:
            file_metadata = {"name": file_name or os.path.basename(file_path)}

            if folder_id:
                file_metadata["parents"] = [folder_id]

            media = MediaFileUpload(
                file_path, mimetype=mimetypes.guess_type(file_path)[0]
            )

            result = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

            print(f"✓ Uploaded {file_metadata['name']} to Google Drive")
            return result.get("id")

        except ImportError:
            print("⚠️  MediaFileUpload not available")
            return None
        except Exception as e:
            print(f"⚠️  Error uploading file: {e}")
            return None

    def download_file(self, file_id: str, local_path: str) -> bool:
        """
        Download a file from Google Drive

        Args:
            file_id: Google Drive file ID
            local_path: Local path to save file

        Returns:
            True if successful, False otherwise
        """
        if not self._check_authenticated():
            return False

        try:
            # Get file metadata
            file_info = (
                self.service.files().get(fileId=file_id, fields="mimeType").execute()
            )

            # Download file
            request = self.service.files().get_media(fileId=file_id)

            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with open(local_path, "wb") as f:
                f.write(request.execute())

            print(f"✓ Downloaded file {file_id} to {local_path}")
            return True

        except Exception as e:
            print(f"⚠️  Error downloading file: {e}")
            return False

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive

        Args:
            file_id: Google Drive file ID

        Returns:
            True if successful, False otherwise
        """
        if not self._check_authenticated():
            return False

        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"✓ Deleted file {file_id}")
            return True
        except Exception as e:
            print(f"⚠️  Error deleting file: {e}")
            return False

    def create_folder(
        self, folder_name: str, parent_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a folder in Google Drive

        Args:
            folder_name: Name of folder to create
            parent_id: Parent folder ID (optional)

        Returns:
            Folder ID or None if failed
        """
        if not self._check_authenticated():
            return None

        try:
            folder_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }

            if parent_id:
                folder_metadata["parents"] = [parent_id]

            result = (
                self.service.files().create(body=folder_metadata, fields="id").execute()
            )

            print(f"✓ Created folder '{folder_name}'")
            return result.get("id")

        except Exception as e:
            print(f"⚠️  Error creating folder: {e}")
            return None

    def search_files(self, query: str, page_size: int = 100) -> Optional[List[Dict]]:
        """
        Search for files in Google Drive

        Args:
            query: Search query string
            page_size: Number of results per page

        Returns:
            List of file dicts or None if not authenticated
        """
        return self.list_files(query=query, page_size=page_size)

    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """
        Get information about a file

        Args:
            file_id: Google Drive file ID

        Returns:
            File info dict or None if failed
        """
        if not self._check_authenticated():
            return None

        try:
            result = (
                self.service.files()
                .get(
                    fileId=file_id,
                    fields="id, name, mimeType, size, modifiedTime, parents, owners",
                )
                .execute()
            )

            return result
        except Exception as e:
            print(f"⚠️  Error getting file info: {e}")
            return None

    def move_file(self, file_id: str, folder_id: str) -> bool:
        """
        Move a file to a different folder

        Args:
            file_id: Google Drive file ID
            folder_id: Target folder ID

        Returns:
            True if successful, False otherwise
        """
        if not self._check_authenticated():
            return False

        try:
            # Get current parents
            file = self.service.files().get(fileId=file_id, fields="parents").execute()

            # Update parents
            self.service.files().update(
                fileId=file_id,
                addParents=[folder_id],
                removeParents=file.get("parents", []),
                fields="id, parents",
            ).execute()

            print(f"✓ Moved file {file_id} to folder {folder_id}")
            return True

        except Exception as e:
            print(f"⚠️  Error moving file: {e}")
            return False

    def batch_delete(self, file_ids: List[str]) -> List[bool]:
        """
        Delete multiple files at once

        Args:
            file_ids: List of Google Drive file IDs

        Returns:
            List of success status for each file
        """
        results = []

        for file_id in file_ids:
            success = self.delete_file(file_id)
            results.append(success)

        return results

    def get_storage_usage(self) -> Optional[Dict]:
        """
        Get Google Drive storage usage

        Returns:
            Dict with storage info or None if not authenticated
        """
        if not self._check_authenticated():
            return None

        try:
            about = self.service.about().get(fields="storageQuota").execute()
            quota = about.get("storageQuota", {})

            return {
                "limit": quota.get("limit", 0),
                "usage": quota.get("usage", 0),
                "usage_in_drive": quota.get("usageInDrive", 0),
                "usage_percent": (quota.get("usage", 0) / quota.get("limit", 1)) * 100,
            }
        except Exception as e:
            print(f"⚠️  Error getting storage usage: {e}")
            return None
