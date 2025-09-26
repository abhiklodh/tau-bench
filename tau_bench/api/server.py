# Copyright Sierra

import os
import sys
import argparse
import uvicorn
from pathlib import Path


def create_server_parser() -> argparse.ArgumentParser:
    """Create argument parser for API server."""
    parser = argparse.ArgumentParser(
        description="Tau-Bench API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server with default settings
  tau-bench-server

  # Start server on specific host and port
  tau-bench-server --host 127.0.0.1 --port 8080

  # Start with custom log directory and debug logging
  tau-bench-server --log-dir /custom/path --log-level debug --reload

  # Production deployment
  tau-bench-server --host 0.0.0.0 --port 80 --workers 4
        """
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    
    parser.add_argument(
        "--log-dir",
        type=str,
        default="api_results",
        help="Directory to store API results (default: api_results)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level (default: info)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development (not for production)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    return parser


def main():
    """Main entry point for the API server."""
    parser = create_server_parser()
    args = parser.parse_args()
    
    # Set environment variables for the service
    os.environ["TAU_BENCH_LOG_DIR"] = args.log_dir
    
    # Create log directory if it doesn't exist
    Path(args.log_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Starting Tau-Bench API Server...")
    print(f"📁 Log directory: {args.log_dir}")
    print(f"🌐 Server will be available at: http://{args.host}:{args.port}")
    print(f"📚 API documentation: http://{args.host}:{args.port}/docs")
    print(f"🔍 Health check: http://{args.host}:{args.port}/health")
    
    try:
        # Run the server
        uvicorn.run(
            "tau_bench.api.app:app",
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,  # reload doesn't work with multiple workers
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()