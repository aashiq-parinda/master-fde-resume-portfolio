import pytest
from src.engine.failover import MultiCloudFailoverManager

def test_automated_failover_and_failback():
    mgr = MultiCloudFailoverManager(failure_threshold=3, recovery_threshold=2)
    assert mgr.active_cloud == "AWS"
    
    # 2 failures: still AWS
    mgr.report_probe_result("AWS", is_healthy=False)
    mgr.report_probe_result("AWS", is_healthy=False)
    assert mgr.active_cloud == "AWS"
    
    # 3rd failure: automated failover to AZURE
    res = mgr.report_probe_result("AWS", is_healthy=False)
    assert mgr.active_cloud == "AZURE"
    assert res["event_triggered"]["action"] == "FAILOVER_TO_SECONDARY"
    
    # Primary recovers (1 success)
    mgr.report_probe_result("AWS", is_healthy=True)
    assert mgr.active_cloud == "AZURE" # needs 2 successes to failback
    
    # 2nd success -> Failback to AWS
    res_back = mgr.report_probe_result("AWS", is_healthy=True)
    assert mgr.active_cloud == "AWS"
    assert res_back["event_triggered"]["action"] == "FAILBACK_TO_PRIMARY"

def test_manual_failover_drill():
    mgr = MultiCloudFailoverManager()
    mgr.manual_failover("AZURE", "Disaster recovery drill")
    assert mgr.active_cloud == "AZURE"
