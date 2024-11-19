# Playground-backup
# Image Fetcher

A Python script to download images from a specific platform using a user ID.

## Prerequisites

### Install Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify installation by opening a terminal/command prompt and running:
   ```
   python --version
   pip --version
   ```

### Install Dependencies
Open a terminal/command prompt and run:
```bash
pip install requests
```

## Usage

### Basic Usage
```bash
python image-fetcher.py [USER_ID]
```
Replace `[USER_ID]` with the target user's ID or profile URL.

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `USER_ID` | Required. User ID or full profile URL | `python image-fetcher.py cldm123456789abcdefjhig` |
| `--output` | Custom output directory | `python image-fetcher.py cldm123456789abcdefjhig --output my_images` |
| `--only-png` | Download only PNG images | `python image-fetcher.py cldm123456789abcdefjhig --only-png` |
| `--only-jpeg` | Download only JPEG images | `python image-fetcher.py cldm123456789abcdefjhig --only-jpeg` |
| `--name-by-date` | Rename files to creation date | `python image-fetcher.py cldm123456789abcdefjhig --name-by-date` |

### Examples

1. Download all images for a user:
   ```bash
   python image-fetcher.py cldm123456789abcdefjhig
   ```

2. Download only PNG images to a specific directory:
   ```bash
   python image-fetcher.py cldm123456789abcdefjhig --output ./playground_images --only-png
   ```

3. Download images with date-based filenames:
   ```bash
   python image-fetcher.py https://playground.com/profile/cldm123456789abcdefjhig --name-by-date
   ```

## Output Structure
- `downloaded_data/`: Default output directory
  - `png/`: PNG images
  - `jpeg/`: JPEG images
  - JSON files with image metadata

## Troubleshooting
- Ensure you have a stable internet connection
- Check that the user ID or profile URL is correct
- Verify you have write permissions in the output directory
- Check if you have enough harddisk space(up to 1.5 Gigabytes per 1000 images)

## Notes
- Script downloads only public images
- Large collections may take some time to download(up to several hours)
