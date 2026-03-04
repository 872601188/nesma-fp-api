"""
NESMA Requirement Analyzer
Analyzes software requirements text to identify function point components.
"""

import re
import spacy
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Component:
    type: str  # ILF, EIF, EI, EO, EQ
    name: str
    description: str
    complexity_hints: List[str]

class RequirementAnalyzer:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if model not available
            self.nlp = None
        
        # Keywords for identifying component types
        self.ilf_keywords = [
            "database", "table", "file", "record", "entity", "data store",
            "storage", "repository", "master data", "reference data"
        ]
        
        self.eif_keywords = [
            "external file", "interface file", "shared data", "external database",
            "external table", "imported data", "referenced file"
        ]
        
        self.ei_keywords = [
            "input", "enter", "create", "add", "insert", "submit", "import",
            "load", "upload", "register", "save", "store"
        ]
        
        self.eo_keywords = [
            "output", "report", "display", "show", "export", "generate",
            "print", "notify", "send", "alert", "dashboard"
        ]
        
        self.eq_keywords = [
            "query", "search", "view", "lookup", "inquire", "retrieve",
            "fetch", "get", "find", "select", "filter"
        ]
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze requirements text and identify function point components.
        """
        sentences = self._split_sentences(text)
        
        components = {
            "ILF": [],
            "EIF": [],
            "EI": [],
            "EO": [],
            "EQ": []
        }
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Identify ILFs (Internal Logical Files)
            if any(kw in sentence_lower for kw in self.ilf_keywords):
                if not any(kw in sentence_lower for kw in self.eif_keywords):
                    component = self._extract_component(sentence, "ILF")
                    if component:
                        components["ILF"].append(component)
            
            # Identify EIFs (External Interface Files)
            if any(kw in sentence_lower for kw in self.eif_keywords):
                component = self._extract_component(sentence, "EIF")
                if component:
                    components["EIF"].append(component)
            
            # Identify EIs (External Inputs)
            if any(kw in sentence_lower for kw in self.ei_keywords):
                component = self._extract_component(sentence, "EI")
                if component:
                    components["EI"].append(component)
            
            # Identify EOs (External Outputs)
            if any(kw in sentence_lower for kw in self.eo_keywords):
                component = self._extract_component(sentence, "EO")
                if component:
                    components["EO"].append(component)
            
            # Identify EQs (External Inquiries)
            if any(kw in sentence_lower for kw in self.eq_keywords):
                component = self._extract_component(sentence, "EQ")
                if component:
                    components["EQ"].append(component)
        
        return components
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents]
        else:
            # Simple fallback
            return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    def _extract_component(self, sentence: str, component_type: str) -> Dict[str, Any]:
        """Extract component details from a sentence."""
        # Extract potential name (nouns or noun phrases)
        name = self._extract_name(sentence)
        
        # Determine complexity hints
        complexity_hints = self._determine_complexity_hints(sentence)
        
        return {
            "type": component_type,
            "name": name,
            "description": sentence,
            "complexity_hints": complexity_hints
        }
    
    def _extract_name(self, sentence: str) -> str:
        """Extract a name for the component from the sentence."""
        if self.nlp:
            doc = self.nlp(sentence)
            # Look for noun phrases
            noun_phrases = [chunk.text for chunk in doc.noun_chunks]
            if noun_phrases:
                return noun_phrases[0][:50]  # Limit length
        
        # Fallback: extract capitalized words or first few words
        words = sentence.split()
        if words:
            return " ".join(words[:3])[:50]
        return "Unknown"
    
    def _determine_complexity_hints(self, sentence: str) -> List[str]:
        """Determine complexity hints based on sentence content."""
        hints = []
        sentence_lower = sentence.lower()
        
        # Data element hints
        if any(kw in sentence_lower for kw in ["multiple", "various", "different", "several"]):
            hints.append("multiple_data_elements")
        
        if any(kw in sentence_lower for kw in ["complex", "complicated", "sophisticated"]):
            hints.append("complex_processing")
        
        if any(kw in sentence_lower for kw in ["simple", "basic", "standard"]):
            hints.append("simple_processing")
        
        if any(kw in sentence_lower for kw in ["many", "numerous", "large number"]):
            hints.append("high_volume")
        
        if any(kw in sentence_lower for kw in ["validation", "verify", "check", "validate"]):
            hints.append("validation_required")
        
        if any(kw in sentence_lower for kw in ["calculation", "compute", "calculate", "formula"]):
            hints.append("calculation_required")
        
        return hints
