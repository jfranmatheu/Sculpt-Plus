

def redraw_areas_of_type(context, area_type: str, region_type: str | None = None):
    for area in context.screen.areas:
        if area.type != area_type:
            continue
        if region_type is not None:
            for region in area.regions:
                if region.type != region_type:
                    continue
                region.tag_redraw()
        else:
            area.tag_redraw()
