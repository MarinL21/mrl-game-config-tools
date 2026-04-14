#!/usr/bin/env python3
"""
Detect backend language and framework in a project.

Usage:
    python scripts/detect_backend.py [--path <project_path>]

Examples:
    python scripts/detect_backend.py
    python scripts/detect_backend.py --path /path/to/project
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, List


# Backend language detection patterns
BACKEND_PATTERNS = {
    "nodejs": {
        "files": ["package.json", "server.js", "app.js", "index.js"],
        "dirs": ["server", "backend", "api"],
        "keywords": ["express", "koa", "fastify", "nest"]
    },
    "python": {
        "files": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "manage.py", "app.py", "main.py"],
        "dirs": ["server", "backend", "api"],
        "keywords": ["flask", "django", "fastapi", "tornado", "bottle"]
    },
    "java": {
        "files": ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"],
        "dirs": ["src/main/java", "src/main/kotlin"],
        "keywords": ["spring", "springboot", "javax.servlet"]
    },
    "go": {
        "files": ["go.mod", "go.sum", "main.go"],
        "dirs": ["cmd", "internal", "pkg"],
        "keywords": ["gin", "echo", "fiber", "gorilla"]
    },
    "php": {
        "files": ["composer.json", "composer.lock", "index.php", "app.php"],
        "dirs": ["app", "src"],
        "keywords": ["laravel", "symfony", "codeigniter", "yii"]
    },
    "ruby": {
        "files": ["Gemfile", "Gemfile.lock", "config.ru", "Rakefile"],
        "dirs": ["app", "lib"],
        "keywords": ["rails", "sinatra", "rack"]
    },
    "csharp": {
        "files": ["*.csproj", "*.sln", "*.cs"],
        "dirs": ["src", "Controllers", "Models"],
        "keywords": ["asp.net", "mvc", "webapi"]
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


def detect_backend_language(project_path: Path) -> Optional[Dict]:
    """
    Detect the backend language and framework in a project.
    
    Returns:
        Dict with 'language', 'framework', 'confidence', and 'evidence', or None if not detected
    """
    if not project_path.exists():
        return None
    
    results = []
    
    for lang, patterns in BACKEND_PATTERNS.items():
        confidence = 0
        evidence = []
        
        # Check for files
        found_files = find_files_in_path(project_path, patterns["files"])
        if found_files:
            confidence += len(found_files) * 10
            evidence.extend([f"Found file: {f.relative_to(project_path)}" for f in found_files[:3]])
        
        # Check for directories
        for dir_name in patterns["dirs"]:
            dir_path = project_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                confidence += 15
                evidence.append(f"Found directory: {dir_name}")
                break
        
        # Check for keywords in found files
        if found_files and patterns.get("keywords"):
            for file_path in found_files[:5]:  # Check first 5 files
                if check_keywords_in_file(file_path, patterns["keywords"]):
                    confidence += 20
                    evidence.append(f"Found keyword in: {file_path.relative_to(project_path)}")
                    break
        
        if confidence > 0:
            # Try to determine framework
            framework = None
            if found_files:
                for file_path in found_files:
                    content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
                    for keyword in patterns.get("keywords", []):
                        if keyword.lower() in content:
                            framework = keyword
                            break
                    if framework:
                        break
            
            results.append({
                "language": lang,
                "framework": framework,
                "confidence": confidence,
                "evidence": evidence[:5]  # Limit evidence items
            })
    
    if not results:
        return None
    
    # Sort by confidence and return the best match
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[0]


def main():
    parser = argparse.ArgumentParser(description='Detect backend language in a project')
    parser.add_argument('--path', type=str, default='.', help='Project path (default: current directory)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    project_path = Path(args.path).resolve()
    
    result = detect_backend_language(project_path)
    
    if args.json:
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"language": None, "message": "No backend language detected"}, indent=2))
    else:
        if result:
            print(f"✅ Detected backend language: {result['language']}")
            if result.get('framework'):
                print(f"   Framework: {result['framework']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Evidence:")
            for evidence in result['evidence']:
                print(f"     - {evidence}")
        else:
            print("❌ No backend language detected")
            print("   Will use default: Node.js")
            sys.exit(1)
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
