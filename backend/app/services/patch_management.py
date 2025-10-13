from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random

from app.models.alert import Client


class PatchManagementService:
    """Generates patch advisories, plans maintenance windows, and simulates blast radius."""

    def __init__(self):
        # Mock CVE dataset (id, severity, product, summary)
        self.mock_cves = [
            {"cve": "CVE-2024-12345", "severity": 9.8, "product": "database", "summary": "Critical RCE in SQL engine"},
            {"cve": "CVE-2025-10001", "severity": 8.6, "product": "web-app", "summary": "Auth bypass in session handling"},
            {"cve": "CVE-2024-56789", "severity": 7.5, "product": "api-gateway", "summary": "DoS via malformed headers"},
            {"cve": "CVE-2023-98765", "severity": 6.4, "product": "storage-server", "summary": "Privilege escalation in driver"},
            {"cve": "CVE-2025-22222", "severity": 9.1, "product": "firewall", "summary": "Policy injection vulnerability"},
        ]

    def get_advisories(self, client: Client) -> Dict:
        critical_systems = set(client.critical_systems)
        advisories = []
        for cve in self.mock_cves:
            impact = 1.2 if cve["product"] in critical_systems else 1.0
            score = round(min(10.0, cve["severity"] * impact), 1)
            advisories.append({
                **cve,
                "client_impact_score": score,
                "recommended_action": self._recommend_action(cve["product"], score),
            })

        advisories.sort(key=lambda x: (x["client_impact_score"], x["severity"]), reverse=True)
        return {
            "client_id": client.id,
            "client_name": client.name,
            "generated_at": datetime.now().isoformat(),
            "advisories": advisories,
        }

    def plan_maintenance(self, client: Client, advisories: List[Dict]) -> Dict:
        # Find a low-impact window (heuristic: pick outside business hours)
        start = datetime.now().replace(hour=2, minute=0, second=0, microsecond=0)
        if start < datetime.now():
            start = start + timedelta(days=1)
        duration_min = 45 + (len(advisories) * 10)

        stages = []
        # Stage by dependency layers to reduce blast radius
        for adv in advisories[:4]:
            pre = self._pre_checks(adv["product"]) 
            post = self._post_checks(adv["product"]) 
            stages.append({
                "product": adv["product"],
                "cve": adv["cve"],
                "pre_checks": pre,
                "post_checks": post,
                "estimated_minutes": 20,
            })

        risk = self._estimate_plan_risk(client, advisories)
        return {
            "client_id": client.id,
            "client_name": client.name,
            "window_start": start.isoformat(),
            "window_duration_minutes": duration_min,
            "staged_rollout": stages,
            "overall_risk_score": risk,
            "approval_required": risk > 0.6,
        }

    def simulate_blast_radius(self, client: Client, target_product: str) -> Dict:
        deps = client.system_dependencies
        directly_depends = deps.get(target_product, [])
        indirectly = [k for k, v in deps.items() if target_product in v]
        total_systems = set(directly_depends + indirectly)
        risk = min(0.95, 0.3 + 0.1 * len(total_systems))

        return {
            "client_id": client.id,
            "target": target_product,
            "impacted_systems": list(total_systems),
            "predicted_outage_minutes": 5 * len(total_systems),
            "risk_score": round(risk, 2),
            "rollback_plan": [
                "Snapshot/backup before patch",
                "Health checks per dependency",
                "Rollback if error budget exceeded",
            ],
        }

    def _recommend_action(self, product: str, score: float) -> str:
        if score >= 9.0:
            return f"Patch {product} within 24h"
        if score >= 7.5:
            return f"Schedule patch in next maintenance window"
        return f"Monitor and patch in next cycle"

    def _pre_checks(self, product: str) -> List[str]:
        return [
            f"Backup {product}",
            f"Drain traffic from {product} (if applicable)",
            "Verify failover readiness",
        ]

    def _post_checks(self, product: str) -> List[str]:
        return [
            f"Smoke test {product}",
            "Latency/throughput baseline within 5%",
            "Error rate < 1% for 15 min",
        ]

    def _estimate_plan_risk(self, client: Client, advisories: List[Dict]) -> float:
        """Heuristic risk estimate for the whole maintenance window.
        Considers CVE severities, number of systems touched, and dependency blast radius.
        """
        if not advisories:
            return 0.2

        # Severity factor: higher severities tend to imply higher urgency and potential risk
        sev_scores = [a.get("severity", 7.0) for a in advisories]
        max_sev = max(sev_scores)
        avg_sev = sum(sev_scores) / len(sev_scores)
        sev_factor = min(1.0, (max_sev / 10.0) * 0.5 + (avg_sev / 10.0) * 0.3)

        # Scope factor: number of distinct products to patch
        products = {a.get("product", "system") for a in advisories}
        scope_factor = min(0.3, 0.07 * len(products))

        # Dependency factor: how many dependents could be affected
        deps = client.system_dependencies
        impacted = set()
        for p in products:
            impacted.update(deps.get(p, []))
            impacted.update([k for k, v in deps.items() if p in v])
        dep_factor = min(0.35, 0.05 * len(impacted))

        risk = sev_factor + scope_factor + dep_factor
        return round(min(0.95, max(0.1, risk)), 2)


