#!/usr/bin/env python3.11
"""
Manus Automation Runner
This script is designed to be called from a Manus scheduled task
It has access to all Manus tools (search, browser, etc.)
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '/home/ubuntu')

# Import the main automation
from manus_automation import ManusAutomation


def main():
    """
    Main entry point for scheduled execution
    This runs in a Manus context with full tool access
    """
    
    print("="*60)
    print("🤖 Manus Content Pipeline Automation")
    print("="*60)
    
    # Create and run automation
    automation = ManusAutomation()
    
    try:
        # Authenticate with Google
        automation.authenticate()
        
        # Process the queue
        automation.process_queue()
        
        print("\n✅ Automation cycle complete")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(0)
        
    except Exception as error:
        print(f"\n❌ Fatal error: {error}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
