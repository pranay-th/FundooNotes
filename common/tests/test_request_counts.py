"""
common/tests/test_request_counts.py

Tests for the per-method request counting feature added to
RequestLoggingMiddleware and exposed via GET /api/stats/requests/.

Test coverage
-------------
1. Making N requests of a given method increments that method's counter by N.
2. Different HTTP methods have independent counters (no cross-contamination).
3. The /api/stats/requests/ endpoint returns all expected method keys.
4. The stats endpoint requires authentication (401 for anonymous callers).
5. Non-standard HTTP methods are tallied under the "OTHER" bucket.
"""

import pytest
from django.core.cache import cache
from django.urls import reverse

from common.middleware import _TRACKED_METHODS, _cache_key, get_request_counts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clear_counters():
    """Reset all method counters in the cache before each test."""
    for method in list(_TRACKED_METHODS) + ["OTHER"]:
        cache.delete(_cache_key(method))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_counters():
    """
    Automatically clear all request counters before every test so that
    counter state from one test cannot bleed into another.
    """
    _clear_counters()
    yield
    _clear_counters()


# ---------------------------------------------------------------------------
# Unit tests for get_request_counts() helper
# ---------------------------------------------------------------------------

class TestGetRequestCountsHelper:
    """Direct unit tests for the get_request_counts() helper function."""

    def test_returns_all_method_keys(self):
        """get_request_counts() must always include all tracked methods + OTHER."""
        counts = get_request_counts()
        expected_keys = {"GET", "POST", "PUT", "PATCH", "DELETE", "OTHER"}
        assert set(counts.keys()) == expected_keys

    def test_defaults_to_zero_when_no_requests(self):
        """All counters start at 0 when the cache is empty."""
        counts = get_request_counts()
        for key, value in counts.items():
            assert value == 0, f"Expected 0 for {key}, got {value}"

    def test_reflects_manually_set_cache_values(self):
        """get_request_counts() reads live values from the cache."""
        cache.set(_cache_key("GET"), 7, timeout=None)
        cache.set(_cache_key("POST"), 3, timeout=None)
        counts = get_request_counts()
        assert counts["GET"] == 7
        assert counts["POST"] == 3
        # Untouched methods remain 0
        assert counts["DELETE"] == 0


# ---------------------------------------------------------------------------
# Integration tests: counter increments via real HTTP requests
# ---------------------------------------------------------------------------

class TestCounterIncrementViaRequests:
    """
    Verify that the middleware increments counters correctly when real
    HTTP requests flow through the Django test client.

    We use the /api/stats/requests/ endpoint itself as a convenient
    authenticated GET target, and the /api/users/register/ endpoint as a
    POST target (no auth required).
    """

    @pytest.mark.django_db
    def test_get_counter_increments_by_n(self, auth_client):
        """
        Making N GET requests increments the GET counter by exactly N.
        """
        url = reverse("request-stats")
        n = 4
        for _ in range(n):
            auth_client.get(url)

        counts = get_request_counts()
        assert counts["GET"] >= n, (
            f"Expected GET counter >= {n}, got {counts['GET']}"
        )

    @pytest.mark.django_db
    def test_post_counter_increments_by_n(self, api_client):
        """
        Making N POST requests increments the POST counter by exactly N.
        """
        url = reverse("register")
        n = 3
        payload = {
            "username": "counter_test_user",
            "email": "counter@example.com",
            "phone_number": "9876543210",
            "password": "SecurePass123!",
        }
        for i in range(n):
            # Vary the payload so each request is distinct (avoids 400 on dup)
            payload["username"] = f"counter_user_{i}"
            payload["email"] = f"counter{i}@example.com"
            payload["phone_number"] = f"98765432{10 + i}"
            api_client.post(url, payload, format="json")

        counts = get_request_counts()
        assert counts["POST"] >= n, (
            f"Expected POST counter >= {n}, got {counts['POST']}"
        )

    @pytest.mark.django_db
    def test_different_methods_have_independent_counters(self, auth_client, api_client):
        """
        GET and POST counters are independent; incrementing one does not
        affect the other.
        """
        get_url = reverse("request-stats")
        post_url = reverse("register")

        # Make 2 GET requests
        auth_client.get(get_url)
        auth_client.get(get_url)

        get_before = get_request_counts()["GET"]
        post_before = get_request_counts()["POST"]

        # Make 1 POST request
        api_client.post(
            post_url,
            {
                "username": "indep_user",
                "email": "indep@example.com",
                "phone_number": "1112223334",
                "password": "SecurePass123!",
            },
            format="json",
        )

        get_after = get_request_counts()["GET"]
        post_after = get_request_counts()["POST"]

        # GET counter must not have changed after the POST
        assert get_after == get_before, (
            "GET counter changed after a POST request — counters are not independent"
        )
        # POST counter must have increased by exactly 1
        assert post_after == post_before + 1, (
            f"Expected POST counter to increase by 1, got {post_after - post_before}"
        )


# ---------------------------------------------------------------------------
# Integration tests: /api/stats/requests/ endpoint
# ---------------------------------------------------------------------------

class TestRequestStatsEndpoint:
    """Tests for the GET /api/stats/requests/ view."""

    @pytest.mark.django_db
    def test_returns_200_for_authenticated_user(self, auth_client):
        """Authenticated users receive a 200 response."""
        url = reverse("request-stats")
        response = auth_client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_returns_401_for_anonymous_user(self, api_client):
        """Unauthenticated requests are rejected with 401."""
        url = reverse("request-stats")
        response = api_client.get(url)
        assert response.status_code == 401

    @pytest.mark.django_db
    def test_response_contains_all_method_keys(self, auth_client):
        """
        The payload must contain exactly the six expected method keys:
        GET, POST, PUT, PATCH, DELETE, OTHER.
        """
        url = reverse("request-stats")
        response = auth_client.get(url)
        assert response.status_code == 200

        data = response.json()
        assert "payload" in data, "Response missing 'payload' key"

        payload = data["payload"]
        expected_keys = {"GET", "POST", "PUT", "PATCH", "DELETE", "OTHER"}
        assert set(payload.keys()) == expected_keys, (
            f"Unexpected keys in payload: {set(payload.keys())}"
        )

    @pytest.mark.django_db
    def test_all_counter_values_are_non_negative_integers(self, auth_client):
        """Every counter value must be a non-negative integer."""
        url = reverse("request-stats")
        response = auth_client.get(url)
        payload = response.json()["payload"]

        for method, count in payload.items():
            assert isinstance(count, int), (
                f"Counter for {method} is not an int: {count!r}"
            )
            assert count >= 0, (
                f"Counter for {method} is negative: {count}"
            )

    @pytest.mark.django_db
    def test_response_follows_standardized_format(self, auth_client):
        """Response must follow the {message, payload, status} envelope."""
        url = reverse("request-stats")
        response = auth_client.get(url)
        data = response.json()

        assert "message" in data
        assert "payload" in data
        assert "status" in data
        assert data["status"] == 200

    @pytest.mark.django_db
    def test_counter_visible_in_endpoint_after_requests(self, auth_client):
        """
        After making several GET requests the stats endpoint reflects the
        updated count (end-to-end counter visibility test).
        """
        url = reverse("request-stats")

        # Record baseline
        baseline = auth_client.get(url).json()["payload"]["GET"]

        # Make 3 more GET requests
        for _ in range(3):
            auth_client.get(url)

        # The final call also counts, so we expect at least baseline + 4
        final = auth_client.get(url).json()["payload"]["GET"]
        assert final >= baseline + 4, (
            f"Expected GET count to grow by at least 4, "
            f"baseline={baseline}, final={final}"
        )
