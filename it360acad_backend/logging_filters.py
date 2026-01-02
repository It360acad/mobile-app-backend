import logging

class TenantContextFilter(logging.Filter):
    """
    Filter that adds tenant_id and user_id to the log record.
    These values should be set on the record by middleware or manually.
    """
    def filter(self, record):
        if not hasattr(record, 'tenant_id'):
            record.tenant_id = 'N/A'
        if not hasattr(record, 'user_id'):
            record.user_id = 'Anonymous'
        return True

