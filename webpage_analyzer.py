import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import hashlib
import concurrent.futures
from typing import Dict, List, Set
import logging
from datetime import datetime
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Suppress insecure request warnings
warnings.simplefilter('ignore', InsecureRequestWarning)

class WebpageAnalyzer:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.setup_logging()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'webpage_analyzer_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def fetch_page(self, url: str) -> tuple:
        """Fetch page content with timing"""
        try:
            start_time = time.time()
            response = requests.get(url, headers=self.headers, timeout=30)
            load_time = time.time() - start_time
            return response.text, response.headers, load_time
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None, None, 0

    def check_broken_links(self, url: str) -> Dict[str, List[str]]:
        """Check for broken links on the webpage"""
        broken_links = {"internal": [], "external": []}
        working_links = {"internal": [], "external": []}
        base_domain = urlparse(url).netloc

        try:
            content, _, _ = self.fetch_page(url)
            if not content:
                return broken_links

            soup = BeautifulSoup(content, 'html.parser')
            links = {a.get('href') for a in soup.find_all('a', href=True)}
            
            def check_link(link: str) -> tuple:
                if not link.startswith(('http://', 'https://')):
                    link = urljoin(url, link)
                try:
                    response = requests.head(link, headers=self.headers, timeout=10)
                    is_working = response.status_code < 400
                    is_internal = urlparse(link).netloc == base_domain
                    return link, is_working, is_internal
                except:
                    return link, False, urlparse(link).netloc == base_domain

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                results = list(executor.map(check_link, links))

            for link, is_working, is_internal in results:
                category = "internal" if is_internal else "external"
                if is_working:
                    working_links[category].append(link)
                else:
                    broken_links[category].append(link)

        except Exception as e:
            self.logger.error(f"Error checking links: {str(e)}")

        return {
            "broken": broken_links,
            "working": working_links
        }

    def analyze_performance(self, url: str) -> Dict:
        """Analyze webpage performance metrics"""
        try:
            content, headers, load_time = self.fetch_page(url)
            if not content:
                return {}

            soup = BeautifulSoup(content, 'html.parser')
            
            # Calculate page size and resource counts
            page_size = len(content)
            resources = {
                'images': len(soup.find_all('img')),
                'scripts': len(soup.find_all('script')),
                'stylesheets': len(soup.find_all('link', rel='stylesheet')),
                'total_resources': 0
            }
            resources['total_resources'] = sum(resources.values())

            # Analyze compression and caching
            compression = {
                'gzip_enabled': 'gzip' in headers.get('Content-Encoding', ''),
                'content_type': headers.get('Content-Type', ''),
                'cache_control': headers.get('Cache-Control', 'Not set')
            }

            return {
                'load_time': round(load_time, 3),
                'page_size': page_size,
                'resources': resources,
                'compression': compression,
                'time_to_first_byte': round(load_time * 0.2, 3),  # Estimated TTFB
            }

        except Exception as e:
            self.logger.error(f"Error in performance analysis: {str(e)}")
            return {}

    def check_content_duplication(self, url: str) -> Dict:
        """Check for duplicate content within the page"""
        try:
            content, _, _ = self.fetch_page(url)
            if not content:
                return {}

            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(['script', 'style']):
                script.decompose()

            # Extract text content
            paragraphs = soup.find_all(['p', 'div', 'section'])
            
            # Create content fingerprints
            content_hashes = {}
            duplicates = []

            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:  # Only check substantial content
                    content_hash = hashlib.md5(text.encode()).hexdigest()
                    if content_hash in content_hashes:
                        duplicates.append({
                            'original': content_hashes[content_hash][:100],
                            'duplicate': text[:100],
                            'length': len(text)
                        })
                    else:
                        content_hashes[content_hash] = text

            return {
                'total_paragraphs': len(paragraphs),
                'duplicate_count': len(duplicates),
                'duplicates': duplicates
            }

        except Exception as e:
            self.logger.error(f"Error in duplication check: {str(e)}")
            return {}

    def analyze_webpage(self, url: str) -> Dict:
        """Main function to analyze webpage"""
        try:
            print(f"\nAnalyzing {url}...")
            
            # Run all analyses
            performance = self.analyze_performance(url)
            links = self.check_broken_links(url)
            duplication = self.check_content_duplication(url)

            # Print summary
            print("\n=== Analysis Results ===")
            print(f"Load Time: {performance.get('load_time', 'N/A')} seconds")
            print(f"Page Size: {performance.get('page_size', 0) / 1024:.1f} KB")
            print(f"Broken Links: {len(links['broken']['internal']) + len(links['broken']['external'])}")
            print(f"Duplicate Content Blocks: {duplication.get('duplicate_count', 0)}")

            return {
                'performance': performance,
                'links': links,
                'duplication': duplication
            }

        except Exception as e:
            self.logger.error(f"Error in webpage analysis: {str(e)}")
            return {}

def main():
    try:
        analyzer = WebpageAnalyzer(max_workers=5)
        url = input("Enter the URL to analyze: ")
        results = analyzer.analyze_webpage(url)
        
        # Additional detailed results can be accessed through the results dictionary
        print("\nAnalysis complete! Check the log file for detailed results.")
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()