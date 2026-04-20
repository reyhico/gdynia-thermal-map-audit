"""Tests for Pydantic schema validation."""

import pytest
from pydantic import ValidationError

from gdynia_thermal_audit.schemas.annotation_records import AnnotationRecord
from gdynia_thermal_audit.schemas.source_inventory import SourceInventoryRecord
from gdynia_thermal_audit.schemas.layer_catalog import LayerCatalogRecord
from gdynia_thermal_audit.schemas.fetch_log import FetchLogRecord
from gdynia_thermal_audit.schemas.spatial_unit_metrics import SpatialUnitMetrics
from gdynia_thermal_audit.schemas.building_level_metrics import BuildingLevelMetrics
from gdynia_thermal_audit.schemas.pipeline_run_log import PipelineRunLog


# ---------------------------------------------------------------------------
# AnnotationRecord
# ---------------------------------------------------------------------------


class TestAnnotationRecord:
    def _valid(self, **overrides):
        base = {
            "record_id": "ANN-20240601-0001",
            "lon": 18.53,
            "lat": 54.52,
            "source_url": "https://termalne.obliview.com/?z=17",
            "observed_anomaly": True,
            "visibility_quality": 1,
            "annotator": "JK",
            "annotation_date": "2024-06-01",
        }
        base.update(overrides)
        return base

    def test_valid_record(self):
        rec = AnnotationRecord(**self._valid())
        assert rec.record_id == "ANN-20240601-0001"

    def test_optional_fields_default_none(self):
        rec = AnnotationRecord(**self._valid())
        assert rec.building_id is None
        assert rec.anomaly_scale_1_5 is None

    def test_anomaly_scale_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            AnnotationRecord(**self._valid(anomaly_scale_1_5=6))

    def test_anomaly_scale_min(self):
        rec = AnnotationRecord(**self._valid(anomaly_scale_1_5=1))
        assert rec.anomaly_scale_1_5 == 1

    def test_visibility_quality_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            AnnotationRecord(**self._valid(visibility_quality=4))

    def test_invalid_date_raises(self):
        with pytest.raises(ValidationError):
            AnnotationRecord(**self._valid(annotation_date="01/06/2024"))

    def test_lon_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            AnnotationRecord(**self._valid(lon=200.0))

    def test_lat_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            AnnotationRecord(**self._valid(lat=-100.0))


# ---------------------------------------------------------------------------
# SourceInventoryRecord
# ---------------------------------------------------------------------------


class TestSourceInventoryRecord:
    def test_valid_record(self):
        rec = SourceInventoryRecord(record_id="SRC-001", url="https://example.com")
        assert rec.record_id == "SRC-001"
        assert rec.status_code is None

    def test_all_optional_fields(self):
        rec = SourceInventoryRecord(
            record_id="SRC-002",
            url="https://example.com/wms",
            status_code=200,
            content_type="application/vnd.ogc.wms_xml",
            inferred_data_type="wms",
        )
        assert rec.inferred_data_type == "wms"

    def test_missing_required_url_raises(self):
        with pytest.raises(ValidationError):
            SourceInventoryRecord(record_id="SRC-003")


# ---------------------------------------------------------------------------
# LayerCatalogRecord
# ---------------------------------------------------------------------------


class TestLayerCatalogRecord:
    def test_valid_record(self):
        rec = LayerCatalogRecord(
            layer_id="LYR-001",
            source_url="https://example.com/wms",
            service_type="WMS",
        )
        assert rec.service_type == "WMS"

    def test_optional_fields_default_none(self):
        rec = LayerCatalogRecord(
            layer_id="LYR-002",
            source_url="https://example.com",
            service_type="UNKNOWN",
        )
        assert rec.title is None
        assert rec.crs is None


# ---------------------------------------------------------------------------
# SpatialUnitMetrics
# ---------------------------------------------------------------------------


class TestSpatialUnitMetrics:
    def test_valid_raster_scenario(self):
        m = SpatialUnitMetrics(
            unit_id="GDY-01",
            unit_type="district",
            data_source="raster",
            coverage_ratio=0.85,
            mean_intensity=0.62,
        )
        assert m.coverage_ratio == pytest.approx(0.85)

    def test_coverage_ratio_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            SpatialUnitMetrics(
                unit_id="GDY-01",
                unit_type="district",
                data_source="raster",
                coverage_ratio=1.5,  # > 1.0
            )

    def test_all_indicators_none_is_valid(self):
        m = SpatialUnitMetrics(unit_id="GDY-02", unit_type="grid", data_source="annotation")
        assert m.anomaly_count is None
        assert m.priority_index is None


# ---------------------------------------------------------------------------
# BuildingLevelMetrics
# ---------------------------------------------------------------------------


class TestBuildingLevelMetrics:
    def test_valid(self):
        m = BuildingLevelMetrics(building_id="OSM-12345", has_anomaly=True, source="annotation")
        assert m.has_anomaly is True

    def test_anomaly_scale_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            BuildingLevelMetrics(building_id="OSM-999", anomaly_scale=0, source="vector")


# ---------------------------------------------------------------------------
# PipelineRunLog
# ---------------------------------------------------------------------------


class TestPipelineRunLog:
    def test_valid(self):
        log = PipelineRunLog(
            run_id="550e8400-e29b-41d4-a716-446655440000",
            start_time="2024-06-01T08:00:00Z",
        )
        assert log.scenario == "auto"
        assert log.steps_completed == []
        assert log.errors == []

    def test_with_steps(self):
        log = PipelineRunLog(
            run_id="550e8400-e29b-41d4-a716-446655440001",
            start_time="2024-06-01T08:00:00Z",
            steps_completed=["audit_site", "probe_endpoints"],
        )
        assert len(log.steps_completed) == 2
