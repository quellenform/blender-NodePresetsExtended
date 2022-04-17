# Node Presets (Extended)

This is a modified version of the original add-on [Node Presets](https://docs.blender.org/manual/en/latest/addons/node/node_presets.html) written by *Campbell Barton*.

## What was changed?

- It includes the correction of a bug in the bundled version of Blender 3.1:
*Error message: `location: <unknown location>:-1`*
- Added file paths for different node types so that you can distinguish between *Shader/Texturing*, *Compositing* and *Geometry*
- The nodes are displayed sorted by name
- The nodes can only be selected if a root node is also present

## Installation & Usage
- Open Blender and go to Preferences then the Add-ons tab
- Click `Node` and disable the original Add-on `Node: Node Presets` first!
- Then enable `Node: Node Presets Extended`
- Set the file path to the folders containing the blend files with your node groups. Each directory or folder can have multiple blend-files and all node groups they contain will be available in the appropriate areas
- All node groups found in the files are then accessible in the corresponding areas via the menu `node editors --> Add --> Template`

> **Note**: Node Groups whose name starts with an underscore are NOT included!

More details can be found at [blender.stackexchange.com](https://blender.stackexchange.com/a/260854/145249).