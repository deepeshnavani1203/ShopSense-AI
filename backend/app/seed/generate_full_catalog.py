import json
from pathlib import Path

SEED_PATH = Path("app/seed/products.json")

def generate_catalog():
    products = []
    
    # ── 1. ELECTRONICS (50 items) ──────────────────────────────────────────────
    # 20 Laptops
    laptop_specs = [
        ("NovaBook 14 Air", "NovaBook", 48999, "Ultrabook for students and daily productivity. 16GB RAM, 512GB SSD, 1.2kg light.", ["lightweight", "student", "portable", "office"], {"ram": "16GB", "storage": "512GB SSD", "display": "14 inch FHD IPS", "weight": "1.2kg", "battery": "12 hours"}, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80"),
        ("Zenith Air 13", "Zenith", 54999, "Ultra-thin aluminum chassis, backlit keyboard, 16GB RAM, 512GB NVMe SSD.", ["lightweight", "portable", "premium", "office"], {"ram": "16GB", "storage": "512GB SSD", "display": "13.3 inch OLED", "weight": "1.1kg", "battery": "14 hours"}, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80"),
        ("PeakDrive Pro 15", "PeakDrive", 68999, "Creator laptop with RTX 3050, 32GB RAM, 1TB SSD, 100% sRGB display.", ["premium", "office", "performance", "gaming"], {"ram": "32GB", "storage": "1TB SSD", "display": "15.6 inch 2.8K", "weight": "1.8kg", "gpu": "RTX 3050"}, "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=900&q=80"),
        ("StudyLite 14 Student", "StudyLite", 32999, "Budget student laptop with Intel Core i3, 8GB RAM, 512GB SSD, 10hr battery.", ["budget", "student", "portable"], {"ram": "8GB", "storage": "512GB SSD", "display": "14 inch HD Anti-Glare", "weight": "1.4kg", "battery": "10 hours"}, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80"),
        ("SwiftEdge 16 Slim", "SwiftEdge", 62999, "OLED ultrabook with AMD Ryzen 7, 16GB RAM, 1TB SSD, 16-inch 3.2K screen.", ["premium", "lightweight", "performance"], {"ram": "16GB", "storage": "1TB SSD", "display": "16 inch 3.2K OLED", "weight": "1.3kg", "battery": "11 hours"}, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80"),
        ("GameForce Legion 16", "GameForce", 82999, "Gaming powerhouse with RTX 4060, Intel i7-13700H, 16GB DDR5, 165Hz screen.", ["gaming", "performance", "premium"], {"ram": "16GB DDR5", "storage": "1TB SSD", "display": "16 inch 165Hz WQXGA", "gpu": "RTX 4060 8GB", "weight": "2.2kg"}, "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=900&q=80"),
        ("ThinkStation WorkBook", "BizPad", 74999, "Business laptop with spill-resistant keyboard, 32GB RAM, fingerprint, TPM 2.0.", ["office", "durable", "premium"], {"ram": "32GB", "storage": "1TB SSD", "display": "14 inch WUXGA IPS", "weight": "1.35kg", "battery": "15 hours"}, "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=900&q=80"),
        ("EcoBook Bamboo Edition", "GreenTech", 42999, "Eco-friendly casing laptop with Ryzen 5, 16GB RAM, 512GB SSD, recyclable design.", ["eco", "student", "portable", "comfortable"], {"ram": "16GB", "storage": "512GB SSD", "display": "14 inch FHD", "weight": "1.25kg", "battery": "10 hours"}, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80"),
        ("AuraFlip 2-in-1 Touch", "AuraBook", 58999, "360-degree convertible laptop with active stylus pen, 16GB RAM, 512GB SSD.", ["student", "portable", "premium"], {"ram": "16GB", "storage": "512GB SSD", "display": "14 inch FHD Touchscreen", "weight": "1.4kg", "stylus": "Included"}, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80"),
        ("TitanGaming RTX 4070", "Titan", 114999, "Flagship gaming rig with RTX 4070, Core i9, 32GB RAM, 2TB SSD, 240Hz display.", ["gaming", "premium", "performance"], {"ram": "32GB DDR5", "storage": "2TB SSD", "display": "17.3 inch 240Hz QHD", "gpu": "RTX 4070 8GB", "weight": "2.6kg"}, "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=900&q=80"),
        ("CampusBook Basic 15", "StudyLite", 28999, "Everyday college laptop with Core i3, 8GB RAM, 256GB SSD, numeric keypad.", ["budget", "student", "office"], {"ram": "8GB", "storage": "256GB SSD", "display": "15.6 inch FHD", "weight": "1.6kg", "battery": "8 hours"}, "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=900&q=80"),
        ("ProStudio 16 Creator", "ProEdit", 98999, "4K calibrated display laptop, 32GB RAM, 1TB SSD, dual Thunderbolt 4 ports.", ["premium", "performance", "office"], {"ram": "32GB", "storage": "1TB SSD", "display": "16 inch 4K Mini-LED", "weight": "1.9kg", "color": "100% DCI-P3"}, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80"),
        ("SpeedBook Ultra 14", "SpeedBook", 45999, "Fast-charging Core i5 laptop with 16GB RAM, 512GB SSD, metallic finish.", ["student", "office", "portable"], {"ram": "16GB", "storage": "512GB SSD", "display": "14 inch 2K IPS", "weight": "1.3kg", "battery": "11 hours"}, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80"),
        ("AeroSlim Feather 13", "AeroTech", 51999, "Featherweight magnesium alloy laptop at just 990g. 16GB RAM, 512GB SSD.", ["lightweight", "portable", "premium"], {"ram": "16GB", "storage": "512GB SSD", "display": "13.3 inch FHD+", "weight": "990g", "battery": "13 hours"}, "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=900&q=80"),
        ("DevStation Linux Edition", "DevCore", 71999, "Pre-installed Ubuntu Linux laptop, AMD Ryzen 9, 32GB RAM, dual M.2 SSD slots.", ["performance", "office", "durable"], {"ram": "32GB", "storage": "1TB SSD", "display": "15.6 inch 2.5K 120Hz", "weight": "1.7kg", "os": "Ubuntu 24.04"}, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80"),
        ("PulseBook 15 Office", "PulseTech", 37999, "Solid office laptop with Intel Core i5, 16GB RAM, 512GB SSD, webcam privacy shutter.", ["office", "budget", "portable"], {"ram": "16GB", "storage": "512GB SSD", "display": "15.6 inch FHD Anti-Glare", "weight": "1.65kg", "battery": "9 hours"}, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80"),
        ("CyberMax 16 Gaming", "CyberMax", 65999, "Entry gaming laptop with RTX 3050, 16GB RAM, 512GB SSD, 144Hz high refresh rate.", ["gaming", "performance", "student"], {"ram": "16GB", "storage": "512GB SSD", "display": "15.6 inch 144Hz FHD", "gpu": "RTX 3050 4GB", "weight": "2.1kg"}, "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=900&q=80"),
        ("CloudLite 11 Student", "StudyLite", 19999, "Ultra-budget 11.6 inch laptop for online schooling, video lectures, and note-taking.", ["budget", "student", "lightweight"], {"ram": "8GB", "storage": "128GB eMMC", "display": "11.6 inch HD", "weight": "1.1kg", "battery": "8 hours"}, "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=900&q=80"),
        ("UltraFlex 14 Pro", "UltraFlex", 59999, "Convertible touch laptop with 360 hinge, Ryzen 7, 16GB RAM, 1TB SSD.", ["portable", "student", "premium"], {"ram": "16GB", "storage": "1TB SSD", "display": "14 inch 2.2K Touch", "weight": "1.45kg", "battery": "12 hours"}, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80"),
        ("OmniBook WorkMaster", "Omni", 87999, "High-end corporate laptop with vPro i7, 32GB RAM, 1TB SSD, 3-year warranty.", ["office", "premium", "durable"], {"ram": "32GB", "storage": "1TB SSD", "display": "14 inch 2.8K IPS", "weight": "1.3kg", "warranty": "3 Years Onsite"}, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80"),
    ]
    for idx, (name, brand, price, desc, tags, attrs, img) in enumerate(laptop_specs, 1):
        products.append({
            "product_id": f"laptop-{idx:03d}",
            "name": name,
            "brand": brand,
            "category": "electronics",
            "subcategory": "laptop",
            "price": price,
            "currency": "INR",
            "description": desc,
            "tags": tags + ["laptop", "computer"],
            "attributes": attrs,
            "use_cases": ["college", "office", "coding", "daily use"],
            "stock_status": "in_stock",
            "image": img,
            "rating": round(4.2 + (idx % 7) * 0.1, 1),
            "review_count": 80 + idx * 15,
            "dataset_source": "curated",
        })

    # 10 Smartphones & Tablets (subcategory: phone, tablet)
    phones_data = [
        ("PixelNova 10 Pro", "PixelNova", 59999, "phone", "Flagship camera phone with 108MP OIS, 120Hz LTPO AMOLED, 5000mAh battery.", ["premium", "wireless", "performance"], {"ram": "12GB", "storage": "256GB", "camera": "108MP Triple", "battery": "5000mAh", "charging": "65W Fast"}, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=80"),
        ("SwiftDial 5G Lite", "SwiftDial", 18999, "phone", "5G smartphone with 50MP AI camera, 8GB RAM, 5000mAh battery, 120Hz display.", ["budget", "wireless", "student"], {"ram": "8GB", "storage": "128GB", "camera": "50MP Dual", "battery": "5000mAh"}, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=900&q=80"),
        ("UltraOne Pro 12", "UltraOne", 42999, "phone", "Smooth performance phone with Snapdragon 8 Gen 2, 12GB RAM, 256GB storage.", ["premium", "wireless", "gaming"], {"ram": "12GB", "storage": "256GB", "battery": "5000mAh", "display": "6.7 inch AMOLED 144Hz"}, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=80"),
        ("BudgetMax 4G Entry", "ValueTech", 9999, "phone", "Reliable entry smartphone with 6.5 inch display, 5000mAh battery, dual SIM.", ["budget", "student", "casual"], {"ram": "4GB", "storage": "64GB", "battery": "5000mAh"}, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=900&q=80"),
        ("GamerPhone Apex 7", "GamerPhone", 49999, "phone", "Dedicated gaming phone with shoulder triggers, active cooling fan, 165Hz screen.", ["gaming", "performance", "wireless"], {"ram": "16GB", "storage": "256GB", "screen": "165Hz AMOLED", "battery": "6000mAh"}, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=80"),
        ("TabPro 11 Creator", "TabPro", 34999, "tablet", "11-inch 2K tablet with magnetic stylus and keyboard support, 4 quad speakers.", ["student", "portable", "office"], {"ram": "8GB", "storage": "128GB", "screen": "11 inch 2K 120Hz", "battery": "8000mAh"}, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=900&q=80"),
        ("KidsTab Safe 8", "SafeKid", 11999, "tablet", "Kid-safe tablet with shockproof bumper case, parental controls, and eye protection.", ["budget", "kids", "portable"], {"ram": "4GB", "storage": "64GB", "screen": "8 inch HD", "case": "Shockproof Rubber"}, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=900&q=80"),
        ("CinemaPad 12.4 Max", "CinemaPad", 45999, "tablet", "Large 12.4 inch OLED tablet with HDR10+, Dolby Atmos, great for movies and notes.", ["premium", "portable", "student"], {"ram": "8GB", "storage": "256GB", "screen": "12.4 inch AMOLED", "speakers": "Dolby Atmos 4x"}, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=900&q=80"),
        ("CameraMaster 50 Ultra", "LensCore", 69999, "phone", "Photographer phone with 1-inch Sony sensor, periscope 10x optical zoom lens.", ["premium", "wireless", "performance"], {"ram": "12GB", "storage": "512GB", "sensor": "1-inch Sony IMX989", "zoom": "10x Optical"}, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=80"),
        ("EverydaySmart A15", "SmartLine", 14999, "phone", "Smooth 90Hz display phone with 50MP camera, 5000mAh, clean Android experience.", ["budget", "wireless", "student"], {"ram": "6GB", "storage": "128GB", "display": "6.6 inch FHD+ 90Hz", "battery": "5000mAh"}, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=900&q=80"),
    ]
    for idx, (name, brand, price, subcat, desc, tags, attrs, img) in enumerate(phones_data, 1):
        products.append({
            "product_id": f"{subcat}-{idx:03d}",
            "name": name,
            "brand": brand,
            "category": "electronics",
            "subcategory": subcat,
            "price": price,
            "currency": "INR",
            "description": desc,
            "tags": tags + [subcat],
            "attributes": attrs,
            "use_cases": ["mobile", "daily use", "calls", "media"],
            "stock_status": "in_stock",
            "image": img,
            "rating": round(4.3 + (idx % 6) * 0.1, 1),
            "review_count": 120 + idx * 25,
            "dataset_source": "curated",
        })

    # 10 Headphones & Audio (subcategory: headphone, speaker)
    audio_data = [
        ("SonicPro Active ANC 900", "SonicPro", 8999, "headphone", "Over-ear wireless headphones with 45dB hybrid ANC and 50hr battery life.", ["wireless", "premium", "office"], {"battery": "50 hours", "anc": "45dB Hybrid", "codec": "LDAC Hi-Res", "fit": "Over-Ear"}, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80"),
        ("ClearBuds Air TWS", "ClearBuds", 2999, "headphone", "True wireless earbuds with environmental noise cancellation, IPX5 water resistance.", ["budget", "wireless", "comfortable"], {"battery": "32 hours total", "waterproof": "IPX5", "driver": "10mm Bass"}, "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=900&q=80"),
        ("StudioMaster 70 Monitor", "Audiophile", 14999, "headphone", "Wired open-back reference studio monitor headphones with neutral frequency response.", ["premium", "office", "durable"], {"impedance": "80 Ohm", "type": "Open-Back Wired", "frequency": "5Hz-35kHz"}, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80"),
        ("SportBeats Hook Earbuds", "FitAudio", 3499, "headphone", "Secure over-ear hook sport earbuds with sweat resistance and dynamic bass boost.", ["fitness", "wireless", "waterproof"], {"battery": "40 hours", "waterproof": "IPX7", "design": "Secure Earhook"}, "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=900&q=80"),
        ("BassCannon 360 Portable", "BoomSound", 3999, "speaker", "Rugged outdoor Bluetooth speaker with 360-degree sound, RGB lights, IP67 waterproof.", ["wireless", "outdoor", "waterproof"], {"battery": "16 hours", "waterproof": "IP67", "power": "24W Stereo"}, "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=80"),
        ("SoundBar Cinema 2.1", "SoundBar", 7999, "speaker", "TV soundbar with wireless down-firing subwoofer, HDMI ARC, and Dolby Digital.", ["home", "premium", "wireless"], {"power": "160W RMS", "subwoofer": "Wireless 6.5 inch", "connectivity": "HDMI ARC, Optical, Bluetooth"}, "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=80"),
        ("GamerHeadset 7.1 Surround", "RaidGamer", 4299, "headphone", "USB gaming headset with 7.1 virtual surround sound, noise-cancelling boom mic.", ["gaming", "performance", "comfortable"], {"sound": "7.1 Surround", "mic": "Retractable Noise-Cancelling", "lighting": "RGB"}, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80"),
        ("MiniPocket Bluetooth Pod", "SoundBite", 1299, "speaker", "Pocket-sized clip-on Bluetooth speaker with crisp vocal output, carabiner clip.", ["budget", "portable", "wireless"], {"battery": "8 hours", "weight": "160g", "waterproof": "Splashproof"}, "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=80"),
        ("QuietComfort Elite ANC", "SoundWave", 19999, "headphone", "Premium luxury noise-cancelling headphones with genuine leather earcups and multi-point.", ["premium", "wireless", "office"], {"battery": "35 hours", "anc": "Customizable 10 Levels", "weight": "240g"}, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80"),
        ("Neckband Pro ExtraBass", "PulseAudio", 1799, "headphone", "Magnetic neckband earphones with vibration alert, fast charging, 25-hour playtime.", ["budget", "wireless", "comfortable"], {"battery": "25 hours", "charge": "10 min = 10 hrs", "waterproof": "IPX5"}, "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=900&q=80"),
    ]
    for idx, (name, brand, price, subcat, desc, tags, attrs, img) in enumerate(audio_data, 1):
        products.append({
            "product_id": f"{subcat}-{idx:03d}",
            "name": name,
            "brand": brand,
            "category": "electronics",
            "subcategory": subcat,
            "price": price,
            "currency": "INR",
            "description": desc,
            "tags": tags + [subcat],
            "attributes": attrs,
            "use_cases": ["music", "travel", "commute", "gaming"],
            "stock_status": "in_stock",
            "image": img,
            "rating": round(4.3 + (idx % 6) * 0.1, 1),
            "review_count": 95 + idx * 30,
            "dataset_source": "curated",
        })

    # 10 Computer Accessories & Gadgets (subcategory: powerbank, smartwatch, monitor, keyboard, mouse)
    # NOTICE: Powerbanks have subcategory="powerbank", NOT laptop!
    gadgets_data = [
        ("PowerVault 20000mAh 65W", "VaultTech", 2799, "powerbank", "65W fast-charging powerbank capable of charging laptops, phones, and tablets.", ["portable", "travel", "budget"], {"capacity": "20000mAh", "output": "65W USB-C PD", "ports": "2x USB-C, 1x USB-A"}, "https://images.unsplash.com/photo-1609592424364-e4610f763f0e?auto=format&fit=crop&w=900&q=80"),
        ("PocketJuice 10000mAh Slim", "SlimPower", 1499, "powerbank", "Ultra-slim pocket 10000mAh power bank with magnetic wireless charging for phones.", ["portable", "wireless", "budget"], {"capacity": "10000mAh", "wireless": "15W MagSafe", "weight": "180g"}, "https://images.unsplash.com/photo-1609592424364-e4610f763f0e?auto=format&fit=crop&w=900&q=80"),
        ("UltraPulse GPS Smartwatch", "PulseWatch", 6999, "smartwatch", "AMOLED smartwatch with standalone GPS, Bluetooth calling, heart rate, and 7-day battery.", ["fitness", "wireless", "health"], {"battery": "7 days", "screen": "1.43 inch AMOLED", "gps": "Built-in", "waterproof": "5ATM"}, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80"),
        ("FitTrack Active Band 8", "FitTrack", 2499, "smartwatch", "Slim fitness tracker with continuous SpO2, sleep score, 14-day battery life.", ["fitness", "budget", "health"], {"battery": "14 days", "sensors": "SpO2, Heart Rate, Sleep", "waterproof": "5ATM"}, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80"),
        ("VisionEdge 27 4K Monitor", "VisionEdge", 26999, "monitor", "27-inch 4K IPS display with 65W USB-C PD hub, HDR400, factory color calibration.", ["office", "premium", "performance"], {"size": "27 inch", "resolution": "3840x2160 4K", "panel": "IPS", "hub": "65W USB-C"}, "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=900&q=80"),
        ("GameView 24 165Hz Monitor", "GameView", 12999, "monitor", "24-inch gaming monitor with 165Hz refresh rate, 1ms response, AMD FreeSync.", ["gaming", "budget", "performance"], {"size": "24 inch", "refresh": "165Hz", "response": "1ms MPRT", "sync": "FreeSync"}, "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=900&q=80"),
        ("MechKeys Pro Wireless RGB", "MechCore", 4999, "keyboard", "75% mechanical wireless keyboard with hot-swappable tactile switches, Bluetooth & 2.4G.", ["office", "gaming", "wireless"], {"switches": "Tactile Brown Hot-swap", "battery": "4000mAh", "layout": "75% Compact"}, "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=80"),
        ("ErgoVertical Silent Mouse", "ErgoFlow", 1899, "mouse", "Ergonomic vertical mouse reducing wrist strain by 57%, whisper-quiet clicks, 4000 DPI.", ["office", "comfortable", "wireless"], {"dpi": "4000 DPI Sensor", "type": "Vertical Ergonomic", "battery": "12 Months AA"}, "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=900&q=80"),
        ("SpeedMaster Gaming Mouse", "RaidGamer", 2999, "mouse", "Ultra-lightweight 58g honeycomb gaming mouse with optical sensor, paracord cable.", ["gaming", "performance", "lightweight"], {"weight": "58g", "sensor": "16000 DPI Optical", "cable": "Ultra-flexible Paracord"}, "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=900&q=80"),
        ("GaN 100W Fast Desktop Charger", "GaNCharge", 3499, "charger", "Compact 100W GaN 4-port fast wall charger for laptop, phones, and accessories.", ["portable", "office", "travel"], {"output": "100W Max GaN III", "ports": "3x USB-C, 1x USB-A", "safety": "ActiveShield 2.0"}, "https://images.unsplash.com/photo-1609592424364-e4610f763f0e?auto=format&fit=crop&w=900&q=80"),
    ]
    for idx, (name, brand, price, subcat, desc, tags, attrs, img) in enumerate(gadgets_data, 1):
        products.append({
            "product_id": f"{subcat}-{idx:03d}",
            "name": name,
            "brand": brand,
            "category": "electronics",
            "subcategory": subcat,
            "price": price,
            "currency": "INR",
            "description": desc,
            "tags": tags + [subcat],
            "attributes": attrs,
            "use_cases": ["work", "desk setup", "travel"],
            "stock_status": "in_stock",
            "image": img,
            "rating": round(4.4 + (idx % 5) * 0.1, 1),
            "review_count": 110 + idx * 20,
            "dataset_source": "curated",
        })

    # ── 2. FOOTWEAR (50 items) ─────────────────────────────────────────────────
    footwear_templates = [
        ("AeroStride Speed Run", "AeroStride", 2999, "running shoes", "Breathable mesh running shoe for daily 5k-10k runs, cushioned EVA midsole.", ["running", "lightweight", "sport"], {"size": "7-11", "sole": "High-Abrasion Rubber", "weight": "240g"}, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80"),
        ("TrailFlex Waterproof Trek", "TrailFlex", 4899, "hiking boots", "Waterproof ankle-support hiking boots with aggressive multidirectional lugs.", ["hiking", "waterproof", "durable", "outdoor"], {"size": "6-12", "waterproof": "Gore-Shield", "ankle": "Mid Ankle Support"}, "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=80"),
        ("CloudWalk Ortho Comfort", "CloudWalk", 2499, "walking shoes", "Orthopedic walking shoe with dual-density memory foam and wide toe box for bad knees.", ["comfortable", "walking", "low-impact", "joint-support"], {"size": "6-12", "insole": "Orthopedic Memory Foam", "fit": "Wide Toe Box"}, "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?auto=format&fit=crop&w=900&q=80"),
        ("UrbanKick Canvas Low", "UrbanKick", 1899, "sneakers", "Classic everyday low-top canvas sneaker with vulcanized gum sole.", ["casual", "comfortable", "student"], {"size": "6-11", "material": "100% Cotton Canvas", "style": "Low-Top"}, "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=900&q=80"),
        ("EliteOxford Genuine Leather", "FormaFlex", 4499, "formal shoes", "Full-grain Italian leather handcrafted oxford shoes with cushioned insole for corporate wear.", ["formal", "premium", "office", "leather"], {"size": "7-11", "leather": "Full-Grain Cowhide", "sole": "Leather welted"}, "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?auto=format&fit=crop&w=900&q=80"),
        ("CampusEase Slip-On", "CampusEase", 1299, "casual shoes", "Slip-on casual shoes with elastic side gusset, washable fabric upper.", ["budget", "student", "casual"], {"size": "6-11", "closure": "Slip-on", "washable": "Machine Washable"}, "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=900&q=80"),
        ("MarathonCarbon Pro Racer", "SpeedBurst", 6999, "running shoes", "Carbon-fiber plate marathon racing shoe with PEBA super-foam for maximum rebound.", ["running", "premium", "performance"], {"size": "7-11", "plate": "Full-Length Carbon", "drop": "8mm"}, "https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&w=900&q=80"),
        ("TerraTrek Sandal Strap", "TerraGrip", 1599, "sandals", "Water-resistant outdoor adventure sandal with quick-dry webbing and arch support.", ["outdoor", "casual", "budget"], {"size": "6-11", "straps": "Quick-Dry Webbing", "footbed": "Anatomical EVA"}, "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?auto=format&fit=crop&w=900&q=80"),
        ("LoaferKnit Smart Office", "SlipEase", 2299, "loafers", "Breathable knit driving loafer with flexible rubber pebble sole for semi-formal days.", ["casual", "office", "comfortable"], {"size": "6-11", "upper": "Engineered Knit", "sole": "Pebbled Driver"}, "https://images.unsplash.com/photo-1560769629-975ec94e6a86?auto=format&fit=crop&w=900&q=80"),
        ("BadKnee OrthoStep Plus", "OrthoStep", 3499, "walking shoes", "Impact-reducing walking shoe specially engineered for arthritis, knee pain, and plantar fasciitis.", ["joint-support", "low-impact", "comfortable"], {"size": "6-12", "cushioning": "Air Cushion Heel", "arch": "High Arch Support"}, "https://images.unsplash.com/photo-1603808033192-082d6919d3e1?auto=format&fit=crop&w=900&q=80"),
    ]
    # Expand to 50 footwear items
    for i in range(1, 51):
        base = footwear_templates[(i - 1) % len(footwear_templates)]
        subcat = base[3]
        price = base[2] + ((i * 170) % 1800) - 200
        if price < 799: price = 899
        products.append({
            "product_id": f"shoe-{i:03d}",
            "name": f"{base[0]} Edition {i}" if i > 10 else base[0],
            "brand": base[1],
            "category": "footwear",
            "subcategory": subcat,
            "price": int(price),
            "currency": "INR",
            "description": f"{base[4]} Premium build designed for reliable performance and comfort.",
            "tags": list(set(base[5] + [subcat.split()[0], "footwear"])),
            "attributes": {**base[6], "color": ["Black", "White", "Navy", "Olive", "Grey"][(i) % 5]},
            "use_cases": ["daily use", "office", "running", "casual"],
            "stock_status": "in_stock",
            "image": base[7],
            "rating": round(4.1 + (i % 8) * 0.1, 1),
            "review_count": 60 + i * 18,
            "dataset_source": "curated",
        })

    # ── 3. FASHION (50 items) ──────────────────────────────────────────────────
    fashion_templates = [
        ("UrbanCotton Oversized Tee", "UrbanThread", 899, "t-shirts", "Heavyweight 240 GSM combed cotton drop-shoulder oversized t-shirt.", ["casual", "student", "comfortable"], {"material": "100% Combed Cotton", "fit": "Oversized Drop Shoulder", "gsm": "240"}, "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80"),
        ("Oxford Slim Formal Shirt", "FormaFit", 1699, "shirts", "Wrinkle-resistant pinpoint Oxford formal shirt with spread collar and French placket.", ["office", "formal", "premium"], {"material": "100% Egyptian Cotton", "fit": "Slim Fit", "weave": "Oxford"}, "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=900&q=80"),
        ("FlexChino Stretch Trousers", "UrbanThread", 1999, "trousers", "4-way stretch twill chino pants with hidden zipper pocket for office and evening wear.", ["office", "casual", "comfortable"], {"material": "97% Cotton, 3% Elastane", "fit": "Tapered Chino"}, "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=80"),
        ("DenimRider Trucker Jacket", "DenimCo", 2799, "jackets", "Classic 14oz rigid denim trucker jacket with brass hardware and adjustable waist tabs.", ["casual", "durable", "street"], {"material": "100% Cotton Denim 14oz", "style": "Trucker Jacket"}, "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=900&q=80"),
        ("CozyFleece Winter Hoodie", "WarmFit", 1799, "hoodies", "Plush brushed fleece pullover hoodie with kangaroo pocket and double-lined hood.", ["casual", "comfortable", "student"], {"material": "Cotton-Poly Fleece", "weight": "360 GSM"}, "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=900&q=80"),
        ("LinenBreeze Resort Shirt", "IsleWear", 1899, "shirts", "Breathable pure linen Cuban collar short-sleeve shirt for summer and vacation.", ["casual", "summer", "lightweight"], {"material": "100% Pure French Linen", "collar": "Camp Cuban Collar"}, "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=900&q=80"),
        ("CargoPro Tactical Joggers", "UrbanTactical", 2199, "trousers", "Water-repellent ripstop cargo pants with 6 reinforced utility pockets and cuffed hems.", ["outdoor", "casual", "durable"], {"material": "Ripstop Cotton Blend", "pockets": "6 Pockets"}, "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=80"),
        ("PolarAviator Sunglasses", "SunOptics", 1499, "accessories", "Polarized UV400 classic aviator metal sunglasses with anti-glare scratch coating.", ["accessories", "premium", "summer"], {"lens": "UV400 Polarized", "frame": "Stainless Steel"}, "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=900&q=80"),
        ("MerinoWool Thermal Pullover", "Highland", 3299, "sweaters", "Ultra-fine Australian merino wool V-neck sweater, lightweight yet naturally insulating.", ["premium", "office", "comfortable"], {"material": "100% Extra Fine Merino Wool", "gauge": "12 Gauge"}, "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=900&q=80"),
        ("BisonLeather Reversible Belt", "LeatherCraft", 1199, "accessories", "Full-grain reversible leather belt (Black/Brown) with rotating brushed silver buckle.", ["office", "formal", "durable"], {"material": "Full-Grain Leather", "width": "35mm", "reversible": "Yes"}, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80"),
    ]
    for i in range(1, 51):
        base = fashion_templates[(i - 1) % len(fashion_templates)]
        subcat = base[3]
        price = base[2] + ((i * 130) % 1500) - 150
        products.append({
            "product_id": f"fashion-{i:03d}",
            "name": f"{base[0]} V{i}" if i > 10 else base[0],
            "brand": base[1],
            "category": "fashion",
            "subcategory": subcat,
            "price": int(price),
            "currency": "INR",
            "description": f"{base[4]} High quality tailoring, made for longevity and contemporary style.",
            "tags": list(set(base[5] + [subcat, "fashion"])),
            "attributes": {**base[6], "size": ["S", "M", "L", "XL", "XXL"][(i) % 5]},
            "use_cases": ["casual wear", "office", "weekend", "outing"],
            "stock_status": "in_stock",
            "image": base[7],
            "rating": round(4.2 + (i % 7) * 0.1, 1),
            "review_count": 45 + i * 14,
            "dataset_source": "curated",
        })

    # ── 4. HOME & KITCHEN (50 items) ───────────────────────────────────────────
    kitchen_templates = [
        ("CrispAir Digital Air Fryer 5.5L", "CrispAir", 4999, "air fryer", "Rapid air circulation air fryer with 8 preset cooking modes and non-stick basket.", ["kitchen", "home", "healthy"], {"capacity": "5.5 Litres", "power": "1700W", "presets": "8 Digital Modes"}, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=900&q=80"),
        ("EspressoBar 15-Bar Coffee Maker", "BaristaPro", 8499, "coffee maker", "Italian pump espresso machine with milk frother steam wand for cappuccino and latte.", ["kitchen", "premium", "coffee"], {"pressure": "15 Bar Italian Pump", "water_tank": "1.5L", "frother": "Steam Wand"}, "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?auto=format&fit=crop&w=900&q=80"),
        ("ChefBlend 1000W Mixer Grinder", "ChefBlend", 3799, "blender", "Heavy-duty mixer grinder with 3 stainless steel jars and pure copper high-torque motor.", ["kitchen", "durable", "home"], {"power": "1000W Pure Copper", "jars": "3 Stainless Steel", "warranty": "2 Years"}, "https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=900&q=80"),
        ("RapidBoil Borosilicate Kettle 1.8L", "BrewMate", 1799, "electric kettle", "Glass electric kettle with blue LED illumination, auto-shutoff and boil-dry protection.", ["kitchen", "budget", "convenience"], {"capacity": "1.8 Litres", "material": "Borosilicate Glass", "power": "1500W"}, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=900&q=80"),
        ("GraniteNonstick 4-Piece Cookware", "ChefKing", 3499, "cookware", "Tri-ply granite stone induction non-stick cookware set including fry pan, kadhai, tawa.", ["kitchen", "cookware", "durable"], {"material": "Granite Stone 5-Layer", "induction_safe": "Yes", "pieces": "4"}, "https://images.unsplash.com/photo-1584990347449-3a3641b65fd3?auto=format&fit=crop&w=900&q=80"),
        ("SmartSolo Microwave Oven 23L", "KitchenWave", 6299, "microwave", "Convection microwave oven with 30 auto-cook recipes and stainless steel interior.", ["kitchen", "home", "convenience"], {"capacity": "23 Litres", "type": "Convection", "power": "800W Microwave / 1200W Grill"}, "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?auto=format&fit=crop&w=900&q=80"),
        ("PureDrop UV+UF Water Purifier", "PureDrop", 7999, "water purifier", "6-stage RO+UV water purifier with mineral booster and 7-litre active storage tank.", ["health", "home", "kitchen"], {"filtration": "RO + UV + Mineralizer", "capacity": "7 Litres", "tds": "Up to 2000 ppm"}, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=900&q=80"),
        ("CrispyToast 4-Slice Toaster", "ToastMaster", 2199, "toaster", "Wide slot stainless steel 4-slice toaster with defrost, reheat, and 7 browning controls.", ["kitchen", "budget", "convenience"], {"slots": "4 Wide Slots", "browning": "7 Settings", "power": "1400W"}, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=900&q=80"),
        ("NutriBullet High-Speed Smoothie", "NutriCore", 4299, "blender", "Personal bullet blender with extractor blades and to-go travel cups for fitness shakes.", ["fitness", "kitchen", "healthy"], {"power": "900W High Torque", "blades": "Nutrient Extractor", "cups": "2 BPA-Free Cups"}, "https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=900&q=80"),
        ("CastIron Dutch Oven 5.2L", "HeritageCast", 3999, "cookware", "Pre-seasoned heavy cast iron Dutch oven pot with tight-fitting self-basting lid.", ["kitchen", "cookware", "durable"], {"capacity": "5.2 Litres", "material": "Pre-Seasoned Cast Iron", "oven_safe": "Up to 260C"}, "https://images.unsplash.com/photo-1584990347449-3a3641b65fd3?auto=format&fit=crop&w=900&q=80"),
    ]
    for i in range(1, 51):
        base = kitchen_templates[(i - 1) % len(kitchen_templates)]
        subcat = base[3]
        price = base[2] + ((i * 190) % 2200) - 200
        products.append({
            "product_id": f"kitchen-{i:03d}",
            "name": f"{base[0]} Model {i}" if i > 10 else base[0],
            "brand": base[1],
            "category": "home-kitchen",
            "subcategory": subcat,
            "price": int(price),
            "currency": "INR",
            "description": f"{base[4]} Premium build designed for modern kitchens and daily meal prep.",
            "tags": list(set(base[5] + [subcat.split()[0], "home", "kitchen"])),
            "attributes": {**base[6], "color": ["Silver", "Matte Black", "Stainless", "Red"][(i) % 4]},
            "use_cases": ["cooking", "breakfast", "kitchen", "daily meals"],
            "stock_status": "in_stock",
            "image": base[7],
            "rating": round(4.3 + (i % 6) * 0.1, 1),
            "review_count": 55 + i * 20,
            "dataset_source": "curated",
        })

    # ── 5. FITNESS (50 items) ──────────────────────────────────────────────────
    fitness_templates = [
        ("FlexCore High-Density Yoga Mat 8mm", "FlexCore", 1499, "yoga", "Eco-friendly non-slip TPE yoga mat with alignment lines and carrying strap.", ["fitness", "yoga", "comfortable"], {"thickness": "8mm", "material": "Eco-friendly TPE", "size": "72x24 inches"}, "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=900&q=80"),
        ("IronGrip Hex Rubber Dumbbell Pair 10kg", "IronGrip", 2999, "weights", "Cast iron hexagonal dumbbells encased in virgin rubber with knurled chrome handles.", ["fitness", "durable", "gym"], {"weight": "10kg x 2 (20kg Total)", "coating": "Virgin Rubber", "shape": "Hex Anti-Roll"}, "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=900&q=80"),
        ("PowerLoop Resistance Band 5-Set", "PowerLoop", 899, "bands", "Stackable latex resistance tubes with door anchor, handles, and ankle straps.", ["fitness", "budget", "portable"], {"resistance": "10 lbs to 150 lbs", "material": "100% Natural Latex", "pieces": "11 pcs Set"}, "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=900&q=80"),
        ("AeroBike Magnetic Exercise Cycle", "FitSpin", 12999, "cardio", "Silent magnetic resistance stationary indoor cycle with LCD console and tablet holder.", ["fitness", "cardio", "premium"], {"resistance": "8-Level Magnetic", "flywheel": "6kg", "max_user_weight": "120kg"}, "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=900&q=80"),
        ("CompactFold Walking Pad Treadmill", "WalkSmart", 21999, "cardio", "Ultra-slim under-desk foldable walking pad treadmill with remote control, 6km/h max.", ["fitness", "cardio", "office"], {"speed": "1-6 km/h", "foldable": "180 Degree Folding", "motor": "2.0 HP Silent Brushless"}, "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=900&q=80"),
        ("DeepTissue Muscle Foam Roller 45cm", "RecoveryPro", 1099, "recovery", "High-density EVA foam roller with grid texture for myofascial release and back pain relief.", ["fitness", "recovery", "joint-support"], {"length": "45cm", "material": "High-Density EVA", "core": "Reinforced PVC"}, "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=900&q=80"),
        ("ProGrip Doorway Pull-Up Bar", "FitHome", 1699, "gym", "No-screw doorway pull-up bar with locking mechanism, holds up to 200kg.", ["fitness", "gym", "durable"], {"capacity": "200kg", "installation": "No Screw Pressure Lock", "grip": "Thick Foam Padded"}, "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=900&q=80"),
        ("SpeedRope Bearing Jump Rope", "PulseFit", 599, "cardio", "Adjustable aluminum alloy speed jump rope with 360-degree ball bearings for boxing conditioning.", ["fitness", "budget", "cardio"], {"cable": "Steel Wire with PVC", "bearings": "Dual 360 Ball Bearing"}, "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=900&q=80"),
        ("CastIron Kettlebell 16kg", "IronGrip", 2499, "weights", "Solid gravity cast iron kettlebell with powder coat finish and wide flat base.", ["fitness", "gym", "durable"], {"weight": "16kg", "finish": "Matte Powder Coat", "base": "Machined Flat Base"}, "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=900&q=80"),
        ("Ventilated Gym Duffel with Shoe Tunnel", "AthleteGear", 1899, "gym bag", "Water-resistant 45L gym duffel bag with separate ventilated shoe and wet laundry compartment.", ["fitness", "travel", "durable"], {"capacity": "45 Litres", "compartment": "Ventilated Shoe Pocket", "material": "Water-Repellent Polyester"}, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80"),
    ]
    for i in range(1, 51):
        base = fitness_templates[(i - 1) % len(fitness_templates)]
        subcat = base[3]
        price = base[2] + ((i * 140) % 1800) - 100
        products.append({
            "product_id": f"fitness-{i:03d}",
            "name": f"{base[0]} Series {i}" if i > 10 else base[0],
            "brand": base[1],
            "category": "fitness",
            "subcategory": subcat,
            "price": int(price),
            "currency": "INR",
            "description": f"{base[4]} Built to withstand intense training sessions and improve personal stamina.",
            "tags": list(set(base[5] + [subcat, "fitness"])),
            "attributes": {**base[6]},
            "use_cases": ["home workout", "gym", "cardio", "strength"],
            "stock_status": "in_stock",
            "image": base[7],
            "rating": round(4.2 + (i % 7) * 0.1, 1),
            "review_count": 40 + i * 16,
            "dataset_source": "curated",
        })

    # ── 6. OUTDOOR & CAMPING (50 items) ────────────────────────────────────────
    outdoor_templates = [
        ("SummitTrek 55L Expedition Rucksack", "SummitTrek", 3999, "backpack", "Ergonomic internal frame trekking backpack with rain cover, hydration bladder pocket.", ["outdoor", "hiking", "durable"], {"capacity": "55 Litres", "frame": "Internal Aluminium Stay", "rain_cover": "Included"}, "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80"),
        ("ForestCamp Dome Tent 3-Person", "ForestCamp", 6499, "tent", "Double-layer waterproof 3000mm hydrostatic camping tent with fiberglass poles and vestibule.", ["camping", "outdoor", "waterproof"], {"capacity": "3 Persons", "waterproof": "3000mm PU Coating", "weight": "3.8kg"}, "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=80"),
        ("AlpineSleep Mummy Sleeping Bag -5C", "AlpineGear", 2899, "sleeping bag", "Cold-weather mummy sleeping bag rated to -5°C with hollow-fiber synthetic insulation.", ["outdoor", "camping", "hiking"], {"temp_rating": "-5C to +10C", "shape": "Mummy Style", "weight": "1.4kg"}, "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=80"),
        ("CarbonTrek Anti-Shock Trekking Poles", "TrailMaster", 1999, "trekking poles", "Pair of ultralight carbon-composite trekking poles with cork grips and twist-lock height adjustment.", ["hiking", "outdoor", "joint-support"], {"material": "Carbon Fiber + 7075 Aluminum", "grip": "Natural Cork", "weight": "210g each"}, "https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=900&q=80"),
        ("CampChef Windproof Butane Stove", "CampChef", 1499, "camping stove", "Compact folding portable camping gas stove with piezo electric ignition and windshield.", ["camping", "outdoor", "portable"], {"power": "3500W", "ignition": "Piezoelectric", "weight": "280g"}, "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=80"),
        ("LumenBeam 1000LM Rechargeable Headlamp", "LumenBeam", 1299, "flashlight", "IPX8 waterproof USB-C rechargeable headlamp with red night-vision mode and 120m beam.", ["outdoor", "camping", "hiking"], {"brightness": "1000 Lumens", "battery": "2600mAh Rechargeable", "waterproof": "IPX8"}, "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=80"),
        ("PureStraw Survival Water Filter", "LifePure", 999, "filtration", "Emergency personal water straw filter removes 99.999% of bacteria and microplastics.", ["outdoor", "camping", "hiking"], {"filtration": "0.1 Micron Hollow Fiber", "capacity": "4000 Litres", "weight": "65g"}, "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=80"),
        ("ChillOut Parachute Camping Hammock", "CampEasy", 1199, "hammock", "Double camping hammock made of 210T parachute nylon with tree straps and carabiners.", ["camping", "outdoor", "portable"], {"capacity": "250kg", "material": "210T Parachute Nylon", "weight": "680g"}, "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=80"),
        ("CampCook Anodized Aluminium Pot Set", "CampChef", 1799, "cookware", "Non-stick nesting lightweight camping cookware set for 2-3 people with foldable handles.", ["camping", "outdoor", "lightweight"], {"material": "Hard-Anodized Aluminum", "pieces": "8 pcs Set", "weight": "750g"}, "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=80"),
        ("HydroShield Dry Bag 20L Waterproof", "OceanPack", 799, "dry bag", "Heavy-duty 500D PVC roll-top waterproof dry bag with shoulder strap for kayaking and rain.", ["waterproof", "outdoor", "budget"], {"capacity": "20 Litres", "material": "500D PVC Tarpaulin", "closure": "Roll-Top Buckle"}, "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80"),
    ]
    for i in range(1, 51):
        base = outdoor_templates[(i - 1) % len(outdoor_templates)]
        subcat = base[3]
        price = base[2] + ((i * 150) % 2000) - 150
        products.append({
            "product_id": f"outdoor-{i:03d}",
            "name": f"{base[0]} X{i}" if i > 10 else base[0],
            "brand": base[1],
            "category": "outdoor",
            "subcategory": subcat,
            "price": int(price),
            "currency": "INR",
            "description": f"{base[4]} Expedition-tested gear designed for trails, camping, and unpredictable weather.",
            "tags": list(set(base[5] + [subcat, "outdoor"])),
            "attributes": {**base[6]},
            "use_cases": ["hiking", "trekking", "camping", "travel"],
            "stock_status": "in_stock",
            "image": base[7],
            "rating": round(4.3 + (i % 6) * 0.1, 1),
            "review_count": 35 + i * 15,
            "dataset_source": "curated",
        })

    # ── 7. BOOKS (50 items) ────────────────────────────────────────────────────
    books_data = [
        ("Atomic Habits", "James Clear", 499, "self-improvement", "Tiny Changes, Remarkable Results. The definitive guide on building good habits and breaking bad ones.", ["habits", "productivity", "study"], "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=900&q=80"),
        ("Deep Work", "Cal Newport", 449, "productivity", "Rules for Focused Success in a Distracted World. Master hard skills and achieve peak performance.", ["focus", "productivity", "study"], "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80"),
        ("The Psychology of Money", "Morgan Housel", 399, "business", "Timeless lessons on wealth, greed, and happiness. How smart people think about investing and saving.", ["finance", "investing", "business"], "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=900&q=80"),
        ("Thinking, Fast and Slow", "Daniel Kahneman", 599, "psychology", "Nobel laureate Kahneman takes us on a groundbreaking tour of the mind and the two systems that drive thinking.", ["psychology", "study", "self-improvement"], "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80"),
        ("Clean Code", "Robert C. Martin", 1199, "technology", "A Handbook of Agile Software Craftsmanship. Learn the principles of writing clean, maintainable software.", ["coding", "technology", "study"], "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80"),
        ("Zero to One", "Peter Thiel", 449, "business", "Notes on Startups, or How to Build the Future. Contrarian insights on technology and monopoly businesses.", ["startup", "business", "innovation"], "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=900&q=80"),
        ("Make Time", "Jake Knapp & John Zeratsky", 499, "productivity", "How to Focus on What Matters Every Day from the creators of Google Ventures Design Sprint.", ["productivity", "time-management", "focus"], "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80"),
        ("Designing Data-Intensive Applications", "Martin Kleppmann", 1899, "technology", "The big ideas behind reliable, scalable, and maintainable systems for engineers.", ["technology", "coding", "software"], "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80"),
        ("Meditations", "Marcus Aurelius", 299, "philosophy", "Stoic philosophy and reflections on personal virtue, resilience, and rational living.", ["philosophy", "classic", "self-improvement"], "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=900&q=80"),
        ("Shoe Dog", "Phil Knight", 499, "biography", "A Memoir by the Creator of Nike. The candid journey of building one of the world's greatest brands.", ["biography", "business", "inspiration"], "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=900&q=80"),
    ]
    for i in range(1, 51):
        base = books_data[(i - 1) % len(books_data)]
        subcat = base[3]
        price = base[2] + ((i * 35) % 400) - 40
        if price < 249: price = 299
        products.append({
            "product_id": f"book-{i:03d}",
            "name": f"{base[0]} (Special Ed. {i})" if i > 10 else base[0],
            "brand": base[1],
            "category": "books",
            "subcategory": subcat,
            "price": int(price),
            "currency": "INR",
            "description": f"{base[4]} High quality paperback edition, essential reading for curious minds.",
            "tags": list(set(base[5] + [subcat, "books", "reading"])),
            "attributes": {"format": "Paperback", "language": "English", "pages": 240 + i * 8},
            "use_cases": ["study", "reading", "gifting", "self-improvement"],
            "stock_status": "in_stock",
            "image": base[6],
            "rating": round(4.5 + (i % 5) * 0.1, 1),
            "review_count": 120 + i * 25,
            "dataset_source": "curated",
        })

    # ── 8. WALLETS & TRAVEL ACCESSORIES (50 items) ─────────────────────────────
    wallet_templates = [
        ("Apex Slim RFID Bifold Wallet", "ApexLeather", 1299, "rfid wallet", "Minimalist genuine crazy-horse leather bifold wallet with RFID blocking layer.", ["rfid", "leather", "budget", "travel"], {"material": "Crazy Horse Leather", "slots": "8 Card Slots + Cash Clip", "rfid": "Certified RFID Blocking"}, "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=900&q=80"),
        ("Titanium Slim Cardholder", "TitanHold", 1699, "cardholder", "Aerospace-grade titanium cardholder with elastic silicone cash band, holds 12 cards.", ["rfid", "compact", "premium"], {"material": "Grade 5 Titanium", "capacity": "1-12 Cards", "weight": "45g"}, "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=900&q=80"),
        ("Nomad Passport Travel Organizer", "NomadGear", 1999, "travel wallet", "Full zip-around travel wallet holding passport, boarding pass, SIM cards, and foreign cash.", ["travel", "rfid", "giftable"], {"material": "Water-Repellent Ballistic Nylon", "passport_slots": "2", "pen_holder": "Yes"}, "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=900&q=80"),
        ("UrbanSling Crossbody Bag 4L", "UrbanPack", 2499, "sling bag", "Compact daily carry sling bag with magnetic Fidlock buckle and padded tablet sleeve.", ["travel", "portable", "waterproof"], {"capacity": "4 Litres", "material": "Cordura 500D Nylon", "buckle": "Magnetic Quick-Release"}, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80"),
        ("Executive Calfskin Long Wallet", "LuxLeather", 2999, "leather wallet", "Hand-stitched full-grain calfskin breast pocket wallet with 14 card slots and checkbook sleeve.", ["leather", "premium", "formal"], {"material": "Italian Calfskin Leather", "slots": "14 Card Slots", "style": "Long Breast Pocket"}, "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=900&q=80"),
        ("AirTag Minimalist Leather Wallet", "TrackWallet", 1799, "rfid wallet", "Slim wallet with dedicated custom molded pocket for Apple AirTag tracking.", ["rfid", "leather", "compact"], {"material": "Top Grain Leather", "airtag_slot": "Molded Secure Pocket", "slots": "6 Cards"}, "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=900&q=80"),
        ("PocketPop Pop-Up Card Case", "QuickCard", 1199, "cardholder", "One-click mechanical trigger pop-up aluminum case fanning cards out for fast access.", ["compact", "budget", "rfid"], {"mechanism": "Single-Click Ejector", "casing": "Anodized Aluminum", "capacity": "6 Cards"}, "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=900&q=80"),
        ("Leather Sleeve for 14-inch Laptop", "SleeveCraft", 2199, "laptop sleeve", "Padded premium faux-suede lined leather laptop sleeve with magnetic flap closure.", ["office", "leather", "premium"], {"compatibility": "13-14 inch Laptops", "lining": "Scratch-Free Microfiber", "closure": "Dual Hidden Magnets"}, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80"),
        ("CarbonFlex Front Pocket Money Clip", "CarbonTech", 1499, "cardholder", "Real 3K carbon fiber money clip wallet holding cards and folded cash, super light.", ["compact", "rfid", "durable"], {"material": "3K Matte Carbon Fiber", "capacity": "8 Cards + 15 Bills", "weight": "28g"}, "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=900&q=80"),
        ("Heritage Trifold Coin Pocket Wallet", "HeritageLeather", 1599, "leather wallet", "Traditional trifold wallet with dedicated snap coin pouch, twin currency dividers.", ["leather", "casual", "giftable"], {"material": "Oil-Pulled Leather", "coin_pocket": "Snap Button Pouch", "slots": "9 Cards"}, "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=900&q=80"),
    ]
    for i in range(1, 51):
        base = wallet_templates[(i - 1) % len(wallet_templates)]
        subcat = base[3]
        price = base[2] + ((i * 90) % 1200) - 100
        products.append({
            "product_id": f"wallet-{i:03d}",
            "name": f"{base[0]} Mod {i}" if i > 10 else base[0],
            "brand": base[1],
            "category": "wallets",
            "subcategory": subcat,
            "price": int(price),
            "currency": "INR",
            "description": f"{base[4]} Meticulously designed for slim profile and durability.",
            "tags": list(set(base[5] + [subcat, "wallets"])),
            "attributes": {**base[6]},
            "use_cases": ["everyday carry", "travel", "office", "gifting"],
            "stock_status": "in_stock",
            "image": base[7],
            "rating": round(4.3 + (i % 6) * 0.1, 1),
            "review_count": 65 + i * 18,
            "dataset_source": "curated",
        })

    # Save to seed
    for p in products:
        p["created_at"] = "2025-01-01T00:00:00Z"
        p["updated_at"] = "2025-01-01T00:00:00Z"

    SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(products)} products across 8 categories into {SEED_PATH}!")
    
    # Check category distribution
    cat_counts = {}
    for p in products:
        c = p["category"]
        cat_counts[c] = cat_counts.get(c, 0) + 1
    print("Category breakdown:", cat_counts)

if __name__ == "__main__":
    generate_catalog()
