from webpage_analyzer import WebpageAnalyzer
import json
from datetime import datetime

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} GB"

def demonstrate_analyzer(url):
    """Comprehensive demonstration of WebpageAnalyzer features"""
    print("\n" + "="*50)
    print(f"WebpageAnalyzer Demonstration - {datetime.now()}")
    print("="*50)

    # Initialize analyzer with 5 concurrent workers
    analyzer = WebpageAnalyzer(max_workers=5)
    
    # 1. Performance Analysis
    print("\n🚀 Running Performance Analysis...")
    performance = analyzer.analyze_performance(url)
    
    if performance:
        print("\nPerformance Metrics:")
        print(f"├── Load Time: {performance['load_time']} seconds")
        print(f"├── Page Size: {format_size(performance['page_size'])}")
        print(f"├── Time to First Byte: {performance['time_to_first_byte']} seconds")
        print("\nResource Counts:")
        print(f"├── Images: {performance['resources']['images']}")
        print(f"├── Scripts: {performance['resources']['scripts']}")
        print(f"├── Stylesheets: {performance['resources']['stylesheets']}")
        print(f"└── Total Resources: {performance['resources']['total_resources']}")
        
        print("\nCompression Info:")
        print(f"├── Gzip Enabled: {performance['compression']['gzip_enabled']}")
        print(f"├── Content Type: {performance['compression']['content_type']}")
        print(f"└── Cache Control: {performance['compression']['cache_control']}")

    # 2. Broken Link Analysis
    print("\n🔍 Checking for Broken Links...")
    links = analyzer.check_broken_links(url)
    
    if links:
        print("\nBroken Links Summary:")
        print(f"├── Internal Broken Links: {len(links['broken']['internal'])}")
        print(f"├── External Broken Links: {len(links['broken']['external'])}")
        print(f"├── Working Internal Links: {len(links['working']['internal'])}")
        print(f"└── Working External Links: {len(links['working']['external'])}")

        if links['broken']['internal'] or links['broken']['external']:
            print("\nDetailed Broken Links:")
            for category in ['internal', 'external']:
                if links['broken'][category]:
                    print(f"\n{category.title()} Broken Links:")
                    for link in links['broken'][category][:5]:  # Show first 5 links
                        print(f"└── {link}")
                    if len(links['broken'][category]) > 5:
                        print(f"    ... and {len(links['broken'][category]) - 5} more")

    # 3. Content Duplication Analysis
    print("\n🔄 Analyzing Content Duplication...")
    duplication = analyzer.check_content_duplication(url)
    
    if duplication:
        print("\nContent Duplication Results:")
        print(f"├── Total Paragraphs Analyzed: {duplication['total_paragraphs']}")
        print(f"└── Duplicate Content Blocks Found: {duplication['duplicate_count']}")

        if duplication['duplicates']:
            print("\nExample Duplicates:")
            for i, dup in enumerate(duplication['duplicates'][:3], 1):  # Show first 3 duplicates
                print(f"\nDuplicate Set {i}:")
                print(f"├── Original: {dup['original']}...")
                print(f"└── Duplicate: {dup['duplicate']}...")
            
            if len(duplication['duplicates']) > 3:
                print(f"\n... and {len(duplication['duplicates']) - 3} more duplicate sets")

    # Save detailed results to JSON
    results = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'performance': performance,
        'links': links,
        'duplication': duplication
    }
    
    filename = f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Detailed results saved to {filename}")
    print("\n" + "="*50)

if __name__ == "__main__":
    print("Welcome to WebpageAnalyzer Demonstration!")
    while True:
        url = input("\nEnter URL to analyze (or 'quit'/'q' to exit): ").strip()
        if url.lower() == 'quit' or url.lower() == 'q':
            break
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        try:
            demonstrate_analyzer(url)
        except Exception as e:
            print(f"Error analyzing {url}: {str(e)}")
            continue
        
        choice = input("\nWould you like to analyze another URL? (y/n): ").lower()
        if choice != 'y':
            break
    
    print("\nThank you for using WebpageAnalyzer!")