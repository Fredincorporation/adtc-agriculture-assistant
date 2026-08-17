import sqlite3
import pickle
import os
from sentence_transformers import SentenceTransformer
from rag_engine import DB_PATH, init_db

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Define crops with distinct, specialized agronomic topics
CROP_MATRIX = [
    # ==================== ANNUALS ====================
    {
        "crop": "Maize",
        "category": "Annuals - Pan-African",
        "topics": {
            "Planting & Spacing": "Sow at onset of main rains. Spacing: 75cm between rows x 25cm between hills (53,333 plants/ha). Seed depth: 3-5cm. Seed rate: 20-25 kg/ha.",
            "Fertilizer & Soil": "Basal application: NPK 15-15-15 at 200 kg/ha at planting or 2 weeks post-emergence. Top-dressing: Urea at 100 kg/ha at 5-6 weeks during weeding or knee-high stage.",
            "Pest Management": "Fall Armyworm (Spodoptera frugiperda): Monitor whorls weekly. Apply emamectin benzoate, chlorantraniliprole, or neem oil extract directly into whorls at early instar stages.",
            "Disease Control": "Maize Streak Virus (MSV): Vector is leafhopper (Cicadulina). Plant MSV-resistant hybrids (e.g., SC 637). Rogue infected plants early.",
            "Harvest & Storage": "Harvest when cobs drop and grain moisture falls below 13%. Shell and dry to 12% moisture. Treat stored grain with actellic super dust to prevent maize weevil (Sitophilus zeamais)."
        }
    },
    {
        "crop": "Cassava",
        "category": "Perennials / Biennials - West & Central Africa",
        "topics": {
            "Planting & Cuttings": "Plant healthy stem cuttings (20-25cm long with 5-7 nodes) slanting or horizontally at 1m x 1m spacing (10,000 plants/ha). Plant at start of rainy season.",
            "Fertilizer & Soil": "Thrives in sandy loam soils pH 5.5-6.5. Apply NPK 15-15-15 at 300 kg/ha or NPK 12-12-17 at 8-12 weeks post-planting. High Potassium requirement.",
            "Disease Control": "Cassava Mosaic Disease (CMD) & Cassava Brown Streak Disease (CBSD): Use disease-free certified cuttings or resistant varieties (e.g., TME 419, TMS 30572). Control whitefly vectors.",
            "Pest Management": "Cassava Green Mite (CGM) & Mealybug: Biological control using predatory mites (Typhlodromalus aripo). Avoid excessive synthetic pyrethroids.",
            "Harvesting & Processing": "Harvest roots between 9 and 18 months depending on variety. Process within 48 hours into gari, fufu, or high-quality cassava flour (HQCF) to prevent physiological deterioration."
        }
    },
    {
        "crop": "Cowpea",
        "category": "Annuals - West & East Africa",
        "topics": {
            "Planting & Spacing": "Sow in July-August in dry savannas. Spacing: 75cm x 20cm (erect varieties) or 75cm x 30cm (spreading varieties). Seed rate: 20-25 kg/ha.",
            "Fertilizer & Soil": "Fixes atmospheric nitrogen. Requires single basal Single Super Phosphate (SSP) at 100 kg/ha to stimulate root nodulation. Minimal Nitrogen fertilizer needed.",
            "Pest Management": "Pod Borer (Maruca vitrata) & Aphids: Major economic pest. Spray neem seed extract or cypermethrin at flower bud initiation, 50% flowering, and podding stages.",
            "Harvest & Storage": "Harvest mature dry pods manually before shattering. Solarize seeds under black plastic sheeting or treat with triple-layer PICS bags to kill cowpea bruchids (Callosobruchus maculatus)."
        }
    },
    {
        "crop": "Yam",
        "category": "Annuals - West African Yam Belt",
        "topics": {
            "Planting & Preparation": "Plant clean seed tubers/setts (200-400g) in mounds or high ridges spaced 1m x 1m between November and March. Treat setts with wood ash or fungicide solution.",
            "Staking & Care": "Stake early with 2-3m tall bamboo or timber poles to maximize photosynthetic leaf exposure. Weed regularly during first 3-4 months.",
            "Disease Management": "Yam Anthracnose (Colletotrichum gloeosporioides): Causes leaf necrosis and vine dieback. Spray copper hydroxide or mancozeb at early disease onset; use resistant varieties.",
            "Harvesting & Barn Storage": "Harvest 7-9 months after planting when leaves yellow and wither. Store whole undamaged tubers in traditional shade-ventilated yam barns on raised wooden racks."
        }
    },
    {
        "crop": "Teff",
        "category": "Annuals - East Africa (Horn of Africa)",
        "topics": {
            "Planting & Seedbed": "Requires fine, firm, compacted seedbed. Broadcast seeds at 10-15 kg/ha or row plant at 20cm spacing in July-August.",
            "Fertilizer Management": "Apply NPS/DAP at 100 kg/ha at sowing. Top-dress Urea at 50-100 kg/ha depending on rainfall and soil fertility to prevent crop lodging.",
            "Weed Control": "Critically sensitive to weed competition during early growth. Apply 2,4-D herbicide or conduct two manual hand weedings at 2 and 4 weeks post-emergence.",
            "Harvesting": "Harvest when panicles turn straw-colored (90-120 days). Thresh manually or mechanically immediately after field drying to prevent grain shattering losses."
        }
    },
    {
        "crop": "Groundnut",
        "category": "Annuals - Southern & West Africa",
        "topics": {
            "Planting & Spacing": "Sow at onset of rains at 45cm x 10cm spacing (220,000 plants/ha). Seed depth: 5cm. Ensure good soil-seed contact.",
            "Nutrition & Gypsum": "Requires Calcium for pod formation. Apply Gypsum (Calcium Sulfate) at 200-400 kg/ha directly over crop rows at pegging stage to eliminate empty pods ('pops').",
            "Disease Management": "Groundnut Rosette Virus: Transmitted by aphids. Prevent by planting early at high density to shade out aphids, and use resistant varieties (e.g., Samnut 22).",
            "Aflatoxin Control & Harvest": "Harvest when 70-80% of inner pods show dark brown markings. Dry pods rapidly off the soil to reduce moisture below 9% to prevent Aspergillus flavus aflatoxin contamination."
        }
    },
    {
        "crop": "Tomato",
        "category": "Annuals - Pan-African Horticulture",
        "topics": {
            "Nursery & Transplanting": "Raise seedlings in nursery beds for 3-4 weeks. Transplant at 75cm x 40cm spacing onto raised beds. Water thoroughly immediately after transplanting.",
            "Fertilizer & Irrigation": "Basal NPK 15-15-15 at 200 kg/ha. Apply Calcium Nitrate top-dressing at flowering to prevent Blossom End Rot. Provide consistent drip or furrow irrigation.",
            "Pest Management": "Tomato Leafminer (Tuta absoluta): Use delta pheromone traps for monitoring. Spray Bacillus thuringiensis (Bt) or spinosad. Rotate chemical classes.",
            "Disease Control": "Early & Late Blight (Phytophthora infestans): Spray chlorothalonil or copper oxychloride preventatively during wet, humid weather. Prune lower leaves."
        }
    },
    {
        "crop": "Coffee (Arabica & Robusta)",
        "category": "Perennials - East & Central Africa",
        "topics": {
            "Spacing & Field Setup": "Arabica: 2.5m x 2.5m (highlands >1400m). Robusta: 3.0m x 3.0m (lowlands <1200m). Dig planting holes 60cm x 60cm filled with topsoil and compost.",
            "Pruning & Canopy": "Implement single-stem or multi-stem pruning after main harvest to remove old wood, suckers, and dead branches. Promotes new flowering wood.",
            "Pest & Disease Control": "Coffee Berry Borer (Hypothenemus hampei): Conduct thorough sanitation picking ('rampango') of all leftover berries. Spray copper fungicides for Coffee Rust (Hemileia vastatrix).",
            "Harvesting & Drying": "Selectively pick only fully ripe red cherries. Process via wet pulping or dry naturally on raised African drying beds to 11-12% moisture content."
        }
    },
    {
        "crop": "Cocoa",
        "category": "Perennials - West Africa",
        "topics": {
            "Shade & Planting": "Plant at 3m x 3m spacing under temporary plantain shade and permanent timber shade trees (e.g., Terminalia, Albizia). Dig holes 40cm x 40cm.",
            "Fertilizer & Maintenance": "Apply specialized Cocoa NPK (e.g., 0-23-19 or 12-24-18) at 300-400 kg/ha per year to mature bearing trees. Prune chupons regularly.",
            "Disease Control": "Black Pod Disease (Phytophthora pod rot): Spray copper-based fungicides every 3-4 weeks during wet season. Remove and bury black/diseased pods.",
            "Harvest & Fermentation": "Harvest mature orange/yellow pods every 12-14 days. Ferment beans in wooden sweat boxes or banana leaf heaps for 5-7 days before sun drying."
        }
    },
    {
        "crop": "Rice (Lowland & Upland)",
        "category": "Annuals - Pan-African",
        "topics": {
            "Planting Methods": "Lowland/Paddy: Transplant 21-day seedlings at 20cm x 20cm spacing (2-3 seedlings/hill). Upland: Direct seed in rows 20cm apart at 60-80 kg/ha seed rate.",
            "Fertilizer Management": "Basal application: NPK 15-15-15 at 200 kg/ha at land prep. Top-dressing: Split Urea (100 kg/ha total) at tillering (3 weeks) and panicle initiation (6 weeks).",
            "Weed Control": "Keep paddies flooded to 5cm depth to suppress weeds. Apply oxadiazon or propanil herbicides 14 days post-emergence in dryland systems.",
            "Harvesting": "Harvest when 80-85% of panicles turn golden yellow. Thresh immediately and dry paddy to 13-14% moisture before milling to prevent broken grains."
        }
    }
]

# Flatten crop matrix into distinct database records
EXPANDED_RECORDS = []

for item in CROP_MATRIX:
    crop_name = item["crop"]
    category = item["category"]
    for topic_name, text in item["topics"].items():
        EXPANDED_RECORDS.append({
            "crop": crop_name,
            "title": f"{crop_name} - {topic_name}",
            "topic": category,
            "content": text
        })

# Re-initialize SQLite database
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

init_db()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(f"Embedding and storing {len(EXPANDED_RECORDS)} specialized topic records...")
for record in EXPANDED_RECORDS:
    full_text = f"{record['crop']} ({record['topic']}) - {record['title']}: {record['content']}"
    emb = model.encode(full_text, normalize_embeddings=True)
    emb_blob = pickle.dumps(emb)
    
    cursor.execute("""
        INSERT INTO knowledge_base (crop, title, topic, content, embedding)
        VALUES (?, ?, ?, ?, ?)
    """, (record["crop"], record["title"], record["topic"], record["content"], emb_blob))

conn.commit()
conn.close()

print(f"[✓] Knowledge Base successfully re-seeded with {len(EXPANDED_RECORDS)} individual agronomic topic vectors!")
