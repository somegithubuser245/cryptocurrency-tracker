"""
Build output processing utilities to eliminate code duplication in run.py
"""
import subprocess
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class BuildOutputProcessor:
    """Helper class to process build output and categorize errors/warnings"""
    
    def __init__(self):
        self.error_keywords = ['error', 'failed', 'cannot', 'unable']
        self.warning_keyword = 'warning'
    
    def process_build_output(
        self, 
        process: subprocess.Popen,
        show_output: bool = True,
        max_errors_to_show: int = 10,
        max_warnings_to_show: int = 5
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Process build output from a subprocess and categorize errors/warnings
        
        Args:
            process: Subprocess with stdout to monitor
            show_output: Whether to print output in real-time
            max_errors_to_show: Maximum number of errors to track
            max_warnings_to_show: Maximum number of warnings to track
        
        Returns:
            Tuple of (success, errors_list, warnings_list)
        """
        build_errors = []
        build_warnings = []
        
        try:
            # Process output line by line
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    if show_output:
                        print(line)  # Show real-time output
                    
                    # Categorize line
                    self._categorize_line(line, build_errors, build_warnings, 
                                        max_errors_to_show, max_warnings_to_show)
            
            # Wait for process to complete
            process.wait()
            
            # Determine success
            success = process.returncode == 0
            
            return success, build_errors, build_warnings
            
        except Exception as e:
            logger.error(f"Error processing build output: {e}")
            return False, [str(e)], []
    
    def _categorize_line(
        self, 
        line: str, 
        build_errors: List[str], 
        build_warnings: List[str],
        max_errors: int,
        max_warnings: int
    ) -> None:
        """
        Categorize a single line as error, warning, or info
        
        Args:
            line: Line to categorize
            build_errors: List to append errors to
            build_warnings: List to append warnings to
            max_errors: Maximum errors to track
            max_warnings: Maximum warnings to track
        """
        line_lower = line.lower()
        
        # Check for errors (excluding warnings)
        if any(error_keyword in line_lower for error_keyword in self.error_keywords):
            if self.warning_keyword not in line_lower and len(build_errors) < max_errors:
                build_errors.append(line)
        # Check for warnings
        elif self.warning_keyword in line_lower and len(build_warnings) < max_warnings:
            build_warnings.append(line)
    
    def log_build_results(
        self, 
        success: bool, 
        build_errors: List[str], 
        build_warnings: List[str],
        operation_name: str = "Build"
    ) -> None:
        """
        Log build results with appropriate formatting
        
        Args:
            success: Whether the build succeeded
            build_errors: List of error messages
            build_warnings: List of warning messages  
            operation_name: Name of the operation (e.g., "Build", "Docker build")
        """
        if success:
            logger.info(f"[SUCCESS] {operation_name} completed successfully!")
            if build_warnings:
                logger.warning(f"[WARN] {len(build_warnings)} warnings found:")
                for warning in build_warnings:
                    logger.warning(f"  {warning}")
        else:
            logger.error(f"[FAIL] {operation_name} failed!")
            if build_errors:
                logger.error("Build errors found:")
                for error in build_errors:
                    logger.error(f"  {error}")
    
    def create_monitored_process(
        self,
        cmd: List[str],
        cwd: Optional[str] = None,
        shell: bool = False
    ) -> subprocess.Popen:
        """
        Create a subprocess configured for output monitoring
        
        Args:
            cmd: Command to run
            cwd: Working directory
            shell: Whether to use shell
        
        Returns:
            Configured subprocess
        """
        return subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True,
            shell=shell
        )
    
    def run_and_monitor_build(
        self,
        cmd: List[str],
        operation_name: str,
        cwd: Optional[str] = None,
        shell: bool = False,
        show_output: bool = True
    ) -> bool:
        """
        Complete build workflow: run command, monitor output, log results
        
        Args:
            cmd: Command to run
            operation_name: Name for logging
            cwd: Working directory
            shell: Whether to use shell
            show_output: Whether to show real-time output
        
        Returns:
            True if build succeeded, False otherwise
        """
        try:
            logger.info(f"Running: {' '.join(cmd)}")
            
            # Create and monitor process
            process = self.create_monitored_process(cmd, cwd, shell)
            success, errors, warnings = self.process_build_output(process, show_output)
            
            # Log results
            self.log_build_results(success, errors, warnings, operation_name)
            
            return success
            
        except Exception as e:
            logger.error(f"{operation_name} failed with exception: {e}")
            return False