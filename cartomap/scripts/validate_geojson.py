#!/usr/bin/env python3
"""Validate and optionally repair a GeoJSON file."""

import json
import sys
import argparse
from pathlib import Path


def check_winding(ring):
    """Return True if ring is counter-clockwise (positive area)."""
    area = sum(
        (ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1])
        for i in range(len(ring) - 1)
    )
    return area > 0


def fix_winding(ring, should_be_ccw=True):
    is_ccw = check_winding(ring)
    if is_ccw != should_be_ccw:
        return ring[::-1]
    return ring


def validate_feature(feature, index, fix=False):
    issues = []
    geom = feature.get("geometry")
    if geom is None:
        return issues, feature

    gtype = geom.get("type", "")
    coords = geom.get("coordinates", [])

    if gtype == "Polygon":
        rings = coords
        if not rings:
            issues.append(f"Feature {index}: empty Polygon coordinates")
            return issues, feature
        outer = rings[0]
        if outer[0] != outer[-1]:
            issues.append(f"Feature {index}: exterior ring not closed")
            if fix:
                outer.append(outer[0])
        if not check_winding(outer):
            issues.append(f"Feature {index}: exterior ring is clockwise (should be CCW)")
            if fix:
                rings[0] = fix_winding(outer, should_be_ccw=True)
        for hi, hole in enumerate(rings[1:], 1):
            if hole[0] != hole[-1]:
                issues.append(f"Feature {index}: hole {hi} not closed")
                if fix:
                    hole.append(hole[0])
            if check_winding(hole):
                issues.append(f"Feature {index}: hole {hi} is CCW (should be CW)")
                if fix:
                    rings[hi] = fix_winding(hole, should_be_ccw=False)

    elif gtype == "MultiPolygon":
        for pi, poly in enumerate(coords):
            for ri, ring in enumerate(poly):
                if ring[0] != ring[-1]:
                    issues.append(f"Feature {index}: polygon {pi} ring {ri} not closed")
                    if fix:
                        ring.append(ring[0])

    return issues, feature


def validate(path: Path, fix=False):
    data = json.loads(path.read_text())
    all_issues = []

    if data.get("type") == "FeatureCollection":
        features = data.get("features", [])
        ids = [f.get("id") for f in features if f.get("id") is not None]
        if len(ids) != len(set(ids)):
            all_issues.append("Duplicate feature IDs detected")
        for i, feat in enumerate(features):
            issues, fixed_feat = validate_feature(feat, i, fix=fix)
            all_issues.extend(issues)
            if fix:
                features[i] = fixed_feat
    elif data.get("type") == "Feature":
        issues, fixed = validate_feature(data, 0, fix=fix)
        all_issues.extend(issues)
        if fix:
            data = fixed
    else:
        all_issues.append(f"Unknown GeoJSON type: {data.get('type')}")

    if all_issues:
        for issue in all_issues:
            print(f"  ISSUE: {issue}")
    else:
        print("  OK: no issues found")

    if fix and all_issues:
        out = path.with_stem(path.stem + "_fixed")
        out.write_text(json.dumps(data, separators=(",", ":")))
        print(f"  Fixed file written to: {out}")

    return len(all_issues)


def main():
    parser = argparse.ArgumentParser(description="Validate (and optionally repair) a GeoJSON file")
    parser.add_argument("file", help="Path to GeoJSON file")
    parser.add_argument("--fix", action="store_true", help="Write repaired file with _fixed suffix")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"Validating {path} ...")
    count = validate(path, fix=args.fix)
    sys.exit(0 if count == 0 else 1)


if __name__ == "__main__":
    main()
