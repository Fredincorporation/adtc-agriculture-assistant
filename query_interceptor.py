import re

class ContextGuardrail:
    def __init__(self):
        self.session_context = {}

        self.location_intents = ["plant", "sow", "planting", "season", "period", "rain", "when to"]
        self.crop_intents = ["fertilizer", "pest", "spacing", "disease", "yield", "harvest", "tool", "tools", "equipment", "prune"]

        # All 54 UN-recognized African countries
        self.known_locations = [
            "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi",
            "Cabo Verde", "Cameroon", "Central African Republic", "Chad", "Comoros",
            "Congo", "Democratic Republic of the Congo", "Congo-Brazzaville",
            "Congo-Kinshasa", "Cote d'Ivoire", "Ivory Coast", "Djibouti", "Egypt",
            "Equatorial Guinea", "Eritrea", "Eswatini", "Swaziland", "Ethiopia",
            "Gabon", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Kenya",
            "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali",
            "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger",
            "Nigeria", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles",
            "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan",
            "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe",
            "Sahel", "West Africa", "East Africa", "Central Africa", "Southern Africa", "North Africa"
        ]

        # Regex patterns with strict word boundaries (\b)
        self.known_crops = [
            # Cereals & Grains
            r"\bmaize\b", r"\bcorn\b", r"\bcassava\b", r"\bcowpeas?\b", r"\byams?\b", r"\bteff\b",
            r"\brice\b", r"\bgroundnuts?\b", r"\bpeanuts?\b", r"\bsorghum\b", r"\bmillet\b",
            r"\bfonio\b", r"\bwheat\b", r"\bbarley\b", r"\boats\b", r"\brye\b",

            # Roots, Tubers & Pulses
            r"\bsweet potat(o|oes)\b", r"\bpotat(o|oes)\b", r"\birish potat(o|oes)\b",
            r"\bcocoyam\b", r"\btaro\b", r"\btannia\b", r"\bpigeon peas?\b", r"\bbambara groundnut\b",
            r"\bsoybeans?\b", r"\bfaba beans?\b", r"\bchickpeas?\b", r"\blentils?\b",
            r"\bdry beans?\b", r"\bhyacinth beans?\b", r"\blablab\b", r"\bvelvet beans?\b", r"\bbroad beans?\b",

            # Cash & Plantation Crops
            r"\bcoffee\b", r"\bcocoa\b", r"\bcacao\b", r"\btea\b", r"\bcotton\b", r"\bcashews?\b",
            r"\bsugarcane\b", r"\brubber\b", r"\btobacco\b", r"\boil palm\b", r"\bpalm oil\b",
            r"\bsesame\b", r"\bsunflowers?\b", r"\bsisal\b", r"\bkenaf\b", r"\bpyrethrum\b", r"\bkola nuts?\b",

            # Fruits & Nuts
            r"\bpawpaws?\b", r"\bpapayas?\b", r"\bmango(es)?\b", r"\bplantains?\b", r"\bbananas?\b",
            r"\bcitrus\b", r"\boranges?\b", r"\bpineapples?\b", r"\bguavas?\b", r"\bavocados?\b",
            r"\bwatermelons?\b", r"\bdate palms?\b", r"\bdates\b", r"\bfigs?\b", r"\bolives?\b",
            r"\bgrapes?\b", r"\bgrapefruits?\b", r"\bmacadamia\b", r"\bcoconuts?\b", r"\bapples?\b", r"\bpeaches?\b",

            # Vegetables & Spices
            r"\btomat(o|oes)\b", r"\bonions?\b", r"\bokra\b", r"\bgarden eggs?\b", r"\beggplants?\b",
            r"\bpeppers?\b", r"\bchili\b", r"\bcabbages?\b", r"\bcauliflowers?\b", r"\bcucumbers?\b",
            r"\bgingers?\b", r"\bgarlics?\b", r"\bturmeric\b", r"\bcloves?\b", r"\bvanilla\b", r"\bcardamoms?\b"
        ]

        self.crop_synonyms = {
            "corn": "Maize",
            "tomatoes": "Tomato",
            "yams": "Yam",
            "sweet potatoes": "Sweet Potato",
            "peanuts": "Groundnut",
            "peanut": "Groundnut",
            "groundnuts": "Groundnut",
            "bananas": "Banana",
            "plantains": "Plantain",
            "dates": "Date Palm"
        }

    def extract_location(self, query: str):
        # Strategy 1: Match dynamic patterns like "in Jos, Nigeria", "around Kumasi (Ghana)", etc.
        countries_pattern = "|".join([re.escape(loc) for loc in self.known_locations])
        pattern = r'\b(?:in|around|near|at)\s+([A-Z][a-zA-Z\s]+?)\s*[,(]?\s*\b(' + countries_pattern + r')\b'
        match = re.search(pattern, query, re.IGNORECASE)

        if match:
            city = match.group(1).strip().title()
            country = match.group(2).strip().title()
            return f"{city}, {country}"

        # Fallback: Direct Country Match
        for loc in self.known_locations:
            if re.search(r'\b' + re.escape(loc) + r'\b', query, re.IGNORECASE):
                return loc

        return None

    def extract_crop(self, query: str):
        for crop_pattern in self.known_crops:
            match = re.search(crop_pattern, query, re.IGNORECASE)
            if match:
                raw_crop = match.group(0).lower()
                return self.crop_synonyms.get(raw_crop, raw_crop.title())
        return None

    def clean_previous_enrichment(self, query: str) -> str:
        # Strip trailing enrichment tags like (Crop: X, Location: Y)
        return re.sub(r'\s*\((?:Crop|Location):[^)]+\)', '', query).strip()

    def extract_known_entities(self, query: str):
        new_loc = self.extract_location(query)
        new_crop = self.extract_crop(query)

        # Active state update: override session slots when explicitly provided
        if new_loc:
            self.session_context["location"] = new_loc
        if new_crop:
            self.session_context["crop"] = new_crop

    def check_and_enrich(self, raw_query: str) -> str:
        base_query = self.clean_previous_enrichment(raw_query)
        self.extract_known_entities(base_query)
        query_lower = base_query.lower()

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
                raw_user_crop = user_crop.lower()
                self.session_context["crop"] = self.crop_synonyms.get(raw_user_crop, user_crop.title())

        # Build Enriched Query using active session slots
        additions = []
        if "crop" in self.session_context and self.session_context["crop"].lower() not in query_lower:
            additions.append(f"Crop: {self.session_context['crop']}")

        if "location" in self.session_context and self.session_context["location"].lower() not in query_lower:
            additions.append(f"Location: {self.session_context['location']}")

        if additions:
            enriched_query = f"{base_query} ({', '.join(additions)})"
            print(f"[ System Context Enriched ]: {enriched_query}\n")
            return enriched_query

        return base_query
