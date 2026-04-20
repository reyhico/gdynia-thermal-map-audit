"""Mermaid flowchart for the pipeline."""

from __future__ import annotations


def get_pipeline_flowchart() -> str:
    """Return a Mermaid diagram string describing the Phase 1 pipeline."""
    return """
```mermaid
flowchart TD
    A([Start]) --> B[audit-site\nDownload landing page HTML]
    B --> C[inspect-viewer\nSnapshot viewer page]
    C --> D[inventory-assets\nExtract script/link/image URLs]
    D --> E[probe-endpoints\nHTTP HEAD/GET + OGC GetCapabilities]
    E --> F{Data available?}

    F -->|Raster WMS/WMTS| G[fetch-assets\nDownload raster tiles]
    F -->|Vector WFS/GeoJSON| H[fetch-assets\nDownload vector features]
    F -->|No machine-readable data| I[Manual annotation\nScenario C]

    G --> J[compute-raster-indicators\nScenario A: zonal stats]
    H --> K[compute-vector-indicators\nScenario B: counts & density]
    I --> L[compute-annotation-indicators\nScenario C: annotation aggregation]

    J --> M[compute-priority-index\nWeighted composite score]
    K --> M
    L --> M

    M --> N[export-article-tables\nCSV + LaTeX tables]
    N --> O[export-figures\nChoropleth maps]
    O --> P([End])

    style A fill:#4CAF50,color:#fff
    style P fill:#4CAF50,color:#fff
    style F fill:#FF9800,color:#fff
    style I fill:#2196F3,color:#fff
```
""".strip()
