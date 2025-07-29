import yaml
from pathlib import Path

class TaxRules:
    def __init__(self, financial_year="fy_24_25"):
        self.financial_year = financial_year
        self._load_rules()

    def _load_rules(self):
        """Loads rules from the YAML file for the specified financial year."""
        rules_path = Path(__file__).parent / "tax_rules.yaml"
        try:
            with open(rules_path, 'r') as f:
                all_rules = yaml.safe_load(f)
            self.rules = all_rules.get(self.financial_year)
            if not self.rules:
                raise ValueError(f"Rules for financial year '{self.financial_year}' not found in tax_rules.yaml")
        except FileNotFoundError:
            raise FileNotFoundError(f"tax_rules.yaml not found in the directory: {rules_path.parent}")
        except Exception as e:
            raise e

    def get_slabs(self, regime):
        """Returns the tax slabs for a given regime ('old' or 'new')."""
        return self.rules.get(f"{regime}_regime_slabs", [])

    def get_deduction_limit(self, section, key=None):
        """Returns the limit for a specific deduction section."""
        section_data = self.rules.get("deductions", {}).get(section)
        if isinstance(section_data, dict):
            return section_data.get(key) if key else section_data.get("limit")
        return section_data

    def get_cess_rate(self):
        """Returns the health and education cess rate."""
        return self.rules.get("cess_rate", 0.0)

# Create a single instance to be used across the application
tax_rules_engine = TaxRules()