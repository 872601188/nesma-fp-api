"""
NESMA Function Point Calculator
Calculates function points based on NESMA (Netherlands Software Metrics Association) method.
"""

from typing import List, Dict, Any
import math

class FunctionPointCalculator:
    def __init__(self):
        # NESMA complexity weights
        self.weights = {
            "ILF": {"Low": 7, "Average": 10, "High": 15},
            "EIF": {"Low": 5, "Average": 7, "High": 10},
            "EI": {"Low": 3, "Average": 4, "High": 6},
            "EO": {"Low": 4, "Average": 5, "High": 7},
            "EQ": {"Low": 3, "Average": 4, "High": 6}
        }
        
        # Default GSC values (all set to average = 3)
        self.default_gsc = [3] * 14
    
    def calculate(self, components: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Calculate function points from identified components.
        """
        function_points = []
        total_unadjusted = 0
        
        # Process each component type
        for component_type, items in components.items():
            for item in items:
                # Determine complexity
                complexity = self._determine_complexity(item, component_type)
                
                # Get weight
                weight = self.weights[component_type][complexity]
                
                fp_item = {
                    "type": component_type,
                    "name": item.get("name", "Unknown"),
                    "complexity": complexity,
                    "count": weight
                }
                
                function_points.append(fp_item)
                total_unadjusted += weight
        
        # Calculate Value Adjustment Factor (VAF)
        vaf = self._calculate_vaf(self.default_gsc)
        
        # Calculate adjusted function points
        adjusted_fp = total_unadjusted * vaf
        
        return {
            "function_points": function_points,
            "total_unadjusted_fp": total_unadjusted,
            "adjusted_fp": round(adjusted_fp, 2),
            "vaf": round(vaf, 2),
            "details": {
                "component_counts": {
                    "ILF": len(components.get("ILF", [])),
                    "EIF": len(components.get("EIF", [])),
                    "EI": len(components.get("EI", [])),
                    "EO": len(components.get("EO", [])),
                    "EQ": len(components.get("EQ", []))
                },
                "complexity_distribution": self._get_complexity_distribution(function_points),
                "gsc_values": self.default_gsc
            }
        }
    
    def _determine_complexity(self, component: Dict, component_type: str) -> str:
        """
        Determine complexity based on component characteristics.
        """
        hints = component.get("complexity_hints", [])
        
        # Count complexity indicators
        high_indicators = 0
        low_indicators = 0
        
        high_hints = ["complex_processing", "high_volume", "validation_required", "calculation_required"]
        low_hints = ["simple_processing"]
        
        for hint in hints:
            if hint in high_hints:
                high_indicators += 1
            elif hint in low_hints:
                low_indicators += 1
        
        # Determine complexity
        if high_indicators >= 2:
            return "High"
        elif low_indicators >= 1 and high_indicators == 0:
            return "Low"
        else:
            return "Average"
    
    def _calculate_vaf(self, gsc_values: List[int]) -> float:
        """
        Calculate Value Adjustment Factor from General System Characteristics.
        VAF = 0.65 + (SUM(GSC) / 100)
        """
        if not gsc_values or len(gsc_values) != 14:
            gsc_values = self.default_gsc
        
        gsc_sum = sum(gsc_values)
        vaf = 0.65 + (gsc_sum / 100)
        return vaf
    
    def _get_complexity_distribution(self, function_points: List[Dict]) -> Dict:
        """
        Get distribution of complexity levels.
        """
        distribution = {
            "ILF": {"Low": 0, "Average": 0, "High": 0},
            "EIF": {"Low": 0, "Average": 0, "High": 0},
            "EI": {"Low": 0, "Average": 0, "High": 0},
            "EO": {"Low": 0, "Average": 0, "High": 0},
            "EQ": {"Low": 0, "Average": 0, "High": 0}
        }
        
        for fp in function_points:
            comp_type = fp["type"]
            complexity = fp["complexity"]
            if comp_type in distribution and complexity in distribution[comp_type]:
                distribution[comp_type][complexity] += 1
        
        return distribution
    
    def calculate_with_custom_gsc(self, components: Dict, gsc_values: List[int]) -> Dict[str, Any]:
        """
        Calculate function points with custom GSC values.
        """
        result = self.calculate(components)
        
        # Recalculate with custom GSC
        vaf = self._calculate_vaf(gsc_values)
        adjusted_fp = result["total_unadjusted_fp"] * vaf
        
        result["adjusted_fp"] = round(adjusted_fp, 2)
        result["vaf"] = round(vaf, 2)
        result["details"]["gsc_values"] = gsc_values
        
        return result
    
    def estimate_effort(self, adjusted_fp: float, language_factor: str = "average") -> Dict[str, Any]:
        """
        Estimate development effort based on function points.
        """
        # Language factors (hours per FP)
        language_factors = {
            "low": 8,      # 4GL, high-level languages
            "average": 15,  # 3GL, typical languages
            "high": 25     # Assembly, low-level languages
        }
        
        factor = language_factors.get(language_factor, 15)
        total_hours = adjusted_fp * factor
        
        # Estimate team size and duration
        # Assuming average productivity
        hours_per_month = 160  # 20 working days * 8 hours
        
        # Brooks' law approximation for team sizing
        if total_hours <= 160:
            team_size = 1
            duration_months = total_hours / hours_per_month
        elif total_hours <= 640:
            team_size = 2
            duration_months = total_hours / (hours_per_month * team_size * 0.9)
        elif total_hours <= 1600:
            team_size = 4
            duration_months = total_hours / (hours_per_month * team_size * 0.8)
        else:
            team_size = 6
            duration_months = total_hours / (hours_per_month * team_size * 0.7)
        
        return {
            "total_hours": round(total_hours, 1),
            "total_days": round(total_hours / 8, 1),
            "team_size": team_size,
            "duration_months": round(duration_months, 1),
            "language_factor": factor
        }
