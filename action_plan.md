# Sculpt+

**An action plan to optimize memory usage and asset importer performance.**

## Issues

1. Memory usage goes up significantly when import and load a lot of assets such as textures into the asset manager of Sculpt+.

2. Importing assets is slow, mainly because the generation of previews for thousands of assets at once, which is expensive and make load times increase heavily. Current implementation have multi-threading to generate previews (but it doesn't work for special formats such as psd, tga and tiff which some users like to use for their textures) is optimized to re-use generated previews in the asset importer modal in the asset manager of Sculpt+ (as a temporal cached data), which skips double generation. However, this is not enough for the goal of an interactive asset importer workflow.

## Proposed solutions

### Asset Importer issue

Some Keywords:

``` bash
• Async load.
• Subprocess generation.

'MT': Current Blender instance Main-Thread.
'SP': Subprocess open by [MT].
'CP': Child process opened and managed by [SP].
```

We need to first change the way we process the thumbnail generation:

[ In the case of brushes ]

PLAN A:

1. [MT] User runs an Operator that lets user select a .blend library hosting brushes and (possibly) texture data linked with brush data.
    1. User click at "Import", which runs the asset importer Operator.
    2. User confirms Operator.
    3. Load library (without importing anything) to take the name of brushes and textures, generate UUIDs for all them and save that relationship in a named txt file (which [SP] can properly find).
    4. Creates a SocketServer instance with an specified ID.
    5. Runs [SP] which opens .blend library in another process. Pass the PORT used by the socket server instance.
    6. Creates a timer handler which gets the SocketServer instance with specific ID, then tries to read any connection from the client socket in [SP].
    7. Enable the Sculpt+ asset importer Modal. Probably add some condition in the event handling of the Modal to wait until [SP] is finished... or likely check when Timer is killed due to [SP] being finished.
    8. DO NOT BLOCK the main thread here (as current version), just finish the Operator, but continue the communication with [SP] on the handler. To keep it dynamic and interactive.
2. [SP]
    1. Creates a SocketClient instance, use the PORT passed in sys.argv.
    2. Filter the images in bpy.data.brushes (both, brush icons and image textures) by file format.
    3. Split {.psd, .tga and .tiff} image datablocks in 1 or more (depending on core count) even sets, then save some temporal bpy.libraries with uuid names, store the loaded relation Name-UUID in each Image datablock so that any [CP] can know the ID of the image when writing the thumbnail back to disk at the correct place.
    4. Execute some [CP], pass the uuid name (or path) of the temporary lib in the args. They ([CP] instances) will generate thumbnails by using bpy module.
    5. Generate the thumbnails for ALL .jpg and .png image files with multithreading by using PIL/Pillow Python package.
    6. Track the opened [SP], will kill itself until all processes have finished (including its own process).

PLAN B:

- Same as Plan A, except the Timer handler and the non-blocking modal operator. Cons: we lose the interactivity. We avoid any issue with subprocess ending after user confirms the asset importer modal (unless we prevent that from happening in Plan A, which may be unfortunate. Some quick ideas: we may want to export thumbnails to /data folder instead of /temp folder; or bidirectional communication to kill generation in subprocesses, then generating remaining thumbnails somehow?).

## Thumbnail Generation

Some Keywords:

``` cmd
• Caching.
• Lazy Loading (async / coroutine).
```

1. Drawing code asks the manager to get the thumbnail for the specified item or set of items (type, ID).
2. Manager will try to retrieve the thumbnail/s data from the DB or the item itself.
   1. [Does exist] Will return the thumbnail object as usual.
   2. [Does not exits] Will use asyncio module to generate asynchronously the requiring thumbnail/s, will add a flag to the item (OR, add a set of IDs in the Manager to track them better) so that the manager knows when the thumbnail is being generated so that it returns its loading state to the drawing code.
   3. [Loading state] Will return a string remarking the loading state.
   4. [Doesn't have source] Will return the Icon ID (string) representing the item by default (eg. sculpt_tool for brush item)... Or morelikely will return None, to indicate drawing code to use the current draw thumbnail fallback instead.

So far, what is new here, is that the manager will handle the retrieving of the thumbnail data and potentially generate thumbnails for not existing thumbnail data (always that is it possible), it will also hosts the loading state of the thumbnails.

### Memory Usage

Some Keywords:

``` cmd
• Caching.
• Lazy Loading.
• Automatic cleaning.
```

- We will be using 1+ (depending on CPU cores) subprocess that will run in background to cherry-pick generate asset previews and pass via sockets drop-by-drop into the main process's asset importer modal.

Better Solution

1. Let Blender loads the images from its sources.
2. Mark those images to not have fake users.
3. Get pixel data from the imported image and pass them to the active dummy image texture (accesible via Props helper).
