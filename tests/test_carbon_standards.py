import unittest
from pydantic import ValidationError
from sentinel.guard import ProductCarbonFootprintISO14067, OrganizationalGHGISO14064

class TestCarbonStandards(unittest.TestCase):
    def test_iso14067_standard_product_pass(self):
        # Test full life cycle processing passing correctly for a standard consumer product under ISO 14067
        payload = {
            "raw_material_kg": 10.5,
            "production_processing_kwh": 25.0,
            "distribution_transport_km": 150.0,
            "end_of_life_disposal_kg": 2.0
        }
        pcf = ProductCarbonFootprintISO14067(**payload)
        total_co2e = pcf.get_total_pcf_co2e()
        self.assertGreater(total_co2e, 0)

        # Verify immutability
        with self.assertRaises((ValidationError, TypeError)):
            pcf.raw_material_kg = 20.0

    def test_iso14064_corporate_boundary_pass(self):
        # Test corporate boundary auditing tracking Scope 1, 2, and 3 inputs under ISO 14064
        payload = {
            "scope1_direct_combustion_liters": 100.0,
            "scope2_indirect_electricity_kwh": 500.0,
            "scope3_value_chain_emissions_co2e": 1200.0
        }
        org_ghg = OrganizationalGHGISO14064(**payload)
        self.assertEqual(org_ghg.scope1_direct_combustion_liters, 100.0)

        # Verify immutability
        with self.assertRaises((ValidationError, TypeError)):
            org_ghg.scope1_direct_combustion_liters = 200.0

    def test_iso14067_missing_parameters_breach(self):
        # Assert that any missing boundary parameters raises an explicit ValidationError with an 'AUDIT COMPLIANCE BREACH' flag
        payload = {
            "raw_material_kg": 10.5,
            "production_processing_kwh": 25.0
            # Missing distribution_transport_km and end_of_life_disposal_kg
        }
        with self.assertRaises(ValidationError) as cm:
            ProductCarbonFootprintISO14067(**payload)
        self.assertIn('AUDIT COMPLIANCE BREACH', str(cm.exception))

    def test_iso14064_out_of_bounds_breach(self):
        # Assert that any out-of-bounds intensity data raises an explicit ValidationError with an 'AUDIT COMPLIANCE BREACH' flag
        payload = {
            "scope1_direct_combustion_liters": 10000.0, # High values to trigger breach
            "scope2_indirect_electricity_kwh": 50000.0,
            "scope3_value_chain_emissions_co2e": 100000.0
        }
        with self.assertRaises(ValidationError) as cm:
            OrganizationalGHGISO14064(**payload)
        self.assertIn('AUDIT COMPLIANCE BREACH', str(cm.exception))

if __name__ == "__main__":
    unittest.main()
