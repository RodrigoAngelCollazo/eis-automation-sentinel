import unittest
from pydantic import ValidationError
from sentinel.guard import ProductCarbonFootprintISO14067, OrganizationalGHGISO14064, EMSAuditISO14001

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

    def test_iso14001_ems_conformance_pass(self):
        # Test that a valid ISO 14001 EMS log structure passes validation
        payload = {
            "legal_compliance_status": True,
            "environmental_aspects": {"waste_water_ph": 7.2, "solid_waste_kg": 50.0},
            "continuous_improvement_target_co2e": 5000.0,
            "current_inventory": {
                "scope1_direct_combustion_liters": 100.0,
                "scope2_indirect_electricity_kwh": 500.0,
                "scope3_value_chain_emissions_co2e": 1200.0
            }
        }
        ems = EMSAuditISO14001(**payload)
        self.assertTrue(ems.legal_compliance_status)

    def test_iso14001_ems_legal_non_conformance(self):
        # Test that legal_compliance_status set to False raises an 'ISO 14001 NON-CONFORMANCE' error
        payload = {
            "legal_compliance_status": False,
            "environmental_aspects": {"waste_water_ph": 7.2, "solid_waste_kg": 50.0},
            "continuous_improvement_target_co2e": 5000.0,
            "current_inventory": {
                "scope1_direct_combustion_liters": 100.0,
                "scope2_indirect_electricity_kwh": 500.0,
                "scope3_value_chain_emissions_co2e": 1200.0
            }
        }
        with self.assertRaises(ValidationError) as cm:
            EMSAuditISO14001(**payload)
        self.assertIn('ISO 14001 NON-CONFORMANCE', str(cm.exception))
        self.assertIn('Legal compliance status is flagged as false', str(cm.exception))

    def test_iso14001_ems_target_exceeded_non_conformance(self):
        # Test that exceeding continuous_improvement_target_co2e raises an 'ISO 14001 NON-CONFORMANCE' error
        payload = {
            "legal_compliance_status": True,
            "environmental_aspects": {"waste_water_ph": 7.2, "solid_waste_kg": 50.0},
            "continuous_improvement_target_co2e": 1000.0,
            "current_inventory": {
                "scope1_direct_combustion_liters": 100.0,
                "scope2_indirect_electricity_kwh": 500.0,
                "scope3_value_chain_emissions_co2e": 1200.0
            }
        }
        # Total emissions calculation: 100*2.68 + 500*0.45 + 1200 = 268 + 225 + 1200 = 1693
        # 1693 > 1000, should raise error
        with self.assertRaises(ValidationError) as cm:
            EMSAuditISO14001(**payload)
        self.assertIn('ISO 14001 NON-CONFORMANCE', str(cm.exception))
        self.assertIn('exceed continuous improvement target', str(cm.exception))

if __name__ == "__main__":
    unittest.main()
