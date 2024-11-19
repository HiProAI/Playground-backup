import requests
import json
import os
import re
import argparse
from datetime import datetime
from urllib.parse import quote, urlparse
from urllib.parse import urlparse as parse_url

class ImageFetcher:
    def __init__(self, user_id, output_dir="downloaded_data", only_png=False, only_jpeg=False, name_by_date=False):
        self.user_id = self.validate_user_id(user_id)
        self.output_dir = output_dir
        self.only_png = only_png
        self.only_jpeg = only_jpeg
        self.name_by_date = name_by_date
        self.base_url = "https://playground.com/api/images/user"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        
        # Create directories for downloaded images
        self.png_dir = os.path.join(output_dir, 'png')
        self.jpeg_dir = os.path.join(output_dir, 'jpeg')
        
        # Create base and image directories if they don't exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(self.png_dir, exist_ok=True)
        os.makedirs(self.jpeg_dir, exist_ok=True)

    def validate_user_id(self, user_id):
        # Check formats: direct userid or profile URL
        if user_id.startswith('http'):
            # Extract userid from URL
            parsed_url = urlparse(user_id)
            match = re.search(r'/profile/([a-zA-Z0-9]+)', parsed_url.path)
            if match:
                return match.group(1)
        
        # Regex to validate userid
        if re.match(r'^[a-zA-Z0-9]+$', user_id):
            return user_id
        
        raise ValueError("Invalid user ID format. Please provide a valid user ID or profile URL.")

    def get_url(self, cursor):
        date_filter = quote('{"start":null,"end":null}')
        params = {
            'limit': '250',
            'cursor': cursor,
            'userId': self.user_id,
            'id': self.user_id,
            'likedImages': 'false',
            'sortBy': 'Newest',
            'filter': 'All',
            'dateFilter': date_filter
        }
        
        # Form URL with parameters
        url = f"{self.base_url}?"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    def save_json(self, data, start_date, end_date):
        # Format dates for filename
        filename = f"{start_date.strftime('%Y-%m-%d-%H-%M')}-{end_date.strftime('%Y-%m-%d-%H-%M')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save data to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"Saved {len(data['images'])} image records to {filename}")

    def download_image(self, url, image_data):
        # Determine download parameters based on configuration
        if self.only_png and self.only_jpeg:
            print("Cannot use both --only-png and --only-jpeg. Choose one.")
            return False
        
        # Determine if this image should be downloaded
        if self.only_png and not url.endswith('.png'):
            return False
        if self.only_jpeg and not(url.endswith('.jpeg') or url.endswith('.jpg')):
            return False

        try:
            # Determine filename
            url_path = parse_url(url).path
            filename = os.path.basename(url_path)
            if self.name_by_date:
                # Use creation date for filename
                created_at = datetime.strptime(image_data['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                filename = created_at.strftime("%Y-%m-%d_%H-%M-%S")+"_"+filename

            # Determine directory based on file extension
            if url.endswith('.png'):
                save_dir = self.png_dir
            elif url.endswith('.jpeg') or url.endswith('.jpg'):
                save_dir = self.jpeg_dir
            else:
                print(f"Unsupported image format: {url}")
                return False

            # Full path for saving
            save_path = os.path.join(save_dir, filename)
            
            # Skip if file already exists
            if os.path.exists(save_path):
                return True

            # Download image
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Save image
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filename}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error downloading image {url}: {e}")
            return False

    def parse_date(self, date_string):
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")

    def fetch_all(self):
        cursor = 0
        total_images_processed = 0
        total_images_downloaded = 0
        
        while True:
            url = self.get_url(cursor)
            print(f"Fetching data from {total_images_processed + 1} to {total_images_processed + 250}")
            
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                if not data['images']:
                    print("No more image records found.")
                    break
                
                # Determine start and end dates
                start_date = self.parse_date(data['images'][-1]['createdAt'])
                end_date = self.parse_date(data['images'][0]['createdAt'])
                
                # Save JSON
                self.save_json(data, start_date, end_date)
                
                # Download images
                for image in data['images']:
                    # Try downloading both PNG and JPEG if they exist
                    if image.get('url'):
                        if self.download_image(image['url'], image):
                            total_images_downloaded += 1
                    
                    if image.get('url_jpeg'):
                        if self.download_image(image['url_jpeg'], image):
                            total_images_downloaded += 1
                
                total_images_processed += len(data['images'])
                
                # Update cursor for next request
                cursor = data['cursor']
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                break
                
        print(f"Finished processing image records.")
        print(f"Total processed: {total_images_processed}")
        print(f"Total downloaded: {total_images_downloaded}")

def main():
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="Fetch and download image records from Playground")
    parser.add_argument("user_id", help="User ID or profile URL to fetch images from")
    parser.add_argument("--output", default="downloaded_data", 
                        help="Output directory for downloaded data (default: downloaded_data)")
    parser.add_argument("--only-png", action="store_true",
                        help="Download only PNG images")
    parser.add_argument("--only-jpeg", action="store_true",
                        help="Download only JPEG images")
    parser.add_argument("--name-by-date", action="store_true",
                        help="Rename files to their creation date")
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Create and run fetcher
        fetcher = ImageFetcher(
            args.user_id, 
            args.output, 
            only_png=args.only_png, 
            only_jpeg=args.only_jpeg,
            name_by_date=args.name_by_date
        )
        fetcher.fetch_all()
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()