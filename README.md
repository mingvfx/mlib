# Mlib
Houdini Pipeline & Automation Toolkit
A collection of robust Python tools and workflow enhancements designed to streamline daily tasks for Technical Artists and VFX professionals in Houdini. This toolkit covers network organization, cross-session node sharing, automated rendering/caching backups, and custom hotkey bindings.

🌟 Modules & Features
1. Network Automation (mlib_script.py)
A suite of functions to automate tedious node networking, grouping, and setup tasks.

Smart Null & Object Merge (create_null_objm): Instantly creates formatted output Nulls or Object Merges based on node selection. Intelligently handles Network Dot routing and automatically inherits node colors and shapes.

Attribute & Group Extraction (extract_groups / extract_path): Automatically reads Point/Primitive groups or specific attributes (e.g., path), and explodes them into neatly aligned Blast + Null node branches with color coding.

Auto Redshift ROP (geo_to_rs): Select any geometry nodes to instantly generate configured Redshift_ROP nodes in the /out context with standardized $HIP output paths and forced object bindings.

Layout Utilities: Automatically align nodes horizontally (align_nodes) or extract setups into the /obj context cleanly (create_geo).

2. CPIO Node Library Manager (cpio_manager.py)
A UI-driven system for saving, sharing, and loading Houdini node networks as .cpio packages across different sessions or team members.

H19 & H20 Auto-Compatibility: Dynamically loads PySide2 or PySide6 depending on your Houdini version.

Metadata Tracking: Generates a sidecar .json file alongside the .cpio to record the author, node count, and original network context.

Multi-Directory Scan: Configure multiple local or network paths to browse shared node packages in a clean, chronologically sorted UI.

3. Cache Auto-Backup (backup_cache.py)
A fail-safe pipeline script designed to execute before a File Cache or ROP writes to disk.

Snapshot Versioning: Automatically saves your current .hip file and creates a timestamped copy (e.g., scene_20260515_103000.hip) directly in your cache output folder.

Context-Aware: Dynamically reads the sopoutput parameter to find the target directory.

Benefit: If a simulation takes hours, you will always have the exact .hip file state that generated that specific cache right next to the .bgeo.sc files.

🛠️ Installation & Setup (Packages Method)
We recommend using Houdini's Packages system. This keeps your core preferences clean and makes it easy to update or share the toolkit.

1. Repository Structure
Clone or extract this repository to a permanent location on your drive or network server (e.g., D:/Pipeline/Mlib_Toolkit). Ensure the folder structure is organized like this:

Plaintext
Mlib_Toolkit/
├── scripts/
│   └── python/
│       ├── mlib_script.py
│       └── cpio_manager.py
└── (other files)
2. Create the Package JSON
Navigate to your Houdini user preferences directory:

Windows: Documents\houdiniXX.X\packages\

Linux/Mac: ~/houdiniXX.X/packages/
(If the packages folder does not exist, simply create it).

Inside the packages folder, create a new text file named mlib_toolkit.json and paste the following configuration. Make sure to change the "MLIB_ROOT" path to your actual repository directory:

JSON
{
    "env": [
        {
            "MLIB_ROOT": "D:/Pipeline/Mlib_Toolkit" 
        },
        {
            "HOUDINI_PATH": "$MLIB_ROOT"
        }
    ]
}
(Note: Always use forward slashes / in Houdini package paths, even on Windows).