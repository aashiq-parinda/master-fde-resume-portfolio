import pytest
from src.analytics.cloud_cost import CloudCostCalculator

def test_cloud_cost_comparison_calculator():
    calc = CloudCostCalculator(inr_exchange_rate=83.0)
    res = calc.calculate_cost_comparison(
        num_containers=2,
        v_cpu=2.0,
        memory_gb=4.0,
        hours_per_month=730,
        monthly_data_processed_gb=100.0
    )
    
    assert "aws" in res
    assert "azure" in res
    assert "gcp" in res
    assert "summary" in res
    
    # Azure should be cheaper than AWS due to night-hours scale-down and free tier
    assert res["summary"]["cheapest_cloud"] == "Azure"
    assert res["summary"]["azure_monthly_savings_pct"] > 15.0
    assert res["azure"]["monthly_total_usd"] < res["aws"]["monthly_total_usd"]
    assert res["aws"]["annual_tcv_inr"] > 0
    assert res["azure"]["annual_tcv_inr"] > 0
