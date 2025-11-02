#!/usr/bin/env python3
"""
ArXiv Research Assistant - Main Entry Point

This script provides a unified interface for running the ArXiv Research Assistant
in different modes: web server, CLI tool, or data processing pipeline.
"""

import os
import sys
import argparse
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import config


def run_web_server(host="127.0.0.1", port=8000, debug=False):
    """Run the Django web server"""
    print(f"🌐 Starting ArXiv Research Assistant Web Server")
    print(f"📍 Server: http://{host}:{port}")
    print(f"🔧 Debug: {debug}")
    print("=" * 50)
    
    os.chdir("llm-integration/llmproject")
    
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llmproject.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Run Django management command
    args = ['manage.py', 'runserver', f'{host}:{port}']
    if not debug:
        args.append('--settings=llmproject.settings')
    
    execute_from_command_line(args)


def run_cli_search(query, search_type="text", k=5, image_path=None):
    """Run CLI-based search"""
    from search.search_engine import ArxivSearchEngine
    
    print(f"🔍 ArXiv Research Assistant - CLI Search")
    print(f"Query: {query}")
    print(f"Type: {search_type}")
    print(f"Results: {k}")
    print("=" * 50)
    
    engine = ArxivSearchEngine()
    
    if search_type == "text":
        results = engine.search_by_text(query, k)
    elif search_type == "image" and image_path:
        results = engine.search_by_image(image_path, k)
    else:
        print("❌ Invalid search type or missing image path")
        return
    
    if not results:
        print("📭 No results found")
        return
    
    print(f"📊 Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"🔹 Result {i}:")
        print(f"   Title: {result.get('title', 'Unknown')}")
        print(f"   Paper ID: {result['paper_id']}")
        print(f"   Section: {result['section_name']}")
        print(f"   Similarity: {result['similarity_score']:.3f}")
        print(f"   Content: {result['content'][:200]}...")
        print()


def build_index(input_file, output_dir="data"):
    """Build FAISS index from embeddings file"""
    from storage.faiss_manager import build_index_from_json
    
    print(f"🏗️  Building FAISS Index")
    print(f"Input: {input_file}")
    print(f"Output: {output_dir}")
    print("=" * 50)
    
    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        return
    
    try:
        manager = build_index_from_json(input_file, output_dir)
        print(f"✅ Index built successfully!")
        print(f"📊 Total vectors: {manager.index.ntotal}")
    except Exception as e:
        print(f"❌ Error building index: {e}")


def process_papers(input_file, output_file):
    """Process papers from JSON to embeddings"""
    from vectorization.processor import process_json
    
    print(f"🔄 Processing Papers")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print("=" * 50)
    
    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        return
    
    try:
        process_json(input_file, output_file)
        print(f"✅ Papers processed successfully!")
    except Exception as e:
        print(f"❌ Error processing papers: {e}")


def validate_config():
    """Validate system configuration"""
    print("🔧 ArXiv Research Assistant - Configuration Validation")
    print("=" * 50)
    
    validation = config.validate_config()
    
    if validation['valid']:
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration issues found:")
        for issue in validation['issues']:
            print(f"   - {issue}")
    
    print("\n📊 Configuration Summary:")
    for key, value in validation['config_summary'].items():
        print(f"   {key}: {value}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ArXiv Research Assistant - AI-Powered Paper Discovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start web server
  python app.py web --host 0.0.0.0 --port 8000

  # Search via CLI
  python app.py search "machine learning" --type text --results 5
  python app.py search "neural networks" --type image --image path/to/image.jpg

  # Build search index
  python app.py build-index --input data/embeddings.json --output data/

  # Process papers
  python app.py process --input papers.json --output embeddings.json

  # Validate configuration
  python app.py validate-config
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Web server command
    web_parser = subparsers.add_parser('web', help='Start web server')
    web_parser.add_argument('--host', default='127.0.0.1', help='Host address')
    web_parser.add_argument('--port', type=int, default=8000, help='Port number')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search papers via CLI')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--type', choices=['text', 'image'], default='text', help='Search type')
    search_parser.add_argument('--image', help='Image path for image search')
    search_parser.add_argument('--results', '-k', type=int, default=5, help='Number of results')
    
    # Build index command
    build_parser = subparsers.add_parser('build-index', help='Build FAISS index')
    build_parser.add_argument('--input', '-i', required=True, help='Input embeddings JSON file')
    build_parser.add_argument('--output', '-o', default='data', help='Output directory')
    
    # Process papers command
    process_parser = subparsers.add_parser('process', help='Process papers to embeddings')
    process_parser.add_argument('--input', '-i', required=True, help='Input papers JSON file')
    process_parser.add_argument('--output', '-o', required=True, help='Output embeddings JSON file')
    
    # Validate config command
    subparsers.add_parser('validate-config', help='Validate configuration')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    try:
        if args.command == 'web':
            run_web_server(args.host, args.port, args.debug)
        elif args.command == 'search':
            run_cli_search(args.query, args.type, args.results, args.image)
        elif args.command == 'build-index':
            build_index(args.input, args.output)
        elif args.command == 'process':
            process_papers(args.input, args.output)
        elif args.command == 'validate-config':
            validate_config()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if config.DEV_MODE:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()