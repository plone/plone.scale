Add a `target_format` parameter to `scaleImage` to encode a scale in another format than the original, e.g. `target_format="AVIF"`.
`pre_scale` reports the target format's mimetype.
Plain scales of AVIF originals are JPEG (PNG with alpha), a fallback for browsers without AVIF support.
@MrTango
