from flask import Request

class LargeRequest(Request):
    max_form_memory_size = 50 * 1024 * 1024   # 50MB field limit
    max_content_length = 300 * 1024 * 1024   # 300MB total
