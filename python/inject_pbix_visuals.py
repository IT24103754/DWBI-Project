"""
IT3101 DWBI Project - Build Full Power BI Dashboard into dwbi_project.pbix
Constructs the complete 3-page layout:
  Page 1: Executive Summary (4 KPI Cards, Revenue Line Chart, Review Distribution Pie Chart)
  Page 2: Trend Analysis (Top Categories Bar Chart, Monthly Order Volume Line Chart)
  Page 3: Interactive Analysis (State Slicer, Year Slicer, Category Slicer, Geographic Map)
"""

import zipfile
import json
import uuid
import os
import shutil

SOURCE_PBIX = 'powerbi/dwbi_project_backup.pbix'
TARGET_PBIX = 'powerbi/dwbi_project.pbix'

def make_uid():
    return uuid.uuid4().hex[:20]

def make_card(x, y, w, h, table, col, func_id=0, title=None):
    vis_id = make_uid()
    query_ref = f"{table}.{col}"
    single_vis = {
        "visualType": "card",
        "projections": {
            "Values": [{"queryRef": query_ref}]
        },
        "prototypeQuery": {
            "Version": 2,
            "From": [{"Name": "t", "Entity": table, "Type": 0}],
            "Select": [{
                "Aggregation": {
                    "Expression": {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "t"}},
                            "Property": col
                        }
                    },
                    "Function": func_id
                },
                "Name": query_ref
            }]
        }
    }
    config = {
        "name": vis_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h}}],
        "singleVisual": single_vis
    }
    return {
        "x": float(x),
        "y": float(y),
        "z": 0.0,
        "width": float(w),
        "height": float(h),
        "config": json.dumps(config, separators=(',', ':')),
        "filters": "[]"
    }

def make_line_chart(x, y, w, h, cat_table, cat_col, val_table, val_col, func_id=0):
    vis_id = make_uid()
    cat_ref = f"{cat_table}.{cat_col}"
    val_ref = f"{val_table}.{val_col}"
    
    single_vis = {
        "visualType": "lineChart",
        "projections": {
            "Category": [{"queryRef": cat_ref}],
            "Y": [{"queryRef": val_ref}]
        },
        "prototypeQuery": {
            "Version": 2,
            "From": [
                {"Name": "c", "Entity": cat_table, "Type": 0},
                {"Name": "v", "Entity": val_table, "Type": 0}
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "c"}},
                        "Property": cat_col
                    },
                    "Name": cat_ref
                },
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "v"}},
                                "Property": val_col
                            }
                        },
                        "Function": func_id
                    },
                    "Name": val_ref
                }
            ]
        }
    }
    config = {
        "name": vis_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h}}],
        "singleVisual": single_vis
    }
    return {
        "x": float(x),
        "y": float(y),
        "z": 0.0,
        "width": float(w),
        "height": float(h),
        "config": json.dumps(config, separators=(',', ':')),
        "filters": "[]"
    }

def make_bar_chart(x, y, w, h, cat_table, cat_col, val_table, val_col, func_id=0):
    vis_id = make_uid()
    cat_ref = f"{cat_table}.{cat_col}"
    val_ref = f"{val_table}.{val_col}"
    
    single_vis = {
        "visualType": "clusteredBarChart",
        "projections": {
            "Category": [{"queryRef": cat_ref}],
            "Y": [{"queryRef": val_ref}]
        },
        "prototypeQuery": {
            "Version": 2,
            "From": [
                {"Name": "c", "Entity": cat_table, "Type": 0},
                {"Name": "v", "Entity": val_table, "Type": 0}
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "c"}},
                        "Property": cat_col
                    },
                    "Name": cat_ref
                },
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "v"}},
                                "Property": val_col
                            }
                        },
                        "Function": func_id
                    },
                    "Name": val_ref
                }
            ]
        }
    }
    config = {
        "name": vis_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h}}],
        "singleVisual": single_vis
    }
    return {
        "x": float(x),
        "y": float(y),
        "z": 0.0,
        "width": float(w),
        "height": float(h),
        "config": json.dumps(config, separators=(',', ':')),
        "filters": "[]"
    }

def make_pie_chart(x, y, w, h, cat_table, cat_col, val_table, val_col, func_id=5):
    vis_id = make_uid()
    cat_ref = f"{cat_table}.{cat_col}"
    val_ref = f"{val_table}.{val_col}"
    
    single_vis = {
        "visualType": "pieChart",
        "projections": {
            "Category": [{"queryRef": cat_ref}],
            "Y": [{"queryRef": val_ref}]
        },
        "prototypeQuery": {
            "Version": 2,
            "From": [
                {"Name": "c", "Entity": cat_table, "Type": 0},
                {"Name": "v", "Entity": val_table, "Type": 0}
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "c"}},
                        "Property": cat_col
                    },
                    "Name": cat_ref
                },
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "v"}},
                                "Property": val_col
                            }
                        },
                        "Function": func_id
                    },
                    "Name": val_ref
                }
            ]
        }
    }
    config = {
        "name": vis_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h}}],
        "singleVisual": single_vis
    }
    return {
        "x": float(x),
        "y": float(y),
        "z": 0.0,
        "width": float(w),
        "height": float(h),
        "config": json.dumps(config, separators=(',', ':')),
        "filters": "[]"
    }

def make_slicer(x, y, w, h, table, col):
    vis_id = make_uid()
    ref = f"{table}.{col}"
    single_vis = {
        "visualType": "slicer",
        "projections": {
            "Values": [{"queryRef": ref}]
        },
        "prototypeQuery": {
            "Version": 2,
            "From": [{"Name": "s", "Entity": table, "Type": 0}],
            "Select": [{
                "Column": {
                    "Expression": {"SourceRef": {"Source": "s"}},
                    "Property": col
                },
                "Name": ref
            }]
        }
    }
    config = {
        "name": vis_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h}}],
        "singleVisual": single_vis
    }
    return {
        "x": float(x),
        "y": float(y),
        "z": 0.0,
        "width": float(w),
        "height": float(h),
        "config": json.dumps(config, separators=(',', ':')),
        "filters": "[]"
    }

def make_map(x, y, w, h, geo_table, lat_col, lng_col, size_table, size_col):
    vis_id = make_uid()
    lat_ref = f"{geo_table}.{lat_col}"
    lng_ref = f"{geo_table}.{lng_col}"
    size_ref = f"{size_table}.{size_col}"
    
    single_vis = {
        "visualType": "map",
        "projections": {
            "Latitude": [{"queryRef": lat_ref}],
            "Longitude": [{"queryRef": lng_ref}],
            "Size": [{"queryRef": size_ref}]
        },
        "prototypeQuery": {
            "Version": 2,
            "From": [
                {"Name": "g", "Entity": geo_table, "Type": 0},
                {"Name": "f", "Entity": size_table, "Type": 0}
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "g"}},
                        "Property": lat_col
                    },
                    "Name": lat_ref
                },
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "g"}},
                        "Property": lng_col
                    },
                    "Name": lng_ref
                },
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "f"}},
                                "Property": size_col
                            }
                        },
                        "Function": 5
                    },
                    "Name": size_ref
                }
            ]
        }
    }
    config = {
        "name": vis_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h}}],
        "singleVisual": single_vis
    }
    return {
        "x": float(x),
        "y": float(y),
        "z": 0.0,
        "width": float(w),
        "height": float(h),
        "config": json.dumps(config, separators=(',', ':')),
        "filters": "[]"
    }

def main():
    print("Reading source pbix...")
    with zipfile.ZipFile(SOURCE_PBIX, 'r') as z_in:
        files = {name: z_in.read(name) for name in z_in.namelist()}

    layout = json.loads(files['Report/Layout'].decode('utf-16-le'))
    page_w = 1920.0
    page_h = 1080.0

    # ── SECTION 1: Executive Summary ──────────────────────────
    sec1 = layout['sections'][0]
    sec1['displayName'] = "Executive Summary"
    sec1['width'] = page_w
    sec1['height'] = page_h

    sec1_visuals = [
        # Top 4 KPI Cards (x, y, w, h)
        make_card(40, 40, 430, 180, "dw fact_order_items", "price_brl", func_id=0),            # Sum Revenue
        make_card(510, 40, 430, 180, "dw fact_order_items", "order_id", func_id=4),           # Distinct Orders
        make_card(980, 40, 430, 180, "dw fact_order_items", "review_score", func_id=1),        # Avg Review
        make_card(1450, 40, 430, 180, "dw fact_order_items", "delivery_delay_days", func_id=1),# Avg Delay
        # Monthly Revenue Trend Line Chart
        make_line_chart(40, 260, 1140, 780, "dw dim_date", "month_name", "dw fact_order_items", "price_brl", func_id=0),
        # Review Distribution Donut/Pie Chart
        make_pie_chart(1220, 260, 660, 780, "dw fact_order_items", "review_score", "dw fact_order_items", "order_id", func_id=5)
    ]
    sec1['visualContainers'] = sec1_visuals

    # ── SECTION 2: Trend Analysis ─────────────────────────────
    sec2 = {
        "id": 1,
        "name": make_uid(),
        "displayName": "Trend Analysis",
        "filters": "[]",
        "ordinal": 1,
        "visualContainers": [
            # Top Categories Clustered Bar Chart
            make_bar_chart(40, 40, 1000, 1000, "dw dim_product", "category_en", "dw fact_order_items", "price_brl", func_id=0),
            # Monthly Order Count Line Chart
            make_line_chart(1080, 40, 800, 1000, "dw dim_date", "month_name", "dw fact_order_items", "order_id", func_id=4)
        ],
        "config": "{}",
        "displayOption": 1,
        "width": page_w,
        "height": page_h
    }

    # ── SECTION 3: Interactive Analysis ───────────────────────
    sec3 = {
        "id": 2,
        "name": make_uid(),
        "displayName": "Interactive Analysis",
        "filters": "[]",
        "ordinal": 2,
        "visualContainers": [
            # Slicer 1: State
            make_slicer(40, 40, 360, 300, "dw dim_customer", "state"),
            # Slicer 2: Year
            make_slicer(40, 370, 360, 280, "dw dim_date", "year"),
            # Slicer 3: Category
            make_slicer(40, 680, 360, 360, "dw dim_product", "category_en"),
            # Geographic Centroids Map
            make_map(440, 40, 1440, 1000, "dw dim_geography", "lat", "lng", "dw fact_order_items", "order_item_key")
        ],
        "config": "{}",
        "displayOption": 1,
        "width": page_w,
        "height": page_h
    }

    layout['sections'] = [sec1, sec2, sec3]
    files['Report/Layout'] = json.dumps(layout, separators=(',', ':')).encode('utf-16-le')

    print(f"Writing complete dashboard to {TARGET_PBIX}...")
    with zipfile.ZipFile(TARGET_PBIX, 'w', compression=zipfile.ZIP_DEFLATED) as z_out:
        for name, data in files.items():
            z_out.writestr(name, data)

    print(f"SUCCESS: {TARGET_PBIX} created with all 3 pages and full visuals suite!")

if __name__ == '__main__':
    main()
