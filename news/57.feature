Pre scale: store non-random uid to prepare space for a scale.
You call ``pre_scale`` to pre-register the scale with a unique id
without actually doing any scaling with Pillow.
When you later call the ``scale`` method, the scale is generated.
You can still call ``scale`` directly without first calling ``pre_scale``.
[maurits]
