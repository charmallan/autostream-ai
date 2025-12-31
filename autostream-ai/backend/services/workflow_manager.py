"""
Workflow Manager for AutoStream AI
Orchestrates the step-by-step video creation workflow
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

from models.schemas import WorkflowStep, WorkflowState


class WorkflowManager:
    """
    Manages the video creation workflow with step-by-step progression
    and state persistence
    """
    
    def __init__(self, projects_dir: Optional[str] = None):
        """
        Initialize the workflow manager
        
        Args:
            projects_dir: Directory to store project states
        """
        self.base_dir = Path(projects_dir) if projects_dir else Path(__file__).parent.parent / "projects"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Current active project state
        self.current_state: Optional[WorkflowState] = None
        
        # Step configurations
        self.step_order = [
            WorkflowStep.TRENDS,
            WorkflowStep.SCRIPT,
            WorkflowStep.AUDIO,
            WorkflowStep.ASSETS,
            WorkflowStep.VIDEO,
            WorkflowStep.COMPLETE
        ]
        
        self.step_descriptions = {
            WorkflowStep.TRENDS: "Discover trending topics in your niche",
            WorkflowStep.SCRIPT: "Generate and refine your video script",
            WorkflowStep.AUDIO: "Create voiceover with AI narration",
            WorkflowStep.ASSETS: "Configure avatars, logos, and backgrounds",
            WorkflowStep.VIDEO: "Generate your faceless video",
            WorkflowStep.COMPLETE: "Review and export your video"
        }
        
        self.step_requirements = {
            WorkflowStep.TRENDS: [],
            WorkflowStep.SCRIPT: [WorkflowStep.TRENDS],
            WorkflowStep.AUDIO: [WorkflowStep.SCRIPT],
            WorkflowStep.ASSETS: [WorkflowStep.SCRIPT],
            WorkflowStep.VIDEO: [WorkflowStep.AUDIO, WorkflowStep.ASSETS],
            WorkflowStep.COMPLETE: [WorkflowStep.VIDEO]
        }
        
        logger.info("Workflow Manager initialized")
    
    def create_project(self, name: str = "New Project") -> str:
        """
        Create a new video project
        
        Args:
            name: Project name
            
        Returns:
            Project ID
        """
        project_id = str(uuid.uuid4())[:8]
        
        self.current_state = WorkflowState(
            id=project_id,
            name=name,
            current_step=WorkflowStep.TRENDS
        )
        
        self._save_state()
        
        logger.info(f"Created new project: {name} ({project_id})")
        return project_id
    
    def load_project(self, project_id: str) -> bool:
        """
        Load an existing project
        
        Args:
            project_id: Project ID to load
            
        Returns:
            True if loaded successfully, False otherwise
        """
        state_file = self.base_dir / project_id / "workflow_state.json"
        
        if not state_file.exists():
            logger.error(f"Project not found: {project_id}")
            return False
        
        try:
            with open(state_file, "r") as f:
                data = json.load(f)
            
            self.current_state = WorkflowState(**data)
            logger.info(f"Loaded project: {self.current_state.name} ({project_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            return False
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current workflow state as dictionary
        
        Returns:
            Dictionary representation of current state
        """
        if not self.current_state:
            return {"error": "No active project"}
        
        state_dict = self.current_state.model_dump()
        state_dict["step_info"] = self._get_step_info()
        
        return state_dict
    
    def get_current_step(self) -> str:
        """
        Get current step name
        
        Returns:
            Current step as string
        """
        if not self.current_state:
            return "idle"
        return self.current_state.current_step.value
    
    def next_step(self) -> bool:
        """
        Move to the next workflow step
        
        Returns:
            True if moved successfully, False if at final step
        """
        if not self.current_state:
            logger.error("No active project")
            return False
        
        current_index = self.step_order.index(self.current_state.current_step)
        
        if current_index >= len(self.step_order) - 1:
            logger.warning("Already at final step")
            return False
        
        # Check requirements for next step
        next_step = self.step_order[current_index + 1]
        requirements = self.step_requirements.get(next_step, [])
        
        completed_steps = self._get_completed_steps()
        
        for req in requirements:
            if req not in completed_steps:
                logger.error(f"Requirements not met for {next_step}: {req}")
                return False
        
        # Move to next step
        self.current_state.current_step = next_step
        self.current_state.updated_at = datetime.now()
        self._save_state()
        
        logger.info(f"Moved to step: {next_step.value}")
        return True
    
    def previous_step(self) -> bool:
        """
        Move to the previous workflow step
        
        Returns:
            True if moved successfully, False if at first step
        """
        if not self.current_state:
            logger.error("No active project")
            return False
        
        current_index = self.step_order.index(self.current_state.current_step)
        
        if current_index <= 0:
            logger.warning("Already at first step")
            return False
        
        self.current_state.current_step = self.step_order[current_index - 1]
        self.current_state.updated_at = datetime.now()
        self._save_state()
        
        logger.info(f"Moved to step: {self.current_state.current_step.value}")
        return True
    
    def update_step(self, step_name: str, data: Dict[str, Any]) -> bool:
        """
        Update data for a specific step
        
        Args:
            step_name: Name of the step to update
            data: Data to update
            
        Returns:
            True if updated successfully
        """
        if not self.current_state:
            logger.error("No active project")
            return False
        
        step_map = {
            "trends": self.current_state.trends,
            "script": self.current_state.script,
            "audio": self.current_state.audio,
            "assets": self.current_state.assets,
            "video": self.current_state.video
        }
        
        if step_name not in step_map:
            logger.error(f"Invalid step name: {step_name}")
            return False
        
        # Merge data
        step_data = step_map[step_name]
        step_data.update(data)
        
        self.current_state.updated_at = datetime.now()
        self._save_state()
        
        logger.info(f"Updated step: {step_name}")
        return True
    
    def complete_workflow(self) -> bool:
        """
        Mark the workflow as complete
        
        Returns:
            True if completed successfully
        """
        if not self.current_state:
            return False
        
        self.current_state.current_step = WorkflowStep.COMPLETE
        self.current_state.updated_at = datetime.now()
        self._save_state()
        
        logger.info(f"Workflow completed for project: {self.current_state.name}")
        return True
    
    def reset_workflow(self) -> bool:
        """
        Reset the workflow to the beginning
        
        Returns:
            True if reset successfully
        """
        if not self.current_state:
            return False
        
        project_name = self.current_state.name
        
        self.current_state = WorkflowState(
            id=self.current_state.id,
            name=project_name,
            current_step=WorkflowStep.TRENDS
        )
        
        self._save_state()
        
        logger.info(f"Workflow reset for project: {project_name}")
        return True
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get overall workflow progress
        
        Returns:
            Dictionary with progress information
        """
        if not self.current_state:
            return {"progress": 0, "current_step": "idle"}
        
        current_index = self.step_order.index(self.current_state.current_step)
        total_steps = len(self.step_order) - 1  # Exclude COMPLETE step
        
        # Calculate progress (each completed step counts as 20%)
        base_progress = (current_index / total_steps) * 100
        
        # Add progress within current step (simplified)
        step_data = self._get_current_step_data()
        step_progress = self._calculate_step_progress(step_data)
        
        total_progress = min(base_progress + (step_progress / total_steps), 100)
        
        return {
            "progress": round(total_progress, 1),
            "current_step": self.current_state.current_step.value,
            "current_step_name": self.step_descriptions.get(
                self.current_state.current_step, "Unknown"
            ),
            "completed_steps": self._get_completed_steps(),
            "remaining_steps": self._get_remaining_steps(),
            "step_info": self._get_step_info()
        }
    
    def _get_step_info(self) -> Dict[str, Any]:
        """Get information about all steps"""
        if not self.current_state:
            return {}
        
        current_step = self.current_state.current_step
        
        return {
            "total_steps": len(self.step_order) - 1,
            "current_index": self.step_order.index(current_step),
            "steps": [
                {
                    "name": step.value,
                    "description": self.step_descriptions.get(step, ""),
                    "status": self._get_step_status(step),
                    "required": step in self.step_requirements.get(current_step, []),
                    "number": i + 1
                }
                for i, step in enumerate(self.step_order[:-1])  # Exclude COMPLETE
            ]
        }
    
    def _get_step_status(self, step: WorkflowStep) -> str:
        """Get the status of a specific step"""
        if not self.current_state:
            return "pending"
        
        if self.current_state.current_step == step:
            return "active"
        
        if step in self._get_completed_steps():
            return "completed"
        
        return "pending"
    
    def _get_completed_steps(self) -> list:
        """Get list of completed steps"""
        if not self.current_state:
            return []
        
        completed = []
        for step in self.step_order[:-1]:  # Exclude COMPLETE
            if self._is_step_completed(step):
                completed.append(step)
        
        return completed
    
    def _get_remaining_steps(self) -> list:
        """Get list of remaining steps"""
        if not self.current_state:
            return []
        
        current_index = self.step_order.index(self.current_state.current_step)
        remaining = []
        
        for i, step in enumerate(self.step_order[current_index + 1:-1], start=current_index + 1):
            remaining.append({
                "name": step.value,
                "description": self.step_descriptions.get(step, ""),
                "number": i
            })
        
        return remaining
    
    def _is_step_completed(self, step: WorkflowStep) -> bool:
        """Check if a step is completed"""
        step_map = {
            WorkflowStep.TRENDS: self.current_state.trends,
            WorkflowStep.SCRIPT: self.current_state.script,
            WorkflowStep.AUDIO: self.current_state.audio,
            WorkflowStep.ASSETS: self.current_state.assets,
            WorkflowStep.VIDEO: self.current_state.video
        }
        
        step_data = step_map.get(step, {})
        
        if step == WorkflowStep.TRENDS:
            return bool(step_data.get("selected"))
        
        if step == WorkflowStep.SCRIPT:
            return bool(step_data.get("content"))
        
        if step == WorkflowStep.AUDIO:
            return bool(step_data.get("path"))
        
        if step == WorkflowStep.ASSETS:
            return bool(step_data.get("avatar") or step_data.get("background"))
        
        if step == WorkflowStep.VIDEO:
            return bool(step_data.get("output_path"))
        
        return False
    
    def _get_current_step_data(self) -> Dict[str, Any]:
        """Get data for the current step"""
        if not self.current_state:
            return {}
        
        step_map = {
            WorkflowStep.TRENDS: self.current_state.trends,
            WorkflowStep.SCRIPT: self.current_state.script,
            WorkflowStep.AUDIO: self.current_state.audio,
            WorkflowStep.ASSETS: self.current_state.assets,
            WorkflowStep.VIDEO: self.current_state.video
        }
        
        return step_map.get(self.current_state.current_step, {})
    
    def _calculate_step_progress(self, step_data: Dict[str, Any]) -> float:
        """Calculate progress within current step (0-20)"""
        if not step_data:
            return 0
        
        # This is a simplified calculation
        # Each step has different completion criteria
        if "trends" in step_data and "selected" in step_data:
            return 20 if step_data.get("selected") else 10
        
        if "content" in step_data:
            return 20 if step_data.get("edited") else 15
        
        if "path" in step_data:
            return 20 if step_data.get("path") else 10
        
        if "avatar" in step_data or "background" in step_data:
            assets_count = sum(1 for k in ["avatar", "logo", "background"] if step_data.get(k))
            return min(assets_count * 6.67, 20)
        
        if "output_path" in step_data:
            return 20
        
        return 0
    
    def _save_state(self) -> None:
        """Save current state to file"""
        if not self.current_state:
            return
        
        project_dir = self.base_dir / self.current_state.id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        state_file = project_dir / "workflow_state.json"
        
        with open(state_file, "w") as f:
            json.dump(
                self.current_state.model_dump(mode="json"),
                f,
                indent=2,
                default=str
            )
    
    def export_project(self, project_id: str, export_path: str) -> bool:
        """
        Export project data to a zip file
        
        Args:
            project_id: Project ID to export
            export_path: Path to save the export
            
        Returns:
            True if exported successfully
        """
        if not self.load_project(project_id):
            return False
        
        try:
            import shutil
            
            project_dir = self.base_dir / project_id
            export_file = Path(export_path)
            
            # Create zip file
            shutil.make_archive(
                str(export_file).replace(".zip", ""),
                "zip",
                project_dir
            )
            
            logger.info(f"Exported project: {project_id} to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export project: {e}")
            return False
