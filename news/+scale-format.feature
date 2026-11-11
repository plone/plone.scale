Add a ``format`` option to ``scaleImage``: convert scales to JPEG, WEBP or AVIF.
Logos, diagrams and other PNG and GIF images with few colors stay PNG, and animations keep their format.
WEBP and AVIF keep transparency.
The quality is given as for JPEG: for AVIF it is lowered by 10 percent, which still looks a bit better than JPEG.
``guess_scale_mimetype`` gives the mimetype a scale will most likely get, which the storage now uses for scales that are not generated yet.
@jladage
