/* Draw strokes in off-screen buffer. */
static bool gpencil_render_offscreen(tGPDfill *tgpf)
{
  bool is_ortho = false;
  float winmat[4][4];

  if (!tgpf->gpd) {
    return false;
  }

  /* set temporary new size */
  tgpf->bwinx = tgpf->region->winx;
  tgpf->bwiny = tgpf->region->winy;
  tgpf->brect = tgpf->region->winrct;

  /* resize region */
  tgpf->region->winrct.xmin = 0;
  tgpf->region->winrct.ymin = 0;
  tgpf->region->winrct.xmax = max_ii((int)tgpf->region->winx * tgpf->fill_factor, MIN_WINDOW_SIZE);
  tgpf->region->winrct.ymax = max_ii((int)tgpf->region->winy * tgpf->fill_factor, MIN_WINDOW_SIZE);
  tgpf->region->winx = (short)abs(tgpf->region->winrct.xmax - tgpf->region->winrct.xmin);
  tgpf->region->winy = (short)abs(tgpf->region->winrct.ymax - tgpf->region->winrct.ymin);

  /* save new size */
  tgpf->sizex = (int)tgpf->region->winx;
  tgpf->sizey = (int)tgpf->region->winy;

  char err_out[256] = "unknown";
  GPUOffScreen *offscreen = GPU_offscreen_create(
      tgpf->sizex, tgpf->sizey, true, GPU_RGBA8, err_out);
  if (offscreen == NULL) {
    printf("GPencil - Fill - Unable to create fill buffer\n");
    return false;
  }

  GPU_offscreen_bind(offscreen, true);
  uint flag = IB_rectfloat;
  ImBuf *ibuf = IMB_allocImBuf(tgpf->sizex, tgpf->sizey, 32, flag);

  rctf viewplane;
  float clip_start, clip_end;

  is_ortho = ED_view3d_viewplane_get(tgpf->depsgraph,
                                     tgpf->v3d,
                                     tgpf->rv3d,
                                     tgpf->sizex,
                                     tgpf->sizey,
                                     &viewplane,
                                     &clip_start,
                                     &clip_end,
                                     NULL);

  /* Rescale `viewplane` to fit all strokes. */
  float width = viewplane.xmax - viewplane.xmin;
  float height = viewplane.ymax - viewplane.ymin;

  float width_new = width * tgpf->zoom;
  float height_new = height * tgpf->zoom;
  float scale_x = (width_new - width) / 2.0f;
  float scale_y = (height_new - height) / 2.0f;

  viewplane.xmin -= scale_x;
  viewplane.xmax += scale_x;
  viewplane.ymin -= scale_y;
  viewplane.ymax += scale_y;

  if (is_ortho) {
    orthographic_m4(winmat,
                    viewplane.xmin,
                    viewplane.xmax,
                    viewplane.ymin,
                    viewplane.ymax,
                    -clip_end,
                    clip_end);
  }
  else {
    perspective_m4(winmat,
                   viewplane.xmin,
                   viewplane.xmax,
                   viewplane.ymin,
                   viewplane.ymax,
                   clip_start,
                   clip_end);
  }

  GPU_matrix_push_projection();
  GPU_matrix_identity_projection_set();
  GPU_matrix_push();
  GPU_matrix_identity_set();

  GPU_depth_mask(true);
  GPU_clear_color(0.0f, 0.0f, 0.0f, 0.0f);
  GPU_clear_depth(1.0f);

  ED_view3d_update_viewmat(
      tgpf->depsgraph, tgpf->scene, tgpf->v3d, tgpf->region, NULL, winmat, NULL, true);
  /* set for opengl */
  GPU_matrix_projection_set(tgpf->rv3d->winmat);
  GPU_matrix_set(tgpf->rv3d->viewmat);

  /* draw strokes */
  const float ink[4] = {1.0f, 0.0f, 0.0f, 1.0f};
  gpencil_draw_datablock(tgpf, ink);

  GPU_depth_mask(false);

  GPU_matrix_pop_projection();
  GPU_matrix_pop();

  /* create a image to see result of template */
  if (ibuf->rect_float) {
    GPU_offscreen_read_pixels(offscreen, GPU_DATA_FLOAT, ibuf->rect_float);
  }
  else if (ibuf->rect) {
    GPU_offscreen_read_pixels(offscreen, GPU_DATA_UBYTE, ibuf->rect);
  }
  if (ibuf->rect_float && ibuf->rect) {
    IMB_rect_from_float(ibuf);
  }

  tgpf->ima = BKE_image_add_from_imbuf(tgpf->bmain, ibuf, "GP_fill");
  tgpf->ima->id.tag |= LIB_TAG_DOIT;

  BKE_image_release_ibuf(tgpf->ima, ibuf, NULL);

  /* Switch back to window-system-provided frame-buffer. */
  GPU_offscreen_unbind(offscreen, true);
  GPU_offscreen_free(offscreen);

  return true;
}