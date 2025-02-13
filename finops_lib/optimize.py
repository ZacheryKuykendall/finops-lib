import logging
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

def optimize_costs(start_date, end_date, test):
    """
    Optimize cloud costs by analyzing usage patterns and suggesting cost-saving measures.
    
    Args:
        start_date (str): The start date for the optimization period.
        end_date (str): The end date for the optimization period.
        test (bool): Whether to run in test mode with dummy data.
    
    Returns:
        str: A summary of the optimization results.
    """
    try:
        logger.info(f"Optimizing costs from {start_date} to {end_date} (Test mode: {test})")
        
        # Example: Generate detailed fake test data
        if test:
            logger.info("Generating detailed fake test data for optimization...")
            optimization_results = [
                {
                    "resource_name": "VM1",
                    "current_vm_size": "Standard_D4s_v3",
                    "suggested_vm_size": "Standard_D2s_v3",
                    "reason": "Underutilized CPU and memory",
                    "last_month_cost": "$200",
                    "new_monthly_cost": "$100"
                },
                {
                    "resource_name": "VM2",
                    "current_vm_size": "Standard_B2ms",
                    "suggested_vm_size": "Standard_B1ms",
                    "reason": "Low network usage",
                    "last_month_cost": "$150",
                    "new_monthly_cost": "$75"
                }
            ]
        else:
            # Implement real data fetching and analysis
            optimization_results = []  # Replace with real data

        # Generate a PDF report
        report_path = os.path.join(os.getcwd(), "detailed_optimization_report.pdf")
        c = canvas.Canvas(report_path, pagesize=letter)
        c.drawString(100, 750, f"Optimization Report: {start_date} to {end_date}")
        c.drawString(100, 730, "Detailed Service Optimization Results:")
        
        y_position = 710
        for result in optimization_results:
            c.drawString(100, y_position, f"Resource: {result['resource_name']}")
            y_position -= 20
            c.drawString(100, y_position, f"Current VM Size: {result['current_vm_size']}")
            y_position -= 20
            c.drawString(100, y_position, f"Suggested VM Size: {result['suggested_vm_size']}")
            y_position -= 20
            c.drawString(100, y_position, f"Reason: {result['reason']}")
            y_position -= 20
            c.drawString(100, y_position, f"Last Month Cost: {result['last_month_cost']}")
            y_position -= 20
            c.drawString(100, y_position, f"New Monthly Cost: {result['new_monthly_cost']}")
            y_position -= 40  # Add extra space between entries
        
        c.save()

        return f"Optimization completed successfully. Report saved to {report_path}."

    except Exception as e:
        logger.error(f"An error occurred during optimization: {e}")
        return "Optimization failed due to an error."
