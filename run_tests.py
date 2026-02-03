#!/usr/bin/env python3
# coding=utf-8
# Copyright (C) 2023-2026 Roy Pfund. All rights reserved.

"""Test runner for vanity-gateway unit tests"""

import sys
import pytest

if __name__ == "__main__":
    # Run all tests with verbose output and coverage
    args = [
        "tests/test_vanity_gateway.py",
        "tests/test_vg_io_rqs.py",
        "tests/test_vg_io_oai.py",
        "tests/test_vg_io_aws.py",
        "-v",
        "--tb=short",
    ]
    
    # Add any command line arguments passed to this script
    args.extend(sys.argv[1:])
    
    sys.exit(pytest.main(args))
