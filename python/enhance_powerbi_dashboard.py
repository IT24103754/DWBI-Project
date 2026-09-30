import zipfile
import json
import os
import shutil

src_pbix = r'powerbi\dwbi_project_backup.pbix'
backup_copy = r'powerbi\dwbi_project_backup_original.pbix'
output_pbix = r'powerbi\dwbi_project_backup.pbix'
dwbi_pbix = r'powerbi\dwbi_project.pbix'

# 1. Create pristine backup if it doesn't already exist
if not os.path.exists(backup_copy):
    shutil.copyfile(src_pbix, backup_copy)
    print(f"Created backup: {backup_copy}")

# 2. Extract into a temp folder
temp_dir = r'powerbi\temp_extracted'
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

with zipfile.ZipFile(src_pbix, 'r') as z:
    z.extractall(temp_dir)
print("Extracted pbix contents for enhancement...")

# 3. Rename Page tabs to executive names
page_renames = {
    "484976625110958ea07e": "Executive Overview",
    "750f19401b18dca7000a": "Sales & Revenue Trends",
    "bd4fd42548346ac5066d": "Geographic Performance",
    "92cb219801e0a1d70a5b": "Logistics & Delivery"
}

for pid, new_name in page_renames.items():
    p_file = os.path.join(temp_dir, 'Report', 'definition', 'pages', pid, 'page.json')
    if os.path.exists(p_file):
        with open(p_file, 'r', encoding='utf-8') as f:
            p_data = json.load(f)
        p_data['displayName'] = new_name
        with open(p_file, 'w', encoding='utf-8') as f:
            json.dump(p_data, f, ensure_ascii=False)
        print(f"Renamed page {pid} -> {new_name}")

# 4. Enhance Visuals: Grid Layout & Professional Titles
# Helper function to add/update visual title in visualContainerObjects
def add_title(v_data, title_text):
    if 'visual' not in v_data:
        v_data['visual'] = {}
    if 'visualContainerObjects' not in v_data['visual']:
        v_data['visual']['visualContainerObjects'] = {}
    v_data['visual']['visualContainerObjects']['title'] = [
        {
            "properties": {
                "show": {
                    "expr": {
                        "Literal": {
                            "Value": "true"
                        }
                    }
                },
                "text": {
                    "expr": {
                        "Literal": {
                            "Value": f"'{title_text}'"
                        }
                    }
                }
            }
        }
    ]

# Page 1 Visuals Configuration
p1_configs = {
    "0b158af7e9078ca30974": {  # Revenue card
        "pos": {"x": 40, "y": 40, "z": 0, "height": 140, "width": 445, "tabOrder": 0},
        "title": "Total Revenue (USD)"
    },
    "58ecd5f082043710699b": {  # Total orders card
        "pos": {"x": 505, "y": 40, "z": 1000, "height": 140, "width": 445, "tabOrder": 1000},
        "title": "Total Orders & Items"
    },
    "227c86ce022b8e6e4600": {  # Avg review score card
        "pos": {"x": 970, "y": 40, "z": 2000, "height": 140, "width": 445, "tabOrder": 2000},
        "title": "Average Customer Rating (1 to 5 Stars)"
    },
    "9e123c261c0730a7a91a": {  # Avg delay card
        "pos": {"x": 1435, "y": 40, "z": 3000, "height": 140, "width": 445, "tabOrder": 3000},
        "title": "Average Delivery Latency (Days)"
    },
    "afb3ad79b0125b5ceb36": {  # Donut chart
        "pos": {"x": 40, "y": 210, "z": 4000, "height": 830, "width": 910, "tabOrder": 4000},
        "title": "Customer Satisfaction Distribution (1 to 5 Stars)"
    },
    "460c96d4b09309d6910d": {  # Clustered bar chart
        "pos": {"x": 970, "y": 210, "z": 5000, "height": 830, "width": 910, "tabOrder": 5000},
        "title": "Order Fulfillment & Delivery Status Breakdown"
    }
}

# Page 2 Visuals Configuration
p2_configs = {
    "1707b80ed79824057b8e": {  # Sales by category
        "pos": {"x": 40, "y": 40, "z": 0, "height": 470, "width": 910, "tabOrder": 0},
        "title": "Top Revenue by Product Category (English)"
    },
    "380bf9da9604c1702b21": {  # Freight cost by payment type
        "pos": {"x": 970, "y": 40, "z": 1000, "height": 470, "width": 910, "tabOrder": 1000},
        "title": "Freight Logistics Cost by Payment Method"
    },
    "3aef9c7be2dec28234c6": {  # Monthly revenue trend line
        "pos": {"x": 40, "y": 535, "z": 2000, "height": 505, "width": 1840, "tabOrder": 2000},
        "title": "Monthly Revenue Growth & Sales Seasonality Trend"
    }
}

# Page 3 Visuals Configuration
p3_configs = {
    "53e1b14f77bd94cd30ac": {  # Slicer
        "pos": {"x": 40, "y": 40, "z": 0, "height": 460, "width": 380, "tabOrder": 0},
        "title": "Interactive Filters (Year & Payment Method)"
    },
    "9baf9eee56aba41e900a": {  # Action button
        "pos": {"x": 40, "y": 520, "z": 1000, "height": 60, "width": 380, "tabOrder": 1000}
    },
    "deaabc52dca330019013": {  # Map
        "pos": {"x": 440, "y": 40, "z": 2000, "height": 1000, "width": 780, "tabOrder": 2000},
        "title": "Geographic Sales Density Across Brazilian States"
    },
    "ae91bcdad8c46e2c971b": {  # Sales by State bar chart
        "pos": {"x": 1240, "y": 40, "z": 3000, "height": 1000, "width": 640, "tabOrder": 3000},
        "title": "Top Performing States by Gross Revenue"
    }
}

# Apply visual configurations
all_configs = {**p1_configs, **p2_configs, **p3_configs}

for root, dirs, files in os.walk(temp_dir):
    for f in files:
        if f == 'visual.json':
            v_path = os.path.join(root, f)
            vid = os.path.basename(root)
            if vid in all_configs:
                cfg = all_configs[vid]
                with open(v_path, 'r', encoding='utf-8') as jf:
                    v_data = json.load(jf)
                if 'pos' in cfg:
                    v_data['position'] = cfg['pos']
                if 'title' in cfg:
                    add_title(v_data, cfg['title'])
                with open(v_path, 'w', encoding='utf-8') as jf:
                    json.dump(v_data, jf, ensure_ascii=False)
                print(f"Enhanced visual [{vid}]: {cfg.get('title', 'Position updated')}")

# 5. Repack back into zip/pbix format
def repack_pbix(source_folder, target_file):
    with zipfile.ZipFile(target_file, 'w', zipfile.ZIP_DEFLATED) as z_out:
        for foldername, subfolders, filenames in os.walk(source_folder):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, source_folder)
                z_out.write(filepath, arcname)

repack_pbix(temp_dir, output_pbix)
print(f"Successfully updated: {output_pbix}")

# Also update dwbi_project.pbix so both have the enhanced design
shutil.copyfile(output_pbix, dwbi_pbix)
print(f"Successfully synchronized: {dwbi_pbix}")

# Clean up temp folder
shutil.rmtree(temp_dir)
print("Cleaned up temp directory. Enhancement complete!")
