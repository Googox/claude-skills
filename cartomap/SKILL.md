# Cartomap — Geospatial Mapping & GeoJSON Toolkit

**Tier:** POWERFUL  
**Category:** Engineering  
**Tags:** geospatial, cartography, GeoJSON, TopoJSON, maps, spatial-data, visualization

## Overview

Cartomap is a comprehensive geospatial mapping skill for working with geographic data formats, cartographic datasets, and spatial analysis workflows. It provides structured tooling for loading, transforming, validating, and visualizing GeoJSON and TopoJSON data — from country-level world maps down to regional administrative boundaries.

The skill integrates with the [cartomap](https://github.com/cartomap) open dataset ecosystem, which publishes simplified GeoJSON/TopoJSON for Dutch administrative areas (`nl`) and world regions (`world`), and provides patterns for working with any compliant geographic dataset.

## Core Capabilities

### 1. GeoJSON & TopoJSON Authoring

**Format expertise:**
- GeoJSON (RFC 7946): Feature, FeatureCollection, Geometry types (Point, LineString, Polygon, MultiPolygon, etc.)
- TopoJSON: topology-preserving format that reduces file size 40–80% vs equivalent GeoJSON
- CRS handling: WGS-84 default (EPSG:4326); reprojection guidance for Web Mercator (EPSG:3857) and others
- Coordinate precision: rounding strategies for web vs print vs data-exchange contexts

**Common transforms:**
- Simplify polygon complexity (Douglas-Peucker / Visvalingam-Whyatt)
- Merge / dissolve boundaries (e.g., provinces → country outline)
- Clip to bounding box or mask geometry
- Validate and repair self-intersections, winding-order issues, and duplicate coordinates

### 2. Cartomap Dataset Integration

**Dutch administrative areas (`cartomap/nl`):**

| Layer | Description | Typical use |
|-------|-------------|-------------|
| `gemeenten` | Municipalities (~342) | Local-authority choropleth maps |
| `provincies` | Provinces (12) | Regional comparison maps |
| `coropgebieden` | COROP regions (40) | Economic/statistical areas |
| `waterschappen` | Water boards (21) | Environmental & flood risk maps |
| `veiligheidsregio` | Safety regions (25) | Emergency management maps |

**World regions (`cartomap/world`):**

| Layer | Description |
|-------|-------------|
| `countries` | Simplified country polygons (110m, 50m, 10m resolution) |
| `land` | Landmass outline |
| `graticule` | Latitude/longitude grid lines |
| `sphere` | Background sphere for globe projections |

**Loading datasets:**
```js
// TopoJSON via CDN
import * as topojson from "topojson-client";
const world = await fetch("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json").then(r => r.json());
const countries = topojson.feature(world, world.objects.countries);

// cartomap/nl municipalities
const nl = await fetch("https://cartomap.github.io/nl/wgs84/gemeente_2024.topojson").then(r => r.json());
const gemeenten = topojson.feature(nl, nl.objects.gemeente_2024);
```

### 3. Map Visualization Workflows

**D3.js choropleth (web):**
```js
import * as d3 from "d3";
import * as topojson from "topojson-client";

// 1. Load data
const [geo, stats] = await Promise.all([fetchGeo(), fetchStats()]);
const features = topojson.feature(geo, geo.objects.gemeenten);

// 2. Projection
const projection = d3.geoMercator().fitSize([width, height], features);
const path = d3.geoPath(projection);

// 3. Color scale
const color = d3.scaleSequential(d3.interpolateBlues)
  .domain(d3.extent(stats, d => d.value));

// 4. Render
svg.selectAll("path")
  .data(features.features)
  .join("path")
  .attr("d", path)
  .attr("fill", d => color(statsMap.get(d.id)));
```

**Python / GeoPandas (data science):**
```python
import geopandas as gpd
import matplotlib.pyplot as plt

gdf = gpd.read_file("gemeente_2024.geojson")
gdf = gdf.merge(stats_df, on="gemeentecode")

fig, ax = plt.subplots(figsize=(10, 12))
gdf.plot(column="value", cmap="Blues", legend=True, ax=ax)
ax.set_title("Municipality Map")
plt.tight_layout()
plt.savefig("map.png", dpi=150)
```

**Leaflet.js (interactive tiles):**
```js
const map = L.map("map").setView([52.3, 5.3], 7);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

const layer = L.geoJSON(geojsonData, {
  style: f => ({ fillColor: colorScale(f.properties.value), weight: 1 }),
  onEachFeature: (f, l) => l.bindPopup(f.properties.name)
}).addTo(map);
```

### 4. Spatial Analysis Patterns

**Point-in-polygon lookup:**
```python
from shapely.geometry import Point
import geopandas as gpd

gdf = gpd.read_file("gemeente_2024.geojson").set_index("gemeentecode")
point = Point(4.9041, 52.3676)  # Amsterdam
result = gdf[gdf.contains(point)]
```

**Bounding box filter:**
```python
bbox = (4.5, 51.9, 5.1, 52.5)  # (minX, minY, maxX, maxY) — Utrecht area
subset = gdf.cx[bbox[0]:bbox[2], bbox[1]:bbox[3]]
```

**Area calculation (projected CRS):**
```python
gdf_rd = gdf.to_crs("EPSG:28992")          # Rijksdriehoekstelsel (NL national grid)
gdf_rd["area_km2"] = gdf_rd.geometry.area / 1e6
```

**Centroid extraction:**
```python
gdf["centroid_lon"] = gdf.geometry.centroid.x
gdf["centroid_lat"] = gdf.geometry.centroid.y
```

### 5. Data Quality & Validation

**GeoJSON validation checklist:**
- [ ] All coordinates are [longitude, latitude] order (not lat/lon)
- [ ] Polygons are closed (first == last coordinate)
- [ ] Exterior rings are counter-clockwise; holes are clockwise
- [ ] No self-intersecting rings
- [ ] CRS is WGS-84 (or explicitly declared)
- [ ] Feature `id` fields are unique
- [ ] No `null` geometry in FeatureCollection unless intentional

**TopoJSON validation:**
- [ ] `arcs` array is populated
- [ ] `transform` (scale + translate) is present
- [ ] Object keys match expected layer names
- [ ] Quantization level is appropriate (typically 1e4–1e6)

**Automated validation script:** see `scripts/validate_geojson.py`

### 6. File Size Optimization

| Technique | Typical saving | Trade-off |
|-----------|---------------|-----------|
| Convert GeoJSON → TopoJSON | 40–80% | Requires topojson-client at runtime |
| Reduce coordinate precision (6 → 4 dp) | 15–25% | Sub-meter accuracy lost (acceptable for web maps) |
| Simplify geometry (low tolerance) | 20–60% | Visual quality at high zoom reduced |
| gzip/brotli compression | 60–80% (on top) | Server must serve compressed |
| Remove unused properties | Variable | Depends on property payload |

## Workflows

### Workflow 1: Build a Dutch Municipality Choropleth

1. **Fetch geometry** — Load `gemeente_YYYY.topojson` from cartomap/nl
2. **Prepare statistics** — Join your data on `gemeentecode` (CBS municipality code)
3. **Choose projection** — Rijksdriehoekstelsel (`EPSG:28992`) for accurate NL maps; Mercator for tile-based overlays
4. **Design color scale** — Sequential for continuous data; diverging for above/below average; categorical for discrete classes
5. **Render** — D3 for SVG exports; Leaflet/MapLibre for interactive web; GeoPandas/matplotlib for print/report output
6. **Label** — Add municipality names at centroids; hide labels below a minimum area threshold

### Workflow 2: World Map with Country Data

1. **Fetch** `countries-110m.json` (low-res) or `countries-50m.json` (medium) from world-atlas
2. **Join** on ISO 3166-1 numeric codes (the `id` field in world-atlas)
3. **Project** — Natural Earth (`d3.geoNaturalEarth1`) for world overviews; Mercator for regional
4. **Render** — Same D3/Leaflet patterns as above
5. **Clip** to region of interest if needed (bounding box clip)

### Workflow 3: GeoJSON → TopoJSON Pipeline

1. **Install** `topojson-server`: `npm install -g topojson-server`
2. **Convert**: `geo2topo -q 1e5 input.geojson > output.topojson`
3. **Validate** file size reduction and visual accuracy at target zoom levels
4. **Simplify** further if needed: `toposimplify -P 0.001 output.topojson > simplified.topojson`
5. **Merge** multiple layers into one file: `geo2topo layer1=a.geojson layer2=b.geojson > combined.topojson`

### Workflow 4: Validate & Repair GeoJSON

1. **Run** `python scripts/validate_geojson.py input.geojson` — reports issues
2. **Fix winding order** — `scripts/validate_geojson.py --fix`
3. **Check topology** — look for gaps, overlaps, and slivers using GeoPandas overlay
4. **Re-validate** after repair pass

## Key Dependencies

| Library | Purpose | Install |
|---------|---------|---------|
| `topojson-client` | Parse TopoJSON in browser/Node | `npm install topojson-client` |
| `topojson-server` | Convert GeoJSON → TopoJSON | `npm install -g topojson-server` |
| `d3-geo` | Projections, path rendering | `npm install d3-geo` |
| `geopandas` | Python spatial data frames | `pip install geopandas` |
| `shapely` | Python geometry operations | `pip install shapely` |
| `fiona` | Python GeoJSON/Shapefile I/O | `pip install fiona` |
| `pyproj` | Python CRS transformations | `pip install pyproj` |
| `leaflet` | Interactive tile maps | `npm install leaflet` |

## Data Sources

- **cartomap/nl**: https://github.com/cartomap/nl — Dutch administrative boundaries (updated annually)
- **cartomap/world**: https://github.com/cartomap/world — Simplified world geometries
- **world-atlas**: https://github.com/topojson/world-atlas — Natural Earth world data as TopoJSON
- **us-atlas**: https://github.com/topojson/us-atlas — US state/county TopoJSON
- **Natural Earth**: https://www.naturalearthdata.com/ — Free vector and raster map data
- **OpenStreetMap**: https://www.openstreetmap.org/ — Contributor-maintained global map data

## Common Issues & Fixes

**Coordinates appear mirrored or inverted:**  
GeoJSON uses [longitude, latitude] — many data sources export [latitude, longitude]. Swap coordinate pairs.

**Polygons render with holes where there should be fill:**  
Winding order is reversed. Use `scripts/validate_geojson.py --fix` or the `rewind` option in D3.

**File too large for web delivery:**  
Convert to TopoJSON + gzip. Target < 500 KB for initial load; lazy-load detail layers.

**Projection looks distorted:**  
Use an equal-area projection (Albers, Lambert) for area comparison; equidistant for distance; conformal (Mercator) for navigation only.

**Municipality codes don't match your data:**  
CBS codes change annually with mergers. Align on `gemeentecode` year matching your TopoJSON vintage.
