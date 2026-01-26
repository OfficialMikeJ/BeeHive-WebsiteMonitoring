"""
BeeHive Reports Export Module
Generate PDF and CSV reports for monitoring data
"""
import io
import csv
import zipfile
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import logging

logger = logging.getLogger(__name__)


def generate_csv_report(websites: List[Dict[str, Any]], monitoring_data: List[Dict[str, Any]]) -> bytes:
    """Generate CSV report for monitoring data"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Website Name',
        'URL',
        'Status',
        'Timestamp',
        'Latency (ms)',
        'Page Load Time (ms)',
        'Status Code',
        'Online',
        'SSL Days Until Expiry',
        'Error Message'
    ])
    
    # Create website lookup
    website_lookup = {w['id']: w for w in websites}
    
    # Write monitoring data
    for data in monitoring_data:
        website = website_lookup.get(data['website_id'], {})
        writer.writerow([
            website.get('name', 'Unknown'),
            website.get('url', 'Unknown'),
            website.get('status', 'Unknown'),
            data.get('timestamp', ''),
            data.get('latency', ''),
            data.get('page_load_time', ''),
            data.get('status_code', ''),
            'Yes' if data.get('is_online') else 'No',
            data.get('ssl_info', {}).get('days_until_expiry', '') if data.get('ssl_info') else '',
            data.get('error_message', '')
        ])
    
    return output.getvalue().encode('utf-8')


def generate_pdf_report(websites: List[Dict[str, Any]], monitoring_data: List[Dict[str, Any]], 
                        report_period: str = "Last 30 Days") -> bytes:
    """Generate PDF report for monitoring data"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#FFD700'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#000000'),
        spaceAfter=12,
    )
    
    # Add title
    title = Paragraph("🐝 BeeHive - Website Monitoring Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Add report info
    report_info = Paragraph(f"<b>Report Period:</b> {report_period}<br/>"
                           f"<b>Generated:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}<br/>"
                           f"<b>Total Websites:</b> {len(websites)}", styles['Normal'])
    elements.append(report_info)
    elements.append(Spacer(1, 20))
    
    # Add summary section
    summary_heading = Paragraph("Summary Statistics", heading_style)
    elements.append(summary_heading)
    
    # Calculate statistics
    total_checks = len(monitoring_data)
    online_checks = sum(1 for d in monitoring_data if d.get('is_online'))
    uptime_percentage = (online_checks / total_checks * 100) if total_checks > 0 else 0
    avg_latency = sum(d.get('latency', 0) for d in monitoring_data) / total_checks if total_checks > 0 else 0
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Monitoring Checks', str(total_checks)],
        ['Online Checks', str(online_checks)],
        ['Uptime Percentage', f'{uptime_percentage:.2f}%'],
        ['Average Latency', f'{avg_latency:.2f} ms'],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFD700')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Add websites section
    websites_heading = Paragraph("Monitored Websites", heading_style)
    elements.append(websites_heading)
    
    for website in websites:
        # Get monitoring data for this website
        site_data = [d for d in monitoring_data if d['website_id'] == website['id']]
        site_checks = len(site_data)
        site_online = sum(1 for d in site_data if d.get('is_online'))
        site_uptime = (site_online / site_checks * 100) if site_checks > 0 else 0
        site_avg_latency = sum(d.get('latency', 0) for d in site_data) / site_checks if site_checks > 0 else 0
        
        website_info = Paragraph(
            f"<b>{website['name']}</b><br/>"
            f"URL: {website['url']}<br/>"
            f"Status: <font color=\"{'green' if website['status'] == 'online' else 'red'}\">{website['status'].upper()}</font><br/>"
            f"Checks: {site_checks} | Uptime: {site_uptime:.1f}% | Avg Latency: {site_avg_latency:.1f}ms",
            styles['Normal']
        )
        elements.append(website_info)
        elements.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def create_zip_archive(files: Dict[str, bytes]) -> bytes:
    """Create a ZIP archive containing multiple files"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in files.items():
            zip_file.writestr(filename, content)
    
    return zip_buffer.getvalue()


async def generate_monitoring_report(db, user_id: str, days: int = 30, format: str = "both") -> bytes:
    """
    Generate monitoring report for a user
    
    Args:
        db: MongoDB database instance
        user_id: User ID to generate report for
        days: Number of days to include in report
        format: 'pdf', 'csv', or 'both'
    
    Returns:
        bytes: ZIP file containing the requested reports
    """
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get user's websites
    websites = await db.websites.find({"owner_id": user_id}, {"_id": 0}).to_list(None)
    
    if not websites:
        raise ValueError("No websites found for this user")
    
    # Get monitoring data for all websites
    website_ids = [w['id'] for w in websites]
    monitoring_data = await db.monitoring_data.find({
        "website_id": {"$in": website_ids},
        "timestamp": {"$gte": start_date.isoformat()}
    }, {"_id": 0}).sort("timestamp", -1).to_list(None)
    
    # Generate reports
    files = {}
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    report_period = f"Last {days} Days"
    
    if format in ['csv', 'both']:
        csv_content = generate_csv_report(websites, monitoring_data)
        files[f'beehive_report_{timestamp}.csv'] = csv_content
    
    if format in ['pdf', 'both']:
        pdf_content = generate_pdf_report(websites, monitoring_data, report_period)
        files[f'beehive_report_{timestamp}.pdf'] = pdf_content
    
    # Create summary text file
    summary = f"""BeeHive Monitoring Report
========================

Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
Report Period: {report_period}
Total Websites: {len(websites)}
Total Checks: {len(monitoring_data)}

Websites:
"""
    for website in websites:
        summary += f"\n- {website['name']}: {website['url']} (Status: {website['status']})"
    
    files[f'beehive_summary_{timestamp}.txt'] = summary.encode('utf-8')
    
    # Create ZIP archive
    return create_zip_archive(files)
