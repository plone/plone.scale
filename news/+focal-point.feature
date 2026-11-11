Add a ``focal_point`` option to ``scaleImage`` and ``scalePILImage``: the modes that crop keep that point of the image in view, instead of the center.
It is an ``(x, y)`` tuple or ``"x,y"`` string with fractions of the width and height.
@jladage
