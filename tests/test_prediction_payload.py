import unittest

from power_outage_mlops.components.data_ingestion import parse_damage
from power_outage_mlops.payload import coerce_payload


class PredictionPayloadTests(unittest.TestCase):
    def test_parse_damage_suffixes(self):
        self.assertEqual(parse_damage("1.5M"), 1_500_000)
        self.assertEqual(parse_damage("2K"), 2_000)
        self.assertEqual(parse_damage("."), 0)

    def test_coerce_payload_numeric_fields(self):
        payload = {
            "state": "TX",
            "storm_event_count": "12",
            "saidi_minutes": "105.5",
        }
        coerced = coerce_payload(payload)
        self.assertEqual(coerced["state"], "TX")
        self.assertEqual(coerced["storm_event_count"], 12.0)
        self.assertEqual(coerced["saidi_minutes"], 105.5)


if __name__ == "__main__":
    unittest.main()
