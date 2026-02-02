"""MLflow client for experiment tracking."""
import mlflow
from typing import Dict, Any
from cv_analyzer.core.config import settings
from cv_analyzer.core.logging import get_logger

logger = get_logger(__name__)


class MLflowClient:
    """Client for logging experiments to MLflow."""
    
    def __init__(self):
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        self.experiment_name = settings.mlflow_experiment_name
        self._ensure_experiment()
    
    def _ensure_experiment(self):
        """Ensure experiment exists."""
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                mlflow.create_experiment(self.experiment_name)
                logger.info("mlflow_experiment_created", experiment=self.experiment_name)
        except Exception as e:
            logger.error("mlflow_experiment_setup_failed", error=str(e))
            # Continue anyway - MLflow will use default experiment
    
    def log_run(
        self,
        job_id: str,
        cv_id: str,
        provider: str,
        prompt_version: str,
        result: Dict[str, Any],
    ):
        """
        Log a CV analysis run to MLflow.
        
        Args:
            job_id: Job identifier
            cv_id: CV identifier
            provider: AI provider name
            prompt_version: Prompt template version
            result: Analysis result
        """
        try:
            mlflow.set_experiment(self.experiment_name)
            
            with mlflow.start_run(run_name=f"job-{job_id}"):
                # Log parameters
                mlflow.log_param("job_id", job_id)
                mlflow.log_param("cv_id", cv_id)
                mlflow.log_param("provider", provider)
                mlflow.log_param("prompt_version", prompt_version)
                mlflow.log_param("model", result["provider"]["model"])
                
                # Log metrics
                analysis = result["analysis"]
                if "overall_score" in analysis:
                    mlflow.log_metric("overall_score", analysis["overall_score"])
                
                if "score_breakdown" in analysis:
                    for key, value in analysis["score_breakdown"].items():
                        mlflow.log_metric(f"score_{key}", value)
                
                # Log provider metrics
                mlflow.log_metric("tokens_used", result["provider"]["tokens_used"])
                mlflow.log_metric("latency_ms", result["provider"]["latency_ms"])
                
                # Log artifacts (analysis JSON)
                import tempfile
                import json
                with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                    json.dump(result, f, indent=2)
                    mlflow.log_artifact(f.name, "analysis.json")
                
                # Log tags
                mlflow.set_tag("provider", provider)
                mlflow.set_tag("prompt_version", prompt_version)
                mlflow.set_tag("cv_id", cv_id)
                
                logger.info("mlflow_run_logged", job_id=job_id, run_id=mlflow.active_run().info.run_id)
        except Exception as e:
            logger.error("mlflow_logging_failed", job_id=job_id, error=str(e))
            # Don't fail the job if MLflow logging fails


mlflow_client = MLflowClient()
