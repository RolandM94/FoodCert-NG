from rest_framework.test import APITestCase

from apps.locations.models import LGA, State, Ward


def data(response):
    return response.data.get("data", response.data) if isinstance(response.data, dict) else response.data


class LocationEndpointTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.lga = LGA.objects.create(state=self.state, name="Ikeja")
        Ward.objects.create(lga=self.lga, name="Ward A")

    def test_states_are_publicly_listed(self):
        response = self.client.get("/api/states/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data(response)[0]["name"], "Lagos")

    def test_state_lgas_endpoint_lists_lgas_for_state(self):
        response = self.client.get(f"/api/states/{self.state.id}/lgas/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data(response)[0]["name"], "Ikeja")

    def test_lga_and_ward_indexes_are_available(self):
        lga_response = self.client.get("/api/lgas/")
        ward_response = self.client.get("/api/wards/")

        self.assertEqual(lga_response.status_code, 200)
        self.assertEqual(ward_response.status_code, 200)
        self.assertEqual(str(data(lga_response)[0]["state"]), str(self.state.id))
        self.assertEqual(str(data(ward_response)[0]["lga"]), str(self.lga.id))
