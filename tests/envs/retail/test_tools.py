# Copyright Sierra

import json
import pytest
from tests.envs.base_test import BaseEnvironmentTest, BaseToolTest
from tau_bench.envs.retail.data import load_data
from tau_bench.envs.retail.tools import ALL_TOOLS
from tau_bench.envs.retail.tools.get_user_details import GetUserDetails
from tau_bench.envs.retail.tools.calculate import Calculate
from tau_bench.envs.retail.tools.get_order_details import GetOrderDetails
from tau_bench.envs.retail.tools.get_product_details import GetProductDetails
from tau_bench.envs.retail.tools.find_user_id_by_name_zip import FindUserIdByNameZip
from tau_bench.envs.retail.tools.find_user_id_by_email import FindUserIdByEmail
from tau_bench.envs.retail.tools.list_all_product_types import ListAllProductTypes
from tau_bench.envs.retail.tools.cancel_pending_order import CancelPendingOrder


class TestRetailEnvironment(BaseEnvironmentTest):
    """Test the retail environment as a whole."""
    
    @property
    def data_load_func(self):
        return load_data
    
    @property
    def all_tools(self):
        return ALL_TOOLS
    
    def test_retail_data_structure(self):
        """Test retail-specific data structure."""
        data = self.data_load_func()
        
        # Check required keys
        assert "users" in data
        assert "orders" in data
        assert "products" in data
        
        # Check that we have data
        assert len(data["users"]) > 0
        assert len(data["orders"]) > 0
        assert len(data["products"]) > 0


class TestGetUserDetails(BaseToolTest):
    """Test GetUserDetails tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return GetUserDetails
    
    def test_get_existing_user(self):
        """Test getting details for existing user."""
        data = self.data
        # Get first user ID from test data
        user_id = next(iter(data["users"].keys()))
        
        result = self.tool_class.invoke(data, user_id=user_id)
        
        # Should return valid JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        
        # Should contain expected user structure
        assert "name" in parsed
        assert "address" in parsed
        assert "email" in parsed
    
    def test_get_nonexistent_user(self):
        """Test getting details for non-existent user."""
        data = self.data
        result = self.tool_class.invoke(data, user_id="nonexistent_user")
        
        assert result == "Error: user not found"
    
    def test_tool_info(self):
        """Test tool info for GetUserDetails."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "get_user_details"
        assert "user_id" in info["function"]["parameters"]["properties"]
        assert info["function"]["parameters"]["required"] == ["user_id"]


class TestCalculate(BaseToolTest):
    """Test Calculate tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return Calculate
    
    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        data = self.data
        
        # Test addition
        result = self.tool_class.invoke(data, expression="2 + 3")
        assert result == "5.0"
        
        # Test multiplication
        result = self.tool_class.invoke(data, expression="4 * 5")
        assert result == "20.0"
        
        # Test complex expression
        result = self.tool_class.invoke(data, expression="(10 + 5) * 2")
        assert result == "30.0"
    
    def test_invalid_expression(self):
        """Test handling of invalid expressions."""
        data = self.data
        
        # Test invalid characters
        result = self.tool_class.invoke(data, expression="2 + abc")
        assert "Error:" in result
        
        # Test dangerous expression attempts
        result = self.tool_class.invoke(data, expression="import os")
        assert "Error:" in result
    
    def test_division_by_zero(self):
        """Test division by zero handling."""
        data = self.data
        result = self.tool_class.invoke(data, expression="5 / 0")
        assert "Error:" in result
    
    def test_tool_info(self):
        """Test tool info for Calculate."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "calculate"
        assert "expression" in info["function"]["parameters"]["properties"]
        assert info["function"]["parameters"]["required"] == ["expression"]


class TestGetOrderDetails(BaseToolTest):
    """Test GetOrderDetails tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return GetOrderDetails
    
    def test_get_existing_order(self):
        """Test getting details for existing order."""
        data = self.data
        # Get first order ID from test data
        order_id = next(iter(data["orders"].keys()))
        
        result = self.tool_class.invoke(data, order_id=order_id)
        
        # Should return valid JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        
        # Should contain expected order structure
        expected_fields = ["user_id", "items", "status", "address"]
        for field in expected_fields:
            assert field in parsed, f"Order missing field: {field}"
    
    def test_get_nonexistent_order(self):
        """Test getting details for non-existent order."""
        data = self.data
        result = self.tool_class.invoke(data, order_id="#NONEXISTENT")
        
        assert result == "Error: order not found"
    
    def test_tool_info(self):
        """Test tool info for GetOrderDetails."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "get_order_details"
        assert "order_id" in info["function"]["parameters"]["properties"]
        assert info["function"]["parameters"]["required"] == ["order_id"]


class TestGetProductDetails(BaseToolTest):
    """Test GetProductDetails tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return GetProductDetails
    
    def test_get_existing_product(self):
        """Test getting details for existing product."""
        data = self.data
        # Get first product ID from test data
        product_id = next(iter(data["products"].keys()))
        
        result = self.tool_class.invoke(data, product_id=product_id)
        
        # Should return valid JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        
        # Should contain expected product structure
        expected_fields = ["name", "product_id"]
        for field in expected_fields:
            assert field in parsed, f"Product missing field: {field}"
    
    def test_get_nonexistent_product(self):
        """Test getting details for non-existent product."""
        data = self.data
        result = self.tool_class.invoke(data, product_id="nonexistent_product")
        
        assert result == "Error: product not found"
    
    def test_tool_info(self):
        """Test tool info for GetProductDetails."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "get_product_details"
        assert "product_id" in info["function"]["parameters"]["properties"]
        assert info["function"]["parameters"]["required"] == ["product_id"]


class TestFindUserIdByNameZip(BaseToolTest):
    """Test FindUserIdByNameZip tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return FindUserIdByNameZip
    
    def test_find_existing_user(self):
        """Test finding an existing user by name and zip."""
        data = self.data
        
        # Get a user from test data to use for search
        user_id, user_data = next(iter(data["users"].items()))
        first_name = user_data["name"]["first_name"]
        last_name = user_data["name"]["last_name"]
        zip_code = user_data["address"]["zip"]
        
        result = self.tool_class.invoke(
            data,
            first_name=first_name,
            last_name=last_name,
            zip=zip_code
        )
        
        assert result == user_id
    
    def test_find_nonexistent_user(self):
        """Test searching for non-existent user."""
        data = self.data
        
        result = self.tool_class.invoke(
            data,
            first_name="NonExistent",
            last_name="User",
            zip="00000"
        )
        
        assert result == "Error: user not found"
    
    def test_partial_match(self):
        """Test that partial matches don't work (all fields must match)."""
        data = self.data
        
        # Get a user from test data
        user_data = next(iter(data["users"].values()))
        first_name = user_data["name"]["first_name"]
        last_name = user_data["name"]["last_name"]
        
        # Use wrong zip
        result = self.tool_class.invoke(
            data,
            first_name=first_name,
            last_name=last_name,
            zip="wrong_zip"
        )
        
        assert result == "Error: user not found"
    
    def test_tool_info(self):
        """Test tool info for FindUserIdByNameZip."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "find_user_id_by_name_zip"
        required_params = info["function"]["parameters"]["required"]
        expected_params = {"first_name", "last_name", "zip"}
        assert set(required_params) == expected_params


class TestFindUserIdByEmail(BaseToolTest):
    """Test FindUserIdByEmail tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return FindUserIdByEmail
    
    def test_find_existing_user(self):
        """Test finding an existing user by email."""
        data = self.data
        
        # Get a user from test data to use for search
        user_id, user_data = next(iter(data["users"].items()))
        email = user_data["email"]
        
        result = self.tool_class.invoke(data, email=email)
        assert result == user_id
    
    def test_find_nonexistent_user(self):
        """Test searching for non-existent user by email."""
        data = self.data
        
        result = self.tool_class.invoke(data, email="nonexistent@example.com")
        assert result == "Error: user not found"
    
    def test_tool_info(self):
        """Test tool info for FindUserIdByEmail."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "find_user_id_by_email"
        assert "email" in info["function"]["parameters"]["properties"]
        assert info["function"]["parameters"]["required"] == ["email"]


class TestListAllProductTypes(BaseToolTest):
    """Test ListAllProductTypes tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return ListAllProductTypes
    
    def test_list_products(self):
        """Test listing all product types."""
        data = self.data
        result = self.tool_class.invoke(data)
        
        # Should return valid JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        
        # Should contain product names mapped to product ids
        assert len(parsed) > 0
        
        # Each value should be a product id that exists in the data
        for product_name, product_id in parsed.items():
            assert isinstance(product_name, str)
            assert isinstance(product_id, str)
            assert product_id in data["products"]
    
    def test_products_sorted(self):
        """Test that products are returned in sorted order."""
        data = self.data
        result = self.tool_class.invoke(data)
        parsed = json.loads(result)
        
        product_names = list(parsed.keys())
        assert product_names == sorted(product_names)
    
    def test_tool_info(self):
        """Test tool info for ListAllProductTypes."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "list_all_product_types"
        assert info["function"]["parameters"]["required"] == []


class TestCancelPendingOrder(BaseToolTest):
    """Test CancelPendingOrder tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return CancelPendingOrder
    
    def get_pending_order(self, data):
        """Find a pending order for testing."""
        for order_id, order in data["orders"].items():
            if order["status"] == "pending":
                return order_id, order
        return None, None
    
    def test_cancel_existing_pending_order(self):
        """Test canceling an existing pending order."""
        data = self.data
        order_id, order = self.get_pending_order(data)
        
        if order_id is None:
            pytest.skip("No pending orders found in test data")
        
        original_status = order["status"]
        result = self.tool_class.invoke(
            data, 
            order_id=order_id, 
            reason="no longer needed"
        )
        
        # Should return valid JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        
        # Order should now be cancelled
        assert parsed["status"] == "cancelled"
        assert parsed["cancel_reason"] == "no longer needed"
        assert "payment_history" in parsed
    
    def test_cancel_nonexistent_order(self):
        """Test canceling non-existent order."""
        data = self.data
        result = self.tool_class.invoke(
            data,
            order_id="#NONEXISTENT",
            reason="no longer needed"
        )
        
        assert result == "Error: order not found"
    
    def test_invalid_cancel_reason(self):
        """Test using invalid cancellation reason."""
        data = self.data
        order_id, order = self.get_pending_order(data)
        
        if order_id is None:
            pytest.skip("No pending orders found in test data")
        
        result = self.tool_class.invoke(
            data,
            order_id=order_id,
            reason="invalid reason"
        )
        
        assert result == "Error: invalid reason"
    
    def test_cancel_non_pending_order(self):
        """Test canceling non-pending order."""
        data = self.data
        # Find a non-pending order
        non_pending_order = None
        for order_id, order in data["orders"].items():
            if order["status"] != "pending":
                non_pending_order = order_id
                break
        
        if non_pending_order is None:
            pytest.skip("No non-pending orders found in test data")
        
        result = self.tool_class.invoke(
            data,
            order_id=non_pending_order,
            reason="no longer needed"
        )
        
        assert result == "Error: non-pending order cannot be cancelled"
    
    def test_tool_info(self):
        """Test tool info for CancelPendingOrder."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "cancel_pending_order"
        required_params = info["function"]["parameters"]["required"]
        expected_params = {"order_id", "reason"}
        assert set(required_params) == expected_params
        
        # Check that reason has proper enum values
        reason_prop = info["function"]["parameters"]["properties"]["reason"]
        expected_reasons = ["no longer needed", "ordered by mistake"]
        assert set(reason_prop["enum"]) == set(expected_reasons)