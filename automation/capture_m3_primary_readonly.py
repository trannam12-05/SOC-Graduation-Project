"""Capture real Primary console, read-only: no keys, VM lifecycle or disk writes."""
import argparse
import sys
import capture_m2_core_console as capture

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--label", default="primary-initial")
    args = parser.parse_args()
    needle = "n.get('name') == 'SOC-Core-L2'"
    assert capture.REMOTE.count(needle) == 1
    capture.REMOTE = capture.REMOTE.replace(needle, "n.get('name') == 'OPNsense-Primary'")
    sys.argv = [sys.argv[0], "--output-dir", args.output_dir, "--label", args.label]
    capture.main()
