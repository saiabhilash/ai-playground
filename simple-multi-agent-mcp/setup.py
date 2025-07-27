#!/usr/bin/env python3
"""
Setup script for Simple Multi-Agent System with MCP Server
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def setup_environment():
    """Setup the development environment"""
    print("🚀 Setting up Simple Multi-Agent System...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Get current directory
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    # Install dependencies
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Create .env file from example if it doesn't exist
    env_file = current_dir / ".env"
    env_example = current_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created")
        print("💡 You may want to edit .env with your specific configuration")
    
    # Run tool tests
    print("\n🧪 Running tool tests...")
    if not run_command(f"{sys.executable} test_tools.py", "Running tool tests"):
        print("⚠️  Tool tests failed, but continuing setup...")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 **Next Steps:**")
    print("  1. Review and edit .env file if needed")
    print("  2. Run demo: python demo.py")
    print("  3. Run interactive mode: python main.py")
    print("\n📚 **Available Commands:**")
    print("  • python test_tools.py  - Test MCP tools")
    print("  • python demo.py        - Run automated demo")
    print("  • python main.py        - Interactive chat mode")
    
    return True


def main():
    """Main setup function"""
    try:
        success = setup_environment()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
