#!/usr/bin/env python3
"""
Fetches all git tags, finds the latest semver tag, increments the patch version,
and creates + pushes the new tag.
"""

import re
import subprocess
import sys


def run(cmd):
    """Run a shell command and return stdout."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()


def parse_version(tag):
    """Parse a version tag like 'v1.2.3' or '1.2.3' into (major, minor, patch)."""
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    if match:
        return tuple(map(int, match.groups()))
    return None


def main():
    # Fetch all tags from remote
    print("Fetching tags...")
    run("git fetch --tags")

    # Get all tags
    tags_output = run("git tag")
    if not tags_output:
        print("No tags found. Creating v0.0.1")
        new_tag = "v0.0.1"
    else:
        tags = tags_output.split("\n")

        # Filter and parse semver tags
        semver_tags = []
        for tag in tags:
            version = parse_version(tag)
            if version:
                semver_tags.append((version, tag))

        if not semver_tags:
            print("No semver tags found. Creating v0.0.1")
            new_tag = "v0.0.1"
        else:
            # Sort by version tuple and get the latest
            semver_tags.sort(key=lambda x: x[0], reverse=True)
            latest_version, latest_tag = semver_tags[0]

            # Increment patch version
            major, minor, patch = latest_version
            new_version = (major, minor, patch + 1)

            # Preserve 'v' prefix if original had it
            prefix = "v" if latest_tag.startswith("v") else ""
            new_tag = f"{prefix}{new_version[0]}.{new_version[1]}.{new_version[2]}"

            print(f"Latest tag: {latest_tag}")

    run(f"git tag {new_tag}")
    run(f"git push --tags")

    print(f"Successfully created and pushed {new_tag}")


if __name__ == "__main__":
    main()
