# examples/redis_memory_plugin.py
"""
Example of registering a custom scheme via import side-effect.
Usage:
  adk-webx --memory-service "redis://localhost:6379/0?ttl=300"            --plugin python:examples.redis_memory_plugin
"""

from adk_service_plugins.service_loader import register_scheme


def _factory(parsed, qs):
    # Example: your own class here
    class RedisMemoryService:
        def __init__(self, url: str, **kwargs):
            self.url = url
            self.kwargs = kwargs

        def __repr__(self):
            return f"<RedisMemoryService {self.url} {self.kwargs}>"

    return RedisMemoryService(url=parsed.geturl(), **qs)


register_scheme("memory", "redis", _factory)
