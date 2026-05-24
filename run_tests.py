import unittest
import sys

def main():
    print("==================================================")
    print("EIS AUTOMATION SENTINEL - Automated Health Suite")
    print("==================================================")
    
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n[SUCCESS] All core sentinel tests passed cleanly. 100% health.")
        sys.exit(0)
    else:
        print("\n[FAILURE] One or more sentinel tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
