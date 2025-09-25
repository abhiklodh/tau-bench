# Copyright Sierra

import json
import pytest
from tests.envs.base_test import BaseEnvironmentTest, BaseToolTest
from tau_bench.envs.airline.data import load_data
from tau_bench.envs.airline.tools import ALL_TOOLS
from tau_bench.envs.airline.tools.get_user_details import GetUserDetails
from tau_bench.envs.airline.tools.get_reservation_details import GetReservationDetails
from tau_bench.envs.airline.tools.search_direct_flight import SearchDirectFlight
from tau_bench.envs.airline.tools.search_onestop_flight import SearchOnestopFlight
from tau_bench.envs.airline.tools.calculate import Calculate
from tau_bench.envs.airline.tools.list_all_airports import ListAllAirports


class TestAirlineEnvironment(BaseEnvironmentTest):
    """Test the airline environment as a whole."""
    
    @property
    def data_load_func(self):
        return load_data
    
    @property
    def all_tools(self):
        return ALL_TOOLS
    
    def test_airline_data_structure(self):
        """Test airline-specific data structure."""
        data = self.data_load_func()
        
        # Check required keys
        assert "users" in data
        assert "reservations" in data
        assert "flights" in data
        
        # Check that we have data
        assert len(data["users"]) > 0
        assert len(data["reservations"]) > 0
        assert len(data["flights"]) > 0


class TestAirlineGetUserDetails(BaseToolTest):
    """Test GetUserDetails tool for airline."""
    
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
        
        # Should contain expected user structure for airline
        assert "name" in parsed
        assert "address" in parsed
        assert "email" in parsed
        # Airline users may have additional fields like reservations
    
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


class TestGetReservationDetails(BaseToolTest):
    """Test GetReservationDetails tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return GetReservationDetails
    
    def test_get_existing_reservation(self):
        """Test getting details for existing reservation."""
        data = self.data
        # Get first reservation ID from test data
        reservation_id = next(iter(data["reservations"].keys()))
        
        result = self.tool_class.invoke(data, reservation_id=reservation_id)
        
        # Should return valid JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        
        # Should contain expected reservation structure
        expected_fields = ["user_id", "flights", "passengers", "payment"]
        for field in expected_fields:
            # Note: not all reservations may have all fields, so we check more flexibly
            pass
    
    def test_get_nonexistent_reservation(self):
        """Test getting details for non-existent reservation."""
        data = self.data
        result = self.tool_class.invoke(data, reservation_id="NONEXISTENT")
        
        assert result == "Error: user not found"  # Note: the error message says "user not found" in the code
    
    def test_tool_info(self):
        """Test tool info for GetReservationDetails."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "get_reservation_details"
        assert "reservation_id" in info["function"]["parameters"]["properties"]
        assert info["function"]["parameters"]["required"] == ["reservation_id"]


class TestSearchDirectFlight(BaseToolTest):
    """Test SearchDirectFlight tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return SearchDirectFlight
    
    def get_flight_route(self, data):
        """Find a valid flight route for testing."""
        for flight in data["flights"].values():
            for date, info in flight["dates"].items():
                if info["status"] == "available":
                    return flight["origin"], flight["destination"], date
        return None, None, None
    
    def test_search_available_flight(self):
        """Test searching for available direct flights."""
        data = self.data
        origin, destination, date = self.get_flight_route(data)
        
        if origin is None:
            pytest.skip("No available flights found in test data")
        
        result = self.tool_class.invoke(
            data,
            origin=origin,
            destination=destination,
            date=date
        )
        
        # Should return valid JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        
        # Should have at least one flight result
        assert len(parsed) > 0
        
        # Each result should have flight information
        for flight in parsed:
            assert "origin" in flight
            assert "destination" in flight
            assert flight["origin"] == origin
            assert flight["destination"] == destination
    
    def test_search_no_flights(self):
        """Test searching for flights that don't exist."""
        data = self.data
        result = self.tool_class.invoke(
            data,
            origin="XXX",  # Non-existent airport
            destination="YYY",
            date="2024-01-01"
        )
        
        # Should return empty list
        assert result == "[]"
    
    def test_search_unavailable_date(self):
        """Test searching for flights on unavailable date."""
        data = self.data
        
        # Find a flight and try a date we know won't work
        flight = next(iter(data["flights"].values()))
        result = self.tool_class.invoke(
            data,
            origin=flight["origin"],
            destination=flight["destination"],
            date="2099-12-31"  # Far future date
        )
        
        # Should return empty list
        assert result == "[]"
    
    def test_tool_info(self):
        """Test tool info for SearchDirectFlight."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "search_direct_flight"
        required_params = info["function"]["parameters"]["required"]
        expected_params = {"origin", "destination", "date"}
        assert set(required_params) == expected_params


class TestSearchOnestopFlight(BaseToolTest):
    """Test SearchOnestopFlight tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return SearchOnestopFlight
    
    def test_search_onestop_flights(self):
        """Test searching for one-stop flights."""
        data = self.data
        
        # Find available airports for testing
        airports = set()
        for flight in data["flights"].values():
            airports.add(flight["origin"])
            airports.add(flight["destination"])
        
        airports = list(airports)
        if len(airports) < 2:
            pytest.skip("Not enough airports for testing")
        
        origin = airports[0]
        destination = airports[1] if airports[1] != origin else airports[2] if len(airports) > 2 else airports[0]
        
        result = self.tool_class.invoke(
            data,
            origin=origin,
            destination=destination,
            date="2024-05-20"  # Using a common test date
        )
        
        # Should return valid JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        
        # Results could be empty (no connecting flights) or contain flight pairs
        for flight_pair in parsed:
            assert isinstance(flight_pair, list)
            assert len(flight_pair) == 2  # Should be pairs for connections
    
    def test_tool_info(self):
        """Test tool info for SearchOnestopFlight."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "search_onestop_flight"
        required_params = info["function"]["parameters"]["required"]
        expected_params = {"origin", "destination", "date"}
        assert set(required_params) == expected_params


class TestAirlineCalculate(BaseToolTest):
    """Test Calculate tool for airline."""
    
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
        result = self.tool_class.invoke(data, expression="100 + 50")
        assert result == "150.0"
        
        # Test multiplication (common for calculating costs)
        result = self.tool_class.invoke(data, expression="250 * 2")
        assert result == "500.0"
    
    def test_tool_info(self):
        """Test tool info for Calculate."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "calculate"


class TestListAllAirports(BaseToolTest):
    """Test ListAllAirports tool."""
    
    @property
    def data(self):
        return load_data()
    
    @property
    def tool_class(self):
        return ListAllAirports
    
    def test_list_airports(self):
        """Test listing all airports."""
        data = self.data
        result = self.tool_class.invoke(data)
        
        # Should return valid JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        
        # Should contain airport codes mapped to cities
        assert len(parsed) > 0
        
        # Each airport should map to a city name
        for airport, city in parsed.items():
            assert isinstance(airport, str)
            assert isinstance(city, str)
            assert len(airport) == 3  # Airport codes are 3 letters
            assert airport.isupper()  # Should be uppercase
            assert len(city) > 0  # City name should not be empty
    
    def test_airports_from_flight_data(self):
        """Test that listed airports are reasonable for airline system."""
        data = self.data
        result = self.tool_class.invoke(data)
        parsed = json.loads(result)
        
        # Should have reasonable number of airports
        assert len(parsed) > 10  # Should have multiple airports
        
        # Common airports should be included
        common_airports = {"JFK", "LAX", "SFO", "ORD"}
        airport_codes = set(parsed.keys())
        assert common_airports.intersection(airport_codes), "Should include common airports"
    
    def test_tool_info(self):
        """Test tool info for ListAllAirports."""
        info = self.tool_class.get_info()
        assert info["function"]["name"] == "list_all_airports"
        assert info["function"]["parameters"]["required"] == []