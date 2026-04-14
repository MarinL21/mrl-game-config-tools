#!/usr/bin/env python3
"""
Detect frontend framework in a project.

Usage:
    python scripts/detect_frontend.py [--path <project_path>]

Examples:
    python scripts/detect_frontend.py
    python scripts/detect_frontend.py --path /path/to/project
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, List


# Frontend framework detection patterns
FRONTEND_PATTERNS = {
    "react": {
        "files": ["package.json", "src/App.jsx", "src/App.tsx", "src/index.jsx", "src/index.tsx"],
        "keywords": ["react", "react-dom", "react-router"],
        "config_files": ["vite.config.ts", "vite.config.js", "webpack.config.js", "craco.config.js"]
    },
    "vue": {
        "files": ["package.json", "src/main.js", "src/main.ts", "src/App.vue", "vue.config.js"],
        "keywords": ["vue", "vue-router", "@vue"],
        "config_files": ["vite.config.ts", "vite.config.js", "vue.config.js"]
    },
    "angular": {
        "files": ["package.json", "angular.json", "src/app/app.component.ts"],
        "keywords": ["@angular/core", "@angular/common"],
        "config_files": ["angular.json", "tsconfig.json"]
    },
    "svelte": {
        "files": ["package.json", "svelte.config.js", "src/App.svelte"],
        "keywords": ["svelte", "sveltekit"],
        "config_files": ["svelte.config.js", "vite.config.js"]
    },
    "html": {
        "files": ["index.html", "*.html"],
        "keywords": [],
        "config_files": []
    }
}


def find_files_in_path(path: Path, patterns: List[str]) -> List[Path]:
    """Find files matching patterns in the given path."""
    found_files = []
    for pattern in patterns:
        # Handle wildcard patterns
        if "*" in pattern:
            found_files.extend(path.rglob(pattern))
        else:
            file_path = path / pattern
            if file_path.exists():
                found_files.append(file_path)
    return found_files


def check_keywords_in_file(file_path: Path, keywords: List[str]) -> bool:
    """Check if any keyword exists in the file."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
        return any(keyword.lower() in content for keyword in keywords)
    except Exception:
        return False


def check_package_json(project_path: Path, keywords: List[str]) -> bool:
    """Check package.json for keywords."""
    package_json = project_path / "package.json"
    if package_json.exists():
        try:
            import json
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                return any(keyword.lower() in k.lower() for keyword in keywords for k in deps.keys())
        except Exception:
            return False
    return False


def detect_frontend_framework(project_path: Path) -> Optional[Dict]:
    """
    Detect the frontend framework in a project.
    
    Returns:
        Dict with 'framework', 'confidence', and 'evidence', or None if not detected
    """
    if not project_path.exists():
        return None
    
    results = []
    
    for framework, patterns in FRONTEND_PATTERNS.items():
        confidence = 0
        evidence = []
        
        # Check package.json for keywords
        if check_package_json(project_path, patterns["keywords"]):
            confidence += 50
            evidence.append("Found framework keywords in package.json")
        
        # Check for files
        found_files = find_files_in_path(project_path, patterns["files"])
        if found_files:
            confidence += len(found_files) * 10
            evidence.extend([f"Found file: {f.relative_to(project_path)}" for f in found_files[:3]])
        
        # Check for config files
        if patterns.get("config_files"):
            config_files = find_files_in_path(project_path, patterns["config_files"])
            if config_files:
                confidence += 20
                evidence.append(f"Found config file: {config_files[0].relative_to(project_path)}")
        
        # Check for keywords in found files
        if found_files and patterns.get("keywords"):
            for file_path in found_files[:3]:  # Check first 3 files
                if check_keywords_in_file(file_path, patterns["keywords"]):
                    confidence += 15
                    evidence.append(f"Found keyword in: {file_path.relative_to(project_path)}")
                    break
        
        if confidence > 0:
            results.append({
                "framework": framework,
                "confidence": confidence,
                "evidence": evidence[:5]  # Limit evidence items
            })
    
    # Special case: if no framework detected but index.html exists, assume HTML
    if not results:
        index_html = project_path / "index.html"
        if index_html.exists():
            return {
                "framework": "html",
                "confidence": 30,
                "evidence": ["Found index.html"]
            }
        return None
    
    # Sort by confidence and return the best match
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[0]


def main():
    parser = argparse.ArgumentParser(description='Detect frontend framework in a project')
    parser.add_argument('--path', type=str, default='.', help='Project path (default: current directory)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    project_path = Path(args.path).resolve()
    
    result = detect_frontend_framework(project_path)
    
    if args.json:
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"framework": None, "message": "No frontend framework detected"}, indent=2))
    else:
        if result:
            print(f"✅ Detected frontend framework: {result['framework']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Evidence:")
            for evidence in result['evidence']:
                print(f"     - {evidence}")
        else:
            print("❌ No frontend framework detected")
            print("   Will use default: React")
            sys.exit(1)
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
