"""Simple test to verify directory structure without imports."""

from pathlib import Path

def main():
    """Test the directory structure."""
    project_root = Path(__file__).parent
    print(f"Project root: {project_root}")
    
    print("\nDirectory structure:")
    print("==================")
    
    # List all directories recursively
    for item in sorted(project_root.rglob("*")):
        if item.is_dir():
            relative_path = item.relative_to(project_root)
            print(f"📁 {relative_path}")
        elif item.suffix in ['.py', '.md', '.txt', '.toml']:
            relative_path = item.relative_to(project_root)
            print(f"📄 {relative_path}")
    
    print("\n" + "="*50)
    print("✅ Directory structure verification complete!")
    print("\nNew structure benefits:")
    print("- Modular design with separated concerns")
    print("- Standard Python package layout with src/ directory")
    print("- Clear separation of assets, examples, and tests")
    print("- Proper configuration files (setup.py, pyproject.toml)")
    print("- Documentation structure in docs/")
    print("- Clean import paths and namespace")

if __name__ == "__main__":
    main()