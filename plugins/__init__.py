try:
    from .plugin import AivonPlugin
    plugin = AivonPlugin()
    plugin.register()
except Exception as e:
    import logging
    root = logging.getLogger()
    root.debug(repr(e))
