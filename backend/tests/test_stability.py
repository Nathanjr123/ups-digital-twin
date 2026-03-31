"""
Stability tests for UPS Digital Twin backend.
Ensures data generation, validation, API endpoints, and ML predictions
don't crash under various conditions.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ml.data_generator import UPSDataGenerator, FleetDataGenerator
from app.models.ups import UPSTelemetry, UPSMetadata, UPSInfo, FleetSummary, TelemetryHistory
from app.services.ups_service import UPSService


class TestDataGenerator:
    """Test that data generators produce valid data under all failure modes."""

    def setup_method(self):
        self.ups = UPSDataGenerator("UPS-TEST", "Test Location", "TestModel 10kVA")

    def test_normal_operation_valid(self):
        """Normal operation should always produce valid telemetry."""
        for _ in range(50):
            data = self.ups.generate_normal_operation()
            t = UPSTelemetry(**data)
            assert 0 <= t.battery_soc <= 100
            assert 0 <= t.load_percentage <= 100
            assert t.runtime_remaining >= 0
            assert 45 <= t.input_frequency <= 65
            assert t.input_current >= 0
            assert t.output_current >= 0

    def test_battery_degradation_valid(self):
        """Battery degradation at all stages should produce valid telemetry."""
        for day in range(15):
            data = self.ups.generate_battery_degradation(day)
            data = UPSService()._clamp_telemetry(data)
            t = UPSTelemetry(**data)
            assert 0 <= t.battery_soc <= 100
            assert t.runtime_remaining >= 0
            assert 0 <= t.health_score <= 100

    def test_overload_valid(self):
        """Overload conditions should produce valid telemetry."""
        for _ in range(50):
            data = self.ups.generate_overload_condition()
            data = UPSService()._clamp_telemetry(data)
            t = UPSTelemetry(**data)
            assert 0 <= t.load_percentage <= 100
            assert t.runtime_remaining >= 0

    def test_cooling_failure_valid(self):
        """Cooling failure at all stages should produce valid telemetry."""
        for hours in range(25):
            data = self.ups.generate_cooling_failure(hours)
            data = UPSService()._clamp_telemetry(data)
            t = UPSTelemetry(**data)
            assert t.battery_temperature <= 100, f"Battery temp {t.battery_temperature} too high at hour {hours}"
            assert t.inverter_temperature <= 120, f"Inverter temp {t.inverter_temperature} too high at hour {hours}"

    def test_input_power_instability_valid(self):
        """Input power instability should produce valid telemetry."""
        for _ in range(50):
            data = self.ups.generate_input_power_instability()
            data = UPSService()._clamp_telemetry(data)
            t = UPSTelemetry(**data)
            assert 0 <= t.input_voltage <= 500
            assert 45 <= t.input_frequency <= 65

    def test_anomaly_valid(self):
        """Random anomalies should produce valid telemetry."""
        for _ in range(50):
            data = self.ups.generate_anomaly()
            data = UPSService()._clamp_telemetry(data)
            t = UPSTelemetry(**data)
            assert t.status == "anomaly_detected"

    def test_data_point_all_failure_modes(self):
        """generate_data_point should work for all failure modes."""
        modes = ["none", "battery_degradation", "overload", "cooling_failure", "input_power"]
        svc = UPSService()
        for mode in modes:
            ups = UPSDataGenerator("UPS-TEST", "Test", "Model")
            ups.set_failure_mode(mode)
            for _ in range(20):
                data = ups.generate_data_point()
                data = svc._clamp_telemetry(data)
                t = UPSTelemetry(**data)
                assert t.ups_id == "UPS-TEST"


class TestFleetDataGenerator:
    """Test fleet-level data generation."""

    def test_fleet_initialization(self):
        """Fleet should initialize with 12 units."""
        fleet = FleetDataGenerator()
        assert len(fleet.fleet) == 12

    def test_fleet_snapshot_valid(self):
        """Fleet snapshot should produce 12 valid telemetry entries."""
        svc = UPSService()
        for _ in range(10):
            snapshot = svc.generate_fleet_snapshot()
            assert len(snapshot) == 12
            for t in snapshot:
                assert 0 <= t.battery_soc <= 100
                assert t.runtime_remaining >= 0
                assert 0 <= t.health_score <= 100
                assert 0 <= t.load_percentage <= 100
                assert 0 <= t.input_voltage <= 500
                assert 0 <= t.output_voltage <= 500
                assert 45 <= t.input_frequency <= 65
                assert 45 <= t.output_frequency <= 65
                assert t.input_current >= 0
                assert t.output_current >= 0

    def test_get_ups_by_id(self):
        """Should find UPS by ID."""
        fleet = FleetDataGenerator()
        ups = fleet.get_ups_by_id("UPS-001")
        assert ups.ups_id == "UPS-001"

    def test_get_ups_by_id_not_found(self):
        """Should raise ValueError for unknown ID."""
        fleet = FleetDataGenerator()
        with pytest.raises(ValueError):
            fleet.get_ups_by_id("UPS-999")


class TestUPSService:
    """Test the UPS service layer."""

    def setup_method(self):
        self.svc = UPSService()

    def test_get_all_ups(self):
        """Should return 12 valid UPS info objects."""
        result = self.svc.get_all_ups()
        assert len(result) == 12
        for ups in result:
            assert ups.metadata.ups_id
            assert ups.health_status in ["healthy", "warning", "critical"]

    def test_get_all_ups_repeated(self):
        """Repeated calls should never crash (tests randomness stability)."""
        for _ in range(20):
            result = self.svc.get_all_ups()
            assert len(result) == 12

    def test_get_ups_by_id(self):
        """Should return valid info for known UPS."""
        result = self.svc.get_ups_by_id("UPS-001")
        assert result is not None
        assert result.metadata.ups_id == "UPS-001"

    def test_get_ups_by_id_not_found(self):
        """Should return None for unknown UPS."""
        result = self.svc.get_ups_by_id("UPS-999")
        assert result is None

    def test_get_latest_telemetry(self):
        """Should return valid telemetry."""
        result = self.svc.get_latest_telemetry("UPS-001")
        assert result is not None
        assert result.ups_id == "UPS-001"

    def test_get_fleet_summary(self):
        """Fleet summary should have valid counts."""
        summary = self.svc.get_fleet_summary()
        assert summary.total_units == 12
        assert summary.healthy_units + summary.warning_units + summary.critical_units == 12
        assert 0 <= summary.average_health_score <= 100
        assert 0 <= summary.average_battery_soc <= 100

    def test_fleet_summary_repeated(self):
        """Repeated fleet summary calls should never crash."""
        for _ in range(20):
            summary = self.svc.get_fleet_summary()
            assert summary.total_units == 12

    def test_get_telemetry_history(self):
        """Should generate history for any UPS."""
        history = self.svc.get_telemetry_history("UPS-001", hours=1)
        assert history is not None
        assert history.ups_id == "UPS-001"
        assert len(history.data_points) > 0

    def test_get_telemetry_history_critical_ups(self):
        """History for critical UPS (UPS-012 cooling failure) should not crash."""
        history = self.svc.get_telemetry_history("UPS-012", hours=24)
        assert history is not None
        for point in history.data_points:
            assert point.battery_temperature < 200, f"Unrealistic temp: {point.battery_temperature}"

    def test_clamp_telemetry_negative_values(self):
        """Clamping should fix negative/out-of-range values."""
        bad_data = {
            "input_voltage": -10,
            "input_current": -5,
            "input_frequency": 30,
            "output_voltage": 600,
            "output_current": -1,
            "output_frequency": 70,
            "battery_voltage": -2,
            "battery_soc": 110,
            "runtime_remaining": -20,
            "load_percentage": -5,
            "health_score": 150,
        }
        result = self.svc._clamp_telemetry(bad_data)
        assert result["input_voltage"] == 0
        assert result["input_current"] == 0
        assert result["input_frequency"] == 45
        assert result["output_voltage"] == 500
        assert result["output_current"] == 0
        assert result["output_frequency"] == 65
        assert result["battery_voltage"] == 0
        assert result["battery_soc"] == 100
        assert result["runtime_remaining"] == 0
        assert result["load_percentage"] == 0
        assert result["health_score"] == 100


class TestMLPredictions:
    """Test that ML predictions don't crash."""

    def setup_method(self):
        from app.ml.model_trainer import train_models_on_startup
        self.trainer = train_models_on_startup()
        self.models = self.trainer.get_models()
        self.svc = UPSService()

    def test_anomaly_detection_all_units(self):
        """Anomaly detection should work for all 12 units."""
        detector = self.models["anomaly_detector"]
        snapshot = self.svc.generate_fleet_snapshot()
        for t in snapshot:
            result = detector.detect_anomaly(t.model_dump())
            assert "is_anomaly" in result
            assert "anomaly_score" in result
            assert "contributing_factors" in result

    def test_failure_prediction_all_units(self):
        """Failure prediction should work for all 12 units."""
        predictor = self.models["failure_predictor"]
        snapshot = self.svc.generate_fleet_snapshot()
        for t in snapshot:
            result = predictor.predict_failure(t.model_dump())
            assert "will_fail" in result
            assert "failure_probability" in result
            assert 0 <= result["failure_probability"] <= 1

    def test_predictions_repeated(self):
        """Repeated predictions should never crash."""
        detector = self.models["anomaly_detector"]
        predictor = self.models["failure_predictor"]
        for _ in range(10):
            snapshot = self.svc.generate_fleet_snapshot()
            for t in snapshot:
                d = t.model_dump()
                detector.detect_anomaly(d)
                predictor.predict_failure(d)


class TestAPIEndpoints:
    """Test FastAPI endpoints via live server."""

    def setup_method(self):
        import httpx
        self.client = httpx.Client(base_url="http://localhost:8001", timeout=10)

    def test_health(self):
        r = self.client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_root(self):
        r = self.client.get("/")
        assert r.status_code == 200
        assert "status" in r.json()

    def test_get_all_ups(self):
        r = self.client.get("/api/ups/")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 12

    def test_get_fleet_summary(self):
        r = self.client.get("/api/ups/fleet-summary")
        assert r.status_code == 200
        data = r.json()
        assert data["total_units"] == 12

    def test_get_ups_by_id(self):
        r = self.client.get("/api/ups/UPS-001")
        assert r.status_code == 200
        assert r.json()["metadata"]["ups_id"] == "UPS-001"

    def test_get_ups_not_found(self):
        r = self.client.get("/api/ups/UPS-999")
        assert r.status_code == 404

    def test_get_telemetry(self):
        r = self.client.get("/api/ups/UPS-001/telemetry")
        assert r.status_code == 200
        assert r.json()["ups_id"] == "UPS-001"

    def test_get_history(self):
        r = self.client.get("/api/ups/UPS-001/history?hours=1")
        assert r.status_code == 200
        data = r.json()
        assert data["ups_id"] == "UPS-001"
        assert len(data["data_points"]) > 0

    def test_get_predictions(self):
        r = self.client.get("/api/predictions/UPS-001")
        assert r.status_code == 200
        data = r.json()
        assert "anomaly" in data
        assert "failure" in data
        assert "overall_risk_score" in data

    def test_get_predictions_critical_ups(self):
        """Predictions for critical UPS should not crash."""
        for ups_id in ["UPS-009", "UPS-011", "UPS-012"]:
            r = self.client.get(f"/api/predictions/{ups_id}")
            assert r.status_code == 200, f"Prediction failed for {ups_id}"

    def test_run_batch_predictions(self):
        r = self.client.post("/api/predictions/run")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 12

    def test_get_alerts(self):
        r = self.client.get("/api/alerts/")
        assert r.status_code == 200

    def test_get_alert_stats(self):
        r = self.client.get("/api/alerts/statistics")
        assert r.status_code == 200

    def test_model_performance(self):
        r = self.client.get("/api/predictions/analytics/model-performance")
        assert r.status_code == 200

    def test_all_endpoints_repeated(self):
        """Hit all major endpoints 5 times to check stability."""
        endpoints = [
            "/api/ups/",
            "/api/ups/fleet-summary",
            "/api/ups/UPS-001",
            "/api/ups/UPS-012",
            "/api/predictions/UPS-001",
            "/api/predictions/UPS-012",
            "/api/alerts/",
        ]
        for _ in range(5):
            for endpoint in endpoints:
                r = self.client.get(endpoint)
                assert r.status_code == 200, f"Failed: {endpoint} (attempt {_+1})"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
