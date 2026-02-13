"""
Radar Module: Change Monitor
Tracks post-change performance and detects regressions.

Constitution Reference: Section 8 (Monitoring, Rollback & Anti-Oscillation)
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
import duckdb


@dataclass
class MonitoredChange:
    """A change being monitored for rollback."""
    change_id: int
    customer_id: str
    campaign_id: str
    campaign_name: str
    change_date: date
    lever: str  # 'budget', 'bid', 'status'
    old_value: float
    new_value: float
    change_pct: float
    rule_id: str
    risk_tier: str
    
    # Monitoring metadata
    monitoring_window_days: int
    min_wait_hours: int
    
    # Performance metrics
    baseline: Optional[Dict] = None  # Pre-change performance
    current: Optional[Dict] = None   # Post-change performance
    delta: Optional[Dict] = None     # Change in performance


@dataclass
class PerformanceMetrics:
    """Campaign performance metrics."""
    period_start: date
    period_end: date
    days: int
    
    # Core metrics
    impressions: int
    clicks: int
    cost_micros: int
    conversions: float
    conversion_value_micros: float
    
    # Derived metrics
    ctr: float
    cpc_micros: float
    cpa_micros: float
    roas: float
    
    # Context
    avg_daily_cost: float
    avg_daily_conversions: float


class ChangeMonitor:
    """Monitor executed changes for performance regressions."""
    
    def __init__(self, db_path: str = "warehouse.duckdb"):
        self.db_path = db_path
        
        # Constitution: Section 8 - Monitoring windows
        self.monitoring_windows = {
            'budget': 7,   # Budget changes: 7 days
            'bid': 14,     # Bid changes: 14 days
            'status': 7,   # Status changes: 7 days
        }
        
        # Constitution: Section 8 - Minimum wait time
        self.min_wait_hours = 72  # 72 hours minimum
    
    def get_changes_to_monitor(self, customer_id: str) -> List[MonitoredChange]:
        """
        Get all changes that need monitoring.
        
        Constitution: Only monitor changes where minimum wait time has elapsed.
        """
        conn = duckdb.connect(self.db_path, read_only=True)
        
        query = """
        SELECT 
            cl.change_id,
            cl.customer_id,
            cl.campaign_id,
            cd.campaign_name,
            cl.change_date,
            cl.lever,
            cl.old_value,
            cl.new_value,
            cl.change_pct,
            cl.rule_id,
            cl.risk_tier,
            cl.executed_at,
            cl.rollback_status
        FROM analytics.change_log cl
        LEFT JOIN analytics.campaign_daily cd 
            ON cl.customer_id = cd.customer_id 
            AND cl.campaign_id = cd.campaign_id
            AND cd.snapshot_date = (
                SELECT MAX(snapshot_date) 
                FROM analytics.campaign_daily 
                WHERE customer_id = cl.customer_id 
                AND campaign_id = cl.campaign_id
            )
        WHERE cl.customer_id = ?
        AND cl.rollback_status IS NULL  -- Not already rolled back or confirmed
        AND cl.executed_at < ?  -- Minimum wait time elapsed
        ORDER BY cl.change_date DESC, cl.executed_at DESC
        """
        
        # Calculate cutoff: 72 hours ago
        cutoff_time = datetime.now() - timedelta(hours=self.min_wait_hours)
        
        rows = conn.execute(query, [customer_id, cutoff_time]).fetchall()
        conn.close()
        
        changes = []
        for row in rows:
            lever = row[5]
            monitoring_window = self.monitoring_windows.get(lever, 7)
            
            change = MonitoredChange(
                change_id=row[0],
                customer_id=row[1],
                campaign_id=row[2],
                campaign_name=row[3] or "Unknown",
                change_date=row[4],
                lever=lever,
                old_value=row[6],
                new_value=row[7],
                change_pct=row[8],
                rule_id=row[9],
                risk_tier=row[10],
                monitoring_window_days=monitoring_window,
                min_wait_hours=self.min_wait_hours
            )
            
            changes.append(change)
        
        return changes
    
    def get_baseline_performance(
        self, 
        customer_id: str, 
        campaign_id: str, 
        change_date: date,
        window_days: int = 14
    ) -> Optional[PerformanceMetrics]:
        """
        Get pre-change baseline performance.
        
        Constitution: Baseline = performance before change.
        Window: 7-14 days before change date (depending on lever).
        """
        conn = duckdb.connect(self.db_path, read_only=True)
        
        # Baseline period: window_days BEFORE change_date
        period_end = change_date - timedelta(days=1)  # Day before change
        period_start = period_end - timedelta(days=window_days - 1)
        
        query = """
        SELECT 
            COUNT(*) as days,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks,
            SUM(cost_micros) as cost_micros,
            SUM(conversions) as conversions,
            SUM(conversions_value) as conversion_value_micros
        FROM analytics.campaign_daily
        WHERE customer_id = ?
        AND campaign_id = ?
        AND snapshot_date >= ?
        AND snapshot_date <= ?
        """
        
        row = conn.execute(query, [customer_id, campaign_id, period_start, period_end]).fetchone()
        conn.close()
        
        if not row or row[0] == 0:
            return None
        
        days = row[0]
        impressions = row[1] or 0
        clicks = row[2] or 0
        cost_micros = row[3] or 0
        conversions = row[4] or 0.0
        conversion_value_micros = row[5] or 0
        
        # Calculate derived metrics
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        cpc_micros = (cost_micros / clicks) if clicks > 0 else 0.0
        cpa_micros = (cost_micros / conversions) if conversions > 0 else 0.0
        roas = (conversion_value_micros / cost_micros) if cost_micros > 0 else 0.0
        
        avg_daily_cost = cost_micros / days / 1_000_000 if days > 0 else 0.0
        avg_daily_conversions = conversions / days if days > 0 else 0.0
        
        return PerformanceMetrics(
            period_start=period_start,
            period_end=period_end,
            days=days,
            impressions=impressions,
            clicks=clicks,
            cost_micros=cost_micros,
            conversions=conversions,
            conversion_value_micros=conversion_value_micros,
            ctr=ctr,
            cpc_micros=cpc_micros,
            cpa_micros=cpa_micros,
            roas=roas,
            avg_daily_cost=avg_daily_cost,
            avg_daily_conversions=avg_daily_conversions
        )
    
    def get_post_change_performance(
        self, 
        customer_id: str, 
        campaign_id: str, 
        change_date: date,
        window_days: int = 14
    ) -> Optional[PerformanceMetrics]:
        """
        Get post-change performance.
        
        Constitution: Post-change = performance after change + min wait time.
        Window: Same length as baseline (7-14 days).
        """
        conn = duckdb.connect(self.db_path, read_only=True)
        
        # Post-change period: window_days AFTER change_date + min wait
        period_start = change_date + timedelta(days=3)  # Start after min wait (72hr)
        period_end = period_start + timedelta(days=window_days - 1)
        
        # Don't try to monitor future dates
        today = date.today()
        if period_end > today:
            period_end = today
        
        if period_start >= today:
            return None  # Not enough time has passed
        
        query = """
        SELECT 
            COUNT(*) as days,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks,
            SUM(cost_micros) as cost_micros,
            SUM(conversions) as conversions,
            SUM(conversions_value) as conversion_value_micros
        FROM analytics.campaign_daily
        WHERE customer_id = ?
        AND campaign_id = ?
        AND snapshot_date >= ?
        AND snapshot_date <= ?
        """
        
        row = conn.execute(query, [customer_id, campaign_id, period_start, period_end]).fetchone()
        conn.close()
        
        if not row or row[0] == 0:
            return None
        
        days = row[0]
        impressions = row[1] or 0
        clicks = row[2] or 0
        cost_micros = row[3] or 0
        conversions = row[4] or 0.0
        conversion_value_micros = row[5] or 0
        
        # Calculate derived metrics
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        cpc_micros = (cost_micros / clicks) if clicks > 0 else 0.0
        cpa_micros = (cost_micros / conversions) if conversions > 0 else 0.0
        roas = (conversion_value_micros / cost_micros) if cost_micros > 0 else 0.0
        
        avg_daily_cost = cost_micros / days / 1_000_000 if days > 0 else 0.0
        avg_daily_conversions = conversions / days if days > 0 else 0.0
        
        return PerformanceMetrics(
            period_start=period_start,
            period_end=period_end,
            days=days,
            impressions=impressions,
            clicks=clicks,
            cost_micros=cost_micros,
            conversions=conversions,
            conversion_value_micros=conversion_value_micros,
            ctr=ctr,
            cpc_micros=cpc_micros,
            cpa_micros=cpa_micros,
            roas=roas,
            avg_daily_cost=avg_daily_cost,
            avg_daily_conversions=avg_daily_conversions
        )
    
    def calculate_performance_delta(
        self, 
        baseline: PerformanceMetrics, 
        current: PerformanceMetrics
    ) -> Dict:
        """
        Calculate before vs after performance changes.
        
        Returns percentage changes for key metrics.
        """
        def safe_pct_change(old, new):
            if old == 0:
                return 0.0 if new == 0 else 999.0  # Large number if went from 0 to something
            return (new - old) / old
        
        # CPA change (lower is better, so positive % is bad)
        cpa_change_pct = safe_pct_change(baseline.cpa_micros, current.cpa_micros)
        
        # ROAS change (higher is better, so positive % is good)
        roas_change_pct = safe_pct_change(baseline.roas, current.roas)
        
        # Conversion change (higher is better)
        conversions_change_pct = safe_pct_change(baseline.conversions, current.conversions)
        
        # Conversion value change (higher is better)
        value_change_pct = safe_pct_change(
            baseline.conversion_value_micros, 
            current.conversion_value_micros
        )
        
        # Cost change (context dependent)
        cost_change_pct = safe_pct_change(baseline.cost_micros, current.cost_micros)
        
        return {
            # Before metrics
            "baseline_cpa": baseline.cpa_micros / 1_000_000,  # Convert to dollars
            "baseline_roas": baseline.roas,
            "baseline_conversions": baseline.conversions,
            "baseline_conversion_value": baseline.conversion_value_micros / 1_000_000,
            "baseline_cost": baseline.cost_micros / 1_000_000,
            "baseline_period": f"{baseline.period_start} to {baseline.period_end}",
            
            # After metrics
            "current_cpa": current.cpa_micros / 1_000_000,
            "current_roas": current.roas,
            "current_conversions": current.conversions,
            "current_conversion_value": current.conversion_value_micros / 1_000_000,
            "current_cost": current.cost_micros / 1_000_000,
            "current_period": f"{current.period_start} to {current.period_end}",
            
            # Changes (as percentages)
            "cpa_change_pct": cpa_change_pct,
            "roas_change_pct": roas_change_pct,
            "conversions_change_pct": conversions_change_pct,
            "value_change_pct": value_change_pct,
            "cost_change_pct": cost_change_pct,
            
            # Directional indicators
            "cpa_worsened": cpa_change_pct > 0,  # CPA increased (bad)
            "roas_worsened": roas_change_pct < 0,  # ROAS decreased (bad)
            "conversions_dropped": conversions_change_pct < 0,  # Conv decreased (bad)
            "value_dropped": value_change_pct < 0,  # Value decreased (bad)
        }
    
    def monitor_all_changes(self, customer_id: str) -> List[MonitoredChange]:
        """
        Monitor all changes for a customer.
        
        Returns list of changes with baseline, current, and delta populated.
        """
        changes = self.get_changes_to_monitor(customer_id)
        
        for change in changes:
            # Get baseline performance (before change)
            baseline = self.get_baseline_performance(
                change.customer_id,
                change.campaign_id,
                change.change_date,
                window_days=change.monitoring_window_days
            )
            
            # Get post-change performance (after change)
            current = self.get_post_change_performance(
                change.customer_id,
                change.campaign_id,
                change.change_date,
                window_days=change.monitoring_window_days
            )
            
            # Calculate delta if both exist
            if baseline and current:
                change.baseline = baseline
                change.current = current
                change.delta = self.calculate_performance_delta(baseline, current)
            else:
                # Not enough data yet
                change.baseline = baseline
                change.current = current
                change.delta = None
        
        return changes


def format_change_summary(change: MonitoredChange) -> str:
    """Format a change for human-readable output."""
    lines = []
    lines.append(f"Change ID: {change.change_id}")
    lines.append(f"Campaign: {change.campaign_name} ({change.campaign_id})")
    lines.append(f"Date: {change.change_date}")
    lines.append(f"Action: {change.lever} {change.old_value:.2f} → {change.new_value:.2f} ({change.change_pct:+.1%})")
    lines.append(f"Rule: {change.rule_id} ({change.risk_tier} risk)")
    
    if change.delta:
        lines.append(f"\nPerformance Change:")
        lines.append(f"  CPA: ${change.delta['baseline_cpa']:.2f} → ${change.delta['current_cpa']:.2f} ({change.delta['cpa_change_pct']:+.1%})")
        lines.append(f"  ROAS: {change.delta['baseline_roas']:.2f} → {change.delta['current_roas']:.2f} ({change.delta['roas_change_pct']:+.1%})")
        lines.append(f"  Conversions: {change.delta['baseline_conversions']:.1f} → {change.delta['current_conversions']:.1f} ({change.delta['conversions_change_pct']:+.1%})")
    else:
        lines.append("\nStatus: Insufficient data for analysis")
    
    return "\n".join(lines)
