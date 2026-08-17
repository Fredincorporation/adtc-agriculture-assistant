import re

class ContextGuardrail:
    def __init__(self):
        self.session_context = {}
        
        self.location_intents = ["plant", "sow", "planting", "season", "period", "rain", "when to"]
        self.crop_intents = ["fertilizer", "pest", "spacing", "disease", "yield", "harvest", "tool", "tools", "equipment", "prune"]

    def extract_known_entities(self, query: str):
        query_lower = query.lower()
        
        locations = ["nigeria", "kenya", "ghana", "uganda", "zambia", "malawi", "ethiopia", "tanzania", "sahel", "west africa", "east africa"]
        for loc in locations:
            if loc in query_lower:
                self.session_context["location"] = loc.title()
                
        crops = ["pawpaw", "paw paw", "papaya", "maize", "cassava", "cowpea", "yam", "teff", "rice", "groundnut", "tomato", "coffee", "cocoa"]
        for crop in crops:
            if crop in query_lower:
                self.session_context["crop"] = crop.title()

    def check_and_enrich(self, raw_query: str) -> str:
        self.extract_known_entities(raw_query)
        query_lower = raw_query.lower()
        
        # 1. Location slot check
        requires_location = any(intent in query_lower for intent in self.location_intents)
        if requires_location and "location" not in self.session_context:
            print("\n[ Assistant ]: Location details help provide accurate seasonal advice.")
            user_loc = input("[ Prompt ]: What country or region are you located in? ").strip()
            if user_loc:
                self.session_context["location"] = user_loc.title()

        # 2. Crop slot check
        requires_crop = any(intent in query_lower for intent in self.crop_intents)
        if requires_crop and "crop" not in self.session_context:
            print("\n[ Assistant ]: Farming advice depends on the specific crop.")
            user_crop = input("[ Prompt ]: Which crop are you asking about? ").strip()
            if user_crop:
                self.session_context["crop"] = user_crop.title()

        # Build Enriched Query using active session slots
        additions = []
        if "crop" in self.session_context and self.session_context["crop"].lower() not in query_lower:
            additions.append(f"Crop: {self.session_context['crop']}")
            
        if "location" in self.session_context and self.session_context["location"].lower() not in query_lower:
            additions.append(f"Location: {self.session_context['location']}")

        if additions:
            enriched_query = f"{raw_query} ({', '.join(additions)})"
            print(f"[ System Context Enriched ]: {enriched_query}\n")
            return enriched_query

        return raw_query
