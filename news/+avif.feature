Add a `target_format` parameter to `scaleImage` to encode a scale in another format than the original, e.g. `target_format="AVIF"`, and a `speed` parameter for the AVIF encoder's trade-off between encoding time and file size.
`pre_scale` reports the target format's mimetype.
AVIF originals keep their format when scaled, like PNG and WEBP ones; pass `target_format="JPEG"` for a fallback.
@MrTango
