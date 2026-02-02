# 📁 File Analysis Module

This document explains how file analysis and malware detection works in Fsociety.

---

## Overview

The File Analysis module provides:

- **Hash Verification**: Calculate and verify file hashes
- **YARA Scanning**: Detect malware signatures
- **File Type Detection**: Verify file types match extensions
- **VirusTotal Integration**: Check against known malware

---

## Analysis Techniques

| Technique | Purpose |
|-----------|---------|
| **MD5/SHA256** | File integrity verification |
| **YARA Rules** | Pattern-based malware detection |
| **Magic Bytes** | True file type detection |
| **Entropy Analysis** | Detect packed/encrypted files |

---

## API Endpoints

### Analyze File
```http
POST /api/files/analyze
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: [binary data]
```

### Response
```json
{
  "filename": "suspicious.exe",
  "file_size": 102400,
  "hashes": {
    "md5": "d41d8cd98f00b204e9800998ecf8427e",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb924..."
  },
  "mime_type": "application/x-executable",
  "is_malicious": true,
  "detections": [
    {
      "rule": "TrojanDownloader",
      "description": "Detects trojan downloader patterns"
    }
  ],
  "risk_level": "critical"
}
```

---

## Code Flow

```python
# utils/file_tools.py

import hashlib
import yara
import magic

def analyze_file(file_content: bytes, filename: str) -> dict:
    """Analyze file for malware indicators"""
    
    # 1. Calculate hashes
    hashes = {
        'md5': hashlib.md5(file_content).hexdigest(),
        'sha256': hashlib.sha256(file_content).hexdigest()
    }
    
    # 2. Detect file type
    mime_type = magic.from_buffer(file_content, mime=True)
    
    # 3. Scan with YARA rules
    rules = yara.compile(filepath='data/yara_rules/malware.yar')
    matches = rules.match(data=file_content)
    
    # 4. Determine risk level
    is_malicious = len(matches) > 0
    
    return {
        'filename': filename,
        'file_size': len(file_content),
        'hashes': hashes,
        'mime_type': mime_type,
        'is_malicious': is_malicious,
        'detections': [{'rule': m.rule, 'description': m.meta.get('description')} for m in matches],
        'risk_level': 'critical' if is_malicious else 'low'
    }
```

---

## YARA Rules

Example rule for detecting suspicious patterns:

```yara
rule SuspiciousExecutable {
    meta:
        description = "Detects potentially malicious executable"
        author = "Fsociety"
        
    strings:
        $mz = {4D 5A}  // PE header
        $suspicious = "CreateRemoteThread"
        $powershell = "powershell.exe"
        
    condition:
        $mz at 0 and ($suspicious or $powershell)
}
```

---

## Related Documentation

- [Security Audit](../SecurityAudit/overview.md)
- [YARA Documentation](https://yara.readthedocs.io/)
