import base64
import json
from falkordb import FalkorDB
import logzero
from logzero import logger
import hashlib
from datetime import datetime

class FalkorDBIngestor:
    def __init__(self, plugin_data):
        self.db = FalkorDB(host='localhost', port=6379, username='', password='')
        self.graph = self.db.select_graph('MyGraph')
        logzero.loglevel(logzero.DEBUG)

        self.clear_database()
        self.plugin_data = json.loads(plugin_data)
        self.file_content = self.decode_file_content()
        self.file_checksum = self.calculate_checksum(self.file_content)
        self.xrvoyageplugin_id = self.create_xrvoyageplugin_node()
        self.version_id = self.create_version_node()
        self.link_nodes()

    def calculate_checksum(self, content):
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def clear_database(self):
        query = "MATCH (n) DETACH DELETE n"
        logger.debug("Executing query: %s" % query)
        self.graph.query(query)
        logger.debug("Database cleared.")

    def decode_file_content(self):
        encoded_content = self.plugin_data['data']['object']['file']
        return base64.b64decode(encoded_content).decode('utf-8')

    def create_xrvoyageplugin_node(self):
        attributes = ', '.join(["%s: $%s" % (k, k) for k in self.plugin_data.keys() if k != 'data'])
        query = "MERGE (p:XrVoyagePlugin {name: $name}) SET p += {%s} RETURN id(p) as id" % attributes
        logger.debug("Executing query: %s" % query)
        params = {k: v for k, v in self.plugin_data.items() if k != 'data'}
        result = self.graph.query(query, params=params)
        return result.result_set[0][0]

    def create_version_node(self):
        query = "CREATE (v:Version {name: $name, updated_utc: $updated_utc, file_checksum: $file_checksum}) RETURN id(v) as id"
        logger.debug("Executing query: %s" % query)
        params = {
            'name': f"Version {self.plugin_data['updated_utc']}",
            'updated_utc': self.plugin_data['updated_utc'],
            'file_checksum': self.file_checksum
        }
        result = self.graph.query(query, params=params)
        version_id = result.result_set[0][0]
        self.link_nodes_helper(self.xrvoyageplugin_id, version_id, 'HAS_VERSION')
        return version_id

    def create_class_node(self, class_name):
        query = "MERGE (c:Class {name: $name}) RETURN id(c) as id"
        logger.debug("Executing query: %s" % query)
        result = self.graph.query(query, params={'name': class_name})
        return result.result_set[0][0]

    def create_class_update_node(self, class_name):
        query = """
        CREATE (cu:ClassUpdate {
            class_name: $class_name,
            updated_utc: $updated_utc,
            payload: $payload
        }) RETURN id(cu) as id
        """
        params = {
            'class_name': class_name,
            'updated_utc': self.plugin_data['updated_utc'],
            'payload': json.dumps(self.plugin_data)
        }
        logger.debug("Executing query: %s" % query)
        result = self.graph.query(query, params=params)
        return result.result_set[0][0]

    def create_function_node(self, function_name):
        query = "MERGE (f:Function {name: $name}) RETURN id(f) as id"
        logger.debug("Executing query: %s" % query)
        result = self.graph.query(query, params={'name': function_name})
        return result.result_set[0][0]

    def create_function_update_node(self, function_data):
        fragment = self.extract_code_fragment(function_data['line_start'], function_data['line_end'])
        checksum = self.calculate_checksum(fragment)
        
        query = """
        CREATE (fu:FunctionUpdate {
            function_name: $function_name,
            updated_utc: $updated_utc,
            line_start: $line_start,
            line_end: $line_end,
            code_fragment: $code_fragment,
            checksum: $checksum,
            status: $status,
            scope: $scope,
            is_async: $is_async
        }) RETURN id(fu) as id
        """
        
        params = {
            'function_name': function_data['name'],
            'updated_utc': self.plugin_data['updated_utc'],
            'line_start': function_data['line_start'],
            'line_end': function_data['line_end'],
            'code_fragment': fragment,
            'checksum': checksum,
            'status': function_data['status'],
            'scope': function_data['scope'],
            'is_async': function_data['async']
        }
        
        logger.debug("Executing query: %s" % query)
        result = self.graph.query(query, params=params)
        return result.result_set[0][0]

    def extract_code_fragment(self, start_line, end_line):
        lines = self.file_content.split('\n')
        fragment = '\n'.join(lines[start_line-1:end_line])
        return fragment

    def create_decorator_node(self, decorator):
        query = "MERGE (d:Decorator {name: $name, args: $args}) RETURN id(d) as id"
        params = {'name': decorator['name'], 'args': json.dumps(decorator['args'])}
        logger.debug("Executing query: %s" % query)
        result = self.graph.query(query, params=params)
        return result.result_set[0][0]

    def link_nodes_helper(self, from_id, to_id, relationship_type):
        query = "MATCH (a),(b) WHERE id(a) = $from_id AND id(b) = $to_id CREATE (a)-[:%s]->(b)" % relationship_type
        params = {'from_id': from_id, 'to_id': to_id}
        logger.debug("Executing query: %s" % query)
        self.graph.query(query, params=params)

    def link_nodes(self):
        for class_data in self.plugin_data['data']['classes']:
            class_id = self.create_class_node(class_data['class'])
            self.link_nodes_helper(self.xrvoyageplugin_id, class_id, 'HAS_CLASS')
            self.link_nodes_helper(self.version_id, class_id, 'HAS_CLASS')

            class_update_id = self.create_class_update_node(class_data['class'])
            self.link_nodes_helper(class_id, class_update_id, 'HAS_CLASS_UPDATE')
            self.link_nodes_helper(self.version_id, class_update_id, 'HAS_VERSION')

            for function_data in class_data['functions']:
                function_id = self.create_function_node(function_data['name'])
                self.link_nodes_helper(class_id, function_id, 'HAS_FUNCTION')
                self.link_nodes_helper(class_update_id, function_id, 'HAS_FUNCTION')
                self.link_nodes_helper(self.version_id, function_id, 'HAS_FUNCTION')

                function_update_id = self.create_function_update_node(function_data)
                self.link_nodes_helper(function_id, function_update_id, 'HAS_FUNCTION_UPDATE')
                self.link_nodes_helper(self.version_id, function_update_id, 'HAS_VERSION')

                for decorator in function_data.get('decorators', []):
                    decorator_id = self.create_decorator_node(decorator)
                    self.link_nodes_helper(function_id, decorator_id, 'HAS_DECORATOR')

    def get_existing_version(self):
        query = "MATCH (v:Version {file_checksum: $file_checksum}) RETURN id(v) as id"
        params = {'file_checksum': self.file_checksum}
        result = self.graph.query(query, params=params)
        return result.result_set[0][0] if result.result_set else None

    def ingest(self):
        existing_version_id = self.get_existing_version()
        if existing_version_id:
            logger.info("File content hasn't changed. Skipping ingestion.")
            return

        self.link_nodes()
        logger.info("Ingestion completed successfully.")

def main():
    plugin_data = """
{
  "_id": "666614917503b8640c903fc4",
  "data": {
    "object": {
      "file": "Y2xhc3MgWHJWb3lhZ2VQbHVnaW4gewogICAgcHJpdmF0ZSBzdGF0ZTogYW55OwogICAgcHJpdmF0ZSBsaWdodDogYW55OwogICAgcHJpdmF0ZSBzcGhlcmVQYW5lbDogYW55OwogICAgcHJpdmF0ZSBtYW5hZ2VyOiBhbnk7CiAgICBwcml2YXRlIGFuY2hvcjogYW55OwogICAgcHJpdmF0ZSBzdGF0ZURhdGFTb3VyY2U6IHN0cmluZzsKICAgIHByaXZhdGUgc3RhdGVEYXRhS2V5OiBzdHJpbmc7CgogICAgcHVibGljIGNvbnN0cnVjdG9yKCkgewogICAgICAgIHRoaXMuc2V0dXBTdGF0ZSgpOwogICAgICAgIGNvbnNvbGUubG9nKCJTdGF0ZSBpbml0aWFsaXplZCBmcm9tIHBhbmVsIGRhdGE6IiwgSlNPTi5zdHJpbmdpZnkodGhpcy5zdGF0ZSwgbnVsbCwgMikpOwogICAgICAgIHRoaXMuc2V0dXBHVUkoKTsKICAgICAgICB0aGlzLnNldHVwU2NlbmUoKTsKICAgIH0KCnByaXZhdGUgc2V0dXBTdGF0ZSgpOiB2b2lkIHsKICAgIC8vIEV4dHJhY3RpbmcgY29uZmlndXJhdGlvbnMgZnJvbSBwcmVkZWZpbmVkIG1ldGhvZHMgb3IgcGFzc2VkIGRhdGEKICAgIHRoaXMuc3RhdGVEYXRhU291cmNlID0gInNwaGVyZVY2Q29uZmlnIjsKICAgIGlmICghdGhpcy5wYW5lbCB8fCAhdGhpcy5wYW5lbC5ndWlkKSB7CiAgICAgICAgY29uc29sZS5lcnJvcigiUGFuZWwgb3IgUGFuZWwgR1VJRCBpcyBub3QgZGVmaW5lZC4iKTsKICAgICAgICByZXR1cm47CiAgICB9CiAgICB0aGlzLnN0YXRlRGF0YUtleSA9IHRoaXMuc3RhdGVEYXRhU291cmNlICsgIi0iICsgdGhpcy5wYW5lbC5ndWlkOwoKICAgIGNvbnN0IGNvbmZpZ0dVSSA9IHRoaXMuZ2V0RGF0YUJ5SWRBbmRLZXkodGhpcy5zdGF0ZURhdGFTb3VyY2UsIHRoaXMuc3RhdGVEYXRhS2V5KTsKICAgIGlmICghY29uZmlnR1VJKSB7CiAgICAgICAgY29uc29sZS5lcnJvcihgRGF0YSBub3QgZm91bmQgZm9yIGtleTogJHt0aGlzLnN0YXRlRGF0YUtleX1gKTsKICAgICAgICByZXR1cm47CiAgICB9CgogICAgdGhpcy5zdGF0ZSA9IHsKICAgICAgICBjb25maWdHVUk6IGNvbmZpZ0dVSSwKICAgICAgICBkYXRhTGlzdDogdGhpcy5nZXREYXRhQnlJZEFuZEtleSgnbGlzdC1zdGFydHJlaycsICdsaXN0JykKICAgIH07CgogICAgdGhpcy5pbml0aWFsaXplU2NlbmVQYXJhbWV0ZXJzKHRoaXMuc3RhdGUuY29uZmlnR1VJKTsKfQoKcHJpdmF0ZSBpbml0aWFsaXplU2NlbmVQYXJhbWV0ZXJzKGNvbmZpZzogYW55KTogdm9pZCB7CiAgICBjb25zb2xlLmxvZygiSW5pdGlhbGl6aW5nIHNjZW5lIHBhcmFtZXRlcnMgZnJvbSBjb25maWc6IiwgY29uZmlnKTsKICAgIGNvbmZpZy5mb2xkZXJzLmZvckVhY2goKGZvbGRlcjogYW55KSA9PiB7CiAgICAgICAgT2JqZWN0LmtleXMoZm9sZGVyLnBhcmFtZXRlcnMpLmZvckVhY2gocGFyYW1OYW1lID0+IHsKICAgICAgICAgICAgY29uc3QgcGFyYW0gPSBmb2xkZXIucGFyYW1ldGVyc1twYXJhbU5hbWVdOwogICAgICAgICAgICB0aGlzLnVwZGF0ZVNjZW5lUGFyYW1ldGVyKGZvbGRlci5pZCwgcGFyYW1OYW1lLCBwYXJhbS52YWx1ZSk7CiAgICAgICAgICAgIGNvbnNvbGUubG9nKGBQYXJhbWV0ZXIgaW5pdGlhbGl6ZWQgZm9yICR7Zm9sZGVyLmlkfSAtICR7cGFyYW1OYW1lfTogJHtwYXJhbS52YWx1ZX1gKTsKICAgICAgICB9KTsKICAgIH0pOwp9CgoKICAgIHByaXZhdGUgc2V0dXBHVUkoKTogdm9pZCB7CiAgICAgICAgY29uc3QgZ3VpID0gbmV3IEdVSSh7IHRpdGxlOiB0aGlzLnN0YXRlLmNvbmZpZ0dVSS5ndWlfbmFtZSB9KTsKICAgICAgICBjb25zdCBmb2xkZXJzID0gdGhpcy5zdGF0ZS5jb25maWdHVUkuZm9sZGVyczsKICAgICAgICBpZiAoIWZvbGRlcnMpIHsKICAgICAgICAgICAgdGhyb3cgbmV3IEVycm9yKCJQYW5lbCBkYXRhIGRvZXMgbm90IGNvbnRhaW4gJ2ZvbGRlcnMnLiIpOwogICAgICAgIH0KCiAgICAgICAgdGhpcy5zdGF0ZS5ndWkgPSBndWk7CgogICAgICAgIGZvbGRlcnMuZm9yRWFjaCgoZm9sZGVyRGF0YTogYW55KSA9PiB7CiAgICAgICAgICAgIGNvbnN0IGZvbGRlciA9IGd1aS5hZGRGb2xkZXIoZm9sZGVyRGF0YS5uYW1lKTsKICAgICAgICAgICAgY29uc3QgcGFyYW1ldGVycyA9IGZvbGRlckRhdGEucGFyYW1ldGVyczsKCiAgICAgICAgICAgIGZvciAoY29uc3QgcGFyYW0gaW4gcGFyYW1ldGVycykgewogICAgICAgICAgICAgICAgY29uc3QgcGFyYW1Db25maWcgPSBwYXJhbWV0ZXJzW3BhcmFtXTsKCiAgICAgICAgICAgICAgICB0cnkgewogICAgICAgICAgICAgICAgICAgIGlmICghcGFyYW1Db25maWcgfHwgcGFyYW1Db25maWcudmFsdWUgPT09IHVuZGVmaW5lZCkgewogICAgICAgICAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoYFBhcmFtZXRlciB2YWx1ZSBpcyB1bmRlZmluZWQgZm9yIHBhcmFtOiAke3BhcmFtfSBpbiBmb2xkZXI6ICR7Zm9sZGVyRGF0YS5uYW1lfWApOwogICAgICAgICAgICAgICAgICAgIH0KCiAgICAgICAgICAgICAgICAgICAgaWYgKHBhcmFtQ29uZmlnLm1pbiAhPT0gdW5kZWZpbmVkICYmIHBhcmFtQ29uZmlnLm1heCAhPT0gdW5kZWZpbmVkICYmIHBhcmFtQ29uZmlnLnN0ZXAgIT09IHVuZGVmaW5lZCkgewogICAgICAgICAgICAgICAgICAgICAgICBmb2xkZXIuYWRkKHBhcmFtQ29uZmlnLCAndmFsdWUnLCBwYXJhbUNvbmZpZy5taW4sIHBhcmFtQ29uZmlnLm1heCwgcGFyYW1Db25maWcuc3RlcCkubmFtZShwYXJhbSkub25DaGFuZ2UoKHZhbHVlKSA9PiB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICB0aGlzLnVwZGF0ZVN0YXRlKGZvbGRlckRhdGEuaWQsIHBhcmFtLCB2YWx1ZSk7CiAgICAgICAgICAgICAgICAgICAgICAgIH0pOwogICAgICAgICAgICAgICAgICAgIH0gZWxzZSBpZiAodHlwZW9mIHBhcmFtQ29uZmlnLnZhbHVlID09PSAnc3RyaW5nJyAmJiBwYXJhbUNvbmZpZy52YWx1ZS5zdGFydHNXaXRoKCcjJykpIHsKICAgICAgICAgICAgICAgICAgICAgICAgZm9sZGVyLmFkZENvbG9yKHBhcmFtQ29uZmlnLCAndmFsdWUnKS5uYW1lKHBhcmFtKS5vbkNoYW5nZSgodmFsdWUpID0+IHsKICAgICAgICAgICAgICAgICAgICAgICAgICAgIHRoaXMudXBkYXRlU3RhdGUoZm9sZGVyRGF0YS5pZCwgcGFyYW0sIHZhbHVlKTsKICAgICAgICAgICAgICAgICAgICAgICAgfSk7CiAgICAgICAgICAgICAgICAgICAgfSBlbHNlIGlmIChwYXJhbUNvbmZpZy5vcHRpb25zICE9PSB1bmRlZmluZWQpIHsKICAgICAgICAgICAgICAgICAgICAgICAgZm9sZGVyLmFkZChwYXJhbUNvbmZpZywgJ3ZhbHVlJywgcGFyYW1Db25maWcub3B0aW9ucykubmFtZShwYXJhbSkub25DaGFuZ2UoKHZhbHVlKSA9PiB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICB0aGlzLnVwZGF0ZVN0YXRlKGZvbGRlckRhdGEuaWQsIHBhcmFtLCB2YWx1ZSk7CiAgICAgICAgICAgICAgICAgICAgICAgIH0pOwogICAgICAgICAgICAgICAgICAgIH0gZWxzZSB7CiAgICAgICAgICAgICAgICAgICAgICAgIGZvbGRlci5hZGQocGFyYW1Db25maWcsICd2YWx1ZScpLm5hbWUocGFyYW0pLm9uQ2hhbmdlKCh2YWx1ZSkgPT4gewogICAgICAgICAgICAgICAgICAgICAgICAgICAgdGhpcy51cGRhdGVTdGF0ZShmb2xkZXJEYXRhLmlkLCBwYXJhbSwgdmFsdWUpOwogICAgICAgICAgICAgICAgICAgICAgICB9KTsKICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICB9IGNhdGNoIChlcnJvcikgewogICAgICAgICAgICAgICAgICAgIGNvbnNvbGUuZXJyb3IoYEZhaWxlZCB0byBhZGQgcGFyYW1ldGVyIHRvIEdVSTogJHtwYXJhbX0gaW4gZm9sZGVyOiAke2ZvbGRlckRhdGEubmFtZX0uIEVycm9yOiAke2Vycm9yLm1lc3NhZ2V9YCk7CiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgIH0KICAgICAgICB9KTsKCiAgICAgICAgY29uc3QgY29uZmlndXJhdGlvbkZvbGRlciA9IGd1aS5hZGRGb2xkZXIoIkNvbmZpZ3VyYXRpb24iKTsKICAgICAgICBjb25maWd1cmF0aW9uRm9sZGVyLmFkZCh7CiAgICAgICAgICAgIHNhdmVDb25maWd1cmF0aW9uOiAoKSA9PiB7CiAgICAgICAgICAgICAgICBjb25zb2xlLmxvZygiQ2FsbGluZyBzYXZlQ29uZmlndXJhdGlvbiB3aXRoIHN0YXRlOiIsIEpTT04uc3RyaW5naWZ5KHRoaXMuc3RhdGUuY29uZmlnR1VJLCBudWxsLCAyKSk7CiAgICAgICAgICAgICAgICB0aGlzLnNhdmVDb25maWd1cmF0aW9uKHRoaXMuc3RhdGUuY29uZmlnR1VJKTsKICAgICAgICAgICAgfQogICAgICAgIH0sICdzYXZlQ29uZmlndXJhdGlvbicpLm5hbWUoIlNhdmUgQ29uZmlndXJhdGlvbiIpOwogICAgfQoKcHJpdmF0ZSBzZXR1cFNjZW5lKCk6IHZvaWQgewogICAgY29uc3Qgc2NlbmUgPSB0aGlzLnNjZW5lOyAgLy8gQXNzdW1pbmcgdGhpcy5zY2VuZSBpcyBhbHJlYWR5IHNldAoKICAgIHRoaXMubGlnaHQgPSBuZXcgQmFieWxvbmpzQ29yZS5IZW1pc3BoZXJpY0xpZ2h0KCJoZW1pc3BoZXJpY0xpZ2h0IiwgbmV3IEJhYnlsb25qc0NvcmUuVmVjdG9yMygwLCAxLCAwKSwgc2NlbmUpOwogICAgdGhpcy5saWdodC5pbnRlbnNpdHkgPSAyOwoKICAgIHRoaXMubWFuYWdlciA9IG5ldyBCYWJ5bG9uanNHdWkuR1VJM0RNYW5hZ2VyKHNjZW5lKTsKCiAgICB0aGlzLnNwaGVyZVBhbmVsID0gbmV3IEJhYnlsb25qc0d1aS5TcGhlcmVQYW5lbCgpOwogICAgdGhpcy5tYW5hZ2VyLmFkZENvbnRyb2wodGhpcy5zcGhlcmVQYW5lbCk7CgogICAgdGhpcy5hbmNob3IgPSBuZXcgQmFieWxvbmpzQ29yZS5UcmFuc2Zvcm1Ob2RlKCJhbmNob3IiLCBzY2VuZSk7CiAgICB0aGlzLnNwaGVyZVBhbmVsLmxpbmtUb1RyYW5zZm9ybU5vZGUodGhpcy5hbmNob3IpOwoKICAgIC8vIE5vdyB0aGF0IHNwaGVyZVBhbmVsIGlzIGluaXRpYWxpemVkLCBhcHBseSB0aGUgcGFyYW1ldGVycwogICAgdGhpcy5pbml0aWFsaXplU2NlbmVQYXJhbWV0ZXJzKHRoaXMuc3RhdGUuY29uZmlnR1VJKTsKfQoKICAgIHByaXZhdGUgdXBkYXRlU3RhdGUoZm9sZGVySWQ6IHN0cmluZywgcGFyYW06IHN0cmluZywgdmFsdWU6IGFueSk6IHZvaWQgewogICAgICAgIHRyeSB7CiAgICAgICAgICAgIGNvbnN0IGZvbGRlciA9IHRoaXMuc3RhdGUuY29uZmlnR1VJLmZvbGRlcnMuZmluZCgoZm9sZGVyOiBhbnkpID0+IGZvbGRlci5pZCA9PT0gZm9sZGVySWQpOwogICAgICAgICAgICBpZiAoZm9sZGVyICYmIGZvbGRlci5wYXJhbWV0ZXJzW3BhcmFtXSAhPT0gdW5kZWZpbmVkKSB7CiAgICAgICAgICAgICAgICBjb25zdCBkZXNjcmlwdG9yID0gT2JqZWN0LmdldE93blByb3BlcnR5RGVzY3JpcHRvcihmb2xkZXIucGFyYW1ldGVyc1twYXJhbV0sICd2YWx1ZScpOwogICAgICAgICAgICAgICAgaWYgKCFkZXNjcmlwdG9yIHx8IGRlc2NyaXB0b3Iud3JpdGFibGUpIHsKICAgICAgICAgICAgICAgICAgICBmb2xkZXIucGFyYW1ldGVyc1twYXJhbV0udmFsdWUgPSB2YWx1ZTsKICAgICAgICAgICAgICAgICAgICBjb25zb2xlLmxvZyhgU3RhdGUgdXBkYXRlZDogJHtmb2xkZXJJZH0gLSAke3BhcmFtfSA9ICR7dmFsdWV9YCk7CiAgICAgICAgICAgICAgICAgICAgdGhpcy51cGRhdGVTY2VuZVBhcmFtZXRlcihmb2xkZXJJZCwgcGFyYW0sIHZhbHVlKTsKICAgICAgICAgICAgICAgIH0gZWxzZSB7CiAgICAgICAgICAgICAgICAgICAgdGhyb3cgbmV3IEVycm9yKGBQYXJhbWV0ZXIgJHtwYXJhbX0gaW4gZm9sZGVyICR7Zm9sZGVySWR9IGlzIHJlYWQtb25seS5gKTsKICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgfSBlbHNlIHsKICAgICAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcihgUGFyYW1ldGVyICR7cGFyYW19IG5vdCBmb3VuZCBpbiBmb2xkZXIgJHtmb2xkZXJJZH1gKTsKICAgICAgICAgICAgfQogICAgICAgIH0gY2F0Y2ggKGVycm9yKSB7CiAgICAgICAgICAgIGNvbnNvbGUuZXJyb3IoYEZhaWxlZCB0byB1cGRhdGUgc3RhdGU6ICR7ZXJyb3IubWVzc2FnZX1gKTsKICAgICAgICB9CiAgICB9Cgpwcml2YXRlIHVwZGF0ZVNjZW5lUGFyYW1ldGVyKGZvbGRlcklkOiBzdHJpbmcsIHBhcmFtTmFtZTogc3RyaW5nLCB2YWx1ZTogYW55KTogdm9pZCB7CiAgICBjb25zb2xlLmxvZyhgVXBkYXRpbmcgc2NlbmUgcGFyYW1ldGVyIGZvciAke2ZvbGRlcklkfSAtICR7cGFyYW1OYW1lfSB0byAke3ZhbHVlfWApOwogICAgc3dpdGNoIChmb2xkZXJJZCkgewogICAgICAgIGNhc2UgInNwaGVyZUNvbmZpZyI6CiAgICAgICAgICAgIHRoaXMuYXBwbHlTcGhlcmVDb25maWdDaGFuZ2VzKHBhcmFtTmFtZSwgdmFsdWUpOwogICAgICAgICAgICBicmVhazsKICAgICAgICBjYXNlICJidXR0b25Db25maWciOgogICAgICAgICAgICB0aGlzLnVwZGF0ZUJ1dHRvbkNvbmZpZyhmb2xkZXJJZCwgcGFyYW1OYW1lLCB2YWx1ZSk7CiAgICAgICAgICAgIGJyZWFrOwogICAgICAgIGNhc2UgImJ1dHRvblRleHRDb25maWciOgogICAgICAgICAgICB0aGlzLnVwZGF0ZUJ1dHRvblRleHRDb25maWcoZm9sZGVySWQsIHBhcmFtTmFtZSwgdmFsdWUpOwogICAgICAgICAgICBicmVhazsKICAgICAgICBkZWZhdWx0OgogICAgICAgICAgICBjb25zb2xlLmVycm9yKGBObyBoYW5kbGVyIGZvciBmb2xkZXIgJHtmb2xkZXJJZH1gKTsKICAgIH0KfQoKcHJpdmF0ZSBhcHBseVNwaGVyZUNvbmZpZ0NoYW5nZXMocGFyYW1OYW1lOiBzdHJpbmcsIHZhbHVlOiBhbnkpOiB2b2lkIHsKICAgIGlmICghdGhpcy5zcGhlcmVQYW5lbCkgewogICAgICAgIGNvbnNvbGUuZXJyb3IoIlNwaGVyZVBhbmVsIGlzIG5vdCBpbml0aWFsaXplZC4iKTsKICAgICAgICByZXR1cm47CiAgICB9CgogICAgc3dpdGNoIChwYXJhbU5hbWUpIHsKICAgICAgICBjYXNlICJyYWRpdXMiOgogICAgICAgICAgICB0aGlzLnNwaGVyZVBhbmVsLnJhZGl1cyA9IHZhbHVlOwogICAgICAgICAgICBicmVhazsKICAgICAgICBjYXNlICJtYXJnaW4iOgogICAgICAgICAgICB0aGlzLnNwaGVyZVBhbmVsLm1hcmdpbiA9IHZhbHVlOwogICAgICAgICAgICBicmVhazsKICAgICAgICBjYXNlICJjb2x1bW5zIjoKICAgICAgICAgICAgdGhpcy5zcGhlcmVQYW5lbC5jb2x1bW5zID0gdmFsdWU7CiAgICAgICAgICAgIGJyZWFrOwogICAgICAgIGNhc2UgInJvd3MiOgogICAgICAgICAgICB0aGlzLnNwaGVyZVBhbmVsLnJvd3MgPSB2YWx1ZTsKICAgICAgICAgICAgYnJlYWs7CiAgICAgICAgY2FzZSAicG9zaXRpb25YIjoKICAgICAgICBjYXNlICJwb3NpdGlvblkiOgogICAgICAgIGNhc2UgInBvc2l0aW9uWiI6CiAgICAgICAgICAgIHRoaXMudXBkYXRlUG9zaXRpb24ocGFyYW1OYW1lLCB2YWx1ZSk7CiAgICAgICAgICAgIGJyZWFrOwogICAgICAgIGNhc2UgInJvdGF0aW9uIjoKICAgICAgICAgICAgdGhpcy51cGRhdGVSb3RhdGlvbih2YWx1ZSk7CiAgICAgICAgICAgIGJyZWFrOwogICAgICAgIGNhc2UgImJpbGxib2FyZE1vZGUiOgogICAgICAgICAgICB0aGlzLnNwaGVyZVBhbmVsLmVuYWJsZUJpbGxib2FyZE1vZGUodmFsdWUgPyBCQUJZTE9OLk1lc2guQklMTEJPQVJETU9ERV9BTEwgOiBCQUJZTE9OLk1lc2guQklMTEJPQVJETU9ERV9OT05FKTsKICAgICAgICAgICAgYnJlYWs7CiAgICAgICAgZGVmYXVsdDoKICAgICAgICAgICAgY29uc29sZS5lcnJvcihgUGFyYW1ldGVyICR7cGFyYW1OYW1lfSBub3QgcmVjb2duaXplZCBpbiBzcGhlcmVDb25maWdgKTsKICAgIH0KfQoKCnByaXZhdGUgdXBkYXRlQnV0dG9uQ29uZmlnKGZvbGRlcklkOiBzdHJpbmcsIHBhcmFtTmFtZTogc3RyaW5nLCB2YWx1ZTogYW55KTogdm9pZCB7CiAgICBpZiAoIXRoaXMuc3BoZXJlUGFuZWwgfHwgIXRoaXMuc3BoZXJlUGFuZWwuY2hpbGRyZW4pIHsKICAgICAgICBjb25zb2xlLmVycm9yKCJTcGhlcmVQYW5lbCBvciBpdHMgY2hpbGRyZW4gYXJlIG5vdCBpbml0aWFsaXplZC4iKTsKICAgICAgICByZXR1cm47CiAgICB9CgogICAgdGhpcy5zcGhlcmVQYW5lbC5jaGlsZHJlbi5mb3JFYWNoKChidXR0b24pID0+IHsKICAgICAgICBpZiAoIWJ1dHRvbiB8fCAhYnV0dG9uLm1lc2gpIHsKICAgICAgICAgICAgY29uc29sZS5lcnJvcigiQnV0dG9uIG9yIGJ1dHRvbiBtZXNoIGlzIG5vdCBpbml0aWFsaXplZC4iKTsKICAgICAgICAgICAgcmV0dXJuOwogICAgICAgIH0KICAgICAgICBsZXQgbWVzaCA9IGJ1dHRvbi5tZXNoOwoKICAgICAgICBzd2l0Y2ggKHBhcmFtTmFtZSkgewogICAgICAgICAgICBjYXNlICJidXR0b25XaWR0aCI6CiAgICAgICAgICAgIGNhc2UgImJ1dHRvbkhlaWdodCI6CiAgICAgICAgICAgICAgICAvLyBVcGRhdGUgc2NhbGluZyBiYXNlZCBvbiBwYXJhbU5hbWUKICAgICAgICAgICAgICAgIG1lc2guc2NhbGluZyA9IG5ldyBCYWJ5bG9uanNDb3JlLlZlY3RvcjMoCiAgICAgICAgICAgICAgICAgICAgcGFyYW1OYW1lID09PSAiYnV0dG9uV2lkdGgiID8gdmFsdWUgOiBtZXNoLnNjYWxpbmcueCwKICAgICAgICAgICAgICAgICAgICBwYXJhbU5hbWUgPT09ICJidXR0b25IZWlnaHQiID8gdmFsdWUgOiBtZXNoLnNjYWxpbmcueSwKICAgICAgICAgICAgICAgICAgICAxCiAgICAgICAgICAgICAgICApOwogICAgICAgICAgICAgICAgYnJlYWs7CiAgICAgICAgICAgIC8vIEhhbmRsZSBvdGhlciBjYXNlcwogICAgICAgIH0KICAgIH0pOwp9CgoKcHJpdmF0ZSB1cGRhdGVCdXR0b25UZXh0Q29uZmlnKGZvbGRlcklkOiBzdHJpbmcsIHBhcmFtTmFtZTogc3RyaW5nLCB2YWx1ZTogYW55KTogdm9pZCB7CiAgICB0aGlzLnNwaGVyZVBhbmVsLmNoaWxkcmVuLmZvckVhY2goYnV0dG9uID0+IHsKICAgICAgICBsZXQgYnV0dG9uVGV4dCA9IGJ1dHRvbi50ZXh0OyAvLyBBc3N1bWluZyBlYWNoIGJ1dHRvbiBoYXMgYSAndGV4dCcgcHJvcGVydHkKICAgICAgICBpZiAoIWJ1dHRvblRleHQpIHJldHVybjsKCiAgICAgICAgc3dpdGNoIChwYXJhbU5hbWUpIHsKICAgICAgICAgICAgY2FzZSAiZm9udFNpemUiOgogICAgICAgICAgICBjYXNlICJmb250RmFtaWx5IjoKICAgICAgICAgICAgY2FzZSAidGV4dENvbG9yIjoKICAgICAgICAgICAgY2FzZSAidGV4dEFsaWduIjoKICAgICAgICAgICAgY2FzZSAidGV4dEJhc2VsaW5lIjoKICAgICAgICAgICAgY2FzZSAiZm9udFN0eWxlIjoKICAgICAgICAgICAgY2FzZSAiZm9udFdlaWdodCI6CiAgICAgICAgICAgIGNhc2UgIm91dGxpbmVDb2xvciI6CiAgICAgICAgICAgIGNhc2UgIm91dGxpbmVXaWR0aCI6CiAgICAgICAgICAgIGNhc2UgInNoYWRvd0JsdXIiOgogICAgICAgICAgICBjYXNlICJzaGFkb3dDb2xvciI6CiAgICAgICAgICAgIGNhc2UgInNoYWRvd09mZnNldFgiOgogICAgICAgICAgICBjYXNlICJzaGFkb3dPZmZzZXRZIjoKICAgICAgICAgICAgICAgIGJ1dHRvblRleHRbcGFyYW1OYW1lXSA9IHZhbHVlOwogICAgICAgICAgICAgICAgYnJlYWs7CiAgICAgICAgICAgIGRlZmF1bHQ6CiAgICAgICAgICAgICAgICBjb25zb2xlLmVycm9yKGBQYXJhbWV0ZXIgJHtwYXJhbU5hbWV9IG5vdCByZWNvZ25pemVkIGluIGJ1dHRvblRleHRDb25maWdgKTsKICAgICAgICB9CiAgICB9KTsKfQoKCgoKICAgIC8vIHByaXZhdGUgYXN5bmMgdXBkYXRlQnV0dG9uUGFyYW1ldGVycyhmb2xkZXJJZDogc3RyaW5nLCBwYXJhbTogc3RyaW5nLCB2YWx1ZTogYW55KTogUHJvbWlzZTx2b2lkPiB7CiAgICAvLyAgICAgY29uc29sZS5sb2coYFVwZGF0aW5nIGJ1dHRvbiBwYXJhbWV0ZXJzOiAke2ZvbGRlcklkfSAtICR7cGFyYW19ID0gJHt2YWx1ZX1gKTsKCiAgICAvLyAgICAgY29uc3QgYnV0dG9uQ29uZmlnID0gdGhpcy5zdGF0ZS5jb25maWdHVUkuZm9sZGVycy5maW5kKChmb2xkZXI6IGFueSkgPT4gZm9sZGVyLmlkID09PSAiYnV0dG9uQ29uZmlnIikucGFyYW1ldGVyczsKICAgIC8vICAgICBjb25zdCB0ZXh0Q29uZmlnID0gdGhpcy5zdGF0ZS5jb25maWdHVUkuZm9sZGVycy5maW5kKChmb2xkZXI6IGFueSkgPT4gZm9sZGVyLmlkID09PSAiYnV0dG9uVGV4dENvbmZpZyIpLnBhcmFtZXRlcnM7CgogICAgLy8gICAgIHRoaXMuc3RhdGUuZGF0YUxpc3QuZm9yRWFjaCgoZGF0YUl0ZW06IGFueSwgaW5kZXg6IG51bWJlcikgPT4gewogICAgLy8gICAgICAgICBjb25zdCBidXR0b25QbGFuZSA9IHRoaXMuc3BoZXJlUGFuZWwuY2hpbGRyZW5baW5kZXhdLmNvbnRlbnQgYXMgQmFieWxvbmpzQ29yZS5NZXNoOwogICAgLy8gICAgICAgICBjb25zdCBidXR0b25NYXQgPSBidXR0b25QbGFuZS5tYXRlcmlhbCBhcyBCYWJ5bG9uanNDb3JlLlN0YW5kYXJkTWF0ZXJpYWw7CiAgICAvLyAgICAgICAgIGNvbnN0IGR5bmFtaWNUZXh0dXJlID0gYnV0dG9uTWF0LmRpZmZ1c2VUZXh0dXJlIGFzIEJhYnlsb25qc0NvcmUuRHluYW1pY1RleHR1cmU7CgogICAgLy8gICAgICAgICBpZiAoZm9sZGVySWQgPT09ICJidXR0b25Db25maWciKSB7CiAgICAvLyAgICAgICAgICAgICBzd2l0Y2ggKHBhcmFtKSB7CiAgICAvLyAgICAgICAgICAgICAgICAgY2FzZSAiYnV0dG9uV2lkdGgiOgogICAgLy8gICAgICAgICAgICAgICAgIGNhc2UgImJ1dHRvbkhlaWdodCI6CiAgICAvLyAgICAgICAgICAgICAgICAgICAgIGJ1dHRvblBsYW5lLnNjYWxpbmcgPSBuZXcgQmFieWxvbmpzQ29yZS5WZWN0b3IzKGJ1dHRvbkNvbmZpZy5idXR0b25XaWR0aC52YWx1ZSwgYnV0dG9uQ29uZmlnLmJ1dHRvbkhlaWdodC52YWx1ZSwgMSk7CiAgICAvLyAgICAgICAgICAgICAgICAgICAgIGJyZWFrOwogICAgLy8gICAgICAgICAgICAgICAgIGNhc2UgImJ1dHRvbkJhY2tncm91bmRDb2xvciI6CiAgICAvLyAgICAgICAgICAgICAgICAgICAgIGJ1dHRvbk1hdC5kaWZmdXNlQ29sb3IgPSBCYWJ5bG9uanNDb3JlLkNvbG9yMy5Gcm9tSGV4U3RyaW5nKGJ1dHRvbkNvbmZpZy5idXR0b25CYWNrZ3JvdW5kQ29sb3IudmFsdWUgfHwgJyNGRkZGRkYnKTsKICAgIC8vICAgICAgICAgICAgICAgICAgICAgYnJlYWs7CiAgICAvLyAgICAgICAgICAgICAgICAgY2FzZSAiYmFja0ZhY2VDdWxsaW5nIjoKICAgIC8vICAgICAgICAgICAgICAgICAgICAgYnV0dG9uTWF0LmJhY2tGYWNlQ3VsbGluZyA9IGJ1dHRvbkNvbmZpZy5iYWNrRmFjZUN1bGxpbmcudmFsdWU7CiAgICAvLyAgICAgICAgICAgICAgICAgICAgIGJyZWFrOwogICAgLy8gICAgICAgICAgICAgICAgIGNhc2UgInRyYW5zcGFyZW5jeSI6CiAgICAvLyAgICAgICAgICAgICAgICAgICAgIGJ1dHRvbk1hdC5hbHBoYSA9IGJ1dHRvbkNvbmZpZy50cmFuc3BhcmVuY3kudmFsdWU7CiAgICAvLyAgICAgICAgICAgICAgICAgICAgIGJyZWFrOwogICAgLy8gICAgICAgICAgICAgfQogICAgLy8gICAgICAgICB9IGVsc2UgaWYgKGZvbGRlcklkID09PSAiYnV0dG9uVGV4dENvbmZpZyIpIHsKICAgIC8vICAgICAgICAgICAgIHRoaXMuYXBwbHlUZXh0VG9EeW5hbWljVGV4dHVyZShkeW5hbWljVGV4dHVyZSwgaW5kZXgsIGRhdGFJdGVtLCB0ZXh0Q29uZmlnKTsKICAgIC8vICAgICAgICAgfQogICAgLy8gICAgIH0pOwogICAgLy8gfQoKcHJpdmF0ZSBhc3luYyBjcmVhdGVCdXR0b25zQXN5bmMoYnV0dG9uQ29uZmlnOiBhbnksIHRleHRDb25maWc6IGFueSk6IFByb21pc2U8dm9pZD4gewogICAgY29uc29sZS5sb2coIlN0YXJ0aW5nIGJ1dHRvbiBjcmVhdGlvbiB3aXRoIHVwZGF0ZWQgZGF0YUxpc3QiKTsKCiAgICAvLyBEaXNwb3NlIGV4aXN0aW5nIGJ1dHRvbnMgaWYgYW55IGFuZCByZW1vdmUgdGhlbSBwcm9wZXJseQogICAgd2hpbGUgKHRoaXMuc3BoZXJlUGFuZWwuY2hpbGRyZW4ubGVuZ3RoID4gMCkgewogICAgICAgIHZhciBjaGlsZCA9IHRoaXMuc3BoZXJlUGFuZWwuY2hpbGRyZW5bMF07CiAgICAgICAgaWYgKGNoaWxkLmRpc3Bvc2UpIHsKICAgICAgICAgICAgY29uc29sZS5sb2coIkRpc3Bvc2luZyBjaGlsZDoiLCBjaGlsZCk7CiAgICAgICAgICAgIGNoaWxkLmRpc3Bvc2UoKTsgLy8gRGlzcG9zZSB0aGUgY2hpbGQgaWYgaXQgaGFzIGEgZGlzcG9zZSBtZXRob2QKICAgICAgICB9CiAgICAgICAgdGhpcy5zcGhlcmVQYW5lbC5yZW1vdmVDb250cm9sKGNoaWxkKTsgLy8gUmVtb3ZlIHRoZSBjaGlsZCBmcm9tIHRoZSBwYW5lbAogICAgICAgIGNvbnNvbGUubG9nKCJSZW1vdmVkIGNvbnRyb2wgZnJvbSBzcGhlcmVQYW5lbDoiLCBjaGlsZCk7CiAgICB9CgogICAgY29uc3QgcmVEcmF3Q291bnQgPSB0aGlzLnN0YXRlLmNvbmZpZ0dVSS5mb2xkZXJzLmZpbmQoKGZvbGRlcjogYW55KSA9PiBmb2xkZXIuaWQgPT09ICJidXR0b25BbmltYXRpb25Db25maWciKS5wYXJhbWV0ZXJzLnJlRHJhd0NvdW50LnZhbHVlOwogICAgY29uc29sZS5sb2coIlJlZHJhdyBDb3VudCBmcm9tIGNvbmZpZzoiLCByZURyYXdDb3VudCk7CgogICAgY29uc3QgZGF0YUxpc3QgPSB0aGlzLnN0YXRlLmRhdGFMaXN0LnNsaWNlKDAsIHJlRHJhd0NvdW50KTsgLy8gVXNlIGRhdGEgZnJvbSBzdGF0ZQoKICAgIGRhdGFMaXN0LmZvckVhY2goKGRhdGFJdGVtOiBhbnksIGluZGV4OiBudW1iZXIpID0+IHsKICAgICAgICBjb25zb2xlLmxvZygiQ3JlYXRpbmcgYnV0dG9uIGZvciBkYXRhIGl0ZW06IiwgZGF0YUl0ZW0pOwogICAgICAgIGNvbnN0IGJ1dHRvblBsYW5lID0gQmFieWxvbmpzQ29yZS5NZXNoQnVpbGRlci5DcmVhdGVQbGFuZSgicGxhbmUiLCB7CiAgICAgICAgICAgIHdpZHRoOiBidXR0b25Db25maWcuYnV0dG9uV2lkdGgudmFsdWUsIAogICAgICAgICAgICBoZWlnaHQ6IGJ1dHRvbkNvbmZpZy5idXR0b25IZWlnaHQudmFsdWUgCiAgICAgICAgfSwgdGhpcy5zY2VuZSk7CgogICAgICAgIGxldCBidXR0b25NYXQgPSBidXR0b25QbGFuZS5tYXRlcmlhbCBhcyBCYWJ5bG9uanNDb3JlLlN0YW5kYXJkTWF0ZXJpYWw7CiAgICAgICAgaWYgKCFidXR0b25NYXQpIHsKICAgICAgICAgICAgYnV0dG9uTWF0ID0gbmV3IEJhYnlsb25qc0NvcmUuU3RhbmRhcmRNYXRlcmlhbCgiYnV0dG9uTWF0IiwgdGhpcy5zY2VuZSk7CiAgICAgICAgICAgIGJ1dHRvblBsYW5lLm1hdGVyaWFsID0gYnV0dG9uTWF0OwogICAgICAgICAgICBjb25zb2xlLmxvZygiQ3JlYXRlZCBuZXcgbWF0ZXJpYWwgZm9yIGJ1dHRvblBsYW5lIik7CiAgICAgICAgfQoKICAgICAgICBidXR0b25NYXQuZGlmZnVzZUNvbG9yID0gQmFieWxvbmpzQ29yZS5Db2xvcjMuRnJvbUhleFN0cmluZyhidXR0b25Db25maWcuYnV0dG9uQmFja2dyb3VuZENvbG9yLnZhbHVlKTsKICAgICAgICBidXR0b25NYXQuYmFja0ZhY2VDdWxsaW5nID0gYnV0dG9uQ29uZmlnLmJhY2tGYWNlQ3VsbGluZy52YWx1ZTsKICAgICAgICBidXR0b25NYXQuYWxwaGEgPSBidXR0b25Db25maWcudHJhbnNwYXJlbmN5LnZhbHVlOwoKICAgICAgICBjb25zdCBkeW5hbWljVGV4dHVyZSA9IEJhYnlsb25qc0d1aS5BZHZhbmNlZER5bmFtaWNUZXh0dXJlLkNyZWF0ZUZvck1lc2goYnV0dG9uUGxhbmUpOwogICAgICAgIHRoaXMuYXBwbHlUZXh0VG9EeW5hbWljVGV4dHVyZShkeW5hbWljVGV4dHVyZSwgZGF0YUl0ZW0sIHRleHRDb25maWcpOwoKICAgICAgICBjb25zdCBidXR0b24gPSBuZXcgQmFieWxvbmpzR3VpLk1lc2hCdXR0b24zRChidXR0b25QbGFuZSwgImJ1dHRvbiIgKyBkYXRhSXRlbS5ndWlkKTsKICAgICAgICB0aGlzLnNwaGVyZVBhbmVsLmFkZENvbnRyb2woYnV0dG9uKTsKICAgICAgICBjb25zb2xlLmxvZygiQWRkZWQgbmV3IGJ1dHRvbiB0byBzcGhlcmVQYW5lbDoiLCBidXR0b24pOwogICAgfSk7CgogICAgY29uc29sZS5sb2coIkNvbXBsZXRlZCBidXR0b24gY3JlYXRpb24gcHJvY2Vzcy4iKTsKfQoKCnByaXZhdGUgYXBwbHlUZXh0VG9EeW5hbWljVGV4dHVyZShkeW5hbWljVGV4dHVyZTogQmFieWxvbmpzR3VpLkFkdmFuY2VkRHluYW1pY1RleHR1cmUsIGRhdGFJdGVtOiBhbnksIHRleHRDb25maWc6IGFueSk6IHZvaWQgewogICAgY29uc3QgdGV4dEJsb2NrID0gbmV3IEJhYnlsb25qc0d1aS5UZXh0QmxvY2soKTsKICAgIHRleHRCbG9jay50ZXh0ID0gZGF0YUl0ZW0ubmFtZTsKICAgIHRleHRCbG9jay5jb2xvciA9IHRleHRDb25maWcudGV4dENvbG9yLnZhbHVlOwogICAgdGV4dEJsb2NrLmZvbnRTaXplID0gdGV4dENvbmZpZy5mb250U2l6ZS52YWx1ZTsKICAgIHRleHRCbG9jay5mb250RmFtaWx5ID0gdGV4dENvbmZpZy5mb250RmFtaWx5LnZhbHVlOwogICAgdGV4dEJsb2NrLnJlc2l6ZVRvRml0ID0gdHJ1ZTsKICAgIHRleHRCbG9jay50ZXh0SG9yaXpvbnRhbEFsaWdubWVudCA9IEJhYnlsb25qc0d1aS5Db250cm9sLkhPUklaT05UQUxfQUxJR05NRU5UX0NFTlRFUjsKICAgIHRleHRCbG9jay50ZXh0VmVydGljYWxBbGlnbm1lbnQgPSBCYWJ5bG9uanNHdWkuQ29udHJvbC5WRVJUSUNBTF9BTElHTk1FTlRfQ0VOVEVSOwogICAgZHluYW1pY1RleHR1cmUuYWRkQ29udHJvbCh0ZXh0QmxvY2spOwp9CgoKCgogICAgQGV2ZW50RWdyZXNzKCd4ci5kYXRhLnNwaGVyZVY2Q29uZmlnJykKICAgIHB1YmxpYyBzYXZlQ29uZmlndXJhdGlvbihndWlDb25maWc6IGFueSkgewogICAgICAgIHRyeSB7CiAgICAgICAgICAgIGNvbnNvbGUubG9nKCJDb25maXJtaW5nIFN0YXRlIENvbnRleHQ6IiwgSlNPTi5zdHJpbmdpZnkoZ3VpQ29uZmlnLCBudWxsLCAyKSk7CiAgICAgICAgICAgIGlmICghZ3VpQ29uZmlnKSB7CiAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoIlN0YXRlIG9yIGNvbmZpZ0dVSSBpcyBub3QgZGVmaW5lZC4iKTsKICAgICAgICAgICAgfQogICAgICAgICAgICByZXR1cm4geyBbdGhpcy5zdGF0ZURhdGFLZXldOiBndWlDb25maWcgfTsKICAgICAgICB9IGNhdGNoIChlcnJvcikgewogICAgICAgICAgICBjb25zb2xlLmVycm9yKCJGYWlsZWQgdG8gc2F2ZSBjb25maWd1cmF0aW9uOiIsIGVycm9yLm1lc3NhZ2UpOwogICAgICAgICAgICByZXR1cm4gewogICAgICAgICAgICAgICAgW3RoaXMuc3RhdGVEYXRhS2V5XToge30KICAgICAgICAgICAgfTsKICAgICAgICB9CiAgICB9CgogICAgcHJpdmF0ZSBkZWJvdW5jZShmdW5jOiAoLi4uYXJnczogYW55W10pID0+IHZvaWQsIHdhaXQ6IG51bWJlcikgewogICAgICAgIGxldCB0aW1lb3V0OiBOb2RlSlMuVGltZW91dDsKICAgICAgICByZXR1cm4gKC4uLmFyZ3M6IGFueVtdKSA9PiB7CiAgICAgICAgICAgIGNsZWFyVGltZW91dCh0aW1lb3V0KTsKICAgICAgICAgICAgdGltZW91dCA9IHNldFRpbWVvdXQoKCkgPT4gZnVuYy5hcHBseSh0aGlzLCBhcmdzKSwgd2FpdCk7CiAgICAgICAgfTsKICAgIH0KCiAgICBwcml2YXRlIGRlYm91bmNlZFVwZGF0ZVN0YXRlKGZvbGRlcklkOiBzdHJpbmcsIHBhcmFtOiBzdHJpbmcpIHsKICAgICAgICByZXR1cm4gdGhpcy5kZWJvdW5jZShhc3luYyAodmFsdWU6IGFueSkgPT4gewogICAgICAgICAgICBhd2FpdCB0aGlzLnVwZGF0ZVN0YXRlKGZvbGRlcklkLCBwYXJhbSwgdmFsdWUpOwogICAgICAgIH0sIDMwMCk7CiAgICB9Cn0K"
    },
    "classes": [
      {
        "class": "XrVoyagePlugin",
        "functions": [
          {
            "name": "constructor",
            "status": "on",
            "line_start": 10,
            "line_end": 16,
            "scope": "public",
            "async": false,
            "decorators": []
          },
          {
            "name": "setupState",
            "status": "on",
            "line_start": 18,
            "line_end": 45,
            "scope": "private",
            "async": false,
            "decorators": []
          },
          {
            "name": "confirmStateStructure",
            "status": "off",
            "line_start": 48,
            "line_end": 55,
            "scope": "private",
            "async": false,
            "decorators": []
          },
          {
            "name": "setupGUI",
            "status": "off",
            "line_start": 57,
            "line_end": 93,
            "scope": "private",
            "async": false,
            "decorators": []
          },
          {
            "name": "reDrawScene",
            "status": "off",
            "line_start": 96,
            "line_end": 111,
            "scope": "private",
            "async": false,
            "decorators": []
          },
          {
            "name": "setupScene",
            "status": "off",
            "line_start": 113,
            "line_end": 152,
            "scope": "private",
            "async": false,
            "decorators": []
          },
          {
            "name": "createButtonsAsync",
            "status": "off",
            "line_start": 154,
            "line_end": 183,
            "scope": "private",
            "async": true,
            "decorators": []
          },
          {
            "name": "applyTextToDynamicTexture",
            "status": "off",
            "line_start": 186,
            "line_end": 200,
            "scope": "private",
            "async": false,
            "decorators": []
          },
          {
            "name": "updateState",
            "status": "off",
            "line_start": 203,
            "line_end": 216,
            "scope": "private",
            "async": true,
            "decorators": []
          },
          {
            "name": "updateSceneProperties",
            "status": "off",
            "line_start": 224,
            "line_end": 243,
            "scope": "private",
            "async": true,
            "decorators": []
          },
          {
            "name": "createButtonsAsync",
            "status": "off",
            "line_start": 250,
            "line_end": 287,
            "scope": "private",
            "async": true,
            "decorators": []
          },
          {
            "name": "applyTextToDynamicTexture",
            "status": "off",
            "line_start": 293,
            "line_end": 307,
            "scope": "private",
            "async": false,
            "decorators": []
          },
          {
            "name": "saveConfiguration",
            "status": "off",
            "line_start": 311,
            "line_end": 325,
            "scope": "public",
            "async": false,
            "decorators": [
              {
                "name": "eventEgress",
                "args": [
                  "xr.data.sphereV6Config"
                ]
              }
            ]
          },
          {
            "name": "debounce",
            "status": "off",
            "line_start": 327,
            "line_end": 333,
            "scope": "private",
            "async": false,
            "decorators": []
          },
          {
            "name": "debouncedUpdateState",
            "status": "off",
            "line_start": 335,
            "line_end": 339,
            "scope": "private",
            "async": false,
            "decorators": []
          }
        ]
      }
    ]
  },
  "name": "plugin.3D.sphere.v6",
  "token_username": "peters",
  "token_sub": "03e563c9-4dce-4fe5-af52-e37cde040618",
  "guid": "B722CD7C3CE54116912540D6C4257477",
  "created_utc": "2024-06-09 20:46:09.614596",
  "updated_utc": "2024-06-22 03:32:14.355421"
}"""

    ingestor = FalkorDBIngestor(plugin_data)
    ingestor.ingest()

if __name__ == "__main__":
    main()
