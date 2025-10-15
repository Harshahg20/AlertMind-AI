import asyncio
import json
import logging
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

try:
    from transformers import pipeline
    from langchain.llms import HuggingFacePipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None
    HuggingFacePipeline = None

from app.models.alert import Alert

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Correlation prompt for the LLM
CORRELATION_PROMPT = """
You are the Alert Correlation Agent.

Given multiple system alerts in JSON, group them into clusters representing 
the same root cause. Output concise JSON:
[
  { "cluster_id": "<uuid>", "alerts": [...], "summary": "<30-word summary>", "severity": "<low|medium|high>" }
]

Rules:
- Merge alerts that share same host, component, or timestamp window ±3 min.
- Keep only the top 10 clusters by severity.
"""

class AlertCorrelationAgent:
    """
    Alert Correlation Agent using sentence transformers for embeddings
    and optional LLM reasoning with Mistral-7B-Instruct or Gemini
    """
    
    def __init__(self, use_llm: bool = True, model_name: str = "mistralai/Mistral-7B-Instruct"):
        self.name = "alert_correlation_agent"
        self.use_llm = use_llm
        
        # Initialize sentence transformer for embeddings
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                logger.info("✅ Sentence transformer loaded successfully")
            except Exception as e:
                logger.error(f"❌ Failed to load sentence transformer: {e}")
                self.embedder = None
        else:
            logger.warning("⚠️ Sentence transformers not available, using fallback embeddings")
            self.embedder = None
        
        # Initialize LLM for reasoning (optional)
        self.llm = None
        if self.use_llm and TRANSFORMERS_AVAILABLE:
            try:
                # Try to load Mistral model
                if model_name == "mistralai/Mistral-7B-Instruct":
                    self.llm = HuggingFacePipeline(
                        pipeline(
                            "text-generation",
                            model=model_name,
                            max_new_tokens=400,
                            do_sample=True,
                            temperature=0.3,
                            pad_token_id=50256
                        )
                    )
                    logger.info("✅ Mistral-7B-Instruct loaded successfully")
                else:
                    # Fallback to a smaller model
                    self.llm = HuggingFacePipeline(
                        pipeline(
                            "text-generation",
                            model="gpt2",
                            max_new_tokens=200,
                            do_sample=True,
                            temperature=0.3
                        )
                    )
                    logger.info("✅ GPT-2 fallback model loaded")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load LLM: {e}. Continuing without LLM reasoning.")
                self.llm = None
                self.use_llm = False
        else:
            logger.warning("⚠️ Transformers not available, LLM reasoning disabled")
            self.use_llm = False
    
    async def run(self, alerts: List[Alert]) -> Dict:
        """
        Main correlation method that processes alerts and returns clustered results
        """
        try:
            if not alerts:
                return {"clusters": [], "summary": "No alerts to process"}
            
            logger.info(f"🔍 Processing {len(alerts)} alerts for correlation")
            
            # Extract alert texts for embedding
            texts = [self._format_alert_text(alert) for alert in alerts]
            
            # Generate embeddings
            if self.embedder:
                embeddings = self.embedder.encode(texts)
                logger.info(f"📊 Generated embeddings with shape: {embeddings.shape}")
            else:
                # Fallback to simple text similarity
                embeddings = self._fallback_embeddings(texts)
            
            # Perform clustering
            clusters = self.simple_cluster(embeddings, alerts, threshold=0.8)
            logger.info(f"🎯 Found {len(clusters)} alert clusters")
            
            # Generate summaries using LLM if available
            if self.use_llm and self.llm:
                try:
                    summary = await self._generate_llm_summary(clusters)
                except Exception as e:
                    logger.warning(f"⚠️ LLM summary generation failed: {e}")
                    summary = self._generate_fallback_summary(clusters)
            else:
                summary = self._generate_fallback_summary(clusters)
            
            # Calculate correlation metrics
            metrics = self._calculate_correlation_metrics(alerts, clusters)
            
            return {
                "clusters": clusters,
                "summary": summary,
                "metrics": metrics,
                "processed_at": datetime.now().isoformat(),
                "agent_name": self.name
            }
            
        except Exception as e:
            logger.error(f"❌ Alert correlation failed: {e}")
            return {
                "clusters": [],
                "summary": f"Correlation failed: {str(e)}",
                "metrics": {"error": str(e)},
                "processed_at": datetime.now().isoformat(),
                "agent_name": self.name
            }
    
    def _format_alert_text(self, alert: Alert) -> str:
        """Format alert for embedding generation"""
        return f"{alert.system} {alert.severity} {alert.category} {alert.message}"
    
    def _fallback_embeddings(self, texts: List[str]) -> np.ndarray:
        """Fallback embedding method using simple text features"""
        # Simple TF-IDF-like approach
        all_words = set()
        for text in texts:
            all_words.update(text.lower().split())
        
        word_to_idx = {word: i for i, word in enumerate(all_words)}
        embeddings = np.zeros((len(texts), len(all_words)))
        
        for i, text in enumerate(texts):
            words = text.lower().split()
            for word in words:
                if word in word_to_idx:
                    embeddings[i, word_to_idx[word]] += 1
        
        # Normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return embeddings / norms
    
    def simple_cluster(self, embeddings: np.ndarray, alerts: List[Alert], threshold: float = 0.8) -> List[Dict]:
        """
        Simple cosine similarity clustering
        """
        if len(embeddings) == 0:
            return []
        
        # Calculate cosine similarity matrix
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        normalized_embeddings = embeddings / norms
        sims = np.inner(normalized_embeddings, normalized_embeddings)
        
        visited = set()
        clusters = []
        
        for i in range(len(alerts)):
            if i in visited:
                continue
            
            # Start new cluster
            cluster_alerts = [alerts[i]]
            visited.add(i)
            
            # Find similar alerts
            for j in range(len(alerts)):
                if j != i and j not in visited and sims[i, j] > threshold:
                    cluster_alerts.append(alerts[j])
                    visited.add(j)
            
            # Create cluster
            cluster = {
                "cluster_id": str(uuid.uuid4()),
                "alerts": cluster_alerts,
                "alert_count": len(cluster_alerts),
                "severity": self._determine_cluster_severity(cluster_alerts),
                "systems": list(set(alert.system for alert in cluster_alerts)),
                "categories": list(set(alert.category for alert in cluster_alerts)),
                "time_span_minutes": self._calculate_time_span(cluster_alerts),
                "similarity_score": float(np.mean([sims[i, j] for j in range(len(alerts)) if j in [alerts.index(a) for a in cluster_alerts] and j != i])) if len(cluster_alerts) > 1 else 1.0
            }
            
            clusters.append(cluster)
        
        # Sort clusters by severity and alert count
        severity_order = {"critical": 1, "warning": 2, "info": 3, "low": 4}
        clusters.sort(key=lambda x: (severity_order.get(x["severity"], 5), -x["alert_count"]))
        
        # Keep only top 10 clusters
        return clusters[:10]
    
    def _determine_cluster_severity(self, alerts: List[Alert]) -> str:
        """Determine the overall severity of a cluster"""
        severities = [alert.severity for alert in alerts]
        if "critical" in severities:
            return "high"
        elif "warning" in severities:
            return "medium"
        else:
            return "low"
    
    def _calculate_time_span(self, alerts: List[Alert]) -> float:
        """Calculate time span of alerts in cluster in minutes"""
        if len(alerts) <= 1:
            return 0.0
        
        timestamps = [alert.timestamp for alert in alerts]
        time_span = max(timestamps) - min(timestamps)
        return time_span.total_seconds() / 60.0
    
    async def _generate_llm_summary(self, clusters: List[Dict]) -> str:
        """Generate summary using LLM"""
        try:
            # Prepare context for LLM
            cluster_data = []
            for cluster in clusters:
                cluster_info = {
                    "cluster_id": cluster["cluster_id"],
                    "alert_count": cluster["alert_count"],
                    "severity": cluster["severity"],
                    "systems": cluster["systems"],
                    "categories": cluster["categories"],
                    "time_span_minutes": cluster["time_span_minutes"]
                }
                cluster_data.append(cluster_info)
            
            prompt = f"{CORRELATION_PROMPT}\n\nCluster Data:\n{json.dumps(cluster_data, indent=2)}"
            
            # Generate response
            response = self.llm(prompt)
            
            # Extract summary from response
            if isinstance(response, str):
                return response[:500]  # Limit length
            else:
                return str(response)[:500]
                
        except Exception as e:
            logger.error(f"LLM summary generation error: {e}")
            return self._generate_fallback_summary(clusters)
    
    def _generate_fallback_summary(self, clusters: List[Dict]) -> str:
        """Generate summary without LLM"""
        if not clusters:
            return "No alert clusters found."
        
        total_alerts = sum(cluster["alert_count"] for cluster in clusters)
        high_severity_clusters = len([c for c in clusters if c["severity"] == "high"])
        medium_severity_clusters = len([c for c in clusters if c["severity"] == "medium"])
        
        summary = f"Correlated {total_alerts} alerts into {len(clusters)} clusters. "
        summary += f"Found {high_severity_clusters} high-severity and {medium_severity_clusters} medium-severity clusters. "
        
        if clusters:
            top_cluster = clusters[0]
            summary += f"Largest cluster: {top_cluster['alert_count']} alerts from {', '.join(top_cluster['systems'][:3])}."
        
        return summary
    
    def _calculate_correlation_metrics(self, original_alerts: List[Alert], clusters: List[Dict]) -> Dict:
        """Calculate correlation effectiveness metrics"""
        total_alerts = len(original_alerts)
        clustered_alerts = sum(cluster["alert_count"] for cluster in clusters)
        unclustered_alerts = total_alerts - clustered_alerts
        
        # Calculate reduction ratio
        reduction_ratio = (total_alerts - len(clusters)) / total_alerts if total_alerts > 0 else 0
        
        # Calculate severity distribution
        severity_dist = {"critical": 0, "warning": 0, "info": 0, "low": 0}
        for alert in original_alerts:
            severity_dist[alert.severity] = severity_dist.get(alert.severity, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "clusters_created": len(clusters),
            "clustered_alerts": clustered_alerts,
            "unclustered_alerts": unclustered_alerts,
            "reduction_ratio": round(reduction_ratio, 3),
            "severity_distribution": severity_dist,
            "average_cluster_size": round(clustered_alerts / len(clusters), 2) if clusters else 0,
            "correlation_effectiveness": "high" if reduction_ratio > 0.7 else "medium" if reduction_ratio > 0.4 else "low"
        }
    
    def get_agent_info(self) -> Dict:
        """Get information about the agent"""
        return {
            "name": self.name,
            "version": "1.0.0",
            "capabilities": [
                "sentence_transformer_embeddings",
                "cosine_similarity_clustering",
                "llm_reasoning" if self.use_llm else "fallback_summarization",
                "severity_assessment",
                "time_window_correlation"
            ],
            "models_loaded": {
                "sentence_transformer": self.embedder is not None,
                "llm": self.llm is not None
            },
            "status": "ready" if self.embedder else "degraded"
        }
