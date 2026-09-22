# Minecraft PCG via Machine Learning

An experimental machine learning project for **Procedural Content Generation (PCG) in Minecraft**.

The long-term goal is to build a model capable of generating complete Minecraft structures and locations from natural-language descriptions, for example:

> "Generate a large Japanese castle surrounded by a village."

> "Create a medieval fortress on top of a mountain."

> "Generate a fantasy coastal town with towers, bridges and a harbor."

The project is currently in the **data collection and preprocessing stage**. The current pipeline collects real Minecraft creations, parses `.schem` files, processes block data and prepares the dataset that will later be used to train generative models.

## Project Goal

Most procedural Minecraft generation relies on manually designed rules, templates or algorithms.

This project explores a different approach:

**learning the structure of Minecraft builds directly from data.**

The intended pipeline is:

```text
Natural-language prompt
        ↓
Text / semantic representation
        ↓
Generative ML model
        ↓
3D Minecraft block representation
        ↓
.schem file
        ↓
Playable Minecraft structure
```

Ultimately, the model should learn concepts such as:

* architectural structure
* block placement
* geometry
* symmetry
* building styles
* materials
* spatial relationships
* terrain and location composition
* relationships between textual descriptions and 3D Minecraft structures

## Current Status

> 🚧 **Work in progress**

The generative ML part of the project is not implemented yet.

Current development focuses on building the **data infrastructure required for training**.

Implemented or currently being developed:

* automated Minecraft structure collection
* `.schem` downloading
* schematic validation
* NBT parsing
* block palette extraction
* Minecraft block-state processing
* VarInt decoding experiments
* conversion between local schematic palettes and a shared block vocabulary
* structure reconstruction experiments
* extraction of project images and metadata
* automatic generation of text descriptions from structure screenshots
* preparation of `(text description, Minecraft structure)` training pairs

## Dataset Collection

Minecraft structures are currently collected from publicly available projects on **Planet Minecraft**.

The scraper:

1. Iterates through project listing pages.
2. Finds individual Minecraft projects.
3. Detects projects that provide downloadable schematics.
4. Extracts the real `.schem` download URL.
5. Downloads the schematic.
6. Collects screenshots of the structure.
7. Extracts project metadata.
8. Stores every structure in its own directory.

Example:

```text
data/
├── map1_1/
│   ├── map.schem
│   └── metadata.json
│
├── map1_2/
│   ├── map.schem
│   └── metadata.json
│
└── ...
```

A metadata file can contain information such as:

```json
{
  "images": [
    "https://..."
  ],
  "link": "https://www.planetminecraft.com/project/...",
  "page": 1,
  "map_description": "...",
  "download_link": "https://..."
}
```

## Automatic Text Descriptions

For future text-conditioned generation, Minecraft structures need textual descriptions.

The project contains an LLM/Vision pipeline that analyzes screenshots of a build together with the author's description and converts them into a short natural-language prompt.

For example, screenshots of a build could be converted into:

```text
A massive dark medieval fortress with tall stone towers, fortified walls and a central entrance surrounded by detailed battlements.
```

This makes it possible to construct training pairs similar to:

```text
TEXT
"A Japanese castle with several wooden floors and curved dark roofs"

            ↕

STRUCTURE
3D Minecraft block representation
```

The goal is to eventually train a model that learns the relationship between **language and Minecraft geometry**.

## Minecraft Schematic Processing

Minecraft `.schem` files are stored using the NBT format.

Each schematic contains information such as:

```text
Width
Height
Length
Palette
BlockData
BlockEntities
DataVersion
Version
```

The structure can be interpreted as a 3D voxel grid:

```text
X = width
Y = height
Z = length
```

where every voxel represents a Minecraft block.

Conceptually:

```text
structure[x][y][z] → block
```

Example:

```text
(10, 4, 20) → minecraft:stone_bricks
(10, 5, 20) → minecraft:oak_planks
(10, 6, 20) → minecraft:air
```

## Block Palettes

Individual schematic files use their own local block palettes.

For example:

```text
0 → minecraft:air
1 → minecraft:stone
2 → minecraft:oak_planks
```

Another schematic could assign completely different IDs:

```text
0 → minecraft:oak_planks
1 → minecraft:glass
2 → minecraft:air
```

These IDs therefore cannot be used directly as global ML classes.

The preprocessing pipeline builds a **universal Minecraft block vocabulary** where every unique block state receives a consistent ID across the dataset.

For example:

```text
minecraft:air                         → 21
minecraft:oak_planks                  → 51
minecraft:oak_log[axis=y]             → 108
minecraft:ladder[facing=south,...]    → 109
```

This representation is intended to provide a consistent vocabulary for future machine-learning models.

## Block Data Decoding

Schematic block data can use variable-length integer encoding.

The preprocessing experiments decode this representation to recover the sequence of local palette IDs.

Conceptually:

```text
Raw schematic bytes
        ↓
VarInt decoding
        ↓
Local block IDs
        ↓
Local palette
        ↓
Minecraft block names
        ↓
Universal block IDs
```

This allows structures from many different schematic files to eventually be transformed into a consistent numerical representation suitable for ML training.

## Structure Reconstruction

The project also contains experiments for converting processed 3D block representations back into Minecraft schematics.

The intended round trip is:

```text
Minecraft .schem
      ↓
NBT parsing
      ↓
3D numerical representation
      ↓
ML processing / generation
      ↓
3D block representation
      ↓
Minecraft .schem
```

Being able to reconstruct valid schematics is important because generated outputs should eventually be directly importable into Minecraft using tools such as WorldEdit.

## Planned ML Pipeline

The exact generative architecture is still experimental.

Potential directions include:

```text
Text Encoder
     ↓
Latent representation
     ↓
3D Generative Model
     ↓
Minecraft voxel structure
```

Possible model families to investigate include:

* 3D Transformers
* autoregressive voxel models
* discrete diffusion models
* hierarchical generation
* latent 3D generative models
* text-conditioned voxel generation
* structure-aware generative models

Large structures may eventually require hierarchical generation rather than predicting an entire world voxel-by-voxel at once.

For example:

```text
Prompt
  ↓
Global layout
  ↓
Buildings / regions
  ↓
Structural components
  ↓
Individual blocks
```

## Long-Term Vision

The final system should accept prompts such as:

```text
"Create a huge fantasy castle built into a snowy mountain."
```

and automatically produce:

```text
generated_castle.schem
```

which can then be imported into Minecraft.

Future generations could eventually include not only individual buildings, but larger environments such as:

* villages
* castles
* cities
* dungeons
* islands
* landscapes
* fantasy environments
* complete Minecraft locations

The broader research goal is to explore how modern generative machine learning can be applied to **3D voxel-based procedural content generation**.

## Project Structure

Current experimental structure:

```text
minecraftML/
│
├── data.py
│   └── Minecraft structure scraper and dataset collector
│
├── llm.py
│   └── Vision/LLM-based structure description generation
│
├── process_data.ipynb
│   └── Schematic parsing and preprocessing experiments
│
├── train.ipynb
│   └── ML training experiments
│
├── test.ipynb
│   └── Encoding and preprocessing tests
│
├── legacy.json
│   └── Universal Minecraft block palette
│
├── data/
│   ├── map1_1/
│   │   ├── map.schem
│   │   └── metadata.json
│   └── ...
│
└── log.log
```

The repository structure is expected to change significantly as the ML pipeline develops.

## Technologies

The project currently uses or experiments with:

```text
Python
NumPy
NBTLib
BeautifulSoup
Cloudscraper
OpenAI API
Jupyter Notebook
uvarint
mcschematic
Matplotlib
```

Main areas involved:

```text
Machine Learning
Generative AI
Procedural Content Generation
3D / Voxel Generation
Computer Vision
Natural Language Processing
Minecraft Schematic Processing
Web Data Collection
```

## Roadmap

* [x] Build Minecraft project scraper
* [x] Download `.schem` structures
* [x] Extract screenshots and metadata
* [x] Parse Minecraft NBT schematic files
* [x] Extract local block palettes
* [x] Build universal block vocabulary
* [x] Experiment with VarInt decoding
* [x] Experiment with schematic reconstruction
* [x] Build vision-based text description pipeline
* [ ] Finalize normalized dataset format
* [ ] Convert schematics into model-ready 3D tensors / tokens
* [ ] Analyze structure-size distribution
* [ ] Design training architecture
* [ ] Train first structure-generation baseline
* [ ] Add text conditioning
* [ ] Generate valid Minecraft structures
* [ ] Evaluate structural quality
* [ ] Scale generation to larger buildings
* [ ] Generate multi-building locations
* [ ] Generate complete Minecraft environments

## Research Direction

This project sits at the intersection of:

**Machine Learning × Procedural Content Generation × 3D Generation × Minecraft**

Minecraft provides an interesting environment for generative ML because the world is discrete and structured: every environment can be represented as a 3D grid of block states while still containing complex architecture and large-scale spatial relationships.

The main challenge is therefore not simply generating blocks, but learning how thousands or millions of blocks combine into **coherent, functional and visually meaningful structures**.

## Disclaimer

This is an experimental research and learning project and is currently under active development.

Minecraft structures collected from external sources remain the work of their respective creators. Any public dataset creation or redistribution should respect the original creators' licenses and the terms of the source platforms.

Minecraft is a trademark of Mojang Studios / Microsoft. This project is not affiliated with or endorsed by Mojang Studios or Microsoft.
