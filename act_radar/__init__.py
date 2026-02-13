"""
Radar Module: Monitoring & Rollback System

Monitors executed changes and automatically rolls back performance regressions.

Constitution Reference: Section 8 (Monitoring, Rollback & Anti-Oscillation)
"""

from .monitor import ChangeMonitor, MonitoredChange, PerformanceMetrics, format_change_summary
from .triggers import (
    RollbackDecision,
    check_cpa_regression,
    check_roas_regression,
    check_anti_oscillation,
    should_rollback,
    format_rollback_decision
)
from .rollback_executor import (
    RollbackExecutor,
    RollbackResult,
    execute_rollbacks
)
from .alerts import (
    send_rollback_alert,
    send_monitoring_summary,
    generate_rollback_report,
    log_alert,
    format_performance_summary
)

__all__ = [
    'ChangeMonitor',
    'MonitoredChange',
    'PerformanceMetrics',
    'format_change_summary',
    'RollbackDecision',
    'check_cpa_regression',
    'check_roas_regression',
    'check_anti_oscillation',
    'should_rollback',
    'format_rollback_decision',
    'RollbackExecutor',
    'RollbackResult',
    'execute_rollbacks',
    'send_rollback_alert',
    'send_monitoring_summary',
    'generate_rollback_report',
    'log_alert',
    'format_performance_summary',
]
