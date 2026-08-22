import pytest
import xml.etree.ElementTree as ET
from src.engine.mapping import (
    map_rest_payload,
    map_xml_element,
    map_csv_row,
    map_webhook_payload,
    ValidationError
)

def test_map_rest_payload_valid():
    raw = {"id": "r_101", "name": "Rajesh Kumar", "email": "rajesh@crm.com", "balance": 45000.50, "active": True}
    mapped = map_rest_payload(raw)
    assert mapped["external_id"] == "r_101"
    assert mapped["name"] == "Rajesh Kumar"
    assert mapped["email"] == "rajesh@crm.com"
    assert mapped["balance"] == 45000.50
    assert mapped["status"] == "active"

def test_map_rest_payload_invalid():
    # Missing email
    raw = {"id": "r_101", "name": "Rajesh Kumar", "balance": 45000.50, "active": True}
    with pytest.raises(ValidationError):
        map_rest_payload(raw)

    # Invalid email format
    raw2 = {"id": "r_101", "name": "Rajesh Kumar", "email": "rajesh_crm_com", "balance": 45000.50, "active": True}
    with pytest.raises(ValidationError):
        map_rest_payload(raw2)

def test_map_xml_element_valid():
    xml_str = """
    <account>
        <id>x_201</id>
        <name>Amit Patel</name>
        <email>amit@billing.com</email>
        <balance>75000.00</balance>
        <status>active</status>
    </account>
    """
    element = ET.fromstring(xml_str)
    mapped = map_xml_element(element)
    assert mapped["external_id"] == "x_201"
    assert mapped["name"] == "Amit Patel"
    assert mapped["email"] == "amit@billing.com"
    assert mapped["balance"] == 75000.00
    assert mapped["status"] == "active"

def test_map_xml_element_invalid():
    # Missing ID
    xml_str = """
    <account>
        <name>Amit Patel</name>
        <email>amit@billing.com</email>
        <balance>75000.00</balance>
        <status>active</status>
    </account>
    """
    element = ET.fromstring(xml_str)
    with pytest.raises(ValidationError):
        map_xml_element(element)

def test_map_csv_row_valid():
    row = {
        "customer_id": "c_401",
        "name": "Vikram Singh",
        "email": "vikram@mainframe.com",
        "balance": "125000.00",
        "status": "active"
    }
    mapped = map_csv_row(row)
    assert mapped["external_id"] == "c_401"
    assert mapped["name"] == "Vikram Singh"
    assert mapped["email"] == "vikram@mainframe.com"
    assert mapped["balance"] == 125000.00
    assert mapped["status"] == "active"

def test_map_webhook_payload_valid():
    payload = {
        "event": "customer.created",
        "data": {
            "id": "w_301",
            "name": "Sunita Rao",
            "email": "sunita@orders.com",
            "amount": "25000.00",
            "status": "completed"
        }
    }
    mapped = map_webhook_payload(payload)
    assert mapped["external_id"] == "w_301"
    assert mapped["name"] == "Sunita Rao"
    assert mapped["email"] == "sunita@orders.com"
    assert mapped["balance"] == 25000.00
    assert mapped["status"] == "active"
